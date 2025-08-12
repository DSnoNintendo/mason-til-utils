import os
import unittest
from pathlib import Path
from masontilutils.api.chatgpt import ChatGPTEthGenAPI, ChatGPTGenderAPI, ChatGPTIndustryClassificationAPI
from masontilutils.api.queries.enums import Ethnicity, Sex




class TestIndustryClassificationAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests"""
        # Get API key from environment variable
        cls.api_key = os.getenv('CHATGPT_API_KEY')
        if not cls.api_key:
            raise ValueError("CHATGPT_API_KEY environment variable not set")

        # Create API instance
        cls.api = ChatGPTIndustryClassificationAPI(cls.api_key)

    def test_industry_a(self):
        description_a = "Cornerstone Architectural Group, LLC is a full-service architectural firm based in South Plainfield, NJ, specializing in civic, commercial, industrial, institutional, and public sector projects. Their expertise encompasses new construction, remodeling, and modernization of facilities including municipal buildings, schools, corporate interiors, "
        res = self.api.call(description=description_a)
        self.assertEqual(len(res), 1)
        self.assertTrue(res[0]["industry_code"] == "A")

    def test_industry_g_s(self):
        description_g_s = "Cleveland Auto & Tire Co., Inc. in Elizabeth, NJ, operates as a full-service automotive facility specializing in tire sales and comprehensive vehicle maintenance. The business provides a wide selection of passenger, light truck, and commercial tires from leading manufacturers like Michelin, BFGoodrich, Bridgestone, and Goodyear. Their automotive repair services encompass brake systems, oil changes, steering and suspension repairs, and other mechanical solutions. Additionally, they offer commercial roadside assistance for fleet vehicles and mobile repair services. Serving Elizabeth, Jersey City, Newark, and surrounding areas, the company emphasizes quality service for both individual consumers and commercial clients."
        res = self.api.call(description=description_g_s)
        self.assertEqual(len(res), 2)
        industry_codes = [d["industry_code"] for d in res]

        self.assertTrue("G" in industry_codes and "S" in industry_codes)

    def test_industry_i(self):
        description_i = "DPM Technology Solutions LLC is a technology consulting firm based in Old Tappan, New Jersey, specializing in the implementation and customization of cloud-based business solutions. The company focuses primarily on Salesforce.com integrations and Advologix legal practice management software, offering services including system configuration, data migration, custom development, and end-user training. They also provide expertise in point-of-sale (POS) systems, inventory management, and retail management solutions for distribution and manufacturing sectors. Their technical consulting spans strategy development, workflow automation, and ongoing support for businesses of varying sizes."
        res = self.api.call(description=description_i)
        industry_codes = [d["industry_code"] for d in res]

        self.assertTrue("I" in industry_codes)

if __name__ == '__main__':
    unittest.main() 