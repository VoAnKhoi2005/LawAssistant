import hashlib
import os
import win32com.client as win32

def convert_doc_to_docx(input_path, output_path=None):
    word = win32.gencache.EnsureDispatch("Word.Application")
    doc = word.Documents.Open((os.path.abspath(input_path)))

    if output_path is None:
        output_path = os.path.splitext(input_path)[0] + ".docx"

    doc.SaveAs(output_path, FileFormat=16)  # 16 = wdFormatXMLDocument (.docx)
    doc.Close()
    word.Quit()

    return output_path

def clean_content(text):
    """Remove extra whitespace from content."""
    if text:
        return " ".join(text.split())
    return None

def generate_id(full_path_title):
    """Generate unique ID from full path title using SHA256."""
    return hashlib.sha256(full_path_title.encode('utf-8')).hexdigest()