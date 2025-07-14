# PWNA Vendor Directory Scraper

This project contains Python scripts to extract contact details and information for power washing companies from the PWNA (Power Washers of North America) vendor directory and export the data to CSV format.

## 📋 Features

- Scrapes company names, contact information, addresses, and services
- Supports both static HTML and JavaScript-rendered content
- Exports data to CSV format with clean, organized columns
- Handles multiple URL patterns and site structures
- Includes data deduplication and cleaning
- Comprehensive error handling and logging

## 🚀 Quick Start

### Installation

1. Clone or download the scripts
2. Install required dependencies:

```bash
pip install -r requirements.txt
```

### Basic Usage

Run the main scraper:

```bash
python pwna_vendor_scraper.py
```

For JavaScript-heavy sites, use the enhanced version:

```bash
python pwna_selenium_scraper.py
```

## 📊 Data Fields Extracted

The scripts extract the following information for each power washing company:

- **Company Name**
- **Contact Person**
- **Phone Number** (formatted as (XXX) XXX-XXXX)
- **Email Address**
- **Website URL**
- **Street Address**
- **City**
- **State**
- **ZIP Code**
- **Services Offered**
- **Membership Type**
- **Years in Business**
- **Company Description**

## 🔧 Configuration Options

### Basic Scraper (`pwna_vendor_scraper.py`)
- Uses requests and BeautifulSoup
- Faster execution
- Works with static HTML content
- Includes multiple fallback strategies

### Enhanced Scraper (`pwna_selenium_scraper.py`)
- Uses Selenium WebDriver for JavaScript-rendered content
- Slower but more comprehensive
- Handles dynamic loading and AJAX content
- Interactive mode with user prompts

## 📁 Output Files

The scripts generate several output files:

1. **`pwna_vendors.csv`** - Main CSV file with extracted vendor data
2. **`pwna_vendors.json`** - JSON backup of the data
3. **`page_content.html`** - Raw HTML content for debugging
4. **Log files** - Detailed execution logs

## 🛠️ Customization

### Modifying URL Patterns

Edit the `possible_urls` list in the scraper to try different URL patterns:

```python
possible_urls = [
    f"{self.base_url}/vendor-directory",
    f"{self.base_url}/vendors",
    f"{self.base_url}/directory/vendors",
    # Add more URLs as needed
]
```

### Adding New Data Fields

To extract additional fields, modify the `vendor` dictionary in `extract_vendor_details()`:

```python
vendor = {
    'company_name': '',
    'phone': '',
    'email': '',
    # Add new fields here
    'new_field': '',
}
```

### Custom Selectors

Add custom CSS selectors for specific site layouts:

```python
vendor_selectors = [
    'div[class*="vendor"]',
    'div[class*="member"]',
    # Add custom selectors here
    '.your-custom-selector',
]
```

## 🔍 Troubleshooting

### Common Issues

1. **No data extracted**
   - Check if the site requires login/registration
   - Verify the URL is accessible
   - Check `page_content.html` to see what was loaded
   - Try the Selenium version for JavaScript-heavy sites

2. **Incomplete data**
   - The site structure may have changed
   - Adjust CSS selectors in the script
   - Check for pagination or load-more buttons

3. **Rate limiting**
   - Add delays between requests
   - Use rotating user agents
   - Consider using proxies

### Debugging Steps

1. **Check the page content:**
   ```bash
   # Open the saved HTML file in a browser
   open page_content.html
   ```

2. **Enable debug logging:**
   ```python
   logging.basicConfig(level=logging.DEBUG)
   ```

3. **Test individual components:**
   ```python
   # Test contact extraction
   contact_info = scraper.extract_contact_info("Sample text with email@example.com")
   print(contact_info)
   ```

## 📄 Legal and Ethical Considerations

- **Respect robots.txt** - Check the website's robots.txt file
- **Rate limiting** - Don't overwhelm the server with requests
- **Terms of Service** - Review the website's ToS before scraping
- **Data usage** - Use extracted data responsibly and in compliance with privacy laws
- **Attribution** - Consider reaching out to PWNA for official data access

## 🤝 Contributing

Feel free to improve the scripts by:

1. Adding support for new site structures
2. Improving data extraction accuracy
3. Adding new output formats
4. Enhancing error handling

## 📝 Example Usage

```python
from pwna_vendor_scraper import PWNAVendorScraper

# Initialize scraper
scraper = PWNAVendorScraper()

# Scrape vendor directory
vendors = scraper.scrape_vendor_directory()

# Save to CSV
if vendors:
    scraper.save_to_csv('my_vendors.csv')
    print(f"Extracted {len(vendors)} vendors")
else:
    print("No vendors found")
```

## 📧 Support

If you encounter issues:

1. Check the troubleshooting section above
2. Review the log files for error messages
3. Examine the `page_content.html` file
4. Consider the site structure may have changed

## 🔄 Updates

The PWNA website structure may change over time. If the scripts stop working:

1. Check if the vendor directory URL has changed
2. Inspect the page source to identify new HTML structures
3. Update the CSS selectors accordingly
4. Test with both the basic and Selenium versions

---

**Note:** Web scraping should always be done responsibly and in accordance with the website's terms of service and applicable laws.