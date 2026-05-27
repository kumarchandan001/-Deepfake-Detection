from typing import Dict, Any
from ai_engine.utils.logger import setup_logger
from enterprise.saas.billing_engine import BillingEngine
from enterprise.saas.subscription_manager import SubscriptionManager

logger = setup_logger("billing_service")

class BillingService:
    def __init__(self):
        self.engine = BillingEngine()
        self.manager = SubscriptionManager()

    async def get_tenant_billing_status(self, tenant_id: str) -> Dict[str, Any]:
        """
        Gets current plan billing and metered totals.
        """
        try:
            logger.info(f"Retrieving current plan billing calculation status for: {tenant_id}")
            return await self.engine.calculate_current_bill(tenant_id)
        except Exception as e:
            logger.error(f"Error calculating bill for tenant {tenant_id}: {e}")
            raise ValueError(f"Failed to fetch billing status: {e}")

    async def trigger_invoice_generation(self, tenant_id: str) -> Dict[str, Any]:
        """
        Compiles and bills current outstanding balances on Stripe.
        """
        try:
            logger.info(f"Triggering monthly usage cycle rollup invoice for: {tenant_id}")
            return await self.engine.compile_monthly_invoice(tenant_id)
        except Exception as e:
            logger.error(f"Error compiling invoice for tenant {tenant_id}: {e}")
            raise ValueError(f"Invoice compiling failed: {e}")

    async def upgrade_tenant_plan(self, tenant_id: str, email: str, plan_key: str) -> Dict[str, Any]:
        """
        Executes plan upgrade transition operations.
        """
        try:
            logger.info(f"Transitioning tenant {tenant_id} subscription plan key to: {plan_key}")
            return await self.manager.create_tenant_subscription(tenant_id, email, plan_key)
        except Exception as e:
            logger.error(f"Upgrade failed for tenant {tenant_id} to plan {plan_key}: {e}")
            raise ValueError(f"Plan upgrade failed: {e}")

    async def cancel_tenant_plan(self, tenant_id: str) -> Dict[str, Any]:
        """
        Cancels active subscriptions.
        """
        try:
            logger.info(f"Cancelling active plan subscription tier for tenant: {tenant_id}")
            state = await self.manager.cancel_tenant_subscription(tenant_id)
            return {"status": "success", "new_state": state}
        except Exception as e:
            logger.error(f"Cancellation failed for tenant {tenant_id}: {e}")
            raise ValueError(f"Cancellation failed: {e}")
