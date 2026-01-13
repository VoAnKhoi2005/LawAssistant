"""
Migration script to create new triplets collection with updated schema

This script:
1. Creates a new collection "triplets_new" with the updated schema
2. Migrates all existing triplets from "triplets" to "triplets_new"
3. Removes duplicates and merges documents arrays
4. Creates proper indexes on the new collection
5. Optionally renames collections (backup old, use new)

Usage:
    python migrate_triplets_to_new_collection.py
"""

import sys
from src.db.mongo import init_mongo


def migrate_to_new_collection(db, source_col="triplets", target_col="triplets_new"):
    """
    Migrate triplets from old collection to new collection with updated schema
    
    Args:
        db: MongoDB database instance
        source_col: Name of existing triplets collection
        target_col: Name of new triplets collection
    """
    source_collection = db[source_col]
    target_collection = db[target_col]
    concepts_collection = db["concepts"]
    relations_collection = db["relations"]
    
    # Check if target already exists
    if target_col in db.list_collection_names():
        print(f"\n⚠️  Collection '{target_col}' already exists!")
        response = input("Delete and recreate? (yes/no): ")
        if response.lower() == 'yes':
            db.drop_collection(target_col)
            print(f"✓ Dropped existing '{target_col}' collection")
        else:
            print("Migration cancelled.")
            return False
    
    print(f"\n{'='*60}")
    print(f"Migrating: {source_col} → {target_col}")
    print(f"{'='*60}")
    
    # Get total count
    total = source_collection.count_documents({})
    print(f"Total triplets in source: {total:,}")
    
    if total == 0:
        print("No triplets to migrate!")
        return False
    
    # Dictionary to track unique triplets and their documents
    # Key: (subject_id, relation_id, object_id)
    # Value: {subject_name, relation_name, object_name, documents[]}
    unique_triplets = {}
    
    processed = 0
    skipped = 0
    
    print("\nProcessing triplets...")
    
    # Iterate through all source triplets
    for triplet in source_collection.find({}).batch_size(1000):
        processed += 1
        
        if processed % 1000 == 0:
            print(f"  Processed: {processed:,}/{total:,}")
        
        subject_id = triplet.get("subject_id")
        relation_id = triplet.get("relation_id")
        object_id = triplet.get("object_id")
        
        if not subject_id or not relation_id or not object_id:
            skipped += 1
            continue
        
        # Create unique key
        key = (str(subject_id), str(relation_id), str(object_id))
        
        # Get or create entry in unique_triplets
        if key not in unique_triplets:
            # Get names
            subject_name = triplet.get("subject_name")
            relation_name = triplet.get("relation_name")
            object_name = triplet.get("object_name")
            
            # If names don't exist in triplet, fetch from concepts/relations
            if not subject_name:
                concept = concepts_collection.find_one({"_id": subject_id})
                subject_name = concept["name"] if concept else "Unknown"
            
            if not relation_name:
                relation = relations_collection.find_one({"_id": relation_id})
                relation_name = relation["name"] if relation else "Unknown"
            
            if not object_name:
                concept = concepts_collection.find_one({"_id": object_id})
                object_name = concept["name"] if concept else "Unknown"
            
            unique_triplets[key] = {
                "subject_id": subject_id,
                "relation_id": relation_id,
                "object_id": object_id,
                "subject_name": subject_name,
                "relation_name": relation_name,
                "object_name": object_name,
                "documents": []
            }
        
        # Add document reference
        # Handle both old format (section_id, so_hieu) and new format (documents array)
        if "documents" in triplet and isinstance(triplet["documents"], list):
            # New format - extend documents array
            for doc in triplet["documents"]:
                if doc not in unique_triplets[key]["documents"]:
                    unique_triplets[key]["documents"].append(doc)
        else:
            # Old format - create document reference
            section_id = triplet.get("section_id")
            so_hieu = triplet.get("so_hieu")
            
            if section_id and so_hieu:
                doc_ref = {"section_id": section_id, "so_hieu": so_hieu}
                if doc_ref not in unique_triplets[key]["documents"]:
                    unique_triplets[key]["documents"].append(doc_ref)
    
    print(f"\n  Total processed: {processed:,}")
    print(f"  Skipped (invalid): {skipped:,}")
    print(f"  Unique triplets: {len(unique_triplets):,}")
    print(f"  Duplicates removed: {processed - len(unique_triplets):,}")
    
    # Insert into new collection
    print(f"\nInserting into '{target_col}'...")
    
    if unique_triplets:
        # Convert to list and insert in batches
        triplets_list = list(unique_triplets.values())
        batch_size = 1000
        
        for i in range(0, len(triplets_list), batch_size):
            batch = triplets_list[i:i+batch_size]
            target_collection.insert_many(batch)
            print(f"  Inserted: {min(i+batch_size, len(triplets_list)):,}/{len(triplets_list):,}")
        
        print(f"✓ Inserted {len(triplets_list):,} unique triplets")
    
    # Create indexes
    print(f"\nCreating indexes on '{target_col}'...")
    try:
        target_collection.create_index([
            ("subject_id", 1),
            ("relation_id", 1),
            ("object_id", 1)
        ], unique=True)
        print("  ✓ Created unique compound index")
        
        target_collection.create_index("documents.section_id")
        print("  ✓ Created index on documents.section_id")
        
        target_collection.create_index("documents.so_hieu")
        print("  ✓ Created index on documents.so_hieu")
        
        target_collection.create_index("subject_name")
        print("  ✓ Created index on subject_name")
        
        target_collection.create_index("relation_name")
        print("  ✓ Created index on relation_name")
        
        target_collection.create_index("object_name")
        print("  ✓ Created index on object_name")
        
    except Exception as e:
        print(f"  ⚠️  Warning: Index creation issue: {e}")
    
    return True


