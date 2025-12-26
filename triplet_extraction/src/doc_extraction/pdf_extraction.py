import pdfplumber
from llama_cloud_services import LlamaParse

def extract_pdf_text(pdf_path):
    """Extract text directly from PDF using pdfplumber."""
    full_text = []
    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text(x_tolerance=2, y_tolerance=3)
            if text:
                lines = [l.strip() for l in text.splitlines() if l.strip()]
                full_text.append("\n".join(lines))

    return "\n\n".join(full_text) if full_text else ""


def extract_pdf_images(api_key, pdf_path):
    """Extract text from PDF using OCR via LlamaParse."""
    parser = LlamaParse(
        api_key=api_key,
        num_workers=2,
        verbose=True,
        language="vi",
    )
    result = parser.parse(pdf_path)
    text_documents = result.get_markdown_documents(split_by_page=False)
    output_text = ""
    for doc in text_documents:
        output_text += doc.text + "\n"
    return output_text


def extract_text_from_pdf(api_key, pdf_path, force_ocr=False):
    if force_ocr:
        # Always use OCR when forced
        return extract_pdf_images(api_key, pdf_path)

    # Try extracting text directly first
    text = extract_pdf_text(pdf_path)

    if text.strip():
        return text
    else:
        # No text found, fall back to OCR
        return extract_pdf_images(api_key, pdf_path)