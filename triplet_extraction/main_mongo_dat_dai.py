from tqdm import tqdm
import phonlp

from triplet_extraction.src.db import *
from triplet_extraction.src.triplet_extraction import *


def main():
    # === Setup working directory ===
    current_dir = os.getcwd()
    base_dir = os.path.dirname(current_dir)
    print(f"Working directory: {current_dir}")
    print(f"Base directory set to: {base_dir}\n")

    # === Define files paths relative to base directory ===
    vncorenlp_dir = os.path.join(base_dir, "nlp_models", "VnCoreNLP-1.2")
    phonlp_dir = os.path.join(base_dir, "nlp_models", "phonlp")
    synonym_file = os.path.join(base_dir, "listSameKey.txt")
    stopwords_file = os.path.join(base_dir, "stopwords.csv")
    no_triplet_csv_path = os.path.join(base_dir, "logs", "no_triplets_dat_dai_log_1.csv")
    log_file_path = os.path.join(base_dir, "logs", "dat_dai_triplet_extraction.txt")

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

    try:
        reprocess_no_triplet = False
        if not reprocess_no_triplet:
            print("Đang xóa cơ sở dữ liệu cũ...")
            delete_all_mongo(db)
            print("Đang tạo indexes...")
            create_indexes(db)
            print("Bắt đầu trích xuất từ SQLite...")
            rows = extract_all_from_mongo_collection(db["processed_legal_sections"])
        else:
            print("Đang đọc các câu chưa có triplet từ CSV...")
            rows = []
            prev_csv_path = os.path.join(base_dir, "graph", "logs", "no_triplets_dat_dai_log_1.csv")
            with open(prev_csv_path, "r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    rows.append({
                        "id": row["section_id"],
                        "so_hieu": row["document_number"],
                        "content": row["sentence"]
                    })

        print(f"Tìm thấy {len(rows)} hàng để xử lý.\n")
        for i, row in enumerate(tqdm(rows, desc="Đang xử lý văn bản", unit="văn bản")):
            sentence = row['content']
            if not sentence or not sentence.strip():
                continue

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

            doc_metadata = {
                'document_number': row.get('so_hieu', 'UNKNOWN'),
                'section_id': str(row.get('section_id', 'UNKNOWN'))
            }

            if triplets_list or len(triplets_list) > 0:
                try:
                    count = insert_triplet_batch_mongo(
                        db,
                        triplets_list=triplets_list,
                        metadata=doc_metadata,
                        synonym_dict=synonym_dict,
                    )
                    tqdm.write(f"[{i + 1}/{len(rows)}] Đã chèn {count} triplets cho {doc_metadata['section_id']}")
                except Exception as e:
                    tqdm.write(f"Lỗi khi chèn batch cho {doc_metadata['section_id']}: {e}")
            else:
                csv_writer.writerow([doc_metadata['section_id'], doc_metadata['document_number'], sentence])

    except Exception as e:
        print(f"Lỗi nghiêm trọng trong quá trình main: {e}")

    finally:
        if 'mongo_client' in locals():
            mongo_client.close()
        if 'no_triplet_file' in locals():
            no_triplet_file.close()
        print("\nĐã đóng tất cả kết nối. Hoàn thành.")


if __name__ == "__main__":
    main()