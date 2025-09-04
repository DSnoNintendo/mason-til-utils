from typing import Dict, Any, List
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from seleniumbase import Driver
import random
from time import sleep, time

class DDGSearch:
    def __init__(self, headless: bool = True):
        try:
            self.driver = Driver(
                headless=headless,
                uc=True
            )
            self.driver.get("https://www.duckduckgo.com")
            self.last_request_time = 0
        except Exception as e:
            raise RuntimeError(f"Failed to initialize WebDriver: {str(e)}")
        
    def _get(self, url: str):
        current_time = time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < 5:  # If less than minimum wait time has passed
            sleep_time = random.uniform(1.0, 10.0) - time_since_last_request
            if sleep_time > 0:
                print(f"Sleeping for {sleep_time} seconds")
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
