from fastapi import APIRouter, status, HTTPException
from typing import Dict, Any, Optional
from ai_engine.reporting.severity_scoring import SeverityScorer
from ai_engine.advanced_forensics.visual_consistency import VisualConsistencyAnalyzer
from ai_engine.utils.logger import setup_logger

logger = setup_logger("threat_routes")
router = APIRouter(prefix="/api/v1/threats", tags=["Threat Assessment & Cyber Security"])

@router.get("/severity-score", status_code=status.HTTP_200_OK)
async def calculate_threat_severity_index(
    verdict: str,
    confidence: float,
    is_metadata_modified: bool = False,
    liveness_verified: bool = True,
    source_account: Optional[str] = None
) -> Dict[str, Any]:
    """
    Computes standard cybersecurity threat severity indexes based on multiple forensic findings.
    """
    logger.info("Computing active threat severity score details...")
    try:
        return SeverityScorer.calculate_severity_score(
            verdict=verdict,
            confidence=confidence,
            is_metadata_modified=is_metadata_modified,
            liveness_verified=liveness_verified,
            source_account=source_account
        )
    except Exception as e:
        logger.error(f"Failed to score threat severity: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Threat severity calculator failed: {str(e)}"
        )
