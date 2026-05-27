import unittest
import numpy as np
import cv2
import os
import sys
import torch
# Insert path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine.preprocessing.face_extractor import FaceExtractor
from ai_engine.preprocessing.image_processor import ImageProcessor
from ai_engine.preprocessing.normalization import Normalizer

class TestPreprocessingPipeline(unittest.TestCase):
    def setUp(self):
        self.mock_image = np.ones((300, 300, 3), dtype=np.uint8) * 128
        cv2.rectangle(self.mock_image, (100, 100), (200, 200), (200, 200, 200), -1)

    def test_image_normalization_dimensions(self):
        img_rgb = cv2.cvtColor(self.mock_image, cv2.COLOR_BGR2RGB)
        tensor = Normalizer.to_normalized_tensor(img_rgb, apply_imagenet=True)
        
        self.assertEqual(tensor.shape, (3, 300, 300))
        self.assertEqual(tensor.dtype, torch.float32)

    def test_image_processor_falls_back(self):
        processor = ImageProcessor(target_size=(224, 224), extract_faces=True)
        blank_img = np.zeros((100, 100, 3), dtype=np.uint8)
        
        temp_path = "temp_test_image.jpg"
        cv2.imwrite(temp_path, blank_img)
        
        try:
            out = processor.load_and_preprocess(temp_path)
            self.assertIsNotNone(out)
            self.assertEqual(out.shape, (224, 224, 3))
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

if __name__ == "__main__":
    unittest.main()
