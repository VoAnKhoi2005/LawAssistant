from abc import ABC, abstractmethod
from typing import List, Tuple


class ITripletExtractor(ABC):
    """Interface for knowledge triplet extraction"""
    
    @abstractmethod
    async def extract_triplets(self, sentences: List[str]) -> List[Tuple[str, str, str]]:
        """
        Extract knowledge triplets from sentences
        
        Args:
            sentences: List of simplified sentences
            
        Returns:
            List of triplets as (subject, relation, object) tuples
        """
        pass
