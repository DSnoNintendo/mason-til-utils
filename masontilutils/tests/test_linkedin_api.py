import os
import unittest
import pandas as pd
from pathlib import Path
from masontilutils.api.perplexity import PerplexitySonarLinkedInAPI

class TestPerplexitySonarLinkedInAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests"""
        # Get API key from environment variable
        cls.api_key = os.getenv('PERPLEXITY_API_KEY')
        if not cls.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set")

        # Create API instance
        cls.api = PerplexitySonarLinkedInAPI(cls.api_key)

        # Set up test data directory
        cls.test_data_dir = Path(__file__).parent / 'test_data'
        cls.test_data_dir.mkdir(exist_ok=True)

        # Expected test file path
        cls.test_file = cls.test_data_dir / 'companies.csv'

    def test_linkedin_profile_finding(self):
        """Test that API can find LinkedIn profiles for known executives"""
        if not self.test_file.exists():
            self.skipTest(f"Test file {self.test_file} not found")

        # Read test data
        df = pd.read_csv(self.test_file)
        
        # Ensure required columns exist
        required_columns = ['company_name', 'city', 'state', 'contact']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            self.skipTest(f"Missing required columns: {missing_columns}")

        # Test each company
        for _, row in df.iterrows():
            with self.subTest(company=row['company_name']):
                if pd.notna(row['contact']):
                    # Get LinkedIn profile
                    result = self.api.call(
                        name=row['contact'],
                        company_name=row['company_name'],
                        city=row['city'],
                        state=row['state']
                    )


                    # Verify we got a valid LinkedIn URL if a result was found
  
                    print(result)
                    self.assertIn('url', result)
                    self.assertTrue(
                        result['url'].startswith('https://www.linkedin.com/in/'),
                        f"Invalid LinkedIn URL format: {result['url']}"
                    )

if __name__ == '__main__':
    unittest.main() 