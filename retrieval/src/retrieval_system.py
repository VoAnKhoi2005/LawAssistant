"""
Legal Document Retrieval System
Combines verb extraction, concept/relation matching, triplet retrieval, and BM25 ranking
"""

import os
from collections import defaultdict
from typing import List, Dict, Any, Tuple
from triplet_extraction.src.db import init_mongo
from triplet_extraction.src.triplet_extraction import clean_text, parsing_result
from retrieval.src.bm25_ranker import rank_sections_bm25, hybrid_rank


def extract_verbs(text: str, phoNLP_model) -> List[Dict[str, Any]]:
    """
    Extract main verbs from question using PhoNLP
    
    Args:
        text: Input text
        phoNLP_model: PhoNLP model instance
        
    Returns:
        List of verb dictionaries with word, pos, and dependency info
    """
    annotation = phoNLP_model.annotate(text=text)
    df = parsing_result(annotation)
    
    # Extract verbs (POS tag = 'V')
    verbs = df[df['pos'] == 'V'].to_dict('records')
    
    return verbs


def find_matches(word: str, items: List[Dict]) -> List[Dict]:
    """
    Find items where word matches the name or any synonym
    Uses case-insensitive substring search after replacing underscores with spaces
    
    Args:
        word: Word to match
        items: List of concepts or relations
        
    Returns:
        List of matching items
    """
    matches = []
    # Normalize query word: replace underscore with space, lowercase
    normalized_word = word.replace('_', ' ').lower()
    
    for item in items:
        # Normalize item name
        item_name = item.get('name', '').replace('_', ' ').lower()
        
        # Check if normalized word is substring of normalized item name or vice versa
        if normalized_word in item_name or item_name in normalized_word:
            matches.append(item)
            continue
        
        # Check match in synonyms array
        synonyms = item.get('synonyms', []) or item.get('synonym', [])
        if isinstance(synonyms, list):
            for syn in synonyms:
                if isinstance(syn, str):
                    normalized_syn = syn.replace('_', ' ').lower()
                    if normalized_word in normalized_syn or normalized_syn in normalized_word:
                        matches.append(item)
                        break
    
    return matches


def find_phrase_matches(segmented_text: List[str], start_idx: int, max_length: int, items: List[Dict]) -> Tuple[List[Dict], int]:
    """
    Check for matches starting from start_idx for phrases up to max_length words
    
    Args:
        segmented_text: List of tokens
        start_idx: Starting index
        max_length: Maximum phrase length to check
        items: List of concepts or relations
        
    Returns:
        Tuple of (matched_items, phrase_length)
    """
    best_match = None
    best_length = 0
    
    # Try phrases from longest to shortest
    for length in range(min(max_length, len(segmented_text) - start_idx), 0, -1):
        phrase = " ".join(segmented_text[start_idx:start_idx + length])
        matches = find_matches(phrase, items)
        
        if matches:
            if length > best_length:
                best_match = matches
                best_length = length
    
    return best_match, best_length


def match_concepts_and_relations(
    segmented_text: List[str],
    all_concepts: List[Dict],
    all_relations: List[Dict],
    max_phrase_length: int = 5
) -> Tuple[List[Dict], List[Dict]]:
    """
    Match concepts and relations in segmented text
    
    Args:
        segmented_text: List of tokens
        all_concepts: All available concepts
        all_relations: All available relations
        max_phrase_length: Maximum phrase length to check
        
    Returns:
        Tuple of (matched_concepts, matched_relations)
    """
    matched_concepts = []
    matched_relations = []
    i = 0
    
    while i < len(segmented_text):
        # Try to match phrases (multi-word)
        concept_matches, concept_length = find_phrase_matches(
            segmented_text, i, max_phrase_length, all_concepts
        )
        relation_matches, relation_length = find_phrase_matches(
            segmented_text, i, max_phrase_length, all_relations
        )
        
        # Prioritize longer matches
        if concept_length > 0 or relation_length > 0:
            if concept_length >= relation_length:
                for match in concept_matches:
                    matched_concepts.append({
                        'position': i,
                        'matched_text': " ".join(segmented_text[i:i + concept_length]),
                        'data': match
                    })
                i += concept_length
            else:
                for match in relation_matches:
                    matched_relations.append({
                        'position': i,
                        'matched_text': " ".join(segmented_text[i:i + relation_length]),
                        'data': match
                    })
                i += relation_length
        else:
            i += 1
    
    return matched_concepts, matched_relations


