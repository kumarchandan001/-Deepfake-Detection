import cv2
import numpy as np
import torch
import torch.nn as nn
from typing import Tuple, Optional
from ai_engine.inference.gradcam import GradCAM
from ai_engine.preprocessing.normalization import Normalizer
from ai_engine.utils.logger import setup_logger

logger = setup_logger("realtime_gradcam")

class RealtimeGradCAM:
    """
    Extremely fast, realtime Grad-CAM overlay generator optimized for webcam streams.
    Ensures safe execution under torch.no_grad() inference via internal gradient enabling.
    """
    def __init__(self, model: nn.Module, target_layer: nn.Module, alpha: float = 0.45):
        self.model = model
        self.target_layer = target_layer
        self.alpha = alpha
        self.gradcam = GradCAM(model=self.model, target_layer=self.target_layer)

    def process_frame(self, frame: np.ndarray, face_box: Optional[Tuple[int, int, int, int]] = None) -> np.ndarray:
        """
        Generates a Grad-CAM heatmap overlaid on either the entire frame or the detected face bounding box.
        
        Args:
            frame: Raw BGR input frame from webcam (shape: H x W x C).
            face_box: Optional bounding box as (x, y, w, h). If provided, computes Grad-CAM on the crop 
                      and overlays it back onto the same region.
        
        Returns:
            BGR frame containing the blended Grad-CAM color map overlay.
        """
        try:
            h, w, c = frame.shape
            
            # 1. Determine region of interest
            if face_box is not None:
                x, y, fw, fh = face_box
                # Clamp coordinates to frame boundaries
                x = max(0, min(x, w - 1))
                y = max(0, min(y, h - 1))
                fw = max(1, min(fw, w - x))
                fh = max(1, min(fh, h - y))
                roi = frame[y:y+fh, x:x+fw]
            else:
                roi = frame
                x, y, fw, fh = 0, 0, w, h
            
            if roi.size == 0:
                return frame
            
            # 2. Resize and convert to expected RGB format for normalization
            roi_rgb = cv2.cvtColor(roi, cv2.COLOR_BGR2RGB)
            
            # We resize the crop to 224x224 (default image model shape)
            roi_resized = cv2.resize(roi_rgb, (224, 224))
            
            # 3. Normalize and prepare input tensor
            tensor = Normalizer.to_normalized_tensor(roi_resized, apply_imagenet=True)
            tensor_batch = tensor.unsqueeze(0)
            
            device = next(self.model.parameters()).device
            tensor_batch = tensor_batch.to(device)
            
            # 4. Generate Heatmap (Temporarily enable grads since inference has it disabled)
            with torch.enable_grad():
                heatmap = self.gradcam.generate_heatmap(tensor_batch, target_class=0)
            
            # 5. Blend overlay back into the original BGR frame
            roi_bgr = cv2.cvtColor(roi_rgb, cv2.COLOR_RGB2BGR)
            overlay_roi = self.gradcam.overlay_heatmap(roi_bgr, heatmap, alpha=self.alpha)
            
            # 6. Resize blended crop back to original ROI size and stitch it back
            overlay_roi_resized = cv2.resize(overlay_roi, (fw, fh))
            
            output_frame = frame.copy()
            output_frame[y:y+fh, x:x+fw] = overlay_roi_resized
            return output_frame
            
        except Exception as e:
            logger.debug(f"Failed to generate realtime Grad-CAM overlay: {e}")
            return frame
