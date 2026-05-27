from fastapi import APIRouter, UploadFile, File, status, HTTPException, Depends
import os
import uuid
from typing import Set
from backend.schemas.video_response_schema import VideoForensicResponse
from backend.services.video_detection_service import VideoDetectionService
from ai_engine.utils.logger import setup_logger

logger = setup_logger("video_routes")
router = APIRouter(prefix="/api/v1/forensics/video", tags=["Forensics Video Engine"])

def get_video_service() -> VideoDetectionService:
    return VideoDetectionService()

# Supported high-performance formats
ALLOWED_VIDEO_FORMATS: Set[str] = {".mp4", ".avi", ".mov", ".mkv"}
UPLOAD_DIR = "uploads/videos"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post(
    "/analyze", 
    response_model=VideoForensicResponse, 
    status_code=status.HTTP_200_OK,
    summary="Analyze video sequence for facial manipulation"
)
async def analyze_video_payload(
    file: UploadFile = File(...),
    service: VideoDetectionService = Depends(get_video_service)
) -> VideoForensicResponse:
    """
    Ingests video streams asynchronously, performs security formats checks,
    and runs multi-frame facial evaluation pipelines.
    """
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_VIDEO_FORMATS:
        logger.warning(f"Rejected unsupported video upload format: {file.filename}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported format '{file_ext}'. Supported video formats: {ALLOWED_VIDEO_FORMATS}"
        )

    # Secure collision-free UUID naming
    unique_filename = f"{uuid.uuid4()}{file_ext}"
    temp_filepath = os.path.join(UPLOAD_DIR, unique_filename)

    try:
        # Asynchronously write chunks to local video cache
        with open(temp_filepath, "wb") as buffer:
            while chunk := await file.read(2 * 1024 * 1024): # 2MB blocks
                buffer.write(chunk)
                
        logger.info(f"Written video payload: {file.filename} -> {unique_filename}")
        
        # Route to Service layer
        result = service.process_video_analysis(temp_filepath)
        
        # Clean up temp file
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
            
        if not result.get("success", False):
            return VideoForensicResponse(
                success=False,
                filename=file.filename,
                error=result.get("error", "AI Video Engine execution failed.")
            )

        return VideoForensicResponse(
            success=True,
            filename=file.filename,
            analysis={
                "prediction": result["prediction"],
                "confidence": result["confidence"],
                "fake_frame_ratio": result["fake_frame_ratio"],
                "mean_score": result["mean_score"],
                "processing_time": result["processing_time"]
            }
        )

    except Exception as e:
        logger.error(f"Forensic video API failed to complete: {e}")
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forensic video engine failure: {str(e)}"
        )
