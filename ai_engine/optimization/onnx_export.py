import os
import torch
import torch.nn as nn
from typing import Tuple, Dict, Any, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("onnx_export")

class ONNXExporter:
    """
    Automates compiling PyTorch neural network graphs into high-speed, 
    cross-platform ONNX runtime binary formats.
    """
    def __init__(self, output_dir: str = "weights/onnx"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def export(
        self, 
        model: nn.Module, 
        input_shape: Tuple[int, ...], 
        filename: str,
        dynamic_axes: Optional[Dict[str, Dict[int, str]]] = None,
        opset_version: int = 14,
        device: str = "cpu"
    ) -> str:
        """
        Exports a PyTorch model to ONNX format.
        
        Args:
            model: PyTorch model instance
            input_shape: Input tensor shape (e.g., (1, 3, 224, 224) for images)
            filename: Output filename (e.g. 'efficientnet_b4.onnx')
            dynamic_axes: Dictionary defining dynamic dimensions (e.g., batch sizing)
            opset_version: Target ONNX operator set version
            device: Run export on 'cpu' or 'cuda'
            
        Returns:
            Absolute filepath to the exported ONNX model binary.
        """
        output_path = os.path.join(self.output_dir, filename)
        logger.info(f"Initiating ONNX export for model to path: {output_path}")

        try:
            # 1. Prepare model
            model = model.to(device)
            model.eval()

            # 2. Prepare dummy input tensor matching dynamic specs
            dummy_input = torch.randn(*input_shape, device=device)

            # 3. Standard default dynamic axes if none provided (optimizes for batch-size variability)
            if dynamic_axes is None:
                dynamic_axes = {
                    "input": {0: "batch_size"},
                    "output": {0: "batch_size"}
                }

            # 4. Perform PyTorch JIT tracer export
            torch.onnx.export(
                model,
                dummy_input,
                output_path,
                export_params=True,
                opset_version=opset_version,
                do_constant_folding=True,
                input_names=["input"],
                output_names=["output"],
                dynamic_axes=dynamic_axes
            )

            # 5. Run ONNX integrity checks
            import onnx
            onnx_model = onnx.load(output_path)
            onnx.checker.check_model(onnx_model)
            logger.info("ONNX validation check passed successfully.")

            return output_path

        except ImportError:
            logger.warning("ONNX python library not installed. Skipping integrity verification checks.")
            return output_path
        except Exception as e:
            logger.error(f"Failed to export model to ONNX graph format: {e}")
            raise e
