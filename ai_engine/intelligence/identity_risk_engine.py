import time
from typing import Dict, Any, List
from ai_engine.utils.logger import setup_logger

logger = setup_logger("identity_risk")

class IdentityRiskEngine:
    """
    High-Profile Identity Compromise Evaluation Engine.
    Assess deepfake exposure risks specifically for registered corporate targets 
    (VIPS, CEOs, Executive spokespersons).
    """
    def __init__(self):
        # High-risk profile whitelist: {name: role_importance_weight (1.0 to 5.0)}
        self.vip_directory: Dict[str, float] = {
            "ceo": 5.0,
            "cfo": 4.5,
            "cto": 4.0,
            "president": 5.0,
            "spokesperson": 3.5
        }

    def assess_profile_compromise_risk(
        self, 
        target_name: str, 
        role_label: str,
        manipulation_confidence: float
    ) -> Dict[str, Any]:
        """
        Calculates Identity Exposure Score (IES) dynamically.
        IES = Role_Weight * Manipulation_Confidence
        """
        logger.info(f"Identity Risk Engine scanning exposure bounds for: {target_name} ({role_label})")
        
        role_key = role_label.lower()
        role_weight = 1.0 # standard profile baseline weight
        
        # Check matching weights in executive lists
        for key, weight in self.vip_directory.items():
            if key in role_key:
                role_weight = weight
                break

        # Compute risk index score on scale 0.0 to 1.0
        exposure_index = float((manipulation_confidence / 100.0) * (role_weight / 5.0))
        exposure_index = min(1.0, max(0.0, exposure_index))

        # Assign alert categorization tags
        alert_level = "INFORMATIONAL"
        if exposure_index > 0.8:
            alert_level = "CRITICAL_COMPROMISE"
            logger.critical(f"IDENTITY COMPROMISE ALERT: CEO/Executive targeted deepfake verified! Index: {exposure_index:.2f}")
        elif exposure_index > 0.5:
            alert_level = "HIGH_COMPROMISE_WARNING"
            logger.warning(f"HIGH COMPROMISE WARNING: Executive targeted spoofing: Index: {exposure_index:.2f}")
        elif exposure_index > 0.2:
            alert_level = "MEDIUM_COMPROMISE"

        return {
            "target_identity": target_name,
            "role_weight_factor": role_weight,
            "exposure_risk_index": round(exposure_index, 4),
            "threat_alert_level": alert_level,
            "action_guideline": self._get_action_guideline(alert_level),
            "checked_at": time.time()
        }

    def _get_action_guideline(self, alert_level: str) -> str:
        guidelines = {
            "CRITICAL_COMPROMISE": "CEO spoofing matched. Lock credential tokens, deploy takedown alerts, and verify signatures.",
            "HIGH_COMPROMISE_WARNING": "Alert communication channels. Verify all outbound corporate videos.",
            "MEDIUM_COMPROMISE": "Review media parameters. Log incident inside standard operations dashboard.",
            "INFORMATIONAL": "No high-profile spoofing patterns. System monitoring stable."
        }
        return guidelines.get(alert_level, "Log and monitor.")
