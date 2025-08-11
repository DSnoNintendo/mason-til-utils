import re
from typing import List, Dict, Optional

from masontilutils.api.perplexity.base import ThreadedPerplexitySonarAPI
from masontilutils.api.queries.ethgen import (
    EXECUTIVE_OUTPUT_SYSTEM_MESSAGE, 
    EXECUTIVE_QUERY, 
    EXECUTIVE_NONE_IDENTIFIER, 
    PUBLICALLY_TRADED_IDENTIFIER
)
from masontilutils.utils import extract_json_substring


class PerplexityExecutiveAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def build_response(self, results) -> List[dict]:
        executives = []
        for key, data in results.items():
            if isinstance(data, dict) and "name" in data and "role" in data:
                executives.append({
                    "name": data["name"],
                    "role": data["role"],
                    "sources": data.get("sources", [])
                })
        return executives

    def extract_executive(self, text: str) -> List[dict] | None:
        try:
            json_string = extract_json_substring(text)
            results = eval(json_string)
            return self.build_response(results)
        except Exception as e:
            print(f"Error parsing executive data: {e}")
            return None

    def call(self,
             company_name: str,
             city: str,
             state: str,
             address: str,
        ) -> dict:

        system_role = {"role": "system", "content": EXECUTIVE_OUTPUT_SYSTEM_MESSAGE}

        query = EXECUTIVE_QUERY.format(
            company_name=company_name,
            city=city,
            state=state,
            address=address
        )

        response = super().execute_query(
            messages=[
                system_role,
                {"role": "user", "content": query}
            ]
        )
        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            
            if EXECUTIVE_NONE_IDENTIFIER in answer:
                return []
            elif PUBLICALLY_TRADED_IDENTIFIER in answer:
                return []
            else:
                return self.extract_executive(answer)
        else:
            print(f"Error: {response['error']}")
            return [] 