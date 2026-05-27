import asyncio
import time
from typing import Dict, Any, List, Optional
from ai_engine.distributed_inference.ray_cluster import RayForensicCluster, RAY_AVAILABLE
from ai_engine.utils.logger import setup_logger

logger = setup_logger("inference_scheduler")

if RAY_AVAILABLE:
    import ray

class DistributedInferenceScheduler:
    """
    Hyperscale Parallel Workload Inference Scheduler.
    Schedules visual/vocal classification sweeps across multiple Ray compute actors 
    minimizing queuing delay and optimizing resource capacity.
    """
    def __init__(self, cluster: Optional[RayForensicCluster] = None):
        self.cluster = cluster or RayForensicCluster()
        # Track active tasks loads per worker index: {worker_idx: active_tasks_count}
        self.worker_loads = {i: 0 for i in range(len(self.cluster.workers))}
        self._lock = asyncio.Lock()
        logger.info(f"Distributed Inference Scheduler loaded. Tracking loads for {len(self.worker_loads)} workers.")

    def _select_optimal_worker_index(self) -> int:
        """
        Least-Loaded worker selection scheduling algorithm.
        """
        least_load = float("inf")
        optimal_idx = 0
        
        for idx, load in self.worker_loads.items():
            if load < least_load:
                least_load = load
                optimal_idx = idx
                
        return optimal_idx

    async def schedule_image_analysis(self, file_path: str) -> Dict[str, Any]:
        """
        Schedules a dynamic image forensic check on an optimal remote cluster actor.
        """
        start_time = time.time()
        
        async with self._lock:
            worker_idx = self._select_optimal_worker_index()
            self.worker_loads[worker_idx] += 1
            
        logger.info(f"Scheduler routing image checking task to worker [{worker_idx}] for: {file_path}")
        
        try:
            worker = self.cluster.get_worker(worker_idx)
            
            if RAY_AVAILABLE and isinstance(worker, ray.actor.ActorHandle):
                # Execute asynchronously via Ray actor reference future
                future = worker.analyze_image.remote(file_path)
                result = await future
            else:
                # Synchronous local execution fallback
                result = worker.analyze_image(file_path)
                
            return result
        except Exception as e:
            logger.error(f"Failed to execute scheduled image task on worker [{worker_idx}]: {e}")
            return {"success": False, "error": str(e)}
        finally:
            async with self._lock:
                self.worker_loads[worker_idx] = max(0, self.worker_loads[worker_idx] - 1)

    async def schedule_audio_analysis(self, file_path: str) -> Dict[str, Any]:
        """
        Schedules a voice clone forensic check on an optimal remote cluster actor.
        """
        start_time = time.time()
        
        async with self._lock:
            worker_idx = self._select_optimal_worker_index()
            self.worker_loads[worker_idx] += 1
            
        logger.info(f"Scheduler routing audio checking task to worker [{worker_idx}] for: {file_path}")
        
        try:
            worker = self.cluster.get_worker(worker_idx)
            
            if RAY_AVAILABLE and isinstance(worker, ray.actor.ActorHandle):
                # Execute asynchronously via Ray actor reference future
                future = worker.analyze_audio.remote(file_path)
                result = await future
            else:
                # Synchronous local execution fallback
                result = worker.analyze_audio(file_path)
                
            return result
        except Exception as e:
            logger.error(f"Failed to execute scheduled audio task on worker [{worker_idx}]: {e}")
            return {"success": False, "error": str(e)}
        finally:
            async with self._lock:
                self.worker_loads[worker_idx] = max(0, self.worker_loads[worker_idx] - 1)
