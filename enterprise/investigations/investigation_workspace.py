import time
from typing import Dict, Any, List, Optional
from ai_engine.utils.logger import setup_logger
from enterprise.investigations.case_manager import CaseManager
from enterprise.investigations.evidence_chain import EvidenceChainOfCustody
from enterprise.investigations.timeline_engine import ForensicTimelineEngine

logger = setup_logger("investigation_workspace")

class InvestigationWorkspace:
    def __init__(self):
        self.cases = CaseManager()
        self.evidence = EvidenceChainOfCustody()
        self.timeline = ForensicTimelineEngine()

    async def get_workspace_snapshot(self, case_id: str) -> Dict[str, Any]:
        """
        Aggregates investigation case details, custody history, and timelines.
        """
        logger.info(f"Gathering full workspace snapshot package for Case: {case_id}")
        
        case = await self.cases.get_case(case_id)
        if not case:
            raise ValueError(f"Investigation workspace case {case_id} does not exist.")

        # Resolve evidence metadata
        evidence_nodes = []
        custody_chains = {}
        for eid in case["evidence_ids"]:
            node = self.evidence.get_evidence_node(eid)
            if node:
                evidence_nodes.append(node)
                custody_chains[eid] = self.evidence.get_custody_history(eid)

        # Resolve timeline chronologies
        timeline_entries = self.timeline.get_case_timeline(case_id)

        workspace_summary = {
            "case_id": case_id,
            "tenant_id": case["tenant_id"],
            "title": case["title"],
            "description": case["description"],
            "status": case["status"],
            "analyst_id": case["analyst_id"],
            "created_at": case["created_at"],
            "updated_at": case["updated_at"],
            "collaborators": case["collaborators"],
            "evidence": evidence_nodes,
            "custody_ledger": custody_chains,
            "chronology_timeline": timeline_entries,
            "generated_at": time.time()
        }

        # Log workspace access milestone
        await self.timeline.log_timeline_event(
            case_id=case_id,
            event_type="WORKSPACE_ACCESSED",
            actor_id=case["analyst_id"],
            summary=f"Workspace accessed and compiled for Case ID: {case_id}."
        )

        return workspace_summary

    async def add_evidence_with_timeline(
        self, 
        case_id: str, 
        filename: str, 
        file_content: bytes, 
        analyst_id: str,
        device_details: str
    ) -> Dict[str, Any]:
        """
        Utility adding evidence and logging events.
        """
        # Register evidence
        node = await self.evidence.register_evidence(
            case_id=case_id,
            filename=filename,
            file_content=file_content,
            analyst_id=analyst_id,
            device_details=device_details
        )
        
        # Link to case metadata
        await self.cases.link_evidence_to_case(case_id, node["evidence_id"])
        
        # Log to timeline
        await self.timeline.log_timeline_event(
            case_id=case_id,
            event_type="EVIDENCE_REGISTERED",
            actor_id=analyst_id,
            summary=f"Registered new forensic evidence: {filename} (Size: {len(file_content)} bytes).",
            metadata={"evidence_id": node["evidence_id"], "sha256": node["sha256_checksum"]}
        )

        return node
