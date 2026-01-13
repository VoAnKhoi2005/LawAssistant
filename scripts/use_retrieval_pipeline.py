"""
Usage Script for Unified Retrieval Pipeline
============================================

This script demonstrates various ways to use the retrieval pipeline
at E:\Github\LawAssistant\src\retrieval\retrieval_pipeline.py

The pipeline combines:
1. Query Preprocessing (normalize + LLM refine)
2. Graph Retrieval (knowledge graph + triplets)
3. Semantic Retrieval (FAISS + BM25)
4. Hybrid Ranking with DPR to return top 20 most relevant legal sections
"""

import os
import sys
import time
from dotenv import load_dotenv
import phonlp
from src.db import init_mongo
from src.retrieval.retrieval_pipeline import RetrievalPipeline, create_pipeline
from src.retrieval.utils.print_result import format_results_for_llm
from src.triplet_extraction.pos_taging import init_vncorenlp


# ============================================================================
# BASIC USAGE
# ============================================================================

def basic_usage():
    """
    Basic usage example - simplest way to use the pipeline
    """
    print("\n" + "="*80)
    print("BASIC USAGE EXAMPLE")
    print("="*80)

    current_dir = os.getcwd()
    base_dir = os.path.dirname(current_dir)
    print(f"Working directory: {current_dir}")
    print(f"Base directory set to: {base_dir}\n")

    # 1. Load environment variables
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY not found. Create a .env file with your API key")
    
    # 2. Initialize dependencies
    print("\nInitializing dependencies...")
    mongo_client = init_mongo()
    vncorenlp_client = init_vncorenlp(rf"{base_dir}\nlp_models\VnCoreNLP-1.2")
    phonlp_model = phonlp.load(save_dir=rf"{base_dir}\nlp_models\phonlp")
    
    # 3. Create pipeline with default settings
    print("\nCreating pipeline...")
    pipeline = create_pipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phonlp_model,
        semantic_index_dir=r"src\retrieval\semantic\search_index"
    )
    
    # 4. Run a query
    query = "Các loại đất nào được sử dụng kết hợp đa mục đích?"
    print(f"\nQuery: {query}")
    
    results = pipeline.retrieve(query, top_k=20)
    
    # 5. Display results
    pipeline.display_results(results, top_n=5)
    
    return results


# ============================================================================
# ADVANCED CONFIGURATION
# ============================================================================

def advanced_configuration():
    """
    Advanced usage with custom configuration
    """
    print("\n" + "="*80)
    print("ADVANCED CONFIGURATION EXAMPLE")
    print("="*80)

    current_dir = os.getcwd()
    base_dir = os.path.dirname(current_dir)
    print(f"Working directory: {current_dir}")
    print(f"Base directory set to: {base_dir}\n")
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize dependencies
    mongo_client = init_mongo()
    vncorenlp_client = init_vncorenlp(rf"{base_dir}\nlp_models\VnCoreNLP-1.2")
    phonlp_model = phonlp.load(save_dir=rf"{base_dir}\nlp_models\phonlp")
    
    # Create pipeline with custom settings
    pipeline = RetrievalPipeline(
        # Query preprocessing config
        openai_api_key=openai_api_key,
        openai_model="gpt-4o-mini",
        dictionary_path=rf"{base_dir}\src\retrieval\preprocess_query\dictionary.json",
        
        # Graph retrieval config
        mongo_client=mongo_client,
        db_name="KB_PROPERTY_LAW",
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phonlp_model,

        # Semantic retrieval config
        semantic_index_dir=rf"{base_dir}\src\retrieval\semantic\search_index",
        semantic_embedding_model="bkai-foundation-models/vietnamese-bi-encoder",
        
        # DPR config
        dpr_model_name="VoVanPhuc/sup-SimCSE-VietNamese-phobert-base",
        use_dpr=True,
        
        # Enable/disable components
        use_query_preprocessing=True,
        use_graph_retrieval=True,
        use_semantic_retrieval=True,
        
        # Graph traversal depth
        k_hops=2,
        
        # Custom scoring weights (will be normalized)
        graph_weight=0.3,
        semantic_weight=0.3,
        dpr_weight=0.4
    )
    
    # Run query
    query = "Phải xác nhận tài sản trên đất mới được bán đất có đúng không?"
    results = pipeline.retrieve(query, top_k=20)

    print(f"\nQuery: {query}")
    pipeline.display_results(results, top_n=20)
    
    return results


# ============================================================================
# CUSTOM WEIGHTS EXAMPLE
# ============================================================================

