import enum
import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import Optional, Any, Dict

from sqlalchemy import (
    String,
    Integer,
    Float,
    Numeric,
    Text,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, Uuid

# Dialect-agnostic JSONB type (JSONB on PostgreSQL, JSON on SQLite)
JSONBType = JSON().with_variant(JSONB, "postgresql")


class Base(DeclarativeBase):
    """Base declarative class for SQLAlchemy models."""
    pass


# ----------------------------------------------------------------------
# Enums
# ----------------------------------------------------------------------

class IntermediaryCategory(str, enum.Enum):
    RIA = "RIA"
    RA = "RA"
    StockBroker = "StockBroker"
    PMS = "PMS"


class IntermediaryStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    SUSPENDED = "SUSPENDED"
    EXPIRED = "EXPIRED"


class ScamType(str, enum.Enum):
    DABBA_TRADING = "DABBA_TRADING"
    FAKE_SEBI_SCHEME = "FAKE_SEBI_SCHEME"
    GUARANTEED_RETURN = "GUARANTEED_RETURN"
    RECOVERY_FRAUD = "RECOVERY_FRAUD"


class InputType(str, enum.Enum):
    TEXT = "TEXT"
    AUDIO = "AUDIO"
    IMAGE_OCR = "IMAGE_OCR"
    APK = "APK"


class VerdictType(str, enum.Enum):
    SAFE = "SAFE"
    SUSPICIOUS = "SUSPICIOUS"
    HIGH_RISK = "HIGH_RISK"
    CRITICAL_FRAUD = "CRITICAL_FRAUD"


class GrievanceStatus(str, enum.Enum):
    DRAFT = "DRAFT"
    COPIED = "COPIED"
    SUBMITTED = "SUBMITTED"


# ----------------------------------------------------------------------
# Models
# ----------------------------------------------------------------------

class SebiIntermediary(Base):
    """
    SEBI Registered Intermediaries database table.
    Stores registered advisors, research analysts, brokers, and PMS managers.
    """
    __tablename__ = "sebi_intermediaries"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    reg_number: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    entity_name: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False
    )
    category: Mapped[IntermediaryCategory] = mapped_column(
        Enum(IntermediaryCategory, native_enum=False, create_constraint=True),
        nullable=False,
    )
    status: Mapped[IntermediaryStatus] = mapped_column(
        Enum(IntermediaryStatus, native_enum=False, create_constraint=True),
        nullable=False,
        default=IntermediaryStatus.ACTIVE,
    )
    valid_until: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    contact_email: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    complaint_count: Mapped[int] = mapped_column(
        Integer, default=0, nullable=False
    )

    # Relationships
    verification_logs: Mapped[list["VerificationLog"]] = relationship(
        "VerificationLog", back_populates="intermediary", cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<SebiIntermediary {self.reg_number} - {self.entity_name} ({self.status.value})>"


class UnregisteredBlacklist(Base):
    """
    Unregistered Blacklisted Entities/Schemes table.
    Tracks flagged channels, apps, websites, and fraudulent handlers.
    """
    __tablename__ = "unregistered_blacklists"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    entity_name: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False
    )
    channel_handle: Mapped[Optional[str]] = mapped_column(
        String(255), index=True, nullable=True
    )
    domain_or_apk: Mapped[Optional[str]] = mapped_column(
        String(255), nullable=True
    )
    scam_type: Mapped[ScamType] = mapped_column(
        Enum(ScamType, native_enum=False, create_constraint=True),
        nullable=False,
    )
    reporter_count: Mapped[int] = mapped_column(
        Integer, default=1, nullable=False
    )
    confidence_score: Mapped[float] = mapped_column(Float, nullable=False)
    date_flagged: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        index=True,
    )

    def __repr__(self) -> str:
        return f"<UnregisteredBlacklist {self.entity_name} [{self.scam_type.value}] (Score: {self.confidence_score})>"


class VerificationLog(Base):
    """
    Verification Audit Logs table.
    Records scam shield verifications performed by users.
    """
    __tablename__ = "verification_logs"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    input_hash: Mapped[str] = mapped_column(
        String(64), index=True, nullable=False
    )
    input_type: Mapped[InputType] = mapped_column(
        Enum(InputType, native_enum=False, create_constraint=True),
        nullable=False,
    )
    extracted_reg_number: Mapped[Optional[str]] = mapped_column(
        String(64),
        ForeignKey("sebi_intermediaries.reg_number", ondelete="SET NULL"),
        index=True,
        nullable=True,
    )
    extracted_upi: Mapped[Optional[str]] = mapped_column(
        String(255), index=True, nullable=True
    )
    verdict: Mapped[VerdictType] = mapped_column(
        Enum(VerdictType, native_enum=False, create_constraint=True),
        nullable=False,
    )
    fraud_markers: Mapped[Dict[str, Any]] = mapped_column(
        JSONBType, nullable=False, default=dict
    )
    language: Mapped[str] = mapped_column(
        String(10), default="hi", nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        index=True,
    )

    # Relationships
    intermediary: Mapped[Optional["SebiIntermediary"]] = relationship(
        "SebiIntermediary", back_populates="verification_logs", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<VerificationLog {self.id} verdict={self.verdict.value} input_type={self.input_type.value}>"


class GrievanceDraft(Base):
    """
    Grievance Drafts table.
    Stores user complaint drafts for SEBI SCORES filing.
    """
    __tablename__ = "grievance_drafts"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid, primary_key=True, default=uuid.uuid4
    )
    user_session_id: Mapped[str] = mapped_column(
        String(255), index=True, nullable=False
    )
    dispute_type: Mapped[str] = mapped_column(
        String(100), nullable=False
    )
    intermediary_name: Mapped[str] = mapped_column(
        String(255), nullable=False
    )
    amount_lost: Mapped[Decimal] = mapped_column(
        Numeric(14, 2), nullable=False
    )
    incident_summary: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    generated_scores_dossier: Mapped[str] = mapped_column(
        Text, nullable=False
    )
    status: Mapped[GrievanceStatus] = mapped_column(
        Enum(GrievanceStatus, native_enum=False, create_constraint=True),
        nullable=False,
        default=GrievanceStatus.DRAFT,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=func.now(),
        index=True,
    )

    def __repr__(self) -> str:
        return f"<GrievanceDraft {self.id} session={self.user_session_id} amount={self.amount_lost}>"
