import re
from typing import List, Dict

from masontilutils.api.perplexity.base import ThreadedPerplexitySonarAPI
from masontilutils.api.queries.email import (
    EMAIL_OUTPUT_SYSTEM_MESSAGE, 
    EMAIL_JSON_FORMAT,
    EMAIL_QUERY, 
    EMAIL_QUERY_WITH_CONTACT
)
from masontilutils.utils import extract_json_substring


class PerplexityEmailAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def email_valid(self, email: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))

    def build_response(self, results) -> List[dict]:
        emails = []
        for email, data in results.items():
            if self.email_valid(email):
                emails.append({
                    "email": email,
                    "sources": data.get("sources", [])
                })
        return emails

    def call(self,
             company_name: str,
             city: str,
             state: str,
             contact: str | None = None,
        ) -> dict:

        system_role = {"role": "system", "content": EMAIL_OUTPUT_SYSTEM_MESSAGE}

        if contact is None:
            query = EMAIL_QUERY.format(
                company_name=company_name,
                city=city,
                state=state,
                FORMAT=EMAIL_JSON_FORMAT
            )
        else:
            query = EMAIL_QUERY_WITH_CONTACT.format(
                contact=contact,
                company_name=company_name,
                city=city,
                state=state,
                FORMAT=EMAIL_JSON_FORMAT
            )

        response = super().execute_query(
            messages=[
                system_role,
                {"role": "user", "content": query}
            ]
        )
        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            json_string = extract_json_substring(answer)
            try:
                results = eval(json_string)
                return self.build_response(results)
            except Exception as e:
                print(f"Error parsing response: {e}")
                return []
        else:
            print(f"Error: {response['error']}")
            return [] 