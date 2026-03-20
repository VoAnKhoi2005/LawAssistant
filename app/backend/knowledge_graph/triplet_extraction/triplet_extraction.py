from src.triplet_extraction.pos_taging import parsing_result
from src.utils import clean_text

def parse_dataframe_to_tokens(df):
    """Convert DataFrame to a list of token dicts"""
    tokens = []
    for _, row in df.iterrows():
        token = {
            'id': int(row['id']),
            'word': str(row['word']),
            'pos': str(row['pos']),
            'head': int(row['head']),
            'deprel': str(row['deprel'])
        }
        tokens.append(token)
    return tokens


def split_sentence_np_vp(tokens):
    if not tokens:
        return [], []

    root_index = -1
    root_id = None

    # Find the main verb (root or first valid verb)
    for i, token in enumerate(tokens):
        if token['pos'] in ['V', 'R']:
            if token['deprel'] == 'root' and token['head'] == 0:
                # Avoid picking verb at start (index 0)
                if i == 0:
                    continue
                root_index = i
                root_id = token['id']
                break
            elif root_index == -1 and token['deprel'] != 'nmod':
                # Avoid first word if it's a verb
                if i == 0:
                    continue
                root_index = i
                root_id = token['id']

    # Fallback – pick next verb if root not found
    if root_index == -1:
        for i, token in enumerate(tokens):
            if token['pos'] == 'V' and i > 0:  # skip first position
                root_index = i
                root_id = token['id']
                break

    # Final split
    if root_index != -1 and root_id is not None:
        np_tokens = tokens[:root_index]
        vp_tokens = tokens[root_index:]
        return np_tokens, vp_tokens

    return [], []

def collect_dependents(tokens, head_id):
    """Return set of token ids: head_id + all recursive dependents"""
    subtree = {head_id}
    result = []
    added = True
    while added:
        added = False
        for token in tokens:
            if token['head'] in subtree and token['id'] not in subtree:
                subtree.add(token['id'])
                result.append(token)
                added = True
    return result


def collect_direct_dependents(tokens, head_id):
    """Return list of token dicts that directly depend on head_id"""
    return [t for t in tokens if t['head'] == head_id]


def rebuild_phrase(tokens):
    """Sort tokens by their original position in the sentence and join them together"""
    tokens_sorted = sorted(tokens, key=lambda x: x['id'])
    phrase = " ".join(t['word'] for t in tokens_sorted if t['word'].strip())
    return phrase

def extract_main_subjects(np_tokens):
    # Remove leading V tokens
    while np_tokens and np_tokens[0]['pos'] == 'V':
        np_tokens = np_tokens[1:]

    if not np_tokens:
        return []

    sub_tokens = [t for t in np_tokens if t['deprel'] == 'sub']
    if not sub_tokens:
        sub_tokens = [t for t in np_tokens if t['deprel'] == 'root']
    if not sub_tokens:
        return []

    main_subjects = [sub_tokens[0]]
    main_subjects.extend(collect_direct_dependents(np_tokens, sub_tokens[0]['id']))
    if main_subjects and main_subjects[-1]['pos'] in ['Cc', 'CH']:
        main_subjects.pop()
    if len(main_subjects) == len(np_tokens):
        return [rebuild_phrase(np_tokens)]

    # Find Coordination Word (Cc, CH)
    coord_tokens = [t for t in np_tokens if (t['pos'] in ['Cc', 'CH'] and t not in main_subjects)]
    non_main_tokens = set()
    if len(coord_tokens) > 0:
        phrases = []

        for coord in coord_tokens:
            coord_index = next((i for i, t in enumerate(np_tokens) if t['id'] == coord['id']), None)

            left_tokens = []
            main_subjects_id = [obj['id'] for obj in main_subjects]
            for i in range(coord_index - 1, -1, -1):
                token = np_tokens[i]
                if token['pos'] not in ['CH', 'Cc'] and token['id'] not in main_subjects_id:
                    left_tokens.append(token)
                    non_main_tokens.add(token['id'])
                else:
                    break

            right_tokens = []
            for i in range(coord_index + 1, len(np_tokens)):
                token = np_tokens[i]
                if token['pos'] not in ['CH', 'Cc']:
                    right_tokens.append(token)
                    non_main_tokens.add(token['id'])
                else:
                    break

            if left_tokens:
                phrases.append(rebuild_phrase(left_tokens))
            if right_tokens:
                phrases.append(rebuild_phrase(right_tokens))

        # Remove duplicates while preserving order
        phrases = list(dict.fromkeys(phrases))

        for sub in main_subjects:
            if sub['id'] in non_main_tokens:
                main_subjects.remove(sub)
        main_subject_phrase = rebuild_phrase(main_subjects)

        # Properly combine main subject with each phrase
        combined_phrases = []
        for phrase in phrases:
            combined_phrases.append(main_subject_phrase + " " + phrase)

        if not combined_phrases:
            return [main_subject_phrase]

        return combined_phrases
    else:
        return [rebuild_phrase(np_tokens)]

