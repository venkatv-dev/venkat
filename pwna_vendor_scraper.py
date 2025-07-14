#!/usr/bin/env python3
"""
PWNA Vendor Directory Scraper

This script scrapes contact details and information for power washing companies
from the PWNA (Power Washers of North America) vendor directory and exports
the data to a CSV file.

Requirements:
- requests
- beautifulsoup4
- pandas
- lxml

Install with: pip install requests beautifulsoup4 pandas lxml
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import time
import logging
from urllib.parse import urljoin, urlparse
import csv
from typing import List, Dict, Optional
import json

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PWNAVendorScraper:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.base_url = "https://www.pwna.org"
        self.vendor_data = []
        
    def get_page(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """Fetch a webpage and return BeautifulSoup object."""
        for attempt in range(retries):
            try:
                logger.info(f"Fetching: {url} (attempt {attempt + 1})")
                response = self.session.get(url, timeout=30)
                response.raise_for_status()
                
                # Check if we need to handle JavaScript-rendered content
                if "vendor-directory" in url.lower() and len(response.text) < 1000:
                    logger.warning("Page might be JavaScript-rendered. Consider using Selenium.")
                
                return BeautifulSoup(response.content, 'lxml')
                
            except requests.RequestException as e:
                logger.error(f"Error fetching {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    return None
    
    def extract_contact_info(self, text: str) -> Dict[str, str]:
        """Extract contact information from text using regex patterns."""
        contact_info = {}
        
        # Email pattern
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        if emails:
            contact_info['email'] = emails[0]
        
        # Phone pattern (various formats)
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # (123) 456-7890 or 123-456-7890
            r'\+?1[-.\s]?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',  # +1 123 456 7890
            r'\b\d{10}\b'  # 1234567890
        ]
        
        for pattern in phone_patterns:
            phones = re.findall(pattern, text)
            if phones:
                contact_info['phone'] = phones[0]
                break
        
        # Website pattern
        website_pattern = r'https?://[^\s<>"\'`|()]*[^\s<>"\'`|().,;:]'
        websites = re.findall(website_pattern, text)
        if websites:
            contact_info['website'] = websites[0]
        
        return contact_info
    
    def extract_address(self, text: str) -> str:
        """Extract address information from text."""
        # Pattern for addresses (simplified)
        address_patterns = [
            r'\d+\s+[A-Za-z0-9\s,.-]+(?:Street|St|Avenue|Ave|Road|Rd|Drive|Dr|Lane|Ln|Boulevard|Blvd|Circle|Cir|Court|Ct|Plaza|Pl|Way|Highway|Hwy)[A-Za-z0-9\s,.-]*',
            r'\d+\s+[A-Za-z0-9\s,.-]+\b(?:AL|AK|AS|AZ|AR|CA|CO|CT|DE|DC|FM|FL|GA|GU|HI|ID|IL|IN|IA|KS|KY|LA|ME|MH|MD|MA|MI|MN|MS|MO|MT|NE|NV|NH|NJ|NM|NY|NC|ND|MP|OH|OK|OR|PW|PA|PR|RI|SC|SD|TN|TX|UT|VT|VI|VA|WA|WV|WI|WY)\b'
        ]
        
        for pattern in address_patterns:
            addresses = re.findall(pattern, text, re.IGNORECASE)
            if addresses:
                return addresses[0]
        return ""
    
    def extract_vendor_details(self, vendor_element) -> Dict[str, str]:
        """Extract details from a vendor listing element."""
        vendor = {
            'company_name': '',
            'contact_person': '',
            'address': '',
            'city': '',
            'state': '',
            'zip_code': '',
            'phone': '',
            'email': '',
            'website': '',
            'services': '',
            'description': ''
        }
        
        try:
            # Get all text from the vendor element
            vendor_text = vendor_element.get_text(separator=' ', strip=True)
            
            # Extract company name (usually in a heading or first prominent text)
            name_element = vendor_element.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
            if name_element:
                vendor['company_name'] = name_element.get_text(strip=True)
            elif vendor_element.find(class_=re.compile(r'name|title|company', re.I)):
                vendor['company_name'] = vendor_element.find(class_=re.compile(r'name|title|company', re.I)).get_text(strip=True)
            
            # Extract contact information
            contact_info = self.extract_contact_info(vendor_text)
            vendor.update(contact_info)
            
            # Extract address
            vendor['address'] = self.extract_address(vendor_text)
            
            # Look for specific elements with common class names or data attributes
            for field in ['city', 'state', 'zip', 'services', 'description']:
                element = vendor_element.find(class_=re.compile(field, re.I))
                if element:
                    vendor[field] = element.get_text(strip=True)
            
            # Extract links (potential websites)
            links = vendor_element.find_all('a', href=True)
            for link in links:
                href = link['href']
                if href.startswith('http') and 'pwna.org' not in href:
                    vendor['website'] = href
                    break
            
            logger.info(f"Extracted vendor: {vendor['company_name']}")
            
        except Exception as e:
            logger.error(f"Error extracting vendor details: {e}")
        
        return vendor
    
    def scrape_vendor_directory(self) -> List[Dict[str, str]]:
        """Main method to scrape the vendor directory."""
        vendor_url = f"{self.base_url}/vendor-directory"
        
        # Try different possible URL variations
        possible_urls = [
            f"{self.base_url}/vendor-directory",
            f"{self.base_url}/vendors",
            f"{self.base_url}/directory/vendors",
            f"{self.base_url}/member-directory",
            f"{self.base_url}/find-contractor"
        ]
        
        soup = None
        working_url = None
        
        for url in possible_urls:
            soup = self.get_page(url)
            if soup and len(soup.get_text()) > 1000:  # Basic check for content
                working_url = url
                break
        
        if not soup:
            logger.error("Could not access vendor directory page")
            return []
        
        logger.info(f"Successfully accessed: {working_url}")
        
        # Look for vendor listings using various selector strategies
        vendor_selectors = [
            'div[class*="vendor"]',
            'div[class*="member"]',
            'div[class*="listing"]',
            'div[class*="company"]',
            'div[class*="directory"]',
            '.vendor-item',
            '.member-item',
            '.listing-item',
            '.company-card',
            'article',
            'li[class*="vendor"]',
            'li[class*="member"]'
        ]
        
        vendors_found = []
        
        for selector in vendor_selectors:
            vendors = soup.select(selector)
            if vendors and len(vendors) > 1:  # Found multiple vendor elements
                logger.info(f"Found {len(vendors)} vendors using selector: {selector}")
                vendors_found = vendors
                break
        
        if not vendors_found:
            # Fallback: look for any container with contact information
            all_divs = soup.find_all('div')
            for div in all_divs:
                text = div.get_text()
                if re.search(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', text):
                    vendors_found.append(div)
        
        if not vendors_found:
            logger.warning("No vendor listings found. The page structure might be different than expected.")
            # Save page content for inspection
            with open('page_content.html', 'w', encoding='utf-8') as f:
                f.write(str(soup))
            logger.info("Saved page content to 'page_content.html' for inspection")
        
        # Extract data from found vendors
        for vendor_element in vendors_found:
            vendor_data = self.extract_vendor_details(vendor_element)
            if vendor_data['company_name'] or vendor_data['email'] or vendor_data['phone']:
                self.vendor_data.append(vendor_data)
        
        return self.vendor_data
    
    def scrape_additional_pages(self, soup: BeautifulSoup, base_url: str):
        """Look for and scrape additional pages (pagination)."""
        pagination_selectors = [
            'a[class*="next"]',
            'a[class*="page"]',
            '.pagination a',
            '.pager a',
            'a[href*="page"]'
        ]
        
        for selector in pagination_selectors:
            links = soup.select(selector)
            for link in links:
                href = link.get('href')
                if href and isinstance(href, str):
                    next_url = urljoin(base_url, href)
                    if next_url != base_url:  # Avoid infinite loops
                        logger.info(f"Found additional page: {next_url}")
                        # Add logic here to scrape additional pages if needed
    
    def save_to_csv(self, filename: str = 'pwna_vendors.csv'):
        """Save extracted data to CSV file."""
        if not self.vendor_data:
            logger.warning("No vendor data to save")
            return
        
        df = pd.DataFrame(self.vendor_data)
        
        # Clean up the data
        for column in df.columns:
            if df[column].dtype == 'object':
                df[column] = df[column].str.strip()
                df[column] = df[column].replace('', pd.NA)
        
        # Remove duplicates based on company name or email
        df = df.drop_duplicates(subset=['company_name', 'email'], keep='first')
        
        # Save to CSV
        df.to_csv(filename, index=False, encoding='utf-8')
        logger.info(f"Saved {len(df)} vendors to {filename}")
        
        # Print summary
        print(f"\nScraping Summary:")
        print(f"Total vendors found: {len(df)}")
        print(f"Vendors with email: {df['email'].notna().sum()}")
        print(f"Vendors with phone: {df['phone'].notna().sum()}")
        print(f"Vendors with website: {df['website'].notna().sum()}")
        
        return filename
    
    def save_to_json(self, filename: str = 'pwna_vendors.json'):
        """Save extracted data to JSON file."""
        if not self.vendor_data:
            logger.warning("No vendor data to save")
            return
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.vendor_data, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Saved {len(self.vendor_data)} vendors to {filename}")
        return filename

def main():
    """Main function to run the scraper."""
    scraper = PWNAVendorScraper()
    
    try:
        # Scrape the vendor directory
        vendors = scraper.scrape_vendor_directory()
        
        if vendors:
            # Save to CSV
            csv_file = scraper.save_to_csv()
            
            # Also save to JSON for backup
            json_file = scraper.save_to_json()
            
            print(f"\n✅ Scraping completed successfully!")
            print(f"📊 CSV file: {csv_file}")
            print(f"📄 JSON file: {json_file}")
            
            # Display first few records
            if len(vendors) > 0:
                print(f"\n📋 First few records:")
                df = pd.DataFrame(vendors)
                print(df.head().to_string(index=False))
        else:
            print("❌ No vendor data was extracted. Please check the website structure.")
            print("💡 The script saved 'page_content.html' for manual inspection.")
            
    except Exception as e:
        logger.error(f"An error occurred: {e}")
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()