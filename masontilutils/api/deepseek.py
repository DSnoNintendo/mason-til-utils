import ast
import json
import re
import threading
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Dict, Any, Optional

from masontilutils.api.queries import DESCRIPTION_OUTPUT_SYSTEM_MESSAGE, DESCRIPTION_QUERY, NAICS_CODE_OUTPUT_MESSAGE, NAICS_CODE_QUERY_DESCRIPTION, NAICS_CODE_QUERY_CONTRACT
from masontilutils.utils import clean_deep_research_text, extract_json_substring


class ThreadedDeepseekR1API:
    _session_lock = threading.Lock()
    _sessions = {}

    def __init__(self, api_key: str):
        """
        Initialize the Deepseek R1 API client
        :param api_key: Your Deepseek API key
        """
        self.api_key = api_key
        self.base_url = "https://api.deepseek.com/v1/chat/completions"
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
            model: str = "deepseek-reasoner",
            max_tokens: Optional[int] = 3000,
            **additional_args
    ) -> Dict[str, Any]:
        """
        Execute a query against the Deepseek R1 API

        :param query: User query string
        :param model: Model to use (default: deepseek-reasoner)
        :param max_tokens: Maximum response tokens
        :param temperature: Temperature parameter (0.0-1.0)
        :param additional_args: Additional API parameters
        :return: API response dictionary
        """
        payload = {
            "model": model,
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



class DeepseekNAICSCodeAPI(ThreadedDeepseekR1API):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def format_response(self, response: str) -> list[str]:
        json_string = clean_deep_research_text(response)
        naics_codes = re.findall(r'\d{6}', json_string)
        return naics_codes

    def call(self,
             description: str,
             ) -> list[str] | None:

        system_role = {"role": "system", "content": NAICS_CODE_OUTPUT_MESSAGE}

        query = NAICS_CODE_QUERY_DESCRIPTION.format(
            description=description
        )

        response = super().execute_query(
            messages=[
                system_role,
                {"role": "user", "content": query}
            ]
        )
        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            return self.format_response(answer)
        else:
            print(f"Error: {response['error']}")
            return None

class DeepseekBusinessDescriptionAPI(ThreadedDeepseekR1API):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def call(self,
             company_name: str,
             city: str,
             state: str,
             address: str,
             ) -> list[str] | None:

        system_role = {"role": "system", "content": DESCRIPTION_OUTPUT_SYSTEM_MESSAGE}

        query = DESCRIPTION_QUERY.format(
            company_name=company_name,
            city=city,
            state=state,
            address=address
        )

        response = super().execute_query(
            model="deepseek-chat",
            messages=[
                system_role,
                {"role": "user", "content": query}
            ]
        )
        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            if "None" in answer:
                return None
            return clean_deep_research_text(answer)
        else:
            print(f"Error: {response['error']}")
            return None