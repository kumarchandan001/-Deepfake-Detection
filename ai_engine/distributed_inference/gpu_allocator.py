import torch
import os
import sys
from typing import Dict, Any, List
from ai_engine.utils.logger import setup_logger

logger = setup_logger("gpu_allocator")

class GPUResourceAllocator:
    """
    Enterprise GPU Hardware Resource Allocator.
    Manages physical device bindings, fractional slicing capabilities, and OOM protective limits.
    """
    def __init__(self, memory_reserve_mb: int = 1024):
        self.memory_reserve_mb = memory_reserve_mb
        self.device_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
        logger.info(f"GPU Resource Allocator online. Physical devices detected: {self.device_count}")

    def query_gpu_inventory(self) -> List[Dict[str, Any]]:
        """
        Inspects physical CUDA specifications and reports active inventory profiles.
        """
        inventory = []
        if not torch.cuda.is_available():
            logger.warning("CUDA is inactive. Standard CPU configurations returned.")
            return inventory

        for i in range(self.device_count):
            try:
                name = torch.cuda.get_device_name(i)
                total_mem = torch.cuda.get_device_properties(i).total_memory / (1024 * 1024) # MB
                allocated_mem = torch.cuda.memory_allocated(i) / (1024 * 1024) # MB
                cached_mem = torch.cuda.memory_reserved(i) / (1024 * 1024) # MB
                
                free_mem = total_mem - (allocated_mem + self.memory_reserve_mb)
                is_safe = free_mem > 512.0 # at least 512MB free after reserve buffer
                
                inventory.append({
                    "gpu_index": i,
                    "device_name": name,
                    "total_memory_mb": round(total_mem, 2),
                    "allocated_memory_mb": round(allocated_mem, 2),
                    "cached_memory_mb": round(cached_mem, 2),
                    "estimated_free_memory_mb": round(max(0.0, free_mem), 2),
                    "allocation_allowed": is_safe
                })
            except Exception as e:
                logger.error(f"Failed to query device properties for GPU [{i}]: {e}")
                
        return inventory

    def calculate_slicing_capacity(self, required_mb_per_worker: float = 1500.0) -> Dict[str, Any]:
        """
        Calculates optimal fractional worker allocation slices per physical GPU.
        
        Args:
            required_mb_per_worker: Estimated VRAM footprint needed for local model inference.
            
        Returns:
            Dictionary specifying optimal num_workers scaling parameters and fractional GPU quotas.
        """
        if self.device_count == 0:
            return {"fractional_gpu_quota": 0.0, "total_scalable_workers": 2, "gpus_available": 0}

        inventory = self.query_gpu_inventory()
        total_workers = 0
        allocated_quota = 1.0

        for gpu in inventory:
            if gpu["allocation_allowed"]:
                capacity = gpu["estimated_free_memory_mb"]
                slices = int(capacity // required_mb_per_worker)
                total_workers += max(1, slices)

        # Calculate fractional quota per worker (e.g. 0.25 means 4 workers share 1 GPU device)
        if total_workers > 0 and self.device_count > 0:
            fractional_quota = float(self.device_count / total_workers)
            # Clip between [0.1, 1.0] standard boundaries
            allocated_quota = min(1.0, max(0.1, fractional_quota))

        return {
            "fractional_gpu_quota": round(allocated_quota, 3),
            "total_scalable_workers": max(2, total_workers),
            "gpus_available": self.device_count,
            "inventory": inventory
        }

    def enforce_oom_protective_lock(self, device_index: int) -> bool:
        """
        Interrogates designated GPU memory and flags lock blocks if VRAM headroom is unsafe.
        """
        if not torch.cuda.is_available() or device_index >= self.device_count:
            return False

        try:
            total_mem = torch.cuda.get_device_properties(device_index).total_memory / (1024 * 1024)
            allocated = torch.cuda.memory_allocated(device_index) / (1024 * 1024)
            free = total_mem - allocated
            
            if free < self.memory_reserve_mb:
                logger.critical(f"OOM PROTECTION LOCK ENGAGED on GPU [{device_index}]! Free VRAM {free:.1f}MB is below reserve limit.")
                # Perform proactive GPU cache cleaning
                torch.cuda.empty_cache()
                return True
        except Exception as e:
            logger.error(f"OOM guard failed to verify device memory: {e}")
            
        return False
