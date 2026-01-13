from collections import defaultdict
from typing import List, Dict, Any, Tuple
from src.triplet_extraction.pos_taging import parsing_result
from src.utils import clean_text
from src.retrieval.graph.bm25_ranker import rank_sections_bm25, hybrid_rank

STOP_VERBS = {
    # Modal / permission / obligation
    "được", "phải", "cần", "nên", "không_được", "được_phép",

    # Aspect / tense
    "đã", "đang", "sẽ", "vừa", "mới",

    # Passive / causative
    "bị", "được_bị",

    # Copula / state
    "là", "là_phải", "trở_thành",

    # Existential / appearance
    "có", "có_thể", "có_thể_là",

    # Negation helpers
    "không", "chưa", "chẳng", "chớ",

    # Light verbs (semantically empty alone)
    "thực_hiện",
    "tiến_hành",
    "tiến_hành_việc",
    "đưa_ra",
    "đưa_vào",
    "tiếp_tục",
    "tiến_tới",

    # Discourse / logical glue
    "để", "nhằm", "theo", "về", "tại",

    # Result / completion helpers
    "xong", "hoàn_thành",
}


def extract_verbs(text: str, phoNLP_model) -> List[str]:
    """
    Extract semantic verbs from text using PhoNLP.
    """
    annotation = phoNLP_model.annotate(text=text)
    df = parsing_result(annotation)

    verbs = (
        df.loc[df["pos"] == "V", "word"]
        .str.lower()
        .tolist()
    )

    # remove stop verbs
    verbs = [v for v in verbs if v not in STOP_VERBS]

    return verbs


# ============================================================================
# MONGODB GRAPH-BASED MATCHING (REPLACES IN-MEMORY MATCHING)
# ============================================================================

def match_concepts_graph(
    tokens: List[str],
    concepts_col,
    max_phrase_length: int = 5
) -> List[Dict]:
    """
    Match concepts using MongoDB text search and regex
    More efficient than loading all concepts into memory

    Args:
        tokens: List of tokens to match
        concepts_col: MongoDB concepts collection
        max_phrase_length: Maximum phrase length to check

    Returns:
        List of matched concepts with position info
    """
    if not tokens:
        return []

    matched_concepts = []
    i = 0

    while i < len(tokens):
        best_match = None
        best_length = 0

        # Try phrases from longest to shortest
        for length in range(min(max_phrase_length, len(tokens) - i), 0, -1):
            phrase = " ".join(tokens[i:i + length])
            normalized_phrase = phrase.replace('_', ' ').lower()

            # MongoDB query with case-insensitive regex
            query = {
                '$or': [
                    {'name': {'$regex': normalized_phrase, '$options': 'i'}},
                    {'synonym': {'$regex': normalized_phrase, '$options': 'i'}}
                ]
            }

            matches = list(concepts_col.find(query))

            if matches:
                best_match = matches
                best_length = length
                break

        if best_match:
            for match in best_match:
                matched_concepts.append({
                    'position': i,
                    'matched_text': " ".join(tokens[i:i + best_length]),
                    'data': match
                })
            i += best_length
        else:
            i += 1

    return matched_concepts


def match_relations_graph(
    tokens: List[str],
    relations_col,
    max_phrase_length: int = 5
) -> List[Dict]:
    """
    Match relations using MongoDB text search and regex
    More efficient than loading all relations into memory

    Args:
        tokens: List of tokens to match
        relations_col: MongoDB relations collection
        max_phrase_length: Maximum phrase length to check

    Returns:
        List of matched relations with position info
    """
    if not tokens:
        return []

    matched_relations = []
    i = 0

    while i < len(tokens):
        best_match = None
        best_length = 0

        for length in range(min(max_phrase_length, len(tokens) - i), 0, -1):
            phrase = " ".join(tokens[i:i + length])
            normalized_phrase = phrase.replace('_', ' ').lower()

            query = {
                '$or': [
                    {'name': {'$regex': normalized_phrase, '$options': 'i'}},
                    {'synonym': {'$regex': normalized_phrase, '$options': 'i'}}
                ]
            }

            matches = list(relations_col.find(query))

            if matches:
                best_match = matches
                best_length = length
                break

        if best_match:
            for match in best_match:
                matched_relations.append({
                    'position': i,
                    'matched_text': " ".join(tokens[i:i + best_length]),
                    'data': match
                })
            i += best_length
        else:
            i += 1

    return matched_relations


