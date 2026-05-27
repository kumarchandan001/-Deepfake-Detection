import torch
import torch.nn as nn
import timm
from ai_engine.utils.logger import setup_logger

logger = setup_logger("xception_model")

class XceptionClassifier(nn.Module):
    """
    A classification model leveraging the Xception architecture's 
    Depthwise Separable Convolutions to detect manipulation boundaries.
    """
    def __init__(self, num_classes: int = 1, pretrained: bool = True, dropout_rate: float = 0.5):
        super(XceptionClassifier, self).__init__()
        
        logger.info(f"Instantiating Xception Backbone. Pretrained={pretrained}")
        # xception in timm is highly optimized for local high frequency features
        try:
            self.backbone = timm.create_model(
                "xception", pretrained=pretrained, num_classes=0
            )
        except Exception as e:
            logger.warning(f"Failed to load default xception: {e}. Falling back to legacy_xception.")
            self.backbone = timm.create_model(
                "legacy_xception", pretrained=pretrained, num_classes=0
            )
            
        num_features = self.backbone.num_features
        
        self.classifier = nn.Sequential(
            nn.Dropout(p=dropout_rate),
            nn.Linear(num_features, num_classes),
            nn.Sigmoid()
        )

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        features = self.backbone(x)
        out = self.classifier(features)
        return out
