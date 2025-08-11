import os
import unittest
from pathlib import Path
from masontilutils.api.chatgpt import ChatGPTEthGenAPI, ChatGPTGenderAPI, ChatGPTIndustryClassificationAPI
from masontilutils.api.queries.enums import Ethnicity, Sex

class TestChatGPTEthGenAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests"""
        # Get API key from environment variable
        cls.api_key = os.getenv('CHATGPT_API_KEY')
        if not cls.api_key:
            raise ValueError("CHATGPT_API_KEY environment variable not set")

        # Create API instance
        cls.ethgen_api = ChatGPTEthGenAPI(cls.api_key)
        cls.gen_api = ChatGPTGenderAPI(cls.api_key)

        # Set up test images directory
        cls.test_images_dir = Path(__file__).parent / 'test_images'
        cls.test_images_dir.mkdir(exist_ok=True)

        # Define expected image-region mappings
        cls.expected_mappings = {
            '1_rahul sihag.jpg': {"ethnicity": Ethnicity.EAST_ASIA.value, "sex": Sex.MALE.value},
            '2_ryan pritchard.jpg': {"ethnicity": Ethnicity.EUROPE.value, "sex": Sex.MALE.value},
            '3_michelle lee.jpg': {"ethnicity": Ethnicity.EAST_ASIA.value, "sex": Sex.FEMALE.value},
            '4_timothy walker.jpg': {"ethnicity": Ethnicity.AFRICA.value, "sex": Sex.MALE.value},
            '5_sahil faroukie.jpg': {"ethnicity": Ethnicity.WEST_ASIA.value, "sex": Sex.MALE.value},
            '6_kai finau.jpg': {"ethnicity": Ethnicity.PACIFIC_ISLANDS.value, "sex": Sex.MALE.value}
        }
            

    def test_image_analysis_with_file(self):
        """Test that images are correctly analyzed and match expected regions"""
        for image_name, expected_res in self.expected_mappings.items():

            print(f"========== Testing {image_name} ==========")
            image_path = self.test_images_dir / image_name
            
            # Skip if test image doesn't exist
            if not image_path.exists():
                self.skipTest(f"Test image {image_name} not found")
            
            # Get prediction
            print("========== Testing with file ==========")
            print(f"Image path: {image_path}")
            result = self.ethgen_api.call(image_path=str(image_path))
            print(f"Result for {image_name}: {result}")

            # Assert result matches expected region
            self.assertIsNotNone(result, f"Failed to get result for {image_name}")
            
            if result != expected_res:
                name = image_name.split('_')[1]
                result = self.ethgen_api.call(str(image_path), name)

                self.assertIsNotNone(result, f"Failed to get result for {image_name}")
                print(f"Result for {image_name} with name {name}: {result}")
                self.assertEqual(
                result, 
                expected_res,
                )

            print(f"\n\n")

    def test_image_analysis_with_url(self):
        url = "https://media.licdn.com/dms/image/v2/C4E03AQGOZgLtycIRdg/profile-displayphoto-shrink_200_200/profile-displayphoto-shrink_200_200/0/1517726975275?e=1752710400&v=beta&t=nZo6W9gyIb7j_P11Zy6Z_AvLWeLLSmtHdh7VwLW5S3Q"
        result = self.ethgen_api.call(url, parse_url=True)
        print(f"Result for {url}: {result}")

        self.assertEqual(result, {"ethnicity": Ethnicity.EUROPE.value, "sex": Sex.FEMALE.value})


    def test_gen_api_male(self):
        male_names = [ 
            "Brad Beneski",  
            "Brandon Purdy", 
            "Jay Silver", 
            "Brad Beneski",
            "Ryan L Condon",
            "Roger M Terfehr",
            "John Agamalian",
            "Montgomery Lowell West",
            "Victor Jimenez",
            "Anand Deshmukh",
            "Hamid Rastega",
            "William Vuono",
            "Mike Bullert",
            "Robert Stone",
            "Bert Campton",
            "Scott Neal",
            "Cody Lamb",
            "Adrian Loura",
            "Tyler Bender",
            "Troy Dalke",
            "Dean F. Unger",
            "Derek Schies",
            "Ayad Jaber",
            "Larry Yingling",
            "Jim Stewart",
            "Kevin Roach",
            "Thomas Reichert",
            "Scott Wheeler",
            "Bill"
        ]

        female_names = [
            "Vivian E. Norman",
            "Geraldine Jones",
            "Andrea Reed",
            "Lisa Gallagher",
            "Barbara M. Brand",
            "Amanda Whyrick",
            "Carol Loney",
            "Evguenia Vatchkova"

        ]

        unknown = [
            "J. Ross"
        ]

        for name in male_names:
            print(name)
            result = self.gen_api.call(name=name)
            self.assertEqual(result, {"sex": Sex.MALE.value})

        for name in female_names:
            print(name)
            result = self.gen_api.call(name=name)
            self.assertEqual(result, {"sex": Sex.FEMALE.value})

        for name in unknown:
            print(name)
            result = self.gen_api.call(name=name)
            self.assertEqual(result, {"sex": None})


                

    def test_invalid_image(self):
        """Test handling of invalid image file"""
        invalid_path = self.test_images_dir / 'nonexistent.jpg'
        result = self.api.call(str(invalid_path))
        self.assertIsNone(result, "Should return None for invalid image path")


class TestChatGPTEthGenAPI(unittest.TestCase):
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