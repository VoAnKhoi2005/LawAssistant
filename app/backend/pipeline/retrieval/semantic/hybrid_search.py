"""Main Hybrid Search Engine - Optimized for large datasets"""

import os
import logging
from typing import List, Dict, Any, Optional, Tuple, Iterator

import numpy as np

# Import từ cùng folder (dùng relative import)
from .config import SearchConfig
from .models import Document, SearchResult, IndexStats
from .text_processor import TextProcessor
from .embedding_service import EmbeddingService
from .faiss_index import FAISSIndex
from .bm25_index import BM25Index

logger = logging.getLogger(__name__)


class HybridSearchEngine:
    """
    Hybrid Search Engine - Optimized for 20K+ documents
    """

    def __init__(self, config: Optional[SearchConfig] = None):
        self.config = config or SearchConfig()

        self.text_processor = TextProcessor()
        self.embedding_service = EmbeddingService(self.config.embedding_model)
        self.faiss_index = FAISSIndex(
            embedding_dim=0,
            index_path=self.config.index_dir
        )
        self.bm25_index = BM25Index(index_path=self.config.index_dir)

        self._initialized = False

    @property
    def is_ready(self) -> bool:
        return self.faiss_index.is_loaded and self.bm25_index.is_loaded

    # ========================================================================
    #                    BUILD INDEX - OPTIMIZED
    # ========================================================================

    def build_index(self, documents: List[Dict[str, Any]]):
        """
        Build index với batch processing

        Args:
            documents: List of document dicts
        """
        if not documents:
            logger.warning("No documents to index")
            return

        total_docs = len(documents)
        logger.info(f"Building index for {total_docs:,} documents...")

        # Load embedding model
        self.embedding_service.load()
        self.faiss_index.embedding_dim = self.embedding_service.embedding_dim

        # Process và collect data
        all_doc_ids: List[str] = []
        all_contents: List[str] = []
        all_cached_docs: List[Dict] = []
        all_tokenized: List[List[str]] = []

        batch_size = self.config.processing_batch_size

        # Step 1: Process documents theo batch
        logger.info("Step 1/3: Processing documents...")

        for i in range(0, total_docs, batch_size):
            batch = documents[i:i + batch_size]
            batch_end = min(i + batch_size, total_docs)

            logger.info(f"  Processing {i+1:,} - {batch_end:,} / {total_docs:,}")

            for doc in batch:
                doc_id = str(doc.get(self.config.id_field, ""))
                content = doc.get(self.config.content_field, "")

                all_doc_ids.append(doc_id)
                all_contents.append(content)
                all_cached_docs.append(self._extract_cached_fields(doc))

        # Step 2: Tokenize cho BM25
        logger.info("Step 2/3: Tokenizing for BM25...")

        for i in range(0, total_docs, batch_size):
            batch_contents = all_contents[i:i + batch_size]
            batch_end = min(i + batch_size, total_docs)

            logger.info(f"  Tokenizing {i+1:,} - {batch_end:,} / {total_docs:,}")

            batch_tokenized = self.text_processor.tokenize_batch(batch_contents)
            all_tokenized.extend(batch_tokenized)

        # Build BM25 index
        self.bm25_index.build(all_tokenized, all_doc_ids)

        # Step 3: Create embeddings theo batch
        logger.info("Step 3/3: Creating embeddings...")

        all_embeddings = self._encode_in_batches(all_contents)

        # Build FAISS index
        self.faiss_index.build(all_embeddings, all_doc_ids, all_cached_docs)

        # Save indexes
        self.save_index()

        self._initialized = True
        logger.info(f"✅ Index built successfully! Total: {total_docs:,} documents")

    def _encode_in_batches(self, texts: List[str]) -> np.ndarray:
        """Encode texts theo batches để tránh OOM"""

        total = len(texts)
        batch_size = self.config.embedding_batch_size
        all_embeddings = []

        for i in range(0, total, batch_size):
            batch_texts = texts[i:i + batch_size]
            batch_end = min(i + batch_size, total)

            logger.info(f"  Encoding {i+1:,} - {batch_end:,} / {total:,}")

            batch_embeddings = self.embedding_service.encode(
                batch_texts,
                batch_size=batch_size,
                show_progress=False  # Tắt progress bar của từng batch
            )
            all_embeddings.append(batch_embeddings)

        return np.vstack(all_embeddings)

    def build_index_from_iterator(self, doc_iterator: Iterator[Dict[str, Any]], total_docs: Optional[int] = None):
        """
        Build index từ iterator (memory efficient cho rất nhiều documents)

        Args:
            doc_iterator: Iterator yield từng document
            total_docs: Tổng số documents (optional, để hiển thị progress)
        """
        logger.info("Building index from iterator...")

        # Load embedding model
        self.embedding_service.load()
        self.faiss_index.embedding_dim = self.embedding_service.embedding_dim

        all_doc_ids: List[str] = []
        all_cached_docs: List[Dict] = []
        all_tokenized: List[List[str]] = []
        all_embeddings_list: List[np.ndarray] = []

        batch_contents: List[str] = []
        batch_size = self.config.processing_batch_size
        processed = 0

        for doc in doc_iterator:
            doc_id = str(doc.get(self.config.id_field, ""))
            content = doc.get(self.config.content_field, "")

            all_doc_ids.append(doc_id)
            all_cached_docs.append(self._extract_cached_fields(doc))
            all_tokenized.append(self.text_processor.tokenize(content))
            batch_contents.append(content)

            processed += 1

            # Encode khi đủ batch
            if len(batch_contents) >= batch_size:
                progress = f"{processed:,}" if not total_docs else f"{processed:,}/{total_docs:,}"
                logger.info(f"  Processing batch... ({progress})")

                batch_embeddings = self.embedding_service.encode(
                    batch_contents,
                    show_progress=False
                )
                all_embeddings_list.append(batch_embeddings)
                batch_contents = []

        # Process remaining
        if batch_contents:
            logger.info(f"  Processing final batch... ({processed:,} total)")
            batch_embeddings = self.embedding_service.encode(batch_contents, show_progress=False)
            all_embeddings_list.append(batch_embeddings)

        # Combine all embeddings
        all_embeddings = np.vstack(all_embeddings_list)

        # Build indexes
        self.bm25_index.build(all_tokenized, all_doc_ids)
        self.faiss_index.build(all_embeddings, all_doc_ids, all_cached_docs)

        self.save_index()
        self._initialized = True

        logger.info(f"✅ Index built! Total: {processed:,} documents")

    # ========================================================================
    #                    OTHER METHODS (giữ nguyên)
    # ========================================================================

    def save_index(self):
        """Save all indexes to disk"""
        logger.info("Saving indexes...")
        self.faiss_index.save()
        self.bm25_index.save()
        logger.info("Indexes saved!")

    def load_index(self):
        """Load existing indexes from disk"""
        logger.info("Loading indexes...")
        self.embedding_service.load()
        self.faiss_index.embedding_dim = self.embedding_service.embedding_dim
        self.faiss_index.load()
        self.bm25_index.load()
        self._initialized = True
        logger.info("Indexes loaded!")

    def load_or_build(self, documents: Optional[List[Dict[str, Any]]] = None):
        """Load existing index hoặc build mới"""
        if self.index_exists():
            self.load_index()
        elif documents:
            self.build_index(documents)
        else:
            raise ValueError("No existing index and no documents provided")

    def index_exists(self) -> bool:
        """Check if index files exist"""
        return self.faiss_index.exists() and self.bm25_index.exists()

    def add_documents(self, documents: List[Dict[str, Any]]):
        """Add new documents to existing index"""
        if not self.is_ready:
            raise RuntimeError("Index not loaded")

        if not documents:
            return

        logger.info(f"Adding {len(documents)} documents...")

        doc_ids = []
        contents = []
        cached_docs = []

        for doc in documents:
            doc_id = str(doc.get(self.config.id_field, ""))
            content = doc.get(self.config.content_field, "")

            doc_ids.append(doc_id)
            contents.append(content)
            cached_docs.append(self._extract_cached_fields(doc))

        tokenized_docs = self.text_processor.tokenize_batch(contents)
        self.bm25_index.add(tokenized_docs, doc_ids)

        embeddings = self._encode_in_batches(contents)
        self.faiss_index.add(embeddings, doc_ids, cached_docs)

        self.save_index()
        logger.info(f"Added {len(documents)} documents!")

    def rebuild_index(self, documents: List[Dict[str, Any]]):
        """Rebuild index từ đầu"""
        logger.info("Rebuilding index...")
        self.faiss_index.clear()
        self.bm25_index.clear()
        self.build_index(documents)

    def get_stats(self) -> IndexStats:
        """Get index statistics"""
        index_size = 0
        if self.faiss_index.exists():
            index_size = os.path.getsize(self.faiss_index.index_file) / (1024 * 1024)

        return IndexStats(
            total_documents=self.faiss_index.size,
            faiss_vectors=self.faiss_index.size,
            embedding_dim=self.faiss_index.embedding_dim,
            index_size_mb=round(index_size, 2),
            is_loaded=self.is_ready
        )

    def _extract_cached_fields(self, doc: Dict) -> Dict:
        """Extract fields to cache"""
        cached = {}
        for field in self.config.cached_fields:
            if field in doc:
                value = doc[field]
                if field == "_id":
                    value = str(value)
                cached[field] = value
        return cached

    # ========================================================================
    #                              SEARCH
    # ========================================================================

    def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        semantic_weight: Optional[float] = None,
        bm25_weight: Optional[float] = None,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """Hybrid search"""
        if not self.is_ready:
            raise RuntimeError("Index not loaded")

        if not query or not query.strip():
            return []

        top_k = top_k or self.config.default_top_k
        semantic_weight = semantic_weight if semantic_weight is not None else self.config.default_semantic_weight
        bm25_weight = bm25_weight if bm25_weight is not None else self.config.default_bm25_weight

        total_weight = semantic_weight + bm25_weight
        if total_weight == 0:
            return []
        semantic_weight /= total_weight
        bm25_weight /= total_weight

        fetch_k = min(top_k * 5, self.faiss_index.size)
        if fetch_k == 0:
            return []

        # Semantic search
        query_embedding = self.embedding_service.encode_single(query)
        semantic_results = self.faiss_index.search(query_embedding, fetch_k)

        # BM25 search
        tokenized_query = self.text_processor.tokenize(query)
        bm25_results = self.bm25_index.search(tokenized_query, fetch_k)

        # Combine
        combined = self._combine_scores(semantic_results, bm25_results, semantic_weight, bm25_weight)

        # Filter
        if filters:
            combined = self._apply_filters(combined, filters)

        # Build results
        results = []
        for rank, (idx, combined_score, score_details) in enumerate(combined[:top_k], 1):
            doc = self.faiss_index.get_document(idx)
            if doc:
                result = SearchResult(
                    doc_id=self.faiss_index.get_doc_id(idx),
                    content=doc.get(self.config.content_field, ""),
                    metadata={k: v for k, v in doc.items() if k != self.config.content_field},
                    rank=rank,
                    score_combined=combined_score,
                    score_semantic=score_details["semantic"],
                    score_bm25=score_details["bm25"]
                )
                results.append(result)

        return results

    def search_semantic_only(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        return self.search(query, top_k=top_k, semantic_weight=1.0, bm25_weight=0.0)

    def search_bm25_only(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        return self.search(query, top_k=top_k, semantic_weight=0.0, bm25_weight=1.0)

    def _combine_scores(
        self,
        semantic_results: List[Tuple[int, float]],
        bm25_results: List[Tuple[int, float]],
        semantic_weight: float,
        bm25_weight: float
    ) -> List[Tuple[int, float, Dict[str, float]]]:
        """Combine and normalize scores"""
        combined_scores: Dict[int, Dict[str, float]] = {}

        if semantic_results:
            scores = [r[1] for r in semantic_results]
            normalized = self._normalize_scores(scores)
            for (idx, _), norm_score in zip(semantic_results, normalized):
                if idx not in combined_scores:
                    combined_scores[idx] = {"semantic": 0.0, "bm25": 0.0}
                combined_scores[idx]["semantic"] = norm_score

        if bm25_results:
            scores = [r[1] for r in bm25_results]
            normalized = self._normalize_scores(scores)
            for (idx, _), norm_score in zip(bm25_results, normalized):
                if idx not in combined_scores:
                    combined_scores[idx] = {"semantic": 0.0, "bm25": 0.0}
                combined_scores[idx]["bm25"] = norm_score

        results = []
        for idx, scores in combined_scores.items():
            combined = scores["semantic"] * semantic_weight + scores["bm25"] * bm25_weight
            results.append((idx, combined, scores))

        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def _normalize_scores(self, scores: List[float]) -> List[float]:
        if not scores:
            return []
        min_s, max_s = min(scores), max(scores)
        if max_s == min_s:
            return [1.0] * len(scores)
        return [(s - min_s) / (max_s - min_s) for s in scores]

    def _apply_filters(
        self,
        results: List[Tuple[int, float, Dict]],
        filters: Dict[str, Any]
    ) -> List[Tuple[int, float, Dict]]:
        filtered = []
        for idx, score, details in results:
            doc = self.faiss_index.get_document(idx)
            if not doc:
                continue

            match = True
            for field, value in filters.items():
                if field not in doc:
                    match = False
                    break
                doc_value = doc[field]
                if isinstance(value, str) and isinstance(doc_value, str):
                    if value.lower() not in doc_value.lower():
                        match = False
                        break
                elif doc_value != value:
                    match = False
                    break

            if match:
                filtered.append((idx, score, details))

        return filtered