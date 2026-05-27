import cv2
import numpy as np
from typing import Dict, Any
from ai_engine.utils.logger import setup_logger

logger = setup_logger("spoof_protection")

class SpoofProtectionEngine:
    """
    Liveness Verification and Anti-Spoofing Engine.
    Detects printed paper photo bypasses and digital screen replay attacks
    using texture edge analysis (Laplacian Variance).
    """
    @staticmethod
    def calculate_laplacian_variance(face_image_bgr: np.ndarray) -> float:
        """
        Computes the Laplacian variance (sharpness metric) of a face crop.
        Formula: var(Laplacian(gray))
        """
        # Convert crop to gray
        gray = cv2.cvtColor(face_image_bgr, cv2.COLOR_BGR2GRAY)
        # Compute Laplacian edge gradients
        laplacian = cv2.Laplacian(gray, cv2.CV_64F)
        return float(laplacian.var())

    @staticmethod
    def verify_liveness(
        face_image_bgr: np.ndarray,
        min_threshold: float = 120.0,  # Below indicates blurred/low-depth printed photo
        max_threshold: float = 950.0   # Above indicates digital screen pixel moiré lines
    ) -> Dict[str, Any]:
        """
        Executes face liveness checks on incoming crop.
        """
        logger.info("Executing active face liveness anti-spoofing scan...")
        
        report = {
            "liveness_verified": True,
            "sharpness_variance": 0.0,
            "min_limit": min_threshold,
            "max_limit": max_threshold,
            "spoof_type": "ORGANIC_FACE"
        }

        h, w, _ = face_image_bgr.shape
        if h < 20 or w < 20:
            report["liveness_verified"] = False
            report["spoof_type"] = "INSUFFICIENT_RESOLUTION"
            return report

        # Calculate texture edge variance
        variance = SpoofProtectionEngine.calculate_laplacian_variance(face_image_bgr)
        report["sharpness_variance"] = round(variance, 2)

        # 1. Print Attack (Blurred edges, low depth)
        if variance < min_threshold:
            report["liveness_verified"] = False
            report["spoof_type"] = "PRINT_SPOOF_ATTACK"
            logger.warning(f"Liveness Check failed: Low variance ({variance:.2f}). Printed photo suspected.")

        # 2. Replay Screen Attack (High-frequency moiré patterns)
        elif variance > max_threshold:
            report["liveness_verified"] = False
            report["spoof_type"] = "REPLAY_SCREEN_SPOOF"
            logger.warning(f"Liveness Check failed: Excess variance ({variance:.2f}). Digital screen moiré suspected.")
            
        return report

# Backward compatibility alias
SpoofProtection = SpoofProtectionEngine

