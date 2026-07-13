"""BM25 Index management"""

import os
import logging
import pickle
from typing import List, Tuple, Optional

import numpy as np
from rank_bm25 import BM25Okapi

logger = logging.getLogger(__name__)


class BM25Index:
    """
    Quản lý BM25 Index
    - Build index
    - Save/Load
    - Search
    """

    def __init__(self, index_path: str = "./bm25_index"):
        """
        Initialize BM25 Index

        Args:
            index_path: Directory to store index files
        """
        self.index_path = index_path
        self.index_file = os.path.join(index_path, "bm25.pkl")

        self.bm25: Optional[BM25Okapi] = None
        self.tokenized_corpus: List[List[str]] = []
        self.doc_ids: List[str] = []

    @property
    def is_loaded(self) -> bool:
        """Check if index is loaded"""
        return self.bm25 is not None

    @property
    def size(self) -> int:
        """Get number of documents"""
        return len(self.doc_ids)

    def exists(self) -> bool:
        """Check if index file exists"""
        return os.path.exists(self.index_file)

    def build(self, tokenized_corpus: List[List[str]], doc_ids: List[str]):
        """
        Build BM25 index

        Args:
            tokenized_corpus: List of tokenized documents
            doc_ids: List of document IDs
        """
        logger.info(f"Building BM25 index with {len(doc_ids)} documents...")

        assert len(tokenized_corpus) == len(doc_ids), "Length mismatch"

        self.tokenized_corpus = tokenized_corpus
        self.doc_ids = doc_ids
        self.bm25 = BM25Okapi(tokenized_corpus)

        logger.info(f"BM25 index built: {len(doc_ids)} documents")

    def save(self):
        """Save index to disk"""
        if not self.is_loaded:
            raise RuntimeError("No index to save")

        os.makedirs(self.index_path, exist_ok=True)

        data = {
            "tokenized_corpus": self.tokenized_corpus,
            "doc_ids": self.doc_ids
        }

        with open(self.index_file, "wb") as f:
            pickle.dump(data, f)

        logger.info(f"BM25 index saved to {self.index_path}")

    def load(self):
        """Load index from disk"""
        if not self.exists():
            raise FileNotFoundError(f"Index not found at {self.index_path}")

        with open(self.index_file, "rb") as f:
            data = pickle.load(f)

        self.tokenized_corpus = data["tokenized_corpus"]
        self.doc_ids = data["doc_ids"]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        logger.info(f"BM25 index loaded: {len(self.doc_ids)} documents")

    def search(self, tokenized_query: List[str], top_k: int) -> List[Tuple[int, float]]:
        """
        Search documents

        Args:
            tokenized_query: Tokenized query
            top_k: Number of results

        Returns:
            List of (index_position, score)
        """
        if not self.is_loaded:
            raise RuntimeError("Index not loaded")

        if not tokenized_query:
            return []

        scores = self.bm25.get_scores(tokenized_query)

        top_indices = np.argsort(scores)[::-1][:top_k]

        results = [
            (int(idx), float(scores[idx]))
            for idx in top_indices
            if scores[idx] > 0
        ]

        return results

    def add(self, tokenized_docs: List[List[str]], doc_ids: List[str]):
        """
        Add new documents - requires rebuild

        Note: BM25 cần toàn bộ corpus để tính IDF,
        nên phải rebuild khi add documents mới

        Args:
            tokenized_docs: List of tokenized documents
            doc_ids: List of document IDs
        """
        assert len(tokenized_docs) == len(doc_ids), "Length mismatch"

        self.tokenized_corpus.extend(tokenized_docs)
        self.doc_ids.extend(doc_ids)

        # Rebuild BM25 với corpus mới
        self.bm25 = BM25Okapi(self.tokenized_corpus)

        logger.info(f"Added {len(doc_ids)} documents. Total: {len(self.doc_ids)}")

    def clear(self):
        """Clear index"""
        self.bm25 = None
        self.tokenized_corpus = []
        self.doc_ids = []