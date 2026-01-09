from pprint import pprint
from triplet_extraction.src.doc_extraction.parse_text_to_section import parse_document
from pathlib import Path
import pandas as pd

def main():
    data_folder = Path(r"E:\Github\LawAssistant\triplet_extraction\data\luat_dat_dai")
    extracted_csv = data_folder / "extracted_texts_google_fixed.csv"

    df = pd.read_csv(extracted_csv, encoding="utf-8-sig")
    print(f"Loaded {len(df)} documents from CSV")

    TARGET_SO_HIEU = "103/2024/NĐ-CP"

    row = df.loc[df["so_hieu"] == TARGET_SO_HIEU]

    if row.empty:
        raise ValueError(f"Không tìm thấy văn bản có số hiệu {TARGET_SO_HIEU}")

    row = row.iloc[0]

    result = parse_document(
        row["combined_text"],
        row["so_hieu"]
    )

    print("Parsed successfully")
    pprint(result)

if __name__ == "__main__":
    main()