import os
import yaml
from typing import Dict, Optional, Any
from ai_engine.utils.logger import setup_logger
from enterprise.saas.pricing_models import PlanDefinition, PlanPricing, PlanLimits

logger = setup_logger("plan_registry")

class PlanRegistry:
    _instance: Optional["PlanRegistry"] = None
    plans: Dict[str, PlanDefinition] = {}
    config_data: Dict[str, Any] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(PlanRegistry, cls).__new__(cls, *args, **kwargs)
            cls._instance._load_config()
        return cls._instance

    def _load_config(self):
        config_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 
            "saas_config.yaml"
        )
        try:
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    self.config_data = yaml.safe_load(f) or {}
                logger.info(f"Loaded SaaS config from: {config_path}")
            else:
                logger.warning(f"SaaS config not found at: {config_path}. Loading built-in default plans.")
                self.config_data = self._get_default_config()

            self._parse_plans()
        except Exception as e:
            logger.error(f"Error loading SaaS configuration: {e}. Falling back to default plan structures.")
            self.config_data = self._get_default_config()
            self._parse_plans()

    def _get_default_config(self) -> Dict[str, Any]:
        return {
            "stripe": {
                "publishable_key": "pk_test_default",
                "secret_key": "sk_test_default",
                "webhook_secret": "whsec_default",
                "use_mock": True
            },
            "plans": {
                "free": {
                    "name": "Developer Free Tier",
                    "stripe_price_id": "price_free_tier",
                    "price_cents": 0,
                    "billing_interval": "month",
                    "daily_quota": 10,
                    "monthly_quota": 300,
                    "concurrent_request_limit": 1,
                    "compute_queue": "cpu_low_priority",
                    "gpu_fraction": 0.0,
                    "allowed_features": ["image_detection", "basic_audit"]
                },
                "pro": {
                    "name": "Professional Forensics",
                    "stripe_price_id": "price_pro_tier",
                    "price_cents": 19900,
                    "billing_interval": "month",
                    "daily_quota": 200,
                    "monthly_quota": 5000,
                    "concurrent_request_limit": 5,
                    "compute_queue": "gpu_shared",
                    "gpu_fraction": 0.25,
                    "allowed_features": [
                        "image_detection", "video_detection", "audio_detection", 
                        "explainable_ai", "webcam_verification", "standard_audit", "slack_alerts"
                    ]
                },
                "enterprise": {
                    "name": "Enterprise Sovereignty",
                    "stripe_price_id": "price_enterprise_tier",
                    "price_cents": 150000,
                    "billing_interval": "month",
                    "daily_quota": 1000000,
                    "monthly_quota": 10000000,
                    "concurrent_request_limit": 100,
                    "compute_queue": "dedicated_ray_worker",
                    "gpu_fraction": 1.0,
                    "allowed_features": [
                        "image_detection", "video_detection", "audio_detection", 
                        "explainable_ai", "webcam_verification", "advanced_forensic_agents", 
                        "threat_intelligence", "isolated_schema_routing", "compliance_reporting", 
                        "webhook_engine", "slack_alerts", "discord_alerts", "sso_auth", "unlimited_audit_trail"
                    ]
                }
            }
        }

    def _parse_plans(self):
        plans_data = self.config_data.get("plans", {})
        for plan_key, data in plans_data.items():
            pricing = PlanPricing(
                plan_key=plan_key,
                name=data.get("name", plan_key.capitalize()),
                stripe_price_id=data.get("stripe_price_id", f"price_{plan_key}"),
                price_cents=data.get("price_cents", 0),
                billing_interval=data.get("billing_interval", "month"),
                metered_overage_price_cents=data.get("metered_overage_price_cents", 0)
            )
            limits = PlanLimits(
                daily_quota=data.get("daily_quota", 10),
                monthly_quota=data.get("monthly_quota", 300),
                concurrent_request_limit=data.get("concurrent_request_limit", 1),
                compute_queue=data.get("compute_queue", "cpu_low_priority"),
                gpu_fraction=data.get("gpu_fraction", 0.0),
                allowed_features=data.get("allowed_features", [])
            )
            self.plans[plan_key] = PlanDefinition(pricing=pricing, limits=limits)
            logger.info(f"Registered Plan [{plan_key}]: Max {limits.monthly_quota} monthly queries, Queue={limits.compute_queue}")

    def get_plan(self, plan_key: str) -> Optional[PlanDefinition]:
        return self.plans.get(plan_key)

    def is_feature_allowed(self, plan_key: str, feature: str) -> bool:
        plan = self.get_plan(plan_key)
        if not plan:
            return False
        return feature in plan.limits.allowed_features

    def get_stripe_settings(self) -> Dict[str, Any]:
        return self.config_data.get("stripe", {
            "publishable_key": "pk_test_default",
            "secret_key": "sk_test_default",
            "webhook_secret": "whsec_default",
            "use_mock": True
        })
