import numpy as np
from ai_engine.utils.logger import setup_logger

logger = setup_logger("voice_preprocessing")

class VoicePreprocessor:
    """
    Applies standard digital signal processing (DSP) filters to voice signals
    to highlight frequency-range variations and normalize volume.
    """
    @staticmethod
    def apply_preemphasis(y: np.ndarray, coeff: float = 0.97) -> np.ndarray:
        """
        Applies a pre-emphasis filter to boost high-frequency features (vocal friction)
        which are typically attenuated or synthetic-sounding in cloned audio.
        Formula: y_filtered[t] = y[t] - coeff * y[t-1]
        """
        return np.append(y[0], y[1:] - coeff * y[:-1])

    @staticmethod
    def normalize_volume(y: np.ndarray) -> np.ndarray:
        """
        Applies root-mean-square peak normalization to prevent volume imbalances.
        """
        max_val = np.max(np.abs(y))
        if max_val > 0:
            return y / max_val
        return y
