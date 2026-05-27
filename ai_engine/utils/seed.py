import random
import numpy as np
import torch
from ai_engine.utils.logger import setup_logger

logger = setup_logger("seed_config")

def set_seed(seed: int = 42) -> None:
    """
    Sets reproducible random seeds across Python, NumPy, PyTorch CPU, and PyTorch CUDA.
    Also standardizes PyTorch cuDNN determinism flags for research accuracy.
    """
    logger.info(f"Setting global execution seed to: {seed}")
    
    # 1. Standard Python library random seed
    random.seed(seed)
    
    # 2. NumPy array operations seed
    np.random.seed(seed)
    
    # 3. PyTorch device operations seed
    torch.manual_seed(seed)
    
    # 4. PyTorch GPU allocation seeds
    if torch.cuda.is_available():
        torch.cuda.manual_seed(seed)
        torch.cuda.manual_seed_all(seed) # for multi-GPU setups
        
    # 5. cuDNN determinism parameters (ensures reproducibility on convolutional backprop loops)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False
    
    logger.info("Deterministic seeding hooks active.")
