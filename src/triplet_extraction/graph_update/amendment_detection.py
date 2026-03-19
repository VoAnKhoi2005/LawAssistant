import re
from typing import Optional, List, Tuple, Dict, Set

AMENDMENT_KHOAN_PATTERN = re.compile(r"khoản\s+(\d+)", re.IGNORECASE)
AMENDMENT_DIEU_PATTERN = re.compile(r"điều\s+(\d+)", re.IGNORECASE)
AMENDMENT_DIEM_PATTERN = re.compile(r"điểm\s+([a-z])", re.IGNORECASE)
# Shorthand pattern for "khoản X điểm Y" notation (e.g., "khoản 2a", "3b")
AMENDMENT_SHORTHAND_PATTERN = re.compile(r"(?:khoản\s+)?(\d+)([a-z])(?!\d)", re.IGNORECASE)
AMENDMENT_PHAN_PATTERN = re.compile(r"phần\s+thứ\s+([ivxlcdm\d]+)", re.IGNORECASE)
AMENDMENT_CHUONG_PATTERN = re.compile(r"chương\s+([ivxlcdm\d]+)", re.IGNORECASE)
AMENDMENT_MUC_PATTERN = re.compile(r"mục\s+([ivxlcdm\d]+)", re.IGNORECASE)
AMENDMENT_TIEU_MUC_PATTERN = re.compile(r"tiểu\s+mục\s+(\d+)", re.IGNORECASE)
AMENDMENT_PHU_LUC_PATTERN = re.compile(r"phụ\s+lục(?:\s+([ivxlcdm\d]+))?", re.IGNORECASE)
AMENDMENT_SO_HIEU_PATTERN = re.compile(
    r"số\s+(\d{1,3}/\d{4}/[A-ZĐ]+[-–]?[A-Z0-9]+)",
    re.IGNORECASE
)
# Capture law name - Vietnamese law names typically start with "Luật" or "Bộ luật"
AMENDMENT_LAW_NAME_PATTERN = re.compile(r"((?:Bộ\s+)?Luật\s+[^\d\n]+?)(?=\s+số|\s+năm|$)", re.IGNORECASE)
# Enhanced law/document name pattern to capture various legal document types
AMENDMENT_DOC_NAME_PATTERN = re.compile(
    r"((?:Bộ\s+)?(?:Luật|Nghị định|Thông tư|Quyết định|Chỉ thị|Nghị quyết)\s+[^\d\n]+?)(?=\s+số|\s+năm|$)",
    re.IGNORECASE
)


