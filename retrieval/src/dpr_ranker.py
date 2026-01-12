"""
Dense Passage Retrieval (DPR) System for Legal Document Retrieval
Uses Vietnamese language models to encode questions and passages into dense vectors
"""

import numpy as np
from typing import List, Dict, Any, Tuple, Optional
import torch
from transformers import AutoTokenizer, AutoModel


class DPRRanker:
    """
    Dense Passage Retrieval using Vietnamese language models
    
    Supports models like:
    - vinai/phobert-base
    - vinai/bartpho-word
    - VoVanPhuc/sup-SimCSE-VietNamese-phobert-base
    """
    
    def __init__(
        self, 
        model_name: str = "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base",
        device: str = None,
        use_fp16: bool = True
    ):
        """
        Initialize DPR ranker with a Vietnamese language model
        
        Args:
            model_name: HuggingFace model name
            device: 'cuda' or 'cpu', auto-detected if None
            use_fp16: Use half precision (FP16) on GPU for faster inference
        """
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.use_fp16 = use_fp16 and self.device == 'cuda'
        
        print(f"Loading DPR model: {model_name} on {self.device}")
        if self.use_fp16:
            print("Using FP16 precision for faster inference")
        
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name).to(self.device)
        
        # Convert to half precision if using GPU
        if self.use_fp16:
            self.model = self.model.half()
        
        self.model.eval()
        
        self.corpus_embeddings = None
        self.section_ids = []
        
    def _mean_pooling(self, model_output, attention_mask):
        """Apply mean pooling to get sentence embeddings"""
        token_embeddings = model_output[0]
        input_mask_expanded = attention_mask.unsqueeze(-1).expand(token_embeddings.size()).float()
        return torch.sum(token_embeddings * input_mask_expanded, 1) / torch.clamp(input_mask_expanded.sum(1), min=1e-9)
    
    def encode(
        self, 
        texts: List[str], 
        batch_size: int = 32,
        max_length: int = 256,
        show_progress: bool = True
    ) -> np.ndarray:
        """
        Encode texts into dense vectors
        
        Args:
            texts: List of text strings
            batch_size: Batch size for encoding (larger for GPU)
            max_length: Maximum token length
            show_progress: Show progress bar
            
        Returns:
            Array of embeddings (n_texts, embedding_dim)
        """
        # Increase batch size for GPU
        if self.device == 'cuda' and batch_size == 32:
            batch_size = 64
            print(f"Using GPU batch size: {batch_size}")
        
        embeddings = []
        
        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]
                
                if show_progress and (i % (batch_size * 5) == 0 or i == 0):
                    print(f"Encoding batch {i//batch_size + 1}/{(len(texts)-1)//batch_size + 1} ({len(embeddings) * batch_size}/{len(texts)} texts)")
                
                # Tokenize
                encoded = self.tokenizer(
                    batch_texts,
                    padding=True,
                    truncation=True,
                    max_length=max_length,
                    return_tensors='pt'
                ).to(self.device)
                
                # Get embeddings
                model_output = self.model(**encoded)
                batch_embeddings = self._mean_pooling(model_output, encoded['attention_mask'])
                
                # Normalize
                batch_embeddings = torch.nn.functional.normalize(batch_embeddings, p=2, dim=1)
                
                embeddings.append(batch_embeddings.cpu().numpy())
        
        return np.vstack(embeddings)
    
    def fit(
        self, 
        passages: List[str], 
        section_ids: List[str],
        batch_size: int = 32
    ):
        """
        Encode all passages in the corpus
        
        Args:
            passages: List of passage texts
            section_ids: List of section IDs corresponding to passages
            batch_size: Batch size for encoding
        """
        print(f"\nEncoding {len(passages)} passages for DPR...")
        self.section_ids = section_ids
        self.corpus_embeddings = self.encode(passages, batch_size=batch_size)
        print(f"Corpus embeddings shape: {self.corpus_embeddings.shape}")
    
    def search(
        self, 
        query: str, 
        top_k: int = 10
    ) -> List[Tuple[int, float]]:
        """
        Search for most similar passages to query
        
        Args:
            query: Query text
            top_k: Number of top results
            
        Returns:
            List of (doc_index, similarity_score) tuples
        """
        if self.corpus_embeddings is None:
            raise ValueError("Corpus not fitted. Call fit() first.")
        
        # Encode query
        query_embedding = self.encode([query], batch_size=1, show_progress=False)[0]
        
        # Compute cosine similarity (embeddings are already normalized)
        similarities = np.dot(self.corpus_embeddings, query_embedding)
        
        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        return [(int(idx), float(similarities[idx])) for idx in top_indices]


def prepare_section_corpus_dpr(sections: List[Dict[str, Any]]) -> Tuple[List[str], List[str]]:
    """
    Prepare corpus from section documents for DPR
    
    Args:
        sections: List of section dictionaries with 'content' field
        
    Returns:
        Tuple of (passages, section_ids)
    """
    passages = []
    section_ids = []
    
    for section in sections:
        content = section.get('content', '')
        section_id = section.get('_id') or section.get('section_id')
        
        if content and section_id:
            passages.append(content)
            section_ids.append(section_id)
    
    return passages, section_ids


