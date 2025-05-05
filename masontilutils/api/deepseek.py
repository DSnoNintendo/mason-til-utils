import threading
import requests
from requests.adapters import HTTPAdapter
from urllib3.util import Retry
from typing import Dict, Any, Optional

from masontilutils.api.queries import NAICS_CODE_OUTPUT_MESSAGE, NAICS_CODE_QUERY_DESCRIPTION, NAICS_CODE_QUERY_CONTRACT


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
            max_tokens: Optional[int] = 100,
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

        try:
            response = self.session.post(
                self.base_url,
                headers=self.headers,
                json=payload,
                timeout=30
            )
            response.raise_for_status()

            return response.json()
        except requests.exceptions.RequestException as e:
            return {
                "error": f"API request failed: {str(e)}",
                "status_code": e.response.status_code if hasattr(e, 'response') and e.response else None
            }



class DeepseekNAICSCodeAPI(ThreadedDeepseekR1API):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def call(self,
             description: str,
             contract: str | None = None,
             ) -> str | None:

        system_role = {"role": "system", "content": NAICS_CODE_OUTPUT_MESSAGE}

        if description:
            query = NAICS_CODE_QUERY_DESCRIPTION.format(
                description=description
            )
        else:
            query = NAICS_CODE_QUERY_CONTRACT.format(
                description=description,
                contract=contract
            )

        messages = [system_role, {"role": "user", "content": query}]

        response = self.execute_query(query=query)

        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            return answer
        else:
            print(f"Error: {response['error']}")
            return None
