import numpy as np
import librosa
from ai_engine.utils.logger import setup_logger

logger = setup_logger("audio_augmentation")

class AudioAugmentor:
    """
    Applies data augmentations (noise injection, pitch shifting, speed modifications)
    to raw audio waveforms during training.
    """
    @staticmethod
    def inject_noise(y: np.ndarray, noise_level: float = 0.005) -> np.ndarray:
        """
        Adds random white noise of a specific magnitude.
        """
        noise = np.random.randn(len(y))
        return y + noise_level * noise

    @staticmethod
    def shift_pitch(y: np.ndarray, sr: int, n_steps: float = 1.0) -> np.ndarray:
        """
        Shifts vocal pitch without altering duration.
        """
        try:
            return librosa.effects.pitch_shift(y=y, sr=sr, n_steps=n_steps)
        except Exception as e:
            logger.warning(f"Pitch shifting skipped: {e}")
            return y

    @staticmethod
    def modify_speed(y: np.ndarray, rate: float = 1.1) -> np.ndarray:
        """
        Speeds up or slows down the audio duration dynamically.
        """
        try:
            return librosa.effects.time_stretch(y=y, rate=rate)
        except Exception as e:
            logger.warning(f"Time stretching skipped: {e}")
            return y
