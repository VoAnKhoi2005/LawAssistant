"""
Example script to extract table data from search results with filters and pagination
This demonstrates how to parse the saved HTML files and extract structured data from the table.
"""

from bs4 import BeautifulSoup
import pandas as pd
import re
from typing import List, Dict, Optional
from urllib.parse import urlparse, parse_qs


class TableSearchExtractor:
    """
    Extracts search result table data from HTML files with support for:
    - Filtering by date range, document code, keywords
    - Multiple page handling
    - Structured data extraction
    """
    
    def __init__(self, html_file_path: str):
        """
        Initialize the extractor with HTML files path
        
        Args:
            html_file_path: Path to the HTML files containing search results
        """
        self.html_file_path = html_file_path
        with open(html_file_path, 'r', encoding='utf-8') as f:
            self.soup = BeautifulSoup(f.read(), 'html.parser')
    
    def extract_table_data(self) -> List[Dict]:
        """
        Extract all rows from the search result table
        
        Returns:
            List of dictionaries containing document information
        """
        documents = []
        
        # Find the table with class "table search-result"
        table = self.soup.find('table', {'class': 'table search-result'})
        
        if not table:
            print("Table not found!")
            return documents
        
        # Find all table rows (skip header row)
        rows = table.find_all('tr')
        
        for row in rows[1:]:  # Skip the header row
            cols = row.find_all('td')
            
            if len(cols) >= 3:
                # Extract data from each column
                doc_data = self._extract_row_data(cols)
                if doc_data:
                    documents.append(doc_data)
        
        return documents
    
    def _extract_row_data(self, cols: List) -> Optional[Dict]:
        """
        Extract data from a single table row
        
        Args:
            cols: List of table columns (td elements)
            
        Returns:
            Dictionary containing document information
        """
        try:
            # Column 1: Document code and link
            code_col = cols[0]
            code_link = code_col.find('a')
            if not code_link:
                return None
            
            doc_code = code_link.find('span', {'class': 'code'})
            doc_code_text = doc_code.text.strip() if doc_code else ""
            
            # Extract document URL
            doc_url = code_link.get('href', '')
            
            # Extract document ID from URL
            doc_id = self._extract_doc_id(doc_url)
            
            # Column 2: Issue date
            date_col = cols[1]
            issue_date = date_col.find('span', {'class': 'issued-date'})
            issue_date_text = issue_date.text.strip() if issue_date else ""
            
            # Column 3: Abstract/Title and attachments
            abstract_col = cols[2]
            abstract_link = abstract_col.find('a')
            abstract_span = abstract_link.find('span', {'class': 'substract'}) if abstract_link else None
            abstract_text = abstract_span.text.strip() if abstract_span else ""
            
            # Extract attached files
            attachments = self._extract_attachments(abstract_col)
            
            return {
                'document_code': doc_code_text,
                'document_id': doc_id,
                'document_url': doc_url,
                'issue_date': issue_date_text,
                'abstract': abstract_text,
                'attachments': attachments
            }
            
        except Exception as e:
            print(f"Error extracting row data: {e}")
            return None
    
    def _extract_doc_id(self, url: str) -> str:
        """Extract document ID from URL"""
        try:
            parsed = urlparse(url)
            params = parse_qs(parsed.query)
            return params.get('docid', [''])[0]
        except:
            return ""
    
    def _extract_attachments(self, col) -> List[Dict]:
        """Extract attachment links from column"""
        attachments = []
        
        doc_files_div = col.find('div', {'class': 'bl-doc-files'})
        if doc_files_div:
            file_divs = doc_files_div.find_all('div', {'class': 'bl-doc-files'})
            for file_div in file_divs:
                link = file_div.find('a')
                if link:
                    attachments.append({
                        'url': link.get('href', ''),
                        'text': link.text.strip()
                    })
        
        return attachments
    
    def get_pagination_info(self) -> Dict:
        """
        Extract pagination information from the page
        
        Returns:
            Dictionary containing current page, total items, items per page
        """
        page_info_div = self.soup.find('div', {'id': 'document_page_info'})
        
        if page_info_div:
            text = page_info_div.text.strip()
            # Format: "1 - 26 | 26" means items 1-26 out of 26 total
            match = re.match(r'(\d+)\s*-\s*(\d+)\s*\|\s*(\d+)', text)
            if match:
                return {
                    'start_index': int(match.group(1)),
                    'end_index': int(match.group(2)),
                    'total_items': int(match.group(3))
                }
        
        return {
            'start_index': 0,
            'end_index': 0,
            'total_items': 0
        }
    
    def filter_by_date_range(self, documents: List[Dict], 
                            start_date: str = None, 
                            end_date: str = None) -> List[Dict]:
        """
        Filter documents by date range
        
        Args:
            documents: List of document dictionaries
            start_date: Start date in format DD/MM/YYYY
            end_date: End date in format DD/MM/YYYY
            
        Returns:
            Filtered list of documents
        """
        from datetime import datetime
        
        def parse_date(date_str: str) -> Optional[datetime]:
            try:
                return datetime.strptime(date_str, '%d/%m/%Y')
            except:
                return None
        
        filtered = documents
        
        if start_date:
            start_dt = parse_date(start_date)
            if start_dt:
                filtered = [doc for doc in filtered 
                          if parse_date(doc['issue_date']) and 
                             parse_date(doc['issue_date']) >= start_dt]
        
        if end_date:
            end_dt = parse_date(end_date)
            if end_dt:
                filtered = [doc for doc in filtered 
                          if parse_date(doc['issue_date']) and 
                             parse_date(doc['issue_date']) <= end_dt]
        
        return filtered
    
    def filter_by_keyword(self, documents: List[Dict], keyword: str) -> List[Dict]:
        """
        Filter documents by keyword in abstract or document code
        
        Args:
            documents: List of document dictionaries
            keyword: Keyword to search for
            
        Returns:
            Filtered list of documents
        """
        keyword_lower = keyword.lower()
        return [doc for doc in documents 
                if keyword_lower in doc['abstract'].lower() or 
                   keyword_lower in doc['document_code'].lower()]
    
    def filter_by_code_pattern(self, documents: List[Dict], pattern: str) -> List[Dict]:
        """
        Filter documents by code pattern (regex)
        
        Args:
            documents: List of document dictionaries
            pattern: Regex pattern to match document codes
            
        Returns:
            Filtered list of documents
        """
        compiled_pattern = re.compile(pattern, re.IGNORECASE)
        return [doc for doc in documents 
                if compiled_pattern.search(doc['document_code'])]
    
    def to_dataframe(self, documents: List[Dict]) -> pd.DataFrame:
        """
        Convert document list to pandas DataFrame
        
        Args:
            documents: List of document dictionaries
            
        Returns:
            DataFrame with document data
        """
        # Flatten attachments for DataFrame
        data = []
        for doc in documents:
            base_data = {
                'document_code': doc['document_code'],
                'document_id': doc['document_id'],
                'document_url': doc['document_url'],
                'issue_date': doc['issue_date'],
                'abstract': doc['abstract'],
                'num_attachments': len(doc['attachments'])
            }
            
            # Add attachment URLs as separate columns
            for i, att in enumerate(doc['attachments'], 1):
                base_data[f'attachment_{i}_url'] = att['url']
            
            data.append(base_data)
        
        return pd.DataFrame(data)
    
    def export_to_csv(self, documents: List[Dict], output_file: str):
        """
        Export documents to CSV files
        
        Args:
            documents: List of document dictionaries
            output_file: Output CSV files path
        """
        df = self.to_dataframe(documents)
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"Exported {len(documents)} documents to {output_file}")


