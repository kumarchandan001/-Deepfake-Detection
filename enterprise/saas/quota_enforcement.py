import time
from typing import Dict, Any, Tuple, Optional
from ai_engine.utils.logger import setup_logger
from enterprise.saas.plan_registry import PlanRegistry
from enterprise.saas.subscription_manager import SubscriptionManager
from enterprise.saas.usage_tracking import UsageTracker

logger = setup_logger("quota_enforcement")

class QuotaExceededException(Exception):
    def __init__(self, message: str, retry_after: int = 60):
        super().__init__(message)
        self.retry_after = retry_after
        self.message = message

class QuotaEnforcer:
    _instance: Optional["QuotaEnforcer"] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(QuotaEnforcer, cls).__new__(cls, *args, **kwargs)
            cls._instance.registry = PlanRegistry()
            cls._instance.subscriptions = SubscriptionManager()
            cls._instance.tracker = UsageTracker()
            # Token bucket registry: tenant_id -> (tokens, last_update)
            cls._instance._token_buckets: Dict[str, Tuple[float, float]] = {}
        return cls._instance

    async def verify_request(self, tenant_id: str, requested_feature: Optional[str] = None) -> bool:
        """
        Main validation gateway verifying subscription standing, features, daily/monthly quotas,
        and rates. Raises QuotaExceededException if checked rules fail.
        """
        # 1. Fetch Tenant Subscription
        state = await self.subscriptions.get_subscription(tenant_id)
        plan_key = state.plan_key
        plan = self.registry.get_plan(plan_key)
        
        if not plan:
            raise QuotaExceededException(f"No valid plan schema matched for key: {plan_key}")

        # 2. Check Subscription Standing Status
        if state.status not in ["active", "trialing"]:
            raise QuotaExceededException(f"Subscription status is '{state.status}'. Access denied.")

        # 3. Check Feature Authorization
        if requested_feature and not self.registry.is_feature_allowed(plan_key, requested_feature):
            raise QuotaExceededException(
                f"Feature '{requested_feature}' is not enabled in plan tier: {plan.pricing.name}"
            )

        # 4. Check Rate Limits (Token Bucket Rate Limiter)
        await self._enforce_rate_limit(tenant_id, plan.limits.concurrent_request_limit)

        # 5. Check Daily / Monthly Quotas
        daily_usage = await self.tracker.get_usage(tenant_id, "daily_checks")
        monthly_usage = await self.tracker.get_usage(tenant_id, "monthly_checks")

        if daily_usage >= plan.limits.daily_quota:
            raise QuotaExceededException(
                f"Daily API request limit reached ({daily_usage}/{plan.limits.daily_quota})."
            )

        if monthly_usage >= plan.limits.monthly_quota:
            # Enterprise plans support metered billing overages
            if plan_key == "enterprise":
                logger.info(f"Enterprise tenant {tenant_id} exceeded baseline monthly quota. Allowing metered overage.")
                await self.tracker.increment_usage(tenant_id, "monthly_overage_checks")
            else:
                raise QuotaExceededException(
                    f"Monthly API request limit reached ({monthly_usage}/{plan.limits.monthly_quota}). Upgrade tier to continue."
                )

        # 6. Increment usages
        await self.tracker.increment_usage(tenant_id, "daily_checks")
        await self.tracker.increment_usage(tenant_id, "monthly_checks")
        
        return True

    async def _enforce_rate_limit(self, tenant_id: str, limit: int):
        """
        Implements high-performance token-bucket rate limiter.
        """
        now = time.time()
        bucket = self._token_buckets.get(tenant_id)

        if not bucket:
            # First request initialize bucket fully
            self._token_buckets[tenant_id] = (float(limit), now)
            return

        tokens, last_update = bucket
        # Refill tokens proportional to elapsed time (e.g. refill full bucket over 60 seconds)
        elapsed = now - last_update
        refill_rate = limit / 60.0  # refill entire allowance every minute
        new_tokens = min(float(limit), tokens + elapsed * refill_rate)

        if new_tokens < 1.0:
            retry_after = int(max(1.0, (1.0 - new_tokens) / refill_rate))
            logger.warning(f"Rate limit hit for tenant: {tenant_id}. Tokens remaining: {new_tokens:.2f}")
            raise QuotaExceededException(
                f"Rate limit exceeded. Concurrent limit: {limit} requests.", 
                retry_after=retry_after
            )

        # Deduct token
        self._token_buckets[tenant_id] = (new_tokens - 1.0, now)
