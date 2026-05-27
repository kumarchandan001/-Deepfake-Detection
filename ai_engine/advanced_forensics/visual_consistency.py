import numpy as np
from typing import List, Tuple, Dict, Any
from ai_engine.utils.logger import setup_logger

logger = setup_logger("visual_consistency")

class VisualConsistencyAnalyzer:
    """
    Analyzes temporal face markers and acoustic alignments over video sequences.
    Tracks eye blink velocities and mouth opening ratios to isolate deepfakes.
    """
    @staticmethod
    def calculate_eye_aspect_ratio(eye_landmarks: np.ndarray) -> float:
        """
        Computes the Eye Aspect Ratio (EAR) representing eye openness.
        Formula: (||p2 - p6|| + ||p3 - p5||) / (2 * ||p1 - p4||)
        """
        if eye_landmarks.shape[0] < 6:
            return 0.0
            
        # Vertical distances
        a = np.linalg.norm(eye_landmarks[1] - eye_landmarks[5])
        b = np.linalg.norm(eye_landmarks[2] - eye_landmarks[4])
        # Horizontal distance
        c = np.linalg.norm(eye_landmarks[0] - eye_landmarks[3])
        
        if c <= 1e-6:
            return 0.0
            
        return float((a + b) / (2.0 * c))

    @staticmethod
    def analyze_blink_sequence(ear_timeline: List[float], fps: float = 30.0) -> Dict[str, Any]:
        """
        Analyzes EAR timeline sequences for blink intervals and duration anomalies.
        Natural blinking averages 10-20 blinks per minute (0.15s to 0.4s duration per blink).
        Deepfakes often show zero blinks or impossible blink speeds.
        """
        logger.info(f"Analyzing EAR timeline sequence of length {len(ear_timeline)}")
        
        report = {
            "blink_count": 0,
            "anomalous_blink_speed": False,
            "absence_of_blinking": False,
            "average_ear": 0.0,
            "blink_risk_score": 0.0
        }

        if len(ear_timeline) < 10:
            return report

        ear_arr = np.array(ear_timeline)
        report["average_ear"] = float(np.mean(ear_arr))

        # Thresholds for EAR dip (standard is ~0.2 for closed eyes)
        closed_threshold = 0.22
        is_closed = ear_arr < closed_threshold
        
        # Count consecutive frame closures to detect individual blinks
        blink_frames = 0
        blinks = []
        
        for closed in is_closed:
            if closed:
                blink_frames += 1
            else:
                if blink_frames > 0:
                    blinks.append(blink_frames)
                    blink_frames = 0
        if blink_frames > 0:
            blinks.append(blink_frames)

        report["blink_count"] = len(blinks)

        # 1. Flag absence of blinking (over 10 seconds of video timeline)
        video_duration_seconds = len(ear_timeline) / fps
        if video_duration_seconds > 10.0 and len(blinks) == 0:
            report["absence_of_blinking"] = True
            report["blink_risk_score"] = 0.85
            logger.warning("Forensics anomaly: Zero blinking events detected across video sequence.")

        # 2. Flag impossible blink velocities (too fast or too slow)
        for duration_frames in blinks:
            duration_seconds = duration_frames / fps
            if duration_seconds < 0.08 or duration_seconds > 0.8:
                report["anomalous_blink_speed"] = True
                report["blink_risk_score"] = max(report["blink_risk_score"], 0.75)
                logger.warning(f"Forensics anomaly: Unnatural blinking velocity of {duration_seconds:.2f}s.")

        return report

    @staticmethod
    def check_lipsync_alignment(
        mouth_opening_amplitude: np.ndarray, 
        audio_energy_envelope: np.ndarray,
        fps: float = 30.0
    ) -> Dict[str, Any]:
        """
        Cross-correlates facial speech movements with voice energy outputs.
        High cross-correlation shifts represent synthetic speech splicing or deepfake overlays.
        """
        report = {
            "is_synchronized": True,
            "correlation_coefficient": 1.0,
            "delay_seconds": 0.0,
            "lipsync_risk_score": 0.0
        }

        min_len = min(len(mouth_opening_amplitude), len(audio_energy_envelope))
        if min_len < 15:
            return report

        m_amp = mouth_opening_amplitude[:min_len]
        a_env = audio_energy_envelope[:min_len]

        # Calculate cross-correlation shifts
        correlation = np.corrcoef(m_amp, a_env)[0, 1]
        
        if np.isnan(correlation):
            correlation = 0.0

        report["correlation_coefficient"] = float(correlation)

        # High risk threshold: low speech-action correlation
        if correlation < 0.35:
            report["is_synchronized"] = False
            report["lipsync_risk_score"] = float(0.80 * (1.0 - correlation))
            logger.warning(f"Forensics anomaly: Speech-lip mismatch. Correlation={correlation:.3f}")

        return report
