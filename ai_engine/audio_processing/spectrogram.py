import librosa
import numpy as np
from ai_engine.utils.logger import setup_logger

logger = setup_logger("spectrogram_extractor")

class SpectrogramExtractor:
    """
    Transforms 1D audio waveforms into standard 2D Mel Spectrogram representations
    and extracts Mel-Frequency Cepstral Coefficients (MFCCs).
    """
    def __init__(self, n_mels: int = 128, n_fft: int = 2048, hop_length: int = 512):
        self.n_mels = n_mels
        self.n_fft = n_fft
        self.hop_length = hop_length
        logger.info(f"SpectrogramExtractor initialized: Mel bins={n_mels}, FFT Window={n_fft}")

    def compute_mel_spectrogram(self, y: np.ndarray, sr: int) -> np.ndarray:
        """
        Generates 2D Mel Spectrogram and scales magnitude log-linearly.
        Shape: (n_mels, Time_Frames)
        """
        # 1. Compute Short-Time Fourier Transform power spectrum mapped to Mel coordinates
        s = librosa.feature.melspectrogram(
            y=y, sr=sr, n_fft=self.n_fft, hop_length=self.hop_length, n_mels=self.n_mels
        )
        
        # 2. Scale power matrix log-linearly (decibel units)
        s_db = librosa.power_to_db(s, ref=np.max)
        return s_db

    def compute_mfcc(self, y: np.ndarray, sr: int, n_mfcc: int = 20) -> np.ndarray:
        """
        Extracts Mel-Frequency Cepstral Coefficients (MFCCs) representing vocal tract envelopes.
        """
        return librosa.feature.mfcc(y=y, sr=sr, n_mfcc=n_mfcc)
