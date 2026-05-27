import uuid
import time
from typing import Dict, Any, List, Optional
from ai_engine.agents.agent_memory import AgentMemory
from ai_engine.agents.forensic_agent import ForensicAgent
from ai_engine.utils.logger import setup_logger

logger = setup_logger("orchestration_agent")

class OrchestrationAgent:
    """
    Master coordinator scheduling parallel media analysis pipelines, 
    monitoring execution statuses, and compiling final case summaries.
    """
    def __init__(self, memory: Optional[AgentMemory] = None):
        self.memory = memory or AgentMemory()
        self.forensic_agent = ForensicAgent(memory=self.memory)
        # Active cases tracking structure: {case_id: {status: str, results: list}}
        self.cases: Dict[str, Dict[str, Any]] = {}

    def create_case(self, title: str) -> str:
        """
        Initializes a new autonomous case space and returns a case ID token.
        """
        case_id = f"case_{uuid.uuid4().hex[:10]}"
        self.cases[case_id] = {
            "title": title,
            "status": "processing",
            "assets": [],
            "results": [],
            "created_at": time.time()
        }
        self.memory.record_observation(case_id, "OrchestrationAgent", f"New autonomous investigation initiated: '{title}'")
        return case_id

    async def add_and_analyze_asset(self, case_id: str, file_path: str) -> Dict[str, Any]:
        """
        Adds a media asset to the active case scope and executes asynchronous forensic reasoning.
        """
        if case_id not in self.cases:
            logger.error(f"Target case id missing: {case_id}")
            return {"success": False, "error": "Case missing."}

        self.cases[case_id]["assets"].append(file_path)
        
        # Dispatch the analysis task to the forensic agent
        self.memory.record_observation(case_id, "OrchestrationAgent", f"Enqueuing asset file for analysis: {file_path}")
        result = await self.forensic_agent.investigate_media(case_id, file_path)
        
        self.cases[case_id]["results"].append(result)
        return result

    def get_case_summary(self, case_id: str) -> Dict[str, Any]:
        """
        Aggregates all findings, chronologies, and sub-pipeline outputs into a unified audit sheet.
        """
        if case_id not in self.cases:
            return {"success": False, "error": "Case id not found."}

        case_info = self.cases[case_id]
        timeline = self.memory.get_case_timeline(case_id)
        
        # Calculate overall verdict by consensus
        verdicts = [res.get("verdict") for res in case_info["results"] if res.get("success")]
        
        overall_verdict = "AUTHENTIC"
        if any(v in ["FAKE", "MANIPULATED", "FAKE_VOICE"] for v in verdicts):
            overall_verdict = "MANIPULATED"
            
        case_info["status"] = "completed"
        
        summary = {
            "case_id": case_id,
            "title": case_info["title"],
            "status": "completed",
            "overall_verdict": overall_verdict,
            "assets_analyzed": len(case_info["assets"]),
            "timeline": timeline,
            "results": case_info["results"]
        }
        
        self.memory.record_observation(case_id, "OrchestrationAgent", f"Case investigation concluded. Verdict={overall_verdict}")
        return summary
