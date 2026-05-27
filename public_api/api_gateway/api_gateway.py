from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger
from backend.routes.public_api_routes import API_KEYS_DB

logger = setup_logger("api_gateway")

class PublicAPIGateway:
    """
    API Gateway layer orchestrating edge checks, key validations, 
    path mappings routing, and access logs analytics forwarding.
    """
    def __init__(self):
        self.active_keys = API_KEYS_DB

    def validate_incoming_request(self, api_key: str, request_path: str) -> Dict[str, Any]:
        """
        Validates request parameters at the gateway level before forwarding to core service threads.
        """
        logger.info(f"Gateway inspecting path request: {request_path}")
        
        tenant_id = self.active_keys.get(api_key)
        if not tenant_id:
            logger.error("API Gateway authorization failure: Invalid key parameter.")
            return {"authorized": False, "error": "Invalid API Key", "status_code": 401}

        # Check path routing mappings
        allowed_paths = [
            "/api/v1/public/verify/image", 
            "/api/v1/public/verify/audio", 
            "/api/v1/public/verify/video"
        ]
        
        if request_path not in allowed_paths:
            logger.error(f"API Gateway path rejection: {request_path}")
            return {"authorized": False, "error": "Resource Not Found", "status_code": 404}

        logger.info(f"API Gateway authorized client request: Tenant={tenant_id}, Resource={request_path}")
        return {
            "authorized": True,
            "tenant_id": tenant_id,
            "target_forward_route": f"http://internal-api-service:8000{request_path}"
        }
