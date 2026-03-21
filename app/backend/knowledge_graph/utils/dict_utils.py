"""
Dictionary and term normalization utilities
"""

import re
import csv
from typing import Dict, Set, Optional


def load_synonym_dict(filepath: str) -> Dict[str, Dict]:
    """
    Load synonym mappings from listSameKey.txt
    
    Format: key#word1, word2, word3
    First word is canonical name
    
    Args:
        filepath: Path to synonym dictionary file
        
    Returns:
        Dictionary with 'canonical' and 'synonyms' mappings
    """
    canonical_map = {}
    synonyms_map = {}

    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            if not line.strip() or "#" not in line:
                continue
            key, words_str = line.strip().split("#", 1)
            words = [w.strip().lower().replace("_", " ") for w in words_str.split(",") if w.strip()]

            if not words:
                continue

            # First word is the canonical name
            canonical_name = words[0]

            # Map all words (including canonical) to the canonical name
            for word in words:
                canonical_map[word] = canonical_name

            # Store all synonyms (excluding the canonical name itself)
            synonyms_map[canonical_name] = [w for w in words[1:] if w]

    return {'canonical': canonical_map, 'synonyms': synonyms_map}


def normalize_term(term: str, synonym_dict: Optional[Dict] = None) -> Optional[str]:
    """
    Normalize term by:
    1. Removing underscores and extra spaces
    2. Lowercasing
    3. Mapping to canonical name if exists in synonym dict
    
    Args:
        term: Input term
        synonym_dict: Synonym dictionary from load_synonym_dict
        
    Returns:
        Normalized term or None if invalid
    """
    if not term:
        return None
    
    term = re.sub(r"_+", " ", term)  # Replace underscores with space
    term = re.sub(r"\s+", " ", term.strip())  # Clean multiple spaces
    term = term.lower()

    # Map to canonical name if exists
    if synonym_dict and 'canonical' in synonym_dict:
        return synonym_dict['canonical'].get(term, term)
    return term


def load_stopwords(stopword_file: str, column_index: int = 1) -> Set[str]:
    """
    Load stopwords from CSV file
    
    Args:
        stopword_file: Path to CSV file
        column_index: Column index containing stopwords (0-based)
        
    Returns:
        Set of stopwords (lowercase)
    """
    stopwords = set()
    try:
        with open(stopword_file, 'r', encoding='utf-8') as f:
            reader = csv.reader(f)
            for row in reader:
                if row and len(row) > column_index:
                    stopwords.add(row[column_index].strip().lower())
    except Exception as e:
        print(f"Error loading stopwords: {e}")
    return stopwords


def is_valid_term(term: str, stopwords: Set[str]) -> bool:
    """
    Check if term is valid (not stopword and not empty)
    
    Args:
        term: Input term
        stopwords: Set of stopwords
        
    Returns:
        True if valid, False otherwise
    """
    if not term or not term.strip():
        return False
    return term.lower() not in stopwords


def get_canonical_name(term: str, synonym_dict: Dict) -> Optional[str]:
    """
    Get canonical name for a term from synonym dictionary
    
    Args:
        term: Input term
        synonym_dict: Synonym dictionary
        
    Returns:
        Canonical name or original term if not found
    """
    term_normalized = normalize_term(term, None)
    if synonym_dict and 'canonical' in synonym_dict:
        return synonym_dict['canonical'].get(term_normalized, term_normalized)
    return term_normalized


def get_synonyms(term: str, synonym_dict: Dict) -> list:
    """
    Get all synonyms for a term
    
    Args:
        term: Input term
        synonym_dict: Synonym dictionary
        
    Returns:
        List of synonyms (excluding the term itself)
    """
    canonical = get_canonical_name(term, synonym_dict)
    if synonym_dict and 'synonyms' in synonym_dict:
        return synonym_dict['synonyms'].get(canonical, [])
    return []
