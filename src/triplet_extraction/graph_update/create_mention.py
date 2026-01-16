from typing import Set, Dict, Any, Optional
from src.db import init_mongo
from src.triplet_extraction.graph_update.amendment_detection import resolve_full_path, parse_amendment_reference


def get_section_so_hieu(sections_col, section_id) -> Optional[str]:
    """Get the so_hieu of the document that contains this section."""
    section = sections_col.find_one({"_id": section_id})
    if not section:
        return None
    
    document_id = section.get("document_id")
    if not document_id:
        return None
    
    # Get document from sections that have document info
    doc_section = sections_col.find_one({"_id": document_id})
    return doc_section.get("so_hieu") if doc_section else None


def resolve_mention_reference(sections_col, documents_col, ref: Dict[str, Any], current_section_id) -> Optional[Dict[str, Any]]:
    """
    Resolve a mention reference, assuming same so_hieu as current section if not specified.
    Only creates relation if we have enough hierarchy info (at least điều level).
    """
    # If so_hieu is not in ref, get it from the current section
    so_hieu = ref.get('so_hieu')
    if not so_hieu:
        so_hieu = get_section_so_hieu(sections_col, current_section_id)
        if not so_hieu:
            return None
        # Add so_hieu to ref for resolution
        ref = {**ref, 'so_hieu': so_hieu}
    
    # Check minimum requirement: must have điều (article)
    if not ref.get('dieu'):
        return None
    
    # Verify document exists
    doc = documents_col.find_one({"so_hieu": so_hieu})
    if not doc:
        return None
    
    # Try to resolve the full path
    target_node = resolve_full_path(sections_col, ref)
    return target_node


def main():
    mongo = init_mongo()
    db = mongo["KB_PROPERTY_LAW"]

    documents_col = db["documents"]
    sections_col = db["legal_sections"]
    section_relations_col = db["legal_section_relations"]
    
    # Find all non-amendment sections that are at least điều level or deeper
    # We want sections that can contain references (điều, khoản, điểm)
    non_amendment_sections = sections_col.find({
        "$or": [
            {"is_amendment": {"$ne": True}},
            {"is_amendment": {"$exists": False}}
        ],
        "type": {"$in": ["điều", "khoản", "điểm"]}
    })

    count = 0
    skipped_log = []
    relations_created = 0
    
    print("Processing non-amendment sections for mentions...")

    # Process each section and create relations
    for section in non_amendment_sections:
        source_path = section['full_path']
        # Handle pseudo-nodes with #ref suffix
        if '#ref' in source_path:
            source_path = source_path.split('#ref')[0]
        
        ref = parse_amendment_reference(section['content'], documents_col)
        section_id = section.get('_section_id')
        
        if not ref:
            continue

        if ref.get('so_hieu') is None and section.get('so_hieu'):
            ref['so_hieu'] = section['so_hieu']
        
        # Try to resolve the mention reference
        target_node = resolve_mention_reference(sections_col, documents_col, ref, section_id)
        
        if target_node:
            target_path = target_node['full_path']
            
            # Avoid self-references
            if source_path == target_path:
                continue
            
            # Create relation
            relation = {
                "source": source_path,
                "target": target_path,
                "type": "MENTIONS",
                "ref_details": {
                    k: v for k, v in ref.items() 
                    if k in ['so_hieu', 'phan', 'chuong', 'muc', 'tieu_muc', 'dieu', 'khoan', 'diem', 'phu_luc']
                }
            }
            
            # Insert or update relation
            section_relations_col.update_one(
                {"source": source_path, "target": target_path, "type": "MENTIONS"},
                {"$set": relation},
                upsert=True
            )
            relations_created += 1
            
            if relations_created % 100 == 0:
                print(f"Created {relations_created} relations...")
        else:
            # Log references that couldn't be resolved
            skipped_entry = {
                "source": source_path,
                "ref": ref,
                "reason": "could_not_resolve" if ref.get('dieu') else "insufficient_hierarchy"
            }
            skipped_log.append(skipped_entry)

    # Write logs
    with open("mention_skipped.txt", "w", encoding="utf-8") as f:
        f.write(f"Mention references skipped or not found\n")
        f.write(f"Total skipped: {len(skipped_log)}\n")
        f.write("=" * 80 + "\n\n")
        
        # Categorize by reason
        from collections import Counter
        reasons = Counter([entry['reason'] for entry in skipped_log])
        
        f.write("BREAKDOWN BY REASON:\n")
        f.write("-" * 80 + "\n")
        for reason, cnt in reasons.most_common():
            f.write(f"{reason}: {cnt}\n")
        f.write("\n")
        
        f.write("DETAILED ENTRIES:\n")
        f.write("=" * 80 + "\n\n")
        for entry in skipped_log:
            f.write(f"Source: {entry['source']}\n")
            f.write(f"Reason: {entry['reason']}\n")
            f.write(f"Ref: {entry['ref']}\n")
            f.write("-" * 80 + "\n")

    print(f"\nSummary:")
    print(f"Total non-amendment sections processed: {count}")
    print(f"Mention relations created: {relations_created}")
    print(f"References skipped: {len(skipped_log)}")
    if skipped_log:
        from collections import Counter
        reasons = Counter([entry['reason'] for entry in skipped_log])
        print(f"  - Breakdown by reason:")
        for reason, cnt in reasons.most_common():
            print(f"    • {reason}: {cnt}")
    print(f"\nSkipped log written to: mention_skipped.txt")


if __name__ == "__main__":
    main()
