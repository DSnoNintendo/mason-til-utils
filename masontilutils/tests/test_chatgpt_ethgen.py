import os
import unittest
from pathlib import Path
from masontilutils.api.chatgpt import ChatGPTEthGenAPI, EthnicityRegion

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
            '1_rahul sihag.jpg': EthnicityRegion.ASIA,
            '2_ryan pritchard.jpg': EthnicityRegion.EUROPE,
            '3_michelle lee.jpg': EthnicityRegion.ASIA,
            '4_timothy walker.jpg': EthnicityRegion.AFRICA
        }

    def test_image_analysis(self):
        """Test that images are correctly analyzed and match expected regions"""
        for image_name, expected_region in self.expected_mappings.items():

            print(f"========== Testing {image_name} ==========")
            image_path = self.test_images_dir / image_name
            
            # Skip if test image doesn't exist
            if not image_path.exists():
                self.skipTest(f"Test image {image_name} not found")
            
            # Get prediction
            result = self.api.call(str(image_path))
            print(f"Result for {image_name}: {result}")

            # Assert result matches expected region
            self.assertIsNotNone(result, f"Failed to get result for {image_name}")
            
            if result != expected_region:
                print(f"Expected {expected_region.value} for {image_name}, got {result.value if result else None}")
                print("Getting result using name and image")
                name = image_name.split('_')[1]
                result = self.api.call(str(image_path), name)

                self.assertIsNotNone(result, f"Failed to get result for {image_name}")
                print(f"Result for {image_name} with name {name}: {result}")
                self.assertEqual(
                result, 
                expected_region,
                f"Expected {expected_region.value} for {image_name}, got {result.value if result else None}"
                )

            print(f"\n\n")

                

    # def test_invalid_image(self):
    #     """Test handling of invalid image file"""
    #     invalid_path = self.test_images_dir / 'nonexistent.jpg'
    #     result = self.api.call(str(invalid_path))
    #     self.assertIsNone(result, "Should return None for invalid image path")

if __name__ == '__main__':
    unittest.main() 