import os
import numpy as np
import torch
from torch.utils.data import Dataset
from typing import List, Tuple, Optional
from ai_engine.preprocessing.image_processor import ImageProcessor
from ai_engine.preprocessing.normalization import Normalizer
from ai_engine.utils.logger import setup_logger

logger = setup_logger("dataset_loader")

class DeepfakeImageDataset(Dataset):
    def __init__(self, split_dir: str, target_size: Tuple[int, int] = (224, 224), transform=None, extract_faces: bool = True):
        self.split_dir = split_dir
        self.transform = transform
        self.processor = ImageProcessor(target_size=target_size, extract_faces=extract_faces)
        self.samples: List[Tuple[str, int]] = []
        self.classes = ["real", "fake"]
        
        self._scan_dataset()

    def _scan_dataset(self) -> None:
        if not os.path.exists(self.split_dir):
            logger.error(f"Target split directory does not exist: {self.split_dir}")
            raise FileNotFoundError(f"Directory not found: {self.split_dir}")

        for class_idx, class_name in enumerate(self.classes):
            class_folder = os.path.join(self.split_dir, class_name)
            if not os.path.isdir(class_folder):
                logger.warning(f"Class subdirectory missing from dataset split: {class_folder}")
                continue
                
            for root, _, files in os.walk(class_folder):
                for filename in files:
                    if filename.lower().endswith((".png", ".jpg", ".jpeg", ".webp")):
                        full_path = os.path.join(root, filename)
                        self.samples.append((full_path, class_idx))

        logger.info(f"Loaded split '{os.path.basename(self.split_dir)}' containing {len(self.samples)} valid samples.")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        img_path, label = self.samples[idx]
        img_arr = self.processor.load_and_preprocess(img_path)
        
        if img_arr is None:
            logger.warning(f"Failed to load image at: {img_path}. Falling back to next sample.")
            return self.__getitem__((idx + 1) % len(self.samples))

        if self.transform is not None:
            pil_img = self.processor.ndarray_to_pillow(img_arr)
            pil_img = self.transform(pil_img)
            img_arr = np.array(pil_img)

        img_tensor = Normalizer.to_normalized_tensor(img_arr, apply_imagenet=True)
        label_tensor = torch.tensor(label, dtype=torch.float32)

        return img_tensor, label_tensor
