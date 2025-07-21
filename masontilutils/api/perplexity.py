import json
import re
import threading
import time
import ast
from typing import Any, Dict, List, Optional
from requests.adapters import HTTPAdapter

import requests
from urllib3 import Retry

from masontilutils.api.enums import APIResponse
from masontilutils.api.queries import (
    CODE_OUTPUT_SYSTEM_MESSAGE, EMAIL_OUTPUT_SYSTEM_MESSAGE, EXECUTIVE_NONE_IDENTIFIER, NAICS_CODE_QUERY, PERPLEXITY_EMAIL_JSON_FORMAT,
    PERPLEXITY_EMAIL_QUERY, PERPLEXITY_EMAIL_QUERY_WITH_CONTACT, DESCRIPTION_QUERY,
    DESCRIPTION_OUTPUT_SYSTEM_MESSAGE, EXECUTIVE_OUTPUT_SYSTEM_MESSAGE, EXECUTIVE_QUERY, PUBLICALLY_TRADED_IDENTIFIER
)
from masontilutils.utils import extract_json_substring, clean_deep_research_text, create_query

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
        max_tokens: Optional[int] = 2500,
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

        max_retries = 5
        base_delay = 5  # Base delay in seconds
        current_retry = 0

        while current_retry < max_retries:
            try:
                response = self.session.post(
                    self.base_url,
                    headers=self.headers,
                    json=payload,
                    timeout=500
                )
                response.raise_for_status()
                return response.json()

            except requests.exceptions.HTTPError as e:
                print(f"API request failed: {str(e)}")
                if e.response.status_code == 429:
                    # Get rate limit information from headers
                    retry_after = int(e.response.headers.get('Retry-After', base_delay * (2 ** current_retry)))
                    reset_time = e.response.headers.get('X-RateLimit-Reset')
                    
                    print(f"Rate limit exceeded. Retry after {retry_after} seconds.")
                    if reset_time:
                        print(f"Rate limit resets at: {reset_time}")
                    
                    # Sleep for the specified time
                    time.sleep(retry_after)
                    current_retry += 1
                    continue
                else:
                    print(f"API request failed: {str(e)}",
                        f"Status code: {e.response.status_code if hasattr(e, 'response') and e.response else None}")
                    return {
                        "error": f"API request failed: {str(e)}",
                        "status_code": e.response.status_code if hasattr(e, 'response') and e.response else None
                    }

            except requests.exceptions.RequestException as e:
                print(f"API request failed: {str(e)}",
                    f"Status code: {e.response.status_code if hasattr(e, 'response') and e.response else None}")
                return {
                    "error": f"API request failed: {str(e)}",
                    "status_code": e.response.status_code if hasattr(e, 'response') and e.response else None
                }

        # If we've exhausted all retries
        return {
            "error": "Max retries exceeded for rate limit",
            "status_code": 429
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

        retries = 0
        while "error" in response and retries < 3:
            print(f"Retrying due to error: {response['error']} (attempt {retries+1}/3)")
            time.sleep(15)
            response = super().execute_query(
                messages=[system_role, {"role": "user", "content": query}]
            )
            retries += 1

        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            return self.extract_code(answer)
        else:
            print(f"Error: {response['error']}")
            return None


class PerplexityEmailAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        self.email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        super().__init__(api_key)

    def email_valid(self, email: str) -> bool:
        """Check if an email is valid"""
        return re.match(self.email_regex, email) is not None
    
    def build_response(self, results) -> List[dict]:
        res = list()
        if results:
            json_string = extract_json_substring(results)
            # Ensure the JSON string has proper string keys
            json_string = re.sub(r'(\d+)\s*:', r'"\1":', json_string)
            loaded_json = ast.literal_eval(json_string)
            for key, value in loaded_json.items():
                email_dict = dict()
                if self.email_valid(key):
                    email_dict["email"] = key
                    email_dict["sources"] = value["sources"]
                    res.append(email_dict)
        else:
            return res

        return res

    def call(self,
             company_name: str,
             city: str,
             state: str,
             contact: str | None = None,
        ) -> dict:

        system_role = {"role": "system", "content": EMAIL_OUTPUT_SYSTEM_MESSAGE}


        if contact:
            query = create_query(query=PERPLEXITY_EMAIL_QUERY_WITH_CONTACT, 
                                 company_name=company_name, 
                                 city=city, 
                                 state=state,
                                 contact=contact,
                                 FORMAT=PERPLEXITY_EMAIL_JSON_FORMAT)
        else:
            query = create_query(query=PERPLEXITY_EMAIL_QUERY, 
                                 company_name=company_name, 
                                 city=city, 
                                 state=state,
                                 FORMAT=PERPLEXITY_EMAIL_JSON_FORMAT)

        response = super().execute_query(
            model="sonar-deep-research",
            messages=[
                system_role,
                {"role": "user", "content": query}
            ]
        )

        retries = 0
        while "error" in response and retries < 3:
            print(f"Retrying due to error: {response['error']} (attempt {retries+1}/3)")
            time.sleep(15)
            response = super().execute_query(
                model="sonar-deep-research",
                messages=[
                    system_role,
                    {"role": "user", "content": query}
                ]
            )
            retries += 1

        answer = response["choices"][0]["message"]["content"]

        if "error" not in response:
            reply = clean_deep_research_text(answer)
            if "None" in reply:
                return None
            return self.build_response(results=reply)
        else:
            print(f"Error: {response['error']}")
            return None

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
            model="sonar-pro",
            messages=[system_role, {"role": "user", "content": query}]
        )

        retries = 0
        while "error" in response and retries < 3:
            print(f"Retrying due to error: {response['error']} (attempt {retries+1}/3)")
            time.sleep(15)
            response = super().execute_query(
                model="sonar-pro",
                messages=[system_role, {"role": "user", "content": query}]
            )
            retries += 1

        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            json_string = extract_json_substring(answer)
            api_res = json.loads(json_string)
            
            if api_res['description']:
                return api_res['description']
            else:
                return None
        else:
            print(f"Error: {response['error']}")
            return None

class PerplexityExecutiveAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)

    def build_response(self, results) -> List[dict]:
        res = list()
        if results:
            try:
                json_string = clean_deep_research_text(results)
                json_string = extract_json_substring(json_string)
                # Ensure the JSON string has proper string keys
                json_string = re.sub(r'(\d+)\s*:', r'"\1":', json_string)
                loaded_json = ast.literal_eval(json_string)
                print(loaded_json)
                for key, value in loaded_json.items():
                    res.append(value)
            except Exception as e:
                print(f"Error: {e}")
                return json_string
        else:
            res = list()

        return res

    def extract_executive(self, text: str) -> List[dict] | None:
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

        system_role = {
            "role": "system", "content": EXECUTIVE_OUTPUT_SYSTEM_MESSAGE
        }

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

        retries = 0
        while "error" in response and retries < 3:
            print(f"Retrying due to error: {response['error']} (attempt {retries+1}/3)")
            time.sleep(15)
            response = super().execute_query(
                model="sonar-deep-research",
                messages=[
                    system_role,
                    {"role": "user", "content": query}
                ]
            )
            retries += 1

        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            if PUBLICALLY_TRADED_IDENTIFIER in clean_deep_research_text(answer):
                return PUBLICALLY_TRADED_IDENTIFIER
            elif EXECUTIVE_NONE_IDENTIFIER in clean_deep_research_text(answer):
                return None
            
            res =  self.build_response(results=answer)
            return res
        else:
            print(f"Error: {response['error']}")
            return None


def build_response(results) -> List[dict]:
        res = list()
        if results:
            try:
                json_string = clean_deep_research_text(results)
                json_string = extract_json_substring(json_string)
                # Ensure the JSON string has proper string keys
                json_string = re.sub(r'(\d+)\s*:', r'"\1":', json_string)
                loaded_json = ast.literal_eval(json_string)
                for key, value in loaded_json.items():
                    res.append(value)
            except Exception as e:
                print(f"Error: {e}")
                return json_string
        else:
            res = list()

        return res
