import os
import tempfile
from pathlib import Path

import pandas as pd
from dotenv import load_dotenv

from src.db import init_mongo

from knowledge_graph.triplet_extraction.doc_extraction.google_pdf_extraction import extract_text_from_pdf_google_vision
from knowledge_graph.triplet_extraction.doc_extraction.ms_word_extraction import extract_text_from_docx
from knowledge_graph.triplet_extraction.doc_extraction.parse_text_to_section import parse_document
from knowledge_graph.triplet_extraction.doc_extraction.utils import convert_doc_to_docx, strip_markdown_formatting, \
    clean_title

load_dotenv()
credential_file = os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
bucket_name = "vak_ocr_pdf"

data_folder = Path(r"/src/triplet_extraction\data\luat_dat_dai")
file_folder = data_folder / "files"
output_csv = data_folder / "extracted_texts_google_fixed_v1.csv"

# Create temp folder for doc conversions
temp_conversion_folder = Path(tempfile.mkdtemp(prefix="doc_conversion_"))

# Initialize MongoDB client
mongo_client = init_mongo()
db = mongo_client["KB_PROPERTY_LAW"]
sections_collection = db["legal_sections"]

#TODO Add UI to fill in information about the documents to be processed and upload file in the correct order
so_hieu = ""
title = ""
effective_date = ""
file1 = ""
file2 = ""
file3 = ""
file4 = ""

# Skip if already extracted

# Collect all file references
files_to_process = []
for file_name in [file1, file2, file3, file4]:
    if pd.notna(file_name):
        files_to_process.append(file_name)

# Combined text from all files for this document
combined_text = ""
source_files = []

# Extract text from all files
for file_name in files_to_process:
    file_path = file_folder / file_name
    if file_path.exists():
        if file_path.suffix.lower() in [".pdf", ".doc", ".docx"]:
            text = ""

            if file_path.suffix.lower() == ".doc":
                file_path = convert_doc_to_docx(file_path, temp_conversion_folder)

            print(f"Extracting text from {file_name}...")

            try:
                if file_path.suffix.lower() == ".docx":
                    text = "\n".join(extract_text_from_docx(file_path))
                elif file_path.suffix.lower() == ".pdf":
                    text = extract_text_from_pdf_google_vision(
                        credential_file=credential_file,
                        bucket_name=bucket_name,
                        gcs_path=f"pdfs/{file_name}",
                        output_path=f"ocr-output/{file_name.split('.')[0]}/",
                        pdf_path=str(file_path)
                    )

                if text:
                    combined_text += text
                    source_files.append(file_name)
                    print(f"Extracted {len(text):,} characters from {file_name}")
                else:
                    print(f"Warning: No text extracted from {file_name}")

            except Exception as e:
                print(f"Error extracting text from {file_name}: {str(e)}")
                import traceback
                traceback.print_exc()

        else:
            print(f"Skipping {file_name}: unsupported format")
    else:
        print(f"Warning: {file_name} not found")

# Handle the extracted text
if combined_text:
    extracted_data = {
        "so_hieu": so_hieu,
        "title": title,
        "effective_date": effective_date,
        "source_files": ", ".join(source_files),
        "combined_text": combined_text,
        "text_length": len(combined_text)
    }
    db.extracted_documents.insert_one(extracted_data)
    print(f"Total extracted: {len(combined_text):,} characters from {len(source_files)} file(s)")

    processing_text = strip_markdown_formatting(combined_text)
    result = parse_document(processing_text, so_hieu)
    for section_id, section_data in result.items():
        # Add metadata
        section_data["document_title"] = clean_title(title)
        section_data["effective_date"] = effective_date
        section_data["source_file"] = source_files
        section_data["_id"] = section_id

        # Use upsert to insert or update based on _id (custom string)
        update_result = sections_collection.update_one(
            {"_id": section_id},
            {
                "$set": section_data,
            },
            upsert=True
        )
