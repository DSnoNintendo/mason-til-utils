import re
from typing import List

from masontilutils.api.deepseek.base import ThreadedDeepseekR1API
from masontilutils.api.queries.industry import NAICS_CODE_OUTPUT_MESSAGE, NAICS_CODE_QUERY_DESCRIPTION
from masontilutils.utils import clean_deep_research_text


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