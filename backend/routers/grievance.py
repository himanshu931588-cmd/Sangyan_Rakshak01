import logging
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session
from backend.schemas.grievance import GrievanceRequest, GrievanceResponse
from backend.services.dossier_generator import dossier_service

logger = logging.getLogger("GrievanceRouter")

router = APIRouter(prefix="/grievance", tags=["Grievance Dossier"])


@router.post(
    "/generate",
    response_model=GrievanceResponse,
    summary="Generate formal SEBI SCORES / SMART ODR compliant grievance dossier markdown"
)
async def generate_grievance_dossier(
    payload: GrievanceRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Transforms user's incident narrative and scammer metadata into a structured, regulatory-compliant
    grievance dossier formatted for direct submission to SEBI SCORES 2.0 or Cybercrime portals.
    """
    try:
        result = await dossier_service.generate_dossier(
            db=db,
            incident_summary=payload.incident_summary,
            amount=payload.amount,
            scammer_details=payload.scammer_details,
            user_session_id=payload.user_session_id,
            dispute_type=payload.dispute_type,
        )
        return GrievanceResponse(**result)
    except Exception as e:
        logger.error(f"Error in generate_grievance_dossier endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Dossier generation failed: {str(e)}"
        )
