"""
Utility functions for LawAssistant project
"""

from src.utils.text_utils import (
    clean_text, 
    normalize_text, 
    remove_special_chars,
    remove_extra_spaces,
    remove_urls,
    remove_emails,
    truncate_text
)
from src.utils.dict_utils import (
    load_synonym_dict,
    normalize_term,
    load_stopwords,
    is_valid_term,
    get_canonical_name,
    get_synonyms
)
from src.utils.logger import setup_logger, get_logger

__all__ = [
    # Text utilities
    "clean_text",
    "normalize_text", 
    "remove_special_chars",
    "remove_extra_spaces",
    "remove_urls",
    "remove_emails",
    "truncate_text",
    
    # Dictionary utilities
    "load_synonym_dict",
    "normalize_term",
    "load_stopwords",
    "is_valid_term",
    "get_canonical_name",
    "get_synonyms",
    
    # Logging
    "setup_logger",
    "get_logger",
]
