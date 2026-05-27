import numpy as np
import matplotlib.pyplot as plt
import os
from typing import List, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("attention_visualizer")

class AttentionVisualizer:
    """
    Extracts and visualizes self-attention weights inside Transformer 
    sequence models to highlight temporal prediction correlations.
    """
    def __init__(self, output_dir: str = "outputs"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def plot_attention_weights(self, attention_matrix: np.ndarray, frame_labels: Optional[List[str]] = None, filename: str = "attention_map.png") -> str:
        """
        Plots 2D self-attention heatmaps representing correlations between sequence frames.
        Shape of attention_matrix should be: (Sequence_Length, Sequence_Length)
        """
        fig, ax = plt.subplots(figsize=(8, 8))
        
        im = ax.imshow(attention_matrix, cmap='viridis', interpolation='nearest')
        fig.colorbar(im, ax=ax, label="Attention Magnitude")
        
        ax.set_title("Temporal Self-Attention Correlation Map")
        ax.set_xlabel("Query Key Frames")
        ax.set_ylabel("Source Value Frames")
        
        if frame_labels is not None:
            ax.set_xticks(np.arange(len(frame_labels)))
            ax.set_yticks(np.arange(len(frame_labels)))
            ax.set_xticklabels(frame_labels, rotation=45, ha="right")
            ax.set_yticklabels(frame_labels)
            
        plt.tight_layout()
        
        output_filepath = os.path.join(self.output_dir, filename)
        plt.savefig(output_filepath, dpi=150)
        plt.close()
        
        logger.info(f"Self-attention weight map saved at: {output_filepath}")
        return output_filepath
