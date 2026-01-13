import os
from typing import Dict, Optional

import pymongo
from bson import ObjectId
from pymongo import MongoClient
from pymongo.server_api import ServerApi

def init_mongo(uri=None):
    """Initialize MongoDB connection"""
    if uri is None:
        uri = os.getenv("KG_MONGO_URI")

    client = MongoClient(uri, server_api=ServerApi('1'))
    try:
        client.admin.command('ping')
        print("You successfully connected to MongoDB!")
        return client
    except Exception as e:
        print(e)
        return None


def get_or_create_concept(concepts_collection, name, section_id, document_number, synonym_dict=None):
    """Get existing concept or create new one, adding document reference
    Also checks synonyms to find existing concepts"""

    doc_ref = {"section_id": section_id, "so_hieu": document_number}
    
    # Get synonyms list from synonym_dict if available
    synonyms = []
    if synonym_dict and 'synonyms' in synonym_dict and name in synonym_dict['synonyms']:
        synonyms = synonym_dict['synonyms'][name]

    # Use upsert with $setOnInsert to avoid race conditions and reduce DB calls
    result = concepts_collection.find_one_and_update(
        {"$or": [{"name": name}, {"synonym": name}]},
        {
            "$addToSet": {"documents": doc_ref},
            "$setOnInsert": {
                "name": name,
                "synonym": synonyms,
                "description": None
            }
        },
        upsert=True,
        return_document=pymongo.ReturnDocument.AFTER
    )
    
    return result["_id"]


def get_or_create_relation(relations_collection, name, section_id, document_number, synonym_dict=None):
    """Get existing relation or create new one, adding document reference
    Also checks synonyms to find existing relations"""

    doc_ref = {"section_id": section_id, "so_hieu": document_number}
    
    # Get synonyms list from synonym_dict if available
    synonyms = []
    if synonym_dict and 'synonyms' in synonym_dict and name in synonym_dict['synonyms']:
        synonyms = synonym_dict['synonyms'][name]

    # Use upsert with $setOnInsert to avoid race conditions and reduce DB calls
    result = relations_collection.find_one_and_update(
        {"$or": [{"name": name}, {"synonym": name}]},
        {
            "$addToSet": {"documents": doc_ref},
            "$setOnInsert": {
                "name": name,
                "synonym": synonyms,
                "description": None
            }
        },
        upsert=True,
        return_document=pymongo.ReturnDocument.AFTER
    )
    
    return result["_id"]


def insert_triplet_batch_mongo(db, triplets_list, metadata, synonym_dict=None):
    """Insert batch of triplets into MongoDB with concept/relation names
    
    This version checks for duplicate triplets and tracks multiple source sections.
    - If triplet exists, adds the section to documents array
    - If triplet is new, creates it with initial documents array
    """
    concepts_collection = db["concepts"]
    relations_collection = db["relations"]
    triplets_collection = db["triplets"]

    section_id = metadata['section_id']
    document_number = metadata['so_hieu']

    doc_ref = {"section_id": section_id, "so_hieu": document_number}
    
    triplets_inserted = 0

    for triplet in triplets_list:
        c1_name = triplet.get('c1')
        r_name = triplet.get('r')
        c2_name = triplet.get('c2')

        if not c1_name or not r_name or not c2_name:
            continue

        # Get or create concept and relation IDs
        subject_id = get_or_create_concept(concepts_collection, c1_name, section_id, document_number, synonym_dict)
        relation_id = get_or_create_relation(relations_collection, r_name, section_id, document_number, synonym_dict)
        object_id = get_or_create_concept(concepts_collection, c2_name, section_id, document_number, synonym_dict)

        # Use upsert to avoid duplicate triplets while tracking all source sections
        result = triplets_collection.update_one(
            {
                "subject_id": subject_id,
                "relation_id": relation_id,
                "object_id": object_id
            },
            {
                "$addToSet": {"documents": doc_ref},
                "$setOnInsert": {
                    "subject_name": c1_name,
                    "relation_name": r_name,
                    "object_name": c2_name
                }
            },
            upsert=True
        )
        
        if result.upserted_id or result.modified_count > 0:
            triplets_inserted += 1

    return triplets_inserted

