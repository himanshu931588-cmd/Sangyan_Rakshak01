import asyncio
from datetime import date, datetime, timezone
from decimal import Decimal
import logging

from sqlalchemy import select
from backend.database.models import (
    SebiIntermediary,
    UnregisteredBlacklist,
    VerificationLog,
    GrievanceDraft,
    IntermediaryCategory,
    IntermediaryStatus,
    ScamType,
    InputType,
    VerdictType,
    GrievanceStatus,
)
from backend.database.session import AsyncSessionLocal, init_db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SangyanSeeder")


# Benchmark SEBI Registered Intermediaries
SEBI_INTERMEDIARIES_DATA = [
    {
        "reg_number": "INA000012345",
        "entity_name": "Apex Capital Wealth Advisors",
        "category": IntermediaryCategory.RIA,
        "status": IntermediaryStatus.ACTIVE,
        "valid_until": date(2028, 12, 31),
        "contact_email": "compliance@apexcapital.in",
        "complaint_count": 1,
    },
    {
        "reg_number": "INH000098765",
        "entity_name": "Vanguard Financial Research & Analytics",
        "category": IntermediaryCategory.RA,
        "status": IntermediaryStatus.ACTIVE,
        "valid_until": date(2027, 6, 30),
        "contact_email": "research@vanguardanalytics.in",
        "complaint_count": 0,
    },
    {
        "reg_number": "INZ000054321",
        "entity_name": "Zerodha Broking Limited",
        "category": IntermediaryCategory.StockBroker,
        "status": IntermediaryStatus.ACTIVE,
        "valid_until": date(2030, 1, 1),
        "contact_email": "compliance@zerodha.com",
        "complaint_count": 12,
    },
    {
        "reg_number": "INP000007890",
        "entity_name": "Motilal Oswal Asset Management",
        "category": IntermediaryCategory.PMS,
        "status": IntermediaryStatus.ACTIVE,
        "valid_until": date(2029, 8, 15),
        "contact_email": "pms-query@motilaloswal.com",
        "complaint_count": 3,
    },
    {
        "reg_number": "INA000003456",
        "entity_name": "Shree Wealth Advisory Services",
        "category": IntermediaryCategory.RIA,
        "status": IntermediaryStatus.SUSPENDED,
        "valid_until": date(2024, 3, 31),
        "contact_email": "support@shreewealth.co.in",
        "complaint_count": 48,
    },
]

# Benchmark Blacklisted Unregistered Entities / Schemes
UNREGISTERED_BLACKLISTS_DATA = [
    {
        "entity_name": "Royal Forex & Options VIP Club",
        "channel_handle": "@RoyalForex_VIP_Signals",
        "domain_or_apk": "royalforexvip.com",
        "scam_type": ScamType.GUARANTEED_RETURN,
        "reporter_count": 142,
        "confidence_score": 0.98,
        "date_flagged": datetime(2026, 1, 15, 10, 30, tzinfo=timezone.utc),
    },
    {
        "entity_name": "SEBI Official Multiplier Yojana",
        "channel_handle": "@SEBI_Official_Scheme_Bot",
        "domain_or_apk": "sebi-gov-invest.apk",
        "scam_type": ScamType.FAKE_SEBI_SCHEME,
        "reporter_count": 89,
        "confidence_score": 0.99,
        "date_flagged": datetime(2026, 2, 1, 14, 20, tzinfo=timezone.utc),
    },
    {
        "entity_name": "Nifty Dabba Kings",
        "channel_handle": "@NiftyDabbaExpress",
        "domain_or_apk": "niftydabbaking.net",
        "scam_type": ScamType.DABBA_TRADING,
        "reporter_count": 215,
        "confidence_score": 0.96,
        "date_flagged": datetime(2026, 2, 18, 9, 15, tzinfo=timezone.utc),
    },
    {
        "entity_name": "Cyber Cybercrime Loss Recovery Cell",
        "channel_handle": "@SEBI_SCORES_Recovery_Helpline",
        "domain_or_apk": "recovery-funds-claim.org",
        "scam_type": ScamType.RECOVERY_FRAUD,
        "reporter_count": 53,
        "confidence_score": 0.92,
        "date_flagged": datetime(2026, 3, 5, 11, 45, tzinfo=timezone.utc),
    },
    {
        "entity_name": "Lakshmi 10x Daily Return Bot",
        "channel_handle": "@Lakshmi10X_DoubleMoney",
        "domain_or_apk": "lakshmi10x.apk",
        "scam_type": ScamType.GUARANTEED_RETURN,
        "reporter_count": 310,
        "confidence_score": 0.99,
        "date_flagged": datetime(2026, 3, 22, 16, 0, tzinfo=timezone.utc),
    },
]


