from fastapi import APIRouter, Header, HTTPException
from typing import Dict, Any
from ai_engine.utils.logger import setup_logger
from enterprise.saas.billing_service import BillingService

logger = setup_logger("billing_routes")
router = APIRouter(prefix="/api/v1/saas/billing", tags=["SaaS Billing"])
service = BillingService()

@router.get("/status", response_model=Dict[str, Any])
async def get_billing_status(x_tenant_id: str = Header(..., alias="X-Tenant-ID")):
    """
    Exposes current billing period balance and usage parameters.
    """
    try:
        logger.info(f"Billing route checking status for Tenant: {x_tenant_id}")
        return await service.get_tenant_billing_status(x_tenant_id)
    except Exception as e:
        logger.error(f"Failed to fetch billing details: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/invoice", response_model=Dict[str, Any])
async def trigger_invoice(x_tenant_id: str = Header(..., alias="X-Tenant-ID")):
    """
    Compiles outstanding usage events and issues a new Stripe invoice invoice.
    """
    try:
        logger.info(f"Billing route trigger invoice generation for: {x_tenant_id}")
        return await service.trigger_invoice_generation(x_tenant_id)
    except Exception as e:
        logger.error(f"Failed to compile invoice statement: {e}")
        raise HTTPException(status_code=400, detail=str(e))
