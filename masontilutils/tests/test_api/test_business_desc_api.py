import unittest
import os
from masontilutils.api.deepseek import DeepseekBusinessDescriptionAPI
from masontilutils.api.perplexity import PerplexityBusinessDescAPI

MAX_WORDS = 60

class TestPerplexity(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.assertIsNotNone(self.api_key, "PERPLEXITY_API_KEY environment variable is not set")
        
        self.api = PerplexityBusinessDescAPI(self.api_key)

    def test_business_description_length(self):
        """Test that the business description response is less than 50 words."""
        response = self.api.call(
            company_name="WSP USA Inc.",
            city="Briarcilff Manor",
            state="NY"
        )
        
        self.assertIsNotNone(response)
        
        word_count = len(response.split())
        self.assertLess(word_count, MAX_WORDS, f"Response was {word_count} words, expected less than {MAX_WORDS}")

    def test_no_description(self):
        """Test that the business description response is None if no description is found."""
        response = self.api.call(
            company_name="A GOOD DEAL IN NORTH JERSEY LLC",
            city="WOODLAND PARK",
            state="NJ"
        )
        self.assertIsNone(response)

if __name__ == '__main__':
    unittest.main() 