def parse_amendment_reference(text: str, document_col) -> List[dict]:
    """
    Extract legal reference info from text, returning a list of references.
    Handles both single and multiple references in one unified function.
    
    Detects multiple references by finding multiple "điều" occurrences,
    and parses the text accordingly without relying on "tại" keyword.
    
    Returns:
        List of reference dictionaries. Empty list if nothing found.
    """
    if not text or not text.strip():
        return []

    text = text.split(":")[0]  # Consider only text before first colon
    
    # Extract base info (so_hieu, doc_name) that applies to all references
    so_hieu_m = AMENDMENT_SO_HIEU_PATTERN.search(text)
    doc_name_m = AMENDMENT_DOC_NAME_PATTERN.search(text)
    
    so_hieu = so_hieu_m.group(1).upper() if so_hieu_m else None
    doc_name = doc_name_m.group(1).strip() if doc_name_m else None
    
    # If so_hieu is missing but doc_name exists, try search
    if not so_hieu and doc_name:
        so_hieu = search_so_hieu(document_col, doc_name)
    
    # Find all "điều" matches to detect multiple references
    dieu_matches = list(AMENDMENT_DIEU_PATTERN.finditer(text))
    
    # If multiple điều found, parse as multiple references
    if len(dieu_matches) > 1:
        # Split by comma, semicolon, and "và" to get segments
        segments = re.split(r'[,;]\s*|\s+và\s+', text)
        
        references = []
        current_context = {
            'so_hieu': so_hieu,
            'doc_name': doc_name,
            'dieu': None,
            'khoan': None,
            'diem': None,
            'phan': None,
            'chuong': None,
            'muc': None,
            'tieu_muc': None,
            'phu_luc': None,
        }
        
        for segment in segments:
            segment = segment.strip()
            if not segment:
                continue
            
            # Parse this segment
            shorthand_m = AMENDMENT_SHORTHAND_PATTERN.search(segment)
            dieu_m = AMENDMENT_DIEU_PATTERN.search(segment)
            khoan_m = AMENDMENT_KHOAN_PATTERN.search(segment)
            diem_m = AMENDMENT_DIEM_PATTERN.search(segment)
            phan_m = AMENDMENT_PHAN_PATTERN.search(segment)
            chuong_m = AMENDMENT_CHUONG_PATTERN.search(segment)
            muc_m = AMENDMENT_MUC_PATTERN.search(segment)
            tieu_muc_m = AMENDMENT_TIEU_MUC_PATTERN.search(segment)
            phu_luc_m = AMENDMENT_PHU_LUC_PATTERN.search(segment)
            
            # Handle shorthand notation (e.g., "khoản 2a" or "2a" = khoản 2 điểm a)
            if shorthand_m and not diem_m:
                if not khoan_m:
                    khoan_m = shorthand_m
                diem_m = shorthand_m
            
            # Update context with new values found
            if dieu_m:
                current_context['dieu'] = dieu_m.group(1)
                # When điều changes, reset all lower levels unless explicitly mentioned
                if not khoan_m:
                    current_context['khoan'] = None
                if not diem_m:
                    current_context['diem'] = None
            
            if khoan_m:
                current_context['khoan'] = khoan_m.group(1)
                # Reset điểm when khoản changes unless điểm is in same segment
                if not diem_m:
                    current_context['diem'] = None
            
            if diem_m:
                # For shorthand, group(2) contains the letter; for regular, group(1)
                if diem_m == shorthand_m:
                    current_context['diem'] = diem_m.group(2).lower()
                else:
                    current_context['diem'] = diem_m.group(1).lower()
            
            if phan_m:
                current_context['phan'] = phan_m.group(1).lower()
            if chuong_m:
                current_context['chuong'] = chuong_m.group(1).lower()
            if muc_m:
                current_context['muc'] = muc_m.group(1).lower()
            if tieu_muc_m:
                current_context['tieu_muc'] = tieu_muc_m.group(1)
            if phu_luc_m:
                current_context['phu_luc'] = phu_luc_m.group(1).lower() if phu_luc_m.group(1) else None
            
            # Create a reference from current context if we have at least điều
            if current_context['dieu']:
                ref = current_context.copy()
                # Check if this exact reference already exists
                if ref not in references:
                    references.append(ref)
        
        return references if references else []
    
    # Single reference case - parse all components
    shorthand_m = AMENDMENT_SHORTHAND_PATTERN.search(text)
    khoan_m = AMENDMENT_KHOAN_PATTERN.search(text)
    dieu_m = AMENDMENT_DIEU_PATTERN.search(text)
    diem_m = AMENDMENT_DIEM_PATTERN.search(text)
    phan_m = AMENDMENT_PHAN_PATTERN.search(text)
    chuong_m = AMENDMENT_CHUONG_PATTERN.search(text)
    muc_m = AMENDMENT_MUC_PATTERN.search(text)
    tieu_muc_m = AMENDMENT_TIEU_MUC_PATTERN.search(text)
    phu_luc_m = AMENDMENT_PHU_LUC_PATTERN.search(text)

    # Handle shorthand notation (e.g., "khoản 2a" or "2a" = khoản 2 điểm a)
    if shorthand_m and not diem_m:
        if not khoan_m:
            khoan_m = shorthand_m
        diem_m = shorthand_m

    if not (khoan_m or dieu_m or diem_m or phan_m or chuong_m or muc_m or
            tieu_muc_m or phu_luc_m or so_hieu_m or doc_name_m):
        return []

    # For shorthand, group(2) contains the letter; for regular, group(1)
    diem_value = None
    if diem_m:
        if diem_m == shorthand_m:
            diem_value = diem_m.group(2).lower()
        else:
            diem_value = diem_m.group(1).lower()

    ref = {
        "phan": phan_m.group(1).lower() if phan_m else None,
        "chuong": chuong_m.group(1).lower() if chuong_m else None,
        "muc": muc_m.group(1).lower() if muc_m else None,
        "tieu_muc": tieu_muc_m.group(1) if tieu_muc_m else None,
        "phu_luc": phu_luc_m.group(1).lower() if phu_luc_m and phu_luc_m.group(1) else None,
        "dieu": dieu_m.group(1) if dieu_m else None,
        "khoan": khoan_m.group(1) if khoan_m else None,
        "diem": diem_value,
        "so_hieu": so_hieu,
        "doc_name": doc_name,
    }
    
    return [ref]


def search_so_hieu(document_col, law_name: str) -> Optional[str]:
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
    # doc = document_col.find_one(
    #     {"title": {"$regex": re.escape(law_name), "$options": "i"}},
    #     {"so_hieu": 1}
    # )
    #
    # if doc:
    #     return doc.get("so_hieu")

    return None


def parse_amendment_type(text: str) -> List[str]:
    """
    Parse amendment type(s) from text.
    A sentence can have multiple types (e.g., "sửa đổi, bổ sung").

    Args:
        text: Text to parse for amendment types

    Returns:
        List of amendment types found, in order of appearance
    """
    AMENDMENT_PATTERNS = {
        'modify': [
            r'sửa đổi',
            r'đổi',
        ],
        'add': [
            r'bổ sung',
            r'thêm',
            r'tăng',
        ],
        'remove': [
            r'bãi bỏ',
            r'xóa bỏ',
            r'hủy bỏ',
            r'loại bỏ',
        ],
        'replace': [
            r'thay thế',
            r'thay',
        ]
    }

    text = text.split(":")[0]  # Consider only text before first colon

    found_types = []
    seen_types = set()

    # Create a list of (position, type) tuples for all matches
    matches = []

    for amendment_type, patterns in AMENDMENT_PATTERNS.items():
        for pattern in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                matches.append((match.start(), amendment_type))

    # Sort by position to maintain order of appearance
    matches.sort(key=lambda x: x[0])

    # Add types in order, avoiding duplicates
    for _, amendment_type in matches:
        if amendment_type not in seen_types:
            found_types.append(amendment_type)
            seen_types.add(amendment_type)

    return found_types

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

    return node

