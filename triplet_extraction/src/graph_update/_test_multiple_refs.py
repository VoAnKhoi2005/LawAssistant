"""Test multiple reference parsing for amendments"""
import sys
import re

# Inline the parsing logic for testing
AMENDMENT_KHOAN_PATTERN = re.compile(r"khoản\s+(\d+)", re.IGNORECASE)
AMENDMENT_DIEU_PATTERN = re.compile(r"điều\s+(\d+)", re.IGNORECASE)
AMENDMENT_DIEM_PATTERN = re.compile(r"điểm\s+([a-z])", re.IGNORECASE)
AMENDMENT_SO_HIEU_PATTERN = re.compile(r"số\s+(\d+/\d+/QH\d+)", re.IGNORECASE)

def parse_multiple_references_test(text):
    """Simplified version for testing"""
    so_hieu_m = AMENDMENT_SO_HIEU_PATTERN.search(text)
    so_hieu = so_hieu_m.group(1).upper() if so_hieu_m else None
    
    # Split by "tại" to get the reference section
    parts = re.split(r'\btại\b', text, flags=re.IGNORECASE)
    if len(parts) < 2:
        return []
    
    ref_section = parts[-1]
    
    # Split by comma, semicolon, and "và"
    segments = re.split(r'[,;]\s*|\s+và\s+', ref_section)
    
    references = []
    current_context = {
        'so_hieu': so_hieu,
        'dieu': None,
        'khoan': None,
        'diem': None,
    }
    
    for segment in segments:
        segment = segment.strip()
        if not segment:
            continue
        
        # Parse this segment
        dieu_m = AMENDMENT_DIEU_PATTERN.search(segment)
        khoan_m = AMENDMENT_KHOAN_PATTERN.search(segment)
        diem_m = AMENDMENT_DIEM_PATTERN.search(segment)
        
        # Update context with new values found
        if dieu_m:
            current_context['dieu'] = dieu_m.group(1)
            # Reset lower-level context when điều changes
            current_context['khoan'] = None
            current_context['diem'] = None
        if khoan_m:
            current_context['khoan'] = khoan_m.group(1)
            # Reset điểm when khoản changes (if điểm is under khoản)
            if not diem_m:
                current_context['diem'] = None
        if diem_m:
            current_context['diem'] = diem_m.group(1).lower()
        
        # Create a reference from current context if we have at least điều
        if current_context['dieu']:
            ref = current_context.copy()
            references.append(ref)
    
    return references


# Test case from the example
test_text = 'Thay thế cụm từ "Sở Giao thông vận tải" bằng cụm từ "Sở Xây dựng" tại khoản 4 Điều 9, điểm a, điểm c khoản 2 và khoản 3 Điều 11, điểm b khoản 2 và điểm c khoản 3 Điều 17, khoản 1 Điều 22, khoản 2 Điều 23.'

# Parse the references
refs = parse_multiple_references_test(test_text)

print(f"Found {len(refs)} references:")
print("=" * 80)

for i, ref in enumerate(refs, 1):
    parts = []
    if ref.get('diem'):
        parts.append(f"điểm {ref['diem']}")
    if ref.get('khoan'):
        parts.append(f"khoản {ref['khoan']}")
    if ref.get('dieu'):
        parts.append(f"Điều {ref['dieu']}")
    
    print(f"{i}. {' '.join(parts)}")

print("\n" + "=" * 80)
print("\nExpected references:")
print("1. khoản 4 Điều 9")
print("2. điểm a Điều 9")
print("3. điểm c khoản 2 Điều 11")
print("4. khoản 3 Điều 11")
print("5. điểm b khoản 2 Điều 17")
print("6. điểm c khoản 3 Điều 17")
print("7. khoản 1 Điều 22")
print("8. khoản 2 Điều 23")

