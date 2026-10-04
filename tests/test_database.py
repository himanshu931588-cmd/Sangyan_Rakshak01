import asyncio
import unittest
from decimal import Decimal

from sqlalchemy import select, func
from backend.database.models import (
    SebiIntermediary,
    UnregisteredBlacklist,
    VerificationLog,
    GrievanceDraft,
    IntermediaryCategory,
    IntermediaryStatus,
    ScamType,
    VerdictType,
    GrievanceStatus,
)
from backend.database.session import AsyncSessionLocal, engine, init_db
from backend.database.seeds import seed_database


class TestSangyanDatabaseSchema(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        await init_db()
        await seed_database()

    async def test_sebi_intermediaries_seeded(self):
        async with AsyncSessionLocal() as session:
            stmt = select(func.count(SebiIntermediary.id))
            count = (await session.execute(stmt)).scalar()
            self.assertGreaterEqual(count, 5)

            # Query specific RIA
            stmt_ria = select(SebiIntermediary).where(
                SebiIntermediary.reg_number == "INA000012345"
            )
            ria = (await session.execute(stmt_ria)).scalar_one_or_none()
            self.assertIsNotNone(ria)
            self.assertEqual(ria.entity_name, "Apex Capital Wealth Advisors")
            self.assertEqual(ria.category, IntermediaryCategory.RIA)
            self.assertEqual(ria.status, IntermediaryStatus.ACTIVE)

    async def test_unregistered_blacklists_seeded(self):
        async with AsyncSessionLocal() as session:
            stmt = select(func.count(UnregisteredBlacklist.id))
            count = (await session.execute(stmt)).scalar()
            self.assertGreaterEqual(count, 5)

            # Query specific scam entity
            stmt_scam = select(UnregisteredBlacklist).where(
                UnregisteredBlacklist.channel_handle == "@NiftyDabbaExpress"
            )
            scam = (await session.execute(stmt_scam)).scalar_one_or_none()
            self.assertIsNotNone(scam)
            self.assertEqual(scam.scam_type, ScamType.DABBA_TRADING)
            self.assertGreaterEqual(scam.confidence_score, 0.90)

    async def test_verification_logs_and_foreign_keys(self):
        async with AsyncSessionLocal() as session:
            stmt = select(VerificationLog).where(
                VerificationLog.input_hash == "a1b2c3d4e5f67890123456789abcdef0123456789abcdef0123456789abcdef0"
            )
            log = (await session.execute(stmt)).scalar_one_or_none()
            self.assertIsNotNone(log)
            self.assertEqual(log.verdict, VerdictType.SAFE)

            # Verify relationship navigation
            self.assertIsNotNone(log.intermediary)
            self.assertEqual(log.intermediary.entity_name, "Apex Capital Wealth Advisors")
            self.assertIn("registered_match", log.fraud_markers)

    async def test_grievance_drafts(self):
        async with AsyncSessionLocal() as session:
            stmt = select(GrievanceDraft).where(
                GrievanceDraft.user_session_id == "sess_8832940291"
            )
            draft = (await session.execute(stmt)).scalar_one_or_none()
            self.assertIsNotNone(draft)
            self.assertEqual(draft.status, GrievanceStatus.COPIED)
            self.assertEqual(draft.amount_lost, Decimal("150000.00"))


if __name__ == "__main__":
    unittest.main()
