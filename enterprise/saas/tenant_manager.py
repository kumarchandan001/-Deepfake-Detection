import os
from typing import Dict, Any, Optional
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from ai_engine.utils.logger import setup_logger
from backend.db.config import Base
from enterprise.saas.plan_registry import PlanRegistry

logger = setup_logger("tenant_manager")

class TenantManager:
    _instance: Optional["TenantManager"] = None
    
    # Cache created engine pools to prevent overhead
    # tenant_id -> AsyncEngine
    _tenant_engines: Dict[str, Any] = {}

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(TenantManager, cls).__new__(cls, *args, **kwargs)
            cls._instance.registry = PlanRegistry()
        return cls._instance

    def get_tenant_database_url(self, tenant_id: str) -> str:
        """
        Calculates separate physical database paths for Enterprise tenants,
        or defaults to standard main shared database connection path.
        """
        # Retrieve plan from registration lookup
        base_db_url = os.getenv(
            "DATABASE_URL", 
            "sqlite+aiosqlite:///C:/Users/Chandan Kumar/Desktop/Deepfake-Detection/forensics.db"
        )
        
        # Enterprise tenants can leverage isolated database routing
        if tenant_id.startswith("ent_"):
            db_dir = os.path.dirname(base_db_url.replace("sqlite+aiosqlite:///", ""))
            # Create a separate physical SQLite database file for the tenant
            tenant_db_file = os.path.join(db_dir, f"forensics_{tenant_id}.db")
            tenant_url = f"sqlite+aiosqlite:///{tenant_db_file}"
            logger.info(f"Routed Enterprise dynamic isolated database for Tenant {tenant_id}: {tenant_url}")
            return tenant_url
            
        return base_db_url

    async def get_tenant_session(self, tenant_id: str) -> AsyncSession:
        """
        Resolves or instantiates isolated database connection engine pools for the tenant.
        """
        db_url = self.get_tenant_database_url(tenant_id)
        
        if db_url not in self._tenant_engines:
            # Construct separate async engine pool
            engine = create_async_engine(
                db_url,
                echo=False,
                future=True,
                pool_pre_ping=True
            )
            self._tenant_engines[db_url] = engine
            logger.info(f"Registered connection engine pool for: {db_url}")

            # Bootstrap schema tables automatically inside the new database
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            logger.info(f"Provisioned database schema tables successfully for Tenant: {tenant_id}")

        session_factory = async_sessionmaker(
            bind=self._tenant_engines[db_url],
            class_=AsyncSession,
            expire_on_commit=False
        )
        return session_factory()

    def enforce_row_level_isolation(self, query: Any, tenant_id: str, tenant_id_column: Any) -> Any:
        """
        Appends strict row-level filter expressions for shared multi-tenant database tables.
        """
        logger.info(f"Enforcing row-level data boundaries on shared query: Tenant={tenant_id}")
        return query.filter(tenant_id_column == tenant_id)
