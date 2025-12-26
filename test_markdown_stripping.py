"""
Test markdown stripping functionality
"""
import re

def strip_markdown_formatting(text):
    """
    Strip markdown formatting from text without changing content.
    Removes markdown syntax but preserves the actual text content.
    """
    if not text:
        return text
    
    # Remove bold/italic markers (**text**, *text*, __text__, _text_)
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # **bold**
    text = re.sub(r'__([^_]+)__', r'\1', text)      # __bold__
    text = re.sub(r'\*([^*]+)\*', r'\1', text)      # *italic*
    text = re.sub(r'_([^_]+)_', r'\1', text)        # _italic_
    
    # Remove headers (# Header) but keep the text
    text = re.sub(r'^#{1,6}\s+(.+)$', r'\1', text, flags=re.MULTILINE)
    
    # Remove links [text](url) but keep the text
    text = re.sub(r'\[([^\]]+)\]\([^\)]+\)', r'\1', text)
    
    # Remove inline code markers `code`
    text = re.sub(r'`([^`]+)`', r'\1', text)
    
    # Remove horizontal rules (---, ***, ___)
    text = re.sub(r'^[\*\-_]{3,}$', '', text, flags=re.MULTILINE)
    
    # Remove blockquote markers (> text)
    text = re.sub(r'^>\s+', '', text, flags=re.MULTILINE)
    
    # Remove list markers (-, *, +, 1.) but preserve indent structure
    text = re.sub(r'^[\s]*[-\*\+]\s+', '', text, flags=re.MULTILINE)
    text = re.sub(r'^[\s]*\d+\.\s+(?![^\s])', '', text, flags=re.MULTILINE)
    
    return text

# Test case 1: Bold text
test1 = "**Điều 1.** Phạm vi điều chỉnh"
expected1 = "Điều 1. Phạm vi điều chỉnh"
result1 = strip_markdown_formatting(test1)
print(f"Test 1 - Bold text:")
print(f"  Input:    {test1}")
print(f"  Expected: {expected1}")
print(f"  Result:   {result1}")
print(f"  Status:   {'✅ PASS' if result1 == expected1 else '❌ FAIL'}\n")

# Test case 2: Headers
test2 = "# Điều 1. Phạm vi điều chỉnh\nNội dung điều"
expected2 = "Điều 1. Phạm vi điều chỉnh\nNội dung điều"
result2 = strip_markdown_formatting(test2)
print(f"Test 2 - Headers:")
print(f"  Input:    {repr(test2)}")
print(f"  Expected: {repr(expected2)}")
print(f"  Result:   {repr(result2)}")
print(f"  Status:   {'✅ PASS' if result2 == expected2 else '❌ FAIL'}\n")

# Test case 3: Links
test3 = "Theo [Luật Đất đai](https://example.com) năm 2024"
expected3 = "Theo Luật Đất đai năm 2024"
result3 = strip_markdown_formatting(test3)
print(f"Test 3 - Links:")
print(f"  Input:    {test3}")
print(f"  Expected: {expected3}")
print(f"  Result:   {result3}")
print(f"  Status:   {'✅ PASS' if result3 == expected3 else '❌ FAIL'}\n")

# Test case 4: Real amendment text with markdown
test4 = """**Điều 1.** Sửa đổi, bổ sung một số điều của Luật Đấu thầu
1. Sửa đổi, bổ sung, bãi bỏ một số khoản của **Điều 2** như sau:
a) Sửa đổi, bổ sung đoạn đầu khoản 1 như sau:
"1. Hoạt động lựa chọn nhà thầu của cơ quan, tổ chức..."""

expected4 = """Điều 1. Sửa đổi, bổ sung một số điều của Luật Đấu thầu
1. Sửa đổi, bổ sung, bãi bỏ một số khoản của Điều 2 như sau:
a) Sửa đổi, bổ sung đoạn đầu khoản 1 như sau:
"1. Hoạt động lựa chọn nhà thầu của cơ quan, tổ chức..."""

result4 = strip_markdown_formatting(test4)
print(f"Test 4 - Real amendment text:")
print(f"  Input (first 100 chars):    {test4[:100]}")
print(f"  Expected (first 100 chars): {expected4[:100]}")
print(f"  Result (first 100 chars):   {result4[:100]}")
print(f"  Status:   {'✅ PASS' if result4 == expected4 else '❌ FAIL'}\n")

# Test case 5: Ensure numbered clauses are preserved
test5 = """Điều 1. Title
1. First clause
2. Second clause
a) Point a
b) Point b"""

result5 = strip_markdown_formatting(test5)
print(f"Test 5 - Preserve legal structure:")
print(f"  Input:")
for line in test5.split('\n'):
    print(f"    {line}")
print(f"  Result:")
for line in result5.split('\n'):
    print(f"    {line}")
print(f"  Check: '1. First clause' preserved: {'✅ YES' if '1. First clause' in result5 else '❌ NO'}")
print(f"  Check: 'a) Point a' preserved: {'✅ YES' if 'a) Point a' in result5 else '❌ NO'}\n")

print("=" * 80)
print("Summary: Markdown stripping preserves legal document structure")
print("while removing formatting markers like **bold**, # headers, etc.")
