import torch.nn as nn
from ai_engine.audio_models.cnn_audio_model import SpectrogramCNNClassifier
from ai_engine.audio_models.wav2vec_detector import Wav2VecVoiceCloneDetector
from ai_engine.utils.logger import setup_logger

logger = setup_logger("audio_model_factory")

class AudioModelFactory:
    """
    Decoupled factory class designed to map configuration parameters to 
    instantiated PyTorch audio classifier structures.
    """
    @staticmethod
    def create_model(model_name: str, num_classes: int = 1, pretrained: bool = True, dropout_rate: float = 0.5) -> nn.Module:
        logger.info(f"Audio Factory producing model type: {model_name}")
        
        name_clean = model_name.lower().strip()
        
        if name_clean == "spectrogram_cnn" or name_clean == "audio_cnn":
            return SpectrogramCNNClassifier(num_classes=num_classes, dropout_rate=dropout_rate)
            
        elif name_clean in ["wav2vec", "wav2vec2", "audio_wav2vec"]:
            return Wav2VecVoiceCloneDetector(
                num_classes=num_classes, 
                pretrained=pretrained, 
                dropout_rate=dropout_rate
            )
            
        else:
            logger.error(f"Unrecognized audio model architectural request: {model_name}")
            raise ValueError(f"Unknown audio model name: {model_name}")
