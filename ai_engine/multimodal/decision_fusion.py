from typing import Dict, Any
from ai_engine.utils.logger import setup_logger

logger = setup_logger("decision_fusion")

class MultimodalDecisionFusion:
    """
    Combines independent predictions from both visual (video) and acoustic (audio)
    inference engines using a weighted confidence mapping function.
    """
    def __init__(self, weight_video: float = 0.6, weight_audio: float = 0.4):
        self.weight_video = weight_video
        self.weight_audio = weight_audio
        logger.info(f"MultimodalDecisionFusion configured: Weights -> Video={weight_video}, Audio={weight_audio}")

    def fuse_predictions(self, video_result: Dict[str, Any], audio_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculates a unified classification score based on independent video and audio scores.
        """
        # If one engine failed completely, fallback gracefully to the other
        if not video_result.get("success", False):
            logger.warning("Video forensic analysis failed. Falling back strictly to audio scores.")
            return audio_result
            
        if not audio_result.get("success", False):
            logger.warning("Audio forensic analysis failed. Falling back strictly to video scores.")
            return video_result

        # Extract raw prediction scores (scaled float probabilities between 0.0 and 1.0)
        # Note: FAKE = 1.0, REAL = 0.0
        score_video = video_result.get("mean_score", 0.5) if "mean_score" in video_result else (video_result.get("raw_score", 0.5))
        score_audio = audio_result.get("raw_score", 0.5)
        
        # Weighted Aggregation (Multimodal Decision Fusion)
        fused_score = (self.weight_video * score_video) + (self.weight_audio * score_audio)
        
        is_fake = fused_score >= 0.5
        confidence = fused_score if is_fake else (1.0 - fused_score)
        
        prediction_label = "MULTIMODAL_FAKE" if is_fake else "MULTIMODAL_REAL"
        
        return {
            "success": True,
            "prediction": prediction_label,
            "confidence": round(float(confidence * 100), 2),
            "fused_score": float(fused_score),
            "breakdown": {
                "video_prediction": video_result.get("prediction"),
                "video_confidence": video_result.get("confidence"),
                "audio_prediction": audio_result.get("prediction"),
                "audio_confidence": audio_result.get("confidence")
            }
        }
