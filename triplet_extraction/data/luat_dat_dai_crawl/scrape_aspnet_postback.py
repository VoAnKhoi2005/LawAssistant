"""
ASP.NET-aware scraper for chinhphu.vn
This handles the __doPostBack JavaScript mechanism and ViewState properly
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import json
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import os
import re


class ASPNetChinhPhuScraper:
    """
    Scraper for chinhphu.vn that properly handles ASP.NET postback mechanism
    """
    
    BASE_URL = "https://chinhphu.vn/he-thong-van-ban?classid=1&mode=1"

    # Linh vuc (Field/Domain) options - extracted from the dropdown
    # These correspond to ctrl_191017_163$drdDocCategory values
    LINH_VUC_OPTIONS = {
        0: "Tất cả các lĩnh vực",
        2: "An ninh trật tự",
        21: "Đất đai - Nhà ở",
        1: "Đầu tư",
        8: "Doanh nghiệp",
        10: "Giáo dục - Đào tạo",
        11: "Giao thông",
        15: "Khoa học - Công nghệ",
        17: "Lao động - Tiền lương",
        18: "Môi trường",
        22: "Quốc phòng",
        24: "Tài chính - Ngân hàng",
        28: "Thương mại",
        30: "Văn hóa - Thông tin",
        32: "Xây dựng",
        34: "Y tế - Sức khỏe",
        # Add more as needed
    }
    
    def __init__(self):
        """Initialize scraper with session"""
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'vi-VN,vi;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Referer': 'https://chinhphu.vn/he-thong-van-ban',
        })
        self.all_documents = []
        self.viewstate = None
        self.eventvalidation = None
        self.viewstategenerator = None
    
    def extract_aspnet_fields(self, html: str) -> Tuple[str, str, str]:
        """
        Extract ASP.NET hidden fields needed for postback
        
        Returns:
            Tuple of (VIEWSTATE, EVENTVALIDATION, VIEWSTATEGENERATOR)
        """
        soup = BeautifulSoup(html, 'html.parser')
        
        viewstate = soup.find('input', {'name': '__VIEWSTATE'})
        eventvalidation = soup.find('input', {'name': '__EVENTVALIDATION'})
        viewstategenerator = soup.find('input', {'name': '__VIEWSTATEGENERATOR'})
        
        return (
            viewstate.get('value', '') if viewstate else '',
            eventvalidation.get('value', '') if eventvalidation else '',
            viewstategenerator.get('value', '') if viewstategenerator else ''
        )
    
    def fetch_initial_page(self, typegroupid: int = 3) -> Optional[str]:
        """
        Fetch the initial page with GET request
        
        Args:
            typegroupid: Type group (3 = Đất đai - Nhà ở)
        
        Returns:
            HTML content
        """
        try:
            print(f"Fetching initial page (Filter: {self.LINH_VUC_OPTIONS.get(typegroupid, 'Unknown')})...")
            # URL already contains classid=1&mode=1
            response = self.session.get(self.BASE_URL, timeout=15)
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            # Extract ASP.NET fields for future postbacks
            self.viewstate, self.eventvalidation, self.viewstategenerator = \
                self.extract_aspnet_fields(response.text)
            
            print(f"✓ Initial page loaded")
            print(f"  ViewState: {len(self.viewstate)} chars")
            print(f"  EventValidation: {len(self.eventvalidation)} chars")
            
            return response.text
        
        except Exception as e:
            print(f"✗ Error fetching initial page: {e}")
            return None

    def apply_filter(self, typegroupid: int) -> Optional[str]:
        """
        Trigger dropdown AutoPostBack to apply filter
        """
        if not self.viewstate:
            raise RuntimeError("Call fetch_initial_page first")

        form_data = {
            '__EVENTTARGET': 'ctrl_191017_163$drdDocCategory',
            '__EVENTARGUMENT': '',
            '__VIEWSTATE': self.viewstate,
            '__VIEWSTATEGENERATOR': self.viewstategenerator,
            '__EVENTVALIDATION': self.eventvalidation,

            'ctrl_191017_163$drdDocCategory': str(typegroupid),
            'ctrl_191017_163$txtKeyword': '',
            'ctrl_191017_163$txtDocNumber': '',
            'ctrl_191017_163$txtFromDate': '',
            'ctrl_191017_163$txtToDate': '',
            'hidText': ''
        }

        print(f"Applying filter: {self.LINH_VUC_OPTIONS.get(typegroupid)}")

        response = self.session.post(
            self.BASE_URL,
            data=form_data,
            headers={'Content-Type': 'application/x-www-form-urlencoded'},
            timeout=15
        )
        response.raise_for_status()
        response.encoding = 'utf-8'

        self.viewstate, self.eventvalidation, self.viewstategenerator = \
            self.extract_aspnet_fields(response.text)

        return response.text

    def fetch_page_postback(self, page_number: int, typegroupid: int = 3) -> Optional[str]:
        """
        Fetch a specific page using ASP.NET postback
        
        Args:
            page_number: Page number to fetch
            typegroupid: Type group filter value
        
        Returns:
            HTML content
        """
        if not self.viewstate:
            print("Error: No ViewState available. Call fetch_initial_page first.")
            return None
        
        # Build the postback data
        # The __EVENTTARGET simulates clicking page number
        event_target = f"ctrl_191017_163$grvDocument"
        event_argument = f"Page${page_number}"
        
        form_data = {
            '__EVENTTARGET': event_target,
            '__EVENTARGUMENT': event_argument,
            '__VIEWSTATE': self.viewstate,
            '__VIEWSTATEGENERATOR': self.viewstategenerator,
            '__EVENTVALIDATION': self.eventvalidation,
            'ctrl_191017_163$drdDocCategory': str(typegroupid),
            'ctrl_191017_163$txtKeyword': '',
            'ctrl_191017_163$txtDocNumber': '',
            'ctrl_191017_163$txtFromDate': '',
            'ctrl_191017_163$txtToDate': '',
            'hidText': ''
        }
        
        try:
            print(f"  Posting for page {page_number}...")
            response = self.session.post(
                self.BASE_URL,
                data=form_data,
                timeout=15,
                headers={'Content-Type': 'application/x-www-form-urlencoded'}
            )
            response.raise_for_status()
            response.encoding = 'utf-8'
            
            # Update ViewState for next request
            self.viewstate, self.eventvalidation, self.viewstategenerator = \
                self.extract_aspnet_fields(response.text)
            
            print(f"  ✓ Page {page_number} loaded")
            return response.text
        
        except Exception as e:
            print(f"  ✗ Error fetching page {page_number}: {e}")
            return None
    
    def extract_table_data(self, html: str) -> List[Dict]:
        """Extract documents from table in HTML"""
        soup = BeautifulSoup(html, 'html.parser')
        documents = []
        
        table = soup.find('table', {'class': 'table search-result'})
        if not table:
            return documents
        
        rows = table.find_all('tr')[1:]  # Skip header
        
        for row in rows:
            cols = row.find_all('td')
            if len(cols) >= 3:
                doc = self._extract_row_data(cols)
                if doc:
                    documents.append(doc)
        
        return documents
    
    def _extract_row_data(self, cols: List) -> Optional[Dict]:
        """Extract data from a single table row"""
        try:
            # Column 1: Document code
            code_col = cols[0]
            code_link = code_col.find('a')
            if not code_link:
                return None
            
            doc_code_elem = code_link.find('span', {'class': 'code'})
            doc_code = doc_code_elem.text.strip() if doc_code_elem else ""
            
            doc_url = code_link.get('href', '')
            if doc_url and not doc_url.startswith('http'):
                doc_url = 'https://chinhphu.vn' + doc_url
            
            doc_id = ""
            if 'docid=' in doc_url:
                doc_id = doc_url.split('docid=')[1].split('&')[0]
            
            # Column 2: Issue date
            date_col = cols[1]
            issue_date_elem = date_col.find('span', {'class': 'issued-date'})
            issue_date = issue_date_elem.text.strip() if issue_date_elem else ""
            
            # Column 3: Abstract and attachments
            abstract_col = cols[2]
            abstract_link = abstract_col.find('a')
            abstract_elem = abstract_link.find('span', {'class': 'substract'}) if abstract_link else None
            abstract = abstract_elem.text.strip() if abstract_elem else ""
            
            # Extract attachments
            attachments = []
            doc_files_div = abstract_col.find('div', {'class': 'bl-doc-files'})
            if doc_files_div:
                file_divs = doc_files_div.find_all('div', {'class': 'bl-doc-file'})
                for file_div in file_divs:
                    link = file_div.find('a')
                    if link:
                        attachments.append({
                            'url': link.get('href', ''),
                            'text': link.text.strip()
                        })
            
            return {
                'document_code': doc_code,
                'document_id': doc_id,
                'document_url': doc_url,
                'issue_date': issue_date,
                'abstract': abstract,
                'attachments': attachments,
                'num_attachments': len(attachments)
            }
        
        except Exception as e:
            return None
    
    def get_pagination_info(self, html: str) -> Dict:
        """Extract pagination information"""
        soup = BeautifulSoup(html, 'html.parser')
        page_info_div = soup.find('div', {'id': 'document_page_info'})
        
        if page_info_div:
            text = page_info_div.text.strip()
            match = re.match(r'(\d+)\s*-\s*(\d+)\s*\|\s*(\d+)', text)
            if match:
                return {
                    'start_index': int(match.group(1)),
                    'end_index': int(match.group(2)),
                    'total_items': int(match.group(3))
                }
        
        return {'start_index': 0, 'end_index': 0, 'total_items': 0}
    
    def scrape_all_pages(self, typegroupid: int = 3, max_pages: int = None) -> List[Dict]:
        """
        Scrape all pages using ASP.NET postback

        Args:
            typegroupid: Type group (3 = Đất đai - Nhà ở)
            max_pages: Maximum pages to scrape
        """
        print("\n" + "="*70)
        print("ASP.NET POSTBACK SCRAPER - CHINHPHU.VN")
        print(f"Base URL: {self.BASE_URL}")
        print(f"Filter: {self.LINH_VUC_OPTIONS.get(typegroupid, 'Unknown')}")
        print("="*70)
        
        # Fetch initial page
        print("\n[Page 1]")
        html = self.fetch_initial_page()
        html = self.apply_filter(typegroupid)
        
        if not html:
            print("Failed to fetch initial page")
            return []
        
        # Extract documents from first page
        documents = self.extract_table_data(html)
        self.all_documents.extend(documents)
        print(f"  ✓ Extracted {len(documents)} documents")
        
        # Get pagination info
        page_info = self.get_pagination_info(html)
        print(f"  📊 Items {page_info['start_index']}-{page_info['end_index']} of {page_info['total_items']}")
        
        # Calculate total pages
        total_items = page_info['total_items']
        items_per_page = page_info['end_index'] - page_info['start_index'] + 1
        
        if total_items > 0 and items_per_page > 0:
            total_pages = (total_items + items_per_page - 1) // items_per_page
            print(f"  📄 Total pages: {total_pages}")
            
            if max_pages and total_pages > max_pages:
                total_pages = max_pages
                print(f"  ⚠ Limited to {max_pages} pages")
            
            # Scrape remaining pages using postback
            for page_num in range(2, total_pages + 1):
                print(f"\n[Page {page_num}]")
                
                html = self.fetch_page_postback(page_num, typegroupid=typegroupid)
                
                if html:
                    docs = self.extract_table_data(html)
                    self.all_documents.extend(docs)
                    print(f"  ✓ Extracted {len(docs)} documents")
                    
                    # Rate limiting
                    if page_num < total_pages:
                        wait_time = 2
                        print(f"  ⏳ Waiting {wait_time}s...")
                        time.sleep(wait_time)
                else:
                    print(f"  ⚠ Failed, stopping")
                    break
        
        print("\n" + "="*70)
        print(f"COMPLETE - Total: {len(self.all_documents)} documents")
        print("="*70)
        
        return self.all_documents
    
    def save_results(self, output_dir: str = ".", prefix: str = "aspnet_scrape"):
        """Save results to files"""
        if not self.all_documents:
            print("No documents to save")
            return
        
        os.makedirs(output_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # JSON
        json_file = os.path.join(output_dir, f"{prefix}_{timestamp}.json")
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(self.all_documents, f, ensure_ascii=False, indent=2)
        print(f"✓ Saved: {json_file}")
        
        # CSV
        csv_file = os.path.join(output_dir, f"{prefix}_{timestamp}.csv")
        df = self._to_dataframe()
        df.to_csv(csv_file, index=False, encoding='utf-8-sig')
        print(f"✓ Saved: {csv_file}")
    
    def _to_dataframe(self) -> pd.DataFrame:
        """Convert to DataFrame"""
        data = []
        for doc in self.all_documents:
            base_data = {
                'document_code': doc['document_code'],
                'document_id': doc['document_id'],
                'document_url': doc['document_url'],
                'issue_date': doc['issue_date'],
                'abstract': doc['abstract'],
                'num_attachments': doc['num_attachments']
            }
            for i, att in enumerate(doc['attachments'], 1):
                base_data[f'attachment_{i}_url'] = att['url']
            data.append(base_data)
        return pd.DataFrame(data)


def main():
    """Main function"""
    
    scraper = ASPNetChinhPhuScraper()

    print("\nAvailable filters (Lĩnh vực):")
    for key, value in scraper.LINH_VUC_OPTIONS.items():
        print(f"  {key}: {value}")

    documents = scraper.scrape_all_pages(typegroupid=21, max_pages=1)
    
    # Save results
    output_dir = os.path.dirname(os.path.abspath(__file__))
    scraper.save_results(output_dir, prefix="dat_dai_nha_o_aspnet")
    
    print("\n✓ Done!")


if __name__ == "__main__":
    main()