def rank_sections_dpr(
    question: str,
    sections: List[Dict[str, Any]],
    dpr_ranker: DPRRanker = None,
    model_name: str = "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base",
    top_k: int = 10,
    batch_size: int = None
) -> List[Dict[str, Any]]:
    """
    Rank sections using Dense Passage Retrieval
    
    Args:
        question: User question
        sections: List of section documents to rank
        dpr_ranker: Pre-initialized DPR ranker (optional, will create if None)
        model_name: Model name if creating new ranker
        top_k: Number of top results to return
        batch_size: Batch size for encoding (auto-detected if None)
        
    Returns:
        List of ranked sections with DPR scores
    """
    if not sections:
        print("Warning: No sections to rank")
        return []
    
    print(f"DPR ranking {len(sections)} sections...")
    
    # Initialize DPR if not provided
    if dpr_ranker is None:
        dpr_ranker = DPRRanker(model_name=model_name)
    
    # Auto-detect batch size based on device
    if batch_size is None:
        batch_size = 64 if dpr_ranker.device == 'cuda' else 16
    
    # Prepare corpus
    passages, section_ids = prepare_section_corpus_dpr(sections)
    
    if not passages:
        print("Warning: No valid sections to rank")
        return []
    
    # Fit DPR on corpus
    dpr_ranker.fit(passages, section_ids, batch_size=batch_size)
    
    # Search
    ranked_indices = dpr_ranker.search(question, top_k=min(top_k, len(passages)))
    
    # Prepare results
    results = []
    for rank, (doc_idx, score) in enumerate(ranked_indices, 1):
        section = sections[doc_idx].copy()
        section['dpr_score'] = score
        section['rank'] = rank
        section['section_id'] = section_ids[doc_idx]
        results.append(section)
    
    return results


def hybrid_rank_bm25_dpr(
    question: str,
    sections: List[Dict[str, Any]],
    vncorenlp_client,
    dpr_ranker: DPRRanker = None,
    triplet_scores: Dict[str, float] = None,
    top_k: int = 10,
    bm25_weight: float = 0.4,
    dpr_weight: float = 0.4,
    triplet_weight: float = 0.2
) -> List[Dict[str, Any]]:
    """
    Hybrid ranking combining BM25, DPR, and graph-based triplet scores
    
    Args:
        question: User question
        sections: List of section documents
        vncorenlp_client: VnCoreNLP client for BM25 tokenization
        dpr_ranker: Pre-initialized DPR ranker (optional)
        triplet_scores: Dictionary mapping section_id to triplet-based score
        top_k: Number of top results
        bm25_weight: Weight for BM25 score (default: 0.4)
        dpr_weight: Weight for DPR score (default: 0.4)
        triplet_weight: Weight for triplet score (default: 0.2)
        
    Returns:
        List of ranked sections with hybrid scores
    """
    from retrieval.src.bm25_ranker import rank_sections_bm25
    
    if triplet_scores is None:
        triplet_scores = {}
    
    # Get BM25 rankings
    print("\n=== BM25 RANKING ===")
    bm25_results = rank_sections_bm25(question, sections, vncorenlp_client, top_k=len(sections))
    
    # Get DPR rankings
    print("\n=== DPR RANKING ===")
    dpr_results = rank_sections_dpr(question, sections, dpr_ranker=dpr_ranker, top_k=len(sections))
    
    # Create lookup dictionaries
    bm25_scores = {r['section_id']: r['bm25_score'] for r in bm25_results}
    dpr_scores_dict = {r['section_id']: r['dpr_score'] for r in dpr_results}
    
    # Normalize scores
    max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
    max_dpr = max(dpr_scores_dict.values()) if dpr_scores_dict else 1.0
    max_triplet = max(triplet_scores.values()) if triplet_scores else 1.0
    
    if max_bm25 == 0:
        max_bm25 = 1.0
    if max_dpr == 0:
        max_dpr = 1.0
    if max_triplet == 0:
        max_triplet = 1.0
    
    # Calculate hybrid scores
    print("\n=== HYBRID SCORING (BM25 + DPR + Triplet) ===")
    hybrid_results = []
    
    for section in sections:
        section_id = section.get('_id') or section.get('section_id')
        
        normalized_bm25 = bm25_scores.get(section_id, 0.0) / max_bm25
        normalized_dpr = dpr_scores_dict.get(section_id, 0.0) / max_dpr
        normalized_triplet = triplet_scores.get(section_id, 0.0) / max_triplet
        
        hybrid_score = (
            bm25_weight * normalized_bm25 + 
            dpr_weight * normalized_dpr + 
            triplet_weight * normalized_triplet
        )
        
        result = section.copy()
        result['section_id'] = section_id
        result['bm25_score'] = bm25_scores.get(section_id, 0.0)
        result['dpr_score'] = dpr_scores_dict.get(section_id, 0.0)
        result['triplet_score'] = triplet_scores.get(section_id, 0.0)
        result['normalized_bm25'] = normalized_bm25
        result['normalized_dpr'] = normalized_dpr
        result['normalized_triplet'] = normalized_triplet
        result['hybrid_score'] = hybrid_score
        
        hybrid_results.append(result)
    
    # Sort by hybrid score
    hybrid_results.sort(key=lambda x: x['hybrid_score'], reverse=True)
    
    # Add ranks
    for rank, result in enumerate(hybrid_results[:top_k], 1):
        result['rank'] = rank
    
    print(f"Weights: BM25={bm25_weight}, DPR={dpr_weight}, Triplet={triplet_weight}")
    
    return hybrid_results[:top_k]
