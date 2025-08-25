from typing import Dict, Any, List
from fuzzywuzzy import fuzz
import re

from masontilutils.api.duckduckgo.base import DDGSearch


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
        if fuzz.partial_ratio(company_name.lower(), title_lower) < 70:
            return False
        if fuzz.partial_ratio(name.lower(), title_lower) < 70:
            return False
        
        return True
    
    def _remove_word_if_exists(self, text: str, word_to_remove: str) -> str:
        """
        Remove a word from text only if it exists as a complete word (with word boundaries).
        This prevents removing substrings that are part of larger words.
        
        :param text: The text to process
        :param word_to_remove: The word to remove if found as a complete word
        :return: Text with the word removed if it was found as a complete word
        """
        # Use word boundaries \b to ensure we only match complete words
        pattern = rf'\b{re.escape(word_to_remove)}\b'
        return re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
    
    def clean_company_name(self, company_name: str) -> str:
        """
        Clean company name by removing common business suffixes only when they appear as complete words.
        This prevents accidentally removing parts of words (e.g., 'inc' from 'principal').
        """
        company_name = company_name.lower()
        company_name = re.sub(r'[^\w\s]', '', company_name)
        company_name = company_name.strip()
        
        # List of business suffixes to remove (order matters - longer first to avoid conflicts)
        suffixes_to_remove = [
            "corporation",
            "incorporated", 
            "limited",
            "company",
            "services",
            "group",
            "llc",
            "inc", 
            "corp",
            "llp",
            "ltd",
            "co"
        ]
        
        # Remove each suffix only if it exists as a complete word
        for suffix in suffixes_to_remove:
            company_name = self._remove_word_if_exists(company_name, suffix)
        
        # Clean up any extra whitespace
        company_name = re.sub(r'\s+', ' ', company_name).strip()
        
        return company_name

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
        company_name = self.clean_company_name(company_name)

        queries = [
            f'"{name}" "{company_name}" site:linkedin.com',
            f'{name} {company_name} site:linkedin.com',
        ]

        for query in queries:
            print(f"Searching for {query}")
            results = self.api.search(query)

            print(f"length of results: {len(results)}")

            for result in results:
                if self._result_valid(result, name, company_name):
                    return result['url']

        return None 