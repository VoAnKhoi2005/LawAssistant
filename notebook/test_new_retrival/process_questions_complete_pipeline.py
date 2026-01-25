"""
Complete Sequential Pipeline for Legal QA with Retrieval
Following the notebook workflow step by step:
1. Load questions from Excel
2. Query decomposition (spell check + sub-questions)
3. Entity & relation extraction
4. Concept linking (exact match + FAISS)
5. Triplet retrieval from MongoDB
6. Legal section enrichment
7. FAISS retrieval on sections
8. BM25 + DPR reranking
9. Context building
10. Final QA with context
11. Create batch API JSONL files (split by 2M tokens)
"""

import pandas as pd
import json
import os
import numpy as np
import faiss
import pickle
import tiktoken
from pathlib import Path
from dotenv import load_dotenv
from collections import defaultdict
from typing import List, Dict
from bson import ObjectId

# Import project modules
from src.db import init_mongo
from src.triplet_extraction.llm import init_gpt
from src.retrieval.utils.collect_content import collect_sections_content_upward
from rank_bm25 import BM25Okapi

# Import prompts
import sys
sys.path.append(r"E:\Github\LawAssistant\notebook\test_new_retrival")
from query_decompose_prompt import SYSTEM_PROMPT_QUESTION_ENTITIES, SYSTEM_PROMPT_QUERY_DECOMPOSE

# Configuration
INPUT_EXCEL = r"E:\Github\LawAssistant\data\facebook_question.xlsx"
OUTPUT_DIR = r"E:\Github\LawAssistant\notebook\test_new_retrival\QA_batch_requests"
CHECKPOINT_DIR = r"E:\Github\LawAssistant\notebook\test_new_retrival\QA_batch_requests\checkpoints"
NUM_QUESTIONS = 120
QUESTION_COLUMN = "Câu hỏi"
MAX_TOKENS_PER_BATCH = 2_000_000

# Retrieval parameters
TOP_K = 10
FAISS_TOP_N = 100
TOP_K_RERANKING = 10
SIM_THRESHOLD = 0.75

# System prompt for QA
SYSTEM_PROMPT_QA = """
Bạn là trợ lý AI chuyên gia. Nhiệm vụ của bạn là trả lời câu hỏi dựa hoàn toàn trên NGỮ CẢNH được cung cấp và xuất kết quả ở định dạng JSON với hai trường riêng biệt: "answer" (câu trả lời của bạn) và "source" (danh sách các nguồn đã sử dụng).

# HƯỚNG DẪN:
- Bước 1: Đọc kỹ toàn bộ NGỮ CẢNH.
- Bước 2: Tìm các đoạn liên quan trực tiếp đến câu hỏi.
- Bước 3: Tổng hợp và diễn giải lại bằng lời của bạn, có thể giải thích thêm cho dễ hiểu.
- Bước 4: Lúc trả lời phải trích dẫn rõ ràng trong dấu ngoặc.
- Bước 5: Xét ngày có hiệu lực, những văn bản nào mới hơn thay thế cho các văn bản cũ hơn.
- Bước 6: Nếu thông tin trong NGỮ CẢNH mâu thuẫn hoặc không đủ, hãy nêu rõ điều đó và KHÔNG được bịa thêm.
- Bước 7: Ở cuối phải ghi rõ lại những nguồn đã sử dụng.

# QUY TẮC:
- Không sử dụng kiến thức bên ngoài NGỮ CẢNH.
- Không trích dẫn nguyên văn quá dài, hãy tóm tắt lại cho dễ hiểu.
- Trả lời bằng tiếng Việt tự nhiên, rõ ràng.

# ĐỊNH DẠNG KẾT QUẢ YÊU CẦU:
- Phải trả lời duy nhất ở dạng JSON với hai trường:
    - "answer": chứa phần trả lời chi tiết, có trích dẫn nguồn rõ ràng trong ngoặc.
    - "source": danh sách rõ ràng các tài liệu, đoạn được sử dụng (ghi đủ tên và thông tin xác định nguồn).

# Output Format

Kết quả phải là một đối tượng JSON với hai trường chính, không có bất cứ văn bản giải thích nào bên ngoài JSON.
Ví dụ:

{
  "answer": "Theo văn bản [Nghị định 123/2020/NĐ-CP, Điều 5], người bán phải lập hóa đơn điện tử khi bán hàng hóa và cung cấp dịch vụ. Nếu có trường hợp ngoại lệ, hãy đối chiếu thêm các quy định mới hơn nếu có trích dẫn trong NGỮ CẢNH.",
  "source": [
    "Nghị định 123/2020/NĐ-CP, Điều 5",
  ]
}

# Notes

- Tuyệt đối không chèn thêm bất cứ nội dung nào bên ngoài đối tượng JSON.
- Nếu NGỮ CẢNH mâu thuẫn hoặc thiếu, hãy nêu rõ trong "answer" và ghi nguồn liên quan trong "source".
- Trường "source" phải liệt kê đầy đủ những nguồn được sử dụng để đưa ra câu trả lời.

# Nhắc lại yêu cầu chính: Trả lời vào hai trường "answer" và "source" trong JSON, hoàn toàn dựa trên NGỮ CẢNH. Không thêm hoặc lược bỏ trường.
"""

