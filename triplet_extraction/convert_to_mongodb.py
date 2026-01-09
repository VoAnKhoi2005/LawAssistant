from dotenv import load_dotenv
import os
from triplet_extraction.src.db import init_mongo
from triplet_extraction.src.doc_extraction.parse_text_to_section import parse_document
from triplet_extraction.src.doc_extraction.utils import clean_title, strip_markdown_formatting
import pandas as pd
from pathlib import Path

def main():
    load_dotenv()
    uri = os.getenv("MONGODB_URI")
    mongo_client = init_mongo()
    if not mongo_client:
        db = None
        print("Failed to connect to MongoDB. Exiting.")
    else:
        db = mongo_client["KB_PROPERTY_LAW"]
    # Get the collection
    sections_collection = db["legal_sections"]
    data_folder = Path(r"E:\Github\LawAssistant\triplet_extraction\data\luat_dat_dai")

    # Create indexes for better query performance
    # Note: _id is automatically unique, so we don't need to create that index
    try:
        # Drop old full_path unique index if it exists
        sections_collection.drop_index("full_path_1")
        print("Dropped old full_path unique index")
    except Exception:
        pass  # Index doesn't exist, which is fine
    
    sections_collection.create_index("so_hieu")
    sections_collection.create_index("parent_id")
    sections_collection.create_index("full_path")

    # Read the extracted texts CSV
    extracted_csv = data_folder / "extracted_texts_google.csv"
    df = pd.read_csv(extracted_csv, encoding='utf-8-sig')

    print(f"Loaded {len(df)} documents from CSV")

    total_inserted = 0
    total_updated = 0
    total_skipped = 0

    for idx, row in df.iterrows():
        so_hieu = row["so_hieu"]
        title = row["title"]
        effective_date = row["effective_date"]
        source_files = row["source_files"]
        combined_text = row["combined_text"]
        
        # Strip markdown formatting if present
        combined_text = strip_markdown_formatting(combined_text)

        # Check if document already exists in database
        existing_count = sections_collection.count_documents({"so_hieu": so_hieu})
        if existing_count > 0:
            print(f"\n{'=' * 60}")
            print(f"[{idx + 1}/{len(df)}] SKIPPING: {so_hieu} - {title}")
            print(f"Already in database with {existing_count} sections")
            print(f"{'=' * 60}")
            total_skipped += 1
            continue

        print(f"\n{'=' * 60}")
        print(f"[{idx + 1}/{len(df)}] Processing: {so_hieu} - {title}")
        print(f"Text length: {len(combined_text):,} characters")
        print(f"{'=' * 60}")

        try:
            # Parse the combined document
            result = parse_document(combined_text, so_hieu)

            if not result:
                print(f"Warning: No sections parsed from text")
                continue

            print(f"✓ Parsed {len(result)} sections")

            # Insert or update each section in MongoDB
            inserted_count = 0
            updated_count = 0

            for section_id, section_data in result.items():
                # Add metadata
                section_data["document_title"] = clean_title(title)
                section_data["effective_date"] = effective_date
                section_data["source_file"] = source_files
                section_data["_id"] = section_id

                # Use upsert to insert or update based on _id (custom string)
                update_result = sections_collection.update_one(
                    {"_id": section_id},
                    {
                        "$set": section_data,
                    },
                    upsert=True
                )

                if update_result.upserted_id:
                    inserted_count += 1
                elif update_result.modified_count > 0:
                    updated_count += 1

            print(f"✓ Inserted: {inserted_count} sections")
            print(f"✓ Updated: {updated_count} sections")

            total_inserted += inserted_count
            total_updated += updated_count

        except Exception as e:
            print(f"Error parsing document: {str(e)}")
            import traceback
            traceback.print_exc()

    print(f"\n{'=' * 60}")
    print(f"PARSING COMPLETE")
    print(f"{'=' * 60}")
    print(f"Documents skipped (already in DB): {total_skipped}")
    print(f"Total sections inserted: {total_inserted}")
    print(f"Total sections updated: {total_updated}")
    print(f"Total sections processed: {total_inserted + total_updated}")
    print(f"{'=' * 60}")

if __name__ == "__main__":
    main()