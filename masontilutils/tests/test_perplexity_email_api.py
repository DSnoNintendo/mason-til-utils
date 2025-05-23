import unittest
import os
from masontilutils.api.perplexity import PerplexityEmailAPI
from masontilutils.api.enums import APIResponse

class TestPerplexityEmailAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.assertIsNotNone(self.api_key, "PERPLEXITY_API_KEY environment variable is not set")
        
        self.api = PerplexityEmailAPI(self.api_key)
        print(self.api_key)

    def test_call_with_contact(self):
        """Test the API call with a contact name provided."""
        response = self.api.call(
            company_name="American Institute of Architects, Santa Clara Valley",
            city="San Jose",
            state="CA",
            contact="Brent McClureAIA"
        )
        print(response)
        self.assertIsNotNone(response)
        self.assertEqual(APIResponse.FOUND, response["response_type"])
        self.assertGreaterEqual(len(response.keys()), 1)
    


    # def test_call_without_contact(self):
    #     """Test the API call without a contact name."""
    #     response = self.api.call(
    #         company_name="American Institute of Architects, Santa Clara Valley",
    #         city="San Francisco",
    #         state="CA"
    #     )
    #     self.assertIsNotNone(response)
    #     self.assertIn("response_type", response)
    #     self.assertIn("results", response)

if __name__ == '__main__':
    unittest.main() 