# Initialize connections
load_dotenv()
mongo_client = init_mongo()
db = mongo_client["KB_PROPERTY_LAW"]
gpt_client = init_gpt()

# Load FAISS indices
print("Loading FAISS indices...")
concept_index = faiss.read_index(r"E:\Github\LawAssistant\notebook\test_new_retrival\concept.faiss")
sections_index = faiss.read_index(r"E:\Github\LawAssistant\notebook\test_new_retrival\sections.faiss")

with open(r"E:\Github\LawAssistant\notebook\test_new_retrival\concept_id_map.pkl", "rb") as f:
    vector_to_concept = pickle.load(f)

with open(r"E:\Github\LawAssistant\notebook\test_new_retrival\section_id_map.pkl", "rb") as f:
    vector_to_section = pickle.load(f)

print("FAISS indices loaded successfully!\n")


def save_checkpoint(question_idx: int, stage: str, data: dict):
    """Save checkpoint for a specific question and stage."""
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    checkpoint_file = os.path.join(CHECKPOINT_DIR, f"q_{question_idx}_{stage}.json")
    
    checkpoint_data = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "question_idx": question_idx,
        "stage": stage,
        "data": data
    }
    
    with open(checkpoint_file, 'w', encoding='utf-8') as f:
        json.dump(checkpoint_data, f, ensure_ascii=False, indent=2)


def load_checkpoint(question_idx: int, stage: str):
    """Load checkpoint for a specific question and stage."""
    checkpoint_file = os.path.join(CHECKPOINT_DIR, f"q_{question_idx}_{stage}.json")
    
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r', encoding='utf-8') as f:
            checkpoint_data = json.load(f)
        return checkpoint_data["data"]
    return None


def get_completed_questions():
    """Get list of question indices that have been fully processed."""
    if not os.path.exists(CHECKPOINT_DIR):
        return set()
    
    completed = set()
    for filename in os.listdir(CHECKPOINT_DIR):
        if filename.startswith("q_") and filename.endswith("_final.json"):
            question_idx = int(filename.split("_")[1])
            completed.add(question_idx)
    
    return completed


def count_tokens(text, model="gpt-4o-mini"):
    """Count tokens in text using tiktoken."""
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")
    return len(encoding.encode(text))


def embed(text: str) -> list[float]:
    """Generate embedding using OpenAI API."""
    response = gpt_client.embeddings.create(
        model="text-embedding-3-large",
        input=text
    )
    embedding = np.array(response.data[0].embedding, dtype="float32")
    embedding = embedding / np.linalg.norm(embedding)
    return embedding.tolist()


