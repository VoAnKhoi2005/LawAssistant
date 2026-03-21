from typing import List
from pathlib import Path
from core.interfaces.document_extractor_interface import IDocumentExtractor
from knowledge_graph.triplet_extraction.doc_extraction.google_pdf_extraction import extract_text_from_pdf_google_vision
from knowledge_graph.triplet_extraction.doc_extraction.ms_word_extraction import extract_text_from_docx
from knowledge_graph.triplet_extraction.doc_extraction.utils import convert_doc_to_docx, strip_markdown_formatting
import tempfile


class GoogleCloudDocumentExtractor(IDocumentExtractor):
    """Google Cloud Vision-based document extractor"""
    
    def __init__(self, credential_file: str, bucket_name: str):
        self.credential_file = credential_file
        self.bucket_name = bucket_name
    
    async def extract_text(self, file_paths: List[str]) -> str:
        """Extract text using Google Cloud Vision for PDFs and python-docx for Word docs"""
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
                elif file_path.suffix.lower() == ".pdf":
                    text = extract_text_from_pdf_google_vision(
                        credential_file=self.credential_file,
                        bucket_name=self.bucket_name,
                        gcs_path=f"pdfs/{file_path.name}",
                        output_path=f"ocr-output/{file_path.stem}/",
                        pdf_path=str(file_path)
                    )
                
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
        """Supports PDF, DOC, and DOCX formats"""
        return file_extension.lower() in [".pdf", ".doc", ".docx"]
