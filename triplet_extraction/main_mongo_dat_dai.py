from tqdm import tqdm
import phonlp
import time

from triplet_extraction.src.db import *
from triplet_extraction.src.triplet_extraction import *


def main():
    # === Setup working directory ===
    current_dir = os.getcwd()
    base_dir = os.path.dirname(current_dir)
    print(f"Working directory: {current_dir}")
    print(f"Base directory set to: {base_dir}\n")

    # === Define files paths relative to base directory ===
    vncorenlp_dir = os.path.join(current_dir, "nlp_models", "VnCoreNLP-1.2")
    phonlp_dir = os.path.join(current_dir, "nlp_models", "phonlp")
    synonym_file = os.path.join(current_dir, "listSameKey.txt")
    stopwords_file = os.path.join(current_dir, "stopwords.csv")
    no_triplet_csv_path = os.path.join(current_dir, "logs", "no_triplets_dat_dai_log_1.csv")
    log_file_path = os.path.join(current_dir, "logs", "dat_dai_triplet_extraction.txt")

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
    csv_writer.writerow(["section_id", "document_number", "sentence"])

    # === Setup logger ===
    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logger, console_handler, file_handler = setup_logger(
        name="triplet_extraction",
        level=logging.DEBUG,
        log_to_file=True,
        file_path=log_file_path
    )

    # Disable console logging (optional)
    logger.removeHandler(console_handler)

    logger.info("Starting triplet extraction...")
    logger.debug("Debug mode enabled")

    # Progress tracking variables
    total_processed = 0
    total_triplets_inserted = 0
    total_no_triplets = 0
    total_errors = 0
    start_time = time.time()

    try:
        reprocess_no_triplet = False
        if not reprocess_no_triplet:
            print("Đang xóa cơ sở dữ liệu cũ...")
            delete_all_mongo(db)
            print("Đang tạo indexes...")
            create_indexes(db)
            print("Bắt đầu trích xuất từ MongoDB...")
            rows_cursor = extract_all_from_mongo_collection(db["processed_legal_sections"])
            total_count = db["processed_legal_sections"].count_documents({})
            print(f"Tìm thấy {total_count} hàng để xử lý.\n")
            rows_iterator = tqdm(rows_cursor, desc="Đang xử lý văn bản", unit="văn bản", total=total_count)
        else:
            print("Đang đọc các câu chưa có triplet từ CSV...")
            rows = []
            prev_csv_path = os.path.join(base_dir, "graph", "logs", "no_triplets_dat_dai_log_1.csv")
            with open(prev_csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append({
                        "section_id": row["section_id"],
                        "so_hieu": row["document_number"],
                        "content": row["sentence"]
                    })
            print(f"Tìm thấy {len(rows)} hàng để xử lý.\n")
            rows_iterator = tqdm(rows, desc="Đang xử lý văn bản", unit="văn bản")

        for i, row in enumerate(rows_iterator, 1):
            sentence = row['content']
            if not sentence or not sentence.strip():
                continue

            doc_metadata = {
                'document_number': row.get('so_hieu', 'UNKNOWN'),
                'section_id': str(row.get('section_id', row.get('_id', 'UNKNOWN')))
            }

            try:
                triplets = triplet_extraction(
                    text=sentence,
                    vncorenlp_client=vncorenlp_client,
                    phoNLP_model=phoNLP_model,
                    stopwords=stopwords,
                    logger=logger,
                    max_depth=4,
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
                    csv_writer.writerow([doc_metadata['section_id'], doc_metadata['document_number'], sentence])

                total_processed += 1

            except Exception as e:
                total_errors += 1
                tqdm.write(f"Lỗi xử lý {doc_metadata['section_id']}: {e}")
                logger.error(f"Processing error for {doc_metadata['section_id']}: {e}")
                continue

    except Exception as e:
        print(f"\nLỗi nghiêm trọng: {e}")
        logger.critical(f"Critical error: {e}", exc_info=True)

    finally:
        # Print final summary
        elapsed_time = time.time() - start_time
        print(f"\n{'='*60}")
        print(f"TỔNG KẾT")
        print(f"{'='*60}")
        print(f"Tổng số xử lý:           {total_processed:,}")
        print(f"Tổng triplets chèn:      {total_triplets_inserted:,}")
        print(f"Không có triplet:        {total_no_triplets:,}")
        print(f"Lỗi:                     {total_errors:,}")
        print(f"Thời gian:               {elapsed_time/60:.2f} phút")
        print(f"Tốc độ TB:               {total_processed/elapsed_time if elapsed_time > 0 else 0:.2f} văn bản/giây")
        print(f"{'='*60}\n")
        
        if 'mongo_client' in locals():
            mongo_client.close()
        if 'no_triplet_file' in locals():
            no_triplet_file.close()
        print("Đã đóng tất cả kết nối. Hoàn thành.")


if __name__ == "__main__":
    main()