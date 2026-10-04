import hashlib
import re
import logging
from typing import Dict, Any, List, Optional, Tuple

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession

from backend.database.models import (
    SebiIntermediary,
    UnregisteredBlacklist,
    VerificationLog,
    IntermediaryStatus,
    InputType,
    VerdictType,
)

logger = logging.getLogger("FraudVerifierService")


class FraudVerifierService:
    """
    Hybrid rule-based, database-lookup, and heuristic scam detection engine.
    Cross-references SEBI registries, unregistered blacklists, return math, and FOMO triggers.
    """

    UNFEASIBLE_RETURN_THRESHOLD_MONTHLY = 20.0  # >20% monthly is unfeasible/scam marker
    UNFEASIBLE_RETURN_THRESHOLD_DAILY = 1.0     # Any guaranteed daily return

    FOMO_KEYWORDS = [
        "guaranteed return", "100% profit", "double money", "zero risk",
        "limited seats", "join vip group", "fast recovery", "fixed return",
        "गारंटीड रिटर्न", "मुनाफा", "डबल पैसा", "बिना जोखिम"
    ]

    DABBA_KEYWORDS = [
        "dabba trading", "off-exchange", "no demat required", "cash settlement",
        "डब्बा ट्रेडिंग", "बिना डिमैट"
    ]

    RECOVERY_KEYWORDS = [
        "loss recovery", "recover scammed money", "cyber cell refund", "sebi fee claim",
        "रिकवरी", "पैसा वापस"
    ]

    FAKE_SEBI_KEYWORDS = [
        "sebi approved scheme", "sebi guaranteed", "sebi govt bonus", "official sebi bot",
        "सेबी अप्रूव्ड"
    ]

    async def verify_payload(
        self,
        db: AsyncSession,
        text: str,
        extracted_reg: Optional[str] = None,
        extracted_upi: Optional[str] = None,
        extracted_handle: Optional[str] = None,
        promised_return_rate: Optional[float] = None,
        input_type: InputType = InputType.TEXT,
        language: str = "hi",
    ) -> Dict[str, Any]:
        """
        Main verification entry point. Analyzes input text & metadata against database and rules.
        """
        flags: List[str] = []
        risk_score: float = 0.05  # Base low risk
        matched_reg_info: Optional[Dict[str, Any]] = None

        text_lower = text.lower()

        # ------------------------------------------------------------------
        # Rule 1: Cross-reference SEBI Registered Intermediaries Database
        # ------------------------------------------------------------------
        if extracted_reg:
            stmt = select(SebiIntermediary).where(SebiIntermediary.reg_number == extracted_reg.upper())
            res = await db.execute(stmt)
            reg_entry = res.scalar_one_or_none()

            if reg_entry:
                matched_reg_info = {
                    "reg_number": reg_entry.reg_number,
                    "entity_name": reg_entry.entity_name,
                    "category": reg_entry.category.value,
                    "status": reg_entry.status.value,
                    "valid_until": reg_entry.valid_until.isoformat() if reg_entry.valid_until else None,
                    "complaint_count": reg_entry.complaint_count,
                }
                if reg_entry.status == IntermediaryStatus.SUSPENDED:
                    flags.append(f"SEBI Registration {reg_entry.reg_number} is SUSPENDED due to regulatory violations.")
                    risk_score += 0.50
                elif reg_entry.status == IntermediaryStatus.EXPIRED:
                    flags.append(f"SEBI Registration {reg_entry.reg_number} has EXPIRED.")
                    risk_score += 0.35
                else:
                    flags.append(f"Matched active SEBI Registration {reg_entry.reg_number} ({reg_entry.entity_name}).")
            else:
                flags.append(f"Registration number {extracted_reg} was NOT found in SEBI registry (Possible Impersonation).")
                risk_score += 0.45

        # ------------------------------------------------------------------
        # Rule 2: Cross-reference Unregistered Blacklists Database
        # ------------------------------------------------------------------
        conditions = []
        if extracted_handle:
            conditions.append(UnregisteredBlacklist.channel_handle.ilike(f"%{extracted_handle}%"))
        if text:
            conditions.append(UnregisteredBlacklist.entity_name.ilike(f"%{text[:50]}%"))

        if conditions:
            stmt_black = select(UnregisteredBlacklist).where(or_(*conditions))
            res_black = await db.execute(stmt_black)
            black_entry = res_black.scalar_one_or_none()

            if black_entry:
                flags.append(
                    f"CRITICAL: Matched blacklisted scam entity '{black_entry.entity_name}' "
                    f"[{black_entry.scam_type.value}] with confidence score {black_entry.confidence_score}."
                )
                risk_score = max(risk_score, 0.95)

        # ------------------------------------------------------------------
        # Rule 3: Heuristic Return Rate Analysis
        # ------------------------------------------------------------------
        if promised_return_rate and promised_return_rate > self.UNFEASIBLE_RETURN_THRESHOLD_MONTHLY:
            flags.append(f"Unfeasible Return Promise: {promised_return_rate}% return exceeds realistic market standards (>20%/month).")
            risk_score += 0.40

        if any(w in text_lower for w in ["daily return", "per day", "रोजाना रिटर्न"]):
            flags.append("Daily guaranteed return promised - High probability Ponzi scheme marker.")
            risk_score += 0.35

        # ------------------------------------------------------------------
        # Rule 4: FOMO & Pressure Tactics Detection
        # ------------------------------------------------------------------
        fomo_matches = [kw for kw in self.FOMO_KEYWORDS if kw in text_lower]
        if fomo_matches:
            flags.append(f"FOMO / High-pressure triggers detected: {', '.join(fomo_matches[:3])}.")
            risk_score += 0.20

        # ------------------------------------------------------------------
        # Rule 5: Scam Type Classification (Dabba / Fake SEBI / Recovery)
        # ------------------------------------------------------------------
        if any(kw in text_lower for kw in self.DABBA_KEYWORDS):
            flags.append("Dabba Trading / Unrecognized Off-Exchange trading signals detected.")
            risk_score += 0.35

        if any(kw in text_lower for kw in self.FAKE_SEBI_KEYWORDS):
            flags.append("Fake SEBI Approval claim detected (SEBI never guarantees profits).")
            risk_score += 0.40

        if any(kw in text_lower for kw in self.RECOVERY_KEYWORDS):
            flags.append("Recovery Fraud pattern detected (demanding fees to recover past losses).")
            risk_score += 0.45

        # ------------------------------------------------------------------
        # Final Risk Score & Verdict Normalization
        # ------------------------------------------------------------------
        risk_score = min(max(round(risk_score, 2), 0.0), 1.0)

        if risk_score >= 0.80:
            verdict = VerdictType.CRITICAL_FRAUD
        elif risk_score >= 0.60:
            verdict = VerdictType.HIGH_RISK
        elif risk_score >= 0.35:
            verdict = VerdictType.SUSPICIOUS
        else:
            verdict = VerdictType.SAFE

        vernacular_summary = self._generate_vernacular_summary(verdict, flags, risk_score, language)

        # ------------------------------------------------------------------
        # Async Database Audit Logging
        # ------------------------------------------------------------------
        input_hash = hashlib.sha256(text.encode("utf-8")).hexdigest()
        log_entry = VerificationLog(
            input_hash=input_hash,
            input_type=input_type,
            extracted_reg_number=extracted_reg if matched_reg_info else None,
            extracted_upi=extracted_upi,
            verdict=verdict,
            fraud_markers={
                "risk_score": risk_score,
                "flags": flags,
                "extracted_handle": extracted_handle,
            },
            language=language,
        )
        db.add(log_entry)
        await db.commit()

        return {
            "verdict": verdict.value,
            "risk_score": risk_score,
            "flags": flags if flags else ["No suspicious scam markers detected."],
            "analysis_vernacular": vernacular_summary,
            "matched_reg_info": matched_reg_info,
            "extracted_upi": extracted_upi,
            "extracted_reg_number": extracted_reg,
        }

    def _generate_vernacular_summary(
        self, verdict: VerdictType, flags: List[str], risk_score: float, language: str
    ) -> str:
        """Generates clear, vernacular explanation for the end user."""
        if language == "hi":
            if verdict == VerdictType.CRITICAL_FRAUD:
                return (
                    f"⚠️ **अत्यधिक गंभीर धोखाधड़ी चेतावनी (जोखिम: {int(risk_score*100)}%)**\n"
                    f"यह संदेश/चैनल एक प्रमाणित स्कैम है। SEBI कभी भी लाभ की गारंटी नहीं देता। "
                    f"मुख्य संकेत: {'; '.join(flags[:2])}। कृपया कोई पैसा न भेजें।"
                )
            elif verdict == VerdictType.HIGH_RISK:
                return (
                    f"⚠️ **उच्च जोखिम चेतावनी (जोखिम: {int(risk_score*100)}%)**\n"
                    f"इस प्रस्ताव में कई संदिग्ध धोखाधड़ी के संकेत मिले हैं। "
                    f"मुख्य जोखिम: {'; '.join(flags[:2])}।"
                )
            elif verdict == VerdictType.SUSPICIOUS:
                return (
                    f"⚡ **संदिग्ध गतिविधि (जोखिम: {int(risk_score*100)}%)**\n"
                    f"इसमें कुछ गैर-मानक दावे हैं। सतर्क रहें और SEBI पंजीयन अवश्य जांचें।"
                )
            else:
                return f"✅ **सुरक्षित प्रतीत होता है (जोखिम: {int(risk_score*100)}%)**\nसंदेश में कोई ज्ञात धोखाधड़ी के संकेत नहीं मिले।"
        else:
            if verdict in [VerdictType.CRITICAL_FRAUD, VerdictType.HIGH_RISK]:
                return (
                    f"⚠️ **HIGH FRAUD RISK DETECTED (Score: {int(risk_score*100)}%)**\n"
                    f"Critical warning: SEBI never guarantees profits. Identified flags: {'; '.join(flags[:2])}."
                )
            elif verdict == VerdictType.SUSPICIOUS:
                return f"⚡ **SUSPICIOUS OFFER (Score: {int(risk_score*100)}%)**\nProceed with caution. Identified flags: {'; '.join(flags[:2])}."
            else:
                return f"✅ **SAFE VERDICT (Score: {int(risk_score*100)}%)**\nNo suspicious scam markers detected."


verifier_service = FraudVerifierService()
