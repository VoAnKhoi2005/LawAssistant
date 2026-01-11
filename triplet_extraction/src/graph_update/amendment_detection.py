import re
from typing import Optional

KHOAN_PATTERN = re.compile(r"khoản\s+(\d+)", re.IGNORECASE)
DIEU_PATTERN = re.compile(r"điều\s+(\d+)", re.IGNORECASE)
DIEM_PATTERN = re.compile(r"điểm\s+([a-z])", re.IGNORECASE)
SO_HIEU_PATTERN = re.compile(r"số\s+(\d+/\d+/QH\d+)", re.IGNORECASE)
# Capture law name - Vietnamese law names typically start with "Luật" or "Bộ luật"
LAW_NAME_PATTERN = re.compile(r"((?:Bộ\s+)?Luật\s+[^\d\n]+?)(?=\s+số|\s+năm|$)", re.IGNORECASE)


def fuzzy_search_so_hieu(document_col, law_name: str) -> Optional[str]:
    """
    Fuzzy search for so_hieu in document collection using law name.
    Uses text search with case-insensitive regex.
    """
    # Try exact match first
    doc = document_col.find_one(
        {"title": {"$regex": f"^{re.escape(law_name)}$", "$options": "i"}},
        {"so_hieu": 1}
    )

    if doc:
        return doc.get("so_hieu")

    # Try partial match
    doc = document_col.find_one(
        {"title": {"$regex": re.escape(law_name), "$options": "i"}},
        {"so_hieu": 1}
    )

    if doc:
        return doc.get("so_hieu")

    return None


def parse_amendment_reference(text: str, document_col) -> dict | None:
    """
    Extract all available legal reference info from text.
    - Only take the FIRST occurrence of each component
    - Missing components are returned as None
    - If nothing is found at all, return None
    - If so_hieu is missing but law_name exists and document_col is provided,
      attempts to resolve so_hieu via fuzzy search
    """
    text = text.split(":")[0]  # Consider only text before first colon

    khoan_m = KHOAN_PATTERN.search(text)
    dieu_m = DIEU_PATTERN.search(text)
    diem_m = DIEM_PATTERN.search(text)
    so_hieu_m = SO_HIEU_PATTERN.search(text)
    law_name_m = LAW_NAME_PATTERN.search(text)

    if not (khoan_m or dieu_m or diem_m or so_hieu_m or law_name_m):
        return None

    so_hieu = so_hieu_m.group(1).upper() if so_hieu_m else None
    law_name = law_name_m.group(1).strip() if law_name_m else None

    # If so_hieu is missing but law_name exists, try fuzzy search
    if not so_hieu and law_name:
        so_hieu = fuzzy_search_so_hieu(document_col, law_name)

    return {
        "diem": diem_m.group(1).lower() if diem_m else None,
        "khoan": khoan_m.group(1) if khoan_m else None,
        "dieu": dieu_m.group(1) if dieu_m else None,
        "so_hieu": so_hieu,
        "law_name": law_name,
    }


def resolve_full_path(sections_col, ref: dict) -> str | None:
    """
    Resolve amendment reference to canonical full_path using MongoDB.
    """
    # If no so_hieu or dieu, cannot resolve
    if not ref.get("so_hieu") or not ref.get("dieu"):
        return None

    dieu_title = f"điều {ref['dieu']}"

    node = sections_col.find_one(
        {
            "so_hieu": ref["so_hieu"].upper(),
            "type": "điều",
            "title": {"$regex": f"^{dieu_title}$", "$options": "i"}
        },
        {"full_path": 1}
    )

    if not node:
        return None

    return node["full_path"]

from typing import Dict, Optional, Set, Tuple

def add_amendment_ref_to_nodes(
    node: Dict,
    documents_col,
    ref: Optional[Dict[str, str]] = None
) -> None:
    """
    Add amendment references to each node in the tree structure using iterative approach.
    Traverses downward through children only. Prints full path and ref for leaf nodes.
    Only adds ref properties if they don't already exist in the node's ref.

    Args:
        node: Tree node containing type, title, content, and optional children
        ref: Reference dictionary with keys like 'so_hieu', 'dieu', 'khoan'
    """
    if not node:
        return

    # Stack contains tuples of (node, current_ref)
    stack: list[Tuple[Dict, Dict[str, str]]] = [(node, ref or {})]
    visited: Set[int] = set()

    while stack:
        current_node, current_ref = stack.pop()

        # Prevent infinite recursion
        node_id = id(current_node)
        if node_id in visited:
            continue
        visited.add(node_id)

        if current_node['is_amendment'] is not True:
            continue

        # Parse new reference from current node
        new_ref = parse_amendment_reference(current_node['content'], documents_col)

        # Merge references: copy ref and update with new_ref values
        merged_ref = current_ref.copy()
        if new_ref:
            for key in ['so_hieu', 'dieu', 'khoan', 'diem', 'law_name']:
                if new_ref.get(key) and not merged_ref.get(key):
                    merged_ref[key] = new_ref[key]

        # Initialize ref dict if it doesn't exist
        if 'ref' not in current_node:
            current_node['ref'] = {}

        # Only add individual properties if they don't exist
        for key in ['so_hieu', 'dieu', 'khoan', 'diem', 'law_name']:
            if key not in current_node['ref'] and key in merged_ref:
                current_node['ref'][key] = merged_ref[key]

        # Check if this is a leaf node (no children or empty children list)
        is_leaf = 'children' not in current_node or not current_node['children']

        if is_leaf:
            print(f"Leaf: {current_node.get('full_path', 'N/A')}")
            print(f"Ref: {current_node.get('ref', {})}")
            print()

        # Add children to stack
        if 'children' in current_node:
            for child in current_node['children']:
                stack.append((child, merged_ref))