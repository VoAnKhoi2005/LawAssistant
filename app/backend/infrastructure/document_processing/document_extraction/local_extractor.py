from typing import List
from pathlib import Path
from core.interfaces.document_extractor_interface import IDocumentExtractor
from knowledge_graph.triplet_extraction.doc_extraction.ms_word_extraction import extract_text_from_docx
from knowledge_graph.triplet_extraction.doc_extraction.utils import convert_doc_to_docx, strip_markdown_formatting
import tempfile


class LocalDocumentExtractor(IDocumentExtractor):
    """Local document extractor (only Word docs, no cloud OCR)"""
    
    async def extract_text(self, file_paths: List[str]) -> str:
        """Extract text from local Word documents only"""
        combined_text = ""
        
        for file_path_str in file_paths:
            file_path = Path(file_path_str)
            
            if not file_path.exists():
                continue
                
            if not self.supports_format(file_path.suffix.lower()):
                continue
            
            text = ""
            
            # Convert .doc to .docx if needed
            if file_path.suffix.lower() == ".doc":
                temp_conversion_folder = Path(tempfile.mkdtemp(prefix="doc_conversion_"))
                file_path = convert_doc_to_docx(file_path, temp_conversion_folder)
            
            try:
                if file_path.suffix.lower() == ".docx":
                    text = "\n".join(extract_text_from_docx(file_path))
                
                if text:
                    combined_text += text + "\n"
                    
            except Exception as e:
                print(f"Error extracting text from {file_path.name}: {str(e)}")
                continue
        
        # Strip markdown formatting
        if combined_text:
            combined_text = strip_markdown_formatting(combined_text)
        
        return combined_text
    
    def supports_format(self, file_extension: str) -> bool:
        """Supports only DOC and DOCX formats"""
        return file_extension.lower() in [".doc", ".docx"]
