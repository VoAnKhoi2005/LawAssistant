"""Embedding service using SentenceTransformers"""

import logging
from typing import List, Optional
import numpy as np
from sentence_transformers import SentenceTransformer

logger = logging.getLogger(__name__)


class EmbeddingService:
    """
    Quản lý embedding model
    - Load model
    - Encode texts to vectors
    """

    def __init__(self, model_name: str = "bkai-foundation-models/vietnamese-bi-encoder"):
        """
        Initialize embedding service

        Args:
            model_name: HuggingFace model name
        """
        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self._embedding_dim: Optional[int] = None

    def load(self):
        """Load embedding model"""
        if self.model is not None:
            return

        logger.info(f"Loading embedding model: {self.model_name}")
        self.model = SentenceTransformer(self.model_name)
        self._embedding_dim = self.model.get_sentence_embedding_dimension()
        logger.info(f"Model loaded. Embedding dimension: {self._embedding_dim}")

    @property
    def embedding_dim(self) -> int:
        """Get embedding dimension"""
        if self._embedding_dim is None:
            self.load()
        return self._embedding_dim

    def encode(
            self,
            texts: List[str],
            batch_size: int = 500,
            show_progress: bool = True,
            normalize: bool = True
    ) -> np.ndarray:
        """
        Encode texts to embeddings

        Args:
            texts: List of texts
            batch_size: Batch size for encoding
            show_progress: Show progress bar
            normalize: Normalize vectors (for cosine similarity)

        Returns:
            numpy array of embeddings (n_texts, embedding_dim)
        """
        if self.model is None:
            self.load()

        embeddings = self.model.encode(
            texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )

        return embeddings.astype('float32')

    def encode_single(self, text: str, normalize: bool = True) -> np.ndarray:
        """
        Encode single text

        Args:
            text: Text to encode
            normalize: Normalize vector

        Returns:
            numpy array of shape (embedding_dim,)
        """
        if self.model is None:
            self.load()

        embedding = self.model.encode(
            text,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )

        return embedding.astype('float32')