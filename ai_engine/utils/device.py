import torch
from ai_engine.utils.logger import setup_logger

logger = setup_logger("device_config")

def get_device() -> torch.device:
    if torch.cuda.is_available():
        device_name = torch.cuda.get_device_name(0)
        logger.info(f"NVIDIA GPU Acceleration Active: Using device [cuda:0] ({device_name})")
        return torch.device("cuda")
    
    logger.info("NVIDIA CUDA not found. Operating on standard sequential CPU hardware.")
    return torch.device("cpu")
