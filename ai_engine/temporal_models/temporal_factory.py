import torch.nn as nn
from ai_engine.temporal_models.cnn_lstm import CNNLSTMClassifier
from ai_engine.temporal_models.temporal_transformer import TemporalTransformerClassifier
from ai_engine.temporal_models.sequence_model import FrameSequenceAggregator
from ai_engine.utils.logger import setup_logger

logger = setup_logger("temporal_factory")

class TemporalModelFactory:
    """
    Decoupled factory class designed to map configuration parameters to 
    instantiated PyTorch temporal/sequence model structures.
    """
    @staticmethod
    def create_model(model_name: str, sequence_length: int = 16, cnn_backbone: str = "resnet18", num_classes: int = 1, pretrained: bool = True, dropout_rate: float = 0.5) -> nn.Module:
        logger.info(f"Temporal Factory producing model: {model_name}")
        
        name_clean = model_name.lower().strip()
        
        if name_clean == "cnn_lstm" or name_clean == "cnnlstm":
            return CNNLSTMClassifier(
                cnn_backbone=cnn_backbone,
                lstm_hidden_dim=128,
                num_lstm_layers=1,
                num_classes=num_classes,
                pretrained=pretrained,
                dropout_rate=dropout_rate
            )
            
        elif name_clean in ["transformer", "temporal_transformer"]:
            return TemporalTransformerClassifier(
                cnn_backbone=cnn_backbone,
                num_heads=4,
                num_layers=2,
                num_classes=num_classes,
                pretrained=pretrained,
                dropout_rate=dropout_rate
            )
            
        elif name_clean in ["sequence", "sequence_model", "aggregator"]:
            return FrameSequenceAggregator(
                sequence_length=sequence_length,
                num_classes=num_classes,
                dropout_rate=dropout_rate
            )
            
        else:
            logger.error(f"Unrecognized temporal model architectural request: {model_name}")
            raise ValueError(f"Unknown temporal model: {model_name}")
