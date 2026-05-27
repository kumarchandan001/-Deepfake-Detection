import asyncio
from typing import List, Dict, Any, Coroutine
from ai_engine.utils.logger import setup_logger

logger = setup_logger("async_coordinator")

class AsyncCoordinator:
    """
    Asynchronous Forensic Event Coordinator.
    Manages non-blocking concurrent scheduling, maps async tasks,
    and coordinates parallel event executions across cluster nodes.
    """
    @staticmethod
    async def schedule_concurrent_investigations(tasks: List[Coroutine]) -> List[Any]:
        """
        Gathers and executes multiple asynchronous task coroutines concurrently.
        
        Args:
            tasks: List of awaitable coroutine pipelines.
            
        Returns:
            List containing aggregated results from all completed coroutines.
        """
        logger.info(f"Async coordinator scheduling {len(tasks)} parallel forensic investigations...")
        
        try:
            # Parallel gathering inside active asyncio event loop
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            logger.info("All scheduled parallel tasks completed.")
            return results
            
        except Exception as e:
            logger.error(f"Async gathering execution failure: {e}")
            raise e
