"""
Bước 1: Chuẩn hóa từ viết tắt
Load từ file JSON
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class QueryNormalizer:
    # Vietnamese characters cho word boundary
    VIET_CHARS = r'a-zA-ZàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđĐ'

    def __init__(self, json_path: Optional[str] = None):
        """
        Args:
            json_path: Path to JSON file, None = use default (same dir)
        """
        if json_path is None:
            # Default: abbreviations.json trong cùng thư mục
            json_path = Path(__file__).parent / "abbreviations.json"
        else:
            json_path = Path(json_path)

        self.json_path = json_path

        # Load dictionaries
        self.word_dict: Dict[str, str] = {}
        self.punctuation_dict: Dict[str, str] = {}

        self._load_from_json()
        self._build_pattern()

        logger.info(
            f"QueryNormalizer initialized: "
            f"{len(self.word_dict)} words, "
            f"{len(self.punctuation_dict)} punctuation"
        )

    def _load_from_json(self):
        """Load dictionaries từ JSON file"""
        if not self.json_path.exists():
            logger.error(f"JSON file not found: {self.json_path}")
            raise FileNotFoundError(f"JSON file not found: {self.json_path}")

        logger.info(f"Loading from: {self.json_path}")

        with open(self.json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Load abbreviations (lowercase keys)
        self.word_dict = {
            key.lower(): value
            for key, value in data.get("abbreviations", {}).items()
        }

        # Load punctuation
        self.punctuation_dict = data.get("punctuation", {})

        logger.debug(
            f"Loaded {len(self.word_dict)} abbreviations, "
            f"{len(self.punctuation_dict)} punctuation"
        )

    def _build_pattern(self):
        """Build regex pattern cho word matching"""
        if not self.word_dict:
            self.pattern = None
            return

        # Sort by length (longer first) để match chính xác
        sorted_words = sorted(self.word_dict.keys(), key=len, reverse=True)
        escaped = [re.escape(w) for w in sorted_words]

        # Pattern với word boundary cho tiếng Việt
        self.pattern = re.compile(
            rf'(?<![{self.VIET_CHARS}0-9_])' +
            r'(' + '|'.join(escaped) + r')' +
            rf'(?![{self.VIET_CHARS}0-9_])',
            re.IGNORECASE
        )

    def _replace_punctuation(self, text: str) -> str:
        """Thay thế ký tự đặc biệt"""
        for char, replacement in self.punctuation_dict.items():
            text = text.replace(char, replacement)
        return text

    def _replace_words(self, text: str) -> str:
        """Thay thế từ viết tắt"""
        if not self.pattern:
            return text

        def replacer(match):
            word = match.group(1)
            key = word.lower()
            replacement = self.word_dict.get(key, word)

            # Giữ viết hoa nếu từ gốc viết hoa
            if word[0].isupper() and replacement[0].islower():
                replacement = replacement[0].upper() + replacement[1:]

            return replacement

        return self.pattern.sub(replacer, text)

    def _normalize_whitespace(self, text: str) -> str:
        """Chuẩn hóa khoảng trắng"""
        # Gộp nhiều spaces
        text = re.sub(r'\s+', ' ', text)
        # Xóa space trước dấu câu
        text = re.sub(r'\s+([.,!?;:])', r'\1', text)
        # Thêm space sau dấu câu nếu thiếu
        text = re.sub(r'([.,!?;:])([^\s\d\)])', r'\1 \2', text)
        return text.strip()

    def normalize(self, text: str) -> str:
        """
        Chuẩn hóa query

        Args:
            text: Query gốc

        Returns:
            Query đã chuẩn hóa
        """
        if not text or not text.strip():
            return ""

        # Bước 1: Thay thế punctuation
        text = self._replace_punctuation(text)

        # Bước 2: Thay thế từ viết tắt
        text = self._replace_words(text)

        # Bước 3: Chuẩn hóa khoảng trắng
        text = self._normalize_whitespace(text)

        return text

    def reload(self):
        """Reload từ JSON file"""
        self._load_from_json()
        self._build_pattern()
        logger.info("Reloaded from JSON")


__all__ = ["QueryNormalizer"]