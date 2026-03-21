from abc import ABC, abstractmethod
from typing import List
from pathlib import Path


class IDocumentExtractor(ABC):
    """Interface for document text extraction"""
    
    @abstractmethod
    async def extract_text(self, file_paths: List[str]) -> str:
        """
        Extract text from document files
        
        Args:
            file_paths: List of file paths to extract text from
            
        Returns:
            Combined extracted text
        """
        pass
    
    @abstractmethod
    def supports_format(self, file_extension: str) -> bool:
        """
        Check if this extractor supports the given file format
        
        Args:
            file_extension: File extension (e.g., '.pdf', '.docx')
            
        Returns:
            True if supported, False otherwise
        """
        pass
