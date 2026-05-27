from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, EmailStr
from typing import Dict, Any
from ai_engine.utils.logger import setup_logger
from enterprise.saas.tenant_service import TenantService

logger = setup_logger("tenant_routes")
router = APIRouter(prefix="/api/v1/saas/tenant", tags=["SaaS Tenants"])
service = TenantService()

class TenantOnboardRequest(BaseModel):
    tenant_id: str = Field(..., description="Unique client identifier slug")
    name: str = Field(..., description="Legal company name or user name")
    email: EmailStr = Field(..., description="Owner billing email contact")
    plan_key: str = Field("free", description="Target plan tier (free, pro, enterprise)")

@router.post("/onboard", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def onboard_tenant(payload: TenantOnboardRequest):
    """
    Onboarding endpoint mapping company metadata profiles and schema instances.
    """
    try:
        logger.info(f"Onboarding endpoint request for: ID={payload.tenant_id}, Plan={payload.plan_key}")
        result = await service.onboard_tenant(
            tenant_id=payload.tenant_id,
            name=payload.name,
            email=payload.email,
            plan_key=payload.plan_key
        )
        return result
    except Exception as e:
        logger.error(f"Tenant onboarding transaction failed: {e}")
        raise HTTPException(status_code=400, detail=str(e))
