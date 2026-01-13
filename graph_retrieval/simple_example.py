"""
Simple example demonstrating the complete graph_retrieval pipeline
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from triplet_extraction.src.db import init_mongo
from triplet_extraction.src.triplet_extraction import init_vncorenlp
from graph_retrieval.src.retrieval_system import retrieve_and_rank, display_results
import phonlp


def simple_test():
    """Simple test with one question"""
    
    print("="*100)
    print("Legal Document Retrieval System - Simple Test")
    print("="*100)
    
    # Initialize MongoDB
    print("\n[1/4] Connecting to MongoDB...")
    mongo_client = init_mongo()
    db = mongo_client["KB_PROPERTY_LAW"]
    
    # Initialize NLP models
    print("[2/4] Loading NLP models...")
    vncorenlp_path = r"E:\Github\LawAssistant\triplet_extraction\nlp_models\VnCoreNLP-1.2"
    phonlp_path = r"E:\Github\LawAssistant\triplet_extraction\nlp_models\phonlp"
    
    vncorenlp_client = init_vncorenlp(vncorenlp_path)
    phoNLP_model = phonlp.load(save_dir=phonlp_path)
    
    # Test question
    question = "Phải xác nhận tài sản trên đất mới được bán đất có đúng không?"
    print(f"\n[3/4] Processing question: {question}")
    
    # Retrieve and rank
    print("[4/4] Retrieving and ranking sections...")
    ranked_sections = retrieve_and_rank(
        question=question,
        vncorenlp_client=vncorenlp_client,
        phoNLP_model=phoNLP_model,
        sections_col=db["legal_sections"],
        concepts_col=db["concepts"],
        relations_col=db["relations"],
        triplets_col=db["triplets_new"],
        top_k=5,
        use_hybrid=True,
        bm25_weight=0.6,
        triplet_weight=0.4
    )
    
    # Display results
    display_results(ranked_sections, db["legal_sections"])
    
    print("\n" + "="*100)
    print("Test completed successfully!")
    print("="*100)


if __name__ == "__main__":
    simple_test()
