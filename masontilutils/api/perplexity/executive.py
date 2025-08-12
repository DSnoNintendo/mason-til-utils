import re
from typing import List, Dict, Optional

from masontilutils.api.perplexity.base import ThreadedPerplexitySonarAPI
from masontilutils.api.queries.ethgen import (
    EXECUTIVE_OUTPUT_SYSTEM_MESSAGE
)
from masontilutils.api.requests.executive.executive import (
    ExecutiveRequest,
    build_executive_payload,
)
from masontilutils.api.responses.executive.executive import ExecutiveResponse, build_executive_response


class PerplexityExecutiveAPI(ThreadedPerplexitySonarAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key=api_key)
        self.system_message = {"role": "system", "content": EXECUTIVE_OUTPUT_SYSTEM_MESSAGE}

    def call(self,
             company_name: str,
             city: str,
             state: str,
             address: str,
        ) -> ExecutiveResponse | None:

        try:

            request = ExecutiveRequest(
                company_name=company_name,
                city=city,
                state=state,
                address=address
            )
            payload = build_executive_payload(
                self.system_message,
                request,
                model="sonar-deep-research",
                max_tokens=1000,
                temperature=0.0,
            )

            response = self.execute_query(**payload)

            if "error" in response:
                print(f"Error: {response['error']}")
                return None

            # Extract and validate the response
            answer = response["choices"][0]["message"]["content"]
            result: ExecutiveResponse = build_executive_response(answer)
            return result
            
        except Exception as e:
            print(f"Error processing executive search: {str(e)}")
            import traceback
            traceback.print_exc()
            return None 