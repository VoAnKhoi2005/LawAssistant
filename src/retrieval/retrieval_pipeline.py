"""
Unified Retrieval Pipeline
Combines: Query Preprocessing → Graph Retrieval + Semantic Retrieval → Hybrid Ranking
Returns top 20 most relevant legal sections
"""

import logging
import torch
from typing import List, Dict, Optional, Tuple

from src.retrieval.graph.bm25_ranker import hybrid_rank
from src.retrieval.graph.dpr_ranker import DPRRanker
from src.retrieval.graph.retrieval_system import extract_verbs, match_relations_graph, match_concepts_graph, \
    k_hop_traversal_mongo, score_triplets_from_traversal, collect_concept_ids_from_relations, \
    link_relations_to_nearby_concepts
from src.retrieval.preprocess_query.query_preprocessor import QueryPreprocessor
from src.retrieval.semantic.config import SearchConfig
from src.retrieval.semantic.hybrid_search import HybridSearchEngine
from src.retrieval.utils.collect_content import collect_sections_content_upward, collect_sections_content_downward
from src.utils import clean_text

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RetrievalPipeline:
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
        logger.info("INITIALIZING RETRIEVAL PIPELINE")
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
            self.triplets_col = self.db["triplets"]
            self.section_relations_col = self.db["legal_section_relations"]
            self.vncorenlp_client = vncorenlp_client
            self.phonlp_model = phonlp_model
            
            # Load embedding model for concept/relation matching
            logger.info("Loading embedding model for graph matching...")
            from transformers import AutoModel
            self.graph_embedding_model = AutoModel.from_pretrained(dpr_model_name)
            if torch.cuda.is_available():
                self.graph_embedding_model.cuda()
            self.graph_embedding_model.eval()
            
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
    
    def preprocess_query(self, query: str) -> str:
        """Step 1: Preprocess query"""
        if not self.use_query_preprocessing or self.query_preprocessor is None:
            return query
        
        logger.info("\n" + "="*80)
        logger.info("STEP 1: QUERY PREPROCESSING")
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
            max_phrase_length=1,
            similarity_threshold=0.9,
            embedding_model=self.graph_embedding_model if hasattr(self, 'graph_embedding_model') else None
        )
        logger.info(f"Matched {len(matched_relations)} relations")

        relation_concept_ids = collect_concept_ids_from_relations(
            matched_relations,
            self.triplets_col
        )
        relation_connected_concepts = list(
            self.concepts_col.find({"_id": {"$in": list(relation_concept_ids)}})
        )

        # relation_to_nearby_concepts = link_relations_to_nearby_concepts(
        #     segmented_tokens,
        #     matched_relations,
        #     relation_connected_concepts,
        #     window_size=6,
        #     max_phrase_len=4
        # )
        # seed_concept_ids = set()
        # for ids in relation_to_nearby_concepts.values():
        #     seed_concept_ids.update(ids)

        # fallback: use all relation-connected concepts
        # if not seed_concept_ids:
        #     seed_concept_ids = set(relation_concept_ids)

        seed_concept_ids = [r["_id"] for r in relation_connected_concepts]
        seed_relation_ids = [r["data"]["_id"] for r in matched_relations]

        logger.info(
            f"Seed concepts: {len(seed_concept_ids)}, "
            f"Seed relations: {len(seed_relation_ids)}"
        )
        
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
            max_concepts=1000,
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
        sections_content = collect_sections_content_upward(self.sections_col, [str(s['_id']) for s in sections])
        for section in sections:
            section['content'] = sections_content.get(str(section['_id']), section.get('content', ''))

        print(f"\nBM25+Triplet ranking for all {len(sections)} sections...")
        stage1_candidates = hybrid_rank(
            query,
            sections,
            self.vncorenlp_client,
            triplet_scores=triplet_scores,
            top_k=min(top_k, len(sections)),
            bm25_weight=0.6,
            triplet_weight=0.4
        )
        print(f"Selected top {len(stage1_candidates)} candidates for DPR")
        
        return stage1_candidates, triplet_scores
    
    def retrieve_from_semantic(self, query: str, top_k: int = 100) -> List[Dict]:
        """Step 2b: Retrieve from semantic search"""
        if not self.use_semantic_retrieval or self.semantic_engine is None:
            return []

        logger.info("\n" + "="*80)
        logger.info("STEP 2B: SEMANTIC RETRIEVAL")
        
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
        logger.info("\n" + "=" * 80)
        logger.info("STEP 3: HYBRID RANKING")

        # Merge sections (deduplicate by section_id)
        all_sections = {}

        # Add graph sections
        for section in graph_sections:
            section_id = str(section.get('section_id') or section.get('_id'))
            if section_id not in all_sections:
                all_sections[section_id] = section.copy()
                all_sections[section_id]['section_id'] = section_id
                all_sections[section_id]['graph_score'] = graph_scores.get(section_id, 0.0)
                all_sections[section_id]['semantic_score'] = 0.0
                all_sections[section_id]['dpr_score'] = 0.0

        # Add semantic sections
        for section in semantic_sections:
            section_id = str(section.get('section_id') or section.get('_id'))
            if section_id not in all_sections:
                all_sections[section_id] = section.copy()
                all_sections[section_id]['section_id'] = section_id
                all_sections[section_id]['graph_score'] = 0.0
                all_sections[section_id]['semantic_score'] = section.get('semantic_score', 0.0)
                all_sections[section_id]['dpr_score'] = 0.0
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
                
                logger.info(f"✓ DPR scoring complete for {len(sections_list)} sections")

        # # Find common ancestors and merge leaf nodes if threshold met
        # if self.use_graph_retrieval and hasattr(self, 'sections_col'):
        #     logger.info("\nFinding common ancestors for leaf nodes...")
        #
        #     MAX_DESCENDANTS_THRESHOLD = 4
        #     MAX_ANCESTOR_DEPTH = 3
        #
        #     # Define what can be merged: điều and below (điều, khoản, điểm)
        #     MERGEABLE_TYPES = {'khoản', 'điểm'}
        #     # Ancestors can be điều or khoản level to qualify for merging
        #     MERGE_TARGET_TYPES = {'điều', 'khoản'}
        #
        #     # Filter sections that can be merged
        #     mergeable_sections = [s for s in sections_list if s.get('type', '') in MERGEABLE_TYPES]
        #     non_mergeable_sections = [s for s in sections_list if s.get('type', '') not in MERGEABLE_TYPES]
        #
        #     logger.info(f"Mergeable sections (khoản/điểm): {len(mergeable_sections)}")
        #     logger.info(f"Non-mergeable sections (above điều): {len(non_mergeable_sections)}")
        #
        #     if not mergeable_sections:
        #         logger.info("No mergeable sections to analyze")
        #     else:
        #         print("Tracing ancestors for mergeable sections...")

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

        # Fetch related sections (amendments) and add to results
        if self.use_graph_retrieval and hasattr(self, 'section_relations_col'):
            logger.info("\nFetching related sections (amendments)...")
            top_sections = self._add_related_sections(top_sections)

        return top_sections
    
    def _add_related_sections(self, top_sections: List[Dict]) -> List[Dict]:
        """
        Fetch related sections (amendments) for top sections and add them to results
        
        Args:
            top_sections: List of top ranked sections
            
        Returns:
            Extended list with related sections added
        """
        # Extract section identifiers from top sections
        top_section_ids = set()
        for section in top_sections:
            section_id = section.get('section_id')
            full_path = section.get('full_path', '')
            
            if section_id:
                top_section_ids.add(str(section_id))
            if full_path:
                top_section_ids.add(full_path)
        
        if not top_section_ids:
            return top_sections
        
        # Query section_relations collection
        # Find relations where source or target matches any top section
        relations = list(self.section_relations_col.find({
            '$or': [
                {'source': {'$in': list(top_section_ids)}},
                {'target': {'$in': list(top_section_ids)}}
            ]
        }))
        
        if not relations:
            logger.info("No related sections found")
            return top_sections
        
        logger.info(f"Found {len(relations)} section relations")
        
        # Collect all related section identifiers
        related_section_paths = set()
        for rel in relations:
            source = rel.get('source')
            target = rel.get('target')
            
            # If source is in top sections, add target
            if source in top_section_ids:
                related_section_paths.add(target)
            # If target is in top sections, add source
            if target in top_section_ids:
                related_section_paths.add(source)
        
        # Remove sections already in top results
        related_section_paths = related_section_paths - top_section_ids
        
        if not related_section_paths:
            logger.info("No new related sections to add")
            return top_sections
        
        logger.info(f"Fetching {len(related_section_paths)} related sections")
        
        # Fetch related sections from database
        # Try matching by full_path first, then by section_id
        related_sections = list(self.sections_col.find({
            '$or': [
                {'full_path': {'$in': list(related_section_paths)}},
                {'section_id': {'$in': list(related_section_paths)}}
            ]
        }))
        
        if not related_sections:
            logger.info("Related sections not found in database")
            return top_sections
        
        # Collect content for related sections (upward traversal)
        sections_content = self.collect_related_content(related_sections)

        # Add content and prepare related sections for inclusion
        related_results = []
        for section in related_sections:
            section_id = str(section.get('_id'))
            
            # Find the relation details
            relation_info = []
            full_path = section.get('full_path', '')
            for rel in relations:
                if rel.get('source') == full_path or rel.get('target') == full_path or \
                   rel.get('source') == section_id or rel.get('target') == section_id:
                    relation_info.append({
                        'type': rel.get('type'),
                        'source': rel.get('source'),
                        'target': rel.get('target'),
                        'amendment_types': rel.get('amendment_types', [])
                    })
            
            related_result = {
                'section_id': section_id,
                '_id': section['_id'],
                'content': sections_content.get(section_id, section.get('content', '')),
                'type': section.get('type', ''),
                'parent_id': section.get('parent_id'),
                'full_path': full_path,
                'so_hieu': section.get('so_hieu', ''),
                'is_related_section': True,
                'relation_info': relation_info,
                'hybrid_score': 0.0,
                'graph_score': 0.0,
                'semantic_score': 0.0,
                'dpr_score': 0.0
            }
            
            related_results.append(related_result)
        
        logger.info(f"Adding {len(related_results)} related sections to results")
        
        # Append related sections to the end of top sections
        # Don't re-rank, just append
        combined_results = top_sections + related_results
        
        return combined_results

    def collect_related_content(self, sections):
        upward_ids = []
        downward_ids = []

        for s in sections:
            if s.get("type") == "điều":
                downward_ids.append(str(s["_id"]))
            else:
                upward_ids.append(str(s["_id"]))

        result = {}  # { section_id: merged_content }

        if upward_ids:
            upward_map = collect_sections_content_upward(
                self.sections_col, upward_ids
            )
            # upward_map: Dict[str, str]
            result.update(upward_map)

        if downward_ids:
            downward_map = collect_sections_content_downward(
                self.sections_col, downward_ids
            )
            # downward_map: Dict[str, str]
            result.update(downward_map)

        return result

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
        
        # Step 1: Preprocess query
        processed_query = self.preprocess_query(query)
        
        # Step 2a: Graph retrieval
        graph_sections, graph_scores = self.retrieve_from_graph(processed_query, top_k=100)
        logger.info(f"Graph retrieval: {len(graph_sections)} sections with scores")
        
        # Step 2b: Semantic retrieval
        semantic_sections = self.retrieve_from_semantic(processed_query, top_k=100)
        logger.info(f"Semantic retrieval: {len(semantic_sections)} sections")

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

        # Separate main results and related sections
        main_results = [r for r in results if not r.get('is_related_section', False)]
        related_results = [r for r in results if r.get('is_related_section', False)]

        # Display main results
        for result in main_results[:top_n]:
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

            # Check if this is a parent aggregation
            is_parent = result.get('is_parent_aggregation', False)
            num_children = result.get('num_children_aggregated', 0)

            print(f"\n[{rank}] {section_id}")
            if is_parent:
                print(f"    [PARENT AGGREGATION - {num_children} children]")
            print(f"    So Hieu: {so_hieu}")
            print(f"    Path: {full_path}")
            print(f"    Hybrid Score: {hybrid_score:.4f}")
            print(f"      - Graph: {graph_score:.2f} (norm: {result.get('normalized_graph', 0):.3f})")
            print(f"      - Semantic: {semantic_score:.2f} (norm: {result.get('normalized_semantic', 0):.3f})")
            print(f"      - DPR: {dpr_score:.2f} (norm: {result.get('normalized_dpr', 0):.3f})")
            print(f"    Content: {content_preview}")

        # Display related sections
        if related_results:
            logger.info("\n" + "="*100)
            logger.info(f"RELATED SECTIONS - {len(related_results)} sections")
            logger.info("="*100)

            for idx, result in enumerate(related_results, 1):
                section_id = result.get('section_id', 'N/A')
                full_path = result.get('full_path', 'N/A')
                so_hieu = result.get('so_hieu', 'N/A')
                content = result.get('content', 'N/A')
                content_preview = content[:200] + "..." if len(content) > 200 else content

                relation_info = result.get('relation_info', [])

                print(f"\n[R{idx}] {section_id}")
                print(f"    So Hieu: {so_hieu}")
                print(f"    Path: {full_path}")

                # Display relation information
                if relation_info:
                    print(f"    Relations:")
                    for rel in relation_info:
                        rel_type = rel.get('type', 'N/A')
                        amendment_types = ', '.join(rel.get('amendment_types', []))
                        print(f"      - Type: {rel_type}")
                        if amendment_types:
                            print(f"        Amendment Types: {amendment_types}")
                        print(f"        Source: {rel.get('source', 'N/A')}")
                        print(f"        Target: {rel.get('target', 'N/A')}")

                print(f"    Content: {content_preview}")

        logger.info("\n" + "="*100)


def create_pipeline(
    openai_api_key: str,
    mongo_client,
    vncorenlp_client,
    phonlp_model,
    **kwargs
) -> RetrievalPipeline:
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
    return RetrievalPipeline(
        openai_api_key=openai_api_key,
        mongo_client=mongo_client,
        vncorenlp_client=vncorenlp_client,
        phonlp_model=phonlp_model,
        **kwargs
    )
