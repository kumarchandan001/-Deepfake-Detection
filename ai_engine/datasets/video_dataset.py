import os
import torch
from torch.utils.data import Dataset
import numpy as np
import cv2
from typing import List, Tuple, Optional
from ai_engine.video_processing.video_loader import VideoLoader
from ai_engine.video_processing.frame_extractor import FrameExtractor
from ai_engine.video_processing.frame_sampler import FrameSampler
from ai_engine.video_processing.face_tracker import FaceTracker
from ai_engine.preprocessing.normalization import Normalizer
from ai_engine.utils.logger import setup_logger

logger = setup_logger("video_dataset_loader")

class DeepfakeVideoDataset(Dataset):
    """
    Ingests video datasets recursively, tracks primary facial elements over timeline,
    and returns aligned sequences tensors: (Sequence_Length, C, H, W).
    """
    def __init__(self, split_dir: str, sequence_length: int = 16, target_size: Tuple[int, int] = (224, 224)):
        self.split_dir = split_dir
        self.sequence_length = sequence_length
        self.target_size = target_size
        
        self.sampler = FrameSampler(sequence_length=sequence_length)
        self.tracker = FaceTracker()
        
        self.samples: List[Tuple[str, int]] = []
        self.classes = ["real", "fake"] # real = 0, fake = 1
        
        self._scan_dataset()

    def _scan_dataset(self) -> None:
        if not os.path.exists(self.split_dir):
            logger.error(f"Target split directory does not exist: {self.split_dir}")
            raise FileNotFoundError(f"Directory not found: {self.split_dir}")

        for class_idx, class_name in enumerate(self.classes):
            class_folder = os.path.join(self.split_dir, class_name)
            if not os.path.isdir(class_folder):
                continue
                
            for root, _, files in os.walk(class_folder):
                for filename in files:
                    if filename.lower().endswith((".mp4", ".avi", ".mov", ".mkv")):
                        full_path = os.path.join(root, filename)
                        self.samples.append((full_path, class_idx))

        logger.info(f"Loaded split '{os.path.basename(self.split_dir)}' containing {len(self.samples)} valid videos.")

    def __len__(self) -> int:
        return len(self.samples)

    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, torch.Tensor]:
        video_path, label = self.samples[idx]
        
        try:
            # 1. Load video and parse metadata
            loader = VideoLoader(video_path)
            total_frames = loader.metadata.get("frame_count", 0)
            
            # 2. Compute target uniform indices
            indices = self.sampler.get_uniform_indices(total_frames)
            
            # 3. Seek and extract raw frames
            extractor = FrameExtractor(loader)
            raw_frames = extractor.extract_multiple_frames(indices)
            loader.close() # Release descriptors immediately to prevent leakage
            
            # 4. Extract facial boundaries tracking
            face_crops = self.tracker.track_face_sequence(raw_frames)
            
            # 5. Preprocess, resize, and normalize each crop
            tensor_list = []
            for crop in face_crops:
                resized = cv2.resize(crop, self.target_size, interpolation=cv2.INTER_LINEAR)
                tensor = Normalizer.to_normalized_tensor(resized, apply_imagenet=True)
                tensor_list.append(tensor)
                
            # 6. Stack into sequence tensor shape: (Sequence_Length, C, Height, Width)
            sequence_tensor = torch.stack(tensor_list, dim=0)
            label_tensor = torch.tensor(label, dtype=torch.float32)
            
            return sequence_tensor, label_tensor
            
        except Exception as e:
            logger.warning(f"Failed to process video sequence: {video_path}. Error: {e}. Swapping with next sample.")
            return self.__getitem__((idx + 1) % len(self.samples))