def extract_verbs(vp_tokens):
    if not vp_tokens:
        return [], []

    # Find the root verb first
    root_verb = None
    for t in vp_tokens:
        if t['deprel'] == 'root' and t['head'] == 0 and t['pos'] in ['V', 'R']:
            root_verb = t
            break

    # Fallback to the first verb that not nmod or aux
    if not root_verb:
        for t in vp_tokens:
            if t['pos'] == 'V' and t['deprel'] not in ['nmod', 'aux']:
                root_verb = t
                break

    # Fallback to any first verb in vp_tokens
    if not root_verb:
        for t in vp_tokens:
            if t['pos'] == 'V':
                root_verb = t
                break

    if not root_verb:
        return [vp_tokens[0]['word']], [vp_tokens[0]]

    # Check for coordination markers (CH, Cc) that are direct dependents of root
    coord_markers = [t for t in vp_tokens if t['pos'] in ['Cc', 'CH'] and t['head'] == root_verb['id']]

    if coord_markers:
        coordinated_verbs = [root_verb]
        for t in vp_tokens:
            if t['pos'] == 'V' and t['head'] == root_verb['id'] and t['deprel'] in ['vmod', 'conj']:
                coordinated_verbs.append(t)

        # Sort by ID to maintain order
        coordinated_verbs.sort(key=lambda x: x['id'])

        verb_phrases = []
        all_tokens = []
        coordinated_verbs_id = [v['id'] for v in coordinated_verbs]
        for verb in coordinated_verbs:
            phrase_tokens = [verb]
            dependents = collect_direct_dependents(vp_tokens, verb['id'])

            # Keep only dependents that are not other coordinated verbs or coordination markers
            dependents = [d for d in dependents if
                          d['id'] not in coordinated_verbs_id
                          and d['pos'] not in ['CH', 'Cc']
                          and d['deprel'] == 'vmod']

            phrase_tokens.extend(dependents)
            all_tokens.extend(phrase_tokens)

            verb_phrases.append({
                'text': rebuild_phrase(phrase_tokens),
                'tokens': phrase_tokens
            })

        return verb_phrases, all_tokens

    # Single verb: return it with its dependents (recursively collect verb chains)
    verb_tokens = [root_verb]
    
    # Recursively collect all vmod dependents to capture full verb chains
    def collect_verb_chain(verb_id, tokens):
        chain = []
        for t in tokens:
            if t['head'] == verb_id and t['deprel'] == 'vmod' and t['pos'] == 'V':
                chain.append(t)
                # Recursively collect further verb dependents
                chain.extend(collect_verb_chain(t['id'], tokens))
        return chain
    
    verb_tokens.extend(collect_verb_chain(root_verb['id'], vp_tokens))
    sorted_verb_tokens = sorted(verb_tokens, key=lambda x: x['id'])
    
    # Don't filter out tokens - keep the full verb chain
    return [{
        'text': rebuild_phrase(sorted_verb_tokens),
        'tokens': sorted_verb_tokens
    }], sorted_verb_tokens

