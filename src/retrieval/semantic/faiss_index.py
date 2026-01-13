"""FAISS Index management"""

import os
import logging
import pickle
from typing import List, Tuple, Optional, Dict, Any

import faiss
import numpy as np

logger = logging.getLogger(__name__)


class FAISSIndex:
    """
    Quản lý FAISS Index
    - Build index
    - Save/Load
    - Search
    - Add vectors
    """

    def __init__(self, embedding_dim: int, index_path: str = "./faiss_index"):
        """
        Initialize FAISS Index

        Args:
            embedding_dim: Dimension of embeddings
            index_path: Directory to store index files
        """
        self.embedding_dim = embedding_dim
        self.index_path = index_path

        self.index_file = os.path.join(index_path, "faiss.index")
        self.metadata_file = os.path.join(index_path, "faiss_metadata.pkl")

        self.index: Optional[faiss.Index] = None
        self.doc_ids: List[str] = []  # Mapping: index position -> doc_id
        self.documents: List[Dict] = []  # Cached document data

    @property
    def is_loaded(self) -> bool:
        """Check if index is loaded"""
        return self.index is not None

    @property
    def size(self) -> int:
        """Get number of vectors in index"""
        return self.index.ntotal if self.index else 0

    def exists(self) -> bool:
        """Check if index files exist"""
        return os.path.exists(self.index_file) and os.path.exists(self.metadata_file)

    def build(
            self,
            embeddings: np.ndarray,
            doc_ids: List[str],
            documents: List[Dict]
    ):
        """
        Build FAISS index

        Args:
            embeddings: numpy array (n_docs, embedding_dim)
            doc_ids: List of document IDs
            documents: List of document metadata dicts
        """
        logger.info(f"Building FAISS index with {len(doc_ids)} vectors...")

        assert len(embeddings) == len(doc_ids) == len(documents), \
            "Length mismatch between embeddings, doc_ids, and documents"

        # Create flat index (exact search, good for < 100K docs)
        self.index = faiss.IndexFlatIP(self.embedding_dim)
        self.index.add(embeddings)

        self.doc_ids = doc_ids
        self.documents = documents

        logger.info(f"FAISS index built: {self.index.ntotal} vectors")

    def save(self):
        """Save index to disk"""
        if not self.is_loaded:
            raise RuntimeError("No index to save")

        os.makedirs(self.index_path, exist_ok=True)

        # Save FAISS index
        faiss.write_index(self.index, self.index_file)

        # Save metadata
        metadata = {
            "doc_ids": self.doc_ids,
            "documents": self.documents,
            "embedding_dim": self.embedding_dim
        }
        with open(self.metadata_file, "wb") as f:
            pickle.dump(metadata, f)

        logger.info(f"FAISS index saved to {self.index_path}")

    def load(self):
        """Load index from disk"""
        if not self.exists():
            raise FileNotFoundError(f"Index not found at {self.index_path}")

        # Load FAISS index
        self.index = faiss.read_index(self.index_file)

        # Load metadata
        with open(self.metadata_file, "rb") as f:
            metadata = pickle.load(f)

        self.doc_ids = metadata["doc_ids"]
        self.documents = metadata["documents"]

        logger.info(f"FAISS index loaded: {self.index.ntotal} vectors")

    def search(self, query_embedding: np.ndarray, top_k: int) -> List[Tuple[int, float]]:
        """
        Search similar vectors

        Args:
            query_embedding: Query vector (embedding_dim,) or (1, embedding_dim)
            top_k: Number of results

        Returns:
            List of (index_position, score)
        """
        if not self.is_loaded:
            raise RuntimeError("Index not loaded")

        # Reshape if needed
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)

        # Search
        scores, indices = self.index.search(query_embedding, top_k)

        results = [
            (int(idx), float(score))
            for idx, score in zip(indices[0], scores[0])
            if idx != -1 and idx < len(self.doc_ids)
        ]

        return results

    def add(self, embeddings: np.ndarray, doc_ids: List[str], documents: List[Dict]):
        """
        Add new vectors to index

        Args:
            embeddings: numpy array (n_new, embedding_dim)
            doc_ids: List of new document IDs
            documents: List of new document metadata
        """
        if not self.is_loaded:
            raise RuntimeError("Index not loaded")

        assert len(embeddings) == len(doc_ids) == len(documents), \
            "Length mismatch"

        self.index.add(embeddings)
        self.doc_ids.extend(doc_ids)
        self.documents.extend(documents)

        logger.info(f"Added {len(doc_ids)} vectors. Total: {self.index.ntotal}")

    def get_document(self, index_pos: int) -> Optional[Dict]:
        """Get document by index position"""
        if 0 <= index_pos < len(self.documents):
            return self.documents[index_pos]
        return None

    def get_doc_id(self, index_pos: int) -> Optional[str]:
        """Get doc_id by index position"""
        if 0 <= index_pos < len(self.doc_ids):
            return self.doc_ids[index_pos]
        return None

    def clear(self):
        """Clear index"""
        self.index = None
        self.doc_ids = []
        self.documents = []