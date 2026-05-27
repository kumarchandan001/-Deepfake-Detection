import os
import sys
import logging
from typing import Dict, Any, List, Optional

# Ensure standard logger setup
from ai_engine.utils.logger import setup_logger
logger = setup_logger("ray_cluster")

# Gracefully handle Ray availability for stable execution across all systems
RAY_AVAILABLE = False
try:
    import ray
    RAY_AVAILABLE = True
except ImportError:
    logger.warning("Ray library is missing. Distributed GPU scaling will fallback to standard multi-threaded pools.")

# Sub-engine lazy imports
from ai_engine.inference.inference_engine import DeepfakeInferenceEngine
from ai_engine.audio_inference.realtime_audio_engine import RealtimeAudioInferenceEngine

if RAY_AVAILABLE:
    @ray.remote
    class RayForensicWorker:
        """
        Ray remote actor class managing dedicated model instances on specific GPU allocations.
        """
        def __init__(self, worker_id: int, gpu_id: Optional[float] = None):
            self.worker_id = worker_id
            self.gpu_id = gpu_id
            
            # Restrict CUDA visibility to designated GPU slice if requested
            if gpu_id is not None:
                os.environ["CUDA_VISIBLE_DEVICES"] = str(int(gpu_id))
                logger.info(f"Worker [{worker_id}] bound to hardware GPU index: {gpu_id}")
            else:
                logger.info(f"Worker [{worker_id}] initialized on CPU.")
                
            # Instantiate model engines locally inside actor process
            self.image_engine = DeepfakeInferenceEngine()
            self.audio_engine = RealtimeAudioInferenceEngine()

        def analyze_image(self, file_path: str) -> Dict[str, Any]:
            logger.info(f"Worker [{self.worker_id}] auditing image: {os.path.basename(file_path)}")
            return self.image_engine.predict_image(file_path)

        def analyze_audio(self, file_path: str) -> Dict[str, Any]:
            logger.info(f"Worker [{self.worker_id}] auditing audio: {os.path.basename(file_path)}")
            return self.audio_engine.predict_audio_file(file_path)

        def check_health(self) -> bool:
            return True
else:
    # Failback class representation
    class RayForensicWorker:
        def __init__(self, worker_id: int, gpu_id: Optional[float] = None):
            self.worker_id = worker_id
            self.image_engine = DeepfakeInferenceEngine()
            self.audio_engine = RealtimeAudioInferenceEngine()

        def analyze_image(self, file_path: str) -> Dict[str, Any]:
            return self.image_engine.predict_image(file_path)

        def analyze_audio(self, file_path: str) -> Dict[str, Any]:
            return self.audio_engine.predict_audio_file(file_path)

        def check_health(self) -> bool:
            return True


class RayForensicCluster:
    """
    Ray Forensic Cluster Controller.
    Orchestrates connection handles, actor scaling limits, and resource affinities.
    """
    def __init__(self, num_workers: int = 2, gpus_per_worker: float = 0.0):
        self.num_workers = num_workers
        self.gpus_per_worker = gpus_per_worker
        self.workers: List[Any] = []
        self.is_connected = False
        
        self.connect_cluster()

    def connect_cluster(self) -> None:
        """
        Boots Ray environment and initializes remote actor worker pools.
        """
        if not RAY_AVAILABLE:
            logger.warning("Initializing Local Fallback Worker Pool (Non-Ray).")
            self.workers = [RayForensicWorker(i) for i in range(self.num_workers)]
            self.is_connected = True
            return

        try:
            logger.info("Connecting to Ray distributed compute grid...")
            if not ray.is_initialized():
                ray.init(ignore_reinit_error=True, logging_level=logging.ERROR)
            
            self.workers = []
            for i in range(self.num_workers):
                # Configure fractional GPU resource allocations dynamically
                if self.gpus_per_worker > 0.0:
                    worker = RayForensicWorker.options(
                        num_gpus=self.gpus_per_worker
                    ).remote(worker_id=i, gpu_id=float(i % max(1, int(1.0 / self.gpus_per_worker))))
                else:
                    worker = RayForensicWorker.remote(worker_id=i)
                    
                self.workers.append(worker)
                
            self.is_connected = True
            logger.info(f"Ray cluster fully initialized. Scaled {self.num_workers} remote actors.")
        except Exception as e:
            logger.error(f"Ray initialization failure: {e}. Falling back to local thread pool.")
            self.workers = [RayForensicWorker(i) for i in range(self.num_workers)]
            self.is_connected = True

    def get_worker(self, index: int) -> Any:
        return self.workers[index % len(self.workers)]

    def teardown_cluster(self) -> None:
        if RAY_AVAILABLE and ray.is_initialized():
            logger.info("Tearing down active Ray workers pool...")
            ray.shutdown()
            self.is_connected = False
            logger.info("Ray shutdown complete.")
