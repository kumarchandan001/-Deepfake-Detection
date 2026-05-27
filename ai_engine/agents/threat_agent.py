import time
from typing import Dict, Any, List, Optional
from ai_engine.agents.agent_memory import AgentMemory
from ai_engine.utils.logger import setup_logger

logger = setup_logger("threat_agent")

class ThreatAgent:
    """
    Cyber Threat Intelligence Analyst.
    Correlates forensic anomalies with security parameters to detect misinformation 
    campaigns, calculate severity profiles, and generate cyber-defense advisories.
    """
    def __init__(self, memory: Optional[AgentMemory] = None):
        self.memory = memory or AgentMemory()

    def analyze_threat_severity(self, case_id: str, analysis_verdict: str, confidence: float, source_account: Optional[str] = None) -> Dict[str, Any]:
        """
        Determines cybersecurity threat risk profile of a verified manipulation.
        
        Severity levels:
        - LOW: Real media or extremely low confidence manipulation.
        - MEDIUM: Single isolated audio/image deepfake without campaign indicators.
        - HIGH: Video/multimodal manipulation with targeting profiles.
        - CRITICAL: Coordinated campaign vectors targeting key networks.
        """
        logger.info(f"Threat Agent evaluating severity parameters for case [{case_id}]...")
        self.memory.record_observation(case_id, "ThreatAgent", "Initiating cybersecurity severity assessment...")

        is_fake = analysis_verdict in ["FAKE", "MANIPULATED", "FAKE_VOICE"]
        
        severity = "LOW"
        risk_score = 0.0
        indicators = []

        if is_fake:
            risk_score = float(confidence / 100.0)
            
            if analysis_verdict == "FAKE_VOICE":
                severity = "MEDIUM"
                indicators.append("Vocal synthesizer cloning matches.")
            elif analysis_verdict == "MANIPULATED":
                severity = "HIGH"
                indicators.append("High-capacity visual/acoustic decision fusion splicing.")
            else:
                severity = "MEDIUM"
                indicators.append("Spatial convolutional attributions manipulation.")
                
            # Escalate severity if source targets specific operational parameters
            if source_account:
                severity = "CRITICAL"
                risk_score = max(risk_score, 0.95)
                indicators.append(f"Targeted dissemination origin tracked to high-risk account: {source_account}")
        else:
            indicators.append("Organic media verification matching.")

        report = {
            "case_id": case_id,
            "threat_severity": severity,
            "risk_score": round(risk_score, 4),
            "threat_indicators": indicators,
            "actionable_defense_advisory": self._get_actionable_advisory(severity),
            "timestamp": time.time()
        }

        self.memory.record_observation(
            case_id, 
            "ThreatAgent", 
            f"Threat assessment compiled. Severity={severity}, Score={risk_score:.2f}"
        )
        return report

    def _get_actionable_advisory(self, severity: str) -> str:
        """
        Retrieves tailored cybersecurity defense rules.
        """
        advisories = {
            "LOW": "Media matches authentic footprints. Continue routine monitoring sweeps.",
            "MEDIUM": "Flag asset internally. Monitor distribution trajectories across indexing networks.",
            "HIGH": "Deploy visual explainability attributions. Prepare secure takedown advisories.",
            "CRITICAL": "Initiate high-priority incident warnings. Alert security operations (SOC) and apply cryptographic blocks."
        }
        return advisories.get(severity, "Monitor and log.")
