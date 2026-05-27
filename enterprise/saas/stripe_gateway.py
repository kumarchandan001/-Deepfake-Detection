import time
import json
import hmac
import hashlib
from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger
from enterprise.saas.plan_registry import PlanRegistry

logger = setup_logger("stripe_gateway")

class StripeGateway:
    def __init__(self):
        self.registry = PlanRegistry()
        self.settings = self.registry.get_stripe_settings()
        self.use_mock = self.settings.get("use_mock", True)
        self.secret_key = self.settings.get("secret_key", "sk_test_mock")
        
        if not self.use_mock:
            try:
                import stripe
                stripe.api_key = self.secret_key
                self._stripe = stripe
                logger.info("Live Stripe client engine initialized.")
            except ImportError:
                logger.warning("stripe-python library not installed. Defaulting to Mock Stripe engine.")
                self.use_mock = True

        if self.use_mock:
            logger.info("Mock Stripe gateway loaded and verified.")

    async def create_customer(self, name: str, email: str, tenant_id: str) -> Dict[str, Any]:
        if self.use_mock:
            customer_id = f"cus_mock_{hash(tenant_id) & 0xffffffff:08x}"
            logger.info(f"[Stripe MOCK] Created customer: Name={name}, Email={email}, ID={customer_id}")
            return {
                "id": customer_id,
                "name": name,
                "email": email,
                "metadata": {"tenant_id": tenant_id},
                "created": int(time.time())
            }
        else:
            # Synchronous-to-async running in executor
            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: self._stripe.Customer.create(
                    name=name,
                    email=email,
                    metadata={"tenant_id": tenant_id}
                )
            )

    async def create_subscription(self, customer_id: str, price_id: str) -> Dict[str, Any]:
        if self.use_mock:
            subscription_id = f"sub_mock_{int(time.time()):08x}"
            period_start = time.time()
            period_end = period_start + 30 * 86400  # 30 days period
            logger.info(f"[Stripe MOCK] Subscribing customer {customer_id} to price {price_id}. SubscriptionID={subscription_id}")
            return {
                "id": subscription_id,
                "customer": customer_id,
                "status": "active",
                "items": {
                    "data": [{
                        "id": f"si_mock_{int(time.time()):08x}",
                        "price": {"id": price_id}
                    }]
                },
                "current_period_start": int(period_start),
                "current_period_end": int(period_end),
                "cancel_at_period_end": False,
                "created": int(period_start)
            }
        else:
            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: self._stripe.Subscription.create(
                    customer=customer_id,
                    items=[{"price": price_id}],
                    payment_behavior="default_incomplete",
                    expand=["latest_invoice.payment_intent"]
                )
            )

    async def cancel_subscription(self, subscription_id: str) -> Dict[str, Any]:
        if self.use_mock:
            logger.info(f"[Stripe MOCK] Cancelled subscription {subscription_id}")
            return {
                "id": subscription_id,
                "status": "canceled",
                "cancel_at_period_end": False,
                "ended_at": int(time.time())
            }
        else:
            import asyncio
            loop = asyncio.get_event_loop()
            return await loop.run_in_executor(
                None,
                lambda: self._stripe.Subscription.delete(subscription_id)
            )

    def verify_webhook_signature(self, payload: bytes, sig_header: str, webhook_secret: str) -> Dict[str, Any]:
        if self.use_mock:
            # Simulates validation signature header check
            logger.info("[Stripe MOCK] Validating incoming Webhook Signature payload bypass.")
            return json.loads(payload.decode("utf-8"))
        else:
            try:
                event = self._stripe.Webhook.construct_event(
                    payload, sig_header, webhook_secret
                )
                return event
            except Exception as e:
                logger.error(f"Failed to verify Stripe webhook signature: {e}")
                raise ValueError("Invalid Stripe Webhook Signature")

    def generate_mock_signature(self, payload: bytes, secret: str) -> str:
        """
        Helper function to generate a valid mock sig header for SaaS unit tests.
        """
        timestamp = str(int(time.time()))
        signed_payload = f"{timestamp}.{payload.decode('utf-8')}".encode("utf-8")
        mac = hmac.new(secret.encode("utf-8"), signed_payload, hashlib.sha256).hexdigest()
        return f"t={timestamp},v1={mac}"
