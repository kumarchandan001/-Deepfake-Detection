from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from ai_engine.utils.logger import setup_logger
from enterprise.saas.tenant_manager import TenantManager
from enterprise.saas.subscription_manager import SubscriptionManager

logger = setup_logger("tenant_service")

class TenantService:
    def __init__(self):
        self.manager = TenantManager()
        self.subscriptions = SubscriptionManager()

    async def onboard_tenant(self, tenant_id: str, name: str, email: str, plan_key: str = "free") -> Dict[str, Any]:
        """
        Orchestrates onboarding processes for a new tenant client.
        Provisions isolated database schemas for Enterprise plans,
        and registers Stripe subscription mappings.
        """
        logger.info(f"Onboarding new Tenant profile: ID={tenant_id}, Name={name}, Plan={plan_key}")
        
        # 1. Initialize subscription records
        sub_details = await self.subscriptions.create_tenant_subscription(
            tenant_id=tenant_id,
            email=email,
            plan_key=plan_key
        )
        
        # 2. Provision isolated database schemas proactively if Enterprise
        session = None
        if plan_key == "enterprise" or tenant_id.startswith("ent_"):
            logger.info(f"Triggering database engine connection provisioning for Enterprise Tenant: {tenant_id}")
            session = await self.manager.get_tenant_session(tenant_id)
            # Close session immediately after test compilation
            await session.close()

        return {
            "status": "success",
            "tenant_id": tenant_id,
            "stripe_details": {
                "customer_id": sub_details["stripe_customer_id"],
                "subscription_id": sub_details["stripe_subscription_id"]
            },
            "database_profile": "isolated_sqlite_schema" if (plan_key == "enterprise" or tenant_id.startswith("ent_")) else "shared_row_level"
        }

    async def resolve_db_session(self, tenant_id: str) -> AsyncSession:
        """
        Utility resolving active database session connection references for routing.
        """
        return await self.manager.get_tenant_session(tenant_id)
