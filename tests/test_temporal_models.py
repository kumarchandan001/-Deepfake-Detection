import unittest
import torch
import os
import sys
# Insert path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine.temporal_models.temporal_factory import TemporalModelFactory

class TestTemporalDeepfakeModels(unittest.TestCase):
    """
    Validates sequential forward pass shape mappings for CNN-LSTM and Transformers.
    """
    def test_cnn_lstm_forward(self):
        """
        CNN-LSTM should process sequence batch tensors: (B, T, C, H, W)
        and return output dimensions: (B, 1)
        """
        model = TemporalModelFactory.create_model(
            model_name="cnn_lstm", 
            sequence_length=4, 
            cnn_backbone="resnet18", 
            pretrained=False
        )
        # Mock sequence batch: Batch=2, Seq=4, C=3, H=224, W=224
        dummy_sequence = torch.randn(2, 4, 3, 224, 224)
        
        with torch.no_grad():
            preds = model(dummy_sequence)
            
        self.assertEqual(preds.shape, (2, 1))

    def test_transformer_forward(self):
        """
        Temporal Transformer should process sequence batch tensors.
        """
        model = TemporalModelFactory.create_model(
            model_name="transformer",
            sequence_length=4,
            cnn_backbone="resnet18",
            pretrained=False
        )
        dummy_sequence = torch.randn(2, 4, 3, 224, 224)
        
        with torch.no_grad():
            preds = model(dummy_sequence)
            
        self.assertEqual(preds.shape, (2, 1))

if __name__ == "__main__":
    unittest.main()
