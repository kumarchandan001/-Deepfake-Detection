import cv2
import numpy as np
from PIL import Image
from typing import Optional, Tuple
from ai_engine.preprocessing.face_extractor import FaceExtractor
from ai_engine.utils.logger import setup_logger

logger = setup_logger("image_processor")

class ImageProcessor:
    def __init__(self, target_size: Tuple[int, int] = (224, 224), extract_faces: bool = True):
        self.target_size = target_size
        self.extract_faces = extract_faces
        self.extractor = FaceExtractor() if extract_faces else None
        logger.info(f"ImageProcessor configured: Size={target_size}, ExtractFaces={extract_faces}")

    def load_and_preprocess(self, file_path: str) -> Optional[np.ndarray]:
        try:
            img_bgr = cv2.imread(file_path)
            if img_bgr is None:
                logger.error(f"Failed to read image matrix from path: {file_path}")
                return None
                
            processed_img = img_bgr
            if self.extract_faces and self.extractor is not None:
                face = self.extractor.extract_face(img_bgr)
                if face is not None:
                    processed_img = face
                else:
                    logger.debug(f"Face extraction failed. Falling back to global image crop: {file_path}")

            img_rgb = cv2.cvtColor(processed_img, cv2.COLOR_BGR2RGB)
            img_resized = cv2.resize(img_rgb, self.target_size, interpolation=cv2.INTER_LINEAR)
            
            return img_resized
            
        except Exception as e:
            logger.error(f"Image loading pipeline failure for file {file_path}: {e}")
            return None

    @staticmethod
    def ndarray_to_pillow(img_arr: np.ndarray) -> Image.Image:
        return Image.fromarray(img_arr)