def extract_all_from_mongo_collection(collection):
    """Returns a cursor that yields documents one at a time.
    Uses batch_size to prevent memory overflow."""
    projection = {
        'section_id': 1,
        'sequence': 1,
        'so_hieu': 1,
        'content': 1
    }
    return collection.find({}, projection).batch_size(100)

def delete_all_mongo(db):
    """Delete all documents from all collections"""
    db["concepts"].delete_many({})
    db["relations"].delete_many({})
    db["triplets"].delete_many({})


def create_indexes(db):
    """Create indexes for better query performance"""
    db["concepts"].create_index("name")
    db["concepts"].create_index("synonym")
    db["relations"].create_index("name")
    db["relations"].create_index("synonym")
    
    # Indexes for triplets collection with documents array
    db["triplets"].create_index([
        ("subject_id", 1),
        ("relation_id", 1),
        ("object_id", 1)
    ], unique=True)  # Ensure no duplicate triplets
    db["triplets"].create_index("documents.section_id")
    db["triplets"].create_index("documents.so_hieu")

def update_existing_triplets_with_names(db):
    """Update existing triplets to add names from concepts/relations"""
    concepts_collection = db["concepts"]
    relations_collection = db["relations"]
    triplets_collection = db["triplets"]

    triplets = triplets_collection.find({})

    bulk_updates = []

    for triplet in triplets:
        subject_id = triplet.get("subject_id")
        object_id = triplet.get("object_id")
        relation_id = triplet.get("relation_id")

        # Fetch names from concepts/relations
        subject_doc = concepts_collection.find_one({"_id": subject_id})
        object_doc = concepts_collection.find_one({"_id": object_id})
        relation_doc = relations_collection.find_one({"_id": relation_id})

        update_fields = {}
        if subject_doc:
            update_fields["subject_name"] = subject_doc["name"]
        if object_doc:
            update_fields["object_name"] = object_doc["name"]
        if relation_doc:
            update_fields["relation_name"] = relation_doc["name"]

        if update_fields:
            bulk_updates.append(
                pymongo.UpdateOne({"_id": triplet["_id"]}, {"$set": update_fields})
            )

    if bulk_updates:
        result = triplets_collection.bulk_write(bulk_updates)
        print(f"Updated {result.modified_count} triplets with names.")
    else:
        print("No triplets needed updating.")


def migrate_triplets_to_documents_array(db):
    """
    Migrate old triplets with single section_id/so_hieu to new format with documents array
    
    This function converts:
    {
        section_id: "123",
        so_hieu: "100/2019/ND-CP"
    }
    
    To:
    {
        documents: [
            {section_id: "123", so_hieu: "100/2019/ND-CP"}
        ]
    }
    """
    triplets_collection = db["triplets"]
    
    # Find triplets with old schema (has section_id field instead of documents array)
    old_triplets = list(triplets_collection.find({"section_id": {"$exists": True}}))
    
    if not old_triplets:
        print("No old-format triplets found. Migration not needed.")
        return
    
    print(f"Found {len(old_triplets)} old-format triplets to migrate...")
    
    bulk_updates = []
    
    for triplet in old_triplets:
        section_id = triplet.get("section_id")
        so_hieu = triplet.get("so_hieu")
        
        if section_id and so_hieu:
            doc_ref = {"section_id": section_id, "so_hieu": so_hieu}
            
            # Add to documents array and remove old fields
            bulk_updates.append(
                pymongo.UpdateOne(
                    {"_id": triplet["_id"]},
                    {
                        "$set": {"documents": [doc_ref]},
                        "$unset": {"section_id": "", "so_hieu": ""}
                    }
                )
            )
    
    if bulk_updates:
        result = triplets_collection.bulk_write(bulk_updates)
        print(f"Migrated {result.modified_count} triplets to new format.")
    else:
        print("No triplets needed migration.")


