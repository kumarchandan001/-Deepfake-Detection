import cv2
import numpy as np
import torch
import time
from typing import Dict, Any, Optional, Tuple
from ai_engine.inference.inference_engine import DeepfakeInferenceEngine
from ai_engine.preprocessing.face_extractor import FaceExtractor
from ai_engine.preprocessing.normalization import Normalizer
from ai_engine.utils.logger import setup_logger

logger = setup_logger("stream_processor")

class RealtimeStreamProcessor:
    """
    Executes real-time, low-latency face crops, CPU/GPU tensor mapping, 
    and model inference evaluations on individual frame matrices.
    """
    def __init__(self, model_path: Optional[str] = None):
        self.engine = DeepfakeInferenceEngine(model_path=model_path)
        self.extractor = FaceExtractor()
        logger.info("RealtimeStreamProcessor loaded core inference engine.")

    def process_frame(self, frame_bgr: np.ndarray) -> Tuple[np.ndarray, Dict[str, Any]]:
        """
        Ingests raw BGR camera frame, extracts facial region, executes GPU inference,
        and returns annotated frame alongside scoring metadata.
        """
        # 1. Capture dimensions
        h, w, _ = frame_bgr.shape
        
        # 2. Extract facial coordinates
        face = self.extractor.extract_face(frame_bgr)
        
        prediction = "REAL"
        confidence = 100.0
        raw_score = 0.0
        
        annotated_frame = frame_bgr.copy()
        
        if face is not None:
            # We have a face crop! Run real-time inference on the crop
            # Convert face RGB for engine
            face_rgb = cv2.cvtColor(face, cv2.COLOR_BGR2RGB)
            
            # Temporary crop save bypass to optimize execution (Runs tensors directly)
            # Normalizer is extremely fast in Python memory
            resized = cv2.resize(face_rgb, (224, 224), interpolation=cv2.INTER_LINEAR)
            tensor = Normalizer.to_normalized_tensor(resized, apply_imagenet=True)
            # Add batch dimension (1, C, H, W) and transfer to CUDA
            tensor_batch = tensor.unsqueeze(0).to(self.engine.device)
            
            # Model forward check
            with torch.no_grad():
                prediction_prob = self.engine.model(tensor_batch).item()
                
            confidence_threshold = self.engine.config.get("inference.confidence_threshold", 0.5)
            is_fake = prediction_prob >= confidence_threshold
            
            prediction = "FAKE" if is_fake else "REAL"
            confidence = prediction_prob if is_fake else (1.0 - prediction_prob)
            confidence = float(confidence * 100)
            raw_score = float(prediction_prob)
            
            # Overlay color boundary graphics
            box_color = (0, 0, 255) if is_fake else (0, 255, 0) # Red for FAKE, Green for REAL
            
            # Draw facial scanner graphic box
            cv2.rectangle(annotated_frame, (int(w*0.3), int(h*0.2)), (int(w*0.7), int(h*0.8)), box_color, 2)
            cv2.putText(
                annotated_frame, 
                f"{prediction} ({confidence:.1f}%)", 
                (int(w*0.3), int(h*0.2) - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.6, 
                box_color, 
                2
            )
        else:
            # Draw idle search box
            cv2.rectangle(annotated_frame, (int(w*0.35), int(h*0.25)), (int(w*0.65), int(h*0.75)), (255, 0, 0), 1)
            cv2.putText(
                annotated_frame, 
                "LOCATING SUBJECT...", 
                (int(w*0.35), int(h*0.25) - 10), 
                cv2.FONT_HERSHEY_SIMPLEX, 
                0.5, 
                (255, 0, 0), 
                1
            )

        metadata = {
            "prediction": prediction,
            "confidence": round(confidence, 2),
            "raw_score": raw_score,
            "face_detected": face is not None
        }
        
        return annotated_frame, metadata
