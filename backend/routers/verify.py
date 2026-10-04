import logging
from typing import Optional
from fastapi import APIRouter, Depends, File, UploadFile, Form, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.session import get_async_session
from backend.database.models import InputType
from backend.schemas.verify import TextVerificationRequest, VerificationResponse
from backend.services.verifier import verifier_service
from backend.services.ocr_service import ocr_service

logger = logging.getLogger("VerifyRouter")

router = APIRouter(prefix="/verify", tags=["Verification"])


@router.post(
    "/text",
    response_model=VerificationResponse,
    summary="Verify plain text message or social media post"
)
async def verify_text(
    payload: TextVerificationRequest,
    db: AsyncSession = Depends(get_async_session)
):
    """
    Analyzes input text for scam patterns, unfeasible return promises, fake SEBI certificates,
    unregistered channel handles, and FOMO pressure triggers.
    """
    try:
        entities = ocr_service.extract_entities(payload.text)
        result = await verifier_service.verify_payload(
            db=db,
            text=payload.text,
            extracted_reg=entities.get("extracted_reg_number"),
            extracted_upi=entities.get("extracted_upi"),
            extracted_handle=entities.get("extracted_handle"),
            promised_return_rate=entities.get("promised_return_rate"),
            input_type=InputType.TEXT,
            language=payload.language,
        )
        return VerificationResponse(**result)
    except Exception as e:
        logger.error(f"Error in verify_text endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Verification analysis failed: {str(e)}"
        )


@router.post(
    "/media",
    response_model=VerificationResponse,
    summary="Verify media file (screenshot image or voice message audio)"
)
async def verify_media(
    file: UploadFile = File(...),
    language: str = Form("hi"),
    db: AsyncSession = Depends(get_async_session)
):
    """
    Parses screenshot OCR or Audio transcript from uploaded media file, then runs
    multimodal fraud verification against database registries and heuristics.
    """
    try:
        file_bytes = await file.read()
        filename = file.filename or "media_upload"
        filename_lower = filename.lower()

        if any(filename_lower.endswith(ext) for ext in [".jpg", ".jpeg", ".png", ".webp", ".bmp"]):
            input_type = InputType.IMAGE_OCR
            extracted_data = await ocr_service.parse_image(file_bytes, filename)
        elif any(filename_lower.endswith(ext) for ext in [".wav", ".mp3", ".m4a", ".ogg", ".aac"]):
            input_type = InputType.AUDIO
            extracted_data = await ocr_service.parse_audio(file_bytes, filename)
        else:
            # Default to text/binary parsing
            input_type = InputType.APK if filename_lower.endswith(".apk") else InputType.IMAGE_OCR
            extracted_data = await ocr_service.parse_image(file_bytes, filename)

        extracted_text = extracted_data.get("extracted_text", "")

        result = await verifier_service.verify_payload(
            db=db,
            text=extracted_text,
            extracted_reg=extracted_data.get("extracted_reg_number"),
            extracted_upi=extracted_data.get("extracted_upi"),
            extracted_handle=extracted_data.get("extracted_handle"),
            promised_return_rate=extracted_data.get("promised_return_rate"),
            input_type=input_type,
            language=language,
        )
        result["extracted_text"] = extracted_text
        return VerificationResponse(**result)
    except Exception as e:
        logger.error(f"Error in verify_media endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Media verification analysis failed: {str(e)}"
        )
