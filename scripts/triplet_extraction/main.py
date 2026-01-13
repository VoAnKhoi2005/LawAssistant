import json
from tqdm import tqdm

from src.db import *
from src.triplet_extraction.triplet_extraction import *


def main():
    conn, cursor = init_sqlite(r"/src/triplet_extraction\batch_preprocessing\GTVT_law.db")
    gpt_client = init_gpt()
    neo4j_session = init_neo4j(
        uri="neo4j://127.0.0.1:7687",
        username="neo4j",
        password="1234567890",
        db_name="small-ontology",
    )
    vncorenlp_client = init_vncorenlp(r"/src/triplet_extraction\VnCoreNLP-1.2")

    neo4j_session.execute_write(delete_all)
    batch_result_path = r"/src/triplet_extraction\batch_68f0720bbe3081908aa61019a6d518fe_output.jsonl"

    with open(batch_result_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    count = 0
    so_hieu_list = set()
    for line in tqdm(lines, desc="Processing batch results", unit="entry"):
        data = json.loads(line)
        if data.get("response", {}).get("status_code") != 200:
            continue

        content = data["response"]["body"]["choices"][0]["message"]["content"]
        ID = data["custom_id"]

        law_sentence = extract_from_sqlite(cursor, ID)
        so_hieu = law_sentence[0]["so_hieu"]
        so_hieu_list.add(so_hieu)
        if so_hieu.strip() != "36/2024/QH15":
            continue

        count += 1
        rewrite_sentence = content
        extract_triplet_and_store(rewrite_sentence, vncorenlp_client, neo4j_session, ID, so_hieu)

    print("All triplets extracted and stored successfully!")
    print("Processed {} triplets.".format(count))
    print(so_hieu_list)


if __name__ == "__main__":
    main()
