import os
import torch
import numpy as np
import time
from typing import Dict, Any, Optional
from ai_engine.utils.config import Config
from ai_engine.utils.device import get_device
from ai_engine.audio_models.audio_model_factory import AudioModelFactory
from ai_engine.audio_processing.audio_loader import AudioLoader
from ai_engine.audio_processing.spectrogram import SpectrogramExtractor
from ai_engine.audio_processing.waveform_processor import WaveformProcessor
from ai_engine.utils.logger import setup_logger

logger = setup_logger("realtime_audio_engine")

class RealtimeAudioInferenceEngine:
    """
    Ingests raw 1D vocal waveform matrices, extracts target Mel Spectrograms,
    runs GPU-accelerated voice clone predictions, and returns structured outputs.
    """
    def __init__(self, model_path: Optional[str] = None):
        self.config = Config()
        self.device = get_device()
        
        # Setup model configuration
        model_name = self.config.get("model.audio_backbone", "audio_cnn")
        checkpoint_dir = self.config.get("model.checkpoint_dir", "ai_engine/checkpoints")
        
        if model_path is None:
            model_path = os.path.join(checkpoint_dir, "best_audio_model.pth")
            
        self.model_path = model_path
        
        # Load audio signal processing parameters
        self.loader = AudioLoader(target_sr=16000)
        self.processor = WaveformProcessor(target_duration=4.0, sr=16000)
        self.extractor = SpectrogramExtractor(n_mels=128)
        
        # Instantiate models
        self.model = AudioModelFactory.create_model(
            model_name=model_name,
            pretrained=False,
            dropout_rate=0.0
        )
        
        self._load_weights()
        self.model.to(self.device)
        self.model.eval() # Freeze Dropout/BN loops
        logger.info("RealtimeAudioInferenceEngine fully compiled and loaded.")

    def _load_weights(self) -> None:
        if not os.path.exists(self.model_path):
            logger.warning(f"Audio weights file missing at: {self.model_path}. Running unit/mock tests is active.")
            return
            
        logger.info(f"Loading audio weights checkpoint from: {self.model_path}")
        checkpoint = torch.load(self.model_path, map_location=self.device)
        if 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint)

    def predict_waveform(self, y: np.ndarray, sr: int) -> Dict[str, Any]:
        """
        Runs prediction over 1D vocal array.
        """
        start_time = time.time()
        
        try:
            # 1. Pad/crop waveform to target uniform length (4 seconds)
            y_processed = self.processor.process_waveform(y)
            
            # 2. Extract 2D Mel Spectrogram (H, W)
            spec_db = self.extractor.compute_mel_spectrogram(y_processed, sr)
            
            # 3. Add Channel & Batch dimensions for 2D CNN: (1, 1, H, W)
            # Normalize to [-1.0, 1.0] for standard spectral input
            spec_normalized = (spec_db - np.mean(spec_db)) / (np.std(spec_db) + 1e-8)
            spec_tensor = torch.tensor(spec_normalized, dtype=torch.float32).unsqueeze(0).unsqueeze(0)
            
            # Transfer to CUDA
            spec_tensor = spec_tensor.to(self.device)
            
            # 4. Forward model pass
            with torch.no_grad():
                prediction_prob = self.model(spec_tensor).item()
                
            processing_time = time.time() - start_time
            
            # 5. Format results
            confidence_threshold = self.config.get("inference.confidence_threshold", 0.5)
            is_fake = prediction_prob >= confidence_threshold
            
            prediction_label = "FAKE_VOICE" if is_fake else "REAL_VOICE"
            confidence = prediction_prob if is_fake else (1.0 - prediction_prob)
            
            return {
                "success": True,
                "prediction": prediction_label,
                "confidence": round(float(confidence * 100), 2),
                "raw_score": float(prediction_prob),
                "processing_time": round(float(processing_time), 4)
            }
            
        except Exception as e:
            logger.error(f"Failed to execute audio inference pass: {e}")
            return {"success": False, "error": str(e)}

    def predict_audio_file(self, file_path: str) -> Dict[str, Any]:
        """
        Loads local audio asset and parses predictions.
        """
        res = self.loader.load_audio(file_path)
        if res is None:
            return {"success": False, "error": "Failed to load audio."}
            
        y, sr = res
        return self.predict_waveform(y, sr)

# Backward compatibility alias
class RealtimeAudioEngine(RealtimeAudioInferenceEngine):
    def analyze_voice_track(self, file_path: str) -> Dict[str, Any]:
        return self.predict_audio_file(file_path)

