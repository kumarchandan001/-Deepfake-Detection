import time
import asyncio
from typing import Dict, Any, List, Optional
from ai_engine.distributed_inference.ray_cluster import RayForensicCluster, RAY_AVAILABLE
from ai_engine.utils.logger import setup_logger

logger = setup_logger("cluster_manager")

if RAY_AVAILABLE:
    import ray

class ClusterForensicManager:
    """
    Distributed Forensic Cluster Manager & Metrics Collector.
    Tracks cluster health status, aggregates processing latency variables, 
    and exports system telemetry metrics.
    """
    def __init__(self, cluster: Optional[RayForensicCluster] = None):
        self.cluster = cluster or RayForensicCluster()
        self.total_scheduled_tasks = 0
        self.total_failed_tasks = 0
        self.latency_samples: List[float] = []
        logger.info("Cluster Forensic Manager fully initialized.")

    def log_latency_sample(self, latency_sec: float) -> None:
        """
        Registers a processing duration sample to compute rolling averages.
        """
        self.latency_samples.append(latency_sec)
        # Limit history cache to last 1000 records
        if len(self.latency_samples) > 1000:
            self.latency_samples = self.latency_samples[-1000:]

    def get_average_latency_ms(self) -> float:
        if not self.latency_samples:
            return 0.0
        return float(sum(self.latency_samples) / len(self.latency_samples)) * 1000.0

    async def verify_cluster_health(self) -> Dict[str, Any]:
        """
        Sweeps remote Ray actors to verify response health and connection states.
        """
        logger.info("Initiating distributed cluster health audit sweep...")
        
        active_workers = 0
        failed_workers = 0
        details = []

        for idx, worker in enumerate(self.cluster.workers):
            try:
                start_time = time.time()
                
                if RAY_AVAILABLE and isinstance(worker, ray.actor.ActorHandle):
                    # Query actor asynchronously
                    future = worker.check_health.remote()
                    is_healthy = await future
                else:
                    is_healthy = worker.check_health()
                    
                duration = time.time() - start_time
                
                if is_healthy:
                    active_workers += 1
                    details.append({"worker_id": idx, "status": "ONLINE", "ping_ms": round(duration * 1000, 2)})
                else:
                    failed_workers += 1
                    details.append({"worker_id": idx, "status": "UNHEALTHY", "ping_ms": 0.0})
            except Exception as e:
                failed_workers += 1
                logger.error(f"Cluster health sweep failed for worker [{idx}]: {e}")
                details.append({"worker_id": idx, "status": "OFFLINE", "error": str(e)})

        status = "HEALTHY"
        if failed_workers > 0:
            status = "DEGRADED"
        if failed_workers == len(self.cluster.workers):
            status = "CRITICAL_OFFLINE"

        return {
            "cluster_status": status,
            "total_workers": len(self.cluster.workers),
            "active_workers_count": active_workers,
            "failed_workers_count": failed_workers,
            "metrics": {
                "average_inference_latency_ms": round(self.get_average_latency_ms(), 2),
                "total_scheduled_tasks": self.total_scheduled_tasks,
                "total_failed_tasks": self.total_failed_tasks
            },
            "nodes": details
        }
