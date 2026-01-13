"""
BM25 Ranking System for Legal Document Retrieval
Uses BM25 algorithm to rank sections based on relevance to user questions
"""

import math
from collections import Counter, defaultdict
from typing import List, Dict, Any, Tuple


class BM25Ranker:
    """
    BM25 (Best Matching 25) ranking algorithm implementation
    
    Parameters:
        k1: Controls term frequency saturation (default: 1.5)
        b: Controls document length normalization (default: 0.75)
    """
    
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.corpus = []
        self.doc_lengths = []
        self.avg_doc_length = 0
        self.doc_freqs = Counter()
        self.idf_cache = {}
        self.N = 0  # Number of documents
        
    def fit(self, corpus: List[List[str]]):
        """
        Fit the BM25 model on a corpus of documents
        
        Args:
            corpus: List of documents, where each document is a list of tokens
        """
        self.corpus = corpus
        self.N = len(corpus)
        self.doc_lengths = [len(doc) for doc in corpus]
        self.avg_doc_length = sum(self.doc_lengths) / self.N if self.N > 0 else 0
        
        # Calculate document frequencies
        for doc in corpus:
            unique_terms = set(doc)
            for term in unique_terms:
                self.doc_freqs[term] += 1
        
        # Pre-calculate IDF scores
        self._calculate_idf()
    
    def _calculate_idf(self):
        """Calculate IDF (Inverse Document Frequency) for all terms"""
        for term, df in self.doc_freqs.items():
            # IDF formula: log((N - df + 0.5) / (df + 0.5) + 1)
            self.idf_cache[term] = math.log((self.N - df + 0.5) / (df + 0.5) + 1)
    
    def _get_idf(self, term: str) -> float:
        """Get IDF score for a term"""
        return self.idf_cache.get(term, 0.0)
    
    def _score_document(self, query_terms: List[str], doc_index: int) -> float:
        """
        Calculate BM25 score for a single document
        
        Args:
            query_terms: List of query tokens
            doc_index: Index of document in corpus
            
        Returns:
            BM25 score
        """
        doc = self.corpus[doc_index]
        doc_length = self.doc_lengths[doc_index]
        
        # Term frequency in document
        term_freqs = Counter(doc)
        
        score = 0.0
        for term in query_terms:
            if term not in term_freqs:
                continue
            
            tf = term_freqs[term]
            idf = self._get_idf(term)
            
            # BM25 formula
            numerator = tf * (self.k1 + 1)
            denominator = tf + self.k1 * (1 - self.b + self.b * (doc_length / self.avg_doc_length))
            
            score += idf * (numerator / denominator)
        
        return score
    
    def get_scores(self, query: List[str]) -> List[float]:
        """
        Calculate BM25 scores for all documents
        
        Args:
            query: List of query tokens
            
        Returns:
            List of scores for each document
        """
        scores = []
        for i in range(self.N):
            score = self._score_document(query, i)
            scores.append(score)
        
        return scores
    
    def rank(self, query: List[str], top_k: int = 10) -> List[Tuple[int, float]]:
        """
        Rank documents by relevance to query
        
        Args:
            query: List of query tokens
            top_k: Number of top results to return
            
        Returns:
            List of (document_index, score) tuples, sorted by score descending
        """
        scores = self.get_scores(query)
        
        # Create (index, score) pairs and sort
        ranked_docs = [(i, score) for i, score in enumerate(scores)]
        ranked_docs.sort(key=lambda x: x[1], reverse=True)
        
        return ranked_docs[:top_k]


def tokenize_vietnamese(text: str, vncorenlp_client) -> List[str]:
    """
    Tokenize Vietnamese text using VnCoreNLP
    
    Args:
        text: Input text
        vncorenlp_client: VnCoreNLP client instance
        
    Returns:
        List of tokens
    """
    segmented = vncorenlp_client.word_segment(text)
    if segmented and len(segmented) > 0:
        return segmented[0].split()
    return []


