import torch
import torch.nn as nn
import timm
from ai_engine.utils.logger import setup_logger

logger = setup_logger("efficientnet_model")

class EfficientNetClassifier(nn.Module):
    def __init__(self, num_classes: int = 1, pretrained: bool = True, dropout_rate: float = 0.5):
        super(EfficientNetClassifier, self).__init__()
        
        logger.info(f"Instantiating EfficientNet-B0. Pretrained={pretrained}")
        self.backbone = timm.create_model(
            "efficientnet_b0", pretrained=pretrained, num_classes=0
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
