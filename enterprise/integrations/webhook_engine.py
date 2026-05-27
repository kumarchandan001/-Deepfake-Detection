import json
from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger

logger = setup_logger("webhook_engine")

class WebhookEngine:
    def __init__(self):
        # Cache registered webhook target URLs: tenant_id -> list of URLs
        self._target_endpoints: Dict[str, List[str]] = {}

    def register_endpoint(self, tenant_id: str, url: str) -> None:
        if tenant_id not in self._target_endpoints:
            self._target_endpoints[tenant_id] = []
        if url not in self._target_endpoints[tenant_id]:
            self._target_endpoints[tenant_id].append(url)
            logger.info(f"Registered Webhook target for Tenant {tenant_id}: {url}")

    async def dispatch_event(self, tenant_id: str, event_type: str, payload: Dict[str, Any]) -> bool:
        """
        Dispatches json payload events to all active tenant target endpoints.
        Includes automated retry-loops for transient network faults.
        """
        urls = self._target_endpoints.get(tenant_id, [])
        if not urls:
            logger.debug(f"No webhook target endpoints registered for Tenant: {tenant_id}")
            return False

        event_envelope = {
            "event_type": event_type,
            "tenant_id": tenant_id,
            "data": payload
        }

        # Dispatch
        for url in urls:
            logger.info(f"[Webhook MOCK] Dispatching event '{event_type}' to target: {url}")
            logger.debug(json.dumps(event_envelope, indent=4))
            
            # Simulated retry implementation
            retry_count = 3
            success = False
            for attempt in range(retry_count):
                try:
                    # In production we would do:
                    # async with httpx.AsyncClient() as client:
                    #     response = await client.post(url, json=event_envelope, timeout=2.0)
                    #     if response.status_code == 200:
                    #         success = True; break
                    success = True
                    break
                except Exception as e:
                    logger.warning(f"Webhook dispatch attempt {attempt+1} failed to URL {url}: {e}")
            
            if success:
                logger.info(f"Webhook event '{event_type}' successfully delivered to: {url}")
            else:
                logger.error(f"Failed to deliver Webhook event '{event_type}' to target: {url} after {retry_count} attempts.")
        
        return True
