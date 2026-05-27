import unittest
import json
import asyncio
import time
from fastapi import FastAPI
from fastapi.testclient import TestClient
from enterprise.saas.plan_registry import PlanRegistry
from enterprise.saas.stripe_gateway import StripeGateway
from enterprise.saas.subscription_manager import SubscriptionManager
from enterprise.saas.usage_tracking import UsageTracker
from enterprise.saas.quota_enforcement import QuotaEnforcer, QuotaExceededException
from enterprise.saas.billing_engine import BillingEngine
from enterprise.saas.tenant_manager import TenantManager
from enterprise.saas.tenant_context import get_tenant_id, get_plan_key
from enterprise.saas.tenant_middleware import TenantContextMiddleware
from enterprise.saas.quota_middleware import QuotaEnforcementMiddleware
from enterprise.saas.billing_routes import router as billing_router
from enterprise.saas.tenant_routes import router as tenant_router
from enterprise.saas.subscription_routes import router as subscription_router

# Set up simple test FastAPI app instance mapping SaaS features
app = FastAPI()
app.add_middleware(QuotaEnforcementMiddleware)
app.add_middleware(TenantContextMiddleware)
app.include_router(billing_router)
app.include_router(tenant_router)
app.include_router(subscription_router)

@app.get("/api/v1/detection/test")
async def dummy_detection_endpoint():
    return {"status": "success", "processed_by": "gpu_shared", "tenant": get_tenant_id(), "plan": get_plan_key()}

