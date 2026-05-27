import unittest
import os
import sys
import numpy as np
import torch

# Ensure workspace path imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.audio_processing.spectrogram import SpectrogramExtractor
from ai_engine.audio_processing.voice_preprocessing import VoicePreprocessor
from ai_engine.audio_models.cnn_audio_model import SpectrogramCNNClassifier

class TestAudioModels(unittest.TestCase):
    """
    Validates Mel Spectrogram feature extraction pipelines and audio classification architectures.
    """
    def setUp(self):
        # Generate synthetic 1-second audio signal at 16000Hz sampling rate
        self.sr = 16000
        self.duration = 1.0
        self.synthetic_signal = np.sin(2 * np.pi * 440 * np.arange(self.sr * self.duration) / self.sr).astype(np.float32)

    def test_spectrogram_extraction(self):
        """
        SpectrogramExtractor should output correct 2D feature maps from raw signal.
        """
        # Apply pre-emphasis and volume normalization first
        processed_signal = VoicePreprocessor.apply_preemphasis(self.synthetic_signal)
        processed_signal = VoicePreprocessor.normalize_volume(processed_signal)
        
        # Extract 2D Mel Spectrogram
        extractor = SpectrogramExtractor(n_mels=64)
        spec = extractor.compute_mel_spectrogram(processed_signal, sr=self.sr)
        
        # Verify 2D shape (Channels/Mels x Time bins)
        self.assertEqual(spec.ndim, 2)
        self.assertEqual(spec.shape[0], 64)
        self.assertTrue(spec.shape[1] > 0)

    def test_cnn_audio_classifier(self):
        """
        SpectrogramCNNClassifier should complete forward execution over 2D Mel spectrograms.
        """
        # Instantiate spectrogram CNN
        model = SpectrogramCNNClassifier(num_classes=1)
        model.eval()
        
        # Create synthetic spectrogram batch: (Batch, Channels, Height/Mels, Width/Time)
        # Standard input dims: (Batch=2, Channel=1, Mels=128, Time=128)
        dummy_spec_batch = torch.randn(2, 1, 128, 128)
        
        with torch.no_grad():
            outputs = model(dummy_spec_batch)
            
        # Verify binary logit outputs shape: (2, 1)
        self.assertEqual(outputs.shape, (2, 1))

if __name__ == "__main__":
    unittest.main()
