import librosa
import numpy as np
import os
from typing import Tuple, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("audio_loader")

class AudioLoader:
    """
    Ingests raw audio assets (.wav, .mp3, .m4a), managing secure stream loads,
    resampling frequencies, and waveform conversions.
    """
    def __init__(self, target_sr: int = 16000):
        self.target_sr = target_sr
        logger.info(f"AudioLoader configured with target sampling rate: {target_sr} Hz")

    def load_audio(self, file_path: str) -> Optional[Tuple[np.ndarray, int]]:
        """
        Loads audio file, resampling it dynamically to target frequencies.
        """
        if not os.path.exists(file_path):
            logger.error(f"Target audio file missing: {file_path}")
            return None

        try:
            # Load via librosa (highly robust cross-platform decoder)
            y, sr = librosa.load(file_path, sr=self.target_sr)
            logger.info(f"Loaded audio: {file_path} | Length={len(y)} samples | Sample Rate={sr} Hz")
            return y, sr
        except Exception as e:
            logger.error(f"Failed to load audio stream from {file_path}: {e}")
            return None
