import cv2
import numpy as np
from typing import List, Optional
from ai_engine.video_processing.video_loader import VideoLoader
from ai_engine.utils.logger import setup_logger

logger = setup_logger("frame_extractor")

class FrameExtractor:
    """
    Handles efficient seek-based frame extraction from loaded VideoLoader targets.
    """
    def __init__(self, loader: VideoLoader):
        self.loader = loader

    def extract_frame_at_index(self, index: int) -> Optional[np.ndarray]:
        """
        Seeks video capture directly to specific index and reads a single BGR frame.
        """
        cap = self.loader.get_capture()
        if not cap.isOpened():
            logger.error("VideoCapture descriptor is closed. Frame extraction aborted.")
            return None

        # Apply seek boundary check
        total_frames = self.loader.metadata.get("frame_count", 0)
        if index < 0 or index >= total_frames:
            logger.error(f"Target frame index {index} lies outside boundary [0, {total_frames - 1}].")
            return None

        try:
            # Set the position frame property
            cap.set(cv2.CAP_PROP_POS_FRAMES, index)
            ret, frame = cap.read()
            if not ret:
                logger.warning(f"VideoCapture seek success but frame read failed at index: {index}")
                return None
            return frame
        except Exception as e:
            logger.error(f"Error seeking or reading frame at index {index}: {e}")
            return None

    def extract_multiple_frames(self, indices: List[int]) -> List[np.ndarray]:
        """
        Reads a batch of target indexes dynamically, optimizing seeks for forward progression.
        """
        frames = []
        # Sort indices to prevent backward seeking loops (backward seeks are extremely slow in OpenCV)
        sorted_indices = sorted(indices)
        
        cap = self.loader.get_capture()
        
        for idx in sorted_indices:
            frame = self.extract_frame_at_index(idx)
            if frame is not None:
                frames.append(frame)
                
        return frames