class TestSaaSPlatform(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = PlanRegistry()
        # Elevate request limits on free plan to prevent rate limit throttling during sequential test requests
        cls.registry.get_plan("free").limits.concurrent_request_limit = 1000
        cls.gateway = StripeGateway()
        cls.manager = SubscriptionManager()
        cls.tracker = UsageTracker()
        cls.enforcer = QuotaEnforcer()
        cls.billing = BillingEngine()
        cls.tenant_mgr = TenantManager()
        cls.client = TestClient(app)

    def run_async(self, coro):
        loop = asyncio.new_event_loop()
        try:
            asyncio.set_event_loop(loop)
            return loop.run_until_complete(coro)
        finally:
            loop.close()

    def test_plan_registry_configuration_loading(self):
        """
        Validates loading and verification of SaaS plan definitions and settings.
        """
        free_plan = self.registry.get_plan("free")
        self.assertIsNotNone(free_plan)
        self.assertEqual(free_plan.pricing.price_cents, 0)
        self.assertEqual(free_plan.limits.daily_quota, 10)
        self.assertIn("image_detection", free_plan.limits.allowed_features)

        pro_plan = self.registry.get_plan("pro")
        self.assertEqual(pro_plan.pricing.price_cents, 19900)
        self.assertEqual(pro_plan.limits.concurrent_request_limit, 5)

        stripe_settings = self.registry.get_stripe_settings()
        self.assertTrue(stripe_settings.get("use_mock", True))

    def test_stripe_mock_gateway_creation_and_lifecycle(self):
        """
        Verifies customer creation, subscription attachments, and mock webhook processing.
        """
        # Test customer registration
        customer = self.run_async(
            self.gateway.create_customer("Acme Corp", "owner@acme.com", "tenant_acme_123")
        )
        self.assertIn("cus_mock_", customer["id"])
        self.assertEqual(customer["metadata"]["tenant_id"], "tenant_acme_123")

        # Test subscription creation
        stripe_sub = self.run_async(
            self.gateway.create_subscription(customer["id"], "price_pro_tier")
        )
        self.assertEqual(stripe_sub["status"], "active")
        self.assertIn("sub_mock_", stripe_sub["id"])

        # Test subscription cancellation
        cancelled_sub = self.run_async(
            self.gateway.cancel_subscription(stripe_sub["id"])
        )
        self.assertEqual(cancelled_sub["status"], "canceled")

    def test_usage_tracking_metrics_and_fallbacks(self):
        """
        Validates atomic counters incrementation and safe local fallback structures.
        """
        tenant = "tenant_metrics_test"
        
        # Reset any preexisting tests usage
        self.run_async(self.tracker.reset_usage(tenant, "daily_checks"))
        
        # Increment check counter
        val = self.run_async(self.tracker.increment_usage(tenant, "daily_checks", 1))
        self.assertEqual(val, 1)

        val_double = self.run_async(self.tracker.increment_usage(tenant, "daily_checks", 2))
        self.assertEqual(val_double, 3)

        fetched = self.run_async(self.tracker.get_usage(tenant, "daily_checks"))
        self.assertEqual(fetched, 3)

        # Record compute metric
        self.run_async(self.tracker.record_compute_footprint(tenant, 2, 0.450))
        inf_count = self.run_async(self.tracker.get_usage(tenant, "inference_count"))
        compute_ms = self.run_async(self.tracker.get_usage(tenant, "compute_time_ms"))
        self.assertEqual(inf_count, 2)
        self.assertEqual(compute_ms, 450)

    def test_quota_limits_and_rate_enforcements(self):
        """
        Tests rate limitation token buckets, monthly boundaries, and QuotaExceededException.
        """
        tenant = "tenant_quota_test"
        
        # Set to free subscription
        free_sub = self.run_async(self.manager.get_subscription(tenant))
        free_sub.plan_key = "free"
        free_sub.status = "active"
        self.run_async(self.manager.update_subscription_cache(free_sub))

        # Reset usages
        self.run_async(self.tracker.reset_usage(tenant, "daily_checks"))
        self.run_async(self.tracker.reset_usage(tenant, "monthly_checks"))

        # Verify free tier allowed actions
        allowed = self.run_async(self.enforcer.verify_request(tenant, "image_detection"))
        self.assertTrue(allowed)

        # Exclude unallowed feature validation
        with self.assertRaises(QuotaExceededException) as ctx:
            self.run_async(self.enforcer.verify_request(tenant, "advanced_forensic_agents"))
        self.assertIn("Feature 'advanced_forensic_agents' is not enabled in plan tier", str(ctx.exception))

        # Trigger daily quota limits exhaustion manually
        for _ in range(9):  # Increments to 10 total checks
            self.run_async(self.enforcer.verify_request(tenant, "image_detection"))

        with self.assertRaises(QuotaExceededException) as ctx:
            self.run_async(self.enforcer.verify_request(tenant, "image_detection"))
        self.assertIn("Daily API request limit reached", str(ctx.exception))

    def test_tenant_database_isolation_routing(self):
        """
        Validates tenant specific database routing engine allocation.
        """
        # Pro / Free standard row isolation db path check
        standard_path = self.tenant_mgr.get_tenant_database_url("tenant_standard_pro")
        self.assertTrue(standard_path.endswith("forensics.db"))

        # Enterprise isolated physical db file check
        ent_path = self.tenant_mgr.get_tenant_database_url("ent_financial_corp")
        self.assertTrue(ent_path.endswith("forensics_ent_financial_corp.db"))

    def test_billing_engine_statements_and_overages(self):
        """
        Validates metered base prices and monthly invoice summaries computation.
        """
        tenant = "tenant_billing_test"
        
        # Setup Pro Subscription state
        sub = self.run_async(self.manager.get_subscription(tenant))
        sub.plan_key = "pro"
        self.run_async(self.manager.update_subscription_cache(sub))
        
        # Standard invoice generation checks
        self.run_async(self.tracker.reset_usage(tenant, "monthly_checks"))
        self.run_async(self.tracker.reset_usage(tenant, "monthly_overage_checks"))
        
        invoice = self.run_async(self.billing.compile_monthly_invoice(tenant))
        self.assertEqual(invoice["details"]["total_charge_dollars"], 199.00)
        self.assertEqual(invoice["payment_status"], "paid")

    def test_fastapi_saas_context_and_quota_middlewares(self):
        """
        Integration check asserting header context propagation and 429 blocking response payload checks.
        """
        # Test standard client access
        response = self.client.get("/api/v1/detection/test", headers={"X-Tenant-ID": "tenant_api_runner"})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["tenant"], "tenant_api_runner")
        self.assertEqual(data["plan"], "free")

        # Exhaust plan requests on test tenant
        block_tenant = "tenant_block_runner"
        # Trigger onboarding to free tier
        self.client.post("/api/v1/saas/tenant/onboard", json={
            "tenant_id": block_tenant,
            "name": "Block Runner Inc",
            "email": "block@runner.com",
            "plan_key": "free"
        })

        # Fire 10 checks consecutively
        for _ in range(10):
            self.client.get("/api/v1/detection/test", headers={"X-Tenant-ID": block_tenant})

        # 11th request must fail with 429 Limit Block
        block_response = self.client.get("/api/v1/detection/test", headers={"X-Tenant-ID": block_tenant})
        self.assertEqual(block_response.status_code, 429)
        block_data = block_response.json()
        self.assertEqual(block_data["error"], "Quota Exceeded")
        self.assertIn("Daily API request limit reached", block_data["detail"])
        self.assertIn("Retry-After", block_response.headers)
