"""
Vietnamese Legal Concept & Relation Similarity Finder
Uses VoVanPhuc/sup-SimCSE-VietNamese-phobert-base for embeddings with GPU support
Stores in MongoDB and finds similar items considering synonyms
"""

import torch
from transformers import AutoModel, AutoTokenizer
from pymongo import MongoClient, UpdateOne
import numpy as np
from typing import List, Dict, Tuple, Optional
from sklearn.metrics.pairwise import cosine_similarity
from bson import ObjectId
import logging
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VietnameseSimilarityFinder:
    def __init__(self, mongo_uri: str = "mongodb://localhost:27017/",
                 db_name: str = "legal_kb",
                 use_gpu: bool = True):
        """Initialize with MongoDB connection and SimCSE model"""
        # MongoDB setup
        self.client = MongoClient(mongo_uri)
        self.db = self.client[db_name]
        self.concepts = self.db['concepts']
        self.relations = self.db['relations']
        self.triplets = self.db['triplets']

        # GPU setup
        self.device = self._setup_device(use_gpu)
        logger.info(f"Using device: {self.device}")

        # Load Vietnamese SimCSE model
        logger.info("Loading VoVanPhuc/sup-SimCSE-VietNamese-phobert-base...")
        self.model_name = "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base"
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name)
        self.model = AutoModel.from_pretrained(self.model_name)
        self.model.to(self.device)
        self.model.eval()
        logger.info("Model loaded successfully")

        # Create indexes for efficient searching
        self._create_indexes()

    def _setup_device(self, use_gpu: bool) -> torch.device:
        """Setup GPU or CPU device"""
        if use_gpu and torch.cuda.is_available():
            device = torch.device("cuda")
            logger.info(f"GPU available: {torch.cuda.get_device_name(0)}")
            logger.info(f"GPU memory: {torch.cuda.get_device_properties(0).total_memory / 1e9:.2f} GB")
        else:
            device = torch.device("cpu")
            if use_gpu and not torch.cuda.is_available():
                logger.warning("GPU requested but not available, using CPU")
        return device

    def _create_indexes(self):
        """Create MongoDB indexes for efficient queries"""
        self.concepts.create_index("name")
        self.concepts.create_index("embedding")
        self.relations.create_index("name")
        self.relations.create_index("embedding")
        self.triplets.create_index([("subject_id", 1), ("relation_id", 1), ("object_id", 1)])
        self.triplets.create_index("subject_name")
        self.triplets.create_index("object_name")
        logger.info("Indexes created successfully")

    def get_embedding(self, text: str) -> np.ndarray:
        """Generate embedding for a text using SimCSE on GPU"""
        with torch.no_grad():
            inputs = self.tokenizer(text, return_tensors="pt",
                                   padding=True, truncation=True,
                                   max_length=512)
            # Move inputs to GPU
            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            outputs = self.model(**inputs)
            # Use CLS token embedding
            embedding = outputs.last_hidden_state[:, 0, :].squeeze()
            # Move back to CPU for numpy conversion
            return embedding.cpu().numpy()

    def get_batch_embeddings(self, texts: List[str], batch_size: int = 32) -> np.ndarray:
        """Generate embeddings for multiple texts efficiently using GPU batching"""
        all_embeddings = []

        with torch.no_grad():
            for i in range(0, len(texts), batch_size):
                batch_texts = texts[i:i + batch_size]

                # Tokenize batch
                inputs = self.tokenizer(batch_texts, return_tensors="pt",
                                       padding=True, truncation=True,
                                       max_length=512)
                # Move to GPU
                inputs = {k: v.to(self.device) for k, v in inputs.items()}

                outputs = self.model(**inputs)
                # Extract CLS embeddings
                embeddings = outputs.last_hidden_state[:, 0, :].cpu().numpy()
                all_embeddings.append(embeddings)

        return np.vstack(all_embeddings)

    def get_text_variants(self, name: str, synonyms: List[str]) -> List[str]:
        """Get all text variants including name and synonyms"""
        variants = [name]
        if synonyms:
            variants.extend(synonyms)
        return variants

    def get_combined_embedding(self, name: str, synonyms: List[str]) -> np.ndarray:
        """
        Get combined embedding considering name and all synonyms

        Strategy: Average pooling of all variant embeddings

        Why this works:
        1. Each variant (name + synonyms) gets its own embedding
        2. Averaging captures the semantic center of all meanings
        3. Normalization ensures consistent similarity calculations

        Example:
        - name: "gồm"
        - synonyms: ["bao gồm", "chứa", "có"]
        - Creates 4 embeddings, averages them
        - Result captures all semantic variations
        """
        variants = self.get_text_variants(name, synonyms)

        # Use batch processing for efficiency
        embeddings = self.get_batch_embeddings(variants, batch_size=len(variants))

        # Average all embeddings (semantic centroid)
        combined_embedding = np.mean(embeddings, axis=0)
        # Normalize to unit vector for cosine similarity
        combined_embedding = combined_embedding / np.linalg.norm(combined_embedding)

        return combined_embedding

    def generate_and_store_concept_embeddings(self, batch_size: int = 32):
        """Generate embeddings for all concepts and store in MongoDB using GPU"""
        logger.info("Checking concepts for embeddings...")

        # Find concepts without embeddings
        concepts_without_embeddings = list(self.concepts.find({'embeddings': {'$exists': False}}))
        concepts_with_embeddings = self.concepts.count_documents({'embeddings': {'$exists': True}})
        
        total = len(concepts_without_embeddings)
        
        if total == 0:
            logger.info(f"✓ All {concepts_with_embeddings} concepts already have embeddings. Skipping generation.")
            return
        
        logger.info(f"Found {concepts_with_embeddings} concepts with embeddings (skipping)")
        logger.info(f"Generating embeddings for {total} concepts without embeddings...")

        updates = []
        for concept in tqdm(concepts_without_embeddings, desc="Processing concepts", unit="concept"):
            name = concept['name']
            synonyms = concept.get('synonym', [])

            # Generate individual embeddings for name and each synonym
            variants = self.get_text_variants(name, synonyms)
            embeddings = self.get_batch_embeddings(variants, batch_size=len(variants))
            
            # Store as list: [name_embedding, syn1_embedding, syn2_embedding, ...]
            embeddings_list = [emb.tolist() for emb in embeddings]

            # Prepare update
            updates.append(
                UpdateOne(
                    {'_id': concept['_id']},
                    {'$set': {
                        'embeddings': embeddings_list,  # Multiple embeddings
                        'embedding_texts': variants,     # Corresponding texts
                        'embedding_model': self.model_name,
                        'embedding_device': str(self.device),
                        'synonym_count': len(synonyms)
                    }}
                )
            )

            # Batch update
            if len(updates) >= batch_size:
                self.concepts.bulk_write(updates)
                updates = []

        if updates:
            self.concepts.bulk_write(updates)

        logger.info(f"✓ Generated embeddings for {total} new concepts")

    def generate_and_store_relation_embeddings(self, batch_size: int = 128):
        """Generate embeddings for all relations and store in MongoDB using GPU"""
        logger.info("Checking relations for embeddings...")

        # Find relations without embeddings
        relations_without_embeddings = list(self.relations.find({'embeddings': {'$exists': False}}))
        relations_with_embeddings = self.relations.count_documents({'embeddings': {'$exists': True}})
        
        total = len(relations_without_embeddings)
        
        if total == 0:
            logger.info(f"✓ All {relations_with_embeddings} relations already have embeddings. Skipping generation.")
            return
        
        logger.info(f"Found {relations_with_embeddings} relations with embeddings (skipping)")
        logger.info(f"Generating embeddings for {total} relations without embeddings...")

        updates = []
        for relation in tqdm(relations_without_embeddings, desc="Processing relations", unit="relation"):
            name = relation['name']
            synonyms = relation.get('synonym', [])

            # Generate individual embeddings for name and each synonym
            variants = self.get_text_variants(name, synonyms)
            embeddings = self.get_batch_embeddings(variants, batch_size=len(variants))
            
            # Store as list: [name_embedding, syn1_embedding, syn2_embedding, ...]
            embeddings_list = [emb.tolist() for emb in embeddings]

            # Prepare update
            updates.append(
                UpdateOne(
                    {'_id': relation['_id']},
                    {'$set': {
                        'embeddings': embeddings_list,  # Multiple embeddings
                        'embedding_texts': variants,     # Corresponding texts
                        'embedding_model': self.model_name,
                        'embedding_device': str(self.device),
                        'synonym_count': len(synonyms)
                    }}
                )
            )

            # Batch update
            if len(updates) >= batch_size:
                self.relations.bulk_write(updates)
                updates = []

        if updates:
            self.relations.bulk_write(updates)

        logger.info(f"✓ Generated embeddings for {total} new relations")

    def find_similar_concepts(self, concept_name: str, top_k: int = 5,
                             include_synonyms: bool = True,
                             min_similarity: float = 0.0) -> List[Dict]:
        """
        Find similar concepts to the given concept name

        Args:
            concept_name: Name of the concept to find similar items for
            top_k: Number of similar items to return
            include_synonyms: Whether to consider synonyms in similarity
            min_similarity: Minimum similarity threshold (0.0 to 1.0)

        Returns:
            List of similar concepts with similarity scores
        """
        # Get the query concept
        query_concept = self.concepts.find_one({'name': concept_name})
        if not query_concept:
            logger.error(f"Concept '{concept_name}' not found")
            return []

        # Get query embedding (name only)
        query_embedding = self.get_embedding(concept_name)

        # Get all concepts with embeddings (exclude self)
        all_concepts = list(self.concepts.find(
            {'embeddings': {'$exists': True},
             '_id': {'$ne': query_concept['_id']}}
        ))

        results = []
        if all_concepts:
            # Compare against all embeddings (name + synonyms) for each concept
            similarity_scores = []
            for concept in all_concepts:
                # Get all embeddings for this concept
                concept_embeddings = np.array(concept['embeddings'])
                
                # Calculate similarity with each embedding (name + synonyms)
                sims = cosine_similarity([query_embedding], concept_embeddings)[0]
                
                # Take the maximum similarity across all variants
                max_similarity = np.max(sims)
                similarity_scores.append(max_similarity)
            
            similarities = np.array(similarity_scores)

            # Filter by minimum similarity
            valid_indices = np.where(similarities >= min_similarity)[0]

            # Sort by similarity
            sorted_indices = valid_indices[np.argsort(similarities[valid_indices])[::-1]][:top_k]

            for idx in sorted_indices:
                concept = all_concepts[idx]
                results.append({
                    '_id': concept['_id'],
                    'name': concept['name'],
                    'synonyms': concept.get('synonym', []),
                    'similarity_score': float(similarities[idx]),
                    'documents_count': len(concept.get('documents', []))
                })

        return results

    def find_similar_relations(self, relation_name: str, top_k: int = 5,
                              include_synonyms: bool = True,
                              min_similarity: float = 0.0) -> List[Dict]:
        """
        Find similar relations to the given relation name

        Args:
            relation_name: Name of the relation to find similar items for
            top_k: Number of similar items to return
            include_synonyms: Whether to consider synonyms in similarity
            min_similarity: Minimum similarity threshold (0.0 to 1.0)

        Returns:
            List of similar relations with similarity scores
        """
        # Get the query relation
        query_relation = self.relations.find_one({'name': relation_name})
        if not query_relation:
            logger.error(f"Relation '{relation_name}' not found")
            return []

        # Get query embedding (name only)
        query_embedding = self.get_embedding(relation_name)

        # Get all relations with embeddings (exclude self)
        all_relations = list(self.relations.find(
            {'embeddings': {'$exists': True},
             '_id': {'$ne': query_relation['_id']}}
        ))

        results = []
        if all_relations:
            # Compare against all embeddings (name + synonyms) for each relation
            similarity_scores = []
            for relation in all_relations:
                # Get all embeddings for this relation
                relation_embeddings = np.array(relation['embeddings'])
                
                # Calculate similarity with each embedding (name + synonyms)
                sims = cosine_similarity([query_embedding], relation_embeddings)[0]
                
                # Take the maximum similarity across all variants
                max_similarity = np.max(sims)
                similarity_scores.append(max_similarity)
            
            similarities = np.array(similarity_scores)

            # Filter by minimum similarity
            valid_indices = np.where(similarities >= min_similarity)[0]

            # Sort by similarity
            sorted_indices = valid_indices[np.argsort(similarities[valid_indices])[::-1]][:top_k]

            for idx in sorted_indices:
                relation = all_relations[idx]
                results.append({
                    '_id': relation['_id'],
                    'name': relation['name'],
                    'synonyms': relation.get('synonym', []),
                    'similarity_score': float(similarities[idx]),
                    'documents_count': len(relation.get('documents', []))
                })

        return results

    def find_similar_by_id(self, item_id: str, item_type: str = 'concept',
                          top_k: int = 5, min_similarity: float = 0.0) -> List[Dict]:
        """
        Find similar items by ObjectId

        Args:
            item_id: ObjectId string
            item_type: 'concept' or 'relation'
            top_k: Number of similar items to return
            min_similarity: Minimum similarity threshold
        """
        collection = self.concepts if item_type == 'concept' else self.relations
        item = collection.find_one({'_id': ObjectId(item_id)})

        if not item:
            logger.error(f"{item_type} with id '{item_id}' not found")
            return []

        if item_type == 'concept':
            return self.find_similar_concepts(item['name'], top_k, min_similarity=min_similarity)
        else:
            return self.find_similar_relations(item['name'], top_k, min_similarity=min_similarity)

    def get_triplet_context(self, triplet_id: str) -> Dict:
        """
        Get full context for a triplet including embeddings

        Args:
            triplet_id: ObjectId string of the triplet

        Returns:
            Dict with triplet info and related embeddings
        """
        triplet = self.triplets.find_one({'_id': ObjectId(triplet_id)})
        if not triplet:
            logger.error(f"Triplet with id '{triplet_id}' not found")
            return {}

        # Get subject, relation, object details
        subject = self.concepts.find_one({'_id': triplet['subject_id']})
        relation = self.relations.find_one({'_id': triplet['relation_id']})
        obj = self.concepts.find_one({'_id': triplet['object_id']})

        return {
            'triplet': {
                '_id': str(triplet['_id']),
                'subject_name': triplet['subject_name'],
                'relation_name': triplet['relation_name'],
                'object_name': triplet['object_name'],
                'documents': triplet.get('documents', [])
            },
            'subject': {
                '_id': str(subject['_id']) if subject else None,
                'name': subject['name'] if subject else None,
                'synonyms': subject.get('synonym', []) if subject else [],
                'has_embedding': 'embedding' in subject if subject else False
            },
            'relation': {
                '_id': str(relation['_id']) if relation else None,
                'name': relation['name'] if relation else None,
                'synonyms': relation.get('synonym', []) if relation else [],
                'has_embedding': 'embedding' in relation if relation else False
            },
            'object': {
                '_id': str(obj['_id']) if obj else None,
                'name': obj['name'] if obj else None,
                'synonyms': obj.get('synonym', []) if obj else [],
                'has_embedding': 'embedding' in obj if obj else False
            }
        }

    def find_similar_triplets(self, triplet_id: str, top_k: int = 5) -> List[Dict]:
        """
        Find similar triplets based on subject, relation, and object similarity

        Args:
            triplet_id: ObjectId string of the query triplet
            top_k: Number of similar triplets to return

        Returns:
            List of similar triplets with similarity scores
        """
        # Get triplet context
        context = self.get_triplet_context(triplet_id)
        if not context:
            return []

        triplet = context['triplet']

        # Find similar subjects, relations, and objects
        similar_subjects = self.find_similar_concepts(triplet['subject_name'], top_k=10)
        similar_relations = self.find_similar_relations(triplet['relation_name'], top_k=10)
        similar_objects = self.find_similar_concepts(triplet['object_name'], top_k=10)

        # Find triplets with similar components
        candidate_triplets = []

        # Search for triplets with similar subjects
        for subj in similar_subjects[:5]:
            triplets = list(self.triplets.find({'subject_name': subj['name']}))
            for t in triplets:
                if str(t['_id']) != triplet_id:
                    candidate_triplets.append({
                        'triplet': t,
                        'subject_similarity': subj['similarity_score'],
                        'match_type': 'subject'
                    })

        # Search for triplets with similar objects
        for obj in similar_objects[:5]:
            triplets = list(self.triplets.find({'object_name': obj['name']}))
            for t in triplets:
                if str(t['_id']) != triplet_id:
                    candidate_triplets.append({
                        'triplet': t,
                        'object_similarity': obj['similarity_score'],
                        'match_type': 'object'
                    })

        # Remove duplicates and calculate combined scores
        unique_triplets = {}
        for item in candidate_triplets:
            tid = str(item['triplet']['_id'])
            if tid not in unique_triplets:
                unique_triplets[tid] = {
                    'triplet': item['triplet'],
                    'subject_similarity': 0.0,
                    'object_similarity': 0.0,
                    'relation_similarity': 0.0
                }

            if 'subject_similarity' in item:
                unique_triplets[tid]['subject_similarity'] = max(
                    unique_triplets[tid]['subject_similarity'],
                    item['subject_similarity']
                )
            if 'object_similarity' in item:
                unique_triplets[tid]['object_similarity'] = max(
                    unique_triplets[tid]['object_similarity'],
                    item['object_similarity']
                )

        # Calculate combined similarity score
        results = []
        for tid, data in unique_triplets.items():
            combined_score = (
                data['subject_similarity'] * 0.4 +
                data['relation_similarity'] * 0.2 +
                data['object_similarity'] * 0.4
            )

            results.append({
                '_id': data['triplet']['_id'],
                'subject_name': data['triplet']['subject_name'],
                'relation_name': data['triplet']['relation_name'],
                'object_name': data['triplet']['object_name'],
                'documents': data['triplet'].get('documents', []),
                'similarity_score': combined_score,
                'subject_similarity': data['subject_similarity'],
                'relation_similarity': data['relation_similarity'],
                'object_similarity': data['object_similarity']
            })

        # Sort by combined score
        results.sort(key=lambda x: x['similarity_score'], reverse=True)

        return results[:top_k]

    def find_all_similar_groups(self, collection_name: str = 'concepts', 
                                 min_similarity: float = 0.90, 
                                 batch_size: int = 100) -> List[Dict]:
        """
        Fast batch processing to find all similar groups
        Uses vectorized operations for massive speedup
        
        Args:
            collection_name: 'concepts' or 'relations'
            min_similarity: Minimum similarity threshold
            batch_size: Number of items to process in parallel
            
        Returns:
            List of groups with similar items
        """
        collection = self.concepts if collection_name == 'concepts' else self.relations
        
        # Load all items with embeddings
        all_items = list(collection.find({'embeddings': {'$exists': True}}))
        
        if len(all_items) == 0:
            logger.warning(f"No {collection_name} with embeddings found")
            return []
        
        logger.info(f"Processing {len(all_items)} {collection_name} for similarity grouping...")
        
        # Extract first embedding (name embedding) for each item for faster comparison
        item_embeddings = []
        item_info = []
        
        for item in all_items:
            # Use first embedding (name embedding)
            name_embedding = np.array(item['embeddings'][0])
            item_embeddings.append(name_embedding)
            item_info.append({
                'id': str(item['_id']),
                'name': item['name'],
                'synonyms': item.get('synonym', []),
                'all_embeddings': np.array(item['embeddings'])
            })
        
        # Convert to matrix for vectorized operations
        embeddings_matrix = np.vstack(item_embeddings)
        
        # Compute similarity matrix for all items at once (MUCH faster)
        logger.info(f"Computing similarity matrix ({len(all_items)} x {len(all_items)})...")
        similarity_matrix = cosine_similarity(embeddings_matrix)
        
        # Find groups using similarity matrix
        processed = set()
        groups = []
        
        logger.info(f"Finding groups with similarity >= {min_similarity}...")
        for i in tqdm(range(len(all_items)), desc=f"Grouping {collection_name}", unit="item"):
            if str(item_info[i]['id']) in processed:
                continue
            
            # Find all items similar to this one (vectorized operation)
            similar_indices = np.where(similarity_matrix[i] >= min_similarity)[0]
            
            # Remove self
            similar_indices = similar_indices[similar_indices != i]
            
            if len(similar_indices) > 0:
                group = {
                    'main': item_info[i]['name'],
                    'main_id': item_info[i]['id'],
                    'synonyms': item_info[i]['synonyms'],
                    'similar': []
                }
                
                for j in similar_indices:
                    if str(item_info[j]['id']) not in processed:
                        # For more accurate similarity, compare against all embeddings
                        max_sim = similarity_matrix[i][j]
                        
                        # Optional: Check against synonym embeddings too
                        if len(item_info[j]['all_embeddings']) > 1:
                            sims = cosine_similarity([item_embeddings[i]], item_info[j]['all_embeddings'])[0]
                            max_sim = max(max_sim, np.max(sims))
                        
                        if max_sim >= min_similarity:
                            group['similar'].append({
                                'name': item_info[j]['name'],
                                'id': item_info[j]['id'],
                                'similarity': float(max_sim),
                                'synonyms': item_info[j]['synonyms']
                            })
                            processed.add(str(item_info[j]['id']))
                
                if group['similar']:
                    groups.append(group)
                    processed.add(str(item_info[i]['id']))
        
        logger.info(f"Found {len(groups)} groups of similar {collection_name}")
        return groups

    def merge_concepts(self, group: Dict) -> Dict:
        """
        Merge a group of similar concepts
        - Choose main concept based on reference count
        - Move others to synonyms
        - Update all triplets
        
        Returns merge statistics
        """
        main_id = ObjectId(group['main_id'])
        similar_items = group['similar']
        
        if not similar_items:
            return {'merged': 0, 'triplets_updated': 0}
        
        # Count references for each concept (main + similar)
        all_concepts = [{'id': main_id, 'name': group['main']}]
        for sim in similar_items:
            all_concepts.append({'id': ObjectId(sim['id']), 'name': sim['name']})
        
        # Count triplet references
        ref_counts = {}
        for concept in all_concepts:
            count = self.triplets.count_documents({
                '$or': [
                    {'subject_id': concept['id']},
                    {'object_id': concept['id']}
                ]
            })
            ref_counts[str(concept['id'])] = {
                'count': count,
                'name': concept['name'],
                'id': concept['id']
            }
        
        # Choose concept with most references as main
        main_concept = max(ref_counts.values(), key=lambda x: x['count'])
        main_concept_id = main_concept['id']
        main_concept_name = main_concept['name']
        
        # Collect all synonyms
        all_synonyms = set(group['synonyms'])
        merged_concepts = []
        
        for concept_id_str, info in ref_counts.items():
            if info['id'] != main_concept_id:
                # Add this concept's name to synonyms
                all_synonyms.add(info['name'])
                merged_concepts.append(info['id'])
                
                # Get this concept's synonyms
                concept_doc = self.concepts.find_one({'_id': info['id']})
                if concept_doc and 'synonym' in concept_doc:
                    all_synonyms.update(concept_doc['synonym'])
        
        # Update main concept with all synonyms
        self.concepts.update_one(
            {'_id': main_concept_id},
            {'$set': {'synonym': list(all_synonyms)}}
        )
        
        # Update triplets - subject references
        subject_result = self.triplets.update_many(
            {'subject_id': {'$in': merged_concepts}},
            {'$set': {
                'subject_id': main_concept_id,
                'subject_name': main_concept_name
            }}
        )
        
        # Update triplets - object references
        object_result = self.triplets.update_many(
            {'object_id': {'$in': merged_concepts}},
            {'$set': {
                'object_id': main_concept_id,
                'object_name': main_concept_name
            }}
        )
        
        # Delete merged concepts
        self.concepts.delete_many({'_id': {'$in': merged_concepts}})
        
        return {
            'merged': len(merged_concepts),
            'main_name': main_concept_name,
            'main_id': str(main_concept_id),
            'triplets_updated': subject_result.modified_count + object_result.modified_count,
            'ref_count': main_concept['count']
        }

    def merge_relations(self, group: Dict) -> Dict:
        """
        Merge a group of similar relations
        - Choose main relation based on reference count
        - Move others to synonyms
        - Update all triplets
        
        Returns merge statistics
        """
        main_id = ObjectId(group['main_id'])
        similar_items = group['similar']
        
        if not similar_items:
            return {'merged': 0, 'triplets_updated': 0}
        
        # Count references for each relation (main + similar)
        all_relations = [{'id': main_id, 'name': group['main']}]
        for sim in similar_items:
            all_relations.append({'id': ObjectId(sim['id']), 'name': sim['name']})
        
        # Count triplet references
        ref_counts = {}
        for relation in all_relations:
            count = self.triplets.count_documents({'relation_id': relation['id']})
            ref_counts[str(relation['id'])] = {
                'count': count,
                'name': relation['name'],
                'id': relation['id']
            }
        
        # Choose relation with most references as main
        main_relation = max(ref_counts.values(), key=lambda x: x['count'])
        main_relation_id = main_relation['id']
        main_relation_name = main_relation['name']
        
        # Collect all synonyms
        all_synonyms = set(group['synonyms'])
        merged_relations = []
        
        for relation_id_str, info in ref_counts.items():
            if info['id'] != main_relation_id:
                # Add this relation's name to synonyms
                all_synonyms.add(info['name'])
                merged_relations.append(info['id'])
                
                # Get this relation's synonyms
                relation_doc = self.relations.find_one({'_id': info['id']})
                if relation_doc and 'synonym' in relation_doc:
                    all_synonyms.update(relation_doc['synonym'])
        
        # Update main relation with all synonyms
        self.relations.update_one(
            {'_id': main_relation_id},
            {'$set': {'synonym': list(all_synonyms)}}
        )
        
        # Update triplets
        triplet_result = self.triplets.update_many(
            {'relation_id': {'$in': merged_relations}},
            {'$set': {
                'relation_id': main_relation_id,
                'relation_name': main_relation_name
            }}
        )
        
        # Delete merged relations
        self.relations.delete_many({'_id': {'$in': merged_relations}})
        
        return {
            'merged': len(merged_relations),
            'main_name': main_relation_name,
            'main_id': str(main_relation_id),
            'triplets_updated': triplet_result.modified_count,
            'ref_count': main_relation['count']
        }

    def cleanup(self):
        """Cleanup resources"""
        self.client.close()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()


