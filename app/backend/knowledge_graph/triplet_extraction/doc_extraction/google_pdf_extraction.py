import os

import pdfplumber
from google.cloud import storage


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

def async_detect_document(gcs_source_uri, gcs_destination_uri):
    import json
    import re
    from google.cloud import vision
    from google.cloud import storage

    storage_client = storage.Client()

    # Parse destination bucket/prefix
    match = re.match(r"gs://([^/]+)/(.+)", gcs_destination_uri)
    bucket_name = match.group(1)
    prefix = match.group(2)

    bucket = storage_client.bucket(bucket_name)

    # 🔍 CHECK IF OCR OUTPUT ALREADY EXISTS
    existing_blobs = [
        blob for blob in bucket.list_blobs(prefix=prefix)
        if blob.name.endswith(".json")
    ]

    if existing_blobs:
        print("OCR output already exists → loading from GCS")
    else:
        print("No OCR output found → running OCR")

        mime_type = "application/pdf"
        batch_size = 2

        vision_client = vision.ImageAnnotatorClient()

        feature = vision.Feature(
            type_=vision.Feature.Type.DOCUMENT_TEXT_DETECTION
        )

        input_config = vision.InputConfig(
            gcs_source=vision.GcsSource(uri=gcs_source_uri),
            mime_type=mime_type
        )

        output_config = vision.OutputConfig(
            gcs_destination=vision.GcsDestination(uri=gcs_destination_uri),
            batch_size=batch_size
        )

        request = vision.AsyncAnnotateFileRequest(
            features=[feature],
            input_config=input_config,
            output_config=output_config
        )

        operation = vision_client.async_batch_annotate_files(
            requests=[request]
        )

        operation.result(timeout=900)

        # Reload blobs after OCR
        existing_blobs = [
            blob for blob in bucket.list_blobs(prefix=prefix)
            if blob.name.endswith(".json")
        ]

    # SORT OUTPUT FILES BY PAGE NUMBER
    def start_page(blob_name):
        m = re.search(r"output-(\d+)-to-\d+\.json", blob_name)
        return int(m.group(1)) if m else 0

    existing_blobs.sort(key=lambda b: start_page(b.name))

    # READ ALL PAGES
    full_text = []
    page_count = 0

    for blob in existing_blobs:
        response = json.loads(blob.download_as_text())
        for page in response["responses"]:
            page_count += 1
            text = page.get("fullTextAnnotation", {}).get("text", "")
            if text.strip():
                full_text.append(text)

    print(f"Total pages loaded: {page_count}")

    return "\n".join(full_text)

def upload_to_gcs(local_path, bucket_name, gcs_path):
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    blob = bucket.blob(gcs_path)
    blob.upload_from_filename(local_path)
    return f"gs://{bucket_name}/{gcs_path}"

def extract_pdf_images_google_vision(bucket_name, gcs_path, output_path, pdf_path):
    result_path = upload_to_gcs(pdf_path, bucket_name, gcs_path)

    text = async_detect_document(
        result_path,
        f"gs://{bucket_name}/{output_path}"
    )

    return text


def extract_text_from_pdf_google_vision(credential_file, bucket_name, gcs_path, output_path, pdf_path, force_ocr=False):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credential_file
    if force_ocr:
        # Always use OCR when forced
        return extract_pdf_images_google_vision(bucket_name, gcs_path, output_path, pdf_path)

    # Try extracting text directly first
    text = extract_pdf_text(pdf_path)

    if text.strip():
        return text
    else:
        # No text found, fall back to OCR
        return extract_pdf_images_google_vision(bucket_name, gcs_path, output_path, pdf_path)
