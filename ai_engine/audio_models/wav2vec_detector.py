import torch
import torch.nn as nn
from transformers import Wav2Vec2Model, Wav2Vec2Config
from ai_engine.utils.logger import setup_logger

logger = setup_logger("wav2vec_model")

class Wav2VecVoiceCloneDetector(nn.Module):
    """
    State-of-the-art audio network leveraging pre-trained Wav2Vec2 representations
    to classify raw 1D voice signals for synthetic artifacts.
    """
    def __init__(self, num_classes: int = 1, pretrained: bool = True, dropout_rate: float = 0.5):
        super(Wav2VecVoiceCloneDetector, self).__init__()
        
        logger.info(f"Instantiating Wav2Vec2 Voice Clone Detector. Pretrained={pretrained}")
        
        if pretrained:
            # Load pre-trained features encoder weights (frozen to prevent representation decay)
            self.wav2vec = Wav2Vec2Model.from_pretrained("facebook/wav2vec2-base")
            for param in self.wav2vec.parameters():
                param.requires_grad = False
        else:
            config = Wav2Vec2Config()
            self.wav2vec = Wav2Vec2Model(config)
            
        num_features = self.wav2vec.config.hidden_size
        
        # Dense classification head
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(num_features, 64),
            nn.ReLU(),
            nn.Linear(64, num_classes),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """
        Input shape: (Batch, Sequence_Length) representing 1D audio sample array.
        """
        # Extract features (Output shape: Batch, Time_Steps, Hidden_Size)
        outputs = self.wav2vec(x)
        features = outputs.last_hidden_state
        
        # Apply mean pooling over temporal frames
        mean_features = torch.mean(features, dim=1)
        
        out = self.classifier(mean_features)
        return out
