from pydantic import BaseModel
from typing import Optional

class DetectionAnalysis(BaseModel):
    prediction: str
    confidence: float
    raw_score: float
    processing_time: float

class ForensicDetectionResponse(BaseModel):
    success: bool
    filename: str
    analysis: Optional[DetectionAnalysis] = None
    error: Optional[str] = None
