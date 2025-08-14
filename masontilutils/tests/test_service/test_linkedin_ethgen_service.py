import os
import unittest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
from masontilutils.services.ethgen.linkedin_ethgen_service import (
    LinkedInEthGenService, 
    ServiceRequest, 
    ServiceResponse, 
    ServiceExecutiveInfo
)
from masontilutils.api.responses.ethgen.ethgen import EthGenResponse, GenderResponse
from masontilutils.api.responses.executive.executive import ExecutiveResponse, ExecutiveInfo
from masontilutils.api.queries.enums import Ethnicity, Sex


class TestLinkedInEthGenService(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests"""
        # Mock environment variables
        cls.mock_env_patcher = patch.dict(os.environ, {
            'PERPLEXITY_API_KEY': 'test_perplexity_key',
            'CHATGPT_API_KEY': 'test_chatgpt_key'
        })
        cls.mock_env_patcher.start()

    @classmethod
    def tearDownClass(cls):
        """Clean up after tests"""
        cls.mock_env_patcher.stop()

    def setUp(self):
        """Set up for each test"""
        # Patch all external dependencies
        self.perplexity_patcher = patch('masontilutils.services.ethgen.linkedin_ethgen_service.PerplexityExecutiveAPI')
        self.chatgpt_ethgen_patcher = patch('masontilutils.services.ethgen.linkedin_ethgen_service.ChatGPTEthGenAPI')
        self.chatgpt_gender_patcher = patch('masontilutils.services.ethgen.linkedin_ethgen_service.ChatGPTGenderAPI')
        self.ddg_patcher = patch('masontilutils.services.ethgen.linkedin_ethgen_service.DuckDuckGoLinkedInAPI')
        self.linkedin_browser_patcher = patch('masontilutils.services.ethgen.linkedin_ethgen_service.LinkedInBrowser')

        # Start all patches
        self.mock_perplexity = self.perplexity_patcher.start()
        self.mock_chatgpt_ethgen = self.chatgpt_ethgen_patcher.start()
        self.mock_chatgpt_gender = self.chatgpt_gender_patcher.start()
        self.mock_ddg = self.ddg_patcher.start()
        self.mock_linkedin_browser = self.linkedin_browser_patcher.start()

        # Create service instance
        self.service = LinkedInEthGenService()

        # Set up mock instances
        self.mock_executive_api = Mock()
        self.mock_ethgen_api = Mock()
        self.mock_gender_api = Mock()
        self.mock_ddg_api = Mock()
        self.mock_browser = Mock()

        self.service.executive_api = self.mock_executive_api
        self.service.ethgen_api = self.mock_ethgen_api
        self.service.gender_api = self.mock_gender_api
        self.service.ddg_api = self.mock_ddg_api
        self.service.browser = self.mock_browser

    def tearDown(self):
        """Clean up after each test"""
        self.perplexity_patcher.stop()
        self.chatgpt_ethgen_patcher.stop()
        self.chatgpt_gender_patcher.stop()
        self.ddg_patcher.stop()
        self.linkedin_browser_patcher.stop()

    def test_init_missing_perplexity_key(self):
        """Test initialization fails when PERPLEXITY_API_KEY is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {'CHATGPT_API_KEY': 'test_key'}):
                with self.assertRaises(ValueError) as context:
                    LinkedInEthGenService()
                self.assertIn("PERPLEXITY_API_KEY", str(context.exception))

    def test_init_missing_chatgpt_key(self):
        """Test initialization fails when CHATGPT_API_KEY is missing"""
        with patch.dict(os.environ, {}, clear=True):
            with patch.dict(os.environ, {'PERPLEXITY_API_KEY': 'test_key'}):
                with self.assertRaises(ValueError) as context:
                    LinkedInEthGenService()
                self.assertIn("CHATGPT_API_KEY", str(context.exception))

    def test_create_executive_info(self):
        """Test creation of ExecutiveInfo objects"""
        mock_executive = Mock()
        mock_executive.name = "John Doe"
        mock_executive.role = "CEO"
        mock_executive.sources = ["source1", "source2"]

        result = self.service.create_executive_info(mock_executive)

        self.assertIsInstance(result, ServiceExecutiveInfo)
        self.assertEqual(result.name, "John Doe")
        self.assertEqual(result.role, "CEO")
        self.assertEqual(result.linkedin_url, "")
        self.assertEqual(result.ethnicity, "")
        self.assertEqual(result.gender, "")
        self.assertEqual(result.sources, ["source1", "source2"])

    def test_start_and_stop(self):
        """Test browser startup and shutdown"""
        # Test start
        self.service.start()
        self.mock_linkedin_browser.assert_called_once()
        self.service.browser.login.assert_called_once()

        # Test stop
        self.service.stop()
        self.service.browser.close.assert_called_once()

    def test_get_linkedin(self):
        """Test LinkedIn URL retrieval"""
        expected_url = "https://www.linkedin.com/in/johndoe"
        self.mock_ddg_api.call.return_value = expected_url

        result = self.service.get_linkedin("John Doe", "Test Company")

        self.mock_ddg_api.call.assert_called_once_with(name="John Doe", company_name="Test Company")
        self.assertEqual(result, expected_url)

    def test_call_publicly_traded_company(self):
        """Test handling of publicly traded companies"""
        # Mock executive response for publicly traded company
        executive_response = ExecutiveResponse(
            executives=[],
            is_publicly_traded=True,
            is_none=False
        )
        self.mock_executive_api.call.return_value = executive_response

        result = self.service.call("Apple Inc", "Cupertino", "CA", "1 Apple Park Way")

        self.assertIsNotNone(result)
        self.assertTrue(result.is_publicly_traded)
        self.assertEqual(result.ethnicity, "C")
        self.assertEqual(len(result.executives), 0)

    def test_call_no_executive_response(self):
        """Test handling when no executive response is returned"""
        self.mock_executive_api.call.return_value = None

        result = self.service.call("Unknown Company", "Unknown City", "XX", "Unknown Address")

        self.assertIsNone(result)

    def test_call_empty_executive_response(self):
        """Test handling when executive response is empty or marked as none"""
        executive_response = ExecutiveResponse(
            executives=[],
            is_publicly_traded=False,
            is_none=True
        )
        self.mock_executive_api.call.return_value = executive_response

        result = self.service.call("Test Company", "Test City", "TX", "Test Address")

        self.assertIsNone(result)

    def test_call_no_executives_found(self):
        """Test handling when no executives are found"""
        executive_response = ExecutiveResponse(
            executives=[],
            is_publicly_traded=False,
            is_none=False
        )
        self.mock_executive_api.call.return_value = executive_response

        result = self.service.call("Test Company", "Test City", "TX", "Test Address")

        self.assertIsNotNone(result)
        self.assertFalse(result.executive_found)
        self.assertEqual(len(result.executives), 0)

    def test_call_single_executive_with_full_data(self):
        """Test handling of single executive with complete LinkedIn and image data"""
        # Mock executive response
        mock_executive = ExecutiveInfo(name="John Doe", role="CEO", sources=["source1"])
        executive_response = ExecutiveResponse(
            executives=[mock_executive],
            is_publicly_traded=False,
            is_none=False
        )
        self.mock_executive_api.call.return_value = executive_response

        # Mock LinkedIn URL
        linkedin_url = "https://www.linkedin.com/in/johndoe"
        self.mock_ddg_api.call.return_value = linkedin_url

        # Mock profile picture
        profile_picture = "base64_encoded_image"
        self.mock_browser.get_profile_picture_from_url.return_value = profile_picture

        # Mock ethnicity and gender response
        ethgen_response = EthGenResponse(
            ethnicity=Ethnicity.EUROPE.value,
            sex=Sex.MALE.value
        )
        self.mock_ethgen_api.call.return_value = ethgen_response

        result = self.service.call("Test Company", "Test City", "TX", "Test Address")

        self.assertIsNotNone(result)
        self.assertTrue(result.executive_found)
        self.assertFalse(result.multiple_executives)
        self.assertEqual(len(result.executives), 1)
        
        executive = result.executives[0]
        self.assertEqual(executive.name, "John Doe")
        self.assertEqual(executive.role, "CEO")
        self.assertEqual(executive.linkedin_url, linkedin_url)
        self.assertEqual(executive.ethnicity, Ethnicity.EUROPE.value)
        self.assertEqual(executive.gender, Sex.MALE.value)
        
        self.assertEqual(result.ethnicity, Ethnicity.EUROPE.value)
        self.assertEqual(result.gender, Sex.MALE.value)

    def test_call_single_executive_no_linkedin(self):
        """Test handling of single executive with no LinkedIn profile found"""
        # Mock executive response
        mock_executive = ExecutiveInfo(name="John Doe", role="CEO", sources=["source1"])
        executive_response = ExecutiveResponse(
            executives=[mock_executive],
            is_publicly_traded=False,
            is_none=False
        )
        self.mock_executive_api.call.return_value = executive_response

        # Mock no LinkedIn URL found
        self.mock_ddg_api.call.return_value = None

        result = self.service.call("Test Company", "Test City", "TX", "Test Address")

        self.assertIsNotNone(result)
        self.assertTrue(result.executive_found)
        self.assertEqual(len(result.executives), 1)
        
        executive = result.executives[0]
        self.assertEqual(executive.name, "John Doe")
        self.assertEqual(executive.linkedin_url, "")
        self.assertEqual(executive.ethnicity, "")
        self.assertEqual(executive.gender, "")

    def test_call_single_executive_no_profile_picture(self):
        """Test handling when LinkedIn profile exists but no profile picture"""
        # Mock executive response
        mock_executive = ExecutiveInfo(name="John Doe", role="CEO", sources=["source1"])
        executive_response = ExecutiveResponse(
            executives=[mock_executive],
            is_publicly_traded=False,
            is_none=False
        )
        self.mock_executive_api.call.return_value = executive_response

        # Mock LinkedIn URL
        linkedin_url = "https://www.linkedin.com/in/johndoe"
        self.mock_ddg_api.call.return_value = linkedin_url

        # Mock no profile picture
        self.mock_browser.get_profile_picture_from_url.return_value = None

        result = self.service.call("Test Company", "Test City", "TX", "Test Address")

        self.assertIsNotNone(result)
        self.assertTrue(result.executive_found)
        self.assertEqual(len(result.executives), 1)
        
        executive = result.executives[0]
        self.assertEqual(executive.linkedin_url, linkedin_url)
        self.assertEqual(executive.ethnicity, "")
        self.assertEqual(executive.gender, "")

    def test_call_single_executive_ethgen_fails_gender_succeeds(self):
        """Test fallback to gender API when ethnicity/gender detection fails"""
        # Mock executive response
        mock_executive = ExecutiveInfo(name="John Doe", role="CEO", sources=["source1"])
        executive_response = ExecutiveResponse(
            executives=[mock_executive],
            is_publicly_traded=False,
            is_none=False
        )
        self.mock_executive_api.call.return_value = executive_response

        # Mock LinkedIn and profile picture
        linkedin_url = "https://www.linkedin.com/in/johndoe"
        self.mock_ddg_api.call.return_value = linkedin_url
        self.mock_browser.get_profile_picture_from_url.return_value = "profile_picture"

        # Mock ethgen API failure
        self.mock_ethgen_api.call.return_value = None

        # Mock gender API success
        gender_response = GenderResponse(sex=Sex.MALE.value)
        self.mock_gender_api.call.return_value = gender_response

        result = self.service.call("Test Company", "Test City", "TX", "Test Address")

        executive = result.executives[0]
        self.assertEqual(executive.ethnicity, "")
        self.assertEqual(executive.gender, Sex.MALE.value)
        self.mock_gender_api.call.assert_called_once_with("John Doe")

    def test_call_single_executive_all_apis_fail(self):
        """Test when both ethnicity and gender APIs fail"""
        # Mock executive response
        mock_executive = ExecutiveInfo(name="John Doe", role="CEO", sources=["source1"])
        executive_response = ExecutiveResponse(
            executives=[mock_executive],
            is_publicly_traded=False,
            is_none=False
        )
        self.mock_executive_api.call.return_value = executive_response

        # Mock LinkedIn and profile picture
        self.mock_ddg_api.call.return_value = "https://www.linkedin.com/in/johndoe"
        self.mock_browser.get_profile_picture_from_url.return_value = "profile_picture"

        # Mock all API failures
        self.mock_ethgen_api.call.return_value = None
        self.mock_gender_api.call.return_value = None

        result = self.service.call("Test Company", "Test City", "TX", "Test Address")

        executive = result.executives[0]
        self.assertEqual(executive.ethnicity, "")
        self.assertEqual(executive.gender, "")

    def test_call_multiple_executives_same_ethnicity_gender(self):
        """Test handling of multiple executives with same ethnicity and gender"""
        # Mock executive response with multiple executives
        mock_exec1 = ExecutiveInfo(name="John Doe", role="CEO", sources=["source1"])
        mock_exec2 = ExecutiveInfo(name="Jane Smith", role="CTO", sources=["source2"])
        executive_response = ExecutiveResponse(
            executives=[mock_exec1, mock_exec2],
            is_publicly_traded=False,
            is_none=False
        )
        self.mock_executive_api.call.return_value = executive_response

        # Mock LinkedIn URLs
        self.mock_ddg_api.call.side_effect = [
            "https://www.linkedin.com/in/johndoe",
            "https://www.linkedin.com/in/janesmith"
        ]

        # Mock profile pictures
        self.mock_browser.get_profile_picture_from_url.side_effect = [
            "profile_picture1",
            "profile_picture2"
        ]

        # Mock ethnicity and gender responses (same for both)
        ethgen_response = EthGenResponse(
            ethnicity=Ethnicity.EUROPE.value,
            sex=Sex.MALE.value
        )
        self.mock_ethgen_api.call.return_value = ethgen_response

        result = self.service.call("Test Company", "Test City", "TX", "Test Address")

        self.assertIsNotNone(result)
        self.assertTrue(result.executive_found)
        self.assertTrue(result.multiple_executives)
        self.assertFalse(result.multiple_ethnicities)
        self.assertFalse(result.multiple_genders)
        self.assertEqual(len(result.executives), 2)
        self.assertEqual(result.ethnicity, Ethnicity.EUROPE.value)
        self.assertEqual(result.gender, Sex.MALE.value)

    def test_call_multiple_executives_different_ethnicity(self):
        """Test handling of multiple executives with different ethnicities"""
        # Mock executive response with multiple executives
        mock_exec1 = ExecutiveInfo(name="John Doe", role="CEO", sources=["source1"])
        mock_exec2 = ExecutiveInfo(name="Jane Smith", role="CTO", sources=["source2"])
        executive_response = ExecutiveResponse(
            executives=[mock_exec1, mock_exec2],
            is_publicly_traded=False,
            is_none=False
        )
        self.mock_executive_api.call.return_value = executive_response

        # Mock LinkedIn URLs
        self.mock_ddg_api.call.side_effect = [
            "https://www.linkedin.com/in/johndoe",
            "https://www.linkedin.com/in/janesmith"
        ]

        # Mock profile pictures
        self.mock_browser.get_profile_picture_from_url.side_effect = [
            "profile_picture1",
            "profile_picture2"
        ]

        # Mock different ethnicity responses
        ethgen_responses = [
            EthGenResponse(ethnicity=Ethnicity.EUROPE.value, sex=Sex.MALE.value),
            EthGenResponse(ethnicity=Ethnicity.EAST_ASIA.value, sex=Sex.FEMALE.value)
        ]
        self.mock_ethgen_api.call.side_effect = ethgen_responses

        result = self.service.call("Test Company", "Test City", "TX", "Test Address")

        self.assertIsNotNone(result)
        self.assertTrue(result.executive_found)
        self.assertTrue(result.multiple_executives)
        self.assertTrue(result.multiple_ethnicities)
        self.assertTrue(result.multiple_genders)
        self.assertEqual(result.ethnicity, "Non-Minority")
        self.assertEqual(result.gender, "Z")
        
        # Check individual executives
        self.assertEqual(result.executives[0].ethnicity, Ethnicity.EUROPE.value)
        self.assertEqual(result.executives[1].ethnicity, Ethnicity.EAST_ASIA.value)

    def test_call_multiple_executives_same_ethnicity_different_gender(self):
        """Test handling of multiple executives with same ethnicity but different genders"""
        # Mock executive response with multiple executives
        mock_exec1 = ExecutiveInfo(name="John Doe", role="CEO", sources=["source1"])
        mock_exec2 = ExecutiveInfo(name="Jane Smith", role="CTO", sources=["source2"])
        executive_response = ExecutiveResponse(
            executives=[mock_exec1, mock_exec2],
            is_publicly_traded=False,
            is_none=False
        )
        self.mock_executive_api.call.return_value = executive_response

        # Mock LinkedIn URLs
        self.mock_ddg_api.call.side_effect = [
            "https://www.linkedin.com/in/johndoe",
            "https://www.linkedin.com/in/janesmith"
        ]

        # Mock profile pictures
        self.mock_browser.get_profile_picture_from_url.side_effect = [
            "profile_picture1",
            "profile_picture2"
        ]

        # Mock same ethnicity, different gender responses
        ethgen_responses = [
            EthGenResponse(ethnicity=Ethnicity.EUROPE.value, sex=Sex.MALE.value),
            EthGenResponse(ethnicity=Ethnicity.EUROPE.value, sex=Sex.FEMALE.value)
        ]
        self.mock_ethgen_api.call.side_effect = ethgen_responses

        result = self.service.call("Test Company", "Test City", "TX", "Test Address")

        self.assertIsNotNone(result)
        self.assertTrue(result.multiple_executives)
        self.assertFalse(result.multiple_ethnicities)
        self.assertTrue(result.multiple_genders)
        self.assertEqual(result.ethnicity, Ethnicity.EUROPE.value)
        self.assertEqual(result.gender, "Z")

    def test_service_request_initialization(self):
        """Test ServiceRequest initialization"""
        request = ServiceRequest("Test Company", "Test City", "TX", "123 Main St")
        
        self.assertIsNotNone(request.id)
        self.assertEqual(request.company_name, "Test Company")
        self.assertEqual(request.city, "Test City")
        self.assertEqual(request.state, "TX")
        self.assertEqual(request.address, "123 Main St")
        self.assertIsInstance(request.response, ServiceResponse)

    def test_service_response_defaults(self):
        """Test ServiceResponse default values"""
        response = ServiceResponse()
        
        self.assertEqual(response.executives, [])
        self.assertFalse(response.executive_found)
        self.assertFalse(response.multiple_executives)
        self.assertFalse(response.multiple_ethnicities)
        self.assertFalse(response.multiple_genders)
        self.assertFalse(response.is_publicly_traded)

    def test_close_method(self):
        """Test the close method"""
        self.service.browser = Mock()
        self.service.close()
        self.service.browser.quit.assert_called_once()

        # Test when browser is None
        self.service.browser = None
        self.service.close()  # Should not raise an exception


if __name__ == '__main__':
    unittest.main() 