def search_concepts(query_embedding, top_k=TOP_K, sim_threshold=SIM_THRESHOLD):
    """Search for concepts using FAISS."""
    q = np.array([query_embedding], dtype="float32")
    faiss.normalize_L2(q)
    
    scores, indices = concept_index.search(q, top_k)
    
    concept_scores = defaultdict(float)
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1 or score < sim_threshold:
            continue
        cid = vector_to_concept[idx]
        if score > concept_scores[cid]:
            concept_scores[cid] = score
    
    return sorted(concept_scores.items(), key=lambda x: x[1], reverse=True)


def get_openai_embedding(text: str, model: str = "text-embedding-3-large") -> np.ndarray:
    """Get OpenAI embedding for section retrieval."""
    response = gpt_client.embeddings.create(input=text, model=model)
    emb = np.array(response.data[0].embedding, dtype="float32")
    return emb / np.linalg.norm(emb)


def preprocess_text(text: str):
    """Preprocess text for BM25."""
    return text.lower().split()


def retrieve_faiss_candidates(query: str, top_n: int):
    """Retrieve FAISS candidates for sections."""
    query_emb = get_openai_embedding(query)
    D, I = sections_index.search(query_emb.reshape(1, -1), top_n)
    return {
        vector_to_section[idx]: float(score)
        for score, idx in zip(D[0], I[0])
        if idx in vector_to_section
    }


def rerank_sections(query: str, sections: List[Dict], faiss_scores: Dict[str, float], top_k: int):
    """Rerank sections using BM25 + DPR."""
    if not sections:
        return []
    
    texts = [
        f"{s.get('title', '')} {s.get('content', '')} {s.get('document_title', '')}"
        for s in sections
    ]
    
    tokenized_corpus = [preprocess_text(t) for t in texts]
    bm25 = BM25Okapi(tokenized_corpus)
    bm25_scores = bm25.get_scores(preprocess_text(query))
    if bm25_scores.max() > 0:
        bm25_scores = bm25_scores / bm25_scores.max()
    
    dpr_scores = np.array([faiss_scores.get(s["_id"], 0.0) for s in sections])
    if dpr_scores.max() > 0:
        dpr_scores = dpr_scores / dpr_scores.max()
    
    combined_scores = 0.3 * bm25_scores + 0.7 * dpr_scores
    ranked_idx = np.argsort(combined_scores)[::-1][:top_k]
    
    results = []
    for i in ranked_idx:
        sec = sections[i].copy()
        sec["bm25_score"] = float(bm25_scores[i])
        sec["dpr_score"] = float(dpr_scores[i])
        sec["combined_score"] = float(combined_scores[i])
        results.append(sec)
    
    return results