def validate_migration(db, source_col="triplets", target_col="triplets_new"):
    """Validate the migration was successful"""
    source_collection = db[source_col]
    target_collection = db[target_col]
    
    source_count = source_collection.count_documents({})
    target_count = target_collection.count_documents({})
    
    # Count total document references in new collection
    total_docs = 0
    for triplet in target_collection.find({}, {"documents": 1}):
        total_docs += len(triplet.get("documents", []))
    
    print("\n" + "="*60)
    print("VALIDATION RESULTS")
    print("="*60)
    print(f"Source collection ({source_col}):")
    print(f"  Total triplets: {source_count:,}")
    print(f"\nTarget collection ({target_col}):")
    print(f"  Total triplets: {target_count:,}")
    print(f"  Total document references: {total_docs:,}")
    print(f"  Duplicates removed: {source_count - target_count:,}")
    
    # Sample comparison
    print("\nSample verification:")
    sample = target_collection.find_one({})
    if sample:
        print(f"  Sample triplet has {len(sample.get('documents', []))} document reference(s)")
        print(f"  Subject: {sample.get('subject_name')}")
        print(f"  Relation: {sample.get('relation_name')}")
        print(f"  Object: {sample.get('object_name')}")
    
    return target_count > 0


def swap_collections(db, old_col="triplets", new_col="triplets_new", backup_col="triplets_backup"):
    """
    Swap collections: rename old to backup, rename new to old
    
    Args:
        db: MongoDB database
        old_col: Current production collection
        new_col: New migrated collection
        backup_col: Backup name for old collection
    """
    print("\n" + "="*60)
    print("SWAPPING COLLECTIONS")
    print("="*60)
    print(f"  {old_col} → {backup_col}")
    print(f"  {new_col} → {old_col}")
    
    # Check if backup already exists
    if backup_col in db.list_collection_names():
        print(f"\n⚠️  Backup collection '{backup_col}' already exists!")
        response = input("Delete existing backup? (yes/no): ")
        if response.lower() == 'yes':
            db.drop_collection(backup_col)
            print(f"✓ Dropped existing '{backup_col}'")
        else:
            print("Swap cancelled.")
            return False
    
    # Rename old to backup
    db[old_col].rename(backup_col)
    print(f"✓ Renamed {old_col} → {backup_col}")
    
    # Rename new to old
    db[new_col].rename(old_col)
    print(f"✓ Renamed {new_col} → {old_col}")
    
    print("\n✓ Collections swapped successfully!")
    print(f"\nYour old data is backed up in: {backup_col}")
    print(f"To remove backup: db.{backup_col}.drop()")
    
    return True


def main():
    """Main migration workflow"""
    print("="*60)
    print("MongoDB Triplets Collection Migration")
    print("Migrate to new collection with updated schema")
    print("="*60)
    
    # Connect to MongoDB
    print("\nConnecting to MongoDB...")
    client = init_mongo()
    if not client:
        print("❌ Failed to connect to MongoDB")
        return 1
    
    # Get database name
    db_name = input("\nEnter database name (default: KB_PROPERTY_LAW): ").strip()
    if not db_name:
        db_name = "KB_PROPERTY_LAW"
    
    db = client[db_name]
    print(f"✓ Connected to database: {db_name}")
    
    # Get collection names
    print("\nCollection names:")
    source_col = input("  Source collection (default: triplets): ").strip()
    if not source_col:
        source_col = "triplets"
    
    target_col = input("  Target collection (default: triplets_new): ").strip()
    if not target_col:
        target_col = "triplets_new"
    
    # Check source exists
    if source_col not in db.list_collection_names():
        print(f"\n❌ Source collection '{source_col}' does not exist!")
        return 1
    
    # Show current state
    source_count = db[source_col].count_documents({})
    print(f"\nSource collection '{source_col}': {source_count:,} triplets")
    
    # Confirm migration
    print("\n" + "="*60)
    print("This will:")
    print(f"  1. Create new collection '{target_col}'")
    print(f"  2. Migrate all triplets from '{source_col}'")
    print("  3. Remove duplicates and merge document references")
    print("  4. Create proper indexes")
    print(f"  5. Keep original '{source_col}' unchanged")
    print("="*60)
    
    response = input("\nProceed with migration? (yes/no): ")
    if response.lower() != 'yes':
        print("Migration cancelled.")
        return 0
    
    # Run migration
    success = migrate_to_new_collection(db, source_col, target_col)
    
    if not success:
        print("\n❌ Migration failed!")
        return 1
    
    # Validate
    validate_migration(db, source_col, target_col)
    
    # Ask about swapping
    print("\n" + "="*60)
    response = input(f"\nSwap collections to use '{target_col}' as '{source_col}'? (yes/no): ")
    if response.lower() == 'yes':
        backup_col = input(f"Backup name for old collection (default: {source_col}_backup): ").strip()
        if not backup_col:
            backup_col = f"{source_col}_backup"
        
        swap_collections(db, source_col, target_col, backup_col)
    else:
        print(f"\nMigration complete! New collection is: {target_col}")
        print(f"To use it, update your code to reference '{target_col}'")
        print(f"Or manually rename: db.{target_col}.rename('{source_col}')")
    
    print("\n" + "="*60)
    print("✓ MIGRATION COMPLETED SUCCESSFULLY")
    print("="*60)
    
    return 0


if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\nMigration cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
