import re
import threading
from typing import Any, Dict, Optional
from requests.adapters import HTTPAdapter

import requests
from urllib3 import Retry

from masontilutils.api.enums import APIResponse
from masontilutils.api.queries import (
    CODE_OUTPUT_SYSTEM_MESSAGE, EMAIL_OUTPUT_SYSTEM_MESSAGE, NAICS_CODE_QUERY,
    PERPLEXITY_EMAIL_QUERY, PERPLEXITY_EMAIL_QUERY_WITH_CONTACT, DESCRIPTION_QUERY,
    DESCRIPTION_OUTPUT_SYSTEM_MESSAGE, EXECUTIVE_OUTPUT_SYSTEM_MESSAGE, EXECUTIVE_QUERY
)
from masontilutils.utils import clean_deep_research_text, create_query

class ThreadedPerplexitySonarAPI:
    _session_lock = threading.Lock()
    _sessions = {}
    
    def __init__(self, api_key: str):
        """
        Initialize the Perplexity Sonar API client
        :param api_key: Your Perplexity API key
        """
        self.api_key = api_key
        self.base_url = "https://api.perplexity.ai/chat/completions"
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
    @property
    def session(self):
        """Get or create a requests session for the current thread"""
        thread_id = threading.get_ident()
        
        with self._session_lock:
            if thread_id not in self._sessions:
                session = requests.Session()
                # Configure retry strategy
                retry_strategy = Retry(
                    total=3,
                    backoff_factor=0.5,
                    status_forcelist=[429, 500, 502, 503, 504]
                )
                adapter = HTTPAdapter(max_retries=retry_strategy)
                session.mount("https://", adapter)
                session.mount("http://", adapter)
                self._sessions[thread_id] = session
                
            return self._sessions[thread_id]

    def execute_query(
            self,
            query: str = None,
            model: str = "sonar-pro",
            max_tokens: Optional[int] = 1000,
            temperature: float = 0.1,
            **additional_args
    ) -> Dict[str, Any]:

        payload = {
            "model": model,
            "temperature": temperature,
            **additional_args
        }
        
        if query is not None:
            payload["messages"] = [{"role": "user", "content": query}]
        elif "messages" not in payload and "messages" not in additional_args:
            payload["messages"] = []
            
        if max_tokens is not None:
            payload["max_tokens"] = max_tokens

        try:
            response = self.session.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=500
            )
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API request failed: {str(e)}",
                "status_code": e.response.status_code if hasattr(e, 'response') and e.response else None
            }
        
class PerplexityNAICSCodeAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def extract_code(self, str):
        """Extract the NAICS code from the response"""
        match = re.search(r"\d{6}", str)
        return match.group(0) if match else None

    def call(self,
             company_name: str,
             city: str,
             state: str,
        ) -> str | None:

        system_role = {"role": "system", "content": CODE_OUTPUT_SYSTEM_MESSAGE}

        query = NAICS_CODE_QUERY.format(
            company_name=company_name,
            city=city,
            state=state
        )

        response = super().execute_query(
            messages=[system_role, {"role": "user", "content": query}]
        )

        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            print(answer)
            return self.extract_code(answer)
        else:
            print(f"Error: {response['error']}")
            return None


class PerplexitySonarEmailAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def extract_emails(self, text: str) -> list:
        """Extract all valid email addresses from a string"""
        email_pattern = r'\b[A-Za-z0-9._*%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text, re.IGNORECASE)
        return list(set(emails))  # Return unique emails


    def build_response(self, response_type, results) -> dict:
        res = dict()
        res["response_type"] = response_type
        res["results"] = results

        return res


    def get_response_type(self, response):
        if "@" in response:
            emails = self.extract_emails(response)
            if all("*" in email for email in emails):
                print(f"Redacted email returned {emails}")
                return APIResponse.REJECTED
            return APIResponse.FOUND

        elif "None" in response or "@" not in response:
            return APIResponse.NONE

        return APIResponse.ERROR


    def call(self,
             company_name: str,
             city: str,
             state: str,
             contact: str | None = None,
        ) -> dict:

        system_role = {"role": "system", "content": EMAIL_OUTPUT_SYSTEM_MESSAGE}


        if contact:
            query = create_query(query=PERPLEXITY_EMAIL_QUERY_WITH_CONTACT, 
                                 company_name=company_name, city=city, state=state, contact=contact)
        else:
            query = create_query(query=PERPLEXITY_EMAIL_QUERY, 
                                 company_name=company_name, city=city, state=state)

        response = super().execute_query(
            model="sonar-deep-research",
            messages=[
                system_role,
                {"role": "user", "content": query}
            ]
        )

        answer = response["choices"][0]["message"]["content"]

        response_type = self.get_response_type(answer)

        if "error" not in response:
            if response_type == APIResponse.FOUND:
                print(f"Found email for {company_name}, {answer}")
                return self.build_response(response_type=response_type, results=self.extract_emails(answer))
            else:
                return self.build_response(response_type=response_type, results=None)
        else:
            print(f"Error: {response['error']}")
            return self.build_response(response_type=APIResponse.ERROR, results=None)

class PerplexityBusinessDescAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def call(self,
             company_name: str,
             city: str,
             state: str,
        ) -> str | None:

        system_role = {"role": "system", "content": DESCRIPTION_OUTPUT_SYSTEM_MESSAGE}

        query = DESCRIPTION_QUERY.format(
            company_name=company_name,
            city=city,
            state=state
        )

        response = super().execute_query(
            model="sonar-deep-research",
            messages=[system_role, {"role": "user", "content": query}]
        )

        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            if "None" in answer:
                return None
            return clean_deep_research_text(answer)
        else:
            print(f"Error: {response['error']}")
            return None

class PerplexityExecutiveAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def extract_executive(self, text: str) -> dict:
        """Extract executive information from the response"""
        # Look for patterns like "Name: John Smith" or "Title: CEO"
        name_match = re.search(r"Name:\s*([^\n]+)", text, re.IGNORECASE)
        title_match = re.search(r"Title:\s*([^\n]+)", text, re.IGNORECASE)
        
        if name_match and title_match:
            return {
                "name": name_match.group(1).strip(),
                "title": title_match.group(1).strip()
            }
        return None

    def call(self,
             company_name: str,
             city: str,
             state: str,
        ) -> dict:

        system_role = {"role": "system", "content": EXECUTIVE_OUTPUT_SYSTEM_MESSAGE}

        query = EXECUTIVE_QUERY.format(
            company_name=company_name,
            city=city,
            state=state
        )

        response = super().execute_query(
            model="sonar-deep-research",
            messages=[
                system_role,
                {"role": "user", "content": query}
            ]
        )

        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            if "No executive information found" in answer:
                return None
            return self.extract_executive(answer)
        else:
            print(f"Error: {response['error']}")
            return None

class PerplexityLinkedInAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def extract_linkedin_url(self, text: str) -> str | None:
        """Extract LinkedIn URL from the response"""
        # Look for LinkedIn URL pattern
        linkedin_pattern = r'https?://(?:www\.)?linkedin\.com/in/[a-zA-Z0-9-]+/?'
        match = re.search(linkedin_pattern, text)
        return match.group(0) if match else None

    def call(self,
             name: str,
             company_name: str,
             city: str,
             state: str,
        ) -> str | None:
        query = f"""Find a linkedin profile for {name} of {company_name}. Return the url only. If none found return None."""

        response = super().execute_query(
            model="sonar-pro",
            messages=[{"role": "user", "content": query}],
            temperature=0.1  # Low temperature for more precise results
        )

        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            print(answer)
            linkedin_url = self.extract_linkedin_url(answer)
            return linkedin_url if linkedin_url else None
        else:
            print(f"Error: {response['error']}")
            return None

