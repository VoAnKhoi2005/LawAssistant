"""
Query Preprocessing Pipeline
Bước 1: Normalize (từ JSON)
Bước 2: LLM Refine
"""

import logging
from typing import Optional
from pathlib import Path

from .normalizer import QueryNormalizer
from .llm_refiner import LLMRefiner

logger = logging.getLogger(__name__)


class QueryPreprocessor:
    """
    Pipeline tiền xử lý query

    Flow:
        Input → Normalize (JSON) → LLM Refine → Output

    Usage:
        preprocessor = QueryPreprocessor(
            openai_api_key="your-key",
            json_path="abbreviations.json"
        )
        result = preprocessor.process("Thủ tục đkkd & bhxh ko?")
    """

    def __init__(
            self,
            openai_api_key: str,
            openai_model: str = "gpt-4o-mini",
            json_path: Optional[str] = None,
            openai_base_url: Optional[str] = None
    ):
        """
        Args:
            openai_api_key: OpenAI API key
            openai_model: Model name
            json_path: Path to abbreviations JSON file
            openai_base_url: Custom API endpoint
        """
        # Bước 1: Normalizer
        self.normalizer = QueryNormalizer(json_path=json_path)

        # Bước 2: LLM Refiner
        self.refiner = LLMRefiner(
            api_key=openai_api_key,
            model=openai_model,
            base_url=openai_base_url
        )

        logger.info("QueryPreprocessor initialized")

    def process(self, query: str) -> str:
        """
        Xử lý query qua pipeline

        Args:
            query: Query gốc từ người dùng

        Returns:
            Query đã xử lý
        """
        if not query or not query.strip():
            return ""

        # Bước 1: Normalize
        normalized = self.normalizer.normalize(query)
        logger.debug(f"Normalized: {normalized}")

        # Bước 2: LLM Refine
        refined = self.refiner.refine(normalized)
        logger.debug(f"Refined: {refined}")

        return refined

    def process_normalize_only(self, query: str) -> str:
        """
        Chỉ chạy bước Normalize (không gọi LLM)

        Args:
            query: Query gốc

        Returns:
            Query đã normalize
        """
        if not query or not query.strip():
            return ""
        return self.normalizer.normalize(query)

    def reload_normalizer(self):
        """Reload normalizer từ JSON file"""
        self.normalizer.reload()


__all__ = ["QueryPreprocessor"]