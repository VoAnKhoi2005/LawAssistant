import hashlib
import os
import re
from pathlib import Path

import win32com.client as win32

def convert_doc_to_docx(input_path, output_path=None):
    input_path = Path(input_path)

    word = win32.Dispatch("Word.Application")
    word.Visible = False

    doc = word.Documents.Open(str(input_path.resolve()))

    # Nếu output_path là THƯ MỤC → tạo filename
    if output_path is None:
        output_file = input_path.with_suffix(".docx")
    else:
        output_path = Path(output_path)
        if output_path.is_dir():
            output_file = output_path / input_path.with_suffix(".docx").name
        else:
            output_file = output_path

    doc.SaveAs(str(output_file), FileFormat=16)  # wdFormatXMLDocument
    doc.Close(False)
    word.Quit()

    return output_file

def clean_title(raw: str) -> str:
    # Remove quotes
    text = raw.replace('"', '')

    # Replace newlines & multiple spaces
    text = re.sub(r'\s+', ' ', text).strip()

    # Normalize uppercase -> title case (Vietnamese friendly)
    text = text.lower().capitalize()

    return text

def clean_content(text):
    """Remove extra whitespace from content."""
    if text:
        return " ".join(text.split())
    return None

def generate_id(full_path_title):
    """Generate unique ID from full path title using SHA256."""
    return hashlib.sha256(full_path_title.encode('utf-8')).hexdigest()