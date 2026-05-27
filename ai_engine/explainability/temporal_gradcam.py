import cv2
import numpy as np
import torch
import os
from typing import List
from ai_engine.inference.gradcam import GradCAM
from ai_engine.preprocessing.normalization import Normalizer
from ai_engine.utils.logger import setup_logger

logger = setup_logger("temporal_gradcam")

class TemporalGradCAM:
    """
    Renders visual activation maps across sequential frame segments 
    to localize artificial textures temporally.
    """
    def __init__(self, model: torch.nn.Module, target_layer: torch.nn.Module):
        self.gradcam = GradCAM(model=model, target_layer=target_layer)

    def generate_sequence_heatmaps(self, frame_crops: List[np.ndarray]) -> List[np.ndarray]:
        """
        Loops over facial crops, runs Grad-CAM backward checks, and overlays color heatmaps.
        """
        annotated_frames = []
        logger.info(f"Generating Grad-CAM overlays over sequence of {len(frame_crops)} crops...")
        
        for idx, crop in enumerate(frame_crops):
            try:
                # 1. Normalize and pad batch dimension (1, C, H, W)
                tensor = Normalizer.to_normalized_tensor(crop, apply_imagenet=True)
                tensor_batch = tensor.unsqueeze(0)
                
                # Check target device
                device = next(self.gradcam.model.parameters()).device
                tensor_batch = tensor_batch.to(device)
                
                # 2. Generate 2D Heatmap
                heatmap = self.gradcam.generate_heatmap(tensor_batch, target_class=0)
                
                # 3. Blend overlay onto BGR frame
                crop_bgr = cv2.cvtColor(crop, cv2.COLOR_RGB2BGR)
                overlay = self.gradcam.overlay_heatmap(crop_bgr, heatmap, alpha=0.4)
                
                # Convert back to RGB for sequence display
                overlay_rgb = cv2.cvtColor(overlay, cv2.COLOR_BGR2RGB)
                annotated_frames.append(overlay_rgb)
                
            except Exception as e:
                logger.error(f"Failed to generate Grad-CAM overlay for frame {idx}: {e}")
                # Append raw crop if error occurs
                annotated_frames.append(crop)
                
        return annotated_frames
        
    def save_annotated_sequence(self, annotated_frames: List[np.ndarray], output_dir: str, prefix: str = "forensic") -> None:
        """
        Saves the resulting sequence overlay crops locally as individual JPEG assets.
        """
        os.makedirs(output_dir, exist_ok=True)
        for idx, frame in enumerate(annotated_frames):
            path = os.path.join(output_dir, f"{prefix}_heatmap_frame_{idx}.jpg")
            frame_bgr = cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)
            cv2.imwrite(path, frame_bgr)
        logger.info(f"Saved {len(annotated_frames)} Grad-CAM overlay files to: {output_dir}")
