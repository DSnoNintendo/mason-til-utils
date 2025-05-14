from typing import Dict, Any, List
from urllib.parse import urlencode
from bs4 import BeautifulSoup
import primp
from time import sleep, time
import undetected_chromedriver as uc
from fuzzywuzzy import fuzz
import random

class DDGSearch:
    def __init__(self, headless: bool = True):
        try:
            self.driver = uc.Chrome(
                headless=headless,
                use_subprocess=False
            )
            self.driver.get("https://www.duckduckgo.com")
            self.last_request_time = 0
        except Exception as e:
            raise RuntimeError(f"Failed to initialize WebDriver: {str(e)}")
        
    def _get(self, url: str):
        current_time = time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < 10:  # If less than minimum wait time has passed
            sleep_time = random.uniform(10, 30) - time_since_last_request
            if sleep_time > 0:
                sleep(sleep_time)
        
        self.driver.get(url)
        self.last_request_time = time()

    def _get_html(self) -> str:
        return self.driver.page_source
    
    def _parse_response(self, html: str) -> List[Dict[str, Any]]:
        results = []

        soup = BeautifulSoup(html, 'html.parser')

        articles = soup.find_all('article', attrs={'data-testid': 'result'})
        for article in articles:
            # Extract the LinkedIn URL
            link = article.find('a', {'data-testid': 'result-title-a'})
            url = link['href'] if link else None

            # Extract the title
            title = link.get_text() if link else None

            # Extract the description - look in multiple possible locations
            description_text = None
            description = article.find('div', {'data-result': 'snippet'})
            if description:
                # Get all text content, removing HTML tags
                description_text = ' '.join(description.stripped_strings)

            result = {
                'url': url,
                'title': title, 
                'description': description_text
            }

            results.append(result)

        return results
    
    def __exit__(self, exc_type, exc_value, traceback):
        self.driver.quit()
    
    def search(self, query: str) -> List[Dict[str, Any]]:
        params = {
            'q': query,
            't': 'h_',
            'ia': 'web'
        }
        url = f"https://duckduckgo.com/?{urlencode(params)}"

        self._get(url)

        return self._parse_response(self._get_html())
    
    def close(self):
        self.driver.quit()


class DuckDuckGoAPI:
    def __init__(self):
        """
        Initialize the DuckDuckGo Search API client
        """
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            "Referer": "https://duckduckgo.com/"
        }

        self.client = primp.Client(
            timeout=10,
            cookie_store=True,
            referer=True,
            impersonate="random",
            impersonate_os="random",
            follow_redirects=False,
            verify=True,
        )

    def execute_search(
            self,
            query: str,
            max_results: int = 5,
            **additional_args
    ) -> List[Dict[str, Any]]:
        """
        Execute a search query using DuckDuckGo

        :param query: Search query string
        :param max_results: Maximum number of results to return (default: 5)
        :param additional_args: Additional search parameters
        :return: List of search results
        """
        try:
            # Construct the search URL with parameters
            base_url = "https://duckduckgo.com/"
            params = {
                'q': query,
                't': 'h_',
                'ia': 'web'
            }
            
            # Build the full URL with encoded parameters
            full_url = f"{base_url}?{urlencode(params)}"
            print(f"Requesting URL: {full_url}")
            
            # Make the request
            payload = self.client.get(
                full_url,
            )

            # Parse the HTML response
            soup = BeautifulSoup(payload.text, 'html.parser')
            print(payload.text)
            results = []
            
            # Find all article elements that have data-* attributes with value "result"
            
            articles = soup.find_all('article')

            print(articles)

            # Process each article up to max_results
            for article in articles[:max_results]:
                result = {}
                
                # Extract title and link if available
                title_elem = article.find('h2')
                if title_elem and title_elem.find('a'):
                    result['title'] = title_elem.find('a').get_text(strip=True)
                    result['link'] = title_elem.find('a').get('href')
                
                # Extract snippet if available
                snippet_elem = article.find(['p', 'div'], class_='result__snippet')
                if snippet_elem:
                    result['snippet'] = snippet_elem.get_text(strip=True)
                
                results.append(result)
                
            return results
            
        except Exception as e:
            return [{
                "error": f"Search request failed: {str(e)}",
                "status_code": getattr(e, 'status_code', None)
            }]

class DuckDuckGoLinkedInAPI():
    def __init__(self):
        self.api = DDGSearch()

    def _is_linkedin_profile_url(self, url: str) -> bool:
        return url.startswith("https://www.linkedin.com/in/")
    
    def _result_valid(self, result: Dict[str, Any], name: str, company_name: str) -> bool:
        if not self._is_linkedin_profile_url(result['url']):
            return False
        # Use fuzzy matching to check company name and person name in title
        title_lower = result['title'].lower()
        if fuzz.partial_ratio(company_name.lower(), title_lower) < 80:
            return False
        if fuzz.partial_ratio(name.lower(), title_lower) < 80:
            return False
        
        return True

    def call(
            self,
            name: str,
            company_name: str,
    ) -> List[Dict[str, Any]]:
        """
        Search for LinkedIn profiles using DuckDuckGo

        :param name: Name of the person
        :param company_name: Name of the company
        :return: List of search results
        """

        query = f'{name} {company_name} site:linkedin.com'

        results = self.api.search(query)

        for result in results:
            if self._result_valid(result, name, company_name):
                return result['url']

        return None

