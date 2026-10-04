import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database"] == "connected"


@pytest.mark.asyncio
async def test_verify_text_valid_ria_lookup():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        payload = {
            "text": "Checking registration INA000012345 Apex Capital Wealth Advisors.",
            "language": "hi"
        }
        response = await client.post("/api/v1/verify/text", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["verdict"] in ["SAFE", "SUSPICIOUS", "HIGH_RISK", "CRITICAL_FRAUD"]
        assert data["matched_reg_info"] is not None
        assert data["matched_reg_info"]["reg_number"] == "INA000012345"
        assert data["matched_reg_info"]["entity_name"] == "Apex Capital Wealth Advisors"


@pytest.mark.asyncio
async def test_verify_text_fraudulent_telegram_scam():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        payload = {
            "text": "Join @RoyalForex_VIP_Signals for guaranteed 50% monthly profit! Send money to scammer10x@ybl.",
            "language": "hi"
        }
        response = await client.post("/api/v1/verify/text", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["verdict"] in ["HIGH_RISK", "CRITICAL_FRAUD"]
        assert data["risk_score"] >= 0.60
        assert len(data["flags"]) > 0


@pytest.mark.asyncio
async def test_verify_media_screenshot_upload():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        # Create 1x1 pixel PNG bytes
        dummy_image_bytes = (
            b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
            b'\x08\x06\x00\x00\x00\x1f\x15c4\x00\x00\x00\rIDATx\x9cc`\x00\x00\x00'
            b'\x02\x00\x01Haf\xa4\x00\x00\x00\x00IEND\xaeB`\x82'
        )
        files = {
            "file": ("telegram_screenshot.png", dummy_image_bytes, "image/png")
        }
        data = {"language": "hi"}
        response = await client.post("/api/v1/verify/media", files=files, data=data)
        assert response.status_code == 200
        result = response.json()
        assert "verdict" in result
        assert "analysis_vernacular" in result
        assert result["extracted_text"] is not None


@pytest.mark.asyncio
async def test_verify_media_audio_upload():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        dummy_audio_bytes = b"RIFF....WAVEfmt ....data...."
        files = {
            "file": ("scam_voice_note.wav", dummy_audio_bytes, "audio/wav")
        }
        data = {"language": "en"}
        response = await client.post("/api/v1/verify/media", files=files, data=data)
        assert response.status_code == 200
        result = response.json()
        assert "verdict" in result
        assert result["extracted_text"] is not None
