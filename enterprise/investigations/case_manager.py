import time
import uuid
from typing import Dict, Any, List, Optional
from ai_engine.utils.logger import setup_logger
from backend.db.config import AsyncSessionLocal
from backend.db.models import Investigation

logger = setup_logger("case_manager")

class CaseManager:
    _instance: Optional["CaseManager"] = None
    
    # Fallback storage for local runtime sessions
    # case_id -> CaseMetadata dict
    _cases_db: Dict[str, Dict[str, Any]] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CaseManager, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    async def create_case(
        self, 
        tenant_id: str, 
        title: str, 
        description: str, 
        analyst_id: str
    ) -> Dict[str, Any]:
        """
        Creates a new forensic investigation case.
        """
        case_id = f"case_{uuid.uuid4().hex[:12]}"
        logger.info(f"Creating case: Tenant={tenant_id}, CaseID={case_id}, Title='{title}'")

        # 1. DB integration if database exists
        try:
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    db_case = Investigation(
                        id=case_id,
                        title=title,
                        description=description,
                        analyst_id=analyst_id,
                        status="open"
                    )
                    session.add(db_case)
            logger.info("Case recorded in DB metadata table successfully.")
        except Exception as e:
            logger.warning(f"Database write bypassed (standard local mode): {e}")

        # 2. Local fallback storage
        case_payload = {
            "case_id": case_id,
            "tenant_id": tenant_id,
            "title": title,
            "description": description,
            "analyst_id": analyst_id,
            "status": "open",
            "created_at": time.time(),
            "updated_at": time.time(),
            "evidence_ids": [],
            "collaborators": [analyst_id]
        }
        self._cases_db[case_id] = case_payload
        return case_payload

    async def get_case(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves case metadata.
        """
        return self._cases_db.get(case_id)

    async def update_case_status(self, case_id: str, status: str) -> Dict[str, Any]:
        """
        Updates investigation status (open, under_review, resolved, archived).
        """
        case = await self.get_case(case_id)
        if not case:
            raise ValueError(f"Investigation case {case_id} not located.")

        logger.info(f"Updating case status: CaseID={case_id}, Old={case['status']}, New={status}")
        case["status"] = status
        case["updated_at"] = time.time()
        
        # Sync in DB if possible
        try:
            async with AsyncSessionLocal() as session:
                async with session.begin():
                    db_case = await session.get(Investigation, case_id)
                    if db_case:
                        db_case.status = status
        except Exception:
            pass

        return case

    async def add_collaborator(self, case_id: str, analyst_id: str) -> Dict[str, Any]:
        """
        Grants workspace editing access to another forensic investigator.
        """
        case = await self.get_case(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found.")

        if analyst_id not in case["collaborators"]:
            case["collaborators"].append(analyst_id)
            case["updated_at"] = time.time()
            logger.info(f"Collaborator {analyst_id} associated to case {case_id}.")
        return case

    async def link_evidence_to_case(self, case_id: str, evidence_id: str) -> Dict[str, Any]:
        """
        Associates uploaded media artifacts with the case workspace.
        """
        case = await self.get_case(case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found.")

        if evidence_id not in case["evidence_ids"]:
            case["evidence_ids"].append(evidence_id)
            case["updated_at"] = time.time()
            logger.info(f"Linked Evidence {evidence_id} to case {case_id}.")
        return case

    async def list_cases_for_tenant(self, tenant_id: str) -> List[Dict[str, Any]]:
        """
        Lists all cases owned by a tenant.
        """
        return [c for c in self._cases_db.values() if c["tenant_id"] == tenant_id]
