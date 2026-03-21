"""
Integrated Pipeline for Adding New Legal Documents to Knowledge Graph
This script combines 3 steps:
1. Document Extraction - Extract text from PDF/DOC/DOCX files
2. Sentence Simplification - Simplify complex legal sentences using GPT
3. Triplet Extraction - Extract knowledge graph triplets from simplified sentences

Usage:
    Command Line: python add_document_pipeline.py --cli
    GUI: python add_document_pipeline.py --gui
    Or just run: python add_document_pipeline.py (defaults to GUI)
"""

import argparse
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
from dotenv import load_dotenv
from openai import OpenAI
from pymongo import MongoClient
from transformers.integrations import tiktoken

# Import required modules from existing codebase
try:
    from src.db import init_mongo, insert_triplet_batch_mongo
    from src.triplet_extraction.doc_extraction.google_pdf_extraction import extract_text_from_pdf_google_vision
    from src.triplet_extraction.doc_extraction.ms_word_extraction import extract_text_from_docx
    from src.triplet_extraction.doc_extraction.parse_text_to_section import parse_document
    from src.triplet_extraction.doc_extraction.utils import convert_doc_to_docx, strip_markdown_formatting, clean_title
    from src.triplet_extraction.pos_taging import init_vncorenlp
    from src.triplet_extraction.triplet_extraction import triplet_extraction
    from src.triplet_extraction.utils import load_synonym_dict, load_stopwords, setup_logger
    from src.utils import clean_text
    import phonlp
except ImportError as e:
    print(f"Error importing required modules: {e}")
    print("Make sure you're running this from the project root directory")
    sys.exit(1)

# Load environment variables
load_dotenv()


