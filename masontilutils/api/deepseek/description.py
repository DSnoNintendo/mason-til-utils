from masontilutils.api.deepseek.base import ThreadedDeepseekR1API
from masontilutils.api.queries.industry import DESCRIPTION_OUTPUT_SYSTEM_MESSAGE, DESCRIPTION_QUERY
from masontilutils.utils import clean_deep_research_text


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