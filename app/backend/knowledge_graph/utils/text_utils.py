"""
Text processing utilities for LawAssistant
Unified clean_text and text manipulation functions
"""

import re
from typing import Optional


def clean_text(text: str) -> str:
    """
    Clean and normalize Vietnamese legal text
    
    Removes:
    - Newlines, tabs
    - Extra whitespace
    - Special punctuation (!, ?)
    - Quotes
    - Non-alphanumeric characters (except Vietnamese and common punctuation)
    
    Args:
        text: Raw text string
        
    Returns:
        Cleaned and normalized text (lowercase)
    """
    if not text:
        return ""
    
    text = re.sub(r"[\r\n\t]+", " ", text)                # Remove newline, tab
    text = re.sub(r"\s+", " ", text)                     # Remove extra whitespace
    text = re.sub(r"[!?]+", "", text)                    # Remove !, ?
    text = text.replace('"', '')                         # Remove quotes
    text = re.sub(r"[^0-9a-zA-ZÀ-Ỹà-ỹđĐ\s\.\,\:\;\-\/]", " ", text)
    return text.strip().lower()


def normalize_text(text: str, lowercase: bool = True) -> str:
    """
    Normalize text with more options
    
    Args:
        text: Input text
        lowercase: Whether to convert to lowercase
        
    Returns:
        Normalized text
    """
    if not text:
        return ""
    
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = text.strip()
    
    if lowercase:
        text = text.lower()
    
    return text


def remove_special_chars(text: str, keep_punctuation: bool = False) -> str:
    """
    Remove special characters from text
    
    Args:
        text: Input text
        keep_punctuation: If True, keeps common punctuation (.,;:-)
        
    Returns:
        Text with special characters removed
    """
    if not text:
        return ""
    
    if keep_punctuation:
        text = re.sub(r"[^0-9a-zA-ZÀ-Ỹà-ỹđĐ\s\.\,\:\;\-]", " ", text)
    else:
        text = re.sub(r"[^0-9a-zA-ZÀ-Ỹà-ỹđĐ\s]", " ", text)
    
    text = re.sub(r"\s+", " ", text)
    return text.strip()


def remove_extra_spaces(text: str) -> str:
    """Remove multiple consecutive spaces"""
    return re.sub(r"\s+", " ", text).strip()


def remove_urls(text: str) -> str:
    """Remove URLs from text"""
    return re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)


def remove_emails(text: str) -> str:
    """Remove email addresses from text"""
    return re.sub(r'\S+@\S+', '', text)


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """
    Truncate text to maximum length
    
    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text
    return text[:max_length - len(suffix)] + suffix
