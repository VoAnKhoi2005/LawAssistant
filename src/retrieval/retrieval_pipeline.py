"""
Unified Retrieval Pipeline
Combines: Query Preprocessing → Graph Retrieval + Semantic Retrieval → Hybrid Ranking
Returns top 20 most relevant legal sections
"""

import logging
from typing import List, Dict, Optional, Tuple

# Query Preprocessing
from src.retrieval.preprocess_query.src import QueryPreprocessor

# Graph Retrieval
from src.retrieval.graph.src import (
    k_hop_traversal_mongo,
    score_triplets_from_traversal,
    match_concepts_graph,
    match_relations_graph,
    extract_verbs,
    collect_sections_content
)
from src.retrieval.graph.dpr_ranker import DPRRanker

# Semantic Retrieval
from src.retrieval.semantic.src import HybridSearchEngine
from src.retrieval.semantic.src import SearchConfig

# NLP utilities
from src.triplet_extraction.src import clean_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UnifiedRetrievalPipeline:
    """
    Unified pipeline combining:
    1. Query Preprocessing (normalize + LLM refine)
    2. Graph Retrieval (knowledge graph + triplets)
    3. Semantic Retrieval (FAISS + BM25)
    4. Hybrid scoring to get top 20 sections
    """
    
    def __init__(
        self,
        # Query preprocessing
        openai_api_key: str,
        openai_model: str = "gpt-4o-mini",
        dictionary_path: Optional[str] = None,
        
        # Graph retrieval dependencies
        mongo_client = None,
        db_name: str = "KB_PROPERTY_LAW",
        vncorenlp_client = None,
        phonlp_model = None,
        
        # Semantic retrieval config
        semantic_index_dir: str = "./search_index",
        semantic_embedding_model: str = "bkai-foundation-models/vietnamese-bi-encoder",
        
        # DPR config
        dpr_model_name: str = "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base",
        use_dpr: bool = True,
        
        # Retrieval options
        use_query_preprocessing: bool = True,
        use_graph_retrieval: bool = True,
        use_semantic_retrieval: bool = True,
        k_hops: int = 2,
        
        # Scoring weights
        graph_weight: float = 0.3,
        semantic_weight: float = 0.3,
        dpr_weight: float = 0.4
    ):
        """
        Initialize unified retrieval pipeline
        
        Args:
            openai_api_key: OpenAI API key for query preprocessing
            openai_model: OpenAI model name
            dictionary_path: Path to abbreviations dictionary JSON
            mongo_client: MongoDB client for graph retrieval
            db_name: Database name
            vncorenlp_client: VnCoreNLP client
            phonlp_model: PhoNLP model
            semantic_index_dir: Directory for semantic search indexes
            semantic_embedding_model: Model for semantic embeddings
            dpr_model_name: Model for dense passage retrieval
            use_dpr: Whether to use DPR in ranking
            use_query_preprocessing: Enable/disable query preprocessing
            use_graph_retrieval: Enable/disable graph retrieval
            use_semantic_retrieval: Enable/disable semantic retrieval
            k_hops: Number of hops for graph traversal
            graph_weight: Weight for graph scores (0-1)
            semantic_weight: Weight for semantic scores (0-1)
            dpr_weight: Weight for DPR scores (0-1)
        """
        self.use_query_preprocessing = use_query_preprocessing
        self.use_graph_retrieval = use_graph_retrieval
        self.use_semantic_retrieval = use_semantic_retrieval
        self.use_dpr = use_dpr
        self.k_hops = k_hops
        
        # Normalize weights
        total_weight = graph_weight + semantic_weight + dpr_weight
        self.graph_weight = graph_weight / total_weight
        self.semantic_weight = semantic_weight / total_weight
        self.dpr_weight = dpr_weight / total_weight
        
        logger.info("="*80)
        logger.info("INITIALIZING UNIFIED RETRIEVAL PIPELINE")
        logger.info("="*80)
        
        # 1. Query Preprocessor
        if self.use_query_preprocessing:
            logger.info("\n[1/4] Initializing Query Preprocessor...")
            self.query_preprocessor = QueryPreprocessor(
                openai_api_key=openai_api_key,
                openai_model=openai_model,
                json_path=dictionary_path
            )
            logger.info("✓ Query preprocessor ready")
        else:
            self.query_preprocessor = None
            logger.info("[1/4] Query preprocessing disabled")
        
        # 2. Graph Retrieval Components
        if self.use_graph_retrieval:
            logger.info("\n[2/4] Initializing Graph Retrieval...")
            if mongo_client is None:
                raise ValueError("mongo_client required for graph retrieval")
            if vncorenlp_client is None:
                raise ValueError("vncorenlp_client required for graph retrieval")
            if phonlp_model is None:
                raise ValueError("phonlp_model required for graph retrieval")
            
            self.db = mongo_client[db_name]
            self.sections_col = self.db["legal_sections"]
            self.concepts_col = self.db["concepts"]
            self.relations_col = self.db["relations"]
            self.triplets_col = self.db["triplets_new"]
            self.vncorenlp_client = vncorenlp_client
            self.phonlp_model = phonlp_model
            
            logger.info(f"✓ Graph retrieval ready (k_hops={k_hops})")
        else:
            logger.info("[2/4] Graph retrieval disabled")
        
        # 3. Semantic Retrieval Engine
        if self.use_semantic_retrieval:
            logger.info("\n[3/4] Initializing Semantic Retrieval...")
            config = SearchConfig(
                index_dir=semantic_index_dir,
                embedding_model=semantic_embedding_model
            )
            self.semantic_engine = HybridSearchEngine(config)
            
            # Load index if exists
            if self.semantic_engine.index_exists():
                self.semantic_engine.load_index()
                logger.info(f"✓ Semantic search ready ({self.semantic_engine.faiss_index.size} docs indexed)")
            else:
                logger.warning("! Semantic index not found - will need to build index first")
        else:
            self.semantic_engine = None
            logger.info("[3/4] Semantic retrieval disabled")
        
        # 4. DPR Ranker
        if self.use_dpr:
            logger.info("\n[4/4] Initializing DPR Ranker...")
            self.dpr_ranker = DPRRanker(model_name=dpr_model_name)
            logger.info(f"✓ DPR ready on {self.dpr_ranker.device}")
        else:
            self.dpr_ranker = None
            logger.info("[4/4] DPR disabled")
        
        logger.info("\n" + "="*80)
        logger.info("PIPELINE INITIALIZATION COMPLETE")
        logger.info(f"Weights: Graph={self.graph_weight:.2f}, Semantic={self.semantic_weight:.2f}, DPR={self.dpr_weight:.2f}")
        logger.info("="*80 + "\n")
    
    def preprocess_query(self, query: str) -> str:
        """Step 1: Preprocess query"""
        if not self.use_query_preprocessing or self.query_preprocessor is None:
            return query
        
        logger.info("\n" + "="*80)
        logger.info("STEP 1: QUERY PREPROCESSING")
        logger.info("="*80)
        logger.info(f"Original query: {query}")
        
        processed_query = self.query_preprocessor.process(query)
        logger.info(f"Processed query: {processed_query}")
        
        return processed_query
    
    def retrieve_from_graph(self, query: str, top_k: int = 100) -> Tuple[List[Dict], Dict[str, float]]:
        """Step 2a: Retrieve from knowledge graph"""
        if not self.use_graph_retrieval:
            return [], {}
        
        logger.info("\n" + "="*80)
        logger.info("STEP 2A: GRAPH RETRIEVAL")
        logger.info("="*80)
        
        # Clean and segment text
        cleaned_query = clean_text(query)
        segmented_text = self.vncorenlp_client.word_segment(cleaned_query)[0]
        segmented_tokens = segmented_text.split(" ")
        logger.info(f"Segmented: {segmented_text}")
        
        # Extract verbs
        verbs = extract_verbs(segmented_text, self.phonlp_model)
        logger.info(f"Verbs: {verbs}")
        
        # Match relations from verbs
        matched_relations = match_relations_graph(
            verbs,
            self.relations_col,
            max_phrase_length=1
        )
        logger.info(f"Matched {len(matched_relations)} relations")
        
        # Match concepts
        matched_concepts = match_concepts_graph(
            segmented_tokens,
            self.concepts_col,
            max_phrase_length=3
        )
        logger.info(f"Matched {len(matched_concepts)} concepts")
        
        # Extract IDs
        seed_concept_ids = [match['data']['_id'] for match in matched_concepts]
        seed_relation_ids = [match['data']['_id'] for match in matched_relations]
        
        if not seed_concept_ids and not seed_relation_ids:
            logger.warning("No concepts or relations matched - graph retrieval skipped")
            return [], {}
        
        # K-hop traversal
        logger.info(f"\nPerforming {self.k_hops}-hop graph traversal...")
        traversal_result = k_hop_traversal_mongo(
            seed_concept_ids=seed_concept_ids,
            seed_relation_ids=seed_relation_ids,
            triplets_col=self.triplets_col,
            concepts_col=self.concepts_col,
            k_hops=self.k_hops,
            max_concepts=500
        )
        
        # Score sections from triplets
        triplet_section_ids, triplet_scores = score_triplets_from_traversal(
            traversal_result,
            seed_concept_ids,
            seed_relation_ids
        )
        
        if not triplet_section_ids:
            logger.warning("No sections found from graph traversal")
            return [], {}
        
        # Fetch sections
        sections = list(self.sections_col.find({'section_id': {'$in': triplet_section_ids}}))
        if not sections:
            sections = list(self.sections_col.find({'_id': {'$in': triplet_section_ids}}))
        
        # Collect full content (traverse to parent 'điều')
        sections_content = collect_sections_content(
            self.sections_col, 
            [str(s['_id']) for s in sections]
        )
        for section in sections:
            section['content'] = sections_content.get(str(section['_id']), section.get('content', ''))
        
        logger.info(f"✓ Graph retrieval: {len(sections)} sections with scores")
        
        return sections, triplet_scores
    
    def retrieve_from_semantic(self, query: str, top_k: int = 100) -> List[Dict]:
        """Step 2b: Retrieve from semantic search"""
        if not self.use_semantic_retrieval or self.semantic_engine is None:
            return []
        
        logger.info("\n" + "="*80)
        logger.info("STEP 2B: SEMANTIC RETRIEVAL")
        logger.info("="*80)
        
        if not self.semantic_engine.is_ready:
            logger.error("Semantic index not loaded!")
            return []
        
        # Perform hybrid search (FAISS + BM25)
        search_results = self.semantic_engine.search(
            query=query,
            top_k=top_k,
            semantic_weight=0.6,
            bm25_weight=0.4
        )
        
        # Convert to section dictionaries
        sections = []
        for result in search_results:
            section = {
                'section_id': result.doc_id,
                'content': result.content,
                'semantic_score': result.score_combined,
                'semantic_score_faiss': result.score_semantic,
                'semantic_score_bm25': result.score_bm25,
                **result.metadata
            }
            sections.append(section)
        
        logger.info(f"✓ Semantic retrieval: {len(sections)} sections")
        
        return sections
    
    def merge_and_rank(
        self, 
        graph_sections: List[Dict],
        semantic_sections: List[Dict],
        graph_scores: Dict[str, float],
        query: str,
        top_k: int = 20
    ) -> List[Dict]:
        """Step 3: Merge results and apply hybrid ranking"""
        logger.info("\n" + "="*80)
        logger.info("STEP 3: HYBRID RANKING")
        logger.info("="*80)
        
        # Merge sections (deduplicate by section_id)
        all_sections = {}
        
        # Add graph sections
        for section in graph_sections:
            section_id = str(section.get('section_id') or section.get('_id'))
            if section_id not in all_sections:
                all_sections[section_id] = section.copy()
                all_sections[section_id]['section_id'] = section_id
                all_sections[section_id]['graph_score'] = graph_scores.get(section_id, 0.0)
        
        # Add semantic sections
        for section in semantic_sections:
            section_id = str(section.get('section_id') or section.get('_id'))
            if section_id not in all_sections:
                all_sections[section_id] = section.copy()
                all_sections[section_id]['section_id'] = section_id
                all_sections[section_id]['graph_score'] = 0.0
            else:
                # Merge semantic scores if section exists
                all_sections[section_id].update({
                    'semantic_score': section.get('semantic_score', 0.0),
                    'semantic_score_faiss': section.get('semantic_score_faiss', 0.0),
                    'semantic_score_bm25': section.get('semantic_score_bm25', 0.0)
                })
        
        sections_list = list(all_sections.values())
        logger.info(f"Total unique sections: {len(sections_list)}")
        
        if not sections_list:
            logger.warning("No sections to rank!")
            return []
        
        # Apply DPR if enabled
        if self.use_dpr and self.dpr_ranker is not None:
            logger.info("\nApplying DPR scoring...")
            from src.retrieval.graph.dpr_ranker import prepare_section_corpus_dpr
            
            passages, section_ids = prepare_section_corpus_dpr(sections_list)
            if passages:
                self.dpr_ranker.fit(passages, section_ids, batch_size=64)
                dpr_results = self.dpr_ranker.search(query, top_k=len(passages))
                
                dpr_scores = {section_ids[idx]: score for idx, score in dpr_results}
                for section in sections_list:
                    section_id = section['section_id']
                    section['dpr_score'] = dpr_scores.get(section_id, 0.0)
        
        # Normalize scores
        graph_scores_list = [s.get('graph_score', 0.0) for s in sections_list]
        semantic_scores_list = [s.get('semantic_score', 0.0) for s in sections_list]
        dpr_scores_list = [s.get('dpr_score', 0.0) for s in sections_list]
        
        max_graph = max(graph_scores_list) if max(graph_scores_list) > 0 else 1.0
        max_semantic = max(semantic_scores_list) if max(semantic_scores_list) > 0 else 1.0
        max_dpr = max(dpr_scores_list) if max(dpr_scores_list) > 0 else 1.0
        
        # Calculate hybrid scores
        logger.info(f"\nCalculating hybrid scores:")
        logger.info(f"  Graph weight: {self.graph_weight:.2f}")
        logger.info(f"  Semantic weight: {self.semantic_weight:.2f}")
        logger.info(f"  DPR weight: {self.dpr_weight:.2f}")
        
        for section in sections_list:
            norm_graph = section.get('graph_score', 0.0) / max_graph
            norm_semantic = section.get('semantic_score', 0.0) / max_semantic
            norm_dpr = section.get('dpr_score', 0.0) / max_dpr
            
            hybrid_score = (
                self.graph_weight * norm_graph +
                self.semantic_weight * norm_semantic +
                self.dpr_weight * norm_dpr
            )
            
            section['normalized_graph'] = norm_graph
            section['normalized_semantic'] = norm_semantic
            section['normalized_dpr'] = norm_dpr
            section['hybrid_score'] = hybrid_score
        
        # Sort by hybrid score
        sections_list.sort(key=lambda x: x['hybrid_score'], reverse=True)
        
        # Get top K
        top_sections = sections_list[:top_k]
        
        # Add ranks
        for rank, section in enumerate(top_sections, 1):
            section['rank'] = rank
        
        logger.info(f"\n✓ Ranking complete: Top {len(top_sections)} sections selected")
        
        return top_sections
    
    def retrieve(self, query: str, top_k: int = 20) -> List[Dict]:
        """
        Main retrieval pipeline
        
        Args:
            query: User query (raw)
            top_k: Number of top sections to return
            
        Returns:
            List of top K ranked sections with scores
        """
        logger.info("\n" + "="*100)
        logger.info(f"QUERY: {query}")
        logger.info("="*100)
        
        # Step 1: Preprocess query
        processed_query = self.preprocess_query(query)
        
        # Step 2a: Graph retrieval
        graph_sections, graph_scores = self.retrieve_from_graph(processed_query, top_k=100)
        
        # Step 2b: Semantic retrieval
        semantic_sections = self.retrieve_from_semantic(processed_query, top_k=100)
        
        # Step 3: Merge and rank
        final_results = self.merge_and_rank(
            graph_sections=graph_sections,
            semantic_sections=semantic_sections,
            graph_scores=graph_scores,
            query=processed_query,
            top_k=top_k
        )
        
        return final_results
    
    def display_results(self, results: List[Dict], top_n: int = 20):
        """Display retrieval results in a formatted way"""
        logger.info("\n" + "="*100)
        logger.info(f"TOP {min(top_n, len(results))} RESULTS")
        logger.info("="*100)
        
        for result in results[:top_n]:
            rank = result.get('rank', 0)
            section_id = result.get('section_id', 'N/A')
            hybrid_score = result.get('hybrid_score', 0.0)
            
            graph_score = result.get('graph_score', 0.0)
            semantic_score = result.get('semantic_score', 0.0)
            dpr_score = result.get('dpr_score', 0.0)
            
            full_path = result.get('full_path', 'N/A')
            so_hieu = result.get('so_hieu', 'N/A')
            content = result.get('content', 'N/A')
            content_preview = content[:200] + "..." if len(content) > 200 else content
            
            print(f"\n[{rank}] {section_id}")
            print(f"    So Hieu: {so_hieu}")
            print(f"    Path: {full_path}")
            print(f"    Hybrid Score: {hybrid_score:.4f}")
            print(f"      - Graph: {graph_score:.2f} (norm: {result.get('normalized_graph', 0):.3f})")
            print(f"      - Semantic: {semantic_score:.2f} (norm: {result.get('normalized_semantic', 0):.3f})")
            print(f"      - DPR: {dpr_score:.2f} (norm: {result.get('normalized_dpr', 0):.3f})")
            print(f"    Content: {content_preview}")
        
        logger.info("\n" + "="*100)


def create_pipeline(
    openai_api_key: str,
    mongo_client,
    vncorenlp_client,
    phonlp_model,
    **kwargs
) -> UnifiedRetrievalPipeline:
    """
    Convenience function to create pipeline with default settings
    
    Args:
        openai_api_key: OpenAI API key
        mongo_client: MongoDB client
        vncorenlp_client: VnCoreNLP client  
        phonlp_model: PhoNLP model
        **kwargs: Additional arguments to override defaults
        
    Returns:
        Configured UnifiedRetrievalPipeline instance
    """
    return UnifiedRetrievalPipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phonlp_model,
        **kwargs
    )
