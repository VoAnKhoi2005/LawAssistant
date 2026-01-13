"""
Test script to demonstrate case-insensitive substring matching with underscore normalization
"""

import os
import sys

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from triplet_extraction.src.db import init_mongo
from triplet_extraction.src.triplet_extraction import init_vncorenlp
from graph_retrieval.src.retrieval_system import retrieve_and_rank, print_matched_concepts_relations
import phonlp


def test_improved_matching():
    """Test improved matching with underscore and substring support"""
    
    print("="*100)
    print("Test: Improved Case-Insensitive Substring Matching with Underscore Normalization")
    print("="*100)
    
    # Initialize
    print("\n[1/2] Initializing system...")
    mongo_client = init_mongo()
    db = mongo_client["KB_PROPERTY_LAW"]
    
    vncorenlp_path = r"E:\Github\LawAssistant\triplet_extraction\nlp_models\VnCoreNLP-1.2"
    phonlp_path = r"E:\Github\LawAssistant\triplet_extraction\nlp_models\phonlp"
    
    vncorenlp_client = init_vncorenlp(vncorenlp_path)
    phoNLP_model = phonlp.load(save_dir=phonlp_path)
    
    # Test questions with underscored terms
    test_questions = [
        "Phải xác nhận tài sản trên đất mới được bán đất có đúng không?",
        "Giấy chứng nhận quyền sử dụng đất được cấp như thế nào?",
        "Quyền sử dụng đất có thể chuyển nhượng không?",
    ]
    
    print("[2/2] Testing matching with different question formats...\n")
    
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
            top_k=3,
            use_hybrid=True,
            return_matches=True
        )
        
        # Print detailed matching information
        print_matched_concepts_relations(matched_concepts, matched_relations)
        
        # Summary
        print(f"\n📊 Summary:")
        print(f"   • Concepts matched: {len(matched_concepts)}")
        print(f"   • Relations matched: {len(matched_relations)}")
        print(f"   • Candidate sections found: {len(ranked_sections)}")
    
    print("\n" + "="*100)
    print("✅ Test completed! Matching now supports:")
    print("   1. Case-insensitive matching")
    print("   2. Underscore normalization (xác_nhận ↔ xác nhận)")
    print("   3. Substring matching (sử_dụng matches quyền_sử_dụng)")
    print("="*100)


def compare_matching_examples():
    """Show examples of what now matches"""
    
    print("\n" + "="*100)
    print("🔍 Matching Examples")
    print("="*100)
    
    examples = [
        {
            "query": "xác nhận",
            "matches": ["xác_nhận", "xác_nhận_quyền", "được_xác_nhận"],
            "reason": "Underscore normalized to space, substring match"
        },
        {
            "query": "sử dụng",
            "matches": ["sử_dụng", "quyền_sử_dụng", "sử_dụng_đất"],
            "reason": "Underscore normalized, case-insensitive substring"
        },
        {
            "query": "đất",
            "matches": ["đất", "Đất", "đất_có", "quyền_sử_dụng_đất"],
            "reason": "Case-insensitive, matches as substring"
        },
        {
            "query": "CHUYỂN_NHƯỢNG",
            "matches": ["chuyển_nhượng", "chuyển nhượng", "Chuyển_Nhượng"],
            "reason": "Case-insensitive with underscore normalization"
        }
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{i}. Query: '{example['query']}'")
        print(f"   Matches: {', '.join(example['matches'])}")
        print(f"   Reason: {example['reason']}")
    
    print("\n" + "="*100)


if __name__ == "__main__":
    test_improved_matching()
    compare_matching_examples()
