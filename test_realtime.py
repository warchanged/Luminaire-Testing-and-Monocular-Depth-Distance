# test_realtime.py
import unittest
import cv2
from pathlib import Path
from realtime import RealtimeLightDetection

class TestRealtime(unittest.TestCase):
    def test_process_frame(self):
        # Find a test image
        test_image_path = Path("data/nyu_data/data/0001.jpg")
        self.assertTrue(test_image_path.exists())

        # Read the image
        frame = cv2.imread(str(test_image_path))
        self.assertIsNotNone(frame)

        # Initialize the detector
        detector = RealtimeLightDetection()

        # Process the frame
        vis_frame, results, fps = detector.process_frame(frame)

        # Check the results
        self.assertIsNotNone(vis_frame)
        self.assertIsInstance(results, dict)
        self.assertIsInstance(fps, float)
        self.assertIn('detections', results)
        self.assertIn('features', results)
        self.assertIn('depth_map', results)
        self.assertIn('timing', results)

if __name__ == '__main__':
    unittest.main()
