import re
from typing import List, Dict, Set

NP_EXPAND_DEPRELS = {"compound", "det", "nmod", "amod", "flat"}  # dùng để mở rộng NP
OBJ_MODIFIERS = {"nmod", "vmod", "acl", "conj", "amod"}  # kéo vào object (ví dụ 'phối_hợp', 'giải_quyết')
PUNCT_DEPRELS = {"punct"}

def clean_text(text: str) -> str:
    text = re.sub(r"[\r\n\t]+", " ", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[!?]+", "", text)
    return text.strip().lower()

def normalize_token(tok: str) -> str:
    return tok.replace("_", " ").strip()

def clean_text_default(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())

def has_numeric_heads(dep_annots: List[Dict]) -> bool:
    # Kiểm tra xem trường head có numeric không — nếu không, có thể parse chưa bật
    for t in dep_annots:
        h = t.get("head")
        if isinstance(h, int) and h >= 0:
            return True
        # some versions use string numbers
        if isinstance(h, str) and h.isdigit():
            return True
    return False

def build_index_map(dep_annots: List[Dict]) -> Dict[int, Dict]:
    d = {}
    for t in dep_annots:
        idx = t.get("index")
        if isinstance(idx, str) and idx.isdigit():
            idx = int(idx)
        d[idx] = t
    return d

def build_children_map(dep_annots: List[Dict]) -> Dict[int, List[Dict]]:
    children = {}
    for t in dep_annots:
        head = t.get("head")
        if isinstance(head, str) and head.isdigit():
            head = int(head)
        idx = t.get("index")
        if isinstance(idx, str) and idx.isdigit():
            idx = int(idx)
        children.setdefault(head, []).append(t)
    return children

def collect_subtree_tokens(start_idx: int, children_map: Dict[int, List[Dict]],
                           allowed_deprels: Set[str]) -> Set[int]:
    """
    BFS/DFS collect indices of subtree tokens that are connected via allowed_deprels
    starting from start_idx (excluding start_idx itself unless specified by caller).
    This gathers dependent words that should be included in the phrase.
    """
    collected = set()
    stack = [start_idx]
    while stack:
        cur = stack.pop()
        for child in children_map.get(cur, []):
            dep = child.get("depLabel") or child.get("depRel") or ""
            if dep in allowed_deprels:
                idx_child = child.get("index")
                if isinstance(idx_child, str) and idx_child.isdigit():
                    idx_child = int(idx_child)
                if idx_child not in collected:
                    collected.add(idx_child)
                    stack.append(idx_child)
    return collected

def phrase_from_indices(indices: Set[int], index_map: Dict[int, Dict]) -> str:
    # sort by index and join normalized wordForm
    idxs = sorted(indices)
    tokens = [normalize_token(index_map[i]["wordForm"]) for i in idxs if i in index_map]
    return " ".join(tokens).strip()

def get_full_np(head_idx: int, index_map: Dict[int, Dict], children_map: Dict[int, List[Dict]]) -> str:
    """
    Lấy cụm NP toàn bộ: head + các child có deprel thuộc NP_EXPAND_DEPRELS,
    kèm theo các compound/det phía trước.
    """
    indices = {head_idx}
    # include compound/det/amod/nmod attached to head
    extra = collect_subtree_tokens(head_idx, children_map, NP_EXPAND_DEPRELS)
    indices.update(extra)
    # also include left-side compounds/dets that reference head via children_map (already included)
    return phrase_from_indices(indices, index_map)

def get_full_object_phrase(obj_idx: int, index_map: Dict[int, Dict], children_map: Dict[int, List[Dict]]) -> str:
    """
    Lấy object phrase: object head + NP expansions + modifiers (vmod/nmod/acl/conj)
    We include head and its compound/det, then append modifiers found (ordered by index).
    """
    base_indices = {obj_idx}
    base_indices.update(collect_subtree_tokens(obj_idx, children_map, NP_EXPAND_DEPRELS))
    # modifiers (verbs/adjectival modifiers) attached to object
    modifier_indices = collect_subtree_tokens(obj_idx, children_map, OBJ_MODIFIERS)
    # Combine base + modifiers
    all_indices = base_indices.union(modifier_indices)
    return phrase_from_indices(all_indices, index_map)