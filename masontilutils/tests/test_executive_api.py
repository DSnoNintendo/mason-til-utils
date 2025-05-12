import os
import unittest
import pandas as pd
from pathlib import Path
from fuzzywuzzy import fuzz
from masontilutils.api.perplexity import PerplexitySonarExecutiveAPI

class TestPerplexitySonarExecutiveAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests"""
        # Get API key from environment variable
        cls.api_key = os.getenv('PERPLEXITY_API_KEY')
        if not cls.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set")

        # Create API instance
        cls.api = PerplexitySonarExecutiveAPI(cls.api_key)

        # Set up test data directory
        cls.test_data_dir = Path(__file__).parent / 'test_data'
        cls.test_data_dir.mkdir(exist_ok=True)

        # Expected test file path
        cls.test_file = cls.test_data_dir / 'companies.csv'

        # Minimum similarity ratio for names to be considered a match
        cls.MIN_SIMILARITY = 80

    def test_executive_matching(self):
        """Test that API results match expected executives from CSV file"""
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
                # Get API result
                result = self.api.call(
                    company_name=row['company_name'],
                    city=row['city'],
                    state=row['state']
                )

                # If we have a contact in the CSV file, compare with API result
                if pd.notna(row['contact']):
                    self.assertIsNotNone(
                        result,
                        f"No executive found for {row['company_name']}"
                    )
                    print(result)
                    if result:
                        # Compare names using fuzzy matching
                        similarity = fuzz.ratio(
                            result['name'].lower(),
                            row['contact'].lower()
                        )
                        self.assertGreaterEqual(
                            similarity,
                            self.MIN_SIMILARITY,
                            f"Name similarity too low for {row['company_name']}. "
                            f"Expected: {row['contact']}, Got: {result['name']}, "
                            f"Similarity: {similarity}%"
                        )
                        # Verify we got a title
                        self.assertIsNotNone(
                            result['title'],
                            f"No title found for {row['company_name']}"
                        )

if __name__ == '__main__':
    unittest.main() 