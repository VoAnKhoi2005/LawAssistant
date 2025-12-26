import re

from triplet_extraction.src.doc_extraction.utils import clean_content, generate_id


def collect_content(output_text, start_index):
    """
    Collect content lines until hitting a structural marker.
    Returns: (content_string, next_index)
    """
    content_lines = []
    i = start_index
    while i < len(output_text):
        next_line = output_text[i].strip()
        # Check for structural markers that indicate a new section
        # Use stricter patterns to avoid matching references
        if (re.match(r"^điều\s+[ivxlcdm\d]+[.:]", next_line.lower())  # Article header with dot or colon
                or re.match(r"^chương\s+[ivxlcdm\d]+", next_line.lower())  # Chapter header
                or re.match(r"^mục\s+[ivxlcdm\d]+", next_line.lower())  # Section header
                or re.match(r"^\d+\.\s+", next_line)  # Clause (numbered item)
                or re.match(r"^[a-zA-ZđĐ]\)\s+", next_line)):  # Point (lettered item)
            break
        if next_line:
            content_lines.append(next_line)
        i += 1
    return "\n".join(content_lines).strip() or None, i


def parse_document(input_text, so_hieu):
    """
    Parse Vietnamese legal document structure and store in database.
    Handles hierarchy: Chương (Chapter) -> Mục (Section) -> Điều (Article)
    -> Khoản (Clause) -> Điểm (Point)

    Edge case: Documents without chapters are supported - elements will be
    organized directly under the document (so_hieu).
    """
    text = [line.strip() for line in input_text.splitlines() if line.strip()]
    index = 0
    result = {}
    # Track current parent IDs and titles for hierarchy
    chuong_id = muc_id = dieu_id = khoan_id = None
    chuong_title = muc_title = dieu_title = khoan_title = ""

    while index < len(text):
        line = text[index].strip()
        next_line = text[index + 1].strip() if index < len(text) - 1 else ""

        if (("............." in line or "--------------" in line)
                or ("............." in next_line or "--------------" in next_line)):
            index = index + 1
            continue

        # ---- Chương (Chapter) ----
        match = re.match(r"^(chương\s+[ivxlcdm\d]+)(?:[.\s]+(.*))?", line.lower())
        if match:
            title = match.group(1).strip()
            inline_content = match.group(2).strip() if match.group(2) else ""

            # Collect following content
            extra_content, index = collect_content(text, index + 1)
            content = inline_content
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            full_path = f"{so_hieu}_{title}"
            chuong_id = generate_id(full_path)
            result[chuong_id] = {
                "id": chuong_id,
                "title": title,
                "content": content,
                "parent_id": None,
                "so_hieu": so_hieu,
                "full_path": full_path
            }

            # Reset hierarchy
            chuong_title = title
            muc_id = dieu_id = khoan_id = None
            muc_title = dieu_title = khoan_title = ""
            continue

        # ---- Mục (Section) ----
        match = re.match(r"^(mục\s+[ivxlcdm\d]+)(?:[.\s]+(.*))?", line.lower())
        if match:
            title = match.group(1).strip()
            inline_content = match.group(2).strip() if match.group(2) else ""

            # Collect following content
            extra_content, index = collect_content(text, index + 1)
            content = inline_content
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            # Build path considering no chapter case
            if chuong_title:
                full_path = f"{so_hieu}_{chuong_title}_{title}"
            else:
                full_path = f"{so_hieu}_{title}"

            muc_id = generate_id(full_path)
            result[muc_id] = {
                "id": muc_id,
                "title": title,
                "content": content,
                "parent_id": chuong_id,  # Will be None if no chapter
                "so_hieu": so_hieu,
                "full_path": full_path
            }

            # Reset hierarchy
            muc_title = title
            dieu_id = khoan_id = None
            dieu_title = khoan_title = ""
            continue

        # ---- Điều (Article) ----
        # Match only lines starting with "Điều" followed by number/roman and a dot or colon
        # This excludes references like "quy định tại Điều X" or "khoản Y Điều Z"
        match = re.match(r"^điều\s+([ivxlcdm\d]+)[.:]", line.lower())
        if match:
            # Skip if this looks like a reference in a list (e.g., "Điều 105; Điều 118.")
            # Check if line contains semicolons before the match (indicating it's in a list)
            if ';' in line[:match.end()]:
                index += 1
                continue
            
            # Extract title (e.g., "điều 1")
            title = f"điều {match.group(1)}"
            # Split at first dot or colon after article number to get content
            parts = re.split(r"^điều\s+[ivxlcdm\d]+[.:]\s*", line.lower(), maxsplit=1)
            content = parts[1].strip() if len(parts) > 1 else ""
            extra_content, index = collect_content(text, index + 1)
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            parent_id = muc_id if muc_id else chuong_id

            # Build path considering no chapter case
            if chuong_title:
                parent_path = f"{so_hieu}_{chuong_title}"
            else:
                parent_path = so_hieu

            if muc_title:
                parent_path += f"_{muc_title}"

            full_path = f"{parent_path}_{title}"
            dieu_id = generate_id(full_path)
            result[dieu_id] = {
                "id": dieu_id,
                "title": title,
                "content": content,
                "parent_id": parent_id,
                "so_hieu": so_hieu,
                "full_path": full_path
            }

            # Update path and reset child levels
            dieu_title = title
            khoan_id = None
            khoan_title = ""
            continue

        # ---- Khoản (Clause) ----
        if re.match(r"^\d+\.", line):
            parts = re.split(r"\.", line, maxsplit=1)
            title_num = parts[0].strip()
            title = f"khoản {title_num}"
            content = parts[1].strip() if len(parts) > 1 else ""
            extra_content, index = collect_content(text, index + 1)
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            # Build path considering no chapter case
            if chuong_title:
                parent_path = f"{so_hieu}_{chuong_title}"
            else:
                parent_path = so_hieu

            if muc_title:
                parent_path += f"_{muc_title}"
            parent_path += f"_{dieu_title}"

            full_path = f"{parent_path}_{title}"
            khoan_id = generate_id(full_path)
            result[khoan_id] = {
                "id": khoan_id,
                "title": title,
                "content": content,
                "parent_id": dieu_id,
                "so_hieu": so_hieu,
                "full_path": full_path
            }

            khoan_title = title
            continue

        # ---- Điểm (Point) ----
        match = re.match(r"^([^\W\d_])\)", line, re.UNICODE)
        if match:
            letter = match.group(1)
            title = f"điểm {letter}"
            parts = re.split(r"\)", line, maxsplit=1)
            content = parts[1].strip() if len(parts) > 1 else ""
            extra_content, index = collect_content(text, index + 1)
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            # Build path considering no chapter case
            if chuong_title:
                parent_path = f"{so_hieu}_{chuong_title}"
            else:
                parent_path = so_hieu

            if muc_title:
                parent_path += f"_{muc_title}"
            parent_path += f"_{dieu_title}_{khoan_title}"

            full_path = f"{parent_path}_{title}"
            diem_id = generate_id(full_path)
            result[diem_id] = {
                "id": diem_id,
                "title": title,
                "content": content,
                "parent_id": khoan_id,
                "so_hieu": so_hieu,
                "full_path": full_path
            }
            index += 1
            continue

        index += 1
    return result