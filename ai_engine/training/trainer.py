import os
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torch.cuda.amp import autocast, GradScaler
from tqdm import tqdm
from typing import Dict, Any
from ai_engine.training.validate import evaluate_model
from ai_engine.training.losses import get_loss_criterion
from ai_engine.training.callbacks import EarlyStoppingCallback
from ai_engine.utils.logger import setup_logger

logger = setup_logger("trainer")

class DeepfakeTrainer:
    def __init__(self, model: nn.Module, train_loader: DataLoader, val_loader: DataLoader, config, device: torch.device):
        self.model = model.to(device)
        self.train_loader = train_loader
        self.val_loader = val_loader
        self.config = config
        self.device = device
        
        self.epochs = config.get("training.epochs", 10)
        self.lr = config.get("training.learning_rate", 0.0001)
        self.mixed_precision = config.get("training.mixed_precision", True)
        self.patience = config.get("training.patience", 5)
        self.accumulation_steps = config.get("training.accumulation_steps", 1)
        
        # 1. Load loss function from factory
        loss_type = config.get("training.loss_type", "bce")
        self.criterion = get_loss_criterion(loss_type=loss_type)
        
        # 2. Setup optimizer
        opt_name = config.get("training.optimizer", "adam").lower()
        if opt_name == "sgd":
            self.optimizer = optim.SGD(self.model.parameters(), lr=self.lr, momentum=0.9, weight_decay=1e-4)
        else:
            self.optimizer = optim.Adam(self.model.parameters(), lr=self.lr, weight_decay=1e-5)
            
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(self.optimizer, mode='min', factor=0.5, patience=2)
        self.scaler = GradScaler(enabled=self.mixed_precision)
        
        # 3. Setup callbacks
        checkpoint_dir = config.get("model.checkpoint_dir", "ai_engine/checkpoints")
        self.early_stopping = EarlyStoppingCallback(
            patience=self.patience, 
            checkpoint_dir=checkpoint_dir,
            filename="best_model.pth"
        )

    def train(self) -> Dict[str, Any]:
        logger.info(f"Initiating training session: Total Epochs={self.epochs}, Device={self.device}")
        
        history = {
            "train_loss": [], "val_loss": [], 
            "val_acc": [], "val_f1": [], "val_auc": []
        }
        
        for epoch in range(self.epochs):
            self.model.train()
            running_loss = 0.0
            pbar = tqdm(enumerate(self.train_loader), total=len(self.train_loader), desc=f"Epoch {epoch+1}/{self.epochs}")
            
            self.optimizer.zero_grad()
            
            for step, (images, labels) in pbar:
                images = images.to(self.device)
                labels = labels.to(self.device).unsqueeze(1)
                
                with autocast(enabled=self.mixed_precision):
                    outputs = self.model(images)
                    loss = self.criterion(outputs, labels)
                    loss = loss / self.accumulation_steps
                
                self.scaler.scale(loss).backward()
                
                # Gradient clipping to prevent exploding gradient anomalies (highly critical for deep models)
                if (step + 1) % self.accumulation_steps == 0 or (step + 1) == len(self.train_loader):
                    self.scaler.unscale_(self.optimizer)
                    nn.utils.clip_grad_norm_(self.model.parameters(), max_norm=1.0)
                    
                    self.scaler.step(self.optimizer)
                    self.scaler.update()
                    self.optimizer.zero_grad()
                
                running_loss += loss.item() * self.accumulation_steps * images.size(0)
                pbar.set_postfix({"batch_loss": f"{loss.item() * self.accumulation_steps:.4f}"})
                
            epoch_train_loss = running_loss / len(self.train_loader.dataset)
            epoch_val_loss, val_metrics = evaluate_model(
                self.model, self.val_loader, self.criterion, self.device
            )
            
            self.scheduler.step(epoch_val_loss)
            
            logger.info(
                f"Epoch {epoch+1} Complete - "
                f"Train Loss: {epoch_train_loss:.4f} | Val Loss: {epoch_val_loss:.4f} | "
                f"Accuracy: {val_metrics['accuracy']*100:.2f}% | F1: {val_metrics['f1']*100:.2f}%"
            )
            
            history["train_loss"].append(epoch_train_loss)
            history["val_loss"].append(epoch_val_loss)
            history["val_acc"].append(val_metrics["accuracy"])
            history["val_f1"].append(val_metrics["f1"])
            history["val_auc"].append(val_metrics["auc"])
            
            # Check callback stopping states
            self.early_stopping.check(epoch_val_loss, self.model, epoch, self.optimizer)
            if self.early_stopping.early_stop:
                logger.warning("Early Stopping triggered. Exiting trainer loops.")
                break
                
        return history
