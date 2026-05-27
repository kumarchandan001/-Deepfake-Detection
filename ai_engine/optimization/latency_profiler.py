import time
import torch
import torch.nn as nn
from typing import Tuple, Dict, Any
from ai_engine.utils.logger import setup_logger

logger = setup_logger("latency_profiler")

class LatencyProfiler:
    """
    Measures and profiles inference metrics for computer vision 
    and acoustic forensic models, tracking GPU/CPU latencies and memory usage.
    """
    @staticmethod
    def profile(
        model: nn.Module,
        input_shape: Tuple[int, ...],
        num_warmup: int = 20,
        num_iters: int = 100,
        device: str = "cpu"
    ) -> Dict[str, Any]:
        """
        Profiles the forward-pass execution latency of a target model.
        
        Args:
            model: PyTorch model instance
            input_shape: Input dummy tensor dimensions
            num_warmup: Number of non-recorded warm-up iterations
            num_iters: Number of recorded benchmark iterations
            device: Run profiling on 'cpu' or 'cuda'
            
        Returns:
            Dictionary containing latency, throughput, and memory stats.
        """
        logger.info(f"Starting performance profiling on device: {device}")
        
        # 1. Setup device and prep model
        device_obj = torch.device(device)
        model = model.to(device_obj)
        model.eval()
        
        dummy_input = torch.randn(*input_shape, device=device_obj)

        # 2. GPU Warm-up (Important to bypass initial driver initialization delays)
        logger.info(f"Running {num_warmup} warm-up iterations...")
        with torch.no_grad():
            for _ in range(num_warmup):
                _ = model(dummy_input)

        if "cuda" in device:
            torch.cuda.synchronize()

        # 3. Benchmark iterations
        logger.info(f"Running {num_iters} benchmark iterations...")
        latencies = []
        
        with torch.no_grad():
            for _ in range(num_iters):
                start_time = time.perf_counter()
                _ = model(dummy_input)
                if "cuda" in device:
                    torch.cuda.synchronize()
                end_time = time.perf_counter()
                
                latencies.append((end_time - start_time) * 1000.0) # convert to ms

        # 4. Compile statistics
        avg_latency = sum(latencies) / len(latencies)
        min_latency = min(latencies)
        max_latency = max(latencies)
        latencies_sorted = sorted(latencies)
        p50_latency = latencies_sorted[int(len(latencies_sorted) * 0.5)]
        p95_latency = latencies_sorted[int(len(latencies_sorted) * 0.95)]
        p99_latency = latencies_sorted[int(len(latencies_sorted) * 0.99)]
        
        # Samples processed per second
        throughput = 1000.0 / avg_latency if avg_latency > 0 else 0.0

        # Memory footprint calculations
        gpu_allocated_mb = 0.0
        gpu_cached_mb = 0.0
        if "cuda" in device:
            gpu_allocated_mb = torch.cuda.max_memory_allocated(device_obj) / (1024 * 1024)
            gpu_cached_mb = torch.cuda.max_memory_reserved(device_obj) / (1024 * 1024)

        report = {
            "device": device,
            "iterations": num_iters,
            "average_latency_ms": avg_latency,
            "min_latency_ms": min_latency,
            "max_latency_ms": max_latency,
            "p50_latency_ms": p50_latency,
            "p95_latency_ms": p95_latency,
            "p99_latency_ms": p99_latency,
            "throughput_fps": throughput,
            "max_gpu_allocated_mb": gpu_allocated_mb,
            "max_gpu_reserved_mb": gpu_cached_mb
        }

        logger.info(f"--- Profiling Report ({device}) ---")
        logger.info(f"Average Latency: {avg_latency:.3f} ms")
        logger.info(f"95th Percentile: {p95_latency:.3f} ms")
        logger.info(f"Throughput: {throughput:.2f} samples/sec")
        if "cuda" in device:
            logger.info(f"Max CUDA Memory Allocated: {gpu_allocated_mb:.2f} MB")
        logger.info("---------------------------------")

        return report
ZOOM = LatencyProfiler  # Quick class mapping for internal convenience