async def seed_database() -> None:
    """
    Seeds the database with realistic SEBI registered intermediaries,
    blacklisted fraudulent entities, verification logs, and grievance drafts.
    """
    logger.info("Initializing database tables...")
    await init_db()

    async with AsyncSessionLocal() as session:
        # Seed SEBI Intermediaries
        logger.info("Seeding SEBI Intermediaries...")
        for item in SEBI_INTERMEDIARIES_DATA:
            stmt = select(SebiIntermediary).where(
                SebiIntermediary.reg_number == item["reg_number"]
            )
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()
            if not existing:
                intermediary = SebiIntermediary(**item)
                session.add(intermediary)
                logger.info(f"Added intermediary: {item['reg_number']} ({item['entity_name']})")
            else:
                logger.info(f"Intermediary already exists: {item['reg_number']}")

        # Seed Blacklisted Entities
        logger.info("Seeding Unregistered Blacklist entries...")
        for item in UNREGISTERED_BLACKLISTS_DATA:
            stmt = select(UnregisteredBlacklist).where(
                UnregisteredBlacklist.entity_name == item["entity_name"]
            )
            res = await session.execute(stmt)
            existing = res.scalar_one_or_none()
            if not existing:
                blacklist = UnregisteredBlacklist(**item)
                session.add(blacklist)
                logger.info(f"Added blacklist entry: {item['entity_name']}")
            else:
                logger.info(f"Blacklist entry already exists: {item['entity_name']}")

        await session.commit()

        # Seed Sample Verification Log
        sample_logs = [
            VerificationLog(
                input_hash="a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0",
                input_type=InputType.TEXT,
                extracted_reg_number="INA000012345",
                extracted_upi="apexcapital@icici",
                verdict=VerdictType.SAFE,
                fraud_markers={
                    "registered_match": True,
                    "fake_guarantee_detected": False,
                    "blacklisted_domain": False,
                },
                language="hi",
            ),
            VerificationLog(
                input_hash="f9e8d7c6b5a43210987654321fedcba0987654321fedcba0987654321fedcba0",
                input_type=InputType.APK,
                extracted_reg_number=None,
                extracted_upi="scammer10x@ybl",
                verdict=VerdictType.CRITICAL_FRAUD,
                fraud_markers={
                    "dabba_trading_signal": True,
                    "malicious_apk": True,
                    "fake_sebi_logo": True,
                },
                language="hi",
            ),
        ]
        for log in sample_logs:
            stmt_log = select(VerificationLog).where(VerificationLog.input_hash == log.input_hash)
            res_log = await session.execute(stmt_log)
            if not res_log.scalar_one_or_none():
                session.add(log)

        # Seed Sample Grievance Drafts
        sample_drafts = [
            GrievanceDraft(
                user_session_id="sess_8832940291",
                dispute_type="Unauthorized Trading & High Fee Demands",
                intermediary_name="Shree Wealth Advisory Services",
                amount_lost=Decimal("150000.00"),
                incident_summary="Offered fake 50% monthly returns on Telegram and deducted advisory fees without valid agreement.",
                generated_scores_dossier="DOSSIER-2026-SEBI-0091: Verified unregistered Telegram channel promoting guaranteed returns under suspended RIA registration INA000003456.",
                status=GrievanceStatus.COPIED,
            ),
            GrievanceDraft(
                user_session_id="sess_7712093841",
                dispute_type="Dabba Trading Loss Recovery",
                intermediary_name="Nifty Dabba Kings",
                amount_lost=Decimal("350000.00"),
                incident_summary="Traded off-exchange on non-SEBI recognized portal niftydabbaking.net.",
                generated_scores_dossier="DOSSIER-2026-SEBI-0142: Unregistered Dabba trading entity with 215 user report flags.",
                status=GrievanceStatus.DRAFT,
            ),
        ]
        for draft in sample_drafts:
            stmt_draft = select(GrievanceDraft).where(GrievanceDraft.user_session_id == draft.user_session_id)
            res_draft = await session.execute(stmt_draft)
            if not res_draft.scalar_one_or_none():
                session.add(draft)

        await session.commit()
        logger.info("Database seeding completed successfully.")


if __name__ == "__main__":
    asyncio.run(seed_database())
