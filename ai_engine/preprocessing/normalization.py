import numpy as np
import torch
from typing import Tuple

class Normalizer:
    IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
    IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)

    @classmethod
    def to_normalized_tensor(cls, img_rgb: np.ndarray, apply_imagenet: bool = True) -> torch.Tensor:
        img_float = img_rgb.astype(np.float32) / 255.0

        if apply_imagenet:
            img_float = (img_float - cls.IMAGENET_MEAN) / cls.IMAGENET_STD

        img_transposed = np.transpose(img_float, (2, 0, 1))
        return torch.tensor(img_transposed, dtype=torch.float32)

    @classmethod
    def denormalize_image(cls, img_tensor: torch.Tensor, from_imagenet: bool = True) -> np.ndarray:
        img_arr = img_tensor.cpu().numpy().transpose(1, 2, 0)
        
        if from_imagenet:
            img_arr = (img_arr * cls.IMAGENET_STD) + cls.IMAGENET_MEAN
            
        img_arr = np.clip(img_arr * 255.0, 0, 255).astype(np.uint8)
        return img_arr
