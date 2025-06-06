import unittest
import os
from masontilutils.api.deepseek import DeepseekNAICSCodeAPI

class TestNAICSCodeAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.assertIsNotNone(self.api_key, "DEEPSEEK_API_KEY environment variable is not set")
        
        self.description = """WSP USA Inc. in Briarcliff Manor, NY, provides engineering and professional consulting services focused on transportation infrastructure, environmental solutions, and construction management. The firm specializes in bridge design, civil engineering, geographic information systems (GIS), and sustainable project development for public and private sector clients."""
        
        self.api = DeepseekNAICSCodeAPI(self.api_key)

    def test_naics_code_response(self):
        """Test that the NAICS code API returns a valid response."""
        response = self.api.call(
            description=self.description
        )
        print(response)
        
        # Assert response is not None
        self.assertIsNotNone(response)
        
        # Assert response is a dictionary
        self.assertIsInstance(response, dict)
        
        # Assert response contains expected keys
        # Assert response has exactly 3 keys
        self.assertEqual(len(response.keys()), 4)
        
        # Assert each key exists
        self.assertIn(1, response)
        self.assertIn(2, response)
        self.assertIn(3, response)
        self.assertIn("industry_classification", response)
        self.assertEqual(response["industry_classification"], "P")
        self.assertIsInstance(response[1], (int, type(None)))
        self.assertIsInstance(response[2], (int, type(None)))
        self.assertIsInstance(response[3], (int, type(None)))

        if all(k is None for k in [response[1], response[2], response[3]]):
            self.assertIsNone(response["industry_classification"])
        else:
            self.assertIsInstance(response["industry_classification"], str)


if __name__ == '__main__':
    unittest.main() 