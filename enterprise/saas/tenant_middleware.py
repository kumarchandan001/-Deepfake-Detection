from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from ai_engine.utils.logger import setup_logger
from enterprise.saas.tenant_context import set_tenant_id, set_plan_key, clear_saas_context
from enterprise.saas.subscription_manager import SubscriptionManager

logger = setup_logger("tenant_middleware")

class TenantContextMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.subscriptions = SubscriptionManager()

    async def dispatch(self, request: Request, call_next):
        """
        Extracts tenant identifiers from incoming headers, registering contexts.
        """
        # Read header parameter
        tenant_id = request.headers.get("X-Tenant-ID", "free_default_tenant")
        
        # Verify plan status and associate plan keys
        try:
            state = await self.subscriptions.get_subscription(tenant_id)
            plan_key = state.plan_key
        except Exception:
            plan_key = "free"

        # Register request scope values
        token_tenant = set_tenant_id(tenant_id)
        token_plan = set_plan_key(plan_key)

        logger.info(f"Registered Tenant request context scope: Tenant={tenant_id}, Plan={plan_key}")

        try:
            response = await call_next(request)
            return response
        finally:
            # Prevent greenlet thread leaks by clearing scope values
            clear_saas_context()
            logger.info("Cleared request contextual tenant scopes.")
