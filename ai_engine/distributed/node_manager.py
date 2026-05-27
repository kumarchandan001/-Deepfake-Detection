import time
import torch
from typing import Dict, Any, List
from ai_engine.utils.logger import setup_logger

logger = setup_logger("node_manager")

class NodeManager:
    """
    Distributed AI Node Manager.
    Monitors node health markers, registers active workers,
    and dynamically routes workloads based on hardware limits.
    """
    def __init__(self):
        # Cluster node directory: {node_ip: {status: str, gpu_count: int, last_seen: float}}
        self.active_nodes: Dict[str, Dict[str, Any]] = {}
        
        # Self-registration of local master node
        self.register_local_node()

    def register_local_node(self) -> None:
        """
        Self-registers master hardware configurations on start.
        """
        gpu_count = torch.cuda.device_count() if torch.cuda.is_available() else 0
        node_spec = {
            "node_role": "master",
            "status": "healthy",
            "gpu_count": gpu_count,
            "gpu_names": [torch.cuda.get_device_name(i) for i in range(gpu_count)] if gpu_count > 0 else ["CPU-only execution pool"],
            "last_ping": time.time()
        }
        self.active_nodes["localhost"] = node_spec
        logger.info(f"Master node registered successfully. Hardware: {node_spec['gpu_names']}")

    def register_worker_node(self, node_ip: str, gpu_count: int = 0) -> None:
        """
        Registers external worker nodes entering the cluster network.
        """
        self.active_nodes[node_ip] = {
            "node_role": "worker",
            "status": "healthy",
            "gpu_count": gpu_count,
            "last_ping": time.time()
        }
        logger.info(f"Registered external worker node: {node_ip} (GPUs={gpu_count})")

    def ping_node(self, node_ip: str) -> None:
        """
        Keeps node state active in registry.
        """
        if node_ip in self.active_nodes:
            self.active_nodes[node_ip]["last_ping"] = time.time()
            self.active_nodes[node_ip]["status"] = "healthy"

    def get_healthy_execution_pool(self, max_inactivity_sec: float = 30.0) -> List[str]:
        """
        Prunes inactive workers and returns list of responsive execution IPs.
        """
        current_time = time.time()
        healthy_ips = []
        
        for ip, spec in list(self.active_nodes.items()):
            elapsed = current_time - spec["last_ping"]
            if elapsed > max_inactivity_sec:
                spec["status"] = "offline"
                logger.warning(f"Worker node [{ip}] marked OFFLINE: Inactive for {elapsed:.2f}s.")
            else:
                healthy_ips.append(ip)
                
        return healthy_ips
