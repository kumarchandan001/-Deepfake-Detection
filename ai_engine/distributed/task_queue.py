from typing import Dict, Any
from ai_engine.distributed.celery_worker import async_analyze_image, async_analyze_voice
from ai_engine.utils.logger import setup_logger

logger = setup_logger("task_queue")

class ForensicTaskQueue:
    """
    Client Task Ingestion Queue.
    Routes jobs to the active Celery cluster, falling back to local 
    synchronous execution if the Redis broker is unavailable.
    """
    @staticmethod
    def dispatch_image_task(image_path: str, run_sync: bool = False) -> Dict[str, Any]:
        """
        Dispatches image forensic analysis job.
        
        Returns:
            Dictionary containing task identity markers or prediction outputs if run synchronously.
        """
        if run_sync:
            logger.info("Executing image forensic sweep synchronously on query thread...")
            # Direct non-blocking execution call bypasses broker
            return async_analyze_image(image_path)

        try:
            logger.info(f"Dispatching async task for image: {image_path}")
            # Trigger standard Celery broker delay method
            task = async_analyze_image.delay(image_path)
            return {
                "success": True,
                "async_mode": True,
                "task_id": task.id,
                "status": task.status
            }
        except Exception as e:
            logger.warning(f"Celery task dispatch failed: {e}. Falling back to sequential synchronous processing.")
            return async_analyze_image(image_path)

    @staticmethod
    def dispatch_audio_task(voice_path: str, run_sync: bool = False) -> Dict[str, Any]:
        """
        Dispatches voice clone forensic analysis job.
        """
        if run_sync:
            logger.info("Executing audio forensic sweep synchronously on query thread...")
            return async_analyze_voice(voice_path)

        try:
            logger.info(f"Dispatching async task for voice: {voice_path}")
            task = async_analyze_voice.delay(voice_path)
            return {
                "success": True,
                "async_mode": True,
                "task_id": task.id,
                "status": task.status
            }
        except Exception as e:
            logger.warning(f"Celery task dispatch failed: {e}. Falling back to sequential synchronous processing.")
            return async_analyze_voice(voice_path)
