import cv2
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from ai_engine.preprocessing.face_extractor import FaceExtractor
from ai_engine.utils.logger import setup_logger

logger = setup_logger("face_tracker")

class FaceTracker:
    """
    Locates, tracks, and extracts facial frames across video timelines.
    Uses Intersection-over-Union (IoU) overlap bounds to ensure target identity consistency.
    """
    def __init__(self, overlap_threshold: float = 0.3):
        self.extractor = FaceExtractor()
        self.overlap_threshold = overlap_threshold
        logger.info(f"FaceTracker initialized: IoU overlap threshold={overlap_threshold}")

    @staticmethod
    def _compute_iou(boxA: Tuple[int, int, int, int], boxB: Tuple[int, int, int, int]) -> float:
        """
        Computes standard Intersection over Union (IoU) metric between two bounding boxes.
        Format: (xmin, ymin, xmax, ymax)
        """
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        interArea = max(0, xB - xA) * max(0, yB - yA)
        boxAArea = (boxA[2] - boxA[0]) * (boxA[3] - boxA[1])
        boxBArea = (boxB[2] - boxB[0]) * (boxB[3] - boxB[1])

        unionArea = float(boxAArea + boxBArea - interArea)
        return interArea / unionArea if unionArea > 0 else 0.0

    def track_face_sequence(self, frames: List[np.ndarray]) -> List[np.ndarray]:
        """
        Tracks the primary actor across sequential frames, extracting aligned, matching face crops.
        """
        tracked_sequence = []
        last_box: Optional[Tuple[int, int, int, int]] = None
        
        logger.info(f"Tracking face sequence across {len(frames)} frames...")

        for idx, frame in enumerate(frames):
            try:
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                # Detect bounding boxes
                faces = self.extractor.face_cascade.detectMultiScale(
                    gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30)
                )

                if len(faces) == 0:
                    # In case of minor detection drop: use last known crop as fallback
                    if len(tracked_sequence) > 0:
                        tracked_sequence.append(tracked_sequence[-1])
                    continue

                # Parse crops coords to standard format: (xmin, ymin, xmax, ymax)
                formatted_boxes = []
                for (x, y, w, h) in faces:
                    formatted_boxes.append((x, y, x + w, y + h))

                best_box = None
                if last_box is None:
                    # First frame: select the largest face box
                    best_box = max(formatted_boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]))
                else:
                    # Subsequent frames: select the box with highest IoU overlap with last known position
                    best_box = max(formatted_boxes, key=lambda b: self._compute_iou(b, last_box))
                    # Ensure overlap satisfies tracking threshold
                    if self._compute_iou(best_box, last_box) < self.overlap_threshold:
                        # Fallback to the largest box if tracking target breaks
                        best_box = max(formatted_boxes, key=lambda b: (b[2]-b[0])*(b[3]-b[1]))

                last_box = best_box
                
                # Extract face crop
                xmin, ymin, xmax, ymax = best_box
                face_crop = frame[ymin:ymax, xmin:xmax]
                
                # Normalize color space
                face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
                tracked_sequence.append(face_rgb)

            except Exception as e:
                logger.error(f"Error tracking face at frame index {idx}: {e}")
                # Append last known crop if error occurs to maintain sequence length
                if len(tracked_sequence) > 0:
                    tracked_sequence.append(tracked_sequence[-1])

        # Fill up sequence with fallback zero layers if no faces are ever detected
        if len(tracked_sequence) == 0:
            logger.warning("No facial structures found in entire sequence. Returning mock black crops.")
            dummy_crop = np.zeros((224, 224, 3), dtype=np.uint8)
            tracked_sequence = [dummy_crop] * len(frames)

        return tracked_sequence
