import hashlib
import re
from pathlib import Path

from bson import ObjectId


def convert_doc_to_docx(input_path, output_path=None):
    try:
        import win32com.client as win32
    except ImportError as exc:
        raise RuntimeError("DOC to DOCX conversion requires win32com on Windows") from exc

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

def strip_markdown_formatting(text):
    """
    Strip markdown formatting from text without changing content.
    Removes markdown syntax but preserves the actual text content.
    """
    if not text:
        return text

    # Remove bold/italic markers (**text**, *text*, __text__, _text_)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'__([^_]+)__', r'\1', text)  # __bold__
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # *italic*
    text = re.sub(r'_([^_]+)_', r'\1', text)  # _italic_

    # Remove headers (# Header) but keep the text
    text = re.sub(r'^#{1,6}\s+(.+)$', r'\1', text, flags=re.MULTILINE)

    # Remove links [text](url) but keep the text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)

    # Remove inline code markers `code`
    text = re.sub(r'`([^`]+)`', r'\1', text)

    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r'^[\*\-_]{3,}$', '', text, flags=re.MULTILINE)

    # Remove blockquote markers (> text)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)

    # Remove list markers (-, *, +, 1.) but preserve indent structure
    text = re.sub(r'^[\s]*[-\*\+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+(?![^\s])', '', text, flags=re.MULTILINE)

    return text
