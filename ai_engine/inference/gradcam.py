import cv2
import numpy as np
import torch
import torch.nn as nn
import os
from typing import Tuple

class GradCAM:
    def __init__(self, model: nn.Module, target_layer: nn.Module):
        self.model = model
        self.target_layer = target_layer
        self.gradients = None
        self.activations = None
        
        self.target_layer.register_forward_hook(self._save_activations)
        self.target_layer.register_backward_hook(self._save_gradients)

    def _save_activations(self, module, input, output):
        self.activations = output.detach()

    def _save_gradients(self, module, grad_input, grad_output):
        self.gradients = grad_output[0].detach()

    def generate_heatmap(self, input_tensor: torch.Tensor, target_class: int = 0) -> np.ndarray:
        self.model.zero_grad()
        output = self.model(input_tensor)
        
        score = output[0] if output.dim() == 1 else output[0, target_class]
        score.backward(retain_graph=True)
        
        gradients = self.gradients.cpu().numpy()[0]
        activations = self.activations.cpu().numpy()[0]
        
        weights = np.mean(gradients, axis=(1, 2))
        
        cam = np.zeros(activations.shape[1:], dtype=np.float32)
        for i, w in enumerate(weights):
            cam += w * activations[i]
            
        cam = np.maximum(cam, 0)
        if cam.max() > 0:
            cam = cam / cam.max()
            
        return cam

    @staticmethod
    def overlay_heatmap(img_bgr: np.ndarray, heatmap: np.ndarray, alpha: float = 0.4) -> np.ndarray:
        heatmap_resized = cv2.resize(heatmap, (img_bgr.shape[1], img_bgr.shape[0]))
        heatmap_color = np.uint8(255 * heatmap_resized)
        heatmap_color = cv2.applyColorMap(heatmap_color, cv2.COLORMAP_JET)
        
        overlay = cv2.addWeighted(heatmap_color, alpha, img_bgr, 1.0 - alpha, 0)
        return overlay
