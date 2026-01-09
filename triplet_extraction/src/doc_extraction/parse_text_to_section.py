import re

from triplet_extraction.src.doc_extraction.utils import clean_content, generate_id


def collect_content(output_text, start_index):
    """
    Collect content lines until hitting a structural marker OUTSIDE of quotes.
    Returns: (content_string, next_index)
    """
    content_lines = []
    i = start_index
    in_quotes = False

    # Define opening and closing quote characters
    OPENING_QUOTES = ('"', '"', '“', '「', '『')
    CLOSING_QUOTES = ('"', '"', '”', '」', '』')
    SENTENCE_ENDINGS = ('.', '。', '!', '?', ':', ';', '」', '』', '"', '"', ')', ']')

    while i < len(output_text):
        next_line = output_text[i].strip()

        if next_line:
            # 🔑 snapshot trạng thái quote TRƯỚC dòng này
            in_quotes_before = in_quotes

            # Process each character to track quote state
            for char in next_line:
                if char in OPENING_QUOTES:
                    in_quotes = True
                elif char in CLOSING_QUOTES:
                    in_quotes = False
                elif char == '"':  # ASCII quote toggles
                    in_quotes = not in_quotes

            # Only check for structural markers when NOT inside quotes
            # ⚠️ dùng trạng thái TRƯỚC dòng
            if not in_quotes_before:
                lower_line = next_line.lower()
                if (re.match(r"^điều\s+[ivxlcdm]+\s*[.:]?", lower_line)
                        or re.match(r"^điều\s+\d+\s*[.:]?", lower_line)
                        or re.match(r"^chương\s+[ivxlcdm]+", lower_line)
                        or re.match(r"^chương\s+\d+", lower_line)
                        or re.match(r"^mục\s+[ivxlcdm]+", lower_line)
                        or re.match(r"^mục\s+\d+", lower_line)
                        or re.match(r"^phụ\s+lục\s+[ivxlcdm]+\s*[.:]?", lower_line)
                        or re.match(r"^phụ\s+lục\s+\d+\s*[.:]?", lower_line)
                        or re.match(r"^\d+\.\s+", next_line)
                        or re.match(r"^[a-zA-ZđĐ]\)\s+", next_line)):
                    break

            # Add line to content
            content_lines.append(next_line)

        i += 1

    return "\n".join(content_lines).strip() or "", i


def parse_document(input_text, so_hieu):
    """
    Parse Vietnamese legal document structure and store in database.
    Handles hierarchy: Chương (Chapter) -> Mục (Section) -> Điều (Article)
    -> Khoản (Clause) -> Điểm (Point) and Phụ lục (Appendix).

    Edge case: Documents without chapters are supported - elements will be
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
    chuong_id = muc_id = dieu_id = khoan_id = phu_luc_id = None
    chuong_title = muc_title = dieu_title = khoan_title = phu_luc_title = ""

    last_article_num = 0  # Track last article number for validation
    
    while index < len(text):
        line = text[index].strip()
        next_line = text[index + 1].strip() if index < len(text) - 1 else ""

        # ---- Phụ lục (Appendix) ----
        match = re.match(r"^(phụ\s+lục\s+[ivxlcdm\d]+)(?:[.\s]+(.*))?", line.lower())
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

            # Reset hierarchy (Phụ lục should not inherit chương/mục/điều)
            phu_luc_title = title
            chuong_id = muc_id = dieu_id = khoan_id = None
            chuong_title = muc_title = dieu_title = khoan_title = ""
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
                "full_path": full_path,
                "type": "chương",
                "is_amendment": False
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

            if phu_luc_id:
                parent_id = phu_luc_id
            else:
                parent_id = chuong_id

            # Build path considering no chapter case
            if chuong_title:
                full_path = f"{so_hieu}_{chuong_title}_{title}"
            elif phu_luc_title:
                full_path = f"{so_hieu}_{phu_luc_title}_{title}"
            else:
                full_path = f"{so_hieu}_{title}"

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
            
            # Extract article number and validate order
            article_num_str = match.group(1)
            is_valid_article = False
            try:
                current_article_num = int(article_num_str)
                # Check if article number increases continuously (must be previous + 1)
                if current_article_num == last_article_num + 1:
                    is_valid_article = True
                    last_article_num = current_article_num
            except ValueError:
                # Roman numerals - treat as content for now
                pass
            
            # If not a valid article header, treat as content and skip
            if not is_valid_article:
                index += 1
                continue
            
            # Extract title (e.g., "điều 1")
            title = f"điều {article_num_str}"
            # Split at first dot or colon after article number to get content
            parts = re.split(r"^điều\s+[ivxlcdm\d]+[.:]\s*", line.lower(), maxsplit=1)
            content = parts[1].strip() if len(parts) > 1 else ""
            
            # Check if this is an amendment article (e.g., "Sửa đổi, bổ sung")
            is_amendment = bool(AMENDMENT_PATTERN.search(content))

            # Check if this is under an appendix
            is_phu_luc = phu_luc_id is not None

            extra_content, index = collect_content(text, index + 1)
            if extra_content:
                content = f"{content}\n{extra_content}" if content else extra_content
            content = clean_content(content)

            if muc_id:
                parent_id = muc_id
            elif phu_luc_id:
                parent_id = phu_luc_id
            else:
                parent_id = chuong_id

            # Build path considering no chapter case
            if chuong_title:
                parent_path = f"{so_hieu}_{chuong_title}"
            elif phu_luc_title:
                parent_path = f"{so_hieu}_{phu_luc_title}"
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
            elif muc_id:
                parent_id = muc_id
            elif phu_luc_id:
                parent_id = phu_luc_id
            else:
                parent_id = chuong_id

            # Build path considering no chapter case
            if chuong_title:
                parent_path = f"{so_hieu}_{chuong_title}"
            elif phu_luc_title:
                parent_path = f"{so_hieu}_{phu_luc_title}"
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
                "type": "điểm",
                "full_path": full_path,
                "is_amendment": is_amendment,
                "is_phu_luc": is_phu_luc
            }
            continue

        index += 1
    return result