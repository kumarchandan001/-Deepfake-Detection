import os
import sys
from typing import Dict, Any
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine.inference.inference_engine import DeepfakeInferenceEngine
from ai_engine.utils.logger import setup_logger

logger = setup_logger("detection_service")

class DetectionService:
    def __init__(self):
        self.engine = None
        
    def get_engine(self) -> DeepfakeInferenceEngine:
        if self.engine is None:
            logger.info("Initializing lazily loaded DeepfakeInferenceEngine...")
            try:
                self.engine = DeepfakeInferenceEngine()
            except Exception as e:
                logger.error(f"Failed to initialize raw inference engine: {e}")
                raise e
        return self.engine

    def process_image_analysis(self, image_path: str) -> Dict[str, Any]:
        engine = self.get_engine()
        return engine.predict_image(image_path)
