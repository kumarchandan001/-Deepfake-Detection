import os
import sys
from typing import Dict, Any
# Setup paths
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from ai_engine.video_inference.video_inference_engine import DeepfakeVideoInferenceEngine
from ai_engine.utils.logger import setup_logger

logger = setup_logger("video_detection_service")

class VideoDetectionService:
    """
    Decoupled service layer sitting between video routing endpoints 
    and the deep learning sequential evaluation engine.
    """
    def __init__(self):
        self.engine = None

    def get_engine(self) -> DeepfakeVideoInferenceEngine:
        """
        Lazily loads the target video inference engine.
        """
        if self.engine is None:
            logger.info("Initializing lazily loaded DeepfakeVideoInferenceEngine...")
            try:
                self.engine = DeepfakeVideoInferenceEngine()
            except Exception as e:
                logger.error(f"Failed to initialize raw video inference engine: {e}")
                raise e
        return self.engine

    def process_video_analysis(self, video_path: str) -> Dict[str, Any]:
        """
        Routes the target video file path to the underlying evaluation engine.
        """
        engine = self.get_engine()
        return engine.analyze_video(video_path)
