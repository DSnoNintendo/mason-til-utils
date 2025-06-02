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

    # def test_call_with_contact(self):
    #     """Test the API call with a contact name provided."""
    #     response = self.api.call(
    #         company_name="American Institute of Architects, Santa Clara Valley",
    #         city="San Jose",
    #         state="CA",
    #         contact="Brent McClureAIA"
    #     )
    #     self.assertTrue(type(response) == list)
    #     self.assertTrue(len(response) > 0)
    #     for email in response:
    #         self.assertIsNotNone(email["email"])
    #         self.assertIsNotNone(email["sources"])
    #         self.assertTrue(len(email["email"]) > 0)
    #         self.assertTrue(len(email["sources"]) > 0)
    
    def test_call_without_contact(self):
        """Test the API call without a contact name."""
        print("test_call_without_contact")
        response = self.api.call(
            company_name="American Institute of Architects, Santa Clara Valley",
            city="San Jose",
            state="CA",
        )
        self.assertTrue(type(response) == list)
        self.assertTrue(len(response) > 0)
        for email in response:
            self.assertIsNotNone(email["email"])
            self.assertIsNotNone(email["sources"])
            self.assertTrue(len(email["email"]) > 0)
            self.assertTrue(len(email["sources"]) > 0)

    # def test_call_with_invalid_company_name(self):
    #     """Test the API call with an invalid company name."""
    #     print("test_call_with_invalid_company_name")
    #     response = self.api.call(
    #         company_name="Invalid Company Name",
    #         city="San Francisco",
    #         state="CA"
    #     )
    #     print(response)
    #     self.assertIsNone(response)

if __name__ == '__main__':
    unittest.main() 