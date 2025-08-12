import json
import threading
import traceback
from typing import Dict, Any, List, Optional, Union
import base64
from openai import OpenAI
from openai.types.chat import ChatCompletion

from masontilutils.api.queries.enums import Region, Ethnicity, Sex

class ThreadedChatGPTAPI:
    _client_lock = threading.Lock()
    _clients = {}

    def __init__(self, api_key: str):
        """
        Initialize the ChatGPT API client
        :param api_key: Your ChatGPT API key
        """
        self.api_key = api_key

    @property
    def client(self) -> OpenAI:
        """Get or create an OpenAI client for the current thread"""
        thread_id = threading.get_ident()

        with self._client_lock:
            if thread_id not in self._clients:
                self._clients[thread_id] = OpenAI(api_key=self.api_key)

            return self._clients[thread_id]

    def execute_query(
            self,
            query: str = None,
            model: str = "gpt-5",
            **additional_args
    ) -> Dict[str, Any]:
        """
        Execute a query against the ChatGPT API

        :param query: User query string
        :param model: Model to use (default: gpt-4)
        :param max_tokens: Maximum response tokens
        :param additional_args: Additional API parameters
        :return: API response dictionary
        """
        messages = []
        if query is not None:
            messages = [{"role": "user", "content": query}]
        elif "messages" in additional_args:
            messages = additional_args.pop("messages")

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=messages,
                **additional_args
            )
            
            return {
                "choices": [{
                    "message": {
                        "content": response.choices[0].message.content
                    }
                }]
            }
        except Exception as e:
            return {
                "error": f"API request failed: {str(e)}",
                "status_code": getattr(e, 'status_code', None)
            } 