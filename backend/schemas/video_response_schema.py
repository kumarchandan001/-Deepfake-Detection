from pydantic import BaseModel
from typing import Optional

class VideoForensicAnalysis(BaseModel):
    prediction: str
    confidence: float
    fake_frame_ratio: float
    mean_score: float
    processing_time: float

class VideoForensicResponse(BaseModel):
    success: bool
    filename: str
    analysis: Optional[VideoForensicAnalysis] = None
    error: Optional[str] = None
