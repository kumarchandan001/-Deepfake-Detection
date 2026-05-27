import numpy as np
from typing import List
from ai_engine.video_processing.video_loader import VideoLoader
from ai_engine.utils.logger import setup_logger

logger = setup_logger("frame_sampler")

class FrameSampler:
    """
    Computes sequence indices maps designed to feed fixed length sequence model networks.
    """
    def __init__(self, sequence_length: int = 16):
        self.sequence_length = sequence_length
        logger.info(f"FrameSampler configured with sequence length: {sequence_length}")

    def get_uniform_indices(self, total_frames: int) -> List[int]:
        """
        Calculates evenly spaced indices covering the entire video length.
        """
        if total_frames <= 0:
            logger.error("Cannot sample indices from total frames <= 0.")
            return []

        # If total frames is smaller than target sequence length, repeat the final frame
        if total_frames < self.sequence_length:
            logger.debug(f"Total frames {total_frames} is smaller than target sequence length {self.sequence_length}. Applying zero-padding index mapping.")
            indices = list(range(total_frames))
            indices += [total_frames - 1] * (self.sequence_length - total_frames)
            return indices

        # Compute evenly split splits
        indices = np.linspace(0, total_frames - 1, self.sequence_length, dtype=int)
        return list(indices)

    def get_stride_indices(self, total_frames: int, stride: int = 2, start_offset: int = 0) -> List[int]:
        """
        Samples frame indices sequentially separated by a specific stride index distance.
        """
        indices = []
        current = start_offset
        
        while len(indices) < self.sequence_length and current < total_frames:
            indices.append(current)
            current += stride
            
        # Fallback padding if stride reaches boundary prematurely
        if len(indices) < self.sequence_length:
            padding_val = indices[-1] if indices else 0
            indices += [padding_val] * (self.sequence_length - len(indices))
            
        return indices
