import torch
import torch.nn as nn
from ai_engine.utils.logger import setup_logger

logger = setup_logger("sequence_model")

class FrameSequenceAggregator(nn.Module):
    """
    Takes independent frame predictions (or low-level CNN spatial scores) 
    and pools them temporally using trainable dense layer mappings.
    """
    def __init__(self, sequence_length: int = 16, num_classes: int = 1, dropout_rate: float = 0.5):
        super(FrameSequenceAggregator, self).__init__()
        
        logger.info(f"Instantiating Frame Sequence Aggregator: Length={sequence_length}")
        
        # Inbound shape: (Batch, Sequence_Length, 1) -> (Batch, Sequence_Length)
        self.fc = nn.Sequential(
            nn.Linear(sequence_length, 32),
            nn.ReLU(),
            nn.Dropout(p=dropout_rate),
            nn.Linear(32, num_classes),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Input shape: (Batch, Sequence_Length, 1) or (Batch, Sequence_Length)
        """
        if x.dim() == 3:
            # Squeeze channel dimensions
            x = x.squeeze(-1)
            
        out = self.fc(x)
        return out
