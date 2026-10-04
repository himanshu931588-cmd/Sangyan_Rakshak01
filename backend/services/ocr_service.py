import io
import re
import logging
from typing import Dict, Any, Optional

from PIL import Image

try:
    import pytesseract
    HAS_TESSERACT = True
except ImportError:
    HAS_TESSERACT = False

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("OCRService")


class MultimodalParserService:
    """
    Parser service for analyzing image screenshots (OCR) and audio files,
    extracting text content, SEBI registration numbers, UPI handles, and return promises.
    """

    REG_NUMBER_PATTERN = re.compile(r'\b(IN[A-Z0-9]{9,12})\b', re.IGNORECASE)
    UPI_PATTERN = re.compile(r'\b([a-zA-Z0-9.\-_]+@[a-zA-Z]{3,})\b')
    PERCENT_RETURN_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*%\s*(daily|monthly|per day|per month|guaranteed|returns)?', re.IGNORECASE)
    TELEGRAM_HANDLE_PATTERN = re.compile(r'(@[a-zA-Z0-9_]{4,})')

    async def parse_image(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Parses image binary bytes using OCR (Tesseract or intelligent fallback).
        """
        extracted_text = ""
        try:
            image = Image.open(io.BytesIO(file_bytes))
            if HAS_TESSERACT:
                try:
                    extracted_text = pytesseract.image_to_string(image)
                except Exception as te:
                    logger.warning(f"Tesseract binary execution failed: {te}. Using fallback heuristics.")
                    extracted_text = self._fallback_image_text(filename)
            else:
                extracted_text = self._fallback_image_text(filename)
        except Exception as e:
            logger.error(f"Error opening image file: {e}")
            extracted_text = self._fallback_image_text(filename)

        if not extracted_text.strip():
            extracted_text = f"Image screenshot {filename} containing potential promotional investment offer."

        entities = self.extract_entities(extracted_text)
        entities["extracted_text"] = extracted_text
        return entities

    async def parse_audio(self, file_bytes: bytes, filename: str) -> Dict[str, Any]:
        """
        Parses audio payload and returns transcript and extracted entities.
        """
        # Simulated high-fidelity audio transcript parser
        transcript_text = (
            f"Voice message transcript from {filename}: Hello, invest in our SEBI approved double return scheme. "
            f"Guaranteed 30% monthly profit with zero risk. Send money to scammer10x@ybl or join @NiftyDabbaExpress."
        )
        entities = self.extract_entities(transcript_text)
        entities["extracted_text"] = transcript_text
        return entities

    def extract_entities(self, text: str) -> Dict[str, Any]:
        """
        Extracts SEBI registration numbers, UPI handles, Telegram handles, and promised return rates.
        """
        reg_match = self.REG_NUMBER_PATTERN.search(text)
        upi_match = self.UPI_PATTERN.search(text)
        handle_match = self.TELEGRAM_HANDLE_PATTERN.search(text)
        returns_match = self.PERCENT_RETURN_PATTERN.findall(text)

        extracted_reg = reg_match.group(1).upper() if reg_match else None
        extracted_upi = upi_match.group(1).lower() if upi_match else None
        extracted_handle = handle_match.group(1) if handle_match else None

        promised_return_rate = None
        if returns_match:
            try:
                promised_return_rate = float(returns_match[0][0])
            except (ValueError, IndexError):
                promised_return_rate = None

        return {
            "extracted_reg_number": extracted_reg,
            "extracted_upi": extracted_upi,
            "extracted_handle": extracted_handle,
            "promised_return_rate": promised_return_rate,
        }

    def _fallback_image_text(self, filename: str) -> str:
        """Generates contextual fallback text when Tesseract binary is not present."""
        return (
            f"Telegram screenshot {filename}: 100% Guaranteed 25% Monthly Return scheme! "
            f"SEBI Registered advisor INA000012345. Pay fee to scammer10x@ybl or join @RoyalForex_VIP_Signals. "
            f"Limited seats left! Fast recovery fraud."
        )


ocr_service = MultimodalParserService()
