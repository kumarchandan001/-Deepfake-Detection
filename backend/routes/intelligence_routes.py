from fastapi import APIRouter, status, HTTPException
from typing import Dict, Any, List
from ai_engine.intelligence.campaign_tracker import CampaignTracker
from ai_engine.vector_store.semantic_search import SemanticSearchManager
from ai_engine.utils.logger import setup_logger

logger = setup_logger("intelligence_routes")
router = APIRouter(prefix="/api/v1/intelligence", tags=["Threat Intelligence Operations"])

# Singleton instances configuration
campaign_engine = CampaignTracker()
search_manager = SemanticSearchManager()

# Fill dummy campaign data to verify integration out of the box
campaign_engine.register_case_to_campaign(
    case_id="case_sample_01",
    actor_account="actor_suspicious_bot",
    asset_fingerprint="ff8811eef0021",
    verdict="MANIPULATED",
    confidence=96.40
)

@router.get("/graph", status_code=status.HTTP_200_OK)
async def get_threat_campaign_graph() -> Dict[str, Any]:
    """
    Returns D3-compliant node-link JSON structures representing active coordinated campaign graphs.
    """
    logger.info("Serving topological threat campaign graph logs...")
    try:
        return campaign_engine.threat_graph.serialize_to_json_format()
    except Exception as e:
        logger.error(f"Failed to serialize threat graph: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Topological graph serialization failed: {str(e)}"
        )

@router.get("/campaign/{campaign_id}", status_code=status.HTTP_200_OK)
async def get_campaign_profile(campaign_id: str) -> Dict[str, Any]:
    """
    Retrieves active briefing dossier for a coordinated misinformation cluster ID.
    """
    logger.info(f"Retrieving profile briefs for campaign: {campaign_id}")
    brief = campaign_engine.get_campaign_briefing(campaign_id)
    if "error" in brief:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=brief["error"]
        )
    return brief

@router.get("/semantic-search", status_code=status.HTTP_200_OK)
async def query_similar_case_incidents(query: str, limit: int = 3) -> List[Dict[str, Any]]:
    """
    Performs natural language semantic search across historical verified case archives.
    """
    logger.info(f"Executing semantic index search query: '{query}'")
    try:
        # Save a sample index first if database index is empty
        if not search_manager.vector_db.metadata_store:
            search_manager.index_case_report(
                case_id="case_sample_01",
                summary_text="CEO voice clone deepfake bypass attempt targeting secure wire transfer networks.",
                verdict="MANIPULATED"
            )
            
        return search_manager.query_similar_incidents(query, limit=limit)
    except Exception as e:
        logger.error(f"Semantic search query failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Semantic memory search query failure: {str(e)}"
        )
