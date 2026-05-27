import time
from typing import Dict, Any, List, Optional
from ai_engine.utils.logger import setup_logger
from enterprise.saas.plan_registry import PlanRegistry
from enterprise.saas.subscription_manager import SubscriptionManager
from enterprise.saas.usage_tracking import UsageTracker

logger = setup_logger("billing_engine")

class BillingEngine:
    _instance: Optional["BillingEngine"] = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(BillingEngine, cls).__new__(cls, *args, **kwargs)
            cls._instance.registry = PlanRegistry()
            cls._instance.subscriptions = SubscriptionManager()
            cls._instance.tracker = UsageTracker()
        return cls._instance

    async def calculate_current_bill(self, tenant_id: str) -> Dict[str, Any]:
        """
        Computes current period charges based on base subscriptions and metered resource overages.
        """
        state = await self.subscriptions.get_subscription(tenant_id)
        plan = self.registry.get_plan(state.plan_key)
        
        if not plan:
            return {"error": "No valid plan configured"}

        base_price_cents = plan.pricing.price_cents
        overage_cents = 0
        overage_count = 0
        
        # Pull metered counts
        monthly_checks = await self.tracker.get_usage(tenant_id, "monthly_checks")
        overage_checks = await self.tracker.get_usage(tenant_id, "monthly_overage_checks")

        # Compile overages
        if state.plan_key == "enterprise" and overage_checks > 0:
            overage_count = overage_checks
            overage_cents = overage_count * plan.pricing.metered_overage_price_cents
        elif monthly_checks > plan.limits.monthly_quota:
            overage_count = monthly_checks - plan.limits.monthly_quota
            overage_cents = overage_count * plan.pricing.metered_overage_price_cents

        total_cents = base_price_cents + overage_cents

        return {
            "tenant_id": tenant_id,
            "plan_key": state.plan_key,
            "plan_name": plan.pricing.name,
            "base_price_dollars": base_price_cents / 100.0,
            "metered_checks_run": monthly_checks,
            "quota_limit": plan.limits.monthly_quota,
            "overage_checks_count": overage_count,
            "overage_charge_dollars": overage_cents / 100.0,
            "total_charge_dollars": total_cents / 100.0,
            "billing_period_end": state.current_period_end
        }

    async def compile_monthly_invoice(self, tenant_id: str) -> Dict[str, Any]:
        """
        Produces detailed historical invoice statements for records.
        """
        bill = await self.calculate_current_bill(tenant_id)
        invoice_id = f"inv_{tenant_id}_{int(time.time())}"
        
        invoice_data = {
            "invoice_id": invoice_id,
            "issued_at": int(time.time()),
            "tenant_id": tenant_id,
            "details": bill,
            "payment_status": "pending",
            "receipt_url": None
        }
        
        # Proactively attempt Stripe gateway payment mock processing if it's not a free plan
        if bill["total_charge_dollars"] > 0:
            logger.info(f"Simulating collection charge of ${bill['total_charge_dollars']} for Invoice: {invoice_id}")
            invoice_data["payment_status"] = "paid"
            invoice_data["receipt_url"] = f"https://stripe.com/receipts/mock/{invoice_id}"
        else:
            invoice_data["payment_status"] = "settled_zero_balance"

        logger.info(f"Generated monthly invoice for Tenant {tenant_id}: {invoice_id}, Status={invoice_data['payment_status']}")
        return invoice_data
