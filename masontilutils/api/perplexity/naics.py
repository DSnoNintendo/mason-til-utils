import re
from typing import Optional

from masontilutils.api.perplexity.base import ThreadedPerplexitySonarAPI
from masontilutils.api.queries.perplexity import CODE_OUTPUT_SYSTEM_MESSAGE, NAICS_CODE_QUERY


class PerplexityNAICSCodeAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)

    def extract_code(self, str):
        naics_codes = re.findall(r'\d{6}', str)
        return naics_codes[0] if naics_codes else None

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
            messages=[
                system_role,
                {"role": "user", "content": query}
            ]
        )
        if "error" not in response:
            answer = response["choices"][0]["message"]["content"]
            return self.extract_code(answer)
        else:
            print(f"Error: {response['error']}")
            return None 