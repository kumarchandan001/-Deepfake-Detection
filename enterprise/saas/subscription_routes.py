from fastapi import APIRouter, Header, Request, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any
from ai_engine.utils.logger import setup_logger
from enterprise.saas.billing_service import BillingService
from enterprise.saas.subscription_manager import SubscriptionManager

logger = setup_logger("subscription_routes")
router = APIRouter(prefix="/api/v1/saas/subscription", tags=["SaaS Subscriptions"])
billing_service = BillingService()
manager = SubscriptionManager()

class UpgradeRequest(BaseModel):
    email: str
    plan_key: str

@router.post("/upgrade", response_model=Dict[str, Any])
async def upgrade_plan(
    payload: UpgradeRequest, 
    x_tenant_id: str = Header(..., alias="X-Tenant-ID")
):
    """
    Upgrades a tenant's plan via Stripe pricing.
    """
    try:
        logger.info(f"Subscription route upgrading Tenant {x_tenant_id} to plan: {payload.plan_key}")
        result = await billing_service.upgrade_tenant_plan(
            tenant_id=x_tenant_id,
            email=payload.email,
            plan_key=payload.plan_key
        )
        return result
    except Exception as e:
        logger.error(f"Upgrade endpoint failure: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/cancel", response_model=Dict[str, Any])
async def cancel_plan(x_tenant_id: str = Header(..., alias="X-Tenant-ID")):
    """
    Cancels the active plan tier.
    """
    try:
        logger.info(f"Subscription route cancelling active tier for Tenant: {x_tenant_id}")
        return await billing_service.cancel_tenant_plan(x_tenant_id)
    except Exception as e:
        logger.error(f"Cancellation endpoint failure: {e}")
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/webhook", status_code=status.HTTP_200_OK)
async def stripe_webhook(request: Request, stripe_signature: str = Header(None)):
    """
    Listens for inbound Webhook events sent by Stripe.
    """
    if not stripe_signature:
        logger.error("Missing critical Stripe signature header parameter.")
        raise HTTPException(status_code=400, detail="Missing signature header")

    payload = await request.body()
    try:
        logger.info("Inbound Stripe webhook route triggered.")
        result = await manager.handle_stripe_webhook(payload, stripe_signature)
        return result
    except ValueError as e:
        logger.error(f"Invalid webhook payload transaction request: {e}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Stripe Webhook processing crash: {e}")
        raise HTTPException(status_code=500, detail="Internal webhook processing error")
