import time
from typing import Dict, Any, List
from ai_engine.reporting.executive_summary import ExecutiveSummaryBuilder
from ai_engine.reporting.evidence_compiler import EvidenceCompiler
from ai_engine.reporting.severity_scoring import SeverityScorer
from ai_engine.utils.logger import setup_logger

logger = setup_logger("report_builder")

class ForensicReportBuilder:
    """
    Enterprise AI Forensic Report Builder.
    Integrates sub-reporting blocks (summarizers, scoring nodes, timelines)
    to assemble professional cyber investigation briefs.
    """
    @staticmethod
    def build_case_dossier(
        case_id: str,
        case_title: str,
        media_filename: str,
        verdict: str,
        confidence: float,
        exif_results: Dict[str, Any],
        liveness_results: Dict[str, Any],
        source_account: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Synthesizes modular reports and structures a complete forensic incident portfolio.
        """
        logger.info(f"Report Builder compiling modular incident dossier for case: {case_id}")

        # 1. Compute quantitative threat severity score
        severity_profile = SeverityScorer.calculate_severity_score(
            verdict=verdict,
            confidence=confidence,
            is_metadata_modified=exif_results.get("is_manipulated_metadata", False),
            liveness_verified=liveness_results.get("liveness_verified", True),
            source_account=source_account
        )

        # 2. Compile structured timeline elements
        evidence_portfolio = EvidenceCompiler.compile_forensic_evidence(
            media_filename=media_filename,
            verdict=verdict,
            confidence=confidence,
            exif_profile=exif_results,
            liveness_profile=liveness_results
        )

        # 3. Construct human-readable executive briefing
        executive_brief = ExecutiveSummaryBuilder.compile_briefing(
            title=case_title,
            verdict=verdict,
            severity=severity_profile["severity_level"],
            score=severity_profile["severity_score"]
        )

        dossier = {
            "dossier_id": f"DOS_{case_id}_{int(time.time())}",
            "case_id": case_id,
            "case_title": case_title,
            "executive_summary": executive_brief,
            "aggregate_verdict": verdict,
            "confidence": confidence,
            "severity_profile": severity_profile,
            "evidence_portfolio": evidence_portfolio,
            "compiled_epoch": time.time()
        }

        logger.info("Forensic case dossier compiled successfully.")
        return dossier
from typing import Optional