def add_amendment_ref_to_nodes(
    node: Dict,
    documents_col,
    ref: Optional[Dict[str, str]] = None,
    verbose: bool = False,
) -> List[Dict]:
    """
    Add amendment references to each node in the tree structure using iterative approach.
    Traverses downward through children only. Returns array of unique leaf nodes.
    Only adds ref properties if they don't already exist in the node's ref.
    """
    if not node:
        return []

    # Stack contains tuples of (node, current_ref)
    stack: list[Tuple[Dict, Dict[str, str]]] = [(node, ref or {})]
    visited: Set[int] = set()
    leaf_nodes: List[Dict] = []
    seen_paths: Set[str] = set()  # Track unique full_paths

    while stack:
        current_node, current_ref = stack.pop()

        # Prevent infinite recursion
        node_id = id(current_node)
        if node_id in visited:
            continue
        visited.add(node_id)

        if current_node.get('is_amendment') is not True:
            continue

        # Parse amendment type
        amendment_type = parse_amendment_type(current_node['content'])
        
        # Parse references (handles both single and multiple)
        parsed_refs = parse_amendment_reference(current_node['content'], documents_col)
        
        # If multiple references found, create multiple leaf nodes
        if parsed_refs and len(parsed_refs) > 1:
            for idx, new_ref in enumerate(parsed_refs):
                # Merge references: copy ref and update with new_ref values
                merged_ref = current_ref.copy()
                if new_ref:
                    for key in ['so_hieu', 'dieu', 'khoan', 'diem', 'doc_name',
                               'phan', 'chuong', 'muc', 'tieu_muc', 'phu_luc']:
                        if new_ref.get(key) and not merged_ref.get(key):
                            merged_ref[key] = new_ref[key]
                
                # Create a pseudo-node for this reference
                pseudo_node = current_node.copy()
                pseudo_node['ref'] = merged_ref.copy()
                pseudo_node['ref']['amendment_type'] = amendment_type
                
                # Make unique path for multiple refs from same node
                full_path = current_node.get('full_path')
                if full_path:
                    unique_path = f"{full_path}#ref{idx}"
                    if unique_path not in seen_paths:
                        leaf_nodes.append(pseudo_node)
                        seen_paths.add(unique_path)
                        if verbose:
                            print(f"Leaf (multi-ref {idx}): {full_path}")
                            print(f"Ref: {pseudo_node.get('ref', {})}")
                            print()
            
            # Continue to next node without processing children
            if 'children' in current_node and current_node['children']:
                for child in reversed(current_node['children']):
                    stack.append((child, current_ref))
            continue
        
        # Single reference case - extract from list
        new_ref = parsed_refs[0] if parsed_refs else None

        # Merge references: copy ref and update with new_ref values
        merged_ref = current_ref.copy()
        if new_ref:
            for key in ['so_hieu', 'dieu', 'khoan', 'diem', 'doc_name',
                       'phan', 'chuong', 'muc', 'tieu_muc', 'phu_luc']:
                if new_ref.get(key) and not merged_ref.get(key):
                    merged_ref[key] = new_ref[key]

        # Initialize ref dict if it doesn't exist
        if 'ref' not in current_node:
            current_node['ref'] = {}

        # Only add individual properties if they don't exist
        for key in ['so_hieu', 'dieu', 'khoan', 'diem', 'doc_name',
                   'phan', 'chuong', 'muc', 'tieu_muc', 'phu_luc']:
            if key not in current_node['ref'] and key in merged_ref:
                current_node['ref'][key] = merged_ref[key]

        current_node['ref']['amendment_type'] = amendment_type

        # Check if this is a leaf node (no children or empty children list)
        is_leaf = 'children' not in current_node or not current_node['children']

        if is_leaf:
            full_path = current_node.get('full_path')

            # Only add if we haven't seen this full_path before
            if full_path and full_path not in seen_paths:
                leaf_nodes.append(current_node)
                seen_paths.add(full_path)
                if verbose:
                    print(f"Leaf: {full_path}")
                    print(f"Ref: {current_node.get('ref', {})}")
                    print()
            elif full_path in seen_paths:
                if verbose:
                    print(f"Skipping duplicate: {full_path}")

        # Add children to stack
        if 'children' in current_node:
            for child in current_node['children']:
                stack.append((child, merged_ref))

    return leaf_nodes