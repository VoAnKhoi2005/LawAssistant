"""
Demo script showing matched concepts and relations
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from triplet_extraction.src.db import init_mongo
from triplet_extraction.src.triplet_extraction import init_vncorenlp
from retrieval.src.retrieval_system import retrieve_and_rank, display_results, print_matched_concepts_relations
import phonlp


def demo_concept_relation_matching():
    """Demo showing concept and relation matching"""
    
    print("="*100)
    print("Demo: Concept and Relation Matching in Legal Document Retrieval")
    print("="*100)
    
    # Initialize
    print("\nInitializing system...")
    mongo_client = init_mongo()
    db = mongo_client["KB_PROPERTY_LAW"]
    
    vncorenlp_path = r"E:\Github\LawAssistant\triplet_extraction\nlp_models\VnCoreNLP-1.2"
    phonlp_path = r"E:\Github\LawAssistant\triplet_extraction\nlp_models\phonlp"
    
    vncorenlp_client = init_vncorenlp(vncorenlp_path)
    phoNLP_model = phonlp.load(save_dir=phonlp_path)
    
    # Test questions
    test_questions = [
        "Phải xác nhận tài sản trên đất mới được bán đất có đúng không?",
        "Điều kiện để được cấp giấy chứng nhận quyền sử dụng đất là gì?",
        "Ai có quyền chuyển nhượng quyền sử dụng đất?",
    ]
    
    for i, question in enumerate(test_questions, 1):
        print("\n" + "="*100)
        print(f"QUESTION {i}: {question}")
        print("="*100)
        
        # Retrieve with matches
        ranked_sections, matched_concepts, matched_relations = retrieve_and_rank(
            question=question,
            vncorenlp_client=vncorenlp_client,
            phoNLP_model=phoNLP_model,
            sections_col=db["legal_sections"],
            concepts_col=db["concepts"],
            relations_col=db["relations"],
            triplets_col=db["triplets_new"],
            top_k=5,
            use_hybrid=True,
            return_matches=True
        )
        
        # Print detailed matching information
        print_matched_concepts_relations(matched_concepts, matched_relations)
        
        # Display top results
        print("\n" + "="*80)
        print("=== TOP 3 RESULTS ===")
        print("="*80)
        
        for idx, section in enumerate(ranked_sections[:3], 1):
            print(f"\n--- Rank {idx} ---")
            if 'hybrid_score' in section:
                print(f"Hybrid Score: {section['hybrid_score']:.4f} (BM25: {section['bm25_score']:.4f}, Triplet: {section.get('triplet_score', 0)})")
            else:
                print(f"BM25 Score: {section['bm25_score']:.4f}")
            
            section_doc = db["legal_sections"].find_one({'_id': section['section_id']})
            if section_doc:
                print(f"Path: {section_doc.get('full_path', 'N/A')}")
                content = section_doc.get('content', '')
                preview = content[:150] + "..." if len(content) > 150 else content
                print(f"Content: {preview}")
    
    print("\n" + "="*100)
    print("Demo completed!")
    print("="*100)


if __name__ == "__main__":
    demo_concept_relation_matching()
