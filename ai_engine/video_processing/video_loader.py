import cv2
import os
from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("video_loader")

class VideoLoader:
    """
    Ingests video assets of varying formats (.mp4, .avi, .mov, .mkv),
    managing secure file descriptors, stream loading, and metadata extraction.
    """
    def __init__(self, file_path: str):
        self.file_path = file_path
        if not os.path.exists(file_path):
            logger.error(f"Target video file missing: {file_path}")
            raise FileNotFoundError(f"Video file not found at: {file_path}")
            
        self.cap: Optional[cv2.VideoCapture] = None
        self.metadata: Dict[str, Any] = {}
        self._load_and_extract_metadata()

    def _load_and_extract_metadata(self) -> None:
        """
        Loads video stream and extracts dimensions, fps, duration, and frame counts.
        """
        try:
            self.cap = cv2.VideoCapture(self.file_path)
            if not self.cap.isOpened():
                logger.error(f"OpenCV failed to open video stream at: {self.file_path}")
                raise IOError(f"Could not open video file: {self.file_path}")

            # Capture video properties
            fps = self.cap.get(cv2.CAP_PROP_FPS)
            frame_count = int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))
            width = int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Calculate duration in seconds
            duration = frame_count / fps if fps > 0 else 0.0
            
            self.metadata = {
                "filepath": self.file_path,
                "fps": float(fps),
                "frame_count": frame_count,
                "width": width,
                "height": height,
                "duration_seconds": round(duration, 4),
                "format": os.path.splitext(self.file_path)[1].lower()
            }
            logger.info(f"Successfully loaded video metadata: {self.metadata}")
            
        except Exception as e:
            logger.error(f"Failed to extract video properties for {self.file_path}: {e}")
            self.close()
            raise

    def get_capture(self) -> cv2.VideoCapture:
        """
        Returns active OpenCV VideoCapture stream object.
        """
        if self.cap is None or not self.cap.isOpened():
            self.cap = cv2.VideoCapture(self.file_path)
        return self.cap

    def close(self) -> None:
        """
        Closes active video descriptors.
        """
        if self.cap is not None:
            self.cap.release()
            self.cap = None
            logger.debug("Closed active video stream capture.")

    def __del__(self):
        self.close()
