# test_realtime.py
"""
Unit tests for real-time light detection functionality.

Tests the RealtimeLightDetection class for frame processing.
"""
import unittest
import cv2
import numpy as np
from pathlib import Path
from realtime import RealtimeLightDetection

class TestRealtime(unittest.TestCase):
    """Test cases for real-time detection."""
    
    @classmethod
    def setUpClass(cls):
        """Initialize the detector once for all tests."""
        cls.detector = RealtimeLightDetection()
    
    def _find_test_image(self):
        """
        Find a valid test image from multiple possible locations.
        
        Returns:
            Path: Path to a valid test image
            
        Raises:
            FileNotFoundError: If no test image is found
        """
        test_image_paths = [
            Path("data/nyu_data/data/0001.jpg"),
            Path("data/yolo_dataset/images/val/val_00000.jpg"),
            Path("data/nyu_data/data/nyu2_test/0001.jpg")
        ]
        
        for path in test_image_paths:
            if path.exists():
                return path
        
        raise FileNotFoundError(
            f"No test image found in any of: {[str(p) for p in test_image_paths]}"
        )
    
    def test_process_frame_with_valid_image(self):
        """Test processing a valid image frame."""
        # Find a test image
        test_image_path = self._find_test_image()
        
        # Read the image
        frame = cv2.imread(str(test_image_path))
        self.assertIsNotNone(frame, f"Failed to read image: {test_image_path}")
        self.assertEqual(len(frame.shape), 3, "Image should have 3 dimensions (H, W, C)")

        # Process the frame
        vis_frame, results, fps = self.detector.process_frame(frame)

        # Check the results
        self.assertIsNotNone(vis_frame, "Visualized frame should not be None")
        self.assertEqual(vis_frame.shape, frame.shape, 
                        "Visualized frame should have same shape as input")
        
        self.assertIsInstance(results, dict, "Results should be a dictionary")
        self.assertIn('detections', results, "Results missing 'detections' key")
        self.assertIn('features', results, "Results missing 'features' key")
        self.assertIn('depth_map', results, "Results missing 'depth_map' key")
        self.assertIn('timing', results, "Results missing 'timing' key")
        
        self.assertIsInstance(fps, float, "FPS should be a float")
        self.assertGreater(fps, 0, "FPS should be positive")
    
    def test_process_frame_with_invalid_input(self):
        """Test processing with invalid input (None)."""
        with self.assertRaises((AttributeError, TypeError, ValueError)):
            self.detector.process_frame(None)
    
    def test_process_frame_with_empty_image(self):
        """Test processing with an empty image array."""
        empty_frame = np.zeros((0, 0, 3), dtype=np.uint8)
        with self.assertRaises((ValueError, RuntimeError, cv2.error)):
            self.detector.process_frame(empty_frame)

if __name__ == '__main__':
    unittest.main()
