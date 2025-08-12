import os
import unittest
from pathlib import Path
from masontilutils.api.chatgpt import ChatGPTEthGenAPI, ChatGPTGenderAPI
from masontilutils.api.queries.enums import Ethnicity, Sex
from masontilutils.api.responses.ethgen.ethgen import EthGenResponse, GenderResponse

class TestEthGenAPI(unittest.TestCase):
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
            '1_rahul sihag.jpg': {"ethnicity": Ethnicity.SOUTH_ASIA.value, "sex": Sex.MALE.value},
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
            result: EthGenResponse = self.ethgen_api.call(image_path=str(image_path))
            print(f"Result for {image_name}: {result}")

            # Assert result matches expected region
            self.assertIsNotNone(result, f"Failed to get result for {image_name}")
            
            if not (result.ethnicity == expected_res["ethnicity"] and result.sex == expected_res["sex"]):
                name = image_name.split('_')[1]
                result: EthGenResponse = self.ethgen_api.call(str(image_path), name)

                self.assertIsNotNone(result, f"Failed to get result for {image_name}")
                print(f"Result for {image_name} with name {name}: {result}")
                self.assertEqual(result.ethnicity, expected_res["ethnicity"]) 
                self.assertEqual(result.sex, expected_res["sex"]) 

            print(f"\n\n")

    def test_image_analysis_with_url(self):
        url = "https://t3.ftcdn.net/jpg/01/86/40/16/360_F_186401650_6tXxwc5x3pwuA9bYjJG65l9pCFRIAu06.jpg"
        result: EthGenResponse = self.ethgen_api.call(url, parse_url=True)
        print(f"Result for {url}: {result}")

        self.assertIsNotNone(result)
        self.assertEqual(result.ethnicity, Ethnicity.EUROPE.value)
        self.assertEqual(result.sex, Sex.FEMALE.value)


    def test_gen_api(self):
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
            result: GenderResponse = self.gen_api.call(name=name)
            self.assertIsNotNone(result)
            self.assertEqual(result.sex, Sex.MALE.value)

        for name in female_names:
            print(name)
            result: GenderResponse = self.gen_api.call(name=name)
            self.assertIsNotNone(result)
            self.assertEqual(result.sex, Sex.FEMALE.value)

        for name in unknown:
            print(name)
            result: GenderResponse = self.gen_api.call(name=name)
            self.assertIsNotNone(result)
            self.assertEqual(result.sex, None)


                

    def test_invalid_image(self):
        """Test handling of invalid image file"""
        invalid_path = self.test_images_dir / 'nonexistent.jpg'
        result: EthGenResponse = self.ethgen_api.call(str(invalid_path))
        self.assertIsNone(result, "Should return None for invalid image path")