from typing import Set

from knowledge_graph.mongo_helpers import build_tree_downward, init_mongo
from knowledge_graph.triplet_extraction.graph_update.amendment_detection import (
    add_amendment_ref_to_nodes,
    resolve_full_path,
)


def main():
    mongo = init_mongo()
    db = mongo["KB_PROPERTY_LAW"]

    documents_col = db["documents"]
    sections_col = db["legal_sections"]
    section_relations_col = db["legal_section_relations"]
    section_relations_col.delete_many({})

    amendment_articles = sections_col.find({
        "is_amendment": True,
        "type": "điều"
    })

    count = 0
    all_leaves = []
    seen_global_paths: Set[str] = set()
    not_found_log = []
    skipped_log = []
    relations_created = 0

    for article in amendment_articles:
        count += 1

        print(f"Processing: {article['full_path']}")
        downward_tree = build_tree_downward(sections_col, article["_id"])
        leaf_nodes = add_amendment_ref_to_nodes(downward_tree, documents_col)

        for leaf in leaf_nodes:
            full_path = leaf.get('full_path')
            if full_path and full_path not in seen_global_paths:
                all_leaves.append(leaf)
                seen_global_paths.add(full_path)

        print(f"Found {len(leaf_nodes)} unique leaf nodes in this article")
        print("\n")

    # Process each leaf and create relations
    for leaf in all_leaves:
        source_path = leaf['full_path']
        # Handle pseudo-nodes with #ref suffix
        if '#ref' in source_path:
            source_path = source_path.split('#ref')[0]
        
        ref = leaf.get('ref', {})
        
        if not ref or not ref.get('so_hieu') or not ref.get('dieu'):
            skipped_entry = f"{source_path} -> {ref} (missing so_hieu or dieu)"
            skipped_log.append(skipped_entry)
            print(f"→ Skipped incomplete ref: {skipped_entry}")
            continue
        
        # Check if document exists
        so_hieu = ref.get('so_hieu')
        doc = documents_col.find_one({"so_hieu": so_hieu})
        
        if not doc:
            not_found_entry = {
                "source": source_path,
                "ref": ref,
                "reason": "document_not_found",
                "so_hieu": so_hieu
            }
            not_found_log.append(not_found_entry)
            print(f"✗ Document not found: {so_hieu}")
            continue
        
        # Try to resolve the target section
        target_node = resolve_full_path(sections_col, ref)
        
        if target_node:
            # Create relation
            relation = {
                "source": source_path,
                "target": target_node['full_path'],
                "type": "AMENDS",
                "amendment_types": ref.get('amendment_type', [])
            }
            
            # Insert or update relation
            section_relations_col.update_one(
                {"source": source_path, "target": target_node['full_path'], "type": "AMENDS"},
                {"$set": relation},
                upsert=True
            )
            relations_created += 1
            print(f"✓ Created relation: {source_path} -> {target_node['full_path']}")
        else:
            # Document exists but section not found - check what level failed
            dieu = ref.get('dieu')
            khoan = ref.get('khoan')
            diem = ref.get('diem')
            
            # Build incomplete path
            incomplete_path = f"{doc['so_hieu']}"
            
            # Check if article exists
            article_query = {
                "document_id": doc['_id'],
                "type": "điều",
                "number": dieu
            }
            article = sections_col.find_one(article_query)
            
            if not article:
                reason = "article_not_found"
                details = f"điều {dieu}"
                incomplete_path += f" > điều {dieu}"
            elif khoan:
                incomplete_path = article['full_path']
                # Check if khoan exists
                khoan_query = {
                    "document_id": doc['_id'],
                    "parent_id": article['_id'],
                    "type": "khoản",
                    "number": khoan
                }
                khoan_node = sections_col.find_one(khoan_query)
                if not khoan_node:
                    reason = "khoan_not_found"
                    details = f"điều {dieu}, khoản {khoan}"
                    incomplete_path += f" > khoản {khoan}"
                else:
                    # Khoan exists but deeper level missing
                    incomplete_path = khoan_node['full_path']
                    reason = "section_not_resolved"
                    details = f"khoản {khoan} exists but child section not found"
            elif diem:
                incomplete_path = article['full_path']
                # Check if diem exists
                diem_query = {
                    "document_id": doc['_id'],
                    "parent_id": article['_id'],
                    "type": "điểm",
                    "number": diem
                }
                diem_node = sections_col.find_one(diem_query)
                if not diem_node:
                    reason = "diem_not_found"
                    details = f"điều {dieu}, điểm {diem}"
                    incomplete_path += f" > điểm {diem}"
                else:
                    # Diem exists but deeper level missing
                    incomplete_path = diem_node['full_path']
                    reason = "section_not_resolved"
                    details = f"điểm {diem} exists but child section not found"
            else:
                reason = "section_not_resolved"
                details = f"điều {dieu}"
                incomplete_path = article['full_path'] if article else incomplete_path + f" > điều {dieu}"
            
            not_found_entry = {
                "source": source_path,
                "ref": ref,
                "reason": reason,
                "so_hieu": so_hieu,
                "details": details,
                "incomplete_path": incomplete_path
            }
            not_found_log.append(not_found_entry)
            print(f"✗ {reason}: {incomplete_path}")

    # Write not found log to file with categorization
    from collections import Counter
    reasons = Counter([entry['reason'] for entry in not_found_log])
    so_hieu_counts = Counter([entry['so_hieu'] for entry in not_found_log])
    
    with open("amendment_not_found.txt", "w", encoding="utf-8") as f:
        f.write(f"Amendment references not found in database\n")
        f.write(f"Total not found: {len(not_found_log)}\n")
        f.write("=" * 80 + "\n\n")
        
        f.write("BREAKDOWN BY REASON:\n")
        f.write("-" * 80 + "\n")
        for reason, count in reasons.most_common():
            f.write(f"{reason}: {count}\n")
        f.write("\n")
        
        f.write("TOP 20 MISSING DOCUMENTS (so_hieu):\n")
        f.write("-" * 80 + "\n")
        for so_hieu, count in so_hieu_counts.most_common(20):
            f.write(f"{so_hieu}: {count} references\n")
        f.write("\n")
        
        f.write("DETAILED ENTRIES:\n")
        f.write("=" * 80 + "\n\n")
        for entry in not_found_log:
            f.write(f"Source: {entry['source']}\n")
            f.write(f"Reason: {entry['reason']}\n")
            f.write(f"So hieu: {entry['so_hieu']}\n")
            f.write(f"Details: {entry.get('details', 'N/A')}\n")
            f.write(f"Incomplete path: {entry.get('incomplete_path', 'N/A')}\n")
            f.write(f"Full ref: {entry['ref']}\n")
            f.write("-" * 80 + "\n")

    # Write skipped log to file
    with open("amendment_skipped.txt", "w", encoding="utf-8") as f:
        f.write(f"Amendment references skipped (incomplete ref data)\n")
        f.write(f"Total skipped: {len(skipped_log)}\n")
        f.write("=" * 80 + "\n\n")
        for entry in skipped_log:
            f.write(entry + "\n")

    from collections import Counter
    reasons = Counter([entry['reason'] for entry in not_found_log])
    
    print(f"\nSummary:")
    print(f"Total amendment articles processed: {count}")
    print(f"Total unique leaf nodes found: {len(all_leaves)}")
    print(f"Relations created: {relations_created}")
    print(f"References not found: {len(not_found_log)}")
    print(f"  - Breakdown by reason:")
    for reason, cnt in reasons.most_common():
        print(f"    • {reason}: {cnt}")
    print(f"References skipped (incomplete): {len(skipped_log)}")
    print(f"\nNot found log written to: amendment_not_found.txt")
    print(f"Skipped log written to: amendment_skipped.txt")

if __name__ == "__main__":
    main()
