import os
from typing import Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("tensor_rt")

class TensorRTOptimizer:
    """
    Compiles ONNX graphs into ultra-low-latency NVIDIA TensorRT engines
    or configures high-speed TensorRT Execution Providers in ONNX Runtime.
    """
    def __init__(self, cache_dir: str = "weights/tensorrt"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def get_ort_tensorrt_session_options(self) -> dict:
        """
        Builds optimized Execution Provider configurations to inject TensorRT 
        into ONNX Runtime sessions dynamically.
        """
        logger.info("Configuring TensorRT execution provider options...")
        return {
            "device_id": 0,
            "trt_max_workspace_size": 2147483648,  # 2 GB GPU memory limit
            "trt_fp16_enable": True,              # Enable FP16 inference for speeds
            "trt_engine_cache_enable": True,      # Cache engine locally on disk
            "trt_engine_cache_path": self.cache_dir
        }

    def compile_onnx_to_trt_engine(self, onnx_model_path: str, engine_filename: str) -> Optional[str]:
        """
        Attempts to compile a standalone engine binary using native TensorRT APIs.
        Note: Requires the native 'tensorrt' python package to be installed.
        """
        output_engine_path = os.path.join(self.cache_dir, engine_filename)
        logger.info(f"Targeting TRT serialization to: {output_engine_path}")

        try:
            import tensorrt as trt
            
            TRT_LOGGER = trt.Logger(trt.Logger.WARNING)
            builder = trt.Builder(TRT_LOGGER)
            network = builder.create_network(1 << int(trt.NetworkDefinitionCreationFlag.EXPLICIT_BATCH))
            parser = trt.OnnxParser(network, TRT_LOGGER)
            
            # Read ONNX file
            with open(onnx_model_path, "rb") as model:
                if not parser.parse(model.read()):
                    for error in range(parser.num_errors):
                        logger.error(f"ONNX Parsing Error: {parser.get_error(error)}")
                    return None
            
            # Configure building profile
            config = builder.create_builder_config()
            config.set_memory_pool_limit(trt.MemoryPoolType.WORKSPACE, 2 << 30) # 2GB
            
            # FP16 optimization check
            if builder.platform_has_fast_fp16:
                config.set_flag(trt.BuilderFlag.FP16)
                logger.info("FP16 hardware acceleration activated for compilation.")

            # Serialize engine
            serialized_engine = builder.build_serialized_network(network, config)
            if serialized_engine is None:
                logger.error("Failed to serialize TensorRT engine network.")
                return None

            with open(output_engine_path, "wb") as f:
                f.write(serialized_engine)

            logger.info(f"Successfully compiled and cached TensorRT engine: {output_engine_path}")
            return output_engine_path

        except ImportError:
            logger.warning("NVIDIA tensorrt python package not available in local environment. Use ONNX Runtime EP.")
            return None
        except Exception as e:
            logger.error(f"Error compiling TensorRT engine: {e}")
            return None
