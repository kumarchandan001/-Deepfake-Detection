from fastapi import APIRouter, Header, HTTPException, UploadFile, File, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
from ai_engine.utils.logger import setup_logger
from enterprise.saas.quota_service import QuotaService

logger = setup_logger("public_api_routes")
router = APIRouter(prefix="/api/v1/public/verify", tags=["Public Verification APIs"])
quota_service = QuotaService()

# Simple mock database mapping API keys to Tenant profiles
API_KEYS_DB = {
    "df_pub_key_developer_123": "free_developer_tenant",
    "df_pub_key_pro_forensics_456": "pro_forensics_tenant",
    "df_pub_key_enterprise_corporate_789": "ent_corp_tenant"
}

def resolve_api_key(x_api_key: str) -> str:
    """
    Validates API key and maps it to a tenant ID.
    """
    tenant_id = API_KEYS_DB.get(x_api_key)
    if not tenant_id:
        logger.warning(f"Unauthorized API access block. Invalid Key: {x_api_key}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, 
            detail="Unauthorized API access. X-API-Key is invalid."
        )
    return tenant_id

@router.post("/image", response_model=Dict[str, Any])
async def verify_image_public(
    file: UploadFile = File(...),
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """
    Public Endpoint: Verify uploaded images.
    """
    tenant_id = resolve_api_key(x_api_key)
    
    # 1. Enforce SaaS Plan Quotas Check
    try:
        await quota_service.validate_request_access(tenant_id, "image_detection")
    except Exception as e:
        logger.error(f"Quota validation failure on public route: {e}")
        raise HTTPException(status_code=429, detail=str(e))

    # 2. Process image classification mock logic
    logger.info(f"Public API verifying image '{file.filename}' for Tenant: {tenant_id}")
    return {
        "status": "success",
        "filename": file.filename,
        "media_type": "IMAGE",
        "verdict": "REAL",
        "confidence": 0.9823,
        "processing_time_sec": 0.084
    }

@router.post("/audio", response_model=Dict[str, Any])
async def verify_audio_public(
    file: UploadFile = File(...),
    x_api_key: str = Header(..., alias="X-API-Key")
):
    """
    Public Endpoint: Verify voice recordings.
    """
    tenant_id = resolve_api_key(x_api_key)
    
    try:
        await quota_service.validate_request_access(tenant_id, "audio_detection")
    except Exception as e:
        raise HTTPException(status_code=429, detail=str(e))

    logger.info(f"Public API verifying audio '{file.filename}' for Tenant: {tenant_id}")
    return {
        "status": "success",
        "filename": file.filename,
        "media_type": "AUDIO",
        "verdict": "FAKE",
        "confidence": 0.9412,
        "audio_forensics": {
            "synthetic_spectral_noise_detected": True,
            "detected_voice_cloning_profile": "ElevenLabsV2"
        },
        "processing_time_sec": 0.145
    }