# ============================================================================
# K-HOP NEIGHBORHOOD EXTRACTION USING MONGODB
# ============================================================================

def k_hop_traversal_mongo(
    seed_concept_ids: List[str],
    seed_relation_ids: List[str],
    triplets_col,
    concepts_col,
    k_hops: int = 2,
    max_concepts: int = 500
) -> Dict[str, Any]:
    """
    Extract k-hop neighborhood using MongoDB aggregation pipeline

    This performs graph traversal to find:
    1. All concepts connected to seed concepts within k hops
    2. All relations used in those connections
    3. All triplets in the subgraph

    Args:
        seed_concept_ids: Starting concept IDs
        seed_relation_ids: Relation IDs to filter paths (optional)
        triplets_col: MongoDB triplets collection
        concepts_col: MongoDB concepts collection
        k_hops: Number of hops to traverse (1-3 recommended)
        max_concepts: Maximum concepts to return (prevent explosion)

    Returns:
        Dictionary with expanded concepts, relations, and triplets
    """
    if not seed_concept_ids:
        return {
            'concepts': [],
            'relations': [],
            'triplets': [],
            'concept_ids': set(),
            'relation_ids': set()
        }

    print(f"\n=== K-HOP TRAVERSAL (k={k_hops}) ===")
    print(f"Seed concepts: {len(seed_concept_ids)}")
    print(f"Seed relations: {len(seed_relation_ids)}")

    # Track all discovered entities
    all_concept_ids = set(seed_concept_ids)
    all_relation_ids = set(seed_relation_ids)
    all_triplets = []

    current_concept_ids = set(seed_concept_ids)

    # Iterative k-hop expansion
    for hop in range(k_hops):
        print(f"\nHop {hop + 1}: Starting with {len(current_concept_ids)} concepts")

        if not current_concept_ids:
            break

        # Find all triplets connected to current concepts
        query = {
            '$or': [
                {'subject_id': {'$in': list(current_concept_ids)}},
                {'object_id': {'$in': list(current_concept_ids)}}
            ]
        }

        # Optionally filter by seed relations
        if seed_relation_ids and hop == 0:
            query['relation_id'] = {'$in': seed_relation_ids}

        hop_triplets = list(triplets_col.find(query))
        print(f"Found {len(hop_triplets)} triplets at hop {hop + 1}")

        # Extract new concepts and relations from triplets
        new_concept_ids = set()
        new_relation_ids = set()

        for triplet in hop_triplets:
            subject_id = triplet.get('subject_id')
            object_id = triplet.get('object_id')
            relation_id = triplet.get('relation_id')

            if subject_id:
                new_concept_ids.add(subject_id)
            if object_id:
                new_concept_ids.add(object_id)
            if relation_id:
                new_relation_ids.add(relation_id)

            all_triplets.append(triplet)

        # Update global sets
        previously_seen = len(all_concept_ids)
        all_concept_ids.update(new_concept_ids)
        all_relation_ids.update(new_relation_ids)

        print(f"Discovered {len(new_concept_ids)} unique concepts (new: {len(all_concept_ids) - previously_seen})")
        print(f"Total concepts so far: {len(all_concept_ids)}")

        # Prepare next hop (only expand from newly discovered concepts)
        current_concept_ids = new_concept_ids - current_concept_ids

        # Safety limit to prevent explosion
        if len(all_concept_ids) > max_concepts:
            print(f"\nWarning: Reached max concepts limit ({max_concepts}), stopping traversal")
            break

    # Fetch full concept documents
    concepts = list(concepts_col.find({'_id': {'$in': list(all_concept_ids)}}))

    print(f"\n=== TRAVERSAL COMPLETE ===")
    print(f"Total concepts: {len(all_concept_ids)}")
    print(f"Total relations: {len(all_relation_ids)}")
    print(f"Total triplets: {len(all_triplets)}")

    return {
        'concepts': concepts,
        'concept_ids': all_concept_ids,
        'relation_ids': all_relation_ids,
        'triplets': all_triplets
    }


