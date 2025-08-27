import json
import traceback
import base64

from masontilutils.api.chatgpt.base import ThreadedChatGPTAPI
from masontilutils.api.queries.ethgen import (
    ETHGEN_SYSTEM_MESSAGE,
    GENDER_SYSTEM_MESSAGE
)
from masontilutils.utils import extract_json_substring
from masontilutils.api.requests.ethgen.ethgen import (
    EthGenRequest,
    GenderRequest,
    build_ethgen_payload,
    build_gender_payload,
)
from masontilutils.api.responses.ethgen.ethgen import EthGenResponse, GenderResponse, build_ethgen_response, build_gender_response

MODEL = "gpt-4.1"

class ChatGPTEthGenAPI(ThreadedChatGPTAPI):
    def __init__(self, api_key: str):
        super().__init__(api_key)
        self.system_message = ETHGEN_SYSTEM_MESSAGE

    def _encode_image(self, image_path: str) -> str:
        """Encode image to base64 string"""
        with open(image_path, "rb") as image_file:
            return base64.b64encode(image_file.read()).decode('utf-8')
        
    def call(self, image_path: str, name: str | None = None, parse_url: bool = True) -> EthGenResponse | None:
        """
        Analyze an image to determine the likely geographic origin of the person shown.
        
        Args:
            image_path: Path to the image file
            name: Name of the person in the image
            parse_url: Whether the image_path is a url or a local file path
            
        Returns:
            EthGenResponse or None if analysis fails
        """
        try:
            if parse_url:
                image_url = image_path
            else:
                base64_image = self._encode_image(image_path)
                image_url = f"data:image/{image_path.split('.')[-1]};base64,{base64_image}"

            # Build payload via helpers
            request = EthGenRequest(image_path=image_url, name=name)
            payload = build_ethgen_payload(
                self.system_message,
                request,
                image_url,
                model=MODEL,
                max_tokens=100,
                temperature=1,
            )

            response = self.execute_query(**payload)

            if "error" in response:
                print(f"Error: {response['error']}")
                return None
            
            print("Response: ", response)

            # Extract and validate the response
            answer = response["choices"][0]["message"]["content"].strip()
            print(f"Answer: {answer}")
            json_string = extract_json_substring(answer) 

            print(f"Json string: {json_string}")


            api_res = json.loads(json_string)
            res: EthGenResponse = build_ethgen_response(api_res)
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
        
    def call(self, name: str) -> GenderResponse | None:
        """
        Analyze a name to determine the likely gender of the person.
        
        Args:
            name: Name of the person
            
        Returns:
            GenderResponse or None if analysis fails
        """
        try:
            # Build payload via helpers
            first_name = name.split()[0]
            request = GenderRequest(name=first_name)
            payload = build_gender_payload(
                self.system_message,
                request,
                model=MODEL,
                max_tokens=100,
                temperature=1,
            )

            response = self.execute_query(**payload)

            if "error" in response:
                print(f"Error: {response['error']}")
                return None
        
            # Extract and validate the response
            answer = response["choices"][0]["message"]["content"].strip()
            json_string = extract_json_substring(answer)

            api_res = json.loads(json_string)
            res: GenderResponse = build_gender_response(api_res)

            return res
            
        except Exception as e:
            print(f"Error processing name: {str(e)}")
            print("Full traceback:")
        
            traceback.print_exc()
            print()
            print(f"Answer: {answer}")
            return None 