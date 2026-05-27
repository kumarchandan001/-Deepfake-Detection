from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger
from enterprise.saas.plan_registry import PlanRegistry
from enterprise.saas.subscription_manager import SubscriptionManager

logger = setup_logger("feature_flags")

class FeatureFlags:
    _instance: Optional["FeatureFlags"] = None
    
    # Store dynamic runtime overrides: tenant_id -> {feature_name -> is_enabled}
    _tenant_overrides: Dict[str, Dict[str, bool]] = {}
    
    # System wide toggles: feature_name -> is_enabled
    _global_overrides: Dict[str, bool] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(FeatureFlags, cls).__new__(cls, *args, **kwargs)
            cls._instance.registry = PlanRegistry()
            cls._instance.subscriptions = SubscriptionManager()
        return cls._instance

    async def is_feature_active(self, tenant_id: str, feature: str) -> bool:
        """
        Determines if a feature is currently accessible to a tenant.
        Evaluates global bypasses, plan boundaries, and localized client overrides.
        """
        # 1. Global system override check (e.g. disaster kill-switches)
        if feature in self._global_overrides:
            if not self._global_overrides[feature]:
                logger.warning(f"Feature '{feature}' is globally disabled by platform administrators.")
                return False

        # 2. Local tenant override check (e.g. beta features granted to standard tiers)
        if tenant_id in self._tenant_overrides and feature in self._tenant_overrides[tenant_id]:
            override_val = self._tenant_overrides[tenant_id][feature]
            logger.info(f"Applying tenant-specific override for Tenant {tenant_id}: Feature={feature}, Allowed={override_val}")
            return override_val

        # 3. Plan boundary check
        state = await self.subscriptions.get_subscription(tenant_id)
        is_allowed = self.registry.is_feature_allowed(state.plan_key, feature)
        logger.info(f"Evaluated Plan Feature authorization: Tenant={tenant_id}, Plan={state.plan_key}, Feature={feature}, Allowed={is_allowed}")
        return is_allowed

    def set_tenant_override(self, tenant_id: str, feature: str, enabled: bool):
        if tenant_id not in self._tenant_overrides:
            self._tenant_overrides[tenant_id] = {}
        self._tenant_overrides[tenant_id][feature] = enabled
        logger.info(f"Registered Tenant feature override: Tenant={tenant_id}, Feature={feature}, Enabled={enabled}")

    def set_global_override(self, feature: str, enabled: bool):
        self._global_overrides[feature] = enabled
        logger.info(f"Registered System-wide Feature Flag: Feature={feature}, Enabled={enabled}")

    def clear_overrides(self):
        self._tenant_overrides.clear()
        self._global_overrides.clear()
        logger.info("Cleared all feature flag overrides.")
