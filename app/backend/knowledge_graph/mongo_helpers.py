import os
from typing import Dict, Optional

import pymongo
from pymongo import MongoClient
from pymongo.server_api import ServerApi


def init_mongo(uri: Optional[str] = None):
    """Initialize a synchronous MongoDB client for legacy pipeline scripts."""
    mongo_uri = uri or os.getenv("KG_MONGO_URI") or os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MongoDB URI is not configured. Set KG_MONGO_URI or MONGO_URI.")

    client = MongoClient(mongo_uri, server_api=ServerApi("1"))
    client.admin.command("ping")
    return client


def get_or_create_concept(concepts_collection, name, section_id, document_number, synonym_dict=None):
    doc_ref = {"section_id": section_id, "so_hieu": document_number}

    synonyms = []
    if synonym_dict and "synonyms" in synonym_dict and name in synonym_dict["synonyms"]:
        synonyms = synonym_dict["synonyms"][name]

    result = concepts_collection.find_one_and_update(
        {"$or": [{"name": name}, {"synonym": name}]},
        {
            "$addToSet": {"documents": doc_ref},
            "$setOnInsert": {
                "name": name,
                "synonym": synonyms,
                "description": None,
            },
        },
        upsert=True,
        return_document=pymongo.ReturnDocument.AFTER,
    )
    return result["_id"]


def get_or_create_relation(relations_collection, name, section_id, document_number, synonym_dict=None):
    doc_ref = {"section_id": section_id, "so_hieu": document_number}

    synonyms = []
    if synonym_dict and "synonyms" in synonym_dict and name in synonym_dict["synonyms"]:
        synonyms = synonym_dict["synonyms"][name]

    result = relations_collection.find_one_and_update(
        {"$or": [{"name": name}, {"synonym": name}]},
        {
            "$addToSet": {"documents": doc_ref},
            "$setOnInsert": {
                "name": name,
                "synonym": synonyms,
                "description": None,
            },
        },
        upsert=True,
        return_document=pymongo.ReturnDocument.AFTER,
    )
    return result["_id"]


def insert_triplet_batch_mongo(db, triplets_list, metadata, synonym_dict=None):
    concepts_collection = db["concepts"]
    relations_collection = db["relations"]
    triplets_collection = db["triplets"]

    section_id = metadata["section_id"]
    document_number = metadata["so_hieu"]
    doc_ref = {"section_id": section_id, "so_hieu": document_number}

    triplets_inserted = 0

    for triplet in triplets_list:
        c1_name = triplet.get("c1")
        r_name = triplet.get("r")
        c2_name = triplet.get("c2")

        if not c1_name or not r_name or not c2_name:
            continue

        subject_id = get_or_create_concept(
            concepts_collection, c1_name, section_id, document_number, synonym_dict
        )
        relation_id = get_or_create_relation(
            relations_collection, r_name, section_id, document_number, synonym_dict
        )
        object_id = get_or_create_concept(
            concepts_collection, c2_name, section_id, document_number, synonym_dict
        )

        result = triplets_collection.update_one(
            {
                "subject_id": subject_id,
                "relation_id": relation_id,
                "object_id": object_id,
            },
            {
                "$addToSet": {"documents": doc_ref},
                "$setOnInsert": {
                    "subject_name": c1_name,
                    "relation_name": r_name,
                    "object_name": c2_name,
                },
            },
            upsert=True,
        )

        if result.upserted_id or result.modified_count > 0:
            triplets_inserted += 1

    return triplets_inserted


def extract_all_from_mongo_collection(collection):
    projection = {
        "section_id": 1,
        "sequence": 1,
        "so_hieu": 1,
        "content": 1,
    }
    return collection.find({}, projection).batch_size(100)


def build_tree_downward(sections_col, node_id: str, max_depth: int = 10) -> Dict:
    def get_node_with_children(current_id: str, depth: int = 0) -> Optional[Dict]:
        if not current_id or depth > max_depth:
            return None

        node = sections_col.find_one({"_id": current_id})
        if not node:
            return None

        tree_node = {
            "_id": node["_id"],
            "title": node.get("title", ""),
            "type": node.get("type", ""),
            "content": node.get("content", ""),
            "full_path": node.get("full_path", ""),
            "document_title": node.get("document_title", ""),
            "so_hieu": node.get("so_hieu", ""),
            "effective_date": node.get("effective_date", ""),
            "is_amendment": node.get("is_amendment", False),
            "is_phu_luc": node.get("is_phu_luc", False),
            "children": [],
        }

        for child in sections_col.find({"parent_id": current_id}):
            child_tree = get_node_with_children(child["_id"], depth + 1)
            if child_tree:
                tree_node["children"].append(child_tree)

        return tree_node

    return get_node_with_children(node_id)
