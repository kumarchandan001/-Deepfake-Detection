import os
import torch
import time
from typing import Dict, Any, Optional
from ai_engine.utils.config import Config
from ai_engine.utils.device import get_device
from ai_engine.models.model_factory import ModelFactory
from ai_engine.preprocessing.image_processor import ImageProcessor
from ai_engine.preprocessing.normalization import Normalizer
from ai_engine.utils.logger import setup_logger

logger = setup_logger("inference_engine")

class DeepfakeInferenceEngine:
    def __init__(self, model_path: Optional[str] = None):
        self.config = Config()
        self.device = get_device()
        
        if model_path is None:
            checkpoint_dir = self.config.get("model.checkpoint_dir", "ai_engine/checkpoints")
            model_path = os.path.join(checkpoint_dir, "best_model.pth")
            
        self.model_path = model_path
        
        target_size = tuple(self.config.get("dataset.target_size", [224, 224]))
        self.processor = ImageProcessor(target_size=target_size, extract_faces=True)
        
        self.model = ModelFactory.create_model(
            model_name=self.config.get("model.backbone", "efficientnet_b0"),
            pretrained=False,
            dropout_rate=0.0
        )
        
        self._load_weights()
        self.model.to(self.device)
        self.model.eval()
        logger.info("Inference engine fully loaded and operational.")

    def _load_weights(self) -> None:
        if not os.path.exists(self.model_path):
            logger.warning(f"Saved weights file not found at: {self.model_path}. Continuing with randomly initialized weights for development/testing.")
            return
            
        logger.info(f"Loading weights state dictionary from: {self.model_path}")
        checkpoint = torch.load(self.model_path, map_location=self.device)
        
        if 'model_state_dict' in checkpoint:
            self.model.load_state_dict(checkpoint['model_state_dict'])
        else:
            self.model.load_state_dict(checkpoint)

    def predict_image(self, file_path: str) -> Dict[str, Any]:
        start_time = time.time()
        
        img_arr = self.processor.load_and_preprocess(file_path)
        if img_arr is None:
            logger.error(f"Inference input processing failed for image: {file_path}")
            return {
                "success": False,
                "error": "Failed to process image payload."
            }

        img_tensor = Normalizer.to_normalized_tensor(img_arr, apply_imagenet=True)
        img_tensor = img_tensor.unsqueeze(0).to(self.device)

        with torch.no_grad():
            prediction_prob = self.model(img_tensor).item()

        processing_time = time.time() - start_time
        
        confidence_threshold = self.config.get("inference.confidence_threshold", 0.5)
        is_fake = prediction_prob >= confidence_threshold
        
        prediction_label = "FAKE" if is_fake else "REAL"
        confidence = prediction_prob if is_fake else (1.0 - prediction_prob)
        
        return {
            "success": True,
            "prediction": prediction_label,
            "confidence": round(float(confidence * 100), 2),
            "raw_score": float(prediction_prob),
            "processing_time": round(float(processing_time), 4)
        }
