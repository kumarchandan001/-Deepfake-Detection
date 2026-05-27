from fastapi import APIRouter, UploadFile, File, status, HTTPException, Depends
import os
import uuid
import shutil
from typing import Dict, Any
from ai_engine.orchestration.investigation_pipeline import ForensicInvestigationPipeline
from ai_engine.utils.logger import setup_logger

logger = setup_logger("investigation_routes")
router = APIRouter(prefix="/api/v1/investigations", tags=["Autonomous Investigations Operations"])

# Single pipeline instance decoupling
def get_investigation_pipeline() -> ForensicInvestigationPipeline:
    return ForensicInvestigationPipeline()

UPLOAD_DIR = "uploads/investigations"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@router.post(
    "/analyze",
    status_code=status.HTTP_200_OK,
    summary="Trigger autonomous multi-stage forensic verification pipeline"
)
async def trigger_autonomous_investigation(
    case_title: str,
    file: UploadFile = File(...),
    pipeline: ForensicInvestigationPipeline = Depends(get_investigation_pipeline)
) -> Dict[str, Any]:
    """
    Uploader route. Ingests media file and launches async multi-stage forensic scans,
    returning a compiled executive AI case dossier.
    """
    file_ext = os.path.splitext(file.filename)[1].lower()
    unique_id = f"case_{uuid.uuid4().hex[:10]}"
    unique_filename = f"{unique_id}{file_ext}"
    temp_filepath = os.path.join(UPLOAD_DIR, unique_filename)

    logger.info(f"Ingesting media file: {file.filename} -> {temp_filepath}")

    try:
        # Write file chunk by chunk
        with open(temp_filepath, "wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)

        logger.info(f"File uploaded. Executing pipeline for case: {case_title}")
        
        # Launch full pipeline asynchronously
        dossier = await pipeline.execute_case_pipeline(unique_id, case_title, temp_filepath)
        
        # Cleanup local file cache if S3 isn't writing directly
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)

        return dossier

    except Exception as e:
        logger.error(f"Pipeline transaction failed: {e}")
        if os.path.exists(temp_filepath):
            os.remove(temp_filepath)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Forensic investigation execution failure: {str(e)}"
        )
