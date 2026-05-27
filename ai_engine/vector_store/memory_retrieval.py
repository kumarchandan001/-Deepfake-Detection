from typing import List, Dict, Any
from ai_engine.vector_store.semantic_search import SemanticSearchManager
from ai_engine.utils.logger import setup_logger

logger = setup_logger("memory_retrieval")

class MemoryContextRetriever:
    """
    Forensic Memory Context Retriever.
    Searches the semantic vector index for historical incidents matching the query case,
    structuring context blocks to inform active agent reasoning.
    """
    def __init__(self, search_manager: Optional[SemanticSearchManager] = None):
        self.search_manager = search_manager or SemanticSearchManager()

    def retrieve_investigation_context(self, current_summary: str) -> str:
        """
        Queries historical deepfakes cases and returns formatted context text lines 
        for insertion into LLM reasoning loops.
        """
        logger.info("Retrieving historic incident context for reasoning loop...")
        
        matches = self.search_manager.query_similar_incidents(current_summary, limit=2)
        if not matches:
            return "No matching historical deepfake incidents recorded in standard vector database stores."

        context_blocks = []
        context_blocks.append("--- RETRIEVED HISTORICAL INCIDENT CONTEXTS ---")
        
        for idx, item in enumerate(matches):
            context_blocks.append(
                f"Incident Match {idx+1} [Case ID: {item['case_id']}]:\n"
                f"- Verdict: {item['verdict']}\n"
                f"- Case Briefing: {item['summary']}\n"
                f"- Semantic Similarity Index: {item['semantic_similarity_coefficient']:.4f}\n"
            )
            
        context_blocks.append("---------------------------------------------")
        return "\n".join(context_blocks)
from typing import Optional
