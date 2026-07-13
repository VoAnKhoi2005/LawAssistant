"""Vietnamese text processing"""

import re
from typing import List
from underthesea import word_tokenize


class TextProcessor:
    """
    Xử lý text tiếng Việt
    - Preprocessing
    - Tokenization
    """

    # Vietnamese characters pattern
    VIETNAMESE_PATTERN = re.compile(
        r'[^\w\sàáảãạăằắẳẵặâầấẩẫậèéẻẽẹêềếểễệìíỉĩịòóỏõọôồốổỗộơờớởỡợùúủũụưừứửữựỳýỷỹỵđ]',
        re.IGNORECASE
    )

    def preprocess(self, text: str) -> str:
        """
        Tiền xử lý text

        Args:
            text: Raw text

        Returns:
            Preprocessed text
        """
        if not text:
            return ""

        text = text.lower().strip()
        text = self.VIETNAMESE_PATTERN.sub(' ', text)
        text = re.sub(r'\s+', ' ', text).strip()

        return text

    def tokenize(self, text: str) -> List[str]:
        """
        Tokenize text tiếng Việt

        Args:
            text: Text to tokenize

        Returns:
            List of tokens
        """
        text = self.preprocess(text)

        if not text:
            return []

        try:
            tokens = word_tokenize(text, format="text").split()
            return tokens
        except Exception:
            # Fallback to simple split
            return text.split()

    def tokenize_batch(self, texts: List[str]) -> List[List[str]]:
        """
        Tokenize nhiều texts

        Args:
            texts: List of texts

        Returns:
            List of token lists
        """
        return [self.tokenize(text) for text in texts]