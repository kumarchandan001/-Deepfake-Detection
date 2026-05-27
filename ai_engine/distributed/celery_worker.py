import os
from celery import Celery
from typing import Dict, Any
from ai_engine.inference.inference_engine import DeepfakeInferenceEngine
from ai_engine.audio_inference.realtime_audio_engine import RealtimeAudioEngine
from ai_engine.utils.logger import setup_logger

logger = setup_logger("celery_worker")

# Load broker configuration parameters from secure profiles
REDIS_BROKER = os.getenv("REDIS_URL", "redis://localhost:6379/0")

# Instantiate Celery task executor app
celery_app = Celery(
    "antigravity_forensics",
    broker=REDIS_BROKER,
    backend=REDIS_BROKER
)

# Standard configurations
celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_track_started=True
)

logger.info(f"Celery task application initialized. Active Broker: {REDIS_BROKER}")

# Core asynchronous background tasks execution maps
@celery_app.task(name="tasks.async_analyze_image")
def async_analyze_image(image_path: str) -> Dict[str, Any]:
    """
    Asynchronous Celery task wrapping image forensic inference.
    """
    logger.info(f"Worker enqueuing image forensic task for asset: {image_path}")
    try:
        engine = DeepfakeInferenceEngine()
        result = engine.predict_image(image_path)
        logger.info(f"Async image task completed successfully: {image_path}")
        return result
    except Exception as e:
        logger.error(f"Async image verification task failed: {e}")
        return {"success": False, "error": str(e)}

@celery_app.task(name="tasks.async_analyze_voice")
def async_analyze_voice(voice_path: str) -> Dict[str, Any]:
    """
    Asynchronous Celery task wrapping voice forensics.
    """
    logger.info(f"Worker enqueuing audio forensic task for asset: {voice_path}")
    try:
        engine = RealtimeAudioEngine()
        result = engine.analyze_voice_track(voice_path)
        logger.info(f"Async audio task completed successfully: {voice_path}")
        return result
    except Exception as e:
        logger.error(f"Async audio verification task failed: {e}")
        return {"success": False, "error": str(e)}
