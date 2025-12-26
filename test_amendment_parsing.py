"""
Test script to verify amendment document parsing for documents like 90/2025/QH15
"""
from triplet_extraction.src.doc_extraction.parse_text_to_section import parse_document

# Sample text from amendment law
test_text = """Điều 1. Sửa đổi, bổ sung một số điều của Luật Đấu thầu
1. Sửa đổi, bổ sung, bãi bỏ một số khoản của Điều 2 như sau:
a) Sửa đổi, bổ sung đoạn đầu khoản 1 như sau:
"1. Hoạt động lựa chọn nhà thầu của cơ quan, tổ chức, cá nhân sử dụng vốn
ngân sách nhà nước theo quy định của Luật Ngân sách nhà nước, vốn từ nguồn
thu hợp pháp theo quy định của pháp luật của các cơ quan nhà nước, đơn vị sự
nghiệp công lập, trừ trường hợp quy định tại các khoản 7, 8 và 9 Điều 3 của Luật
này để:";
b) Bãi bỏ khoản 2;
c) Sửa đổi, bổ sung khoản 4 như sau:
"4. Tổ chức, cá nhân có hoạt động đấu thầu không thuộc trường hợp quy
định tại khoản 1 và khoản 3 Điều này được tự quyết định chọn áp dụng toàn bộ
hoặc các điều, khoản, điểm cụ thể của Luật này.".
2. Sửa đổi, bổ sung một số điểm, khoản của Điều 3 như sau:
a) Sửa đổi, bổ sung khoản 1 như sau:
"1. Hoạt động đấu thầu thuộc phạm vi điều chỉnh của Luật này phải tuân thủ
quy định của Luật này và quy định khác của pháp luật có liên quan.";
b) Sửa đổi, bổ sung đoạn đầu khoản 7 như sau:
"7. Cơ quan, tổ chức, doanh nghiệp được tự quyết định việc mua sắm trên
cơ sở bảo đảm công khai, minh bạch, hiệu quả và trách nhiệm giải trình.";
3. Sửa đổi, bổ sung một số khoản của Điều 4 như sau:
a) Sửa đổi, bổ sung khoản 1 như sau:
"1. Bên mời thầu là cơ quan có thẩm quyền chấp thuận chủ trương đầu tư.";
Điều 2. Điều khoản thi hành
Luật này có hiệu lực thi hành từ ngày 01 tháng 01 năm 2026."""

# Parse the document
result = parse_document(test_text, "90/2025/QH15")

print(f"Total sections parsed: {len(result)}\n")
print("=" * 80)

# Display the hierarchy
for section_id, section_data in result.items():
    indent = "  " * section_data["full_path"].count("_")
    is_amendment_flag = " [AMENDMENT]" if section_data.get("is_amendment") else ""
    print(f"{indent}{section_data['title']}{is_amendment_flag}")
    if section_data.get("content"):
        # Show full content for points to verify quotes are included
        if "điểm" in section_data['title']:
            print(f"{indent}  → FULL CONTENT:")
            for line in section_data["content"].split("\n"):
                print(f"{indent}     {line}")
        else:
            content_preview = section_data["content"][:200].replace("\n", " ")
            if len(section_data["content"]) > 200:
                content_preview += "..."
            print(f"{indent}  → {content_preview}")
    print(f"{indent}  Full path: {section_data['full_path']}")
    print()

print("=" * 80)
print("\nKey observations:")
print("1. ✅ Điều 1 should be marked as amendment article")
print("2. ✅ Numbered items (1., 2., 3.) under Điều 1 should be 'khoản X (sửa đổi)'")
print("3. ✅ Lettered items (a), b), c)) should be 'điểm X (sửa đổi)'")
print("4. ✅ Quoted sections (e.g., \"1. Hoạt động...\") should be part of content,")
print("      NOT parsed as separate khoản")
print("5. Note: Short items like 'b) Bãi bỏ khoản 2;' may be merged into")
print("         previous section content")
