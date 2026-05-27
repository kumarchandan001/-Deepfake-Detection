import networkx as nx
from typing import Dict, Any, List
from ai_engine.utils.logger import setup_logger

logger = setup_logger("threat_graph")

class ThreatGraph:
    """
    Topological Campaign Threat Graph Engine.
    Correlates actor profiles, fake assets, and forensic classifications
    using directed graphs to analyze coordinated misinformation structures.
    """
    def __init__(self):
        # Create a directed NetworkX graph instance
        self.graph = nx.DiGraph()
        logger.info("ThreatGraph engine initialized successfully.")

    def add_actor(self, account_id: str, platform: str, risk_score: float = 0.0) -> None:
        """
        Adds a profile/account node to the campaign graph.
        """
        self.graph.add_node(
            account_id, 
            type="actor", 
            platform=platform, 
            risk_score=risk_score,
            label=f"Actor: {account_id}"
        )
        logger.debug(f"Graph node added [actor]: {account_id}")

    def add_media_asset(self, asset_id: str, file_type: str, verdict: str) -> None:
        """
        Adds an analyzed media asset node to the graph.
        """
        self.graph.add_node(
            asset_id, 
            type="media", 
            file_type=file_type, 
            verdict=verdict,
            label=f"Asset: {asset_id}"
        )
        logger.debug(f"Graph node added [media]: {asset_id}")

    def add_forensic_finding(self, finding_id: str, confidence: float, anomaly_type: str) -> None:
        """
        Adds a classified forensic marker node to the graph.
        """
        self.graph.add_node(
            finding_id,
            type="finding",
            confidence=confidence,
            anomaly_type=anomaly_type,
            label=f"Finding: {anomaly_type}"
        )
        logger.debug(f"Graph node added [finding]: {finding_id}")

    def link_nodes(self, source_id: str, target_id: str, relation_type: str) -> None:
        """
        Builds a directed connection edge mapping node-to-node linkages.
        Relations: 'posted_by', 'referenced_in', 'exhibits_anomaly'.
        """
        if self.graph.has_node(source_id) and self.graph.has_node(target_id):
            self.graph.add_edge(source_id, target_id, relation=relation_type)
            logger.debug(f"Graph edge compiled: {source_id} -({relation_type})-> {target_id}")
        else:
            logger.warning(f"Failed to build link: Source [{source_id}] or Target [{target_id}] missing.")

    def detect_coordinated_clusters(self) -> List[List[str]]:
        """
        Identifies isolated subgraphs/connected nodes representing coordinated campaigns.
        """
        # Convert to undirected copy to search standard connected components
        undirected_graph = self.graph.to_undirected()
        components = list(nx.connected_components(undirected_graph))
        
        # Filter clusters with 3 or more related nodes (indicates coordinated campaign vectors)
        campaign_clusters = [list(c) for c in components if len(c) >= 3]
        logger.info(f"Topological scans completed. Campaign clusters identified: {len(campaign_clusters)}")
        return campaign_clusters

    def serialize_to_json_format(self) -> Dict[str, Any]:
        """
        Serializes NetworkX DiGraph representation into standard D3-compliant node-link JSONs.
        """
        nodes = []
        links = []

        for node_id, attrs in self.graph.nodes(data=True):
            node_data = {"id": node_id}
            node_data.update(attrs)
            nodes.append(node_data)

        for source, target, attrs in self.graph.edges(data=True):
            links.append({
                "source": source,
                "target": target,
                "relation": attrs.get("relation", "linked")
            })

        return {
            "nodes": nodes,
            "links": links
        }
