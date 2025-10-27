# test_api.py
"""
Unit tests for the Flask API endpoint.

Tests the /detect endpoint for image processing and luminaire detection.
"""
import unittest
import requests
import cv2
import numpy as np
from pathlib import Path
from multiprocessing import Process
from api import app
import time

class TestAPI(unittest.TestCase):
    """Test cases for the API endpoints."""
    
    @classmethod
    def setUpClass(cls):
        """Start the Flask server before running tests."""
        cls.server = Process(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
        cls.server.start()
        
        # Wait for server to be ready
        max_retries = 10
        for i in range(max_retries):
            try:
                requests.get("http://localhost:5000/", timeout=1)
                break
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                if i == max_retries - 1:
                    cls.server.terminate()
                    raise RuntimeError("Server failed to start within timeout period")
                time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        """Stop the Flask server after all tests complete."""
        cls.server.terminate()
        cls.server.join(timeout=5)
        if cls.server.is_alive():
            cls.server.kill()

    def test_detect_endpoint_with_valid_image(self):
        """Test the /detect endpoint with a valid image."""
        # Find a test image - try multiple possible locations
        test_image_paths = [
            Path("data/nyu_data/data/0001.jpg"),
            Path("data/yolo_dataset/images/val/val_00000.jpg"),
            Path("data/nyu_data/data/nyu2_test/0001.jpg")
        ]
        
        test_image_path = None
        for path in test_image_paths:
            if path.exists():
                test_image_path = path
                break
        
        self.assertIsNotNone(test_image_path, 
                           f"No test image found in any of: {[str(p) for p in test_image_paths]}")

        # Prepare the request
        with open(test_image_path, "rb") as f:
            files = {'file': (test_image_path.name, f.read(), 'image/jpeg')}
            response = requests.post("http://localhost:5000/detect", files=files, timeout=30)

        # Check the response
        self.assertEqual(response.status_code, 200, 
                        f"Expected 200, got {response.status_code}")
        data = response.json()
        self.assertIn('detections', data, "Response missing 'detections' key")
        self.assertIn('features', data, "Response missing 'features' key")
        self.assertIn('depth_map', data, "Response missing 'depth_map' key")
        self.assertIn('timing', data, "Response missing 'timing' key")
    
    def test_detect_endpoint_without_file(self):
        """Test the /detect endpoint when no file is provided."""
        response = requests.post("http://localhost:5000/detect", timeout=5)
        self.assertEqual(response.status_code, 400, 
                        "Expected 400 when no file is provided")
        data = response.json()
        self.assertIn('error', data, "Error response should contain 'error' key")

if __name__ == '__main__':
    unittest.main()
