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
        self.assertEqual(len(response.keys()), 3)
        
        # Assert each key exists
        self.assertIn(1, response)
        self.assertIn(2, response)
        self.assertIn(3, response)
        
        # Assert each value is an integer or None
        for value in response.values():
            self.assertTrue(isinstance(value, (int, type(None))), f"Value {value} is not an integer or None")
            # Assert NAICS code is a 6-digit number or None
            if value is not None:
                self.assertEqual(len(str(abs(value))), 6, "NAICS code should be a 6-digit number")

if __name__ == '__main__':
    unittest.main() 