def merge_duplicate_triplets(db):
    """
    Find and merge duplicate triplets (same subject_id, relation_id, object_id)
    Combines their documents arrays and keeps only one triplet
    """
    triplets_collection = db["triplets"]
    
    # Aggregate to find duplicates
    pipeline = [
        {
            "$group": {
                "_id": {
                    "subject_id": "$subject_id",
                    "relation_id": "$relation_id",
                    "object_id": "$object_id"
                },
                "triplet_ids": {"$push": "$_id"},
                "all_documents": {"$push": "$documents"},
                "subject_name": {"$first": "$subject_name"},
                "relation_name": {"$first": "$relation_name"},
                "object_name": {"$first": "$object_name"},
                "count": {"$sum": 1}
            }
        },
        {
            "$match": {"count": {"$gt": 1}}
        }
    ]
    
    duplicates = list(triplets_collection.aggregate(pipeline))
    
    if not duplicates:
        print("No duplicate triplets found.")
        return
    
    print(f"Found {len(duplicates)} sets of duplicate triplets to merge...")
    
    for dup in duplicates:
        # Flatten and deduplicate documents array
        all_docs = []
        for doc_array in dup['all_documents']:
            if doc_array:
                if isinstance(doc_array, list):
                    all_docs.extend(doc_array)
                else:
                    all_docs.append(doc_array)
        
        # Remove duplicates from documents
        unique_docs = []
        seen = set()
        for doc in all_docs:
            doc_key = (doc.get('section_id'), doc.get('so_hieu'))
            if doc_key not in seen:
                seen.add(doc_key)
                unique_docs.append(doc)
        
        # Keep first triplet, delete others
        keep_id = dup['triplet_ids'][0]
        delete_ids = dup['triplet_ids'][1:]
        
        # Update the kept triplet with merged documents
        triplets_collection.update_one(
            {"_id": keep_id},
            {
                "$set": {
                    "documents": unique_docs,
                    "subject_name": dup['subject_name'],
                    "relation_name": dup['relation_name'],
                    "object_name": dup['object_name']
                }
            }
        )
        
        # Delete duplicate triplets
        triplets_collection.delete_many({"_id": {"$in": delete_ids}})
    
    print(f"Merged {len(duplicates)} duplicate triplet sets.")


def build_tree_downward(sections_col, node_id: str, max_depth: int = 10) -> Dict:
    """
    Build tree structure by traversing downward from a given node to all children.

    Args:
        sections_col: MongoDB collection
        node_id: The _id of the starting node
        max_depth: Maximum depth to traverse

    Returns:
        Dict representing the tree structure
    """

    def get_node_with_children(current_id: str, depth: int = 0) -> Optional[Dict]:
        if not current_id or depth > max_depth:
            return None

        node = sections_col.find_one({"_id": current_id})
        if not node:
            return None

        # Build the tree node
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
            "children": []
        }

        # Find all children
        children = sections_col.find({"parent_id": current_id})
        for child in children:
            child_tree = get_node_with_children(child["_id"], depth + 1)
            if child_tree:
                tree_node["children"].append(child_tree)

        return tree_node

    return get_node_with_children(node_id)


def print_tree(node: Dict, indent: int = 0, show_content: bool = False):
    """
    Pretty print the tree structure.
    """
    if not node:
        return

    prefix = "  " * indent
    print(f"{prefix}├─ [{node['type']}] {node['title']}")

    if show_content and node.get('content'):
        content_preview = node['content'][:100] + "..." if len(node['content']) > 100 else node['content']
        print(f"{prefix}   Content: {content_preview}")

    # Print children if using downward tree
    if 'children' in node:
        for child in node['children']:
            print_tree(child, indent + 1, show_content)

    # Print parent if using upward tree
    if 'parent' in node:
        print(f"{prefix}   ↑ Parent:")
        print_tree(node['parent'], indent + 1, show_content)