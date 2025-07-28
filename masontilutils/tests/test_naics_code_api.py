import unittest
import os
from masontilutils.api.chatgpt import ChatGPTIndustryClassificationAPI

class TestNAICSCodeAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = os.getenv("CHATGPT_API_KEY")
        self.assertIsNotNone(self.api_key, "CHATGPT_API_KEY environment variable is not set")
        
        self.description = """WSP USA Inc. in Briarcliff Manor, NY, provides engineering and professional consulting services focused on transportation infrastructure, environmental solutions, and construction management. The firm specializes in bridge design, civil engineering, geographic information systems (GIS), and sustainable project development for public and private sector clients."""
        
        self.api = ChatGPTIndustryClassificationAPI(self.api_key)

    def test_naics_code_response(self):
        """Test that the NAICS code API returns a valid response."""
        response = self.api.call(
            description=self.description
        )
        
        # Assert response is not None
        self.assertIsNotNone(response)

        # Assert each key exists
        self.assertIsInstance(response, list)
        self.assertGreaterEqual(len(response), 0)


if __name__ == '__main__':
    unittest.main() 