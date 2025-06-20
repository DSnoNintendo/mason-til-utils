import os
import unittest
from pathlib import Path
from masontilutils.api.chatgpt import ChatGPTEthGenAPI, Region, Ethnicity, Sex

class TestChatGPTEthGenAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test environment before running tests"""
        # Get API key from environment variable
        cls.api_key = os.getenv('CHATGPT_API_KEY')
        if not cls.api_key:
            raise ValueError("CHATGPT_API_KEY environment variable not set")

        # Create API instance
        cls.api = ChatGPTEthGenAPI(cls.api_key)

        # Set up test images directory
        cls.test_images_dir = Path(__file__).parent / 'test_images'
        cls.test_images_dir.mkdir(exist_ok=True)

        # Define expected image-region mappings
        cls.expected_mappings = {
            '1_rahul sihag.jpg': {"ethnicity": Ethnicity.ASIA.value, "sex": Sex.MALE.value},
            '2_ryan pritchard.jpg': {"ethnicity": Ethnicity.EUROPE.value, "sex": Sex.MALE.value},
            '3_michelle lee.jpg': {"ethnicity": Ethnicity.ASIA.value, "sex": Sex.FEMALE.value},
            '4_timothy walker.jpg': {"ethnicity": Ethnicity.AFRICA.value, "sex": Sex.MALE.value},
            '5_sahil faroukie.jpg': {"ethnicity": Ethnicity.MIDDLE_EAST.value, "sex": Sex.MALE.value}
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
            result = self.api.call(image_path=str(image_path))
            print(f"Result for {image_name}: {result}")

            # Assert result matches expected region
            self.assertIsNotNone(result, f"Failed to get result for {image_name}")
            
            if result != expected_res:
                name = image_name.split('_')[1]
                result = self.api.call(str(image_path), name)

                self.assertIsNotNone(result, f"Failed to get result for {image_name}")
                print(f"Result for {image_name} with name {name}: {result}")
                self.assertEqual(
                result, 
                expected_res,
                )

            print(f"\n\n")

    def test_image_analysis_with_url(self):
        url = "https://media.licdn.com/dms/image/v2/C4E03AQGOZgLtycIRdg/profile-displayphoto-shrink_200_200/profile-displayphoto-shrink_200_200/0/1517726975275?e=1752710400&v=beta&t=nZo6W9gyIb7j_P11Zy6Z_AvLWeLLSmtHdh7VwLW5S3Q"
        result = self.api.call(url, parse_url=True)
        print(f"Result for {url}: {result}")

        self.assertEqual(result, {"ethnicity": Ethnicity.EUROPE.value, "sex": Sex.FEMALE.value})

                

    # def test_invalid_image(self):
    #     """Test handling of invalid image file"""
    #     invalid_path = self.test_images_dir / 'nonexistent.jpg'
    #     result = self.api.call(str(invalid_path))
    #     self.assertIsNone(result, "Should return None for invalid image path")

if __name__ == '__main__':
    unittest.main() 