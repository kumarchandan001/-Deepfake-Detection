from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class PlanPricing(BaseModel):
    plan_key: str
    name: str
    stripe_price_id: str
    price_cents: int
    billing_interval: str = "month"
    metered_overage_price_cents: int = 0

class PlanLimits(BaseModel):
    daily_quota: int
    monthly_quota: int
    concurrent_request_limit: int
    compute_queue: str
    gpu_fraction: float
    allowed_features: List[str]

class PlanDefinition(BaseModel):
    pricing: PlanPricing
    limits: PlanLimits

class TenantSubscriptionState(BaseModel):
    tenant_id: str
    plan_key: str
    status: str  # active, trialing, past_due, canceled, unpaid
    stripe_subscription_id: Optional[str] = None
    current_period_start: float
    current_period_end: float
    cancel_at_period_end: bool = False
    usage_this_period: int = 0
