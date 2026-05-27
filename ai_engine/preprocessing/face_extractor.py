import cv2
import numpy as np
import os
from typing import Optional, Tuple
from ai_engine.utils.logger import setup_logger

logger = setup_logger("face_extractor")

class FaceExtractor:
    def __init__(self, cascade_path: Optional[str] = None):
        if cascade_path is None:
            cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
            
        if not os.path.exists(cascade_path):
            logger.error(f"Haar cascade metadata missing at: {cascade_path}")
            raise FileNotFoundError(f"Cascade definition not found at: {cascade_path}")
            
        self.face_cascade = cv2.CascadeClassifier(cascade_path)
        logger.info("FaceExtractor instance initialized with Haar Cascade.")

    def extract_face(self, img_bgr: np.ndarray, padding: float = 0.15) -> Optional[np.ndarray]:
        try:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
            faces = self.face_cascade.detectMultiScale(
                gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
            )
            
            if len(faces) == 0:
                logger.debug("No human facial structures located in media matrix.")
                return None
                
            x, y, w, h = max(faces, key=lambda f: f[2] * f[3])
            
            pad_h = int(h * padding)
            pad_w = int(w * padding)
            
            h_max, w_max, _ = img_bgr.shape
            ymin = max(0, y - pad_h)
            ymax = min(h_max, y + h + pad_h)
            xmin = max(0, x - pad_w)
            xmax = min(w_max, x + w + pad_w)
            
            face_crop = img_bgr[ymin:ymax, xmin:xmax]
            return face_crop
            
        except Exception as e:
            logger.error(f"Facial boundaries crop failure: {e}")
            return None