def retrieve_triplet_sections(
    matched_concepts: List[Dict],
    matched_relations: List[Dict],
    triplets_col
) -> Tuple[List[str], Dict[str, float]]:
    """
    Retrieve relevant section IDs based on triplet matching
    
    Args:
        matched_concepts: Matched concept dictionaries
        matched_relations: Matched relation dictionaries
        triplets_col: MongoDB triplets collection
        
    Returns:
        Tuple of (section_ids, section_scores)
    """
    # Extract IDs from matches
    concept_ids = [match['data']['_id'] for match in matched_concepts]
    relation_ids = [match['data']['_id'] for match in matched_relations]
    
    # Build query
    query_conditions = []
    
    # Match triplets with concepts as subject or object
    if concept_ids:
        query_conditions.append({
            '$or': [
                {'subject_id': {'$in': concept_ids}},
                {'object_id': {'$in': concept_ids}}
            ]
        })
    
    # Match triplets with relations
    if relation_ids:
        query_conditions.append({'relation_id': {'$in': relation_ids}})
    
    # Combine queries
    if not query_conditions:
        return [], {}
    
    query = {'$or': query_conditions} if len(query_conditions) > 1 else query_conditions[0]
    
    # Query triplets
    matched_triplets = list(triplets_col.find(query))
    
    if not matched_triplets:
        return [], {}
    
    # Score sections based on triplet matches
    section_scores = defaultdict(lambda: {
        'score': 0,
        'triplet_count': 0,
        'concept_matches': 0,
        'relation_matches': 0,
        'full_triplet_matches': 0
    })
    
    for triplet in matched_triplets:
        documents = triplet.get('documents', [])
        
        # Check match type
        has_subject = triplet.get('subject_id') in concept_ids
        has_object = triplet.get('object_id') in concept_ids
        has_relation = triplet.get('relation_id') in relation_ids
        
        # Calculate base score for this triplet
        triplet_score = 0
        if has_subject and has_object and has_relation:
            triplet_score = 10  # Full triplet match
        elif (has_subject or has_object) and has_relation:
            triplet_score = 5   # Concept + relation match
        elif has_subject and has_object:
            triplet_score = 4   # Both concepts match
        elif has_subject or has_object:
            triplet_score = 2   # Single concept match
        elif has_relation:
            triplet_score = 1   # Relation only match
        
        # Update scores for each document/section
        for doc in documents:
            section_id = doc.get('section_id')
            
            if section_id:
                section_scores[section_id]['score'] += triplet_score
                section_scores[section_id]['triplet_count'] += 1
                
                if has_subject or has_object:
                    section_scores[section_id]['concept_matches'] += 1
                if has_relation:
                    section_scores[section_id]['relation_matches'] += 1
                if has_subject and has_object and has_relation:
                    section_scores[section_id]['full_triplet_matches'] += 1
    
    # Extract section IDs and scores
    section_ids = list(section_scores.keys())
    score_dict = {sid: section_scores[sid]['score'] for sid in section_ids}
    
    return section_ids, score_dict


def retrieve_and_rank(
    question: str,
    vncorenlp_client,
    phoNLP_model,
    sections_col,
    concepts_col,
    relations_col,
    triplets_col,
    top_k: int = 10,
    use_hybrid: bool = True,
    bm25_weight: float = 0.6,
    triplet_weight: float = 0.4,
    return_matches: bool = False
) -> Any:
    """
    Complete retrieval and ranking pipeline
    
    Args:
        question: User question
        vncorenlp_client: VnCoreNLP client
        phoNLP_model: PhoNLP model
        sections_col: MongoDB sections collection
        concepts_col: MongoDB concepts collection
        relations_col: MongoDB relations collection
        triplets_col: MongoDB triplets collection
        top_k: Number of results to return
        use_hybrid: Whether to use hybrid ranking (BM25 + triplet)
        bm25_weight: Weight for BM25 in hybrid ranking
        triplet_weight: Weight for triplet score in hybrid ranking
        return_matches: If True, return (ranked_sections, matched_concepts, matched_relations)
        
    Returns:
        List of ranked sections with scores, or tuple if return_matches=True
    """
    # Step 1: Clean and segment text
    cleaned_question = clean_text(question)
    segmented_text = vncorenlp_client.word_segment(cleaned_question)[0]
    print(f"Segmented question: {segmented_text}")
    
    # Step 2: Extract verbs
    verbs = extract_verbs(segmented_text, phoNLP_model)
    print(f"\nExtracted verbs: {[v['word'] for v in verbs]}")
    
    # Step 3: Match concepts and relations
    segmented_tokens = segmented_text.split(" ")
    all_concepts = list(concepts_col.find({}))
    all_relations = list(relations_col.find({}))
    
    matched_concepts, matched_relations = match_concepts_and_relations(
        segmented_tokens, all_concepts, all_relations
    )
    
    print(f"\nMatched {len(matched_concepts)} concepts and {len(matched_relations)} relations")
    
    # Print matched concepts
    if matched_concepts:
        print("\nMatched Concepts:")
        for match in matched_concepts:
            print(f"  Position {match['position']}: '{match['matched_text']}' → {match['data']['name']}")
    
    # Print matched relations
    if matched_relations:
        print("\nMatched Relations:")
        for match in matched_relations:
            print(f"  Position {match['position']}: '{match['matched_text']}' → {match['data']['name']}")
    
    # Step 4: Retrieve sections via triplet matching
    triplet_section_ids, triplet_scores = retrieve_triplet_sections(
        matched_concepts, matched_relations, triplets_col
    )
    
    print(f"\nFound {len(triplet_section_ids)} candidate sections from triplet matching")
    
    # Step 5: Fetch section documents
    if triplet_section_ids:
        sections = list(sections_col.find({'_id': {'$in': triplet_section_ids}}))
    else:
        # Fallback: use all sections (or limit to a reasonable number)
        print("No triplet matches found, using all sections for BM25 ranking")
        sections = list(sections_col.find({}).limit(1000))
    
    print(f"Fetched {len(sections)} sections for ranking")
    
    if not sections:
        return ([], matched_concepts, matched_relations) if return_matches else []
    
    # Step 6: Rank using BM25 or hybrid approach
    if use_hybrid and triplet_scores:
        print(f"\nUsing hybrid ranking (BM25: {bm25_weight}, Triplet: {triplet_weight})")
        ranked_sections = hybrid_rank(
            cleaned_question,
            sections,
            vncorenlp_client,
            triplet_scores=triplet_scores,
            top_k=top_k,
            bm25_weight=bm25_weight,
            triplet_weight=triplet_weight
        )
    else:
        print("\nUsing BM25-only ranking")
        ranked_sections = rank_sections_bm25(
            cleaned_question,
            sections,
            vncorenlp_client,
            top_k=top_k
        )
    
    if return_matches:
        return ranked_sections, matched_concepts, matched_relations
    return ranked_sections


