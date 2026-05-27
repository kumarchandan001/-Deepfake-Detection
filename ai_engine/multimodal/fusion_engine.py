import os
import time
from typing import Dict, Any, Optional
# librosa for audio load fallback
import librosa
from ai_engine.video_inference.video_inference_engine import DeepfakeVideoInferenceEngine
from ai_engine.audio_inference.realtime_audio_engine import RealtimeAudioInferenceEngine
from ai_engine.multimodal.decision_fusion import MultimodalDecisionFusion
from ai_engine.utils.logger import setup_logger

logger = setup_logger("multimodal_fusion")

class MultimodalForensicsEngine:
    """
    Ingests multimodal video assets (.mp4), extracts both visual and acoustic streams,
    routes them to respective GPU classification engines, and fuses decision patterns.
    """
    def __init__(self, frame_weights: Optional[str] = None, audio_weights: Optional[str] = None):
        self.video_engine = DeepfakeVideoInferenceEngine(frame_engine_path=frame_weights)
        self.audio_engine = RealtimeAudioInferenceEngine(model_path=audio_weights)
        self.fusion = MultimodalDecisionFusion(weight_video=0.6, weight_audio=0.4)
        logger.info("MultimodalForensicsEngine fully loaded and initialized.")

    def analyze_media(self, mp4_filepath: str) -> Dict[str, Any]:
        """
        Extracts audio track, executes joint predictions, and fuses results.
        """
        start_time = time.time()
        temp_audio_path = f"temp_track_{int(time.time())}.wav"
        
        try:
            # 1. Demux (Extract) Audio Track from MP4 using librosa (handles video files natively!)
            logger.info(f"Extracting acoustic stream track from: {mp4_filepath}")
            y, sr = librosa.load(mp4_filepath, sr=16000) # Resample to 16kHz standard
            
            # Save audio track temporarily to process
            import soundfile as sf
            sf.write(temp_audio_path, y, sr)
            
            has_audio = True
            logger.info("Successfully demuxed audio track.")
        except Exception as e:
            logger.warning(f"No audio stream track detected or demux failed: {e}. Defaulting strictly to visual forensics.")
            has_audio = False

        try:
            # 2. Run Visual (Video) Forensic Evaluation
            logger.info("Executing video visual forensic pipeline...")
            video_result = self.video_engine.analyze_video(mp4_filepath)
            
            # 3. Run Acoustic (Audio) Forensic Evaluation
            audio_result = {"success": False, "error": "No audio track available."}
            if has_audio:
                logger.info("Executing audio acoustic forensic pipeline...")
                audio_result = self.audio_engine.predict_audio_file(temp_audio_path)
                
            # Clean up temp file
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

            # 4. Fuse Decisions
            fused_result = self.fusion.fuse_predictions(video_result, audio_result)
            
            processing_time = time.time() - start_time
            fused_result["total_processing_time"] = round(processing_time, 4)
            
            return fused_result
            
        except Exception as e:
            logger.error(f"Multimodal evaluation failure: {e}")
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
            return {"success": False, "error": str(e)}

# Backward compatibility alias
class MultimodalFusionEngine(MultimodalForensicsEngine):
    def process_multimodal_container(self, file_path: str) -> Dict[str, Any]:
        res = self.analyze_media(file_path)
        video_pred = "REAL"
        audio_pred = "REAL_VOICE"
        
        # Safely extract sub-predictions if present in results dictionary
        if "video_result" in res:
            video_pred = res["video_result"].get("prediction", "REAL")
        if "audio_result" in res:
            audio_pred = res["audio_result"].get("prediction", "REAL_VOICE")
            
        return {
            "success": res.get("success", True),
            "prediction": res.get("prediction", "REAL"),
            "confidence": res.get("confidence", 50.0),
            "video_prediction": video_pred,
            "audio_prediction": audio_pred,
            "processing_time": res.get("total_processing_time", 0.0)
        }

