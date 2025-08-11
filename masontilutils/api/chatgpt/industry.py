import json
import traceback
from typing import List

from masontilutils.api.chatgpt.base import ThreadedChatGPTAPI, Sex
from masontilutils.api.queries.industry import INDUSTRY_CLASSIFICATION_SYSTEM_MESSAGE
from masontilutils.utils import extract_json_substring

class ChatGPTIndustryClassificationAPI(ThreadedChatGPTAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = {
            "role": "system",
            "content": INDUSTRY_CLASSIFICATION_SYSTEM_MESSAGE
        }
        
    def _build_response(self, api_res: dict):
        print("api_res: ", api_res)
        res = {
            "sex": None
        }
        if api_res["sex"] == "None" or api_res["sex"] == None:
            return res

        for sex in Sex:
            if sex.value.lower() in api_res["sex"].lower():
                res["sex"] = sex.value

        return res

    def call(self, description: str) -> List[str]:
        res = []
        try:
            # Prepare the message with the image
            messages = [
                self.system_message,
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": description
                        }
                    ]
                }
            ]

            
            # Execute the query with vision-specific parameters
            response = self.execute_query(
                model="gpt-4.1",
                messages=messages,
                max_tokens=300,  # We only need a short response
                temperature=0.0,  # Ensure consistent responses
                response_format={"type": "text"}  # Ensure we get text response
            )

            if "error" in response:
                print(f"Error: {response['error']}")
                return None

            # Extract and validate the response
            answer = response["choices"][0]["message"]["content"].strip()
            print(answer)
            json_string = extract_json_substring(answer)
        

            api_res: dict = json.loads(json_string)
            for d in api_res.values():
                if d["NAICS"] != None and d["industry_code"] != None:
                    res.append(d)

            return res
            
        except Exception as e:
            traceback.print_exc()
            print()
            return None 