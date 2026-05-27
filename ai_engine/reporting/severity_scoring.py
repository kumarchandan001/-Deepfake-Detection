from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("severity_scoring")

class SeverityScorer:
    """
    Forensic Threat Severity Scorer.
    Calculates a normalized 0.00 to 1.00 threat risk coefficient
    and maps incidents to Low, Medium, High, or Critical operational severity profiles.
    """
    @staticmethod
    def calculate_severity_score(
        verdict: str,
        confidence: float,
        is_metadata_modified: bool = False,
        liveness_verified: bool = True,
        source_account: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculates the normalized Severity Index dynamically.
        """
        logger.info("Computing quantitative threat severity index...")
        
        is_fake = verdict in ["FAKE", "MANIPULATED", "FAKE_VOICE"]
        
        score = 0.0
        level = "LOW"

        if is_fake:
            # 1. Base score derived from model confidence (0.40 baseline)
            score = 0.40 + (confidence / 100.0) * 0.20
            
            # 2. Escalate if EXIF metadata was tampered with
            if is_metadata_modified:
                score += 0.15
                
            # 3. Escalate if biometric liveness verification failed
            if not liveness_verified:
                score += 0.15
                
            # 4. Escalate if targeted at high-priority social/executive nodes
            if source_account:
                score += 0.10
                
            # Clamp index score to 1.00 maximum limit
            score = min(1.00, max(0.00, score))

            # Map score ranges to cybersecurity action profiles
            if score > 0.85:
                level = "CRITICAL"
            elif score > 0.60:
                level = "HIGH"
            else:
                level = "MEDIUM"
        else:
            # Real media with failed indicators
            if is_metadata_modified or not liveness_verified:
                score = 0.25
                level = "MEDIUM" # potential low-quality media warning
            else:
                score = 0.05
                level = "LOW"

        return {
            "severity_level": level,
            "severity_score": round(score, 4),
            "is_metadata_modified": is_metadata_modified,
            "liveness_verified": liveness_verified,
            "vip_target_implicated": source_account is not None
        }
