import numpy as np
from ai_engine.utils.logger import setup_logger

logger = setup_logger("waveform_processor")

class WaveformProcessor:
    """
    Standardizes 1D audio waveform sizes, applying zero-padding or central cropping
    to compile uniform sample timelines.
    """
    def __init__(self, target_duration: float = 4.0, sr: int = 16000):
        self.target_duration = target_duration
        self.sr = sr
        self.target_length = int(target_duration * sr)
        logger.info(f"WaveformProcessor initialized: Length={self.target_length} samples ({target_duration}s)")

    def process_waveform(self, y: np.ndarray) -> np.ndarray:
        """
        Pads or crops 1D array to achieve target length parameter.
        """
        current_len = len(y)
        
        if current_len == self.target_length:
            return y
            
        elif current_len < self.target_length:
            # 1. Pad with zeros (silence)
            pad_needed = self.target_length - current_len
            y_padded = np.pad(y, (0, pad_needed), mode='constant')
            return y_padded
            
        else:
            # 2. Central crop sequence segment
            start = (current_len - self.target_length) // 2
            return y[start:start + self.target_length]
