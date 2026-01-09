import re

from triplet_extraction.src.doc_extraction.utils import clean_content, generate_id

# Define reusable regex patterns
PHAN_PATTERN = r"^phần\s+thứ"
CHUONG_PATTERN = r"^chương\s+[ivxlcdm\d]+"
MUC_PATTERN = r"^mục\s+[ivxlcdm\d]+"
TIEU_MUC_PATTERN = r"^tiểu\s+mục\s+\d+"
DIEU_PATTERN = r"^điều\s+[ivxlcdm\d]+\s*[.:]?"
PHU_LUC_PATTERN = r"^(phụ\s+lục)(?:\s+([ivxlcdm\d]+))?(?:[.\s]+(.*))?$"

MARKER_PATTERNS = [
    DIEU_PATTERN,
    PHAN_PATTERN,
    CHUONG_PATTERN,
    MUC_PATTERN,
    TIEU_MUC_PATTERN,
    PHU_LUC_PATTERN,
    r"^\d+\.\s+",
    r"^[a-zA-ZđĐ]\)\s+",
]
MARKER_REGEXES = [re.compile(p) for p in MARKER_PATTERNS]

def is_marker_line(line: str) -> bool:
    line = line.strip().lower()
    return any(r.match(line) for r in MARKER_REGEXES)


def prev_line_ends_sentence(lines, current_index, sentence_endings):
    def find_prev(idx):
        while idx >= 0:
            line = lines[idx].strip()
            if line:
                return idx, line
            idx -= 1
        return None, None

    j, prev_line = find_prev(current_index - 1)
    if not prev_line:
        return True
    if prev_line.endswith(sentence_endings):
        return True
    else:
        lower = prev_line.lower()
        if (
            re.match(DIEU_PATTERN, lower)
            or re.match(PHAN_PATTERN, lower)
            or re.match(CHUONG_PATTERN, lower)
            or re.match(MUC_PATTERN, lower)
            or re.match(TIEU_MUC_PATTERN, lower)
        ):
            return True

        k, prev_prev_line = find_prev(j - 1)
        if not prev_prev_line:
            return True

        lower = prev_prev_line.lower()
        if (
            re.match(PHAN_PATTERN, lower)
            or re.match(CHUONG_PATTERN, lower)
            or re.match(MUC_PATTERN, lower)
            or re.match(TIEU_MUC_PATTERN, lower)
        ):
            return True
    return False


def collect_content(output_text, start_index):
    """
    Collect content lines until hitting a structural marker OUTSIDE of quotes.
    Returns: (content_string, next_index)
    """
    content_lines = []
    i = start_index
    in_quotes = False

    OPENING_QUOTES = ('"', '“', '「', '『')
    CLOSING_QUOTES = ('"', '”', '」', '』')
    SENTENCE_ENDINGS = ('.', '。', '!', '?', ':', ';', '」', '』', '"', ')', ']', '"', '”', '」', '』')

    while i < len(output_text):
        line = output_text[i].strip()

        if line:
            in_quotes_before = in_quotes

            # Track quote state
            for ch in line:
                if ch in OPENING_QUOTES:
                    in_quotes = True
                elif ch in CLOSING_QUOTES:
                    in_quotes = False
                elif ch == '"':
                    in_quotes = not in_quotes

            if not in_quotes_before and is_marker_line(line):
                if re.match(r"^(phụ\s+lục)(?:\s+([ivxlcdm\d]+))?(?:[.\s]+(.*))?$", line.lower()):
                    break

                if prev_line_ends_sentence(output_text, i, SENTENCE_ENDINGS):
                    break

            content_lines.append(line)

        i += 1

    return "\n".join(content_lines).strip() or "", i


