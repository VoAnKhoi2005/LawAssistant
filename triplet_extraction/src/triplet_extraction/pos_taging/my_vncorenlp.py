from . import *

vncorenlp_pos_map = {
    "N":   "Noun (Danh từ)",
    "Np":  "Proper noun (Danh từ riêng)",
    "Nc":  "Classifier noun (Danh từ giống loại)",
    "Nu":  "Unit noun (Danh từ đơn vị)",
    "V":   "Verb (Động từ)",
    "Vb":  "Verb (base) (Động từ gốc)",
    "A":   "Adjective (Tính từ)",
    "Ai":  "Adjective (predicative) (Tính từ vị ngữ)",
    "P":   "Pronoun (Đại từ)",
    "R":   "Adverb (Trạng từ)",
    "M":   "Numeral / number (Số từ)",
    "E":   "Preposition / particle (Giới từ / trợ từ)",
    "C":   "Coordinating conjunction (Liên từ phối hợp)",
    "CC":  "Subordinating conjunction / complementizer (Liên từ phụ thuộc)",
    "L":   "Determiner / article (Từ hạn định)",
    "D":   "Adverbial marker / degree marker (Từ chỉ mức độ)",
    "X":   "Other (Khác)",
    "CH":  "Punctuation (Dấu câu)"
}

SUB_DEPRELS = {"sub", "nsubj", "nsubj:pass", "csubj"}
OBJ_DEPRELS = {"dob", "obj", "dobj", "iobj"}   # trực tiếp
NO_OBJECT_TOKENS = {"sau", "như", "như sau", "ví dụ", "v.v", "v.v."}

def init_vncorenlp(vncorenlp_dir, annotators=None):
    if annotators is None:
        annotators = ["wseg", "pos", "ner", "parse"]
    if "rdrsegmenter" not in globals():
        import py_vncorenlp
        rdrsegmenter = py_vncorenlp.VnCoreNLP(
            annotators=annotators,
            save_dir=vncorenlp_dir
        )
    return rdrsegmenter

def process_sentence(text: str, rdrsegmenter, verbose: bool = True) -> dict:
    """
    Dependency-aware sentence processing.
    Requires rdrsegmenter.annotate_text(text) to return tokens with:
        - 'index' (int)
        - 'wordForm' (str)
        - 'posTag' (str)
        - 'head' (int)  -- index of parent, 0 means root
        - 'depLabel' (str) -- dependency label (e.g., 'sub','dob','nmod','vmod', ...)
    If dependency fields are not numeric/available, the function will warn and return empty concepts.
    """
    results = {
        "original": text,
        "cleaned": "",
        "segmented": [],
        "pos_annotation": [],
        "concepts": []
    }

    # 1. Clean
    text_clean = clean_text(text)
    results["cleaned"] = text_clean
    if verbose:
        print("1. Cleaned text:\n", text_clean, "\n")

    # 2. Segmentation
    try:
        segmented = rdrsegmenter.word_segment(text_clean)
    except Exception:
        segmented = [text_clean]
    results["segmented"] = segmented
    if verbose:
        print("2. Segmented text (tokens):\n", segmented, "\n")

    # 3. Annotate (POS + DEP)
    output = rdrsegmenter.annotate_text(text_clean)
    sents = output.values() if isinstance(output, dict) else output

    dep_annots = []
    for sent in sents:
        for tok in sent:
            dep_annots.append(tok)

    # quick check: do we have numeric heads? if not, dependency parse likely not active
    if not has_numeric_heads(dep_annots):
        # fallback: return POS annotation and no concepts (user should enable parse)
        if verbose:
            print("WARNING: dependency parse fields (head/depLabel) not numeric or absent. "
                  "Enable parser with annotators='parse' to use dependency-based extraction.")
        # build pos_annotation (best-effort)
        pos_annot = []
        for t in dep_annots:
            pos_short = t.get("posTag") or t.get("pos") or ""
            pos_full = vncorenlp_pos_map.get(pos_short, pos_short)
            pos_annot.append({
                "index": t.get("index"),
                "token": t.get("wordForm"),
                "pos": pos_full,
                "posTag": pos_short
            })
        results["pos_annotation"] = pos_annot
        results["concepts"] = []
        return results

    # build maps
    index_map = build_index_map(dep_annots)
    children_map = build_children_map(dep_annots)

    # prepare pos_annotation for output
    pos_annot = []
    if verbose:
        print("3. Dependency annotation:")
        print(f"{'Idx':<5} {'Token':<20} {'POS':<6} {'Head':<6} {'DepRel':<10}")
        print("-" * 60)
    for t in dep_annots:
        idx = t.get("index")
        wf = t.get("wordForm")
        pos_short = t.get("posTag") or t.get("pos") or ""
        pos_full = vncorenlp_pos_map.get(pos_short, pos_short)
        head = t.get("head")
        dep = t.get("depLabel") or t.get("depRel") or ""
        pos_annot.append({
            "index": idx,
            "token": wf,
            "pos": pos_full,
            "posTag": pos_short,
            "head": head,
            "depLabel": dep
        })
        if verbose:
            print(f"{str(idx):<5} {normalize_token(wf):<20} {pos_short:<6} {str(head):<6} {dep:<10}")

    results["pos_annotation"] = pos_annot

    # 4. Extract triplets using dependency relations
    triplets = []
    # Iterate over tokens that are subjects (depLabel in SUB_DEPRELS)
    for t in dep_annots:
        dep = t.get("depLabel") or t.get("depRel") or ""
        if dep in SUB_DEPRELS:
            subj_idx = t.get("index")
            subj_phrase = get_full_np(subj_idx, index_map, children_map)
            # find head (relation)
            head_id = t.get("head")
            if isinstance(head_id, str) and head_id.isdigit():
                head_id = int(head_id)
            head_token = index_map.get(head_id)
            if not head_token:
                continue
            relation = normalize_token(head_token.get("wordForm", ""))

            # find direct objects of the same head
            obj_tokens = [x for x in dep_annots if (x.get("head") == head_id or (isinstance(x.get("head"), str) and str(x.get("head")) == str(head_id))) and ((x.get("depLabel") or x.get("depRel") or "") in OBJ_DEPRELS)]
            if not obj_tokens:
                # optionally: some frameworks use dob, but object might be a 'nmod' attached to head or child of head
                # try fallback: find nmod child of head (like 'có ... trách nhiệm' sometimes uses dob or nmod)
                obj_tokens = [x for x in dep_annots if (x.get("head") == head_id or (isinstance(x.get("head"), str) and str(x.get("head")) == str(head_id))) and ((x.get("depLabel") or x.get("depRel") or "") in {"nmod", "obl", "xcomp", "ccomp", "advmod"})]

            for obj_tok in obj_tokens:
                obj_idx = obj_tok.get("index")
                obj_phrase = get_full_object_phrase(obj_idx, index_map, children_map)
                # filter trivial objects
                if not obj_phrase or obj_phrase in NO_OBJECT_TOKENS:
                    continue
                trip = (normalize_token(subj_phrase), relation, normalize_token(obj_phrase))
                if trip not in triplets:
                    triplets.append(trip)

    results["concepts"] = triplets

    if verbose:
        print("\n4. Extracted triplets:")
        if triplets:
            for s, r, o in triplets:
                print(" -", (s, r, o))
        else:
            print(" - (no triplets found)")

    return results