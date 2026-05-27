import unittest
import os
import sys
import asyncio
import numpy as np

# Ensure workspace path imports resolve correctly
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ai_engine.distributed_inference.ray_cluster import RayForensicCluster
from ai_engine.distributed_inference.gpu_allocator import GPUResourceAllocator
from ai_engine.distributed_inference.distributed_batcher import DistributedDynamicBatcher
from ai_engine.distributed_inference.inference_scheduler import DistributedInferenceScheduler
from ai_engine.distributed_inference.cluster_manager import ClusterForensicManager

class TestDistributedInference(unittest.TestCase):
    """
    Validates distributed GPU scheduling, cluster actor scaling, dynamic dynamic batching, 
    and CUDA allocation algorithms.
    """
    def setUp(self):
        self.dummy_img = "mock_dist_image.jpg"
        with open(self.dummy_img, "wb") as f:
            f.write(b"MOCK_DIST_TENSOR_DATA")

    def tearDown(self):
        if os.path.exists(self.dummy_img):
            os.remove(self.dummy_img)

    def test_gpu_allocator_inventory_and_slicing(self):
        """
        GPUResourceAllocator should analyze active CUDA hardware capacity and compute fractional worker quotas.
        """
        allocator = GPUResourceAllocator(memory_reserve_mb=512)
        
        # Test inventory parsing (runs on CPU fallbacks cleanly if CUDA is absent)
        inventory = allocator.query_gpu_inventory()
        self.assertIsInstance(inventory, list)

        # Test worker scaling limits calculations
        slicing = allocator.calculate_slicing_capacity(required_mb_per_worker=1024.0)
        self.assertTrue(slicing["total_scalable_workers"] >= 2)
        self.assertTrue(0.0 <= slicing["fractional_gpu_quota"] <= 1.0)
        
        # Test OOM locks check
        oom_block = allocator.enforce_oom_protective_lock(device_index=0)
        self.assertFalse(oom_block) # standard testing environment should not flag OOM blocks

    def test_distributed_dynamic_batching(self):
        """
        DistributedDynamicBatcher should collect concurrent request futures and dispatch them inside sliding timeframes.
        """
        async def run_batcher_test():
            batcher = DistributedDynamicBatcher(max_batch_size=4, batch_timeout_ms=5.0)
            
            # Submit 3 parallel media check requests concurrently
            tasks = [
                batcher.submit_request("ceo_speech_fake.wav", "AUDIO"),
                batcher.submit_request("genuine_face.png", "IMAGE"),
                batcher.submit_request("botnet_fake_video.mp4", "VIDEO")
            ]
            
            results = await asyncio.gather(*tasks)
            
            self.assertEqual(len(results), 3)
            self.assertTrue(results[0]["success"])
            self.assertEqual(results[0]["prediction"], "FAKE") # 'fake' in ceo_speech_fake.wav
            self.assertEqual(results[1]["prediction"], "REAL") # 'genuine_face.png' lacks 'fake' keyword
            self.assertEqual(results[2]["prediction"], "FAKE")
            
        asyncio.run(run_batcher_test())

    def test_ray_cluster_connections(self):
        """
        RayForensicCluster should connect distributed grids and boot active remote workers.
        """
        cluster = RayForensicCluster(num_workers=3, gpus_per_worker=0.0)
        self.assertTrue(cluster.is_connected)
        self.assertEqual(len(cluster.workers), 3)
        
        # Retrieve worker
        worker = cluster.get_worker(index=4)
        self.assertEqual(worker.worker_id, 1) # worker_id 4 % 3 = 1
        
        cluster.teardown_cluster()

    def test_inference_scheduler_load_balancing(self):
        """
        DistributedInferenceScheduler should assign tasks to the least-loaded remote actor.
        """
        from unittest.mock import patch
        
        async def run_scheduler_test():
            cluster = RayForensicCluster(num_workers=2)
            scheduler = DistributedInferenceScheduler(cluster=cluster)
            
            # Simulate initial artificial worker loads imbalance
            scheduler.worker_loads[0] = 3
            scheduler.worker_loads[1] = 1
            
            # Optimal worker selection should pick the least loaded worker index 1
            optimal_idx = scheduler._select_optimal_worker_index()
            self.assertEqual(optimal_idx, 1)

            # Mock worker behavior to bypass cv2 image reading requirements
            worker = cluster.get_worker(optimal_idx)
            with patch.object(worker, 'analyze_image', return_value={"success": True, "prediction": "REAL"}):
                # Route analysis task
                res = await scheduler.schedule_image_analysis(self.dummy_img)
                self.assertTrue(res["success"])
            
        asyncio.run(run_scheduler_test())

    def test_cluster_forensic_manager_metrics(self):
        """
        ClusterForensicManager should log compute latencies and track overall cluster status metrics.
        """
        async def run_manager_test():
            cluster = RayForensicCluster(num_workers=2)
            manager = ClusterForensicManager(cluster=cluster)
            
            # Log latency metrics samples: 0.12s and 0.18s
            manager.log_latency_sample(0.12)
            manager.log_latency_sample(0.18)
            
            avg_ms = manager.get_average_latency_ms()
            self.assertAlmostEqual(avg_ms, 150.0, places=2)

            # Perform complete health sweep
            report = await manager.verify_cluster_health()
            self.assertEqual(report["total_workers"], 2)
            self.assertTrue(report["cluster_status"] in ["HEALTHY", "DEGRADED"])
            self.assertEqual(len(report["nodes"]), 2)

        asyncio.run(run_manager_test())

if __name__ == "__main__":
    unittest.main()
