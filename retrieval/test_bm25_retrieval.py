"""
Test script for the complete retrieval system with BM25 ranking
Demonstrates verb extraction, concept/relation matching, and BM25 ranking
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from triplet_extraction.src.db import init_mongo
from triplet_extraction.src.triplet_extraction import init_vncorenlp
from retrieval.src.retrieval_system import retrieve_and_rank, display_results
import phonlp


def main():
    """Main test function"""
    
    # === Initialize MongoDB ===
    print("Initializing MongoDB connection...")
    mongo_client = init_mongo()
    db = mongo_client["KB_PROPERTY_LAW"]
    sections_col = db["legal_sections"]
    concepts_col = db["concepts"]
    relations_col = db["relations"]
    triplets_col = db["triplets_new"]
    
    # === Initialize NLP models ===
    print("\nInitializing NLP models...")
    vncorenlp_path = r"E:\Github\LawAssistant\triplet_extraction\nlp_models\VnCoreNLP-1.2"
    phonlp_path = r"E:\Github\LawAssistant\triplet_extraction\nlp_models\phonlp"
    
    vncorenlp_client = init_vncorenlp(vncorenlp_path)
    phoNLP_model = phonlp.load(save_dir=phonlp_path)
    
    print("\nNLP models loaded successfully!")
    
    # === Test questions ===
    test_questions = [
        "Phải xác nhận tài sản trên đất mới được bán đất có đúng không?",
        "Điều kiện để được cấp giấy chứng nhận quyền sử dụng đất là gì?",
        "Ai có quyền chuyển nhượng quyền sử dụng đất?",
    ]
    
    # === Process each question ===
    for i, question in enumerate(test_questions, 1):
        print("\n" + "="*100)
        print(f"QUESTION {i}: {question}")
        print("="*100)
        
        # Retrieve and rank sections
        ranked_sections = retrieve_and_rank(
            question=question,
            vncorenlp_client=vncorenlp_client,
            phoNLP_model=phoNLP_model,
            sections_col=sections_col,
            concepts_col=concepts_col,
            relations_col=relations_col,
            triplets_col=triplets_col,
            top_k=5,
            use_hybrid=True,
            bm25_weight=0.6,
            triplet_weight=0.4
        )
        
        # Display results
        display_results(ranked_sections, sections_col)
        
        print("\n" + "="*100)
    
    print("\n\nTest completed!")


if __name__ == "__main__":
    main()
