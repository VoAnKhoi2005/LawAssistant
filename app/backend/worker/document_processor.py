import time


def process_document_pipeline(document_id, file_path, metadata, progress_callback=None):
    def update(step, progress):
        if progress_callback:
            progress_callback(step, progress)

    # Step 1
    update("Extracting text from document", 10)
    text = extract_text(file_path)

    # Step 2
    update("Simplifying legal sentences", 40)
    simplified = simplify_text(text)

    # Step 3
    update("Extracting knowledge triplets", 80)
    triplets = extract_triplets(simplified)

    return {
        "processed_sentences": len(simplified),
        "extracted_triplets": len(triplets),
        "processing_time": 10.0
    }


def extract_text(file_path: str):
    time.sleep(3)  # replace with real logic
    return "text"


def simplify_text(text: str):
    time.sleep(4)
    return ["sentence1", "sentence2"]


def extract_triplets(sentences):
    time.sleep(3)
    return [("A", "rel", "B")]