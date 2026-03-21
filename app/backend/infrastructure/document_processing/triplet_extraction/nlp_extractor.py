from typing import List, Tuple
import os
import logging
import phonlp
from core.interfaces.triplet_extractor_interface import ITripletExtractor
from knowledge_graph.triplet_extraction.pos_taging.my_vncorenlp import init_vncorenlp
from knowledge_graph.triplet_extraction.triplet_extraction import triplet_extraction
from knowledge_graph.triplet_extraction.utils import load_synonym_dict, load_stopwords, setup_logger


class NLPTripletExtractor(ITripletExtractor):
    """VnCoreNLP + PhoBERT-based triplet extractor"""
    
    def __init__(
        self,
        vncorenlp_dir: str,
        phonlp_dir: str,
        synonym_file: str = None,
        stopwords_file: str = None
    ):
        self.vncorenlp_dir = vncorenlp_dir
        self.phonlp_dir = phonlp_dir
        self.synonym_file = synonym_file
        self.stopwords_file = stopwords_file
        
        # Lazy initialization
        self._vncorenlp_client = None
        self._phoNLP_model = None
        self._synonym_dict = None
        self._stopwords = None
        self._logger = None
    
    def _initialize_models(self):
        """Initialize NLP models lazily"""
        if self._vncorenlp_client is None:
            self._vncorenlp_client = init_vncorenlp(self.vncorenlp_dir)
        
        if self._phoNLP_model is None:
            self._phoNLP_model = phonlp.load(save_dir=self.phonlp_dir)
        
        if self._synonym_dict is None:
            if self.synonym_file and os.path.exists(self.synonym_file):
                self._synonym_dict = load_synonym_dict(self.synonym_file)
            else:
                self._synonym_dict = {}
        
        if self._stopwords is None:
            if self.stopwords_file and os.path.exists(self.stopwords_file):
                self._stopwords = load_stopwords(self.stopwords_file)
            else:
                self._stopwords = set()
        
        if self._logger is None:
            self._logger, _, _ = setup_logger(
                name="triplet_extraction",
                level=logging.DEBUG,
                log_to_file=False
            )
    
    async def extract_triplets(self, sentences: List[str]) -> List[Tuple[str, str, str]]:
        """Extract triplets using VnCoreNLP and PhoBERT"""
        self._initialize_models()
        
        all_triplets = []
        
        for sentence in sentences:
            if not sentence or not sentence.strip():
                continue
            
            try:
                triplets = triplet_extraction(
                    text=sentence,
                    vncorenlp_client=self._vncorenlp_client,
                    phoNLP_model=self._phoNLP_model,
                    stopwords=self._stopwords,
                    logger=self._logger,
                    max_depth=3,
                )
                
                # Filter and convert to list of tuples
                for (c1, r, c2) in triplets:
                    if c1 and r and c2:
                        all_triplets.append((c1, r, c2))
                        
            except Exception as e:
                print(f"Error extracting triplets from sentence: {str(e)}")
                continue
        
        return all_triplets
