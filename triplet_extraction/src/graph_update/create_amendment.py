from triplet_extraction.src.db import build_tree_downward, init_mongo
from triplet_extraction.src.graph_update.amendment_detection import add_amendment_ref_to_nodes


def main():
    mongo = init_mongo()
    db = mongo["KB_PROPERTY_LAW"]

    documents_col = db["documents"]
    sections_col = db["legal_sections"]
    section_relations_col = db["legal_section_relations"]

    amendment_articles = sections_col.find({
        "is_amendment": True,
        "type": "điều"
    })

    count = 0

    for article in amendment_articles:
        count += 1

        print("\n" + "=" * 80)
        print(f"Processing: {article['full_path']}")
        print("=" * 80)

        downward_tree = build_tree_downward(sections_col, article["_id"])
        add_amendment_ref_to_nodes(downward_tree, documents_col)
        # print_tree_with_ref(downward_tree, None, 0, show_content=False)
        print("\n")

    print(f"Total amendment articles processed: {count}")

if __name__ == "__main__":
    main()