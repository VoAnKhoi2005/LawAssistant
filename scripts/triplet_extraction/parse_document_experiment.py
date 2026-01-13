from pathlib import Path
import pandas as pd
from src.triplet_extraction.doc_extraction.parse_text_to_section import parse_document

TARGET_SO_HIEU = "10/2023/NĐ-CP"

def main():
    data_folder = Path(r"/src/triplet_extraction\data\luat_dat_dai")
    extracted_csv = data_folder / "extracted_texts_google.csv"
    df = pd.read_csv(extracted_csv, encoding='utf-8-sig')
    print(f"Loaded {len(df)} documents from CSV")

    row = df.loc[df["so_hieu"] == TARGET_SO_HIEU]

    if row.empty:
        print("Document not found")
    else:
        r = row.iloc[0]
        result = parse_document(r["combined_text"], r["so_hieu"])
        print(result)

if __name__ == "__main__":
    main()