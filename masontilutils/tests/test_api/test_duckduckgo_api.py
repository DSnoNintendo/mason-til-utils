import unittest
from masontilutils.api.duckduckgo import DuckDuckGoLinkedInAPI

class TestDuckDuckGoAPI(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.api = DuckDuckGoLinkedInAPI()

    def test_company_linkedin_search_response(self):
        """Test that the company search API returns valid results."""
        response = self.api.call(
            name="Andrew Dillard",
            company_name="AD CONSTRUCTION EQUIPMENT, INC.",
        )
        
        # Assert response is not None
        self.assertIsNotNone(response)

        self.assertEqual(response, "https://www.linkedin.com/in/andrewdillardconstructionequipmentdbe")



if __name__ == '__main__':
    unittest.main() 