def parse_document(input_text, so_hieu):
    """
    Parse Vietnamese legal document structure and store in database.
    Handles hierarchy: Phần thứ (Part) -> Chương (Chapter) -> Mục (Section) -> Tiểu mục (Subsection) -> Điều (Article)
    -> Khoản (Clause) -> Điểm (Point) and Phụ lục (Appendix).

    Edge case: Documents without parts/chapters are supported - elements will be
    organized directly under the document (so_hieu).
    """

    AMENDMENT_PATTERN = re.compile(
        r"^\s*(sửa đổi|bổ sung|bãi bỏ|thay thế)\b",
        flags=re.IGNORECASE
    )

    text = [line.strip() for line in input_text.splitlines() if line.strip()]
    index = 0
    result = {}
    # Track current parent IDs and titles for hierarchy
    phan_id = chuong_id = muc_id = tieu_muc_id = dieu_id = khoan_id = phu_luc_id = None
    phan_title = chuong_title = muc_title = tieu_muc_title = dieu_title = khoan_title = phu_luc_title = ""

    # Track full_path occurrences to ensure uniqueness
    full_path_counts = {}

    last_article_num = 0  # Track last article number for validation
    
    def make_unique_path(base_path):
        """Ensure full_path is unique by adding suffix if needed."""
        if base_path not in full_path_counts:
            full_path_counts[base_path] = 0
            return base_path
        else:
            # Path already exists, need to add suffix to both
            full_path_counts[base_path] += 1
            count = full_path_counts[base_path]
            
            # Update the existing entry with suffix if it's the first duplicate
            if count == 1:
                # Find and update the original entry
                for entry_id, entry in result.items():
                    if entry.get("full_path") == base_path:
                        new_path = f"{base_path}_1"
                        entry["full_path"] = new_path
                        entry["id"] = generate_id(new_path)
                        # Update result dict key
                        result[entry["id"]] = result.pop(entry_id)
                        break
            
            # Return new path with incremented suffix
            return f"{base_path}_{count + 1}"
    
    while index < len(text):
        line = text[index].strip()
        next_line = text[index + 1].strip() if index < len(text) - 1 else ""

        # ---- Phụ lục (Appendix) ----
        match = re.match(PHU_LUC_PATTERN, line.lower())
        if match:
            base_title = match.group(1).strip()
            appendix_no = match.group(2)
            inline_title = match.group(3) or ""

            # Title đầy đủ của Phụ lục
            title = f"{base_title} {appendix_no}".strip()

            # Collect following content
            extra_content, index = collect_content(text, index + 1)

            content_parts = []
            if inline_title:
                content_parts.append(inline_title)
            if extra_content:
                content_parts.append(extra_content)

            content = clean_content("\n".join(content_parts))

            base_path = f"{so_hieu}_{title}"
            full_path = make_unique_path(base_path)
            phu_luc_id = generate_id(full_path)

            result[phu_luc_id] = {
                "id": phu_luc_id,
                "title": title,
                "content": content,
                "parent_id": None,
                "so_hieu": so_hieu,
                "full_path": full_path,
                "type": "phụ_lục",
            }

            # Reset hierarchy (Phụ lục KHÔNG kế thừa Phần/Chương/Mục/Tiểu mục/Điều)
            phu_luc_title = title
            phan_id = chuong_id = muc_id = tieu_muc_id = dieu_id = khoan_id = None
            phan_title = chuong_title = muc_title = tieu_muc_title = dieu_title = khoan_title = ""
            continue

        # ---- Phần thứ (Part) ----
        if re.match(PHAN_PATTERN, line.lower()):
            # Extract the full title from the line (everything until content or newline)
            parts = line.split('.', 1)  # Split at first dot if exists
            if len(parts) > 1:
                title = parts[0].strip().lower()
                inline_content = parts[1].strip()
            else:
                # Check if there's a colon or just whitespace separation
                title_match = re.match(r'^([^\n:]+?)(?:[:]\s*(.*))?$', line, re.IGNORECASE)
                if title_match:
                    title = title_match.group(1).strip().lower()
                    inline_content = title_match.group(2).strip() if title_match.group(2) else ""
                else:
                    title = line.strip().lower()
                    inline_content = ""

            # Collect following content
            extra_content, index = collect_content(text, index + 1)
            content = inline_content
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            base_path = f"{so_hieu}_{title}"
            full_path = make_unique_path(base_path)
            phan_id = generate_id(full_path)
            result[phan_id] = {
                "id": phan_id,
                "title": title,
                "content": content,
                "parent_id": None,
                "so_hieu": so_hieu,
                "full_path": full_path,
                "type": "phần",
                "is_amendment": False
            }

            # Reset hierarchy
            phan_title = title
            chuong_id = muc_id = tieu_muc_id = dieu_id = khoan_id = None
            chuong_title = muc_title = tieu_muc_title = dieu_title = khoan_title = ""
            continue

        # ---- Chương (Chapter) ----
        match = re.match(f"({CHUONG_PATTERN})(?:[.\\s]+(.*))?", line.lower())
        if match:
            title = match.group(1).strip()
            inline_content = match.group(2).strip() if match.group(2) else ""

            # Collect following content
            extra_content, index = collect_content(text, index + 1)
            content = inline_content
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            # Parent is Phần if exists
            parent_id = phan_id

            # Build path considering no part case
            if phan_title:
                base_path = f"{so_hieu}_{phan_title}_{title}"
            else:
                base_path = f"{so_hieu}_{title}"

            full_path = make_unique_path(base_path)
            chuong_id = generate_id(full_path)
            result[chuong_id] = {
                "id": chuong_id,
                "title": title,
                "content": content,
                "parent_id": parent_id,
                "so_hieu": so_hieu,
                "full_path": full_path,
                "type": "chương",
                "is_amendment": False
            }

            # Reset hierarchy
            chuong_title = title
            muc_id = tieu_muc_id = dieu_id = khoan_id = None
            muc_title = tieu_muc_title = dieu_title = khoan_title = ""
            continue

        # ---- Mục (Section) ----
        match = re.match(f"({MUC_PATTERN})(?:[.\\s]+(.*))?", line.lower())
        if match:
            title = match.group(1).strip()
            inline_content = match.group(2).strip() if match.group(2) else ""

            # Collect following content
            extra_content, index = collect_content(text, index + 1)
            content = inline_content
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            if phu_luc_id:
                parent_id = phu_luc_id
            else:
                parent_id = chuong_id

            # Build path considering hierarchy
            if phan_title:
                if chuong_title:
                    base_path = f"{so_hieu}_{phan_title}_{chuong_title}_{title}"
                else:
                    base_path = f"{so_hieu}_{phan_title}_{title}"
            elif chuong_title:
                base_path = f"{so_hieu}_{chuong_title}_{title}"
            elif phu_luc_title:
                base_path = f"{so_hieu}_{phu_luc_title}_{title}"
            else:
                base_path = f"{so_hieu}_{title}"

            full_path = make_unique_path(base_path)
            muc_id = generate_id(full_path)
            result[muc_id] = {
                "id": muc_id,
                "title": title,
                "content": content,
                "parent_id": parent_id,
                "so_hieu": so_hieu,
                "full_path": full_path,
                "type": "mục",
                "is_amendment": False,
                "is_phu_luc": phu_luc_id is not None
            }

            # Reset hierarchy
            muc_title = title
            tieu_muc_id = dieu_id = khoan_id = None
            tieu_muc_title = dieu_title = khoan_title = ""
            continue

        # ---- Tiểu mục (Subsection) ----
        match = re.match(r"^(tiểu\s+mục\s+\d+)(?:[.\s]+(.*))?", line.lower())
        if match:
            title = match.group(1).strip()
            inline_content = match.group(2).strip() if match.group(2) else ""

            # Collect following content
            extra_content, index = collect_content(text, index + 1)
            content = inline_content
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            if phu_luc_id:
                parent_id = phu_luc_id
            else:
                parent_id = muc_id

            # Build path considering hierarchy
            if phan_title:
                if chuong_title:
                    if muc_title:
                        base_path = f"{so_hieu}_{phan_title}_{chuong_title}_{muc_title}_{title}"
                    else:
                        base_path = f"{so_hieu}_{phan_title}_{chuong_title}_{title}"
                else:
                    base_path = f"{so_hieu}_{phan_title}_{title}"
            elif chuong_title:
                if muc_title:
                    base_path = f"{so_hieu}_{chuong_title}_{muc_title}_{title}"
                else:
                    base_path = f"{so_hieu}_{chuong_title}_{title}"
            elif muc_title:
                base_path = f"{so_hieu}_{muc_title}_{title}"
            elif phu_luc_title:
                base_path = f"{so_hieu}_{phu_luc_title}_{title}"
            else:
                base_path = f"{so_hieu}_{title}"

            full_path = make_unique_path(base_path)
            tieu_muc_id = generate_id(full_path)
            result[tieu_muc_id] = {
                "id": tieu_muc_id,
                "title": title,
                "content": content,
                "parent_id": parent_id,
                "so_hieu": so_hieu,
                "full_path": full_path,
                "type": "tiểu_mục",
                "is_amendment": False,
                "is_phu_luc": phu_luc_id is not None
            }

            # Reset hierarchy
            tieu_muc_title = title
            dieu_id = khoan_id = None
            dieu_title = khoan_title = ""
            continue

        # ---- Điều (Article) ----
        # Match only lines starting with "Điều" followed by number/roman and a dot or colon
        # This excludes references like "quy định tại Điều X" or "khoản Y Điều Z"
        match = re.match(r"^điều\s+([ivxlcdm\d]+)[.:]", line.lower())
        if match:
            article_num_str = match.group(1)

            # Check if this is under an appendix
            is_phu_luc = phu_luc_id is not None
            # if not is_phu_luc:
            #     if article_num_str.isdigit():
            #         current_article_num = int(article_num_str)
            #
            #         if current_article_num != last_article_num + 1:
            #             raise ValueError(
            #                 f"Invalid article order at line {index}: "
            #                 f"expected Điều {last_article_num + 1}, got Điều {current_article_num}"
            #             )
            #         last_article_num = current_article_num
            #     else:
            #         raise ValueError(f"Roman numeral article not supported at line {index}: Điều {article_num_str}")

            # Extract title
            title = f"điều {article_num_str}"
            # Split at first dot or colon after article number to get content
            parts = re.split(r"^điều\s+[ivxlcdm\d]+[.:]\s*", line.lower(), maxsplit=1)
            content = parts[1].strip() if len(parts) > 1 else ""
            
            # Check if this is an amendment article (e.g., "Sửa đổi, bổ sung")
            is_amendment = bool(AMENDMENT_PATTERN.search(content))

            extra_content, index = collect_content(text, index + 1)
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            if tieu_muc_id:
                parent_id = tieu_muc_id
            elif muc_id:
                parent_id = muc_id
            elif phu_luc_id:
                parent_id = phu_luc_id
            else:
                parent_id = chuong_id

            # Build path considering hierarchy
            if phan_title:
                if chuong_title:
                    parent_path = f"{so_hieu}_{phan_title}_{chuong_title}"
                else:
                    parent_path = f"{so_hieu}_{phan_title}"
            elif chuong_title:
                parent_path = f"{so_hieu}_{chuong_title}"
            elif phu_luc_title:
                parent_path = f"{so_hieu}_{phu_luc_title}"
            else:
                parent_path = so_hieu

            if muc_title:
                parent_path += f"_{muc_title}"
            if tieu_muc_title:
                parent_path += f"_{tieu_muc_title}"

            base_path = f"{parent_path}_{title}"
            full_path = make_unique_path(base_path)
            dieu_id = generate_id(full_path)
            result[dieu_id] = {
                "id": dieu_id,
                "title": title,
                "content": content,
                "parent_id": parent_id,
                "so_hieu": so_hieu,
                "full_path": full_path,
                "type": "điều",
                "is_amendment": is_amendment,
                "is_phu_luc": is_phu_luc
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
            content = parts[1].strip() if len(parts) > 1 else ""
            title = f"khoản {title_num}"

            # Check if this is an amendment article (e.g., "Sửa đổi, bổ sung")
            is_amendment = bool(AMENDMENT_PATTERN.search(content))

            is_phu_luc = phu_luc_id is not None
            
            extra_content, index = collect_content(text, index + 1)
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            if dieu_id:
                parent_id = dieu_id
            elif tieu_muc_id:
                parent_id = tieu_muc_id
            elif muc_id:
                parent_id = muc_id
            elif phu_luc_id:
                parent_id = phu_luc_id
            else:
                parent_id = chuong_id

            # Build path considering hierarchy
            if phan_title:
                if chuong_title:
                    parent_path = f"{so_hieu}_{phan_title}_{chuong_title}"
                else:
                    parent_path = f"{so_hieu}_{phan_title}"
            elif chuong_title:
                parent_path = f"{so_hieu}_{chuong_title}"
            elif phu_luc_title:
                parent_path = f"{so_hieu}_{phu_luc_title}"
            else:
                parent_path = so_hieu

            if muc_title:
                parent_path += f"_{muc_title}"
            if tieu_muc_title:
                parent_path += f"_{tieu_muc_title}"
            parent_path += f"_{dieu_title}"

            base_path = f"{parent_path}_{title}"
            full_path = make_unique_path(base_path)
            khoan_id = generate_id(full_path)
            result[khoan_id] = {
                "id": khoan_id,
                "title": title,
                "content": content,
                "parent_id": parent_id,
                "so_hieu": so_hieu,
                "type": "khoản",
                "full_path": full_path,
                "is_amendment": is_amendment,
                "is_phu_luc": is_phu_luc
            }

            khoan_title = title
            continue

        # ---- Điểm (Point) ----
        match = re.match(r"^([^\W\d_])\)", line, re.UNICODE)
        if match:
            letter = match.group(1)
            parts = re.split(r"\)", line, maxsplit=1)
            content = parts[1].strip() if len(parts) > 1 else ""
            title = f"điểm {letter}"

            # Check if this is an amendment article (e.g., "Sửa đổi, bổ sung")
            is_amendment = bool(AMENDMENT_PATTERN.search(content))

            is_phu_luc = phu_luc_id is not None
            
            extra_content, index = collect_content(text, index + 1)
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            # Build path considering hierarchy
            if phan_title:
                if chuong_title:
                    parent_path = f"{so_hieu}_{phan_title}_{chuong_title}"
                else:
                    parent_path = f"{so_hieu}_{phan_title}"
            elif chuong_title:
                parent_path = f"{so_hieu}_{chuong_title}"
            else:
                parent_path = so_hieu

            if muc_title:
                parent_path += f"_{muc_title}"
            if tieu_muc_title:
                parent_path += f"_{tieu_muc_title}"
            parent_path += f"_{dieu_title}_{khoan_title}"

            base_path = f"{parent_path}_{title}"
            full_path = make_unique_path(base_path)
            diem_id = generate_id(full_path)
            result[diem_id] = {
                "id": diem_id,
                "title": title,
                "content": content,
                "parent_id": khoan_id,
                "so_hieu": so_hieu,
                "type": "điểm",
                "full_path": full_path,
                "is_amendment": is_amendment,
                "is_phu_luc": is_phu_luc
            }
            continue

        index += 1
    return result