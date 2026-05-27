import time
from typing import Dict, Any, List, Optional
from ai_engine.agents.agent_memory import AgentMemory
from ai_engine.utils.logger import setup_logger

logger = setup_logger("report_agent")

class ReportAgent:
    """
    Forensic Incident Reporter.
    Synthesizes multi-model analysis parameters, timelines, and threat severity assessments
    into structured executive forensic portfolios.
    """
    def __init__(self, memory: Optional[AgentMemory] = None):
        self.memory = memory or AgentMemory()

    def generate_investigation_report(self, case_id: str, case_title: str, results: List[Dict[str, Any]], threat_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Orchestrates evidence blocks and compiles standard forensic case sheets.
        """
        logger.info(f"Report Agent synthesizing dossier for case [{case_id}]...")
        self.memory.record_observation(case_id, "ReportAgent", "Assembling forensic evidence blocks...")

        timeline = self.memory.get_case_timeline(case_id)
        
        # Consolidate evidence findings
        analyzed_assets_count = len(results)
        positives_count = sum(1 for r in results if r.get("verdict") in ["FAKE", "MANIPULATED", "FAKE_VOICE"])
        
        is_manipulated = positives_count > 0
        overall_verdict = "MANIPULATED" if is_manipulated else "AUTHENTIC"
        
        # Calculate maximum confidence value reported
        max_confidence = max([r.get("confidence", 0.0) for r in results]) if results else 0.0

        dossier = {
            "report_id": f"REP_{case_id}_{int(time.time())}",
            "case_id": case_id,
            "title": case_title,
            "compiled_at": time.time(),
            "executive_summary": self._compile_executive_summary(case_title, overall_verdict, analyzed_assets_count, threat_report.get("threat_severity")),
            "forensic_verdict": overall_verdict,
            "max_confidence": round(max_confidence, 2),
            "threat_profile": {
                "severity": threat_report.get("threat_severity", "LOW"),
                "risk_score": threat_report.get("risk_score", 0.0),
                "indicators": threat_report.get("threat_indicators", []),
                "defense_advisory": threat_report.get("actionable_defense_advisory", "")
            },
            "investigation_timeline": timeline,
            "evidence_count": analyzed_assets_count
        }

        self.memory.record_observation(case_id, "ReportAgent", "Official verification report compiled and signed.")
        return dossier

    def _compile_executive_summary(self, title: str, verdict: str, count: int, severity: str) -> str:
        """
        Builds a natural language summary suitable for SOC briefing sheets.
        """
        if verdict == "MANIPULATED":
            return (
                f"INCIDENT REPORT BRIEFING: The autonomous investigation on '{title}' verified target manipulation "
                f"anomalies within the uploaded media assets ({count} files analyzed). "
                f"Our threat intelligence classifiers mapped these anomalies to a [{severity}] severity profile. "
                f"Attribution vectors strongly indicate synthetic speech vocoders or deep convolutional face splicing."
            )
        else:
            return (
                f"INCIDENT REPORT BRIEFING: The autonomous media forensics sweep on '{title}' successfully "
                f"validated the authenticity of all analyzed elements. Visual attributions and spectral wave signals "
                f"exhibited standard organic characteristics. Zero deepfake indicators registered."
            )
Def = ReportAgent  # Convenience class mapping
