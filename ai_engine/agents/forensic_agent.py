import os
from typing import Dict, Any, Optional
from ai_engine.agents.agent_memory import AgentMemory
from ai_engine.inference.inference_engine import DeepfakeInferenceEngine
from ai_engine.audio_inference.realtime_audio_engine import RealtimeAudioEngine
from ai_engine.multimodal.fusion_engine import MultimodalFusionEngine
from ai_engine.utils.logger import setup_logger

logger = setup_logger("forensic_agent")

class ForensicAgent:
    """
    Autonomous AI Forensic Analyst.
    Dynamically routes media formats to target models, executes deep scans, 
    and writes investigative observations into persistent memory.
    """
    def __init__(self, memory: Optional[AgentMemory] = None):
        self.memory = memory or AgentMemory()
        
        # Instantiate sub-forensic engines dynamically
        self.image_engine = DeepfakeInferenceEngine()
        self.audio_engine = RealtimeAudioEngine()
        self.multimodal_engine = MultimodalFusionEngine()

    async def investigate_media(self, case_id: str, file_path: str) -> Dict[str, Any]:
        """
        Autonomously inspects a target asset and coordinates model verification runs.
        
        Returns:
            Structured dictionary representing final model attributions.
        """
        logger.info(f"Forensic Agent initiating investigation on case [{case_id}] for asset: {file_path}")
        self.memory.record_observation(case_id, "ForensicAgent", f"Analyzing uploaded asset: {os.path.basename(file_path)}")

        if not os.path.exists(file_path):
            err_msg = f"Asset file missing at target destination: {file_path}"
            self.memory.record_observation(case_id, "ForensicAgent", f"ERROR: {err_msg}")
            return {"success": False, "error": err_msg}

        ext = os.path.splitext(file_path)[1].lower()
        result = {"success": False, "verdict": "UNDETERMINED", "confidence": 0.0}

        try:
            # 1. Image Forensics Routing
            if ext in [".jpg", ".jpeg", ".png", ".webp"]:
                self.memory.record_observation(case_id, "ForensicAgent", "Asset identified as IMAGE. Loading spatial convolutional attributions...")
                raw_res = self.image_engine.predict_image(file_path)
                
                if raw_res.get("success", False):
                    result = {
                        "success": True,
                        "verdict": raw_res["prediction"],
                        "confidence": raw_res["confidence"],
                        "raw_score": raw_res["raw_score"],
                        "processing_time": raw_res["processing_time"]
                    }
                    self.memory.record_observation(
                        case_id, 
                        "ForensicAgent", 
                        f"Image scan completed. Verdict={result['verdict']}, Confidence={result['confidence']:.2f}%"
                    )

            # 2. Audio Forensics Routing
            elif ext in [".wav", ".mp3", ".ogg", ".m4a"]:
                self.memory.record_observation(case_id, "ForensicAgent", "Asset identified as AUDIO. Launching acoustic vocoder analysis...")
                raw_res = self.audio_engine.analyze_voice_track(file_path)
                
                if raw_res.get("success", False):
                    result = {
                        "success": True,
                        "verdict": raw_res["prediction"],
                        "confidence": raw_res["confidence"],
                        "processing_time": raw_res["processing_time"]
                    }
                    self.memory.record_observation(
                        case_id, 
                        "ForensicAgent", 
                        f"Acoustic scan completed. Verdict={result['verdict']}, Confidence={result['confidence']:.2f}%"
                    )

            # 3. Video / Multimodal Forensics Routing
            elif ext in [".mp4", ".mov", ".avi", ".mkv"]:
                self.memory.record_observation(case_id, "ForensicAgent", "Asset identified as MULTIMEDIA. Triggering spatial-temporal and speech demux pipelines...")
                raw_res = self.multimodal_engine.process_multimodal_container(file_path)
                
                if raw_res.get("success", False):
                    result = {
                        "success": True,
                        "verdict": raw_res["prediction"],
                        "confidence": raw_res["confidence"],
                        "video_verdict": raw_res["video_prediction"],
                        "audio_verdict": raw_res["audio_prediction"],
                        "processing_time": raw_res["processing_time"]
                    }
                    self.memory.record_observation(
                        case_id, 
                        "ForensicAgent", 
                        f"Multimodal scan completed. Verdict={result['verdict']}, Confidence={result['confidence']:.2f}%"
                    )
            else:
                err_msg = f"Unsupported media type profile: {ext}"
                self.memory.record_observation(case_id, "ForensicAgent", f"ERROR: {err_msg}")
                return {"success": False, "error": err_msg}

            # Cache the context variables in memory
            self.memory.cache_case_context(case_id, result)
            return result

        except Exception as e:
            err_str = f"Inference execution failed: {e}"
            logger.error(err_str)
            self.memory.record_observation(case_id, "ForensicAgent", f"CRITICAL: {err_str}")
            return {"success": False, "error": err_str}
