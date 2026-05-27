import torch.nn as nn
from ai_engine.models.cnn_model import CustomDeepfakeCNN
from ai_engine.models.efficientnet_model import EfficientNetClassifier
from ai_engine.models.xception_model import XceptionClassifier
from ai_engine.utils.logger import setup_logger

logger = setup_logger("model_factory")

class ModelFactory:
    @staticmethod
    def create_model(model_name: str, num_classes: int = 1, pretrained: bool = True, dropout_rate: float = 0.5) -> nn.Module:
        logger.info(f"Factory producing model type: {model_name}")
        
        name_clean = model_name.lower().strip()
        
        if name_clean == "cnn":
            return CustomDeepfakeCNN(num_classes=num_classes, dropout_rate=dropout_rate)
            
        elif name_clean in ["efficientnet_b0", "efficientnet"]:
            return EfficientNetClassifier(
                num_classes=num_classes, 
                pretrained=pretrained, 
                dropout_rate=dropout_rate
            )
            
        elif name_clean == "xception":
            return XceptionClassifier(
                num_classes=num_classes,
                pretrained=pretrained,
                dropout_rate=dropout_rate
            )
            
        else:
            logger.error(f"Unrecognized model architectural request: {model_name}")
            raise ValueError(f"Unknown model name: {model_name}")
