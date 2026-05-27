import time
from typing import Dict, Any, List, Set
from ai_engine.intelligence.threat_graph import ThreatGraph
from ai_engine.utils.logger import setup_logger

logger = setup_logger("campaign_tracker")

class CampaignTracker:
    """
    Coordinated Disinformation Campaign Tracker.
    Binds forensic graph topological profiles to aggregate incident logs,
    providing intelligence tracking over active manipulation networks.
    """
    def __init__(self):
        self.threat_graph = ThreatGraph()
        # Active campaigns tracking cache: {campaign_id: {associated_cases: set, risk_level: str}}
        self.active_campaigns: Dict[str, Dict[str, Any]] = {}

    def register_case_to_campaign(
        self, 
        case_id: str, 
        actor_account: str, 
        asset_fingerprint: str, 
        verdict: str,
        confidence: float
    ) -> str:
        """
        Maps a new verified case to the threat intelligence graph networks 
        and updates coordinated campaign indicators.
        
        Returns:
            Campaign ID token associating the grouped inputs.
        """
        logger.info(f"Campaign Tracker integrating case [{case_id}] into topological network...")
        
        # 1. Update graph structure
        self.threat_graph.add_actor(actor_account, platform="web_stream", risk_score=float(confidence/100.0))
        self.threat_graph.add_media_asset(case_id, file_type="container", verdict=verdict)
        self.threat_graph.add_forensic_finding(f"find_{case_id}", confidence=confidence, anomaly_type=verdict)
        
        # Link graph nodes
        self.threat_graph.link_nodes(actor_account, case_id, relation_type="posted")
        self.threat_graph.link_nodes(case_id, f"find_{case_id}", relation_type="exhibits_anomaly")

        # 2. Cluster campaign nodes topologically
        clusters = self.threat_graph.detect_coordinated_clusters()
        
        campaign_id = "CAMP_STATIC_SWEEP"
        # Find if this case falls inside any clustered subgraph component
        for idx, cluster in enumerate(clusters):
            if case_id in cluster or actor_account in cluster:
                campaign_id = f"CAMP_COORDINATED_{idx:03d}"
                break

        # 3. Cache campaign details in active tracking index
        if campaign_id not in self.active_campaigns:
            self.active_campaigns[campaign_id] = {
                "campaign_id": campaign_id,
                "associated_cases": set(),
                "actors_tracked": set(),
                "status": "active",
                "risk_level": "WARNING",
                "last_updated": time.time()
            }

        campaign = self.active_campaigns[campaign_id]
        campaign["associated_cases"].add(case_id)
        campaign["actors_tracked"].add(actor_account)
        campaign["last_updated"] = time.time()

        # Escalate risk if campaign clusters span multiple files/actors
        if len(campaign["associated_cases"]) >= 3:
            campaign["risk_level"] = "CRITICAL_THREAT"
            logger.critical(f"DISINFORMATION CAMPAIGN DETECTION: Group {campaign_id} has exceeded safe limits!")

        return campaign_id

    def get_campaign_briefing(self, campaign_id: str) -> Dict[str, Any]:
        """
        Returns a structured briefing dossier detailing active misinformation clusters.
        """
        campaign = self.active_campaigns.get(campaign_id)
        if not campaign:
            return {"success": False, "error": "Campaign signature not found."}

        return {
            "campaign_id": campaign_id,
            "threat_risk_level": campaign["risk_level"],
            "cases_linked": list(campaign["associated_cases"]),
            "actors_implicated": list(campaign["actors_tracked"]),
            "is_active": campaign["status"] == "active",
            "last_incident_epoch": campaign["last_updated"]
        }