def prepare_section_corpus(sections: List[Dict[str, Any]], vncorenlp_client) -> Tuple[List[List[str]], List[str]]:
    """
    Prepare corpus from section documents
    
    Args:
        sections: List of section dictionaries with 'content' field
        vncorenlp_client: VnCoreNLP client for tokenization
        
    Returns:
        Tuple of (tokenized_corpus, section_ids)
    """
    corpus = []
    section_ids = []
    
    for section in sections:
        content = section.get('content', '')
        section_id = section.get('_id') or section.get('section_id')
        
        if content and section_id:
            tokens = tokenize_vietnamese(content, vncorenlp_client)
            corpus.append(tokens)
            section_ids.append(section_id)
    
    return corpus, section_ids


def rank_sections_bm25(
    question: str,
    sections: List[Dict[str, Any]],
    vncorenlp_client,
    top_k: int = 10,
    k1: float = 1.5,
    b: float = 0.75
) -> List[Dict[str, Any]]:
    """
    Rank sections using BM25 algorithm
    
    Args:
        question: User question
        sections: List of section documents to rank
        vncorenlp_client: VnCoreNLP client for tokenization
        top_k: Number of top results to return
        k1: BM25 k1 parameter
        b: BM25 b parameter
        
    Returns:
        List of ranked sections with BM25 scores
    """
    # Tokenize question
    query_tokens = tokenize_vietnamese(question, vncorenlp_client)
    
    if not query_tokens:
        print("Warning: Question tokenization resulted in empty tokens")
        return []
    
    # Prepare corpus
    corpus, section_ids = prepare_section_corpus(sections, vncorenlp_client)
    
    if not corpus:
        print("Warning: No valid sections to rank")
        return []
    
    # Initialize and fit BM25
    bm25 = BM25Ranker(k1=k1, b=b)
    bm25.fit(corpus)
    
    # Get rankings
    ranked_indices = bm25.rank(query_tokens, top_k=top_k)
    
    # Prepare results
    results = []
    for idx, (doc_idx, score) in enumerate(ranked_indices, 1):
        section = sections[doc_idx].copy()
        section['bm25_score'] = score
        section['rank'] = idx
        section['section_id'] = section_ids[doc_idx]
        results.append(section)
    
    return results


def hybrid_rank(
    question: str,
    sections: List[Dict[str, Any]],
    vncorenlp_client,
    triplet_scores: Dict[str, float] = None,
    top_k: int = 10,
    bm25_weight: float = 0.6,
    triplet_weight: float = 0.4
) -> List[Dict[str, Any]]:
    """
    Hybrid ranking combining BM25 and triplet-based scores
    
    Args:
        question: User question
        sections: List of section documents
        vncorenlp_client: VnCoreNLP client
        triplet_scores: Dictionary mapping section_id to triplet-based score
        top_k: Number of top results
        bm25_weight: Weight for BM25 score
        triplet_weight: Weight for triplet score
        
    Returns:
        List of ranked sections with hybrid scores
    """
    if triplet_scores is None:
        triplet_scores = {}
    
    # Get BM25 rankings
    bm25_results = rank_sections_bm25(question, sections, vncorenlp_client, top_k=len(sections))
    
    # Normalize scores
    max_bm25 = max([r['bm25_score'] for r in bm25_results]) if bm25_results else 1.0
    max_triplet = max(triplet_scores.values()) if triplet_scores else 1.0
    
    if max_bm25 == 0:
        max_bm25 = 1.0
    if max_triplet == 0:
        max_triplet = 1.0
    
    # Calculate hybrid scores
    for result in bm25_results:
        section_id = result['section_id']
        
        normalized_bm25 = result['bm25_score'] / max_bm25
        normalized_triplet = triplet_scores.get(section_id, 0.0) / max_triplet
        
        hybrid_score = (bm25_weight * normalized_bm25) + (triplet_weight * normalized_triplet)
        
        result['triplet_score'] = triplet_scores.get(section_id, 0.0)
        result['normalized_bm25'] = normalized_bm25
        result['normalized_triplet'] = normalized_triplet
        result['hybrid_score'] = hybrid_score
    
    # Sort by hybrid score
    bm25_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
    
    # Update ranks
    for idx, result in enumerate(bm25_results[:top_k], 1):
        result['rank'] = idx
    
    return bm25_results[:top_k]
