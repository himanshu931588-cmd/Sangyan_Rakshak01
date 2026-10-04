from typing import List, Dict, Any, Literal
from pydantic import BaseModel, Field


class GrievanceRequest(BaseModel):
    """Request payload for generating SEBI SCORES / SMART ODR grievance dossier."""
    incident_summary: str = Field(..., description="User's narrative describing the fraud incident", min_length=10)
    amount: float = Field(..., ge=0.0, description="Amount lost or disputed in INR")
    scammer_details: Dict[str, Any] = Field(
        default_factory=dict,
        description="Dictionary containing scammer info like reg_number, channel_handle, upi_id, domain"
    )
    user_session_id: str = Field("sess_guest", description="Unique session identifier for tracking")
    dispute_type: str = Field("Financial Scam / Fraudulent Investment Advisory", description="Category of dispute")


class GrievanceResponse(BaseModel):
    """Response payload containing generated complaint dossier and filing instructions."""
    dossier_markdown: str = Field(..., description="Markdown text of the generated formal complaint dossier")
    filing_portal: Literal["SEBI_SCORES", "CYBERCRIME_PORTAL"] = Field(
        ..., description="Recommended regulatory portal for filing"
    )
    required_documents: List[str] = Field(
        default_factory=list, description="Checklist of evidentiary documents required for submission"
    )
