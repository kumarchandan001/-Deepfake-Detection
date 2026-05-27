import time
import uuid
from typing import Dict, Any, List, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("timeline_engine")

class ForensicTimelineEngine:
    _instance: Optional["ForensicTimelineEngine"] = None
    
    # Store chronologies: case_id -> list of TimelineEntry dicts
    _timeline_vault: Dict[str, List[Dict[str, Any]]] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ForensicTimelineEngine, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    async def log_timeline_event(
        self, 
        case_id: str, 
        event_type: str,  # e.g., EVIDENCE_UPLOADED, CLASSIFICATION_RUN, CUSTODY_TRANSFERRED, NOTE_ADDED
        actor_id: str, 
        summary: str,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Appends a chronological audit event log entry to a case workspace timeline.
        """
        logger.info(f"Chronology update: Case={case_id}, Type={event_type}, Msg='{summary}'")
        
        entry = {
            "entry_id": f"tle_{uuid.uuid4().hex[:12]}",
            "timestamp": time.time(),
            "event_type": event_type,
            "actor_id": actor_id,
            "summary": summary,
            "metadata": metadata or {}
        }

        if case_id not in self._timeline_vault:
            self._timeline_vault[case_id] = []
            
        self._timeline_vault[case_id].append(entry)
        
        # Sort by timestamp to ensure chronological order
        self._timeline_vault[case_id].sort(key=lambda x: x["timestamp"])
        return entry

    def get_case_timeline(self, case_id: str) -> List[Dict[str, Any]]:
        """
        Gets timeline entries.
        """
        return self._timeline_vault.get(case_id, [])

    async def clear_case_timeline(self, case_id: str) -> None:
        """
        Resets timeline logs.
        """
        if case_id in self._timeline_vault:
            self._timeline_vault[case_id].clear()
            logger.info(f"Cleared chronology workspace vault for case: {case_id}")
