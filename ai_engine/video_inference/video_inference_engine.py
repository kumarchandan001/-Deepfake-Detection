import os
import torch
import time
import cv2
import numpy as np
from typing import Dict, Any, Optional, List
from ai_engine.utils.config import Config
from ai_engine.utils.device import get_device
from ai_engine.video_processing.video_loader import VideoLoader
from ai_engine.video_processing.frame_extractor import FrameExtractor
from ai_engine.video_processing.frame_sampler import FrameSampler
from ai_engine.video_processing.face_tracker import FaceTracker
from ai_engine.inference.inference_engine import DeepfakeInferenceEngine
from ai_engine.utils.logger import setup_logger

logger = setup_logger("video_inference_engine")

class DeepfakeVideoInferenceEngine:
    def __init__(self, frame_engine_path: Optional[str] = None):
        self.config = Config()
        self.device = get_device()
        self.frame_engine = DeepfakeInferenceEngine(model_path=frame_engine_path)
        
        self.sequence_length = self.config.get("dataset.sequence_length", 16)
        self.sampler = FrameSampler(sequence_length=self.sequence_length)
        self.tracker = FaceTracker()
        
        logger.info("DeepfakeVideoInferenceEngine fully compiled and loaded.")

    def analyze_video(self, video_path: str) -> Dict[str, Any]:
        start_time = time.time()
        
        try:
            loader = VideoLoader(video_path)
            total_frames = loader.metadata.get("frame_count", 0)
            
            if total_frames <= 0:
                return {"success": False, "error": "Empty video file."}

            indices = self.sampler.get_uniform_indices(total_frames)
            
            extractor = FrameExtractor(loader)
            raw_frames = extractor.extract_multiple_frames(indices)
            loader.close()
            
            face_crops = self.tracker.track_face_sequence(raw_frames)
            
            frame_scores = []
            fake_count = 0
            temp_crop_path = f"temp_crop_{int(time.time())}.jpg"
            
            for crop in face_crops:
                crop_bgr = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)
                cv2.imwrite(temp_crop_path, crop_bgr)
                
                res = self.frame_engine.predict_image(temp_crop_path)
                
                if res.get("success", False):
                    score = res["raw_score"]
                    frame_scores.append(score)
                    if res["prediction"] == "FAKE":
                        fake_count += 1
                        
            if os.path.exists(temp_crop_path):
                os.remove(temp_crop_path)
                
            if len(frame_scores) == 0:
                return {"success": False, "error": "No frames could be successfully analyzed."}

            mean_score = float(np.mean(frame_scores))
            fake_frame_ratio = fake_count / len(frame_scores)
            
            confidence_threshold = self.config.get("inference.confidence_threshold", 0.5)
            is_fake = mean_score >= confidence_threshold or fake_frame_ratio > 0.4
            
            prediction_label = "FAKE" if is_fake else "REAL"
            confidence = mean_score if is_fake else (1.0 - mean_score)
            processing_time = time.time() - start_time
            
            return {
                "success": True,
                "prediction": prediction_label,
                "confidence": round(float(confidence * 100), 2),
                "fake_frame_ratio": round(fake_frame_ratio, 4),
                "mean_score": mean_score,
                "processing_time": round(processing_time, 4)
            }
            
        except Exception as e:
            logger.error(f"Video analysis execution failure: {e}")
            return {"success": False, "error": str(e)}