def extract_objects(vp_tokens, verb_token):
    # Remove verb tokens from vp_tokens (make a copy to avoid modifying during iteration)
    vp_tokens = [t for t in vp_tokens if t['id'] not in [v['id'] for v in verb_token]]

    if not vp_tokens:
        return []

    obj_token = None

    # Find the first object token (dob, iob, pob)
    # obj_token = next((t for t in vp_tokens if t['deprel'] in ['dob', 'iob', 'pob']), None)

    # Fallback to the first noun in vp_tokens
    if obj_token is None:
        obj_token = next((t for t in vp_tokens if t['pos'] == 'N'), None)

    if obj_token is None:
        obj_token = next((t for t in vp_tokens if (t['deprel'] == 'vmod' or t['pos'] == 'A')), None)

    if obj_token is None:
        return []

    # Collect main object and its dependents
    main_objects = [obj_token]
    main_objects.extend(collect_direct_dependents(vp_tokens, obj_token['id']))

    if len(main_objects) == len(vp_tokens):
        return [{
            'text': rebuild_phrase(vp_tokens),
            'tokens': vp_tokens
        }]

    coord_tokens = [
        t for i, t in enumerate(vp_tokens)
        if t['pos'] in ['Cc', 'CH'] and i < len(vp_tokens) - 1
    ]
    for obj in main_objects:
        if obj in coord_tokens:
            main_objects = []
            break

    if coord_tokens:
        combined_phrases = []

        for coord in coord_tokens:
            coord_index = next((i for i, t in enumerate(vp_tokens) if t['id'] == coord['id']), None)

            # LEFT TOKENS
            left_tokens = []
            for i in range(coord_index - 1, -1, -1):
                token = vp_tokens[i]
                if token['pos'] not in ['CH', 'Cc'] and token['id'] not in [obj['id'] for obj in main_objects]:
                    left_tokens.append(token)
                else:
                    break
            left_tokens = left_tokens[::-1]

            # RIGHT TOKENS
            right_tokens = []
            for i in range(coord_index + 1, len(vp_tokens)):
                token = vp_tokens[i]
                if token['pos'] not in ['CH', 'Cc']:
                    right_tokens.append(token)
                else:
                    break

            # Combine main object with left and right tokens
            for tokens_side in [left_tokens, right_tokens]:
                if tokens_side:
                    combined_phrases.append({
                        'text': rebuild_phrase(main_objects) + " " + rebuild_phrase(tokens_side),
                        'tokens': main_objects + tokens_side
                    })

        # Remove duplicates while preserving order
        seen = set()
        final_phrases = []
        for item in combined_phrases:
            if item['text'] not in seen:
                final_phrases.append(item)
                seen.add(item['text'])

        return final_phrases

    else:
        vp_tokens = [
            token for token in vp_tokens
            if token['pos'] not in ['CH', 'Cc']
        ]

        return [{
            'text': rebuild_phrase(vp_tokens),
            'tokens': vp_tokens
        }]