class DocumentPipeline:
    """Main pipeline class for processing legal documents"""
    
    def __init__(self):
        self.config = self._load_config()
        self.mongo_client = None
        self.db = None
        self.openai_client = None
        self.vncorenlp_client = None
        self.phonlp_model = None
        self.synonym_dict = None
        self.stopwords = None
        self.encoding = tiktoken.get_encoding("cl100k_base")
        
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from environment and defaults"""
        current_dir = os.getcwd()
        
        return {
            # API Keys
            "google_credentials": os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            "openai_api_key": os.getenv("OPENAI_API_KEY"),
            "gcs_bucket_name": "vak_ocr_pdf",
            
            # MongoDB
            "mongo_uri": os.getenv("MONGO_URI", "mongodb://localhost:27017/"),
            "db_name": "KB_PROPERTY_LAW",
            
            # OpenAI Settings
            "model_name": "gpt-4o-mini",
            "max_file_tokens": 2_000_000,
            "max_task_tokens": 500_000,
            
            # Paths
            "vncorenlp_dir": os.path.join(current_dir, "nlp_models", "VnCoreNLP-1.2"),
            "phonlp_dir": os.path.join(current_dir, "nlp_models", "phonlp"),
            "synonym_file": os.path.join(current_dir, "listSameKey.txt"),
            "stopwords_file": os.path.join(current_dir, "stopwords.csv"),
            "temp_dir": Path(tempfile.mkdtemp(prefix="doc_pipeline_")),
            "output_dir": Path(current_dir) / "pipeline_output",
        }
    
    def initialize(self):
        """Initialize all required connections and models"""
        print("Initializing pipeline components...")
        
        try:
            # MongoDB
            self.mongo_client = init_mongo()
            if not self.mongo_client:
                raise Exception("Failed to connect to MongoDB. Please ensure MongoDB is running.")
            self.db = self.mongo_client[self.config["db_name"]]
            print("✓ MongoDB connected")
        except Exception as e:
            raise Exception(f"MongoDB initialization failed: {str(e)}")
        
        try:
            # OpenAI
            if not self.config["openai_api_key"]:
                raise Exception("OPENAI_API_KEY not found in environment variables")
            self.openai_client = OpenAI(api_key=self.config["openai_api_key"])
            print("✓ OpenAI client initialized")
        except Exception as e:
            raise Exception(f"OpenAI initialization failed: {str(e)}")
        
        try:
            # NLP Models
            self.vncorenlp_client = init_vncorenlp(self.config["vncorenlp_dir"])
            if not self.vncorenlp_client:
                raise Exception("VnCoreNLP initialization returned None")
            self.phonlp_model = phonlp.load(save_dir=self.config["phonlp_dir"])
            if not self.phonlp_model:
                raise Exception("PhoNLP model loading returned None")
            print("✓ NLP models loaded")
        except Exception as e:
            raise Exception(f"NLP models initialization failed: {str(e)}. Ensure models are in nlp_models/ directory.")
        
        try:
            # Dictionaries
            self.synonym_dict = load_synonym_dict(self.config["synonym_file"])
            self.stopwords = load_stopwords(self.config["stopwords_file"])
            print("✓ Synonym and stopwords loaded")
        except Exception as e:
            raise Exception(f"Dictionary loading failed: {str(e)}. Ensure listSameKey.txt and stopwords.csv exist.")
        
        # Create output directory
        try:
            self.config["output_dir"].mkdir(exist_ok=True)
        except Exception as e:
            raise Exception(f"Failed to create output directory: {str(e)}")
        
        print("✓ All components initialized successfully\n")
    
    def step1_extract_document(self, document_info: Dict[str, Any]) -> str:
        """
        Step 1: Extract text from document files
        
        Args:
            document_info: Dictionary containing:
                - so_hieu: Document identifier (e.g., "01/2013/QH13")
                - title: Document title
                - effective_date: Effective date (YYYY-MM-DD)
                - files: List of file paths to process
        
        Returns:
            so_hieu of the processed document
        """
        print(f"\n{'='*60}")
        print("STEP 1: Document Text Extraction")
        print(f"{'='*60}\n")
        
        so_hieu = document_info["so_hieu"]
        title = document_info["title"]
        effective_date = document_info["effective_date"]
        files = document_info["files"]
        
        # Check for duplicate document
        print(f"Checking for existing document with so_hieu: {so_hieu}...")
        existing_doc = self.db.extracted_documents.find_one({"so_hieu": so_hieu})
        if existing_doc:
            raise Exception(
                f"DUPLICATE DOCUMENT ERROR: A document with so_hieu '{so_hieu}' already exists in the database.\n"
                f"Existing document title: {existing_doc.get('title', 'N/A')}\n"
                f"Effective date: {existing_doc.get('effective_date', 'N/A')}\n"
                f"Please use a different so_hieu or remove the existing document first."
            )
        print("✓ No duplicate found\n")
        
        print(f"Document: {so_hieu} - {title}")
        print(f"Effective Date: {effective_date}")
        print(f"Files to process: {len(files)}\n")
        
        combined_text = ""
        source_files = []
        extraction_errors = []
        
        for file_path in files:
            file_path = Path(file_path)
            if not file_path.exists():
                error_msg = f"File not found: {file_path}"
                print(f"✗ {error_msg}")
                extraction_errors.append(error_msg)
                continue
            
            if file_path.suffix.lower() not in [".pdf", ".doc", ".docx"]:
                error_msg = f"Unsupported format: {file_path.name} (must be PDF, DOC, or DOCX)"
                print(f"✗ {error_msg}")
                extraction_errors.append(error_msg)
                continue
            
            print(f"Processing {file_path.name}...", end=" ")
            
            try:
                # Convert .doc to .docx if needed
                if file_path.suffix.lower() == ".doc":
                    try:
                        file_path = convert_doc_to_docx(file_path, self.config["temp_dir"])
                    except Exception as e:
                        raise Exception(f"Failed to convert DOC to DOCX: {str(e)}")
                
                # Extract text
                if file_path.suffix.lower() == ".docx":
                    text = "\n".join(extract_text_from_docx(file_path))
                elif file_path.suffix.lower() == ".pdf":
                    if not self.config["google_credentials"]:
                        raise Exception("GOOGLE_APPLICATION_CREDENTIALS not set for PDF extraction")
                    text = extract_text_from_pdf_google_vision(
                        credential_file=self.config["google_credentials"],
                        bucket_name=self.config["gcs_bucket_name"],
                        gcs_path=f"pdfs/{file_path.name}",
                        output_path=f"ocr-output/{file_path.stem}/",
                        pdf_path=str(file_path)
                    )
                
                if text:
                    combined_text += text
                    source_files.append(file_path.name)
                    print(f"✓ Extracted {len(text):,} characters")
                else:
                    error_msg = f"No text extracted from {file_path.name}"
                    print(f"⚠ {error_msg}")
                    extraction_errors.append(error_msg)
                    
            except Exception as e:
                error_msg = f"Error processing {file_path.name}: {str(e)}"
                print(f"✗ {error_msg}")
                extraction_errors.append(error_msg)
        
        if not combined_text:
            error_summary = "\n".join([f"  - {err}" for err in extraction_errors])
            raise Exception(
                f"TEXT EXTRACTION FAILED: No text was extracted from any files.\n"
                f"Errors encountered:\n{error_summary}"
            )
        
        # Save to MongoDB
        try:
            extracted_data = {
                "so_hieu": so_hieu,
                "title": title,
                "effective_date": effective_date,
                "source_files": ", ".join(source_files),
                "combined_text": combined_text,
                "text_length": len(combined_text)
            }
            self.db.extracted_documents.insert_one(extracted_data)
            print(f"✓ Saved extracted text to MongoDB")
        except Exception as e:
            raise Exception(f"Failed to save extracted document to MongoDB: {str(e)}")
        
        # Parse document into sections
        print(f"\nParsing document into sections...")
        try:
            processing_text = strip_markdown_formatting(combined_text)
            result = parse_document(processing_text, so_hieu)
            
            if not result:
                raise Exception("Document parsing returned no sections")
            
            sections_count = 0
            for section_id, section_data in result.items():
                section_data["document_title"] = clean_title(title)
                section_data["effective_date"] = effective_date
                section_data["source_file"] = source_files
                section_data["_id"] = section_id
                
                self.db.legal_sections.update_one(
                    {"_id": section_id},
                    {"$set": section_data},
                    upsert=True
                )
                sections_count += 1
            
            print(f"✓ Total: {len(combined_text):,} characters from {len(source_files)} file(s)")
            print(f"✓ Parsed into {sections_count} sections")
            print(f"✓ Saved to MongoDB collection: legal_sections")
            
        except Exception as e:
            raise Exception(f"Document parsing failed: {str(e)}")
        
        if extraction_errors:
            print(f"\n⚠ Warning: {len(extraction_errors)} file(s) had errors but processing continued")
        
        return so_hieu
    
    def step2_simplify_sentences(self, so_hieu: str) -> str:
        """
        Step 2: Simplify complex legal sentences using GPT batch API
        
        Args:
            so_hieu: Document identifier
        
        Returns:
            so_hieu of the processed document
        """
        print(f"\n{'='*60}")
        print("STEP 2: Sentence Simplification")
        print(f"{'='*60}\n")
        
        print(f"Processing document: {so_hieu}")
        
        # Simplification prompt
        SIMPLIFY_SYSTEM_PROMPT = """
