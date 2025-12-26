from docx import Document
from docx.table import Table
from docx.oxml.table import CT_Tbl
from docx.oxml.text.paragraph import CT_P
from docx.text.paragraph import Paragraph

def extract_text_from_docx(docx_path):
    """Extract text from DOCX file, preserving document structure."""
    doc = Document(docx_path)
    output_text = []
    for child in doc.element.body.iterchildren():
        if isinstance(child, CT_P):
            para = Paragraph(child, doc)
            text = para.text.strip()
            if text:
                output_text.append(text)
        elif isinstance(child, CT_Tbl):
            table = Table(child, doc)
            for row in table.rows:
                for cell in row.cells:
                    text = cell.text.strip()
                    if text:
                        output_text.append(text)

    return output_text