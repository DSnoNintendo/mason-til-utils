from typing import Dict, Any, List
from fuzzywuzzy import fuzz

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
    
    def clean_company_name(self, company_name: str) -> str:
        company_name = company_name.lower()
        company_name = company_name.replace("llc", "")
        company_name = company_name.replace("inc", "")
        company_name = company_name.replace("corp", "")
        company_name = company_name.replace("corporation", "")
        company_name = company_name.replace("llp", "")
        company_name = company_name.replace("co", "")
        company_name = company_name.replace("company", "")
        company_name = company_name.replace("services", "")
        company_name = company_name.replace("group", "")
        company_name = company_name.replace("limited", "")

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
            results = self.api.search(query)

            for result in results:
                if self._result_valid(result, name, company_name):
                    return result['url']

        return None 