import pytest
from httpx import AsyncClient, ASGITransport
from backend.main import app


@pytest.mark.asyncio
async def test_generate_grievance_sebi_scores_portal():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        payload = {
            "incident_summary": "Promised 40% monthly returns on Telegram channel under fake registration INA000012345.",
            "amount": 250000.0,
            "scammer_details": {
                "reg_number": "INA000012345",
                "intermediary_name": "Apex Capital Wealth Advisors",
                "channel_handle": "@ApexScam_VIP",
                "upi_id": "apexscam@ybl"
            },
            "user_session_id": "sess_test_123",
            "dispute_type": "Unauthorized Investment Advisory & High Fee Demand"
        }
        response = await client.post("/api/v1/grievance/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["filing_portal"] == "SEBI_SCORES"
        assert "# FORMAL COMPLAINT DOSSIER" in data["dossier_markdown"]
        assert "₹250,000.00 INR" in data["dossier_markdown"]
        assert len(data["required_documents"]) > 0


@pytest.mark.asyncio
async def test_generate_grievance_cybercrime_portal():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver") as client:
        payload = {
            "incident_summary": "Unregistered Dabba trading app niftydabbaking.net cheated user off-exchange.",
            "amount": 500000.0,
            "scammer_details": {
                "channel_handle": "@NiftyDabbaExpress",
                "domain_or_apk": "niftydabbaking.net",
                "upi_id": "scammerdabba@icici"
            },
            "user_session_id": "sess_test_456",
            "dispute_type": "Dabba Trading / Unregistered Financial Fraud"
        }
        response = await client.post("/api/v1/grievance/generate", json=payload)
        assert response.status_code == 200
        data = response.json()
        assert data["filing_portal"] == "CYBERCRIME_PORTAL"
        assert "FORMAL COMPLAINT DOSSIER" in data["dossier_markdown"]
        assert len(data["required_documents"]) >= 3
