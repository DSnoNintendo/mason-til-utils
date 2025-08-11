import json
import re
import threading
import time
import ast
from typing import Any, Dict, List, Optional
from requests.adapters import HTTPAdapter

import requests
from urllib3 import Retry

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