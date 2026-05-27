import os
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("multimodal_attention")

class MultimodalAttentionVisualizer:
    """
    Renders multimodal fusion explainability profiles.
    Visualizes cross-modal attention matrices and generates modality reliability timelines
    (Visual vs. Acoustic contribution scores over time).
    """
    def __init__(self, output_dir: str = "outputs/realtime"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_cross_attention(
        self, 
        attention_matrix: np.ndarray, 
        video_timestamps: Optional[List[float]] = None,
        audio_timestamps: Optional[List[float]] = None,
        filename: str = "multimodal_cross_attention.png"
    ) -> str:
        """
        Plots a 2D cross-attention map highlighting the correlation alignment 
        between the video timeline and the audio timeline.
        
        Args:
            attention_matrix: Attention weights, shape (Video_Frames, Audio_Frames)
            video_timestamps: Timestamps associated with video frame steps
            audio_timestamps: Timestamps associated with audio chunk steps
            filename: Output filename to save the diagnostic plot
            
        Returns:
            Absolute file path of the saved diagnostic visualization.
        """
        try:
            fig, ax = plt.subplots(figsize=(8, 6))
            im = ax.imshow(attention_matrix, cmap='plasma', aspect='auto', interpolation='nearest')
            fig.colorbar(im, ax=ax, label="Cross-Attention Weights")
            
            ax.set_title("Multimodal Forensic Cross-Attention Correlation Map", fontsize=12, fontweight='bold')
            ax.set_xlabel("Audio Stream Timeline (Chunks / Frames)")
            ax.set_ylabel("Video Stream Timeline (Video Frames)")

            if video_timestamps is not None and len(video_timestamps) == attention_matrix.shape[0]:
                ax.set_yticks(np.arange(0, len(video_timestamps), max(1, len(video_timestamps) // 8)))
                ax.set_yticklabels([f"{t:.2f}s" for t in np.array(video_timestamps)[::max(1, len(video_timestamps) // 8)]])
                
            if audio_timestamps is not None and len(audio_timestamps) == attention_matrix.shape[1]:
                ax.set_xticks(np.arange(0, len(audio_timestamps), max(1, len(audio_timestamps) // 8)))
                ax.set_xticklabels([f"{t:.2f}s" for t in np.array(audio_timestamps)[::max(1, len(audio_timestamps) // 8)]], rotation=45)

            plt.tight_layout()
            output_path = os.path.join(self.output_dir, filename)
            plt.savefig(output_path, dpi=150)
            plt.close()
            
            logger.info(f"Cross-attention heatmap saved at: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to plot cross-attention: {e}")
            raise e

    def plot_modality_reliability_timeline(
        self, 
        video_weights: np.ndarray, 
        audio_weights: np.ndarray, 
        timestamps: np.ndarray,
        filename: str = "modality_contributions.png"
    ) -> str:
        """
        Plots a stacked or dual line chart showing how the decision contribution 
        fluctuates between the video model and the audio model over the duration of the media.
        
        Args:
            video_weights: 1D array of video modality weight contributions (sum to 1 with audio at each frame)
            audio_weights: 1D array of audio modality weight contributions
            timestamps: 1D array of timestamps corresponding to each decision block
            filename: Output filename to save the diagnostic plot
            
        Returns:
            Absolute file path of the saved timeline visualization.
        """
        try:
            fig, ax = plt.subplots(figsize=(10, 4))
            
            ax.plot(timestamps, video_weights, label='Video Modality Weight (Face Forensics)', color='#e056fd', linewidth=2.5, marker='o', markersize=4)
            ax.plot(timestamps, audio_weights, label='Audio Modality Weight (Voice Clones)', color='#30336b', linewidth=2.5, marker='x', markersize=4)
            
            ax.set_title("Dynamic Modal Influence and Confidence Contribution Tracker", fontsize=12, fontweight='bold')
            ax.set_xlabel("Forensic Timeline (Seconds)")
            ax.set_ylabel("Influence Weight (0.0 to 1.0)")
            ax.set_ylim(-0.05, 1.05)
            ax.grid(True, linestyle='--', alpha=0.5)
            ax.legend(loc='upper right')

            plt.tight_layout()
            output_path = os.path.join(self.output_dir, filename)
            plt.savefig(output_path, dpi=150)
            plt.close()
            
            logger.info(f"Modality contribution timeline saved at: {output_path}")
            return output_path
            
        except Exception as e:
            logger.error(f"Failed to plot modality timeline: {e}")
            raise e
