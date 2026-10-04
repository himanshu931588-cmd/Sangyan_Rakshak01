from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field


class TextVerificationRequest(BaseModel):
    """Payload for text analysis endpoint."""
    text: str = Field(..., description="Message, transcript, or suspect text to analyze", min_length=1)
    language: str = Field("hi", description="Vernacular language code (e.g., hi, en, ta, te)")


class VerificationResponse(BaseModel):
    """Response contract for verification endpoints."""
    verdict: Literal["SAFE", "SUSPICIOUS", "HIGH_RISK", "CRITICAL_FRAUD"] = Field(
        ..., description="Calculated verdict level"
    )
    risk_score: float = Field(..., ge=0.0, le=1.0, description="Risk probability score between 0.0 and 1.0")
    flags: List[str] = Field(default_factory=list, description="List of detected risk markers and indicators")
    analysis_vernacular: str = Field(..., description="Vernacular summary explanation for the user")
    matched_reg_info: Optional[Dict[str, Any]] = Field(
        None, description="Details of matched SEBI Intermediary registry entry if found"
    )
    extracted_text: Optional[str] = Field(None, description="Text parsed from OCR or Audio media")
    extracted_upi: Optional[str] = Field(None, description="UPI handle extracted from payload")
    extracted_reg_number: Optional[str] = Field(None, description="SEBI registration number extracted from payload")
