# test_api.py
import unittest
import requests
import cv2
import numpy as np
from pathlib import Path
from multiprocessing import Process
from api import app

class TestAPI(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = Process(target=app.run, kwargs={'host': '0.0.0.0', 'port': 5000})
        cls.server.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.terminate()
        cls.server.join()

    def test_detect_endpoint(self):
        # Find a test image
        test_image_path = Path("data/nyu_data/data/0001.jpg")
        self.assertTrue(test_image_path.exists())

        # Prepare the request
        with open(test_image_path, "rb") as f:
            files = {'file': (test_image_path.name, f.read(), 'image/jpeg')}
            response = requests.post("http://localhost:5000/detect", files=files)

        # Check the response
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('detections', data)
        self.assertIn('features', data)
        self.assertIn('depth_map', data)
        self.assertIn('timing', data)

if __name__ == '__main__':
    unittest.main()