def process_sentence(df, logger):
    logger.debug(df.to_string(index=False))
    tokens = parse_dataframe_to_tokens(df)
    np_tokens, vp_tokens = split_sentence_np_vp(tokens)
    logger.debug("-----------------NP-----------------")
    logger.debug(np_tokens)
    logger.debug("-----------------VP-----------------")
    logger.debug(vp_tokens)

    # Extract subjects, verbs, objects
    subjects = extract_main_subjects(np_tokens)
    verbs, verbs_token = extract_verbs(vp_tokens)
    objects = extract_objects(vp_tokens, verbs_token)

    logger.debug("-----------------subjects----------------")
    logger.debug(subjects)
    logger.debug("-----------------verbs----------------")
    for verb in verbs:
        logger.debug(verb['text'])
    logger.debug("-----------------objects----------------")
    for obj in objects:
        logger.debug(obj['text'])

    verbs_position = {}
    for verb in verbs:
        verb_last_id = verb['tokens'][0]['id']
        verbs_position[verb['text']] = verb_last_id

    verbs_sorted = sorted(verbs, key=lambda v: v['tokens'][0]['id'])
    objects_sorted = sorted(objects, key=lambda o: o['tokens'][0]['id'])

    # Start combine them into triplets
    triplets = []
    for subj in subjects:
        for i, verb in enumerate(verbs_sorted):
            verb_last_id = verb['tokens'][-1]['id']

            # Determine the next verb's first ID (or infinity if this is the last verb)
            next_verb_first_id = verbs_sorted[i + 1]['tokens'][0]['id'] if i + 1 < len(verbs_sorted) else float('inf')

            # Objects that come after this verb but before the next verb
            obj_candidates = []
            for obj in objects_sorted:
                obj_id = obj['tokens'][-1]['id']
                if verb_last_id < obj_id < next_verb_first_id:
                    obj_candidates.append(obj)

            for obj in obj_candidates:
                triplets.append((subj, verb['text'], obj['text']))

    return triplets

def triplet_extraction(text, vncorenlp_client, phoNLP_model, stopwords, logger, max_depth=2):
    """Iteratively extract triplets from text, including nested subjects/objects"""
    if not text.strip():
        return []

    # Queue of (text, current_depth, parent_text) to process
    work_queue = [(text, 0, None)]
    all_triplets = []
    seen_texts = set()

    while work_queue:
        current_text, current_depth, parent_text = work_queue.pop(0)
        
        # Skip if already processed or depth exceeded
        if current_text in seen_texts or current_depth > max_depth:
            continue
        
        seen_texts.add(current_text)
        
        try:
            sentence = clean_text(current_text)
            segmented_text = vncorenlp_client.word_segment(sentence)
            
            # Annotate text
            annotation = phoNLP_model.annotate(text=segmented_text[0])
            df = parsing_result(annotation)
            
            triplets = process_sentence(df, logger)
            
            for subj, verb, obj in triplets:
                # Store triplet with metadata
                all_triplets.append({
                    'subj': subj,
                    'verb': verb,
                    'obj': obj,
                    'depth': current_depth,
                    'parent_text': parent_text,
                    'source_text': current_text
                })
                
                # Queue subject for processing if it's complex enough
                if current_depth < max_depth and len(subj.split()) > 2:
                    work_queue.append((subj, current_depth + 1, subj))
                
                # Queue object for processing if it's complex enough
                if current_depth < max_depth and len(obj.split()) > 2:
                    work_queue.append((obj, current_depth + 1, obj))
                    
        except Exception:
            continue

    # Track which specific subject/object texts were expanded into deeper triplets
    expanded_phrases = set()
    
    for triplet in all_triplets:
        if triplet['parent_text'] is not None:
            # The parent_text is the phrase that was expanded
            expanded_phrases.add(triplet['parent_text'])
    
    # Build parent-child relationship map
    child_refinements = {}  # Maps parent phrase -> refined (subj, obj)
    for triplet in all_triplets:
        if triplet['parent_text'] is not None and triplet['parent_text'] in expanded_phrases:
            if triplet['parent_text'] not in child_refinements:
                child_refinements[triplet['parent_text']] = (triplet['subj'], triplet['obj'])
    
    # Filter and refine triplets
    final_triplets = []
    for triplet in all_triplets:
        subj = triplet['subj']
        verb = triplet['verb']
        obj = triplet['obj']
        
        # If this triplet has a child in expanded_phrases, keep it but replace subj/obj
        has_expanded_subj = subj in expanded_phrases
        has_expanded_obj = obj in expanded_phrases
        
        if has_expanded_subj or has_expanded_obj:
            # Replace with refined versions
            if has_expanded_subj and subj in child_refinements:
                subj = child_refinements[subj][0]
            if has_expanded_obj and obj in child_refinements:
                obj = child_refinements[obj][0]
            
            final_triplets.append((subj, verb, obj, triplet['depth']))
            continue
        
        # Keep triplets that weren't expanded
        final_triplets.append((subj, verb, obj, triplet['depth']))

    # Apply stopwords filtering and normalization
    filtered_triplets = []
    seen = set()

    for triplet_data in final_triplets:
        subj, verb, obj, depth_level = triplet_data

        # Remove stopwords
        subj_filtered = ' '.join([w for w in subj.split() if w.lower() not in stopwords]).strip()
        verb_filtered = ' '.join([w for w in verb.split() if w.lower() not in stopwords]).strip()
        obj_filtered = ' '.join([w for w in obj.split() if w.lower() not in stopwords]).strip()

        # Skip remove stopwords if any element becomes empty
        if not verb_filtered:
            verb_filtered = verb

        # Normalize: replace underscores, strip, lowercase
        subj_filtered = subj_filtered.replace('_', ' ').strip().lower()
        verb_filtered = verb_filtered.replace('_', ' ').strip().lower()
        obj_filtered = obj_filtered.replace('_', ' ').strip().lower()
        
        # Deduplicate triplets
        triplet_tuple = (subj_filtered, verb_filtered, obj_filtered)
        if triplet_tuple not in seen:
            filtered_triplets.append(triplet_tuple)
            seen.add(triplet_tuple)

    return filtered_triplets

