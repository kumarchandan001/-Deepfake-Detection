import torch
import torch.nn as nn
from ai_engine.utils.logger import setup_logger

logger = setup_logger("fp16_optimizer")

class FP16Optimizer:
    """
    Optimizes PyTorch networks for low-latency half-precision (FP16) inference.
    Handles converting models safely by keeping sensitive layers (e.g. BatchNorms) 
    in FP32 to avoid numerical instability or overflow.
    """
    @staticmethod
    def convert_to_fp16(model: nn.Module) -> nn.Module:
        """
        Safely converts a PyTorch model to half precision (FP16).
        
        Args:
            model: Standard FP32 model instance.
            
        Returns:
            Optimized FP16 model instance.
        """
        logger.info("Initiating safe FP16 quantization...")
        
        device = next(model.parameters()).device
        if "cpu" in str(device):
            logger.warning("FP16 calculations are highly inefficient on typical CPUs. Please run on GPU/CUDA.")

        # 1. Base conversion to half precision
        model = model.half()

        # 2. Revert critical normalization layers back to FP32 for numerical stability
        count_reverted = 0
        for name, module in model.named_modules():
            if isinstance(module, (nn.BatchNorm1d, nn.BatchNorm2d, nn.BatchNorm3d, nn.GroupNorm, nn.LayerNorm)):
                module.float()
                count_reverted += 1
                
        logger.info(f"FP16 quantization complete. Reverted {count_reverted} normalization layers to FP32 to ensure numerical stability.")
        return model

    @staticmethod
    def run_with_mixed_precision(model: nn.Module, inputs: torch.Tensor) -> torch.Tensor:
        """
        Executes inference wrapped inside PyTorch Automatic Mixed Precision (AMP).
        Optimizes memory and execution bandwidth automatically.
        """
        device = next(model.parameters()).device
        device_type = "cuda" if "cuda" in str(device) else "cpu"
        
        # Cast inputs appropriately to device
        inputs = inputs.to(device)
        
        with torch.amp.autocast(device_type=device_type, dtype=torch.float16):
            outputs = model(inputs)
            
        return outputs
