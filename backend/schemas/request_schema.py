from pydantic import BaseModel, Field
from typing import Optional

class IngressForensicRequest(BaseModel):
    """
    Standard schema for inbound configuration overrides passed during upload analyses.
    """
    confidence_threshold: Optional[float] = Field(
        default=0.5, 
        ge=0.0, 
        le=1.0, 
        description="Threshold cut value to decide between REAL and FAKE outputs."
    )
    extract_faces: Optional[bool] = Field(
        default=True,
        description="Whether to execute face crop extraction before running inference."
    )
