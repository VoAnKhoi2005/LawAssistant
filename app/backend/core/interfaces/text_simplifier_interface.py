from abc import ABC, abstractmethod
from typing import List


class ITextSimplifier(ABC):
    """Interface for text simplification using LLM"""
    
    @abstractmethod
    async def simplify_text(self, text: str) -> List[str]:
        """
        Simplify complex legal text into simple sentences
        
        Args:
            text: Complex legal text to simplify
            
        Returns:
            List of simplified sentences
        """
        pass
