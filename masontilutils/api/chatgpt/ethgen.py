import json
import traceback
from typing import Union
import base64

from masontilutils.api.chatgpt.base import ThreadedChatGPTAPI, Region, Ethnicity, Sex
from masontilutils.api.queries.ethgen import (
    ANCESTRAL_ANALYSIS_QUERY,
    ANCESTRAL_ANALYSIS_QUERY_WITH_NAME,
    GENDER_ANALYSIS_QUERY,
    ETHGEN_SYSTEM_MESSAGE,
    GENDER_SYSTEM_MESSAGE
)
from masontilutils.utils import extract_json_substring

class ChatGPTEthGenAPI(ThreadedChatGPTAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = ETHGEN_SYSTEM_MESSAGE

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
    def _get_ethnicity_from_region(self, region: Region) -> Ethnicity:
        if region == Region.EUROPE:
            return Ethnicity.EUROPE.value
        elif region == Region.AFRICA:
            return Ethnicity.AFRICA.value
        elif region == Region.NORTH_AMERICA:
            return Ethnicity.NORTH_AMERICA.value
        elif region == Region.SOUTH_AMERICA:
            return Ethnicity.SOUTH_AMERICA.value
        elif region == Region.AUSTRALIA:
            return Ethnicity.AUSTRALIA.value
        elif region == Region.EAST_ASIA:
            return Ethnicity.EAST_ASIA.value
        elif region == Region.SOUTH_ASIA:
            return Ethnicity.SOUTH_ASIA.value
        elif region == Region.SOUTHEAST_ASIA:
            return Ethnicity.EAST_ASIA.value
        elif region == Region.WEST_ASIA:
            return Ethnicity.WEST_ASIA.value
        elif region == Region.CENTRAL_ASIA:
            return Ethnicity.CENTRAL_ASIA.value
        elif region == Region.ANTARCTICA:
            return Ethnicity.ANTARCTICA.value
        elif region == Region.PACIFIC_ISLANDS:
            return Ethnicity.PACIFIC_ISLANDS.value
        else:
            return "None"
        
    def _build_response(self, api_res: dict):
        print("api_res: ", api_res)
        res = {
            "ethnicity": None,
            "sex": None
        }

        for region in Region:
                if region.value.lower() in api_res["region"].lower():
                    res["ethnicity"] = self._get_ethnicity_from_region(region)

        for sex in Sex:
            if sex.value.lower() in api_res["sex"].lower():
                res["sex"] = sex.value

        return res

    def call(self, image_path: str, name: str | None = None, parse_url: bool = False) -> Union[Region, None]:
        """
        Analyze an image to determine the likely geographic origin of the person shown.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            EthnicityRegion enum value or None if analysis fails
        """
        try:
            if parse_url:
                image_url = image_path
            else:
                # Encode the image
                base64_image = self._encode_image(image_path)
                image_url = f"data:image/{image_path.split('.')[-1]};base64,{base64_image}"
            
            # Prepare the message with the image
            messages = [
                self.system_message,
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": ANCESTRAL_ANALYSIS_QUERY if name is None else ANCESTRAL_ANALYSIS_QUERY_WITH_NAME.format(name=name)
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": image_url
                            }
                        }
                    ]
                }
            ]

            
            # Execute the query with vision-specific parameters
            response = self.execute_query(
                model="gpt-4.1",
                messages=messages,
                max_tokens=100,  # We only need a short response
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

            api_res = json.loads(json_string)
            res = self._build_response(api_res)
            return res
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()
            print()
            return None

class ChatGPTGenderAPI(ThreadedChatGPTAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = GENDER_SYSTEM_MESSAGE
        
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

    def call(self, name: str | None = None) -> Union[Region, None]:
        """
        Analyze an image to determine the likely geographic origin of the person shown.
        
        Args:
            image_path: Path to the image file
            
        Returns:
            EthnicityRegion enum value or None if analysis fails
        """
        try:
            # Prepare the message with the image
            messages = [
                self.system_message,
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": GENDER_ANALYSIS_QUERY.format(name=name)
                        }
                    ]
                }
            ]

            
            # Execute the query with vision-specific parameters
            response = self.execute_query(
                model="gpt-4.1",
                messages=messages,
                max_tokens=100,  # We only need a short response
                temperature=0.0,  # Ensure consistent responses
                response_format={"type": "text"}  # Ensure we get text response
            )

            if "error" in response:
                print(f"Error: {response['error']}")
                return None

            # Extract and validate the response
            answer = response["choices"][0]["message"]["content"].strip()
            json_string = extract_json_substring(answer)

            api_res = json.loads(json_string)
            res = self._build_response(api_res)
            return res
            
        except Exception as e:
            print(f"Error processing image: {str(e)}")
            print("Full traceback:")
            traceback.print_exc()
            print()
            return None 