def print_matched_concepts_relations(
    matched_concepts: List[Dict[str, Any]],
    matched_relations: List[Dict[str, Any]]
):
    """
    Print matched concepts and relations in detail
    
    Args:
        matched_concepts: List of matched concept dictionaries
        matched_relations: List of matched relation dictionaries
    """
    print("\n" + "="*80)
    print("=== MATCHED CONCEPTS AND RELATIONS ===")
    print("="*80)
    
    if matched_concepts:
        print(f"\nMatched {len(matched_concepts)} Concepts:")
        for idx, match in enumerate(matched_concepts, 1):
            print(f"\n  {idx}. Position {match['position']}: '{match['matched_text']}'")
            print(f"     → Concept Name: {match['data']['name']}")
            print(f"     → Concept ID: {match['data']['_id']}")
            synonyms = match['data'].get('synonyms', []) or match['data'].get('synonym', [])
            if synonyms:
                print(f"     → Synonyms: {', '.join(synonyms)}")
    else:
        print("\nNo concepts matched.")
    
    if matched_relations:
        print(f"\nMatched {len(matched_relations)} Relations:")
        for idx, match in enumerate(matched_relations, 1):
            print(f"\n  {idx}. Position {match['position']}: '{match['matched_text']}'")
            print(f"     → Relation Name: {match['data']['name']}")
            print(f"     → Relation ID: {match['data']['_id']}")
            synonyms = match['data'].get('synonyms', []) or match['data'].get('synonym', [])
            if synonyms:
                print(f"     → Synonyms: {', '.join(synonyms)}")
    else:
        print("\nNo relations matched.")
    
    print("\n" + "="*80)


def display_results(ranked_sections: List[Dict[str, Any]], sections_col):
    """
    Display ranked results in a formatted way
    
    Args:
        ranked_sections: List of ranked section dictionaries
        sections_col: MongoDB sections collection to fetch full content
    """
    print("\n" + "="*80)
    print("=== RANKED RESULTS ===")
    print("="*80)
    
    for idx, section in enumerate(ranked_sections, 1):
        print(f"\n--- Rank {idx} ---")
        print(f"Section ID: {section.get('section_id')}")
        
        # Display scores
        if 'hybrid_score' in section:
            print(f"Hybrid Score: {section['hybrid_score']:.4f}")
            print(f"  - BM25 Score: {section['bm25_score']:.4f} (normalized: {section['normalized_bm25']:.4f})")
            print(f"  - Triplet Score: {section.get('triplet_score', 0)} (normalized: {section['normalized_triplet']:.4f})")
        else:
            print(f"BM25 Score: {section['bm25_score']:.4f}")
        
        # Fetch and display content
        section_doc = sections_col.find_one({'_id': section['section_id']})
        if section_doc:
            full_path = section_doc.get('full_path', 'N/A')
            content = section_doc.get('content', '')
            preview = content[:200] + "..." if len(content) > 200 else content
            
            print(f"Full Path: {full_path}")
            print(f"Content Preview: {preview}")
