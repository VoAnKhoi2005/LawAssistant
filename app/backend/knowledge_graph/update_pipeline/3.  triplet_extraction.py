import csv
import logging
import os
import time

import phonlp
from bson import ObjectId
from tqdm import tqdm

from src.db import init_mongo, extract_all_from_mongo_collection, insert_triplet_batch_mongo

from knowledge_graph.triplet_extraction.pos_taging.my_vncorenlp import init_vncorenlp
from knowledge_graph.triplet_extraction.triplet_extraction import triplet_extraction
from knowledge_graph.triplet_extraction.utils import load_synonym_dict, load_stopwords, setup_logger

# TODO: Input needed information from step 1 and 2
so_hieu = ""

def main():
    current_dir = os.getcwd()
    base_dir = os.path.dirname(current_dir)
    print(f"Working directory: {current_dir}")
    print(f"Base directory set to: {base_dir}\n")

    # === Define files paths relative to base directory ===
    vncorenlp_dir = os.path.join(current_dir, "nlp_models", "VnCoreNLP-1.2")
    phonlp_dir = os.path.join(current_dir, "nlp_models", "phonlp")
    synonym_file = os.path.join(current_dir, "listSameKey.txt")
    stopwords_file = os.path.join(current_dir, "stopwords.csv")
    no_triplet_csv_path = os.path.join(current_dir, "logs", "no_triplets_dat_dai_log_10_01_2026.csv")
    log_file_path = os.path.join(current_dir, "logs", "dat_dai_triplet_extraction_10_01_2026.txt")

    # === Initialize MongoDB ===
    mongo_client = init_mongo()
    if not mongo_client:
        print("Failed to connect to MongoDB. Exiting.")
        return
    db = mongo_client["KB_PROPERTY_LAW"]

    # === Initialize NLP models ===
    vncorenlp_client = init_vncorenlp(vncorenlp_dir)
    phoNLP_model = phonlp.load(save_dir=phonlp_dir)

    synonym_dict = load_synonym_dict(synonym_file)
    stopwords = load_stopwords(stopwords_file)

    # === Prepare CSV for no-triplet logging ===
    os.makedirs(os.path.dirname(no_triplet_csv_path), exist_ok=True)
    no_triplet_file = open(no_triplet_csv_path, "w", newline="", encoding="utf-8")
    csv_writer = csv.writer(no_triplet_file)
    csv_writer.writerow(["section_id", "document_number", "sequence", "sentence"])

    # === Setup logger ===
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logger, console_handler, file_handler = setup_logger(
        name="triplet_extraction",
        level=logging.DEBUG,
        log_to_file=True,
        file_path=log_file_path
    )

    # Progress tracking variables
    total_processed = 0
    total_triplets_inserted = 0
    total_no_triplets = 0
    total_errors = 0
    start_time = time.time()

    print("Bắt đầu trích xuất từ MongoDB...")

    projection = {
        'section_id': 1,
        'sequence': 1,
        'so_hieu': 1,
        'content': 1
    }
    rows_cursor = db.processed_legal_sections.find({"so_hieu": so_hieu}, projection).batch_size(100)
    total_count = db["processed_legal_sections"].count_documents({})
    print(f"Tìm thấy {total_count} hàng để xử lý.\n")
    rows_iterator = tqdm(rows_cursor, desc="Đang xử lý văn bản", unit="văn bản", total=total_count)

    for i, row in enumerate(rows_iterator, 1):
        section_id = row["section_id"]
        sequence_number = row.get("sequence", 0)

        # Try to find section by ObjectId first, then by string ID
        try:
            section = db["legal_sections"].find_one({"_id": ObjectId(section_id)})
        except:
            section = db["legal_sections"].find_one({"_id": section_id})

        if not section:
            continue

        if section.get("is_amendment", False):
            continue

        sentence = row['content']
        if not sentence or not sentence.strip():
            continue

        doc_metadata = {
            'so_hieu': row.get('so_hieu', 'UNKNOWN'),
            'section_id': str(row.get('section_id', row.get('_id', 'UNKNOWN')))
        }

        try:
            logger.debug(f"Processing section_id: {section_id}, sequence {sequence_number}")
            triplets = triplet_extraction(
                text=sentence,
                vncorenlp_client=vncorenlp_client,
                phoNLP_model=phoNLP_model,
                stopwords=stopwords,
                logger=logger,
                max_depth=3,
            )

            triplets_list = [
                {"c1": c1, "r": r, "c2": c2}
                for (c1, r, c2) in triplets
                if c1 and r and c2
            ]

            if triplets_list:
                try:
                    count = insert_triplet_batch_mongo(
                        db,
                        triplets_list=triplets_list,
                        metadata=doc_metadata,
                        synonym_dict=synonym_dict,
                    )
                    logger.debug(f"Inserted {count} triplets for section_id: {section_id}, sequence {sequence_number}")
                    total_triplets_inserted += count

                    # Update progress bar description with stats
                    elapsed_time = time.time() - start_time
                    rate = total_processed / elapsed_time if elapsed_time > 0 else 0
                    rows_iterator.set_postfix({
                        'triplets': total_triplets_inserted,
                        'no_triplet': total_no_triplets,
                        'errors': total_errors,
                        'rate': f'{rate:.2f}/s'
                    })

                except Exception as e:
                    total_errors += 1
                    tqdm.write(f"Lỗi chèn {doc_metadata['section_id']}: {e}")
                    logger.error(f"Insert error for {doc_metadata['section_id']}: {e}")
            else:
                total_no_triplets += 1
                csv_writer.writerow([doc_metadata['section_id'], doc_metadata['so_hieu'], sequence_number, sentence])

            total_processed += 1

        except Exception as e:
            total_errors += 1
            tqdm.write(f"Lỗi xử lý {doc_metadata['section_id']}: {e}")
            logger.error(f"Processing error for {doc_metadata['section_id']}: {e}")
            continue