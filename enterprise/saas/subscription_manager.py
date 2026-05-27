import time
from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger
from enterprise.saas.pricing_models import TenantSubscriptionState
from enterprise.saas.plan_registry import PlanRegistry
from enterprise.saas.stripe_gateway import StripeGateway

logger = setup_logger("subscription_manager")

class SubscriptionManager:
    _instance: Optional["SubscriptionManager"] = None
    # Thread-safe in-memory cache fallback for testing/dev if DB tables aren't setup
    _subscriptions_cache: Dict[str, TenantSubscriptionState] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(SubscriptionManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.gateway = StripeGateway()
            cls._instance.registry = PlanRegistry()
        return cls._instance

    async def get_subscription(self, tenant_id: str) -> TenantSubscriptionState:
        """
        Retrieves active subscription state for tenant.
        """
        if tenant_id in self._subscriptions_cache:
            return self._subscriptions_cache[tenant_id]
        
        # Default fallback to Developer Free Tier
        now = time.time()
        state = TenantSubscriptionState(
            tenant_id=tenant_id,
            plan_key="free",
            status="active",
            current_period_start=now,
            current_period_end=now + 30 * 86400,
            cancel_at_period_end=False,
            usage_this_period=0
        )
        self._subscriptions_cache[tenant_id] = state
        logger.info(f"Initialized default FREE subscription for tenant: {tenant_id}")
        return state

    async def update_subscription_cache(self, state: TenantSubscriptionState):
        self._subscriptions_cache[state.tenant_id] = state
        logger.info(f"Updated subscription cache for tenant {state.tenant_id}: Plan={state.plan_key}, Status={state.status}")

    async def create_tenant_subscription(self, tenant_id: str, email: str, plan_key: str) -> Dict[str, Any]:
        """
        Registers a customer on Stripe and subscribes them to a target plan.
        """
        plan = self.registry.get_plan(plan_key)
        if not plan:
            raise ValueError(f"Plan structure '{plan_key}' does not exist in registry catalog.")

        logger.info(f"Initiating subscription for Tenant: {tenant_id}, Plan={plan_key}")
        
        # 1. Create Customer
        customer = await self.gateway.create_customer(
            name=f"Tenant_{tenant_id}",
            email=email,
            tenant_id=tenant_id
        )
        
        # 2. Create Subscription
        stripe_sub = await self.gateway.create_subscription(
            customer_id=customer["id"],
            price_id=plan.pricing.stripe_price_id
        )
        
        # 3. Compile local representation
        state = TenantSubscriptionState(
            tenant_id=tenant_id,
            plan_key=plan_key,
            status=stripe_sub["status"],
            stripe_subscription_id=stripe_sub["id"],
            current_period_start=stripe_sub["current_period_start"],
            current_period_end=stripe_sub["current_period_end"],
            cancel_at_period_end=stripe_sub["cancel_at_period_end"],
            usage_this_period=0
        )
        
        await self.update_subscription_cache(state)
        return {
            "stripe_customer_id": customer["id"],
            "stripe_subscription_id": stripe_sub["id"],
            "subscription_state": state
        }

    async def cancel_tenant_subscription(self, tenant_id: str) -> TenantSubscriptionState:
        """
        Terminates the subscription for tenant.
        """
        state = await self.get_subscription(tenant_id)
        if not state.stripe_subscription_id:
            logger.warning(f"Tenant {tenant_id} is on non-Stripe plan. Standardizing cancel locally.")
            state.status = "canceled"
            await self.update_subscription_cache(state)
            return state

        stripe_sub = await self.gateway.cancel_subscription(state.stripe_subscription_id)
        state.status = stripe_sub["status"]
        await self.update_subscription_cache(state)
        return state

    async def handle_stripe_webhook(self, payload: bytes, sig_header: str) -> Dict[str, Any]:
        """
        Processes inbound Stripe webhook events (e.g. invoice payment successes, subscriptions updates).
        """
        webhook_secret = self.gateway.settings.get("webhook_secret", "whsec_mock")
        try:
            event = self.gateway.verify_webhook_signature(payload, sig_header, webhook_secret)
            event_type = event.get("type")
            data_object = event.get("data", {}).get("object", {})
            
            logger.info(f"Processing Stripe Webhook event: {event_type}")

            if event_type in ["customer.subscription.created", "customer.subscription.updated"]:
                # Map metadata customer parameters or lookup tenant mapping
                stripe_sub_id = data_object.get("id")
                customer_id = data_object.get("customer")
                status = data_object.get("status")
                price_id = data_object.get("items", {}).get("data", [{}])[0].get("price", {}).get("id")
                
                # Reverse price ID map to extract correct plan key
                plan_key = "free"
                for key, val in self.registry.plans.items():
                    if val.pricing.stripe_price_id == price_id:
                        plan_key = key
                        break

                # Locate cache key via custom lookup or matching tenant
                target_tenant = None
                for tid, sub in self._subscriptions_cache.items():
                    if sub.stripe_subscription_id == stripe_sub_id:
                        target_tenant = tid
                        break
                
                # Mock helper fallback fallback map
                if not target_tenant:
                    target_tenant = f"tenant_{customer_id.split('_')[-1]}" if customer_id else "unknown_tenant"

                now = time.time()
                state = TenantSubscriptionState(
                    tenant_id=target_tenant,
                    plan_key=plan_key,
                    status=status,
                    stripe_subscription_id=stripe_sub_id,
                    current_period_start=data_object.get("current_period_start", now),
                    current_period_end=data_object.get("current_period_end", now + 30 * 86400),
                    cancel_at_period_end=data_object.get("cancel_at_period_end", False),
                    usage_this_period=0
                )
                await self.update_subscription_cache(state)
                return {"status": "success", "tenant_id": target_tenant, "action": "sub_updated"}

            elif event_type == "customer.subscription.deleted":
                stripe_sub_id = data_object.get("id")
                for tid, sub in list(self._subscriptions_cache.items()):
                    if sub.stripe_subscription_id == stripe_sub_id:
                        sub.status = "canceled"
                        await self.update_subscription_cache(sub)
                        return {"status": "success", "tenant_id": tid, "action": "sub_canceled"}

            return {"status": "ignored", "event_type": event_type}
        except Exception as e:
            logger.error(f"Error handling Stripe webhook: {e}")
            raise ValueError(f"Webhook processing error: {e}")