Role: You are a professional Legal and Linguistics AI Assistant specializing in Vietnamese law. Your task is to deconstruct complex legal texts into independent, direct simple sentences.
Objective: Transform legal clauses into standalone simple sentences. Each sentence must be a direct legal statement, avoiding introductory fillers or explanatory bridges.
Strict "Directness" Rules:
No Filler Subjects: Do not use phrases like "Một loại hành vi là..." (One type of behavior is...), "Bao gồm các loại..." (Includes types of...), or "Được xác định như sau" (Is defined as follows).
Direct Predication: Connect the main Subject directly to the specific Action or Object.
Incorrect: "Một loại hành vi vi phạm là làm sai lệch hồ sơ."
Correct: "Hành vi vi phạm quy định về hồ sơ bao gồm hành vi làm sai lệch hồ sơ." (Or simply: "Làm sai lệch hồ sơ là hành vi vi phạm quy định về hồ sơ.")
The "Simple Sentence" Constraint:
Exactly one Subject and one Predicate.
No conjunctions (và, hoặc, nhưng, mà, còn, rồi...).
No commas (,) or semicolons (;) to link clauses.
Copy Forward Context: If the input lists sub-items under a heading, integrate the full heading context into every single sub-item to ensure they are legally complete.
Output Format:
Return strictly a JSON object.
If information is insufficient: {"need_more_information": "..."}.
If successful: {"simplified_sentences": ["Direct Sentence 1.", "Direct Sentence 2."]}.
Example Transformation: Input: "Hành vi vi phạm quy định về hồ sơ địa giới bao gồm: (a) Làm sai lệch sơ đồ; (b) Làm sai lệch bảng tọa độ." Output: { "simplified_sentences": [ "Hành vi làm sai lệch sơ đồ là hành vi vi phạm quy định về hồ sơ địa giới.", "Hành vi làm sai lệch bảng tọa độ là hành vi vi phạm quy định về hồ sơ địa giới." ] }
"""
        
        # Load sections from MongoDB
        docs = list(self.db.legal_sections.find({"so_hieu": so_hieu}))
        
        # Find leaf nodes
        parent_ids = {doc["parent_id"] for doc in docs if doc.get("parent_id") is not None}
        leaf_nodes = [doc for doc in docs if doc["_id"] not in parent_ids]
        
        print(f"Found {len(docs)} total sections, {len(leaf_nodes)} leaf nodes")
        
        # Build ID map for path collection
        all_docs = list(self.db.legal_sections.find({}))
        id_map = {doc["_id"]: doc for doc in all_docs}
        
        def collect_path(leaf):
            path = []
            current = leaf
            while current:
                path.append(current)
                pid = current.get("parent_id")
                current = id_map.get(pid)
            path.reverse()
            return path
        
        # Collect sections to process
        sections_data = []
        for leaf in leaf_nodes:
            if leaf.get("is_phu_luc") or leaf.get("is_amendment"):
                continue
            
            path_nodes = collect_path(leaf)
            combined_content = "\n".join(
                n["content"]
                for n in path_nodes
                if n.get("content") and n["type"] in ["điều", "khoản", "điểm"]
            )
            
            if not combined_content:
                continue
            
            sections_data.append({
                "leaf_id": leaf["_id"],
                "so_hieu": leaf.get("so_hieu"),
                "full_path": leaf.get("full_path"),
                "combined_content": combined_content
            })
        
        print(f"Collected {len(sections_data)} sections for simplification")
        
        # Create batch tasks
        tasks = []
        for section in sections_data:
            content = clean_text(section["combined_content"])
            content_chunks = self._split_text_by_tokens(content, self.config["max_task_tokens"])
            
            for idx, chunk in enumerate(content_chunks, start=1):
                task = {
                    "custom_id": section["leaf_id"],
                    "method": "POST",
                    "url": "/v1/chat/completions",
                    "body": {
                        "model": self.config["model_name"],
                        "messages": [
                            {"role": "system", "content": SIMPLIFY_SYSTEM_PROMPT},
                            {"role": "user", "content": f'Sentence need simplify:  "{chunk}"'},
                        ],
                    },
                    "_token_count": self._count_chat_tokens([
                        {"role": "system", "content": SIMPLIFY_SYSTEM_PROMPT},
                        {"role": "user", "content": f'Sentence need simplify:  "{chunk}"'},
                    ])
                }
                tasks.append(task)
        
        print(f"Created {len(tasks)} batch tasks")
        
        # Split into files if needed
        batch_file = self.config["output_dir"] / f"batch_{so_hieu.replace('/', '_')}.jsonl"
        with open(batch_file, "w", encoding="utf-8") as f:
            for task in tasks:
                task_copy = {k: v for k, v in task.items() if k != "_token_count"}
                f.write(json.dumps(task_copy, ensure_ascii=False) + "\n")
        
        print(f"✓ Batch file created: {batch_file}")
        
        # Submit batch to OpenAI
        print("\nSubmitting batch to OpenAI...")
        try:
            file_obj = self.openai_client.files.create(
                file=open(batch_file, "rb"),
                purpose="batch"
            )
        except Exception as e:
            raise Exception(f"Failed to upload batch file to OpenAI: {str(e)}")
        
        try:
            batch = self.openai_client.batches.create(
                input_file_id=file_obj.id,
                endpoint="/v1/chat/completions",
                completion_window="24h"
            )
        except Exception as e:
            raise Exception(f"Failed to create batch job: {str(e)}")
        
        print(f"✓ Batch submitted: {batch.id}")
        print(f"  Status: {batch.status}")
        
        # Wait for completion
        print("\nWaiting for batch to complete...")
        max_retries = 2880  # 24 hours with 30 second intervals
        retries = 0
        
        while batch.status not in ("completed", "failed", "expired", "cancelled"):
            if retries >= max_retries:
                raise Exception(f"Batch processing timeout after 24 hours. Batch ID: {batch.id}")
            
            time.sleep(30)
            try:
                batch = self.openai_client.batches.retrieve(batch.id)
                print(f"  Status: {batch.status} - {batch.request_counts.completed}/{batch.request_counts.total} completed")
            except Exception as e:
                print(f"  Warning: Failed to retrieve batch status: {str(e)}")
            
            retries += 1
        
        if batch.status != "completed":
            error_msg = f"Batch processing failed with status: {batch.status}"
            if batch.status == "failed":
                error_msg += f"\nBatch ID: {batch.id}"
                if hasattr(batch, 'errors') and batch.errors:
                    error_msg += f"\nErrors: {batch.errors}"
            raise Exception(error_msg)
        
        # Download results
        result_file = self.config["output_dir"] / f"results_{so_hieu.replace('/', '_')}.jsonl"
        try:
            content = self.openai_client.files.content(batch.output_file_id)
            with open(result_file, "wb") as f:
                f.write(content.read())
            print(f"✓ Results downloaded: {result_file}")
        except Exception as e:
            raise Exception(f"Failed to download batch results: {str(e)}")
        
        # Process results and save to MongoDB
        print("\nProcessing results...")
        total_sentences = 0
        processing_errors = 0
        
        try:
            with open(result_file, "r", encoding="utf-8") as f:
                for line_num, line in enumerate(f, 1):
                    try:
                        data = json.loads(line)
                    except json.JSONDecodeError as e:
                        processing_errors += 1
                        print(f"⚠ Line {line_num}: JSON decode error - {str(e)}")
                        continue
                    
                    if data.get("response", {}).get("status_code") != 200:
                        processing_errors += 1
                        status = data.get("response", {}).get("status_code", "unknown")
                        print(f"⚠ Line {line_num}: Non-200 response - status {status}")
                        continue
                    
                    raw_content = data["response"]["body"]["choices"][0]["message"]["content"].strip()
                    try:
                        parsed = json.loads(raw_content)
                    except json.JSONDecodeError:
                        processing_errors += 1
                        print(f"⚠ Line {line_num}: Failed to parse GPT response as JSON")
                        continue
                    
                    sentences = parsed.get("simplified_sentences", [])
                    if not sentences:
                        continue
                    
                    section_id = data["custom_id"].split("_part")[0]
                    
                    sequence = 1
                    for sentence in sentences:
                        sentence = sentence.strip()
                        if not sentence:
                            continue
                        
                        try:
                            self.db.processed_legal_sections.update_one(
                                {"section_id": section_id, "sequence": sequence},
                                {
                                    "$setOnInsert": {
                                        "content": sentence,
                                        "so_hieu": so_hieu
                                    }
                                },
                                upsert=True
                            )
                            total_sentences += 1
                            sequence += 1
                        except Exception as e:
                            processing_errors += 1
                            print(f"⚠ Failed to save sentence for section {section_id}: {str(e)}")
            
            print(f"✓ Processed {total_sentences} simplified sentences")
            if processing_errors > 0:
                print(f"⚠ {processing_errors} errors occurred during processing")
            print(f"✓ Saved to MongoDB collection: processed_legal_sections")
            
            if total_sentences == 0:
                raise Exception("No sentences were successfully processed from batch results")
            
        except Exception as e:
            if "No sentences were successfully processed" in str(e):
                raise
            raise Exception(f"Failed to process batch results: {str(e)}")
        
        return so_hieu
    
    def step3_extract_triplets(self, so_hieu: str) -> Dict[str, int]:
        """
        Step 3: Extract knowledge graph triplets
        
        Args:
            so_hieu: Document identifier
        
        Returns:
            Dictionary with processing statistics
        """
        print(f"\n{'='*60}")
        print("STEP 3: Triplet Extraction")
        print(f"{'='*60}\n")
        
        print(f"Processing document: {so_hieu}")
        
        total_processed = 0
        total_triplets = 0
        total_no_triplets = 0
        total_errors = 0
        
        # Get processed sentences
        projection = {'section_id': 1, 'sequence': 1, 'so_hieu': 1, 'content': 1}
        rows = list(self.db.processed_legal_sections.find({"so_hieu": so_hieu}, projection))
        
        print(f"Found {len(rows)} sentences to process\n")
        
        for row in rows:
            section_id = row["section_id"]
            sequence = row.get("sequence", 0)
            sentence = row["content"]
            
            if not sentence or not sentence.strip():
                continue
            
            # Get section metadata
            try:
                from bson import ObjectId
                section = self.db.legal_sections.find_one({"_id": ObjectId(section_id)})
            except:
                section = self.db.legal_sections.find_one({"_id": section_id})
            
            if not section or section.get("is_amendment", False):
                continue
            
            doc_metadata = {
                'so_hieu': so_hieu,
                'section_id': str(section_id)
            }
            
            try:
                # Extract triplets
                triplets = triplet_extraction(
                    text=sentence,
                    vncorenlp_client=self.vncorenlp_client,
                    phoNLP_model=self.phonlp_model,
                    stopwords=self.stopwords,
                    logger=None,
                    max_depth=3,
                )
                
                triplets_list = [
                    {"c1": c1, "r": r, "c2": c2}
                    for (c1, r, c2) in triplets
                    if c1 and r and c2
                ]
                
                if triplets_list:
                    count = insert_triplet_batch_mongo(
                        self.db,
                        triplets_list=triplets_list,
                        metadata=doc_metadata,
                        synonym_dict=self.synonym_dict,
                    )
                    total_triplets += count
                else:
                    total_no_triplets += 1
                
                total_processed += 1
                
                if total_processed % 10 == 0:
                    print(f"Processed: {total_processed}/{len(rows)} | Triplets: {total_triplets} | No triplets: {total_no_triplets} | Errors: {total_errors}")
                
            except Exception as e:
                total_errors += 1
                print(f"✗ Error processing sentence {section_id}: {e}")
        
        print(f"\n✓ Extraction complete!")
        print(f"  Total processed: {total_processed}")
        print(f"  Triplets extracted: {total_triplets}")
        print(f"  No triplets: {total_no_triplets}")
        print(f"  Errors: {total_errors}")
        
        return {
            "processed": total_processed,
            "triplets": total_triplets,
            "no_triplets": total_no_triplets,
            "errors": total_errors
        }
    
    def run_full_pipeline(self, document_info: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the complete 3-step pipeline
        
        Args:
            document_info: Document information dictionary
        
        Returns:
            Dictionary with results from all steps
        """
        print(f"\n{'#'*60}")
        print("STARTING FULL DOCUMENT PROCESSING PIPELINE")
        print(f"{'#'*60}\n")
        
        start_time = time.time()
        current_step = "Initialization"
        
        try:
            # Step 1: Extract document
            current_step = "Step 1: Document Extraction"
            print(f"Starting {current_step}...")
            so_hieu = self.step1_extract_document(document_info)
            
            # Step 2: Simplify sentences
            current_step = "Step 2: Sentence Simplification"
            print(f"\nStarting {current_step}...")
            so_hieu = self.step2_simplify_sentences(so_hieu)
            
            # Step 3: Extract triplets
            current_step = "Step 3: Triplet Extraction"
            print(f"\nStarting {current_step}...")
            stats = self.step3_extract_triplets(so_hieu)
            
            elapsed_time = time.time() - start_time
            
            print(f"\n{'#'*60}")
            print("PIPELINE COMPLETED SUCCESSFULLY")
            print(f"{'#'*60}\n")
            print(f"Document: {so_hieu}")
            print(f"Total time: {elapsed_time:.2f} seconds ({elapsed_time/60:.2f} minutes)")
            print(f"Triplets extracted: {stats['triplets']}")
            
            return {
                "success": True,
                "so_hieu": so_hieu,
                "elapsed_time": elapsed_time,
                "stats": stats
            }
            
        except Exception as e:
            elapsed_time = time.time() - start_time
            error_msg = str(e)
            
            print(f"\n{'!'*60}")
            print(f"PIPELINE FAILED AT: {current_step}")
            print(f"{'!'*60}")
            print(f"Error: {error_msg}")
            print(f"Time elapsed before failure: {elapsed_time:.2f} seconds")
            print(f"{'!'*60}\n")
            
            return {
                "success": False,
                "error": error_msg,
                "failed_at": current_step,
                "elapsed_time": elapsed_time
            }
    
    def _split_text_by_tokens(self, text: str, max_tokens: int) -> List[str]:
        """Split text into chunks by token count"""
        tokens = self.encoding.encode(text)
        chunks = []
        
        for i in range(0, len(tokens), max_tokens):
            chunk_tokens = tokens[i:i + max_tokens]
            chunks.append(self.encoding.decode(chunk_tokens))
        
        return chunks
    
    def _count_chat_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens in chat messages"""
        tokens = 0
        for msg in messages:
            tokens += 4  # role + formatting overhead
            tokens += len(self.encoding.encode(msg["content"]))
        tokens += 2  # assistant reply priming
        return tokens


def run_cli_mode():
    """Run pipeline in command-line mode"""
    print("\n" + "="*60)
    print("Legal Document Processing Pipeline - CLI Mode")
    print("="*60 + "\n")
    
    # Collect document information
    print("Please provide the following information:\n")
    
    so_hieu = input("Document ID (so_hieu) [e.g., 01/2013/QH13]: ").strip()
    title = input("Document title: ").strip()
    effective_date = input("Effective date (YYYY-MM-DD): ").strip()
    
    print("\nFile paths (enter one per line, empty line to finish):")
    files = []
    while True:
        file_path = input(f"File {len(files) + 1}: ").strip()
        if not file_path:
            break
        files.append(file_path)
    
    if not files:
        print("Error: At least one file is required!")
        return
    
    document_info = {
        "so_hieu": so_hieu,
        "title": title,
        "effective_date": effective_date,
        "files": files
    }
    
    # Confirm
    print("\n" + "-"*60)
    print("Document Information Summary:")
    print(f"  ID: {so_hieu}")
    print(f"  Title: {title}")
    print(f"  Effective Date: {effective_date}")
    print(f"  Files: {len(files)} file(s)")
    for i, f in enumerate(files, 1):
        print(f"    {i}. {f}")
    print("-"*60 + "\n")
    
    confirm = input("Proceed with processing? (yes/no): ").strip().lower()
    if confirm not in ["yes", "y"]:
        print("Cancelled.")
        return
    
    # Initialize and run pipeline
    pipeline = DocumentPipeline()
    pipeline.initialize()
    result = pipeline.run_full_pipeline(document_info)
    
    return result


def run_gui_mode():
    """Run pipeline with a simple GUI"""
    try:
        import tkinter as tk
        from tkinter import filedialog, messagebox, ttk
    except ImportError:
        print("Error: tkinter not available. Please use --cli mode instead.")
        return
    
    class PipelineGUI:
        def __init__(self, root):
            self.root = root
            self.root.title("Legal Document Processing Pipeline")
            self.root.geometry("700x600")
            
            self.files = []
            self.pipeline = None
            
            self._create_widgets()
        
        def _create_widgets(self):
            # Main frame
            main_frame = ttk.Frame(self.root, padding="10")
            main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
            
            # Title
            title_label = ttk.Label(main_frame, text="Add New Document to Knowledge Graph", 
                                   font=('Arial', 14, 'bold'))
            title_label.grid(row=0, column=0, columnspan=3, pady=10)
            
            # Document ID
            ttk.Label(main_frame, text="Document ID (so_hieu):").grid(row=1, column=0, sticky=tk.W, pady=5)
            self.so_hieu_entry = ttk.Entry(main_frame, width=40)
            self.so_hieu_entry.grid(row=1, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            ttk.Label(main_frame, text="e.g., 01/2013/QH13", foreground="gray").grid(row=2, column=1, sticky=tk.W)
            
            # Title
            ttk.Label(main_frame, text="Document Title:").grid(row=3, column=0, sticky=tk.W, pady=5)
            self.title_entry = ttk.Entry(main_frame, width=40)
            self.title_entry.grid(row=3, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            
            # Effective Date
            ttk.Label(main_frame, text="Effective Date:").grid(row=4, column=0, sticky=tk.W, pady=5)
            self.date_entry = ttk.Entry(main_frame, width=40)
            self.date_entry.grid(row=4, column=1, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            ttk.Label(main_frame, text="Format: YYYY-MM-DD", foreground="gray").grid(row=5, column=1, sticky=tk.W)
            
            # Files section
            ttk.Label(main_frame, text="Document Files:", font=('Arial', 10, 'bold')).grid(row=6, column=0, sticky=tk.W, pady=(15, 5))
            
            # File list
            self.file_listbox = tk.Listbox(main_frame, height=8, width=60)
            self.file_listbox.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            
            # File buttons
            file_btn_frame = ttk.Frame(main_frame)
            file_btn_frame.grid(row=7, column=2, sticky=(tk.N, tk.S), padx=5)
            
            ttk.Button(file_btn_frame, text="Add Files", command=self._add_files).pack(pady=2, fill=tk.X)
            ttk.Button(file_btn_frame, text="Remove", command=self._remove_file).pack(pady=2, fill=tk.X)
            ttk.Button(file_btn_frame, text="Clear All", command=self._clear_files).pack(pady=2, fill=tk.X)
            
            # Progress section
            ttk.Label(main_frame, text="Status:", font=('Arial', 10, 'bold')).grid(row=8, column=0, sticky=tk.W, pady=(15, 5))
            
            self.status_text = tk.Text(main_frame, height=8, width=60, wrap=tk.WORD, state=tk.DISABLED)
            self.status_text.grid(row=9, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=5)
            
            scrollbar = ttk.Scrollbar(main_frame, orient=tk.VERTICAL, command=self.status_text.yview)
            scrollbar.grid(row=9, column=2, sticky=(tk.N, tk.S))
            self.status_text['yscrollcommand'] = scrollbar.set
            
            # Action buttons
            btn_frame = ttk.Frame(main_frame)
            btn_frame.grid(row=10, column=0, columnspan=3, pady=15)
            
            self.process_btn = ttk.Button(btn_frame, text="Start Processing", command=self._start_processing)
            self.process_btn.pack(side=tk.LEFT, padx=5)
            
            ttk.Button(btn_frame, text="Exit", command=self.root.quit).pack(side=tk.LEFT, padx=5)
            
            # Configure grid weights
            self.root.columnconfigure(0, weight=1)
            self.root.rowconfigure(0, weight=1)
            main_frame.columnconfigure(1, weight=1)
        
        def _add_files(self):
            files = filedialog.askopenfilenames(
                title="Select Document Files",
                filetypes=[
                    ("All supported", "*.pdf;*.doc;*.docx"),
                    ("PDF files", "*.pdf"),
                    ("Word files", "*.doc;*.docx"),
                    ("All files", "*.*")
                ]
            )
            for file in files:
                if file not in self.files:
                    self.files.append(file)
                    self.file_listbox.insert(tk.END, os.path.basename(file))
        
        def _remove_file(self):
            selection = self.file_listbox.curselection()
            if selection:
                idx = selection[0]
                self.files.pop(idx)
                self.file_listbox.delete(idx)
        
        def _clear_files(self):
            self.files = []
            self.file_listbox.delete(0, tk.END)
        
        def _log(self, message):
            self.status_text.config(state=tk.NORMAL)
            self.status_text.insert(tk.END, message + "\n")
            self.status_text.see(tk.END)
            self.status_text.config(state=tk.DISABLED)
            self.root.update()
        
        def _start_processing(self):
            # Validate inputs
            so_hieu = self.so_hieu_entry.get().strip()
            title = self.title_entry.get().strip()
            effective_date = self.date_entry.get().strip()
            
            if not so_hieu or not title or not effective_date:
                messagebox.showerror("Error", "Please fill in all document information fields")
                return
            
            if not self.files:
                messagebox.showerror("Error", "Please add at least one document file")
                return
            
            # Confirm
            confirm = messagebox.askyesno(
                "Confirm Processing",
                f"Process document:\n\nID: {so_hieu}\nTitle: {title}\nDate: {effective_date}\nFiles: {len(self.files)}\n\nThis may take several minutes. Continue?"
            )
            
            if not confirm:
                return
            
            # Disable button
            self.process_btn.config(state=tk.DISABLED)
            
            # Clear status
            self.status_text.config(state=tk.NORMAL)
            self.status_text.delete(1.0, tk.END)
            self.status_text.config(state=tk.DISABLED)
            
            document_info = {
                "so_hieu": so_hieu,
                "title": title,
                "effective_date": effective_date,
                "files": self.files
            }
            
            # Initialize pipeline
            self._log("Initializing pipeline...")
            try:
                self.pipeline = DocumentPipeline()
                self.pipeline.initialize()
                self._log("✓ Pipeline initialized\n")
                
            except Exception as e:
                error_msg = str(e)
                self._log(f"\n✗ INITIALIZATION FAILED: {error_msg}")
                messagebox.showerror(
                    "Initialization Error",
                    f"Failed to initialize pipeline:\n\n{error_msg}\n\n"
                    "Please check:\n"
                    "- MongoDB is running\n"
                    "- Environment variables are set\n"
                    "- NLP models are present"
                )
                self.process_btn.config(state=tk.NORMAL)
                return
            
            # Run pipeline
            try:
                result = self.pipeline.run_full_pipeline(document_info)
                
                if result["success"]:
                    self._log(f"\n✓ COMPLETE! Processed in {result['elapsed_time']:.2f}s")
                    self._log(f"✓ Triplets extracted: {result['stats']['triplets']}")
                    messagebox.showinfo(
                        "Success",
                        f"Document processed successfully!\n\n"
                        f"Document: {result['so_hieu']}\n"
                        f"Triplets: {result['stats']['triplets']}\n"
                        f"Time: {result['elapsed_time']/60:.1f} minutes"
                    )
                else:
                    self._log(f"\n✗ FAILED: {result['error']}")
                    messagebox.showerror(
                        "Processing Error",
                        f"Pipeline failed at: {result.get('failed_at', 'Unknown')}\n\n"
                        f"Error:\n{result['error']}\n\n"
                        f"Please check the status log for details."
                    )
                    
            except Exception as e:
                error_msg = str(e)
                self._log(f"\n✗ UNEXPECTED ERROR: {error_msg}")
                import traceback
                traceback_str = traceback.format_exc()
                self._log(f"\n{traceback_str}")
                messagebox.showerror(
                    "Unexpected Error",
                    f"An unexpected error occurred:\n\n{error_msg}\n\n"
                    "See status log for full traceback."
                )
            
            finally:
                self.process_btn.config(state=tk.NORMAL)
    
    # Run GUI
    root = tk.Tk()
    app = PipelineGUI(root)
    root.mainloop()


def main():
    parser = argparse.ArgumentParser(
        description="Legal Document Processing Pipeline - Add new documents to Knowledge Graph"
    )
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Run in command-line interface mode"
    )
    parser.add_argument(
        "--gui",
        action="store_true",
        help="Run with graphical user interface (default)"
    )
    
    args = parser.parse_args()
    
    if args.cli:
        run_cli_mode()
    else:
        run_gui_mode()


if __name__ == "__main__":
    main()
