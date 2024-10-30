import requests
from bs4 import BeautifulSoup
import json
from typing import List, Dict, Optional, Set
from urllib.parse import urljoin, urlparse
from collections import deque

class BasicWebScraper:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.visited = set()  # Track visited URLs to avoid re-visiting

    def fetch_html(self, url: str) -> Optional[str]:
        """Fetch HTML content from a given URL."""
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise exception for HTTP errors
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_elements(self, html: str, tag: str, class_name: Optional[str] = None) -> List[str]:
        """Extract elements from HTML based on the tag and optional class name."""
        soup = BeautifulSoup(html, 'html.parser')
        elements = soup.find_all(tag, class_=class_name)
        return [element.get_text(strip=True) for element in elements]

    def get_links(self, html: str, base_url: str) -> Set[str]:
        """Extract all valid internal links from the HTML page."""
        soup = BeautifulSoup(html, 'html.parser')
        links = set()
        for link in soup.find_all('a', href=True):
            url = urljoin(base_url, link['href'])  # Resolve relative URLs
            if self.is_internal_url(url):
                links.add(url)
        return links

    def is_internal_url(self, url: str) -> bool:
        """Check if a URL is within the same domain as the base URL."""
        return urlparse(url).netloc == urlparse(self.base_url).netloc
    
    def scrape_page(self, url: str, tags: Dict[str, Optional[str]]) -> Dict[str, List[str]]:
        """Scrape data from a single page based on tags and classes."""
        html = self.fetch_html(url)
        if html is None:
            return {}
        
        results = {}
        for tag, class_name in tags.items():
            results[tag] = self.parse_elements(html, tag, class_name)
        
        results['links'] = list(self.get_links(html, url))
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
    
    def crawl(self, tags: Dict[str, Optional[str]], max_pages: int = 50) -> List[Dict[str, List[str]]]:
        """
        Crawl the site starting from base_url using BFS to scrape pages.

        Parameters:
        - tags (Dict[str, Optional[str]]): HTML tags and classes to scrape.
        - max_pages (int): Maximum number of pages to scrape.
        
        Returns:
        - List[Dict[str, List[str]]]: Scraped data for each page.
        """
        queue = deque([self.base_url])  # Start with the base URL
        scraped_data = []
        
        while queue and len(scraped_data) < max_pages:
            url = queue.popleft()
            if url in self.visited:
                continue
            print(f"Scraping {url}")
            self.visited.add(url)
            
            page_data = self.scrape_page(url, tags)
            if page_data:
                scraped_data.append(page_data)
                
                # Enqueue new internal links found on this page
                new_links = page_data.get('links', [])
                for link in new_links:
                    if link not in self.visited:
                        queue.append(link)
        
        return scraped_data

    def save_to_file(self, data: List[Dict[str, List[str]]], filename: str):
        """Save scraped data to a JSON file."""
        try:
            with open(filename, 'w') as file:
                json.dump(data, file, indent=4)
            print(f"Data saved to {filename}")
        except IOError as e:
            print(f"An error occurred while saving data: {e}")

# Example Usage
# Initialize the scraper with a base URL
scraper = BasicWebScraper("https://op.gg")

# Define tags and classes to scrape
tags_to_scrape = {
    'h1': None,          # Get all <h1> tags
    'p': 'intro',        # Get <p> tags with the class 'intro'
    'a': None            # Get all <a> tags for links
}

# Run the crawl function with BFS to gather data
scraped_data = scraper.crawl(tags_to_scrape, max_pages=10)

# Save the crawled data to a JSON file
scraper.save_to_file(scraped_data, "crawled_data.json")