def main():
    import logging
    from src.utils import load_stopwords
    from src.triplet_extraction.pos_taging import init_vncorenlp
    import phonlp
    import os
    from src.utils import setup_logger
    import re

    current_dir = os.getcwd()
    base_dir = r"E:\Github\LawAssistant"
    print(f"Working directory: {current_dir}")
    print(f"Base directory set to: {base_dir}\n")

    # === Define files paths relative to base directory ===
    vncorenlp_dir = os.path.join(base_dir, "nlp_models", "VnCoreNLP-1.2")
    phonlp_dir = os.path.join(base_dir, "nlp_models", "phonlp")
    synonym_file = os.path.join(current_dir, "listSameKey.txt")
    stopwords_file = os.path.join(current_dir, "stopwords.csv")
    no_triplet_csv_path = os.path.join(current_dir, "logs", "no_triplets_dat_dai_log_1.csv")
    log_file_path = os.path.join(current_dir, "logs", "dat_dai_triplet_extraction.txt")

    # === Initialize NLP models ===
    vncorenlp_client = init_vncorenlp(vncorenlp_dir)
    phoNLP_model = phonlp.load(save_dir=phonlp_dir)
    stopwords = load_stopwords(stopwords_file)

    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logger, console_handler, file_handler = setup_logger(
        name="triplet_extraction",
        level=logging.DEBUG,
        log_to_file=False,
        file_path=log_file_path
    )

    sentence = "Người sử dụng đất có quyền chung. Người sử dụng đất được cấp Giấy chứng nhận quyền sử dụng đất khi có đủ điều kiện theo quy định của pháp luật về đất đai. Người sử dụng đất được cấp Giấy chứng nhận quyền sở hữu tài sản gắn liền với đất khi có đủ điều kiện theo quy định của pháp luật về đất đai."
    pattern = re.compile(
        r"""
        (?<!\d)      # not preceded by a digit
        \.           # the dot
        (?!\d|\.)    # not followed by digit or another dot
        \s+          # whitespace
        """,
        re.VERBOSE
    )
    sentences = re.split(pattern, sentence)

    os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
    logger, console_handler, file_handler = setup_logger(
        name="triplet_extraction",
        level=logging.DEBUG,
        log_to_file=True,
        file_path=log_file_path
    )

    all_triplet = []
    for s in sentences:
        print("Processing sentence:", s)
        triplets = triplet_extraction(
            text=s,
            vncorenlp_client=vncorenlp_client,
            phoNLP_model=phoNLP_model,
            stopwords=stopwords,
            logger=logger,
            max_depth=8,
        )
        for t in triplets:
            logger.debug(t)
        all_triplet.extend(triplets)

    for t in all_triplet:
        print(t)


if __name__ == "__main__":
    main()