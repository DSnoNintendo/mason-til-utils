import os
import unittest
import pandas as pd
from pathlib import Path
from fuzzywuzzy import fuzz
from masontilutils.api.perplexity import PerplexityExecutiveAPI
from masontilutils.api.queries import PUBLICALLY_TRADED_IDENTIFIER

class TestPerplexityExecutiveAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests"""
        # Get API key from environment variable
        cls.api_key = os.getenv('PERPLEXITY_API_KEY')
        if not cls.api_key:
            raise ValueError("PERPLEXITY_API_KEY environment variable not set")

        # Create API instance
        cls.api = PerplexityExecutiveAPI(cls.api_key)

        # Set up test data directory
        cls.test_data_dir = Path(__file__).parent / 'test_data'
        cls.test_data_dir.mkdir(exist_ok=True)

        # Expected test file path
        cls.test_file = cls.test_data_dir / 'companies.csv'

        # Minimum similarity ratio for names to be considered a match
        cls.MIN_SIMILARITY = 80

    def get_similarity(self, name1, name2):
        """Compare two names using fuzzy matching"""
        return fuzz.ratio(name1.lower(), name2.lower())
    
    def test_publically_traded(self):
        print("test_publically_traded")
        result = self.api.call(
                    company_name="Uber",
                    city="San Francisco",
                    state="CA"
                )
        self.assertEqual(result, PUBLICALLY_TRADED_IDENTIFIER)


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
        
        i = 0
        # Test each company
        for _, row in df.iterrows():
            if i == 1:
                break
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
                    if result:
                        print("result:")
                        print(result)
                        self.assertGreater(
                            len(result),
                            0,
                            f"No executives found for {row['company_name']}"
                        )
                        self.assertTrue(
                            any(
                                self.get_similarity(result_dict['name'], row['contact']) >= self.MIN_SIMILARITY
                                for result_dict in result
                            )
                        )
                        self.assertTrue(
                            any(
                                result_dict['role']
                                for result_dict in result
                            )
                        )

                        # Verify we got a title
                        self.assertIsNotNone(
                            result[0]['role'],
                            f"No title found for {row['company_name']}"
                        ) 

            i += 1

            

if __name__ == '__main__':
    unittest.main() 