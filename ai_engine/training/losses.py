import torch
import torch.nn as nn
from ai_engine.utils.logger import setup_logger

logger = setup_logger("loss_factory")

class WeightedBCELoss(nn.Module):
    """
    Weighted Binary Cross Entropy Loss to handle class imbalance.
    """
    def __init__(self, pos_weight: float = 1.0):
        super(WeightedBCELoss, self).__init__()
        self.pos_weight = pos_weight

    def forward(self, outputs: torch.Tensor, targets: torch.Tensor) -> torch.Tensor:
        # Scale losses on positive classes (FAKE) if imbalanced
        epsilon = 1e-7
        loss = - (self.pos_weight * targets * torch.log(outputs + epsilon) + (1.0 - targets) * torch.log(1.0 - outputs + epsilon))
        return torch.mean(loss)

def get_loss_criterion(loss_type: str = "bce", pos_weight: float = 1.0) -> nn.Module:
    """
    Decoupled loss helper returning target loss calculations modules.
    """
    logger.info(f"Loss factory returning: {loss_type}")
    
    name = loss_type.lower().strip()
    if name == "weighted_bce":
        return WeightedBCELoss(pos_weight=pos_weight)
        
    # Default standard Binary Cross Entropy Loss
    return nn.BCELoss()
