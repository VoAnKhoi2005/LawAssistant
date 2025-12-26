# Table Search Result Extraction Guide

This directory contains examples and guides for extracting table data from search results with support for filters and multiple pages.

## 📁 Files Overview

### 1. `Hệ thống văn bản.html`
- Saved HTML page containing search results from chinhphu.vn
- Contains a table with 26 land law documents
- Example of a single-page search result

### 2. `extract_table_example.py` ⭐
**Purpose**: Complete working example of extracting data from the saved HTML file

**Features**:
- Extract all table rows and columns
- Parse document codes, dates, abstracts, and attachments
- Filter by date range, keywords, or code patterns
- Export to CSV or pandas DataFrame
- Get pagination information

**Usage**:
```bash
python extract_table_example.py
```

**Example Output**:
```
Found 26 documents
Date range filter (2024): 1 documents
Keyword filter ('Luật Đất'): 8 documents
Pattern filter (QH15): 3 documents
Exported to: extracted_documents.csv
```

### 3. `multi_page_scraping_guide.py` 📚
**Purpose**: Comprehensive guide and examples for multi-page scraping

**Features**:
- URL construction with query parameters
- Pagination handling demonstration
- Form data and filter examples
- Complete scraping guide with best practices
- Error handling and retry logic examples

**Usage**:
```bash
python multi_page_scraping_guide.py
```

### 4. `extracted_documents.csv`
- Generated CSV file with all extracted documents
- Contains columns: document_code, document_id, document_url, issue_date, abstract, attachments

## 🔍 Table Structure Analysis

The search result table has the following structure:

```html
<table class="table search-result">
  <tr>
    <th>Số ký hiệu</th>      <!-- Document Code -->
    <th>Ngày ban hành</th>   <!-- Issue Date -->
    <th>Trích yếu</th>        <!-- Abstract -->
  </tr>
  <tr>
    <td>
      <a href="...">
        <span class="code">31/2024/QH15</span>
      </a>
    </td>
    <td>
      <span class="issued-date">18/01/2024</span>
    </td>
    <td>
      <span class="substract">Luật Đất đai</span>
      <div class="bl-doc-files">
        <a href="...pdf">Tài liệu đính kèm</a>
      </div>
    </td>
  </tr>
</table>
```

## 📊 Data Extracted

Each document contains:
- **document_code**: Document identifier (e.g., "31/2024/QH15")
- **document_id**: Internal database ID
- **document_url**: Link to full document page
- **issue_date**: Date of issuance (DD/MM/YYYY format)
- **abstract**: Document title/summary
- **attachments**: List of attached PDF files with URLs

## 🔧 Filtering Examples

### Filter by Date Range
```python
extractor = TableSearchExtractor("Hệ thống văn bản.html")
documents = extractor.extract_table_data()

# Get documents from 2024
filtered = extractor.filter_by_date_range(
    documents, 
    start_date="01/01/2024",
    end_date="31/12/2024"
)
```

### Filter by Keyword
```python
# Search for documents containing "Luật Đất"
filtered = extractor.filter_by_keyword(documents, "Luật Đất")
```

### Filter by Code Pattern
```python
# Find documents from QH15 session
filtered = extractor.filter_by_code_pattern(documents, r"QH15")
```

## 🌐 Multi-Page Handling

### URL Parameters for Pagination

The website uses URL parameters for filtering and pagination:

```
Base URL: https://chinhphu.vn/he-thong-van-ban

Parameters:
- classid=1          # Document class (1 for laws)
- mode=1             # Search mode
- typegroupid=3      # Type group (3 for land law)
- page=2             # Page number
- keyword=...        # Search keyword
- fromdate=DD/MM/YYYY # Start date
- todate=DD/MM/YYYY   # End date
- maxresults=50      # Items per page
```

### Example URLs

**Page 1 (default)**:
```
https://chinhphu.vn/he-thong-van-ban?classid=1&mode=1&typegroupid=3
```

**Page 2**:
```
https://chinhphu.vn/he-thong-van-ban?classid=1&mode=1&typegroupid=3&page=2
```

**With date filter**:
```
https://chinhphu.vn/he-thong-van-ban?classid=1&mode=1&typegroupid=3&fromdate=01/01/2024&todate=31/12/2024
```

**With keyword**:
```
https://chinhphu.vn/he-thong-van-ban?classid=1&mode=1&typegroupid=3&keyword=Luật+Đất
```

## 🚀 Web Scraping Approach

### For Static Content (current HTML)
```python
from bs4 import BeautifulSoup

with open("Hệ thống văn bản.html", 'r', encoding='utf-8') as f:
    soup = BeautifulSoup(f.read(), 'html.parser')
    table = soup.find('table', {'class': 'table search-result'})
```

### For Dynamic Scraping (multiple pages)
```python
import requests
from bs4 import BeautifulSoup
import time

session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
})

all_documents = []
for page in range(1, total_pages + 1):
    url = f"https://chinhphu.vn/he-thong-van-ban?classid=1&page={page}"
    response = session.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Extract documents from this page
    documents = extract_table_data(soup)
    all_documents.extend(documents)
    
    time.sleep(1)  # Rate limiting
```

### For JavaScript-Heavy Sites
```python
from selenium import webdriver
from selenium.webdriver.common.by import By

driver = webdriver.Chrome()
driver.get(url)

# Wait for table to load
driver.implicitly_wait(10)

# Extract data
table = driver.find_element(By.CLASS_NAME, "table.search-result")
html = driver.page_source

# Parse with BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
```

## 📈 Pagination Information

The page displays pagination info in format: `"1 - 26 | 26"`
- First number: Start index
- Second number: End index
- Third number: Total items

To calculate total pages:
```python
total_pages = (total_items + items_per_page - 1) // items_per_page
```

Example: 150 items with 26 per page = 6 pages

## ⚠️ Best Practices

### Rate Limiting
```python
import time

for page in pages:
    fetch_page(page)
    time.sleep(1)  # Wait 1 second between requests
```

### Error Handling
```python
try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.exceptions.RequestException as e:
    print(f"Error: {e}")
    # Log and continue or retry
```

### Progress Tracking
```python
from tqdm import tqdm

for i, page in enumerate(tqdm(pages, desc="Scraping")):
    documents = fetch_and_parse(page)
    save_intermediate(documents, f"page_{i}.json")
```

### Respect robots.txt
```python
from urllib.robotparser import RobotFileParser

rp = RobotFileParser()
rp.set_url("https://chinhphu.vn/robots.txt")
rp.read()

if rp.can_fetch("*", url):
    # OK to scrape
    pass
```

## 📚 Dependencies

```bash
pip install beautifulsoup4 pandas lxml requests
```

For advanced scraping:
```bash
pip install selenium playwright
```

## 🎯 Key Concepts Demonstrated

1. **HTML Parsing**: Using BeautifulSoup to extract table data
2. **Data Filtering**: Multiple filtering methods (date, keyword, pattern)
3. **Pagination Handling**: URL construction and page iteration
4. **Data Export**: Converting to DataFrame and CSV
5. **Error Handling**: Robust extraction with error management
6. **URL Parameters**: Understanding query string manipulation
7. **Rate Limiting**: Respectful scraping practices

## 📝 Summary

This guide shows how to:
✅ Extract table data from HTML files
✅ Filter results by various criteria
✅ Handle pagination across multiple pages
✅ Build URLs with query parameters
✅ Export data to CSV/DataFrame
✅ Follow web scraping best practices

For questions or issues, refer to:
- `extract_table_example.py` for working code
- `multi_page_scraping_guide.py` for comprehensive examples
