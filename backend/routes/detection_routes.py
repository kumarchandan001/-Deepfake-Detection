from fastapi import APIRouter, UploadFile, File, status, HTTPException, Depends
import os
import uuid
import shutil
from typing import Set
from backend.schemas.response_schema import ForensicDetectionResponse
from backend.services.detection_service import DetectionService
from ai_engine.utils.logger import setup_logger

logger = setup_logger("detection_routes")
router = APIRouter(prefix="/api/v1/forensics", tags=["Forensics Engine"])

def get_detection_service() -> DetectionService:
    return DetectionService()

ALLOWED_MIME_TYPES: Set[str] = {".jpg", ".jpeg", ".png", ".webp"}
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post(
    "/analyze", 
    response_model=ForensicDetectionResponse, 
    status_code=status.HTTP_200_OK,
    summary="Analyze single image for manipulation"
)
async def analyze_image_payload(
    file: UploadFile = File(...),
    service: DetectionService = Depends(get_detection_service)
) -> ForensicDetectionResponse:
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_MIME_TYPES:
        logger.warning(f"Rejected unsupported format upload: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{file_ext}'. Supported formats: {ALLOWED_MIME_TYPES}"
        )

    unique_filename = f"{uuid.uuid4()}{file_ext}"
    temp_filepath = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        with open(temp_filepath, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
                
        logger.info(f"Asynchronously written uploaded image: {file.filename} -> {unique_filename}")
        
        result = service.process_image_analysis(temp_filepath)
        
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            
        if not result.get("success", False):
            return ForensicDetectionResponse(
                success=False,
                filename=file.filename,
                error=result.get("error", "AI Engine execution failure.")
            )

        return ForensicDetectionResponse(
            success=True,
            filename=file.filename,
            analysis={
                "prediction": result["prediction"],
                "confidence": result["confidence"],
                "raw_score": result["raw_score"],
                "processing_time": result["processing_time"]
            }
        )

    except Exception as e:
        logger.error(f"Failed to execute forensic analysis API: {e}")
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Forensic engine failure: {str(e)}"
        )
