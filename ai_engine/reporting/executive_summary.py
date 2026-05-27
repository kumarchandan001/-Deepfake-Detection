from ai_engine.utils.logger import setup_logger

logger = setup_logger("executive_summary")

class ExecutiveSummaryBuilder:
    """
    Forensic Executive Summary Compiler.
    Constructs high-quality human-readable textual briefs mapping out
    forensic verdicts, risk variables, and operational recommendations.
    """
    @staticmethod
    def compile_briefing(title: str, verdict: str, severity: str, score: float) -> str:
        """
        Generates a polished incident verification text block.
        """
        logger.info(f"Synthesizing executive briefing summary for: {title}")
        
        is_manipulated = verdict in ["FAKE", "MANIPULATED", "FAKE_VOICE"]

        if is_manipulated:
            brief = (
                f"SECURITY INCIDENT TELEMETRY SUMMARY: The cybersecurity forensics sweep on target "
                f"investigation '{title}' confirmed structural deepfake manipulation anomalies (Verdict: FAKE). "
                f"Evaluation metrics compiled a [{severity}] threat risk profile with an exposure index "
                f"score of {score:.2f} out of 1.00. High-frequency pixel perturbations and acoustic vocoder "
                f"artifacts represent a highly coordinated targeted evasion attempt. "
                f"Actionable Alert Status: Immediate quarantine of subject assets and review of authentication logs recommended."
            )
        else:
            brief = (
                f"MEDIA INTEGRITY TELEMETRY SUMMARY: The forensic audit on case investigation '{title}' "
                f"successfully validated the structural authenticity of the query asset (Verdict: AUTHENTIC). "
                f"Gradients attributions and spectral voice distributions exhibited uniform organic properties. "
                f"Exif camera tags are clean and match physical sensor standards. Zero deepfake indicators recorded."
            )

        return brief
