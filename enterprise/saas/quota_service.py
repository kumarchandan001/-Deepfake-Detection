from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger
from enterprise.saas.quota_enforcement import QuotaEnforcer, QuotaExceededException
from enterprise.saas.usage_tracking import UsageTracker
from enterprise.saas.subscription_manager import SubscriptionManager
from enterprise.saas.plan_registry import PlanRegistry

logger = setup_logger("quota_service")

class QuotaService:
    def __init__(self):
        self.enforcer = QuotaEnforcer()
        self.tracker = UsageTracker()
        self.subscriptions = SubscriptionManager()
        self.registry = PlanRegistry()

    async def validate_request_access(self, tenant_id: str, feature: Optional[str] = None) -> bool:
        """
        Business service validation method to check quota bounds.
        Raises QuotaExceededException on breaches.
        """
        logger.info(f"Checking request quota authorization for Tenant: {tenant_id}, Feature={feature}")
        return await self.enforcer.verify_request(tenant_id, feature)

    async def get_tenant_quota_telemetry(self, tenant_id: str) -> Dict[str, Any]:
        """
        Gathers live utilization and limit counts for a tenant.
        """
        state = await self.subscriptions.get_subscription(tenant_id)
        plan = self.registry.get_plan(state.plan_key)
        
        if not plan:
            raise ValueError(f"No plan settings located for tenant plan: {state.plan_key}")

        daily_usage = await self.tracker.get_usage(tenant_id, "daily_checks")
        monthly_usage = await self.tracker.get_usage(tenant_id, "monthly_checks")
        overage_usage = await self.tracker.get_usage(tenant_id, "monthly_overage_checks")

        return {
            "tenant_id": tenant_id,
            "plan_key": state.plan_key,
            "plan_name": plan.pricing.name,
            "usage": {
                "daily_checks": daily_usage,
                "monthly_checks": monthly_usage,
                "monthly_overage_checks": overage_usage
            },
            "limits": {
                "daily_quota": plan.limits.daily_quota,
                "monthly_quota": plan.limits.monthly_quota,
                "concurrent_request_limit": plan.limits.concurrent_request_limit
            },
            "allowed_features": plan.limits.allowed_features
        }

    async def clear_daily_counters(self, tenant_id: str) -> None:
        """
        Resets active daily quota values.
        """
        logger.info(f"Resetting daily counter metrics for Tenant: {tenant_id}")
        await self.tracker.reset_usage(tenant_id, "daily_checks")