def process_question(question: str, question_idx: int):
    """
    Process a single question through the complete pipeline.
    Returns the context and metadata for batch API creation.
    Saves checkpoints at each stage and is fully resumeable.
    """
    print(f"\n{'='*70}")
    print(f"Processing Question {question_idx}: {question[:80]}...")
    
    # Check if final result exists
    final_checkpoint = load_checkpoint(question_idx, "final")
    if final_checkpoint:
        print("✓ Found completed checkpoint, loading...")
        return final_checkpoint
    
    # Step 1: Query Decomposition
    print("\n[1] Query Decomposition...")
    decompose_checkpoint = load_checkpoint(question_idx, "decompose")
    
    if decompose_checkpoint:
        print("  ↻ Loading from checkpoint...")
        query_data = decompose_checkpoint
    else:
        response = gpt_client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT_QUERY_DECOMPOSE},
                {"role": "user", "content": f"Question: {question}"}
            ]
        )
        decomposed_output = response.output_text
        query_data = json.loads(decomposed_output)
        save_checkpoint(question_idx, "decompose", query_data)
        print("  ✓ Saved checkpoint")
    
    corrected_question = query_data.get("corrected_question", question)
    decomposed_questions = query_data.get("decomposed_questions", [question])
    print(f"  ✓ Decomposed into {len(decomposed_questions)} sub-questions")
    
    # Step 2: Entity & Relation Extraction
    print("\n[2] Entity & Relation Extraction...")
    extraction_checkpoint = load_checkpoint(question_idx, "extraction")
    
    if extraction_checkpoint:
        print("  ↻ Loading from checkpoint...")
        entities = set(extraction_checkpoint["entities"])
        relations = set(extraction_checkpoint["relations"])
    else:
        question_list = repr(decomposed_questions)
        response = gpt_client.responses.create(
            model="gpt-4.1-mini",
            input=[
                {"role": "system", "content": SYSTEM_PROMPT_QUESTION_ENTITIES},
                {"role": "user", "content": f"Question List: {question_list}"}
            ]
        )
        info_extraction_output = response.output_text
        info_extraction_data = json.loads(info_extraction_output)
        
        entities = set()
        relations = set()
        if isinstance(info_extraction_data, list):
            for item in info_extraction_data:
                entities.update(item.get("entities", []))
                relations.update(item.get("relations", []))
        else:
            entities.update(info_extraction_data.get("entities", []))
            relations.update(info_extraction_data.get("relations", []))
        
        save_checkpoint(question_idx, "extraction", {
            "entities": list(entities),
            "relations": list(relations)
        })
        print("  ✓ Saved checkpoint")
    
    print(f"  ✓ Extracted {len(entities)} entities, {len(relations)} relations")
    
    # Step 3: Concept Linking
    print("\n[3] Concept Linking...")
    linking_checkpoint = load_checkpoint(question_idx, "linking")
    
    if linking_checkpoint:
        print("  ↻ Loading from checkpoint...")
        concept_ids = set(linking_checkpoint["concept_ids"])
    else:
        concept_ids = set()
        
        # Exact match
        exact_concepts = list(db.concepts.find(
            {
                "$or": [
                    {"name": {"$in": list(entities)}},
                    {"synonyms": {"$elemMatch": {"$in": list(entities)}}}
                ]
            },
            {"_id": 1}
        ))
        for concept in exact_concepts:
            concept_ids.add(concept["_id"])
        
        # FAISS similarity search
        for e in entities:
            query_embedding = embed(e)
            results = search_concepts(query_embedding)
            for cid, score in results:
                concept_ids.add(cid)
        
        save_checkpoint(question_idx, "linking", {
            "concept_ids": [str(cid) for cid in concept_ids]
        })
        print("  ✓ Saved checkpoint")
    
    linked_concept_oids = [ObjectId(cid) for cid in concept_ids]
    print(f"  ✓ Linked {len(linked_concept_oids)} concepts")
    
    # Step 4: Triplet Retrieval
    print("\n[4] Triplet Retrieval...")
    triplet_checkpoint = load_checkpoint(question_idx, "triplets")
    
    if triplet_checkpoint:
        print("  ↻ Loading from checkpoint...")
        # Convert documents section_id strings back to ObjectId
        triplets = []
        for t in triplet_checkpoint:
            for doc in t.get("documents", []):
                if isinstance(doc["section_id"], str):
                    doc["section_id"] = ObjectId(doc["section_id"])
            triplets.append(t)
    else:
        pipeline = [
            {
                "$match": {
                    "subject_id": {"$in": linked_concept_oids},
                    "object_id": {"$in": linked_concept_oids}
                }
            },
            {"$lookup": {"from": "concepts", "localField": "subject_id", "foreignField": "_id", "as": "subject"}},
            {"$unwind": "$subject"},
            {"$lookup": {"from": "concepts", "localField": "object_id", "foreignField": "_id", "as": "object"}},
            {"$unwind": "$object"},
            {"$lookup": {"from": "relations", "localField": "relation_id", "foreignField": "_id", "as": "relation"}},
            {"$unwind": "$relation"},
            {"$match": {"$expr": {"$ne": ["$subject_id", "$object_id"]}}},
            {"$project": {"_id": 0, "subject": "$subject.name", "relation": "$relation.name", "object": "$object.name", "documents": 1}}
        ]
        triplets = list(db.triplets.aggregate(pipeline))
        
        # Serialize for checkpoint (convert ObjectId to string)
        triplets_serialized = []
        for t in triplets:
            t_copy = t.copy()
            t_copy["documents"] = [
                {**doc, "section_id": str(doc["section_id"])}
                for doc in t_copy.get("documents", [])
            ]
            triplets_serialized.append(t_copy)
        
        save_checkpoint(question_idx, "triplets", triplets_serialized)
        print("  ✓ Saved checkpoint")
    
    print(f"  ✓ Retrieved {len(triplets)} triplets")
    
    # Step 5: Legal Section Enrichment
    print("\n[5] Legal Section Enrichment...")
    section_ids = set()
    for t in triplets:
        for doc in t.get("documents", []):
            section_ids.add(doc["section_id"])
    
    section_ids = list(section_ids)
    legal_sections = list(db.legal_sections.find(
        {"_id": {"$in": section_ids}},
        {"_id": 1, "title": 1, "content": 1, "full_path": 1, "so_hieu": 1, "document_title": 1}
    ))
    section_map = {s["_id"]: s for s in legal_sections}
    
    # Get related sections via relations
    relations_data = list(db.legal_section_relations.find({
        "$or": [
            {"source": {"$in": section_ids}},
            {"target": {"$in": section_ids}}
        ]
    }))
    
    related_section_ids = set()
    for r in relations_data:
        if r["source"] in section_ids:
            related_section_ids.add(r["target"])
        if r["target"] in section_ids:
            related_section_ids.add(r["source"])
    related_section_ids -= set(section_ids)
    
    related_sections = list(db.legal_sections.find(
        {"_id": {"$in": list(related_section_ids)}},
        {"_id": 1, "title": 1, "content": 1, "full_path": 1, "so_hieu": 1, "document_title": 1}
    ))
    related_section_map = {s["_id"]: s for s in related_sections}
    print(f"  ✓ Found {len(section_map)} direct sections, {len(related_section_map)} related sections")
    
    # Step 6: FAISS Retrieval & Reranking
    print("\n[6] FAISS Retrieval & Reranking...")
    faiss_global_scores = retrieve_faiss_candidates(question, FAISS_TOP_N)
    
    for t in triplets:
        triplet_section_ids = {d["section_id"] for d in t.get("documents", [])}
        
        direct_candidates = [
            section_map[sid] for sid in triplet_section_ids
            if sid in faiss_global_scores and sid in section_map
        ]
        
        if not direct_candidates:
            direct_candidates = [section_map[sid] for sid in triplet_section_ids if sid in section_map]
        
        related_candidates = []
        for r in relations_data:
            if r["source"] in triplet_section_ids and r["target"] in related_section_map:
                sid = r["target"]
                if sid in faiss_global_scores:
                    related_candidates.append({
                        **related_section_map[sid],
                        "relation_type": r["type"],
                        "amendment_types": r.get("amendment_types", [])
                    })
            if r["target"] in triplet_section_ids and r["source"] in related_section_map:
                sid = r["source"]
                if sid in faiss_global_scores:
                    related_candidates.append({
                        **related_section_map[sid],
                        "relation_type": r["type"],
                        "amendment_types": r.get("amendment_types", [])
                    })
        
        t["legal_sections"] = rerank_sections(question, direct_candidates, faiss_global_scores, TOP_K)
        t["related_legal_sections"] = rerank_sections(question, related_candidates, faiss_global_scores, TOP_K)
    
    # Step 7: Final Ranking & Context Building
    print("\n[7] Final Ranking & Context Building...")
    all_ranked = {}
    for t in triplets:
        for s in t.get("legal_sections", []):
            sid = s["_id"]
            score = s["combined_score"]
            if sid not in all_ranked or score > all_ranked[sid]["combined_score"]:
                all_ranked[sid] = s
        
        for s in t.get("related_legal_sections", []):
            sid = s["_id"]
            score = s["combined_score"]
            if sid not in all_ranked or score > all_ranked[sid]["combined_score"]:
                all_ranked[sid] = s
    
    top_k_result = sorted(all_ranked.values(), key=lambda x: x["combined_score"], reverse=True)[:TOP_K_RERANKING]
    
    # Collect full content
    sections_content = collect_sections_content_upward(db.legal_sections, [s['_id'] for s in top_k_result])
    for section in top_k_result:
        section['content'] = sections_content.get(section['_id'], section.get('content', ''))
    
    # Get document metadata
    all_so_hieu = set()
    for s in top_k_result:
        so_hieu = s.get("so_hieu")
        if so_hieu:
            all_so_hieu.add(so_hieu)
    
    documents = db.documents.find({"so_hieu": {"$in": list(all_so_hieu)}})
    documents_by_so_hieu = {doc["so_hieu"]: doc for doc in documents}
    
    # Build context payload
    llm_payload = []
    for s in top_k_result:
        so_hieu = s.get("so_hieu")
        document = documents_by_so_hieu.get(so_hieu, {}) if so_hieu else {}
        effective_date_str = document["effective_date"].strftime("%Y-%m-%d") if document.get("effective_date") else ""
        doc_title = document.get("title", "").strip().replace("\n", " ")
        
        llm_payload.append({
            "so_hieu": s.get("so_hieu", ""),
            "document_title": doc_title,
            "full_path": s.get("full_path", "").replace("_", ", "),
            "effective_date": effective_date_str,
            "content": s.get("content", "")
        })
    
    context_str = json.dumps(llm_payload, ensure_ascii=False, indent=2)
    print(f"  ✓ Built context with {len(llm_payload)} sections")
    
    # Save final result
    final_result = {
        "original_question": question,
        "corrected_question": corrected_question,
        "decomposed_questions": decomposed_questions,
        "entities": list(entities),
        "relations": list(relations),
        "context": context_str,
        "num_sections": len(llm_payload)
    }
    
    save_checkpoint(question_idx, "final", final_result)
    print("  ✓ Saved final checkpoint")
    
    return final_result


