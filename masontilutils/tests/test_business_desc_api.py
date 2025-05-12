import unittest
import os
from masontilutils.api.perplexity import PerplexityBusinessDescAPI

class TestBusinessDescAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api_key = os.getenv("PERPLEXITY_API_KEY")
        self.assertIsNotNone(self.api_key, "PERPLEXITY_API_KEY environment variable is not set")
        
        # TODO: Replace with actual test data
        self.company_name = "WSP USA Inc."
        self.city = "Briarcilff Manor"
        self.state = "NY"
        
        self.api = PerplexityBusinessDescAPI(self.api_key)

    def test_business_description_length(self):
        """Test that the business description response is less than 50 words."""
        response = self.api.call(
            company_name=self.company_name,
            city=self.city,
            state=self.state
        )
        print(response)
        
        # Assert response is not None
        self.assertIsNotNone(response)
        
        # Assert response is less than 50 words
        word_count = len(response.split())
        self.assertLess(word_count, 50, f"Response was {word_count} words, expected less than 50")

if __name__ == '__main__':
    unittest.main() 