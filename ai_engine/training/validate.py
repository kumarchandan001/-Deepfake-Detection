import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import numpy as np
from tqdm import tqdm
from typing import Dict, Tuple
from ai_engine.training.metrics import MetricsCalculator

def evaluate_model(model: nn.Module, dataloader: DataLoader, criterion: nn.Module, device: torch.device) -> Tuple[float, Dict[str, float]]:
    model.eval()
    val_loss = 0.0
    
    all_targets = []
    all_predictions = []

    with torch.no_grad():
        for images, labels in tqdm(dataloader, desc="Validation Iteration"):
            images = images.to(device)
            labels = labels.to(device).unsqueeze(1)

            outputs = model(images)
            loss = criterion(outputs, labels)

            val_loss += loss.item() * images.size(0)
            
            all_targets.extend(labels.cpu().numpy())
            all_predictions.extend(outputs.cpu().numpy())

    total_loss = val_loss / len(dataloader.dataset)
    
    y_true = np.array(all_targets).flatten()
    y_pred_prob = np.array(all_predictions).flatten()

    metrics = MetricsCalculator.compute_all(y_true, y_pred_prob)
    
    return total_loss, metrics
