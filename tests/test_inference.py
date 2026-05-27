import unittest
import torch
import os
import sys
# Insert path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine.models.model_factory import ModelFactory

class TestModelInferencePass(unittest.TestCase):
    """
    Validates model instantiation dynamics and forward dimensions scaling.
    """
    def test_custom_cnn_creation(self):
        """
        Custom CNN should load and run predictions with expected shape.
        """
        model = ModelFactory.create_model("cnn", num_classes=1, pretrained=False)
        dummy_batch = torch.randn(4, 3, 224, 224)
        
        with torch.no_grad():
            preds = model(dummy_batch)
            
        self.assertEqual(preds.shape, (4, 1))

    def test_efficientnet_creation(self):
        """
        EfficientNet wrapper should load features.
        """
        model = ModelFactory.create_model("efficientnet", num_classes=1, pretrained=False)
        dummy_batch = torch.randn(2, 3, 224, 224)
        
        with torch.no_grad():
            preds = model(dummy_batch)
            
        self.assertEqual(preds.shape, (2, 1))

if __name__ == "__main__":
    unittest.main()
