from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_429_TOO_MANY_REQUESTS
from ai_engine.utils.logger import setup_logger
from enterprise.saas.quota_enforcement import QuotaEnforcer, QuotaExceededException

logger = setup_logger("quota_middleware")

class QuotaEnforcementMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.enforcer = QuotaEnforcer()
        # System-level bypass routes (health check, open API metadata, auth)
        self.bypass_paths = [
            "/",
            "/docs",
            "/openapi.json",
            "/api/v1/auth/login",
            "/api/v1/auth/register",
            "/api/v1/saas/webhook"  # Ignore Stripe webhook routes to prevent rate blocks
        ]

    async def dispatch(self, request: Request, call_next):
        """
        Intercepts requests to evaluate plan bounds, throwing 429 errors on breaches.
        """
        path = request.url.path
        is_bypass = False
        for p in self.bypass_paths:
            if p == "/":
                if path == "/":
                    is_bypass = True
                    break
            elif path.startswith(p):
                is_bypass = True
                break

        if is_bypass:
            return await call_next(request)

        # Retrieve active tenant from header
        tenant_id = request.headers.get("X-Tenant-ID", "free_default_tenant")
        
        # Check feature parameters dynamically based on request routing target
        requested_feature = None
        if "/detection" in path:
            requested_feature = "image_detection"
        elif "/video" in path:
            requested_feature = "video_detection"
        elif "/audio" in path:
            requested_feature = "audio_detection"
        elif "/explain" in path:
            requested_feature = "explainable_ai"
        elif "/agent" in path:
            requested_feature = "advanced_forensic_agents"

        try:
            # Enforce limits check
            await self.enforcer.verify_request(tenant_id, requested_feature)
            return await call_next(request)
        except QuotaExceededException as e:
            logger.warning(f"Enforced quota limit rejection on Tenant {tenant_id}: {e.message}")
            return JSONResponse(
                status_code=HTTP_429_TOO_MANY_REQUESTS,
                content={
                    "error": "Quota Exceeded",
                    "detail": e.message,
                    "retry_after_seconds": e.retry_after
                },
                headers={"Retry-After": str(e.retry_after)}
            )
        except Exception as e:
            logger.error(f"Internal evaluation fault inside quota middleware: {e}")
            return await call_next(request)
