import os
import unittest
import pandas as pd
from pathlib import Path
from masontilutils.api.duckduckgo import DuckDuckGoLinkedInAPI

class TestDuckDuckGoLinkedInAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests"""
        # Create API instance (no API key needed for DuckDuckGo)
        cls.api = DuckDuckGoLinkedInAPI()

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
                        company_name=row['company_name']
                    )

                    # Verify we got a valid LinkedIn URL if a result was found
                    print(result)
                    if result:
                        self.assertTrue(
                            result.startswith('https://www.linkedin.com/in/'),
                            f"Invalid LinkedIn URL format: {result}"
                        )

if __name__ == '__main__':
    unittest.main() 