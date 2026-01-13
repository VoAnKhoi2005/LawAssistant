import time

from graph_retrieval.src.dpr_ranker import DPRRanker
from triplet_extraction.src.db import init_mongo
from triplet_extraction.src.triplet_extraction import init_vncorenlp
from graph_retrieval.src.retrieval_system import retrieve_and_rank
import phonlp


def display_results(ranked_results, sections_col=None, top_n=5):
    """
    Display ranked graph_retrieval results
    
    Args:
        ranked_results: List of ranked section dictionaries
        sections_col: MongoDB sections collection (optional, for fallback)
        top_n: Number of top results to display
    """
    print(f"\n{'='*80}")
    print(f"TOP {min(top_n, len(ranked_results))} RESULTS")
    print(f"{'='*80}")
    
    for i, result in enumerate(ranked_results[:top_n], 1):
        section_id = result.get('section_id') or result.get('_id')
        full_path = result.get('full_path')
        so_hieu = result.get('so_hieu', 'N/A')
        content = result.get('content', 'N/A')[:200] + "..."
        
        # Scores
        bm25_score = result.get('bm25_score', 0.0)
        dpr_score = result.get('dpr_score', 0.0)
        triplet_score = result.get('triplet_score', 0.0)
        hybrid_score = result.get('hybrid_score', bm25_score)
        
        print(f"\n[{i}] Section ID: {section_id}")
        print(f"    So Hieu: {so_hieu}")
        print(f"    Full Path: {full_path}")
        print(f"    Hybrid Score: {hybrid_score:.4f}")
        if dpr_score > 0:
            print(f"    - BM25: {bm25_score:.4f}, DPR: {dpr_score:.4f}, Triplet: {triplet_score:.4f}")
        else:
            print(f"    - BM25: {bm25_score:.4f}, Triplet: {triplet_score:.4f}")
        print(f"    Content: {content}")


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
        # "Phải xác nhận tài sản trên đất mới được bán đất có đúng không?",
        # "Điều kiện để được cấp giấy chứng nhận quyền sử dụng đất là gì?",
        # "Điều kiện chuyển nhượng quyền sử dụng đất là gì?",
        # "Ai có quyền chuyển nhượng quyền sử dụng đất?",
        "Các loại đất nào được sử dụng kết hợp đa mục đích?"
    ]
    
    # === Process each question ===
    for i, question in enumerate(test_questions, 1):
        print("\n" + "="*100)
        print(f"QUESTION {i}: {question}")
        print("="*100)

        dpr_ranker = DPRRanker(
            model_name="VoVanPhuc/sup-SimCSE-VietNamese-phobert-base"
        )
        
        # Retrieve and rank sections
        ranked_results = retrieve_and_rank(
            question=question,
            vncorenlp_client=vncorenlp_client,
            phoNLP_model=phoNLP_model,
            sections_col=sections_col,
            concepts_col=concepts_col,
            relations_col=relations_col,
            triplets_col=triplets_col,
            k_hops=2,
            use_khop=True,
            dpr_ranker=dpr_ranker,
            use_dpr=True,
            top_k=20
        )
        
        # Display results
        display_results(ranked_results, sections_col, top_n=20)
        
        print("\n" + "="*100)
    
    print("\n\nTest completed!")


if __name__ == "__main__":
    start = time.perf_counter()

    main()

    end = time.perf_counter()
    print(f"Execution time: {end - start:.4f} seconds")


