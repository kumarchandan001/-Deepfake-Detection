import os
import torch
import numpy as np
from typing import Dict, Any
from ai_engine.utils.logger import setup_logger

logger = setup_logger("callbacks")

class EarlyStoppingCallback:
    """
    Halts training execution early if validation loss fails to decrease.
    """
    def __init__(self, patience: int = 5, min_delta: float = 0.0, checkpoint_dir: str = "ai_engine/checkpoints", filename: str = "best_model.pth"):
        self.patience = patience
        self.min_delta = min_delta
        self.checkpoint_dir = checkpoint_dir
        self.filename = filename
        self.counter = 0
        self.best_loss = np.inf
        self.early_stop = False
        
        os.makedirs(self.checkpoint_dir, exist_ok=True)

    def check(self, val_loss: float, model: torch.nn.Module, epoch: int, optimizer: torch.optim.Optimizer) -> None:
        """
        Runs check validation logic, serializing optimal weights dynamically.
        """
        if val_loss < self.best_loss - self.min_delta:
            logger.info(f"Validation loss decreased ({self.best_loss:.6f} --> {val_loss:.6f}). Saving model weights...")
            self.best_loss = val_loss
            self.counter = 0
            self._save_checkpoint(model, optimizer, epoch, val_loss)
        else:
            self.counter += 1
            logger.info(f"EarlyStopping check: {self.counter}/{self.patience} validation iterations with no reduction.")
            if self.counter >= self.patience:
                self.early_stop = True
                logger.warning(f"Early stopping triggered at epoch {epoch+1}.")

    def _save_checkpoint(self, model: torch.nn.Module, optimizer: torch.optim.Optimizer, epoch: int, val_loss: float) -> None:
        checkpoint_path = os.path.join(self.checkpoint_dir, self.filename)
        torch.save({
            'epoch': epoch,
            'model_state_dict': model.state_dict(),
            'optimizer_state_dict': optimizer.state_dict(),
            'best_val_loss': val_loss,
        }, checkpoint_path)