def example_usage():
    """
    Example usage of the TableSearchExtractor class
    """
    import os
    
    # Path to the HTML files
    current_dir = os.path.dirname(os.path.abspath(__file__))
    html_file = os.path.join(current_dir, "Hệ thống văn bản.html")
    
    # Initialize extractor
    print("Initializing TableSearchExtractor...")
    extractor = TableSearchExtractor(html_file)
    
    # Extract all table data
    print("\n1. Extracting all documents from table...")
    documents = extractor.extract_table_data()
    print(f"   Found {len(documents)} documents")
    
    # Display first few documents
    print("\n2. Sample documents:")
    for i, doc in enumerate(documents[:3], 1):
        print(f"\n   Document {i}:")
        print(f"   - Code: {doc['document_code']}")
        print(f"   - Date: {doc['issue_date']}")
        print(f"   - Abstract: {doc['abstract']}")
        print(f"   - Attachments: {len(doc['attachments'])}")
    
    # Get pagination info
    print("\n3. Pagination information:")
    page_info = extractor.get_pagination_info()
    print(f"   - Start: {page_info['start_index']}")
    print(f"   - End: {page_info['end_index']}")
    print(f"   - Total: {page_info['total_items']}")
    
    # Filter by date range
    print("\n4. Filtering by date range (2024):")
    filtered_2024 = extractor.filter_by_date_range(
        documents, 
        start_date="01/01/2024",
        end_date="31/12/2024"
    )
    print(f"   Found {len(filtered_2024)} documents in 2024")
    
    # Filter by keyword
    print("\n5. Filtering by keyword 'Luật Đất':")
    filtered_keyword = extractor.filter_by_keyword(documents, "Luật Đất")
    print(f"   Found {len(filtered_keyword)} documents")
    
    # Filter by code pattern
    print("\n6. Filtering by code pattern (QH15):")
    filtered_pattern = extractor.filter_by_code_pattern(documents, r"QH15")
    print(f"   Found {len(filtered_pattern)} documents")
    for doc in filtered_pattern:
        print(f"   - {doc['document_code']}: {doc['abstract']}")
    
    # Convert to DataFrame
    print("\n7. Converting to DataFrame:")
    df = extractor.to_dataframe(documents)
    print(f"   DataFrame shape: {df.shape}")
    print("\n   Columns:", df.columns.tolist())
    
    # Export to CSV
    output_csv = os.path.join(current_dir, "extracted_documents.csv")
    print(f"\n8. Exporting to CSV: {output_csv}")
    extractor.export_to_csv(documents, output_csv)
    
    print("\n" + "="*60)
    print("SUMMARY:")
    print("="*60)
    print(f"Total documents extracted: {len(documents)}")
    print(f"Date range filter (2024): {len(filtered_2024)} documents")
    print(f"Keyword filter ('Luật Đất'): {len(filtered_keyword)} documents")
    print(f"Pattern filter (QH15): {len(filtered_pattern)} documents")
    print("="*60)


if __name__ == "__main__":
    example_usage()