# Example usage
def main():
    # Initialize the similarity finder with GPU
    finder = VietnameseSimilarityFinder(
        mongo_uri="mongodb://localhost:27017/",
        db_name="KB_PROPERTY_LAW",
        use_gpu=True
    )

    try:
        # Generate and store embeddings for all concepts and relations
        print("\n=== Generating Embeddings with GPU ===")
        finder.generate_and_store_concept_embeddings(batch_size=128)
        finder.generate_and_store_relation_embeddings(batch_size=128)

        # Find groups of similar concepts (FAST VERSION)
        print("\n" + "="*80)
        print("=== FINDING GROUPS OF SIMILAR CONCEPTS ===")
        print("="*80)
        
        concept_groups = finder.find_all_similar_groups(
            collection_name='concepts',
            min_similarity=0.7
        )

        # Find groups of similar relations (FAST VERSION)
        print("\n" + "="*80)
        print("=== FINDING GROUPS OF SIMILAR RELATIONS ===")
        print("="*80)
        
        relation_groups = finder.find_all_similar_groups(
            collection_name='relations',
            min_similarity=0.90
        )

        # Preview groups before merging
        print("\n" + "="*80)
        print("=== PREVIEW: TOP 10 CONCEPT GROUPS ===")
        print("="*80)
        for i, group in enumerate(concept_groups[:10], 1):
            print(f"\n{i}. {group['main']} ({len(group['similar'])} similar)")
            for sim in group['similar'][:3]:
                print(f"   📊 {sim['name']} (sim: {sim['similarity']:.3f})")

        print("\n" + "="*80)
        print("=== PREVIEW: TOP 10 RELATION GROUPS ===")
        print("="*80)
        for i, group in enumerate(relation_groups[:10], 1):
            print(f"\n{i}. {group['main']} ({len(group['similar'])} similar)")
            for sim in group['similar'][:3]:
                print(f"   📊 {sim['name']} (sim: {sim['similarity']:.3f})")

        # Merge concepts
        print("\n" + "="*80)
        print("=== MERGING SIMILAR CONCEPTS ===")
        print("="*80)
        
        concept_merge_stats = {
            'total_groups': len(concept_groups),
            'total_merged': 0,
            'total_triplets_updated': 0
        }
        
        for group in tqdm(concept_groups, desc="Merging concepts", unit="group"):
            result = finder.merge_concepts(group)
            concept_merge_stats['total_merged'] += result['merged']
            concept_merge_stats['total_triplets_updated'] += result['triplets_updated']
        
        print(f"\n✓ Merged {concept_merge_stats['total_merged']} concepts into {concept_merge_stats['total_groups']} groups")
        print(f"✓ Updated {concept_merge_stats['total_triplets_updated']} triplet references")

        # Merge relations
        print("\n" + "="*80)
        print("=== MERGING SIMILAR RELATIONS ===")
        print("="*80)
        
        relation_merge_stats = {
            'total_groups': len(relation_groups),
            'total_merged': 0,
            'total_triplets_updated': 0
        }
        
        for group in tqdm(relation_groups, desc="Merging relations", unit="group"):
            result = finder.merge_relations(group)
            relation_merge_stats['total_merged'] += result['merged']
            relation_merge_stats['total_triplets_updated'] += result['triplets_updated']
        
        print(f"\n✓ Merged {relation_merge_stats['total_merged']} relations into {relation_merge_stats['total_groups']} groups")
        print(f"✓ Updated {relation_merge_stats['total_triplets_updated']} triplet references")
        
        # Final summary statistics
        print("\n\n" + "="*80)
        print("=== FINAL SUMMARY ===")
        print("="*80)
        
        final_concept_count = finder.concepts.count_documents({})
        final_relation_count = finder.relations.count_documents({})
        total_triplets = finder.triplets.count_documents({})
        
        initial_concept_count = finder.concepts.count_documents({}) + concept_merge_stats['total_merged']
        initial_relation_count = finder.relations.count_documents({}) + relation_merge_stats['total_merged']
        
        print(f"\nCONCEPTS:")
        print(f"  Initial count: {initial_concept_count}")
        print(f"  Final count: {final_concept_count}")
        print(f"  Reduction: {initial_concept_count - final_concept_count} ({(initial_concept_count - final_concept_count) / initial_concept_count * 100:.1f}%)")
        print(f"  Groups merged: {concept_merge_stats['total_groups']}")
        print(f"  Triplets updated: {concept_merge_stats['total_triplets_updated']}")
        
        print(f"\nRELATIONS:")
        print(f"  Initial count: {initial_relation_count}")
        print(f"  Final count: {final_relation_count}")
        print(f"  Reduction: {initial_relation_count - final_relation_count} ({(initial_relation_count - final_relation_count) / initial_relation_count * 100:.1f}%)")
        print(f"  Groups merged: {relation_merge_stats['total_groups']}")
        print(f"  Triplets updated: {relation_merge_stats['total_triplets_updated']}")
        
        print(f"\nTRIPLETS:")
        print(f"  Total count: {total_triplets}")
        print(f"  Total references updated: {concept_merge_stats['total_triplets_updated'] + relation_merge_stats['total_triplets_updated']}")
        
    finally:
        # Cleanup
        finder.cleanup()
        print("\n✓ Cleanup completed")


if __name__ == "__main__":
    main()