def custom_weights():
    """
    Example with custom scoring weights to favor different retrieval methods
    """
    print("\n" + "="*80)
    print("CUSTOM WEIGHTS EXAMPLE")
    print("="*80)
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    mongo_client = init_mongo()
    vncorenlp_client = init_vncorenlp(r"nlp_models\VnCoreNLP-1.2")
    phonlp_model = phonlp.load(save_dir=r"nlp_models\phonlp")
    
    # Favor graph retrieval over others
    pipeline = create_pipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phonlp_model,
        semantic_index_dir=r"src\retrieval\semantic\search_index",
        
        # Custom weights: prioritize graph-based results
        graph_weight=0.5,      # 50% weight to graph
        semantic_weight=0.2,   # 20% weight to semantic
        dpr_weight=0.3,        # 30% weight to DPR
        
        k_hops=3  # Deeper graph traversal
    )
    
    query = "Ai có quyền chuyển nhượng quyền sử dụng đất?"
    results = pipeline.retrieve(query, top_k=20)
    
    pipeline.display_results(results, top_n=5)
    
    return results


# ============================================================================
# SELECTIVE RETRIEVAL MODES
# ============================================================================

def graph_only():
    """Use only graph retrieval (no semantic search)"""
    print("\n" + "="*80)
    print("GRAPH-ONLY RETRIEVAL")
    print("="*80)
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    mongo_client = init_mongo()
    vncorenlp_client = init_vncorenlp(r"nlp_models\VnCoreNLP-1.2")
    phonlp_model = phonlp.load(save_dir=r"nlp_models\phonlp")
    
    pipeline = create_pipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phonlp_model,
        semantic_index_dir=r"src\retrieval\semantic\search_index",
        
        use_graph_retrieval=True,
        use_semantic_retrieval=False,  # Disable semantic
        use_dpr=False  # Disable DPR
    )
    
    query = "Quy định về chuyển mục đích sử dụng đất"
    results = pipeline.retrieve(query, top_k=20)
    
    pipeline.display_results(results, top_n=5)
    
    return results


def semantic_only():
    """Use only semantic retrieval (no graph)"""
    print("\n" + "="*80)
    print("SEMANTIC-ONLY RETRIEVAL")
    print("="*80)
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    mongo_client = init_mongo()
    vncorenlp_client = init_vncorenlp(r"nlp_models\VnCoreNLP-1.2")
    phonlp_model = phonlp.load(save_dir=r"nlp_models\phonlp")
    
    pipeline = create_pipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phonlp_model,
        semantic_index_dir=r"src\retrieval\semantic\search_index",
        
        use_graph_retrieval=False,  # Disable graph
        use_semantic_retrieval=True,
        use_dpr=True
    )
    
    query = "Thủ tục đăng ký quyền sử dụng đất"
    results = pipeline.retrieve(query, top_k=20)
    
    pipeline.display_results(results, top_n=5)
    
    return results


def fast_mode():
    """Fast mode: skip query preprocessing"""
    print("\n" + "="*80)
    print("FAST MODE (No Query Preprocessing)")
    print("="*80)
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    mongo_client = init_mongo()
    vncorenlp_client = init_vncorenlp(r"nlp_models\VnCoreNLP-1.2")
    phonlp_model = phonlp.load(save_dir=r"nlp_models\phonlp")
    
    pipeline = create_pipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phonlp_model,
        semantic_index_dir=r"src\retrieval\semantic\search_index",
        
        use_query_preprocessing=False  # Skip LLM-based preprocessing
    )
    
    query = "Quyền và nghĩa vụ của người sử dụng đất"
    
    start = time.time()
    results = pipeline.retrieve(query, top_k=20)
    elapsed = time.time() - start
    
    print(f"\n⏱️  Query completed in {elapsed:.2f} seconds")
    
    pipeline.display_results(results, top_n=5)
    
    return results


# ============================================================================
# BATCH PROCESSING
# ============================================================================

