import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional, Union

class BasicWebScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
    
    def fetch_html(self, url: str) -> Optional[str]:
        """
        Fetch the HTML content of the page.
        Returns the HTML if successful, or None if there's an error.
        """
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.text
        except requests.RequestException as e:
            print(f"An error occurred while fetching the page: {e}")
            return None

    def parse_elements(self, html: str, tag: str, class_name: Optional[str] = None) -> List[str]:
        """
        Parse and retrieve content from specific HTML elements.
        
        Parameters:
        - html (str): The HTML content of the page.
        - tag (str): The HTML tag to search for (e.g., 'h1', 'p', 'a').
        - class_name (Optional[str]): The class name to filter elements by (optional).
        
        Returns:
        - List[str]: A list of element text contents.
        """
        soup = BeautifulSoup(html, 'html.parser')
        elements = soup.find_all(tag, class_=class_name)
        return [element.get_text(strip=True) for element in elements]

    def get_links(self, html: str) -> List[str]:
        """
        Extracts all hyperlinks from the page.

        Parameters:
        - html (str): The HTML content of the page.

        Returns:
        - List[str]: A list of URLs found on the page.
        """
        soup = BeautifulSoup(html, 'html.parser')
        links = soup.find_all('a', href=True)
        return [link['href'] for link in links]

    def scrape_page(self, url: str, tags: Dict[str, Optional[str]]) -> Dict[str, List[str]]:
        """
        Scrape data from a single page based on specified tags and optional classes.

        Parameters:
        - url (str): The URL to scrape.
        - tags (Dict[str, Optional[str]]): Dictionary where keys are HTML tags
          (e.g., 'h1', 'p') and values are optional class names to filter by.

        Returns:
        - Dict[str, List[str]]: A dictionary where keys are tags and values are lists of text content.
        """
        html = self.fetch_html(url)
        if html is None:
            return {}
        
        results = {}
        for tag, class_name in tags.items():
            results[tag] = self.parse_elements(html, tag, class_name)
        
        results['links'] = self.get_links(html)  # Add all page links to results
        return results

    def scrape_multiple_pages(self, urls: List[str], tags: Dict[str, Optional[str]]) -> List[Dict[str, List[str]]]:
        """
        Scrape data from multiple pages.

        Parameters:
        - urls (List[str]): List of URLs to scrape.
        - tags (Dict[str, Optional[str]]): Dictionary of tags and classes to scrape.

        Returns:
        - List[Dict[str, List[str]]]: A list of dictionaries containing scraped data for each URL.
        """
        data = []
        for url in urls:
            print(f"Scraping {url}")
            page_data = self.scrape_page(url, tags)
            if page_data:
                data.append(page_data)
        return data

    def save_to_file(self, data: Union[Dict, List], filename: str):
        """
        Save the scraped data to a JSON file.

        Parameters:
        - data (Union[Dict, List]): The data to save.
        - filename (str): The file path where data will be saved.
        """
        try:
            with open(filename, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Data saved to {filename}")
        except IOError as e:
            print(f"An error occurred while saving data: {e}")

# Example Usage
# Initialize the scraper with a base URL
scraper = BasicWebScraper("https://example.com")

# Define tags and classes to scrape
tags_to_scrape = {
    'h1': None,          # Get all <h1> tags
    'p': 'intro',        # Get <p> tags with the class 'intro'
    'a': None            # Get all <a> tags for links
}

# Define URLs to scrape (for multiple pages)
urls_to_scrape = [
    "https://example.com/page1",
    "https://example.com/page2",
    "https://example.com/page3"
]

# Scrape data from multiple pages
scraped_data = scraper.scrape_multiple_pages(urls_to_scrape, tags_to_scrape)

# Save the scraped data to a file
scraper.save_to_file(scraped_data, "scraped_data.json")
