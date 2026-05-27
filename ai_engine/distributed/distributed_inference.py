import numpy as np
from typing import List, Dict, Any
from ai_engine.distributed.task_queue import ForensicTaskQueue
from ai_engine.utils.logger import setup_logger

logger = setup_logger("distributed_inference")

class DistributedInferenceRouter:
    """
    Distributed Inference Batch Router.
    Partitions bulk video frames or long-duration voice sequences,
    schedules sub-chunks to available cluster nodes, and aggregates scores.
    """
    @staticmethod
    def partition_and_dispatch_image_batch(
        image_filepaths: List[str], 
        run_sync: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Splits a bulk set of visual query paths and distributes them across available workers.
        """
        logger.info(f"Distributing batch execution of {len(image_filepaths)} images...")
        results = []
        
        for path in image_filepaths:
            # Dispatch each task to the execution broker queue
            res = ForensicTaskQueue.dispatch_image_task(path, run_sync=run_sync)
            results.append({
                "file_path": path,
                "dispatch_result": res
            })
            
        logger.info("Batch execution scheduling completed.")
        return results

    @staticmethod
    def consolidate_batch_verdicts(dispatched_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Synthesizes individual distributed scores into an overall batch verdict.
        """
        total = len(dispatched_results)
        fakes = 0
        confidences = []

        for item in dispatched_results:
            res = item.get("dispatch_result", {})
            if res.get("success", False):
                if res.get("verdict") in ["FAKE", "MANIPULATED", "FAKE_VOICE"]:
                    fakes += 1
                confidences.append(res.get("confidence", 0.0))

        overall_confidence = np.mean(confidences) if confidences else 0.0
        verdict = "MANIPULATED" if fakes > 0 else "AUTHENTIC"

        return {
            "total_items": total,
            "fake_items_detected": fakes,
            "average_confidence": round(float(overall_confidence), 2),
            "final_verdict": verdict
        }