def batch_queries():
    """Process multiple queries efficiently"""
    print("\n" + "="*80)
    print("BATCH QUERY PROCESSING")
    print("="*80)
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize once
    mongo_client = init_mongo()
    vncorenlp_client = init_vncorenlp(r"nlp_models\VnCoreNLP-1.2")
    phonlp_model = phonlp.load(save_dir=r"nlp_models\phonlp")
    
    pipeline = create_pipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phonlp_model,
        semantic_index_dir=r"src\retrieval\semantic\search_index"
    )
    
    # Multiple queries
    queries = [
        "Các loại đất nông nghiệp",
        "Điều kiện chuyển nhượng quyền sử dụng đất",
        "Thời hạn sử dụng đất",
        "Quy định về bồi thường khi thu hồi đất"
    ]
    
    all_results = {}
    
    for i, query in enumerate(queries, 1):
        print(f"\n{'='*80}")
        print(f"Query {i}/{len(queries)}: {query}")
        print('='*80)
        
        start = time.time()
        results = pipeline.retrieve(query, top_k=10)
        elapsed = time.time() - start
        
        all_results[query] = results
        
        # Show top 3 results
        if results:
            print(f"\nTop 3 results (retrieved in {elapsed:.2f}s):")
            for j, result in enumerate(results[:3], 1):
                print(f"  [{j}] {result.get('section_id')} - Score: {result.get('hybrid_score', 0):.4f}")
    
    return all_results


# ============================================================================
# CUSTOM RESULT PROCESSING
# ============================================================================

def custom_result_processing():
    """
    Example showing how to process and filter results
    """
    print("\n" + "="*80)
    print("CUSTOM RESULT PROCESSING")
    print("="*80)
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    mongo_client = init_mongo()
    vncorenlp_client = init_vncorenlp(r"nlp_models\VnCoreNLP-1.2")
    phonlp_model = phonlp.load(save_dir=r"nlp_models\phonlp")
    
    pipeline = create_pipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phonlp_model,
        semantic_index_dir=r"src\retrieval\semantic\search_index"
    )
    
    query = "Điều kiện cấp giấy chứng nhận quyền sử dụng đất"
    results = pipeline.retrieve(query, top_k=20)
    
    # Custom processing: filter by score threshold
    min_score = 0.5
    filtered_results = [r for r in results if r.get('hybrid_score', 0) >= min_score]
    
    print(f"\nTotal results: {len(results)}")
    print(f"Results above {min_score} threshold: {len(filtered_results)}")
    
    # Extract specific fields
    section_ids = [r['section_id'] for r in filtered_results]
    print(f"\nFiltered section IDs: {section_ids[:5]}")
    
    # Group by document
    by_document = {}
    for result in filtered_results:
        so_hieu = result.get('so_hieu', 'Unknown')
        if so_hieu not in by_document:
            by_document[so_hieu] = []
        by_document[so_hieu].append(result)
    
    print(f"\nResults grouped by document:")
    for doc, sections in by_document.items():
        print(f"  {doc}: {len(sections)} sections")
    
    return filtered_results


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """
    Main function demonstrating all usage patterns
    """
    print("\n" + "="*100)
    print("UNIFIED RETRIEVAL PIPELINE - USAGE EXAMPLES")
    print("="*100)
    
    examples = {
        '1': ('Basic Usage', basic_usage),
        '2': ('Advanced Configuration', advanced_configuration),
        '3': ('Custom Weights', custom_weights),
        '4': ('Graph-Only Retrieval', graph_only),
        '5': ('Semantic-Only Retrieval', semantic_only),
        '6': ('Fast Mode (No Preprocessing)', fast_mode),
        '7': ('Batch Query Processing', batch_queries),
        '8': ('Custom Result Processing', custom_result_processing),
    }
    
    print("\nAvailable examples:")
    for key, (name, _) in examples.items():
        print(f"  {key}. {name}")
    print("  9. Run all examples")
    print("  0. Exit")
    
    choice = input("\nSelect an example (0-9): ").strip()
    
    if choice == '0':
        print("Exiting...")
        return
    elif choice == '9':
        print("\nRunning all examples...\n")
        for name, func in examples.values():
            try:
                print(f"\n{'='*100}")
                print(f"Running: {name}")
                print('='*100)
                func()
            except Exception as e:
                print(f"Error in {name}: {e}")
    elif choice in examples:
        name, func = examples[choice]
        print(f"\nRunning: {name}\n")
        func()
    else:
        print("Invalid choice!")


if __name__ == "__main__":
    start = time.perf_counter()
    # Run main menu
    # main()
    
    # Or run specific examples directly:
    # basic_usage()
    results = advanced_configuration()
    # custom_weights()
    # graph_only()
    # semantic_only()
    # fast_mode()
    # batch_queries()
    # custom_result_processing()

    llm_input = format_results_for_llm(results)
    # Display formatted output
    print('\n' + '=' * 80)
    print('FORMATTED OUTPUT FOR LLM')
    print('=' * 80)
    print(llm_input)

    end = time.perf_counter()
    print(f"Execution time: {end - start:.4f} seconds")
