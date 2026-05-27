import os
import numpy as np
import matplotlib.pyplot as plt
import cv2
from typing import Optional, Union, Tuple
from ai_engine.utils.logger import setup_logger

logger = setup_logger("audio_heatmaps")

class AudioSpectrogramHeatmap:
    """
    Renders acoustic feature visual overlays.
    Generates beautiful 2D Mel Spectrograms and maps 1D temporal anomaly scores 
    (from Wav2Vec or sequence models) onto the spectrogram as a forensic explainability heatmap.
    """
    def __init__(self, output_dir: str = "outputs/audio"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def generate_spectrogram_heatmap(
        self, 
        spectrogram: np.ndarray, 
        anomaly_scores: Optional[np.ndarray] = None, 
        sr: int = 16000, 
        hop_length: int = 512,
        filename: str = "acoustic_heatmap.png"
    ) -> str:
        """
        Plots a Mel Spectrogram and overlays temporal deepfake/anomaly highlights.
        
        Args:
            spectrogram: 2D array of the spectrogram (db scale preferred), shape: (Frequencies, Time)
            anomaly_scores: Optional 1D array of deepfake anomaly scores over time, shape: (Time,) or (Sequence_Length,)
            sr: Sampling rate of the audio track
            hop_length: Hop length of the spectrogram representation
            filename: Output filename to save the resulting image
            
        Returns:
            Absolute file path of the saved diagnostic PNG file.
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 4))
            
            # 1. Plot the base spectrogram
            im = ax.imshow(spectrogram, aspect='auto', origin='lower', cmap='magma')
            ax.set_title("Acoustic Forensics: Spectrogram & Deepfake Anomaly Map", fontsize=12, fontweight='bold')
            ax.set_xlabel("Time Bins")
            ax.set_ylabel("Mel Frequency Bins")
            fig.colorbar(im, ax=ax, label="Decibels (dB)")

            # 2. Overlay 1D temporal anomaly score as vertical highlight bands
            if anomaly_scores is not None:
                # Normalize anomaly scores between 0 and 1
                scores_min = anomaly_scores.min()
                scores_max = anomaly_scores.max()
                if (scores_max - scores_min) > 1e-6:
                    norm_scores = (anomaly_scores - scores_min) / (scores_max - scores_min)
                else:
                    norm_scores = anomaly_scores
                
                # Interpolate 1D score to match spectrogram time bins length
                time_bins = spectrogram.shape[1]
                interpolated_scores = np.interp(
                    np.linspace(0, len(norm_scores) - 1, time_bins),
                    np.arange(len(norm_scores)),
                    norm_scores
                )
                
                # Draw vertical transparent overlays based on deepfake probability
                for i in range(time_bins):
                    score = interpolated_scores[i]
                    if score > 0.4:  # Threshold for highlighting potential cloning artifacts
                        # Alpha represents anomaly intensity
                        alpha_val = float(score * 0.35)
                        ax.axvspan(i, i+1, color='cyan', alpha=alpha_val)

            plt.tight_layout()
            output_path = os.path.join(self.output_dir, filename)
            plt.savefig(output_path, dpi=150)
            plt.close()
            
            logger.info(f"Successfully generated and saved acoustic heatmap: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to generate acoustic heatmap visualizer: {e}")
            raise e

    def overlay_gradcam_on_spectrogram(
        self, 
        spectrogram: np.ndarray, 
        gradcam_heatmap: np.ndarray, 
        alpha: float = 0.5
    ) -> np.ndarray:
        """
        Blends a 2D Grad-CAM heatmap directly over a 2D spectrogram.
        Useful for spectrogram-based CNN deepfake models.
        
        Args:
            spectrogram: Original single-channel spectrogram (F x T) normalized to 0-255 or as float.
            gradcam_heatmap: 2D Grad-CAM importance map (F x T) in range [0, 1].
            alpha: Blending weight for the heatmap color overlay.
            
        Returns:
            A blended BGR image as a numpy array.
        """
        # Convert spectrogram to 8-bit BGR image for blending
        spec_norm = spectrogram - spectrogram.min()
        if spec_norm.max() > 0:
            spec_norm = (spec_norm / spec_norm.max()) * 255.0
        spec_8bit = np.uint8(spec_norm)
        spec_bgr = cv2.cvtColor(spec_8bit, cv2.COLOR_GRAY2BGR)
        
        # Apply JET colormap to 2D Grad-CAM heatmap
        heatmap_resized = cv2.resize(gradcam_heatmap, (spectrogram.shape[1], spectrogram.shape[0]))
        heatmap_color = np.uint8(255 * heatmap_resized)
        heatmap_color = cv2.applyColorMap(heatmap_color, cv2.COLORMAP_JET)
        
        # Blend the heatmap and spectrogram BGR image
        blended = cv2.addWeighted(heatmap_color, alpha, spec_bgr, 1.0 - alpha, 0)
        return blended