def score_triplets_from_traversal(
    traversal_result: Dict[str, Any],
    seed_concept_ids: List[str],
    seed_relation_ids: List[str]
) -> Tuple[List[str], Dict[str, float]]:
    """
    Score sections based on triplets from k-hop traversal
    Assigns higher scores to triplets closer to seed entities

    Args:
        traversal_result: Result from k_hop_traversal_mongo
        seed_concept_ids: Original seed concepts
        seed_relation_ids: Original seed relations

    Returns:
        Tuple of (section_ids, section_scores)
    """
    triplets = traversal_result['triplets']

    if not triplets:
        return [], {}

    section_scores = defaultdict(lambda: {
        'score': 0,
        'triplet_count': 0,
        'seed_matches': 0,
        'neighbor_matches': 0
    })

    for triplet in triplets:
        subject_id = triplet.get('subject_id')
        object_id = triplet.get('object_id')
        relation_id = triplet.get('relation_id')
        documents = triplet.get('documents', [])
        
        # Fallback: handle old format with direct section_id
        if not documents and 'section_id' in triplet:
            documents = [{'section_id': triplet['section_id']}]

        # Calculate relevance score
        is_seed_subject = subject_id in seed_concept_ids
        is_seed_object = object_id in seed_concept_ids
        is_seed_relation = relation_id in seed_relation_ids

        # Scoring tiers
        if is_seed_subject and is_seed_object and is_seed_relation:
            triplet_score = 15  # Perfect match: seed-relation-seed
        elif (is_seed_subject or is_seed_object) and is_seed_relation:
            triplet_score = 10  # Seed concept with seed relation
        elif is_seed_subject and is_seed_object:
            triplet_score = 8   # Both seed concepts (any relation)
        elif is_seed_subject or is_seed_object:
            triplet_score = 5   # One seed concept (1-hop neighbor)
        else:
            triplet_score = 2   # 2+ hop neighbors

        # Apply score to all sections containing this triplet
        for doc in documents:
            section_id = doc.get('section_id')

            if section_id:
                section_scores[section_id]['score'] += triplet_score
                section_scores[section_id]['triplet_count'] += 1

                if is_seed_subject or is_seed_object:
                    section_scores[section_id]['seed_matches'] += 1
                else:
                    section_scores[section_id]['neighbor_matches'] += 1

    # Extract section IDs and scores
    section_ids = list(section_scores.keys())
    score_dict = {sid: section_scores[sid]['score'] for sid in section_ids}

    print(f"\n=== SECTION SCORING ===")
    print(f"Sections found: {len(section_ids)}")
    if score_dict:
        print(f"Score range: {min(score_dict.values()):.1f} - {max(score_dict.values()):.1f}")
    else:
        print("No sections scored")

    return section_ids, score_dict

def collect_sections_content(
    sections_col,
    section_ids: List[str]
) -> Dict[str, str]:
    """
    For each section_id:
      - walk parent_id upward until type == 'điều'
      - collect all content on the path

    Returns:
      { section_id: merged_content }
    """

    pipeline = [
        {
            "$match": {
                "_id": {"$in": section_ids}
            }
        },
        {
            "$graphLookup": {
                "from": sections_col.name,
                "startWith": "$parent_id",
                "connectFromField": "parent_id",
                "connectToField": "_id",
                "as": "ancestors",
                "depthField": "depth"
            }
        },
        {
            "$addFields": {
                "chain": {
                    "$concatArrays": [["$$ROOT"], "$ancestors"]
                }
            }
        },
        {
            "$project": {
                "_id": 1,
                "chain": 1
            }
        }
    ]

    docs = list(sections_col.aggregate(pipeline))

    result = {}

    for doc in docs:
        chain = doc["chain"]

        # sort bottom → top
        chain.sort(key=lambda x: x.get("depth", -1))

        contents = []
        for s in chain:
            if s.get("content"):
                contents.append(s["content"].strip())
            if s.get("type") == "điều":
                break

        result[str(doc["_id"])] = "\n".join(reversed(contents))

    return result

# ============================================================================
# MAIN RETRIEVAL AND RANKING WITH K-HOP TRAVERSAL
# ============================================================================

