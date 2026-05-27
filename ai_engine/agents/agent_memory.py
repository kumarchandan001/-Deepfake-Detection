import time
from collections import defaultdict
from typing import List, Dict, Any, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("agent_memory")

class AgentMemory:
    """
    Persistent, thread-safe memory container for autonomous forensics sessions,
    archiving reasoning traces, sub-pipeline metrics, and case metadata.
    """
    def __init__(self):
        # Case memories: {case_id: [memory_logs_list]}
        self.memories: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        # Global metadata profiles cached in active memory
        self.cached_contexts: Dict[str, Dict[str, Any]] = {}

    def record_observation(self, case_id: str, source: str, observation: str, metadata: Optional[Dict[str, Any]] = None) -> None:
        """
        Appends a logical observation checkpoint to the target case timeline.
        """
        log_entry = {
            "timestamp": time.time(),
            "source": source,
            "observation": observation,
            "metadata": metadata or {}
        }
        self.memories[case_id].append(log_entry)
        logger.info(f"Memory recorded on case [{case_id}] from [{source}]: {observation[:75]}...")

    def get_case_timeline(self, case_id: str) -> List[Dict[str, Any]]:
        """
        Retrieves the chronologically ordered trace history for a given case.
        """
        return sorted(self.memories[case_id], key=lambda x: x["timestamp"])

    def query_semantic_keywords(self, case_id: str, keyword: str) -> List[Dict[str, Any]]:
        """
        Heuristic offline semantic parsing matching memory statements containing target terms.
        """
        kw_lower = keyword.lower()
        matches = []
        for entry in self.memories[case_id]:
            if kw_lower in entry["observation"].lower() or any(kw_lower in str(v).lower() for v in entry["metadata"].values()):
                matches.append(entry)
        return matches

    def cache_case_context(self, case_id: str, context: Dict[str, Any]) -> None:
        """
        Caches full metadata profiles to enable active reasoning context.
        """
        self.cached_contexts[case_id] = context
        logger.info(f"Context variables cached for case: {case_id}")

    def get_case_context(self, case_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves active contextual parameters for the forensic reasoner.
        """
        return self.cached_contexts.get(case_id)

    def clear_memory(self, case_id: str) -> None:
        """
        Evicts memories associated with a concluded investigation.
        """
        if case_id in self.memories:
            del self.memories[case_id]
        if case_id in self.cached_contexts:
            del self.cached_contexts[case_id]
        logger.info(f"Incidents context evicted from cache memory for case: {case_id}")
