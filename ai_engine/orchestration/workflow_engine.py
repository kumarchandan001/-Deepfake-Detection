import time
from typing import Dict, Any, List, Callable
from ai_engine.utils.logger import setup_logger

logger = setup_logger("workflow_engine")

class ForensicWorkflowEngine:
    """
    Forensic Orchestration Workflow Engine.
    Coordinates sequential pipeline transitions and tracks operational states 
    (PENDING, RUNNING, COMPLETED, FAILED) for multi-model verification runs.
    """
    def __init__(self):
        # Case state directories: {case_id: {step_name: {status: str, epoch: float}}}
        self.workflow_states: Dict[str, Dict[str, Any]] = {}

    def initialize_workflow(self, case_id: str, stages: List[str]) -> None:
        """
        Registers structural workflow milestones for a given case.
        """
        self.workflow_states[case_id] = {}
        for stage in stages:
            self.workflow_states[case_id][stage] = {
                "status": "PENDING",
                "epoch": time.time(),
                "details": None
            }
        logger.info(f"Forensic workflow initialized for case [{case_id}] with {len(stages)} stages.")

    def transition_stage(self, case_id: str, stage: str, status: str, details: Optional[str] = None) -> None:
        """
        Transitions a target workflow milestone's operational status.
        """
        if case_id in self.workflow_states and stage in self.workflow_states[case_id]:
            self.workflow_states[case_id][stage]["status"] = status
            self.workflow_states[case_id][stage]["epoch"] = time.time()
            self.workflow_states[case_id][stage]["details"] = details
            logger.info(f"Workflow [{case_id}] -> Stage [{stage}] transitioned to state [{status}]")
        else:
            logger.warning(f"Failed to transition state: Case [{case_id}] or Stage [{stage}] unregistered.")

    def get_workflow_progress(self, case_id: str) -> Dict[str, Any]:
        """
        Returns execution statistics for a given workflow timeline.
        """
        if case_id not in self.workflow_states:
            return {"success": False, "error": "Case unregistered."}
            
        stages = self.workflow_states[case_id]
        total = len(stages)
        completed = sum(1 for s in stages.values() if s["status"] == "COMPLETED")
        failed = sum(1 for s in stages.values() if s["status"] == "FAILED")
        
        progress = (completed / total) * 100.0 if total > 0 else 0.0

        return {
            "case_id": case_id,
            "completion_percentage": round(progress, 2),
            "stages_completed": completed,
            "stages_failed": failed,
            "active_stages": stages
        }
from typing import Optional
