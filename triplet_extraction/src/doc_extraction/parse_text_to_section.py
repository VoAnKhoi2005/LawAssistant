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
        if (next_line.lower().startswith("điều")
            or next_line.lower().startswith("chương")
            or next_line.lower().startswith("mục")
            or re.match(r"^\s*(\d+\.\s*|[a-zA-ZđĐ]\)\s*)", next_line)):
            break
        if next_line:
            content_lines.append(next_line)
        i += 1
    return "\n".join(content_lines).strip() or None, i

def parse_document(output_text, so_hieu):
    """
    Parse Vietnamese legal document structure and store in database.
    Handles hierarchy: Chương (Chapter) -> Mục (Section) -> Điều (Article)
    -> Khoản (Clause) -> Điểm (Point)
    """
    index = 0
    result = {}
    # Track current parent IDs and titles for hierarchy
    chuong_id = muc_id = dieu_id = khoan_id = None
    chuong_title = muc_title = dieu_title = khoan_title = ""

    while index < len(output_text):
        line = output_text[index].strip()
        next_line = output_text[index + 1].strip() if index < len(output_text) - 1 else ""

        if (("............." in line or "--------------" in line)
                or ("............." in next_line or "--------------" in next_line)):
            index = index + 1
            continue

        # ---- Chương (Chapter) ----
        match = re.match(r"^(chương\s+[ivxlcdm\d]+)(?:[.\s]+(.*))?", line.lower())
        if match:
            title = match.group(1).strip()                          # e.g. "chương i"
            inline_content = match.group(2).strip() if match.group(2) else ""  # e.g. "quy định chung"

            # Collect following content
            extra_content, index = collect_content(output_text, index + 1)
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
            title = match.group(1).strip()                          # e.g. "mục 2"
            inline_content = match.group(2).strip() if match.group(2) else ""  # e.g. "quy định chung"

            # Collect following content
            extra_content, index = collect_content(output_text, index + 1)
            content = inline_content
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            full_path = f"{so_hieu}_{chuong_title}_{title}"
            muc_id = generate_id(full_path)
            result[muc_id] = {
                "id": muc_id,
                "title": title,
                "content": content,
                "parent_id": chuong_id,
                "so_hieu": so_hieu,
                "full_path": full_path
            }

            # Reset hierarchy
            muc_title = title
            dieu_id = khoan_id = None
            dieu_title = khoan_title = ""
            continue

        # ---- Điều (Article) ----
        if re.match(r"^điều\s+[ivxlcdm\d]+", line.lower()):
            parts = re.split(r"\.", line.lower(), maxsplit=1)
            title = parts[0].strip()
            content = parts[1].strip() if len(parts) > 1 else ""
            extra_content, index = collect_content(output_text, index + 1)
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            parent_id = muc_id if muc_id else chuong_id
            parent_path = f"{so_hieu}_{chuong_title}"
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
            extra_content, index = collect_content(output_text, index + 1)
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            parent_path = f"{so_hieu}_{chuong_title}"
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
            extra_content, index = collect_content(output_text, index + 1)
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            parent_path = f"{so_hieu}_{chuong_title}"
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
            continue
        index += 1
    return result