def retrieve_and_rank(
    question: str,
    vncorenlp_client,
    phoNLP_model,
    sections_col,
    concepts_col,
    relations_col,
    triplets_col,
    dpr_ranker = None,
    top_k: int = 10,
    use_khop: bool = True,
    k_hops: int = 2,
    use_hybrid: bool = True,
    use_dpr: bool = True,
    bm25_weight: float = 0.4,
    dpr_weight: float = 0.4,
    triplet_weight: float = 0.2,
    return_matches: bool = False
) -> Any:
    """
    Main graph function with k-hop graph traversal and Dense Passage Retrieval
    1. Text segmentation and verb extraction
    2. Graph-based concept/relation matching (MongoDB queries)
    3. K-hop neighborhood extraction (graph traversal)
    4. Triplet-based section graph
    5. Hybrid BM25 + graph scoring

    Args:
        question: User query
        vncorenlp_client: Vietnamese NLP client
        phoNLP_model: PhoNLP model
        sections_col: MongoDB sections collection
        concepts_col: MongoDB concepts collection
        relations_col: MongoDB relations collection
        triplets_col: MongoDB triplets collection
        top_k: Number of results to return
        use_khop: Whether to use k-hop expansion
        k_hops: Number of hops for graph traversal
        use_hybrid: Use hybrid BM25 + triplet scoring
        bm25_weight: Weight for BM25 score
        triplet_weight: Weight for triplet score
        return_matches: Return matched entities

    Returns:
        Ranked sections (and optionally matched concepts/relations)
    """
    print("="*80)
    print("LEGAL DOCUMENT RETRIEVAL WITH GRAPH TRAVERSAL")
    print("="*80)

    # Step 1: Clean and segment text
    cleaned_question = clean_text(question)
    segmented_text = vncorenlp_client.word_segment(cleaned_question)[0]
    segmented_tokens = segmented_text.split(" ")
    print(f"\nSegmented question: {segmented_text}")

    # Step 2: Extract verbs
    verbs = extract_verbs(segmented_text, phoNLP_model)
    print(f"Extracted verbs: {verbs}")

    # Step 3: Graph-based relation matching (from verbs)
    matched_relations = match_relations_graph(
        verbs,
        relations_col,
        max_phrase_length=1
    )
    print(f"\nMatched {len(matched_relations)} relations")
    if matched_relations:
        for match in matched_relations:
            print(f"  '{match['matched_text']}' → {match['data']['name']}")

    # Step 4: Context-aware concept matching (words around verbs)
    window_size = 2
    concept_search_tokens = set()

    for match in matched_relations:
        verb_pos = match['position']
        start = max(0, verb_pos - window_size)
        end = min(len(segmented_tokens), verb_pos + window_size + 1)
        concept_search_tokens.update(segmented_tokens[start:end])

    # Fallback: if no relations matched, search all tokens
    if not concept_search_tokens:
        concept_search_tokens = set(segmented_tokens)

    print(f"\nTokens for concept search: {len(concept_search_tokens)} tokens")

    # Graph-based concept matching
    matched_concepts = match_concepts_graph(
        list(concept_search_tokens),
        concepts_col,
        max_phrase_length=3
    )
    print(f"Matched {len(matched_concepts)} concepts")
    if matched_concepts:
        for match in matched_concepts[:5]:  # Show first 5
            print(f"  '{match['matched_text']}' → {match['data']['name']}")
        if len(matched_concepts) > 5:
            print(f"  ... and {len(matched_concepts) - 5} more")

    # Extract IDs for graph traversal
    seed_concept_ids = [match['data']['_id'] for match in matched_concepts]
    seed_relation_ids = [match['data']['_id'] for match in matched_relations]

    # Step 5: K-hop neighborhood extraction (GRAPH TRAVERSAL)
    if use_khop and (seed_concept_ids or seed_relation_ids):
        traversal_result = k_hop_traversal_mongo(
            seed_concept_ids=seed_concept_ids,
            seed_relation_ids=seed_relation_ids,
            triplets_col=triplets_col,
            concepts_col=concepts_col,
            k_hops=k_hops,
            max_concepts=500
        )

        # Score sections from expanded graph
        triplet_section_ids, triplet_scores = score_triplets_from_traversal(
            traversal_result,
            seed_concept_ids,
            seed_relation_ids
        )
    else:
        # Direct triplet matching (no k-hop expansion)
        print("\n=== DIRECT TRIPLET MATCHING (NO K-HOP) ===")
        triplet_section_ids, triplet_scores = retrieve_triplet_sections_direct(
            matched_concepts,
            matched_relations,
            triplets_col
        )

    print(f"\nFound {len(triplet_section_ids)} candidate sections")

    # Step 6: Fetch section documents
    if triplet_section_ids:
        # section_id from triplets is a hash string, not MongoDB _id
        sections = list(sections_col.find({'section_id': {'$in': triplet_section_ids}}))
        
        # Fallback: try _id if section_id field doesn't exist
        if not sections:
            sections = list(sections_col.find({'_id': {'$in': triplet_section_ids}}))
    else:
        print("No triplet matches found, using all sections for BM25 ranking")
        sections = list(sections_col.find({}).limit(1000))

    sections_content = collect_sections_content(sections_col, [str(s['_id']) for s in sections])
    for section in sections:
        section['content'] = sections_content[section['_id']]

    print(f"Fetched {len(sections)} sections for ranking")

    if not sections:
        return ([], matched_concepts, matched_relations) if return_matches else []



    # Step 7: Hybrid ranking (BM25 + DPR + Graph scores)
    if use_hybrid and use_dpr:
        print(f"\n=== TWO-STAGE RANKING: BM25+Triplet → DPR ===")
        
        # Stage 1: BM25+Triplet to get top 100 candidates (fast)
        print(f"\nStage 1: BM25+Triplet ranking for all {len(sections)} sections...")
        stage1_candidates = hybrid_rank(
            cleaned_question,
            sections,
            vncorenlp_client,
            triplet_scores=triplet_scores,
            top_k=min(100, len(sections)),
            bm25_weight=0.6,
            triplet_weight=0.4
        )
        print(f"Selected top {len(stage1_candidates)} candidates for DPR")
        
        # Stage 2: Apply DPR only on top candidates (expensive but accurate)
        print(f"\nStage 2: Applying DPR to re-rank top {len(stage1_candidates)} candidates...")
        
        from src.retrieval.graph.dpr_ranker import rank_sections_dpr
        
        # Get DPR scores for candidates only
        dpr_results = rank_sections_dpr(
            cleaned_question,
            stage1_candidates,
            dpr_ranker=dpr_ranker,
            top_k=len(stage1_candidates)
        )
        
        # Create DPR score lookup
        dpr_scores_dict = {r['section_id']: r['dpr_score'] for r in dpr_results}
        
        # Combine all three scores with proper weights
        print(f"\nStage 3: Computing final hybrid scores...")
        print(f"Weights: BM25={bm25_weight}, DPR={dpr_weight}, Triplet={triplet_weight}")
        
        # Get max scores for normalization
        bm25_scores = {r['section_id']: r.get('bm25_score', 0.0) for r in stage1_candidates}
        max_bm25 = max(bm25_scores.values()) if bm25_scores else 1.0
        max_dpr = max(dpr_scores_dict.values()) if dpr_scores_dict else 1.0
        max_triplet = max(triplet_scores.values()) if triplet_scores else 1.0
        
        if max_bm25 == 0: max_bm25 = 1.0
        if max_dpr == 0: max_dpr = 1.0
        if max_triplet == 0: max_triplet = 1.0
        
        # Compute final hybrid scores
        for candidate in stage1_candidates:
            section_id = candidate['section_id']
            
            norm_bm25 = bm25_scores.get(section_id, 0.0) / max_bm25
            norm_dpr = dpr_scores_dict.get(section_id, 0.0) / max_dpr
            norm_triplet = triplet_scores.get(section_id, 0.0) / max_triplet
            
            candidate['dpr_score'] = dpr_scores_dict.get(section_id, 0.0)
            candidate['triplet_score'] = triplet_scores.get(section_id, 0.0)
            candidate['normalized_bm25'] = norm_bm25
            candidate['normalized_dpr'] = norm_dpr
            candidate['normalized_triplet'] = norm_triplet
            candidate['hybrid_score'] = (
                bm25_weight * norm_bm25 +
                dpr_weight * norm_dpr +
                triplet_weight * norm_triplet
            )
        
        # Sort by final hybrid score
        stage1_candidates.sort(key=lambda x: x['hybrid_score'], reverse=True)
        ranked_sections = stage1_candidates[:top_k]
        
        # Update ranks
        for rank, section in enumerate(ranked_sections, 1):
            section['rank'] = rank
            
    elif use_hybrid and triplet_scores:
        print(f"\n=== HYBRID RANKING (BM25 + Triplet) ===")
        print(f"BM25 weight: {bm25_weight}")
        print(f"Triplet weight: {triplet_weight}")
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
        print("\n=== BM25-ONLY RANKING ===")
        ranked_sections = rank_sections_bm25(
            cleaned_question,
            sections,
            vncorenlp_client,
            top_k=top_k
        )

    print(f"\nReturning top {len(ranked_sections)} results")

    if return_matches:
        return ranked_sections, matched_concepts, matched_relations
    return ranked_sections


