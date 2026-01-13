"""
Example usage of the Unified Retrieval Pipeline
Demonstrates how to use the pipeline to retrieve top 20 relevant sections
"""

import os
import time
from dotenv import load_dotenv

# Import dependencies
import phonlp
from src.db import init_mongo
from src.retrieval.retrieval_pipeline import create_pipeline
from src.triplet_extraction.pos_taging import init_vncorenlp


def main():
    """Main example demonstrating the unified retrieval pipeline"""
    
    print("="*100)
    print("UNIFIED RETRIEVAL PIPELINE - EXAMPLE")
    print("="*100)
    
    # Load environment variables
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    if not openai_api_key:
        print("ERROR: OPENAI_API_KEY not found in environment variables")
        print("Please create a .env file with your OpenAI API key")
        return
    
    # === 1. Initialize MongoDB ===
    print("\n[1/4] Initializing MongoDB...")
    mongo_client = init_mongo()
    print("✓ MongoDB connected")
    
    # === 2. Initialize NLP models ===
    print("\n[2/4] Initializing NLP models...")
    vncorenlp_path = r"../nlp_models/VnCoreNLP-1.2"
    phonlp_path = r"../nlp_models/phonlp"
    
    vncorenlp_client = init_vncorenlp(vncorenlp_path)
    phoNLP_model = phonlp.load(save_dir=phonlp_path)
    print("✓ NLP models loaded")
    
    # === 3. Initialize Unified Retrieval Pipeline ===
    print("\n[3/4] Creating unified retrieval pipeline...")
    
    pipeline = create_pipeline(
        openai_api_key=openai_api_key,
        openai_model="gpt-4o-mini",
        dictionary_path=r"../src/retrieval/preprocess_query/dictionary.json",
        
        # MongoDB
        mongo_client=mongo_client,
        db_name="KB_PROPERTY_LAW",
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phoNLP_model,
        
        # Semantic search
        semantic_index_dir=r"src/retrieval/semantic\search_index",
        semantic_embedding_model="bkai-foundation-models/vietnamese-bi-encoder",
        
        # DPR
        dpr_model_name="VoVanPhuc/sup-SimCSE-VietNamese-phobert-base",
        use_dpr=True,
        
        # Options
        use_query_preprocessing=True,
        use_graph_retrieval=True,
        use_semantic_retrieval=True,
        k_hops=2,
        
        # Weights (will be normalized automatically)
        graph_weight=0.3,
        semantic_weight=0.3,
        dpr_weight=0.4
    )
    
    print("✓ Pipeline ready")
    
    # === 4. Test queries ===
    print("\n[4/4] Running test queries...")
    
    test_queries = [
        "Các loại đất nào được sử dụng kết hợp đa mục đích?",
        "Điều kiện để được cấp giấy chứng nhận quyền sử dụng đất là gì?",
        "Ai có quyền chuyển nhượng quyền sử dụng đất?",
    ]
    
    for i, query in enumerate(test_queries, 1):
        print("\n" + "="*100)
        print(f"QUERY {i}/{len(test_queries)}: {query}")
        print("="*100)
        
        start_time = time.time()
        
        # Retrieve top 20 sections
        results = pipeline.retrieve(query=query, top_k=20)
        
        elapsed_time = time.time() - start_time
        
        # Display results
        pipeline.display_results(results, top_n=20)
        
        print(f"\n⏱️  Query processed in {elapsed_time:.2f} seconds")
    
    print("\n" + "="*100)
    print("ALL QUERIES COMPLETED")
    print("="*100)


def simple_example():
    """Simplified example for quick testing"""
    
    # Load API key
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    # Initialize dependencies
    mongo_client = init_mongo()
    vncorenlp_client = init_vncorenlp(r"/nlp_models\VnCoreNLP-1.2")
    phoNLP_model = phonlp.load(save_dir=r"../nlp_models/phonlp")
    
    # Create pipeline
    pipeline = create_pipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phoNLP_model,
        semantic_index_dir=r"src/retrieval/semantic\search_index"
    )
    
    # Single query
    query = "Các loại đất nào được sử dụng kết hợp đa mục đích?"
    results = pipeline.retrieve(query, top_k=20)
    
    # Show results
    pipeline.display_results(results)
    
    return results


def custom_weights_example():
    """Example with custom scoring weights"""
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    mongo_client = init_mongo()
    vncorenlp_client = init_vncorenlp(r"/nlp_models\VnCoreNLP-1.2")
    phoNLP_model = phonlp.load(save_dir=r"../nlp_models/phonlp")
    
    # Custom weights: favor graph retrieval
    pipeline = create_pipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phoNLP_model,
        semantic_index_dir=r"src/retrieval/semantic\search_index",
        
        # Custom weights
        graph_weight=0.5,      # Higher weight for graph
        semantic_weight=0.2,   # Lower weight for semantic
        dpr_weight=0.3,        # Medium weight for DPR
        
        k_hops=3  # More hops for deeper graph traversal
    )
    
    query = "Điều kiện chuyển nhượng quyền sử dụng đất"
    results = pipeline.retrieve(query, top_k=20)
    
    pipeline.display_results(results)
    
    return results


def without_preprocessing_example():
    """Example without query preprocessing (faster but less accurate)"""
    
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    
    mongo_client = init_mongo()
    vncorenlp_client = init_vncorenlp(r"/nlp_models\VnCoreNLP-1.2")
    phoNLP_model = phonlp.load(save_dir=r"../nlp_models/phonlp")
    
    # Disable query preprocessing
    pipeline = create_pipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phoNLP_model,
        semantic_index_dir=r"src/retrieval/semantic\search_index",
        
        use_query_preprocessing=False  # Skip LLM preprocessing
    )
    
    query = "đkkd & bhxh"  # Abbreviations won't be expanded
    results = pipeline.retrieve(query, top_k=20)
    
    pipeline.display_results(results)
    
    return results


if __name__ == "__main__":
    # Run main example
    main()
    
    # Uncomment to run other examples:
    # simple_example()
    # custom_weights_example()
    # without_preprocessing_example()
