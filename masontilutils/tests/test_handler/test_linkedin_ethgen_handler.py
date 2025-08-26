import os
import unittest
from unittest.mock import Mock
from masontilutils.handler.ethgen.linkedin_ethgen_handler import (
    LinkedInEthGenResponseHandler,
    EthGenNote
)
from masontilutils.service.ethgen.linkedin_ethgen_service import (
    LinkedInEthGenResponse,
    ServiceExecutiveInfo
)
from masontilutils.db import AccessDatabaseManager


class TestLinkedInEthGenResponseHandler(unittest.TestCase):
    def setUp(self):
        """Set up for each test"""
        self.table_name = "test_table"
        self.handler = LinkedInEthGenResponseHandler(self.table_name)
        self.test_mta_uid = "12345"

        # get path of file
        current_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(current_dir, "test_db.accdb")
        self.db_manager = AccessDatabaseManager(db_path=db_path)
        self.db_manager.connect()
        
        # Set up test database table and data
        self._setup_test_database()

    def _setup_test_database(self):
        """Create test table and insert test data"""
        try:
            # Drop table if it exists (for clean test state)
            try:
                drop_query = f"DROP TABLE {self.table_name}"
                self.db_manager.execute_query(drop_query)
            except:
                pass  # Table might not exist
            
            # Create test table with all necessary columns
            create_table_query = f"""CREATE TABLE {self.table_name} (
                MTAuID TEXT PRIMARY KEY,
                company_name TEXT,
                contact TEXT,
                ethnicity TEXT,
                gender TEXT,
                ethgen_note TEXT,
                multiple_owners MEMO,
                linkedin_url MEMO,
                picture_url MEMO,
                sources MEMO
            )"""
            self.db_manager.execute_query(create_table_query)
            
            # Insert test data using f-string formatting like the handler
            test_records = [
                {
                    'mta_uid': '12345',
                    'company_name': 'Test Company 1',
                    'contact': 'John Doe'
                },
                {
                    'mta_uid': '67890',
                    'company_name': 'Test Company 2',
                    'contact': 'Jane Smith'
                },
                {
                    'mta_uid': '11111',
                    'company_name': 'Test Company 3',
                    'contact': "O'Connor Industries"
                }
            ]
            
            for record in test_records:
                insert_query = f"INSERT INTO {self.table_name} (MTAuID, company_name) VALUES ('{record['mta_uid']}', '{record['company_name']}')"
                self.db_manager.execute_query(insert_query)
                
            print(f"Test table '{self.table_name}' created and populated with test data")
            
        except Exception as e:
            print(f"Error setting up test database: {str(e)}")
            raise

    def tearDown(self):
        """Clean up after each test"""
        try:
            # Clean up test table
            drop_query = f"DROP TABLE {self.table_name}"
            self.db_manager.execute_query(drop_query)
        except:
            pass  # Table might not exist
        finally:
            self.db_manager.disconnect()


    def test_init(self):
        """Test handler initialization"""
        self.assertEqual(self.handler.table_name, self.table_name)

    def test_handle_gender_with_gender(self):
        """Test handling gender when gender is present"""
        response = LinkedInEthGenResponse(company_name="Test Co", gender="M")
        result = self.handler.handle_gender(response, self.test_mta_uid)
        
        expected = f"UPDATE {self.table_name} SET gender = 'M' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result, expected)

    def test_handle_gender_without_gender(self):
        """Test handling gender when gender is None"""
        response = LinkedInEthGenResponse(company_name="Test Co", gender=None)
        result = self.handler.handle_gender(response, self.test_mta_uid)
        
        self.assertIsNone(result)

    def test_handle_ethnicity_with_ethnicity(self):
        """Test handling ethnicity when ethnicity is present"""
        response = LinkedInEthGenResponse(company_name="Test Co", ethnicity="Asian")
        result = self.handler.handle_ethnicity(response, self.test_mta_uid)
        
        expected = f"UPDATE {self.table_name} SET ethnicity = 'Asian' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result, expected)

    def test_handle_ethnicity_without_ethnicity(self):
        """Test handling ethnicity when ethnicity is None"""
        response = LinkedInEthGenResponse(company_name="Test Co", ethnicity=None)
        result = self.handler.handle_ethnicity(response, self.test_mta_uid)
        
        self.assertIsNone(result)

    def test_handle_sources_with_sources(self):
        """Test handling sources when sources are present"""
        executive = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="",
            ethnicity="C",
            gender="M",
            sources=["LinkedIn", "Company Website", "News Article"]
        )
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive]
        )
        
        result = self.handler.handle_sources(response, self.test_mta_uid)
        
        expected = f"UPDATE {self.table_name} SET sources = 'LinkedIn , Company Website , News Article' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result, expected)

    def test_handle_sources_without_sources(self):
        """Test handling sources when sources are empty"""
        executive = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="",
            ethnicity="C",
            gender="M",
            sources=[]
        )
        response = LinkedInEthGenResponse(company_name="Test Co", executives=[executive])
        
        result = self.handler.handle_sources(response, self.test_mta_uid)
        
        self.assertIsNone(result)

    def test_handle_sources_single_source(self):
        """Test handling sources with single source"""
        executive = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="",
            ethnicity="C",
            gender="M",
            sources=["LinkedIn"]
        )
        response = LinkedInEthGenResponse(company_name="Test Co", executives=[executive])
        
        result = self.handler.handle_sources(response, self.test_mta_uid)
        
        expected = f"UPDATE {self.table_name} SET sources = 'LinkedIn' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result, expected)

    def test_handle_linkedin_url_with_url(self):
        """Test handling LinkedIn URL when URL is present"""
        executive = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="https://linkedin.com/in/johndoe",
            ethnicity="C",
            gender="M",
            sources=[]
        )
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive]
        )
        response.linkedin_url = "https://linkedin.com/in/johndoe"
        
        result = self.handler.handle_linkedin_url(response, self.test_mta_uid)
        
        expected = f"UPDATE {self.table_name} SET linkedin_url = 'https://linkedin.com/in/johndoe' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result, expected)

    def test_handle_linkedin_url_without_url(self):
        """Test handling LinkedIn URL when URL is not present"""
        response = LinkedInEthGenResponse(company_name="Test Co")
        response.linkedin_url = None
        
        result = self.handler.handle_linkedin_url(response, self.test_mta_uid)
        
        expected = f"UPDATE {self.table_name} SET linkedin_url = '{EthGenNote.NO_LINKEDIN_URL_FOUND.value}' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result, expected)

    def test_handle_picture_url_with_url(self):
        """Test handling picture URL when URL is present"""
        executive = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="",
            ethnicity="C",
            gender="M",
            picture_url="https://example.com/photo.jpg",
            sources=[]
        )
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive]
        )
        
        result = self.handler.handle_picture_url(response, self.test_mta_uid)
        
        expected = f"UPDATE {self.table_name} SET picture_url = 'https://example.com/photo.jpg' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result, expected)

    def test_handle_picture_url_without_url(self):
        """Test handling picture URL when URL is not present"""
        executive = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="",
            ethnicity="C",
            gender="M",
            picture_url="",
            sources=[]
        )
        response = LinkedInEthGenResponse(company_name="Test Co", executives=[executive])
        
        result = self.handler.handle_picture_url(response, self.test_mta_uid)
        
        expected = f"UPDATE {self.table_name} SET picture_url = '{EthGenNote.NO_IMAGE_FOUND.value}' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result, expected)

    def test_handle_name(self):
        """Test handling executive name"""
        executive = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="",
            ethnicity="C",
            gender="M",
            sources=[]
        )
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive]
        )
        
        result = self.handler.handle_name(response, self.test_mta_uid)
        
        expected = f"UPDATE {self.table_name} SET contact = 'John Doe' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result, expected)

    def test_handle_name_with_special_characters(self):
        """Test handling executive name with special characters"""
        executive = ServiceExecutiveInfo(
            name="John O'Connor",
            role="CEO",
            linkedin_url="",
            ethnicity="C",
            gender="M",
            sources=[]
        )
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive]
        )
        
        result = self.handler.handle_name(response, self.test_mta_uid)
        
        expected = f"UPDATE {self.table_name} SET contact = 'John O''Connor' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result, expected)

    def test_handle_publicly_traded_company(self):
        """Test handling publicly traded company"""
        response = LinkedInEthGenResponse(
            company_name="Apple Inc",
            is_publicly_traded=True
        )
        
        result = self.handler.handle(response, self.test_mta_uid)
        
        self.assertEqual(len(result), 1)
        expected = f"UPDATE {self.table_name} SET ethgen_note = '{EthGenNote.PUBLICLY_TRADED.value}' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result[0], expected)

    def test_handle_no_executive_found(self):
        """Test handling when no executive is found"""
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executive_found=False
        )
        
        result = self.handler.handle(response, self.test_mta_uid)
        
        self.assertEqual(len(result), 1)
        expected = f"UPDATE {self.table_name} SET ethgen_note = '{EthGenNote.NO_EXECUTIVE_FOUND.value}' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertEqual(result[0], expected)

    def test_handle_multiple_executives(self):
        """Test handling multiple executives"""
        executive1 = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="",
            ethnicity="C",
            gender="M",
            sources=["LinkedIn"]
        )
        executive2 = ServiceExecutiveInfo(
            name="Jane Smith",
            role="CTO",
            linkedin_url="",
            ethnicity="A",
            gender="F",
            sources=["Website"]
        )
        
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive1, executive2],
            executive_found=True,
            multiple_executives=True,
            ethnicity="",
            gender="Z"
        )
        
        result = self.handler.handle(response, self.test_mta_uid)
        
        # Should have multiple queries
        self.assertGreater(len(result), 1)
        
        # First query should be about multiple executives
        self.assertIn("multiple owners", result[0])
        
        # Should include ethnicity and gender updates
        note_query = f"""UPDATE {self.table_name} SET ethgen_note = 'multiple owners' WHERE MTAuID = '{self.test_mta_uid}'"""
        gender_query = f"UPDATE {self.table_name} SET gender = 'Z' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertIn(note_query, result)
        self.assertIn(gender_query, result)

    def test_handle_single_executive_complete_data(self):
        """Test handling single executive with complete data"""
        executive = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="https://linkedin.com/in/johndoe",
            ethnicity="White",
            gender="M",
            sources=["LinkedIn", "Website"],
            picture_url="https://example.com/photo.jpg"
        )
        
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive],
            executive_found=True,
            multiple_executives=False,
            ethnicity="White",
            gender="M"
        )

        
        result = self.handler.handle(response, self.test_mta_uid)
        
        # Should have multiple queries for different fields
        self.assertGreater(len(result), 1)
        
        # Check for expected queries
        name_query = f"UPDATE {self.table_name} SET contact = 'John Doe' WHERE MTAuID = '{self.test_mta_uid}'"
        ethnicity_query = f"UPDATE {self.table_name} SET ethnicity = 'White' WHERE MTAuID = '{self.test_mta_uid}'"
        gender_query = f"UPDATE {self.table_name} SET gender = 'M' WHERE MTAuID = '{self.test_mta_uid}'"
        linkedin_query = f"UPDATE {self.table_name} SET linkedin_url = 'https://linkedin.com/in/johndoe' WHERE MTAuID = '{self.test_mta_uid}'"
        picture_query = f"UPDATE {self.table_name} SET picture_url = 'https://example.com/photo.jpg' WHERE MTAuID = '{self.test_mta_uid}'"
        sources_query = f"UPDATE {self.table_name} SET sources = 'LinkedIn , Website' WHERE MTAuID = '{self.test_mta_uid}'"
        
        self.assertIn(name_query, result)
        self.assertIn(ethnicity_query, result)
        self.assertIn(gender_query, result)
        self.assertIn(linkedin_query, result)
        self.assertIn(picture_query, result)
        self.assertIn(sources_query, result)

    def test_handle_single_executive_minimal_data(self):
        """Test handling single executive with minimal data"""
        executive = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="",
            ethnicity="C",
            gender="M",
            sources=[]
        )
        
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive],
            executive_found=True,
            multiple_executives=False
        )
        
        result = self.handler.handle(response, self.test_mta_uid)
        
        # Should still have some queries (name, linkedin_url, picture_url at minimum)
        self.assertGreater(len(result), 0)
        
        # Check name query exists
        name_query = f"UPDATE {self.table_name} SET contact = 'John Doe' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertIn(name_query, result)
        
        # Check default linkedin_url query
        no_linkedin_query = f"UPDATE {self.table_name} SET linkedin_url = '{EthGenNote.NO_LINKEDIN_URL_FOUND.value}' WHERE MTAuID = '{self.test_mta_uid}'"
        self.assertIn(no_linkedin_query, result)

    def test_ethgen_note_enum_values(self):
        """Test that EthGenNote enum has expected values"""
        self.assertEqual(EthGenNote.NO_EXECUTIVE_FOUND.value, "No Executive Found")
        self.assertEqual(EthGenNote.PUBLICLY_TRADED.value, "Publicly Traded")
        self.assertEqual(EthGenNote.NO_ETHNICITY_FOUND.value, "No Ethnicity Found")
        self.assertEqual(EthGenNote.NO_GENDER_FOUND.value, "No Gender Found")
        self.assertEqual(EthGenNote.NO_LINKEDIN_URL_FOUND.value, "No LinkedIn Found")
        self.assertEqual(EthGenNote.NO_IMAGE_FOUND.value, "No Image Found")
        self.assertEqual(EthGenNote.MULTIPLE_EXECUTIVES_FOUND.value, "Multiple Executives Found")

    def test_handle_edge_case_empty_executives_list(self):
        """Test handling when executives list is empty but executive_found is True"""
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[],
            executive_found=True
        )
        
        # This should not crash and should handle gracefully
        result = self.handler.handle(response, self.test_mta_uid)
        self.assertIsInstance(result, list)

    def test_handle_none_values_in_executive(self):
        """Test handling when executive has None values"""
        executive = ServiceExecutiveInfo(
            name=None,
            role=None,
            linkedin_url=None,
            picture_url=None,
            ethnicity=None,
            sources=None
        )
        
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive],
            executive_found=True
        )
        
        # This should not crash
        result = self.handler.handle(response, self.test_mta_uid)
        self.assertIsInstance(result, list)

    def test_database_integration_publicly_traded(self):
        """Integration test: Execute publicly traded company queries against real database"""
        response = LinkedInEthGenResponse(
            company_name="Apple Inc",
            is_publicly_traded=True
        )
        
        queries = self.handler.handle(response, self.test_mta_uid)
        
        # Execute the queries against the database
        for query in queries:
            self.db_manager.execute_query(query)
        
        # Verify the data was updated correctly
        result = self.db_manager.fetch_query(f"SELECT ethgen_note FROM {self.table_name} WHERE MTAuID = '{self.test_mta_uid}'")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['ethgen_note'], EthGenNote.PUBLICLY_TRADED.value)

    def test_database_integration_single_executive(self):
        """Integration test: Execute single executive queries against real database"""
        executive = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="https://linkedin.com/in/johndoe",
            ethnicity="White",
            picture_url="https://example.com/photo.jpg",
            sources=["LinkedIn", "Website"]
        )
        
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive],
            executive_found=True,
            multiple_executives=False,
            ethnicity="C",
            gender="M"
        )
        
        queries = self.handler.handle(response, self.test_mta_uid)
        
        # Execute the queries against the database
        for query in queries:
            self.db_manager.execute_query(query)
        
        # Verify the data was updated correctly
        result = self.db_manager.fetch_query(f"SELECT * FROM {self.table_name} WHERE MTAuID = '{self.test_mta_uid}'")
        self.assertEqual(len(result), 1)
        record = result[0]
        
        self.assertEqual(record['contact'], "John Doe")
        self.assertEqual(record['ethnicity'], "C")
        self.assertEqual(record['gender'], "M")
        self.assertEqual(record['linkedin_url'], "https://linkedin.com/in/johndoe")
        self.assertEqual(record['picture_url'], "https://example.com/photo.jpg")
        self.assertEqual(record['sources'], "LinkedIn , Website")

    def test_database_integration_no_executive_found(self):
        """Integration test: Execute no executive found queries against real database"""
        response = LinkedInEthGenResponse(
            company_name="Unknown Co",
            executive_found=False
        )
        
        queries = self.handler.handle(response, self.test_mta_uid)
        
        # Execute the queries against the database
        for query in queries:
            self.db_manager.execute_query(query)
        
        # Verify the data was updated correctly
        result = self.db_manager.fetch_query(f"SELECT ethgen_note FROM {self.table_name} WHERE MTAuID = '{self.test_mta_uid}'")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]['ethgen_note'], EthGenNote.NO_EXECUTIVE_FOUND.value)

    def test_database_integration_multiple_executives(self):
        """Integration test: Execute multiple executives queries against real database"""
        executive1 = ServiceExecutiveInfo(
            name="John Doe",
            role="CEO",
            linkedin_url="",
            picture_url="",
            ethnicity="",
            gender="M",
            sources=["LinkedIn"]
        )
        executive2 = ServiceExecutiveInfo(
            name="Jane S'mith",
            role="CTO",
            linkedin_url="",
            ethnicity="",
            gender="F",
            sources=["Website"]
        )
        
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive1, executive2],
            executive_found=True,
            multiple_executives=True,
            ethnicity="C",
            gender="Z"
        )
        
        queries = self.handler.handle(response, self.test_mta_uid)
        
        # Execute the queries against the database
        for query in queries:
            print(query)
            self.db_manager.execute_query(query)
        
        # Verify the data was updated correctly
        result = self.db_manager.fetch_query(f"SELECT * FROM {self.table_name} WHERE MTAuID = '{self.test_mta_uid}'")
        self.assertEqual(len(result), 1)
        record = result[0]
        
        # Should have multiple executives note
        self.assertIn("multiple owners", record['ethgen_note'])
        self.assertIn("John Doe (CEO)", record['multiple_owners'])
        self.assertIn("Jane S'mith (CTO)", record['multiple_owners'])
        self.assertEqual(record['ethnicity'], "C")
        self.assertEqual(record['gender'], "Z")
        self.assertEqual(record['sources'], "LinkedIn , Website")

    def test_database_integration_family_owned(self):
        """Integration test: Execute multiple executives queries against real database"""
        executive1 = ServiceExecutiveInfo(
            name="John Smith",
            role="CEO",
            linkedin_url="",
            picture_url="",
            ethnicity="",
            gender="M",
            sources=["LinkedIn"]
        )
        executive2 = ServiceExecutiveInfo(
            name="Jane Smith",
            role="CTO",
            linkedin_url="",
            ethnicity="",
            gender="F",
            sources=["Website"]
        )
        
        response = LinkedInEthGenResponse(
            company_name="Test Co",
            executives=[executive1, executive2],
            executive_found=True,
            multiple_executives=True,
            ethnicity="C",
            gender="Z",
            is_family_owned=True
        )
        
        queries = self.handler.handle(response, self.test_mta_uid)
        
        # Execute the queries against the database
        for query in queries:
            print(query)
            self.db_manager.execute_query(query)
        
        # Verify the data was updated correctly
        result = self.db_manager.fetch_query(f"SELECT * FROM {self.table_name} WHERE MTAuID = '{self.test_mta_uid}'")
        self.assertEqual(len(result), 1)
        record = result[0]
        
        # Should have multiple executives note
        self.assertIn("multiple owners, family owned", record['ethgen_note'])
        self.assertIn("John Smith (CEO)", record['multiple_owners'])
        self.assertIn("Jane Smith (CTO)", record['multiple_owners'])
        self.assertEqual(record['ethnicity'], "C")
        self.assertEqual(record['gender'], "Z")
        self.assertEqual(record['sources'], "LinkedIn , Website")


if __name__ == '__main__':
    unittest.main() 