def retrieve_triplet_sections_direct(
    matched_concepts: List[Dict],
    matched_relations: List[Dict],
    triplets_col
) -> Tuple[List[str], Dict[str, float]]:
    """
    Direct triplet matching without k-hop expansion (original method)

    Args:
        matched_concepts: Matched concept dictionaries
        matched_relations: Matched relation dictionaries
        triplets_col: MongoDB triplets collection

    Returns:
        Tuple of (section_ids, section_scores)
    """
    concept_ids = [match['data']['_id'] for match in matched_concepts]
    relation_ids = [match['data']['_id'] for match in matched_relations]

    query_conditions = []

    if concept_ids:
        query_conditions.append({
            '$or': [
                {'subject_id': {'$in': concept_ids}},
                {'object_id': {'$in': concept_ids}}
            ]
        })

    if relation_ids:
        query_conditions.append({'relation_id': {'$in': relation_ids}})

    if not query_conditions:
        return [], {}

    query = {'$or': query_conditions} if len(query_conditions) > 1 else query_conditions[0]
    matched_triplets = list(triplets_col.find(query))

    if not matched_triplets:
        return [], {}

    section_scores = defaultdict(float)

    for triplet in matched_triplets:
        documents = triplet.get('documents', [])
        has_subject = triplet.get('subject_id') in concept_ids
        has_object = triplet.get('object_id') in concept_ids
        has_relation = triplet.get('relation_id') in relation_ids

        if has_subject and has_object and has_relation:
            triplet_score = 10
        elif (has_subject or has_object) and has_relation:
            triplet_score = 5
        elif has_subject and has_object:
            triplet_score = 4
        elif has_subject or has_object:
            triplet_score = 2
        else:
            triplet_score = 1

        for doc in documents:
            section_id = doc.get('section_id')
            if section_id:
                section_scores[section_id] += triplet_score

    section_ids = list(section_scores.keys())
    return section_ids, dict(section_scores)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def print_matched_concepts_relations(
    matched_concepts: List[Dict[str, Any]],
    matched_relations: List[Dict[str, Any]]
):
    """Print matched concepts and relations in detail"""
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
                print(f"     → Synonyms: {', '.join(synonyms[:3])}")
    else:
        print("\nNo concepts matched.")

    if matched_relations:
        print(f"\nMatched {len(matched_relations)} Relations:")
        for idx, match in enumerate(matched_relations, 1):
            print(f"\n  {idx}. Position {match['position']}: '{match['matched_text']}'")
            print(f"     → Relation Name: {match['data']['name']}")
            print(f"     → Relation ID: {match['data']['_id']}")
    else:
        print("\nNo relations matched.")

    print("\n" + "="*80)


def display_results(ranked_sections: List[Dict[str, Any]], sections_col):
    """Display ranked results in a formatted way"""
    print("\n" + "="*80)
    print("=== RANKED RESULTS ===")
    print("="*80)

    for idx, section in enumerate(ranked_sections, 1):
        print(f"\n--- Rank {idx} ---")
        print(f"Section ID: {section.get('section_id')}")

        if 'hybrid_score' in section:
            print(f"Hybrid Score: {section['hybrid_score']:.4f}")
            print(f"  - BM25: {section['bm25_score']:.4f} (normalized: {section['normalized_bm25']:.4f})")
            print(f"  - Triplet: {section.get('triplet_score', 0)} (normalized: {section['normalized_triplet']:.4f})")
        else:
            print(f"BM25 Score: {section['bm25_score']:.4f}")

        section_doc = sections_col.find_one({'_id': section['section_id']})
        if section_doc:
            full_path = section_doc.get('full_path', 'N/A')
            content = section_doc.get('content', '')
            preview = content[:200] + "..." if len(content) > 200 else content

            print(f"Full Path: {full_path}")
            print(f"Content Preview: {preview}")