def create_batch_requests():
    """Main function to process all questions and create batch API files."""
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    
    print(f"{'='*70}")
    print(f"SEQUENTIAL PROCESSING PIPELINE WITH RESUME CAPABILITY")
    print(f"{'='*70}\n")
    
    # Check for existing progress
    completed_questions = get_completed_questions()
    if completed_questions:
        print(f"✓ Found {len(completed_questions)} previously completed questions")
        print(f"  Resuming from checkpoint...\n")
    
    # Read Excel
    print(f"Reading Excel file: {INPUT_EXCEL}")
    df = pd.read_excel(INPUT_EXCEL)
    print(f"Total questions: {len(df)}")
    
    df_subset = df.head(NUM_QUESTIONS)
    df_subset = df_subset[df_subset[QUESTION_COLUMN].notna()]
    df_subset = df_subset[df_subset[QUESTION_COLUMN].str.strip() != ""]
    print(f"Valid questions to process: {len(df_subset)}")
    print(f"Questions to skip (already done): {len(completed_questions)}")
    print(f"Questions remaining: {len(df_subset) - len(completed_questions)}\n")
    
    # Process each question
    all_requests = []
    
    for idx, row in df_subset.iterrows():
        question = str(row[QUESTION_COLUMN]).strip()
        
        # Skip if already completed
        if idx in completed_questions:
            print(f"\n[SKIP] Question {idx} already completed")
            # Load final checkpoint
            result = load_checkpoint(idx, "final")
        else:
            try:
                result = process_question(question, idx)
            except Exception as e:
                print(f"\nError processing question {idx}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        if result:
            # Create batch API request with full context
            batch_request = {
                "custom_id": f"qa-{idx}",
                "method": "POST",
                "url": "/v1/chat/completions",
                "body": {
                    "model": "gpt-4o-mini",
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT_QA},
                        {"role": "user", "content": f"Ngữ cảnh: {result['context']}.\n\nCâu hỏi: {result['corrected_question']}.\n\nHãy trả lời câu hỏi dựa hoàn toàn trên ngữ cảnh đã cho."}
                    ],
                    "temperature": 0.3
                }
            }
            
            request_json = json.dumps(batch_request, ensure_ascii=False)
            request_tokens = count_tokens(request_json)
            
            all_requests.append({
                "request": batch_request,
                "tokens": request_tokens,
                "metadata": result
            })
            
            if idx not in completed_questions:
                print(f"\nQuestion {idx} processed successfully ({request_tokens:,} tokens)")
            else:
                print(f"  ✓ Loaded from checkpoint ({request_tokens:,} tokens)")
        else:
            print(f"\nQuestion {idx} skipped due to error")
    
    # Split into batches
    print(f"\n{'='*70}")
    print(f"CREATING BATCH FILES")
    print(f"{'='*70}\n")
    
    batches = []
    current_batch = []
    current_batch_tokens = 0
    
    for item in all_requests:
        request = item["request"]
        tokens = item["tokens"]
        
        if current_batch_tokens + tokens > MAX_TOKENS_PER_BATCH and current_batch:
            batches.append({"requests": current_batch, "tokens": current_batch_tokens})
            current_batch = []
            current_batch_tokens = 0
        
        current_batch.append(request)
        current_batch_tokens += tokens
    
    if current_batch:
        batches.append({"requests": current_batch, "tokens": current_batch_tokens})
    
    # Write batch files
    output_files = []
    for batch_idx, batch in enumerate(batches, 1):
        output_file = os.path.join(OUTPUT_DIR, f"batch_{batch_idx}.jsonl")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            for request in batch["requests"]:
                f.write(json.dumps(request, ensure_ascii=False) + '\n')
        
        output_files.append(output_file)
        print(f"✓ Batch {batch_idx}: {len(batch['requests'])} requests, {batch['tokens']:,} tokens")
        print(f"  File: {output_file}")
    
    # Summary
    print(f"\n{'='*70}")
    print(f"SUMMARY")
    print(f"Questions processed : {len(all_requests)}/{len(df_subset)}")
    print(f"Total batches       : {len(batches)}")
    print(f"Output directory    : {OUTPUT_DIR}")
    print(f"Checkpoint directory: {CHECKPOINT_DIR}")
    print()
    
    # Save processing metadata
    metadata_file = os.path.join(OUTPUT_DIR, "processing_metadata.json")
    metadata = {
        "timestamp": pd.Timestamp.now().isoformat(),
        "total_questions": len(df_subset),
        "processed_questions": len(all_requests),
        "total_batches": len(batches),
        "batch_files": output_files
    }
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"✓ Saved processing metadata to: {metadata_file}\n")
    
    return output_files


if __name__ == "__main__":
    try:
        output_files = create_batch_requests()
        
        print(f"\n{'='*70}")
        print(f"PIPELINE COMPLETED SUCCESSFULLY")
        print(f"Output: {OUTPUT_DIR}")
        print(f"Checkpoints: {CHECKPOINT_DIR}")
        print(f"Batch files: {len(output_files)}")
        
    except KeyboardInterrupt:
        print("\n\nPipeline interrupted by user")
        print("✓ All progress has been saved to checkpoints")
        print("✓ Run the script again to resume from where you left off")
    except Exception as e:
        print(f"\n\nPipeline failed with error: {str(e)}")
        print("✓ Progress saved up to the point of failure")
        print("✓ Run the script again to resume")
        import traceback
        traceback.print_exc()
