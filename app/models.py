import uuid
from datetime import datetime

from sqlalchemy import (
    BigInteger,
    Boolean,
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    Numeric,
    Text,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


def _uuid_pk() -> Mapped[uuid.UUID]:
    return mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)


def _session_fk() -> Mapped[uuid.UUID]:
    return mapped_column(
        UUID(as_uuid=True),
        ForeignKey("sessions.id", ondelete="CASCADE"),
        nullable=False, index=True,
    )


class Session(Base):
    __tablename__ = "sessions"
    id: Mapped[uuid.UUID] = _uuid_pk()
    started_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
    phase: Mapped[str] = mapped_column(Text, nullable=False, default="intake")
    status: Mapped[str] = mapped_column(Text, nullable=False, default="active")
    lang_profile: Mapped[dict | None] = mapped_column(JSONB)
    token_spend: Mapped[dict | None] = mapped_column(JSONB)


class Intake(Base):
    __tablename__ = "intake"
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True)
    business_name: Mapped[str | None] = mapped_column(Text)
    business_desc: Mapped[str | None] = mapped_column(Text)
    stated_problem: Mapped[str] = mapped_column(Text, nullable=False)  # verbatim
    role: Mapped[str | None] = mapped_column(Text)
    size_band: Mapped[str | None] = mapped_column(Text)
    customer_type: Mapped[str | None] = mapped_column(Text)


class ProblemFrame(Base):
    __tablename__ = "problem_frames"
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    classes: Mapped[dict] = mapped_column(JSONB, nullable=False)
    confidence: Mapped[float] = mapped_column(Float, nullable=False)
    sidedness: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    private_individuals: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    pain_hypothesis: Mapped[str | None] = mapped_column(Text)
    version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)


class Consent(Base):
    __tablename__ = "consents"
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    text_version: Mapped[str] = mapped_column(Text, nullable=False)
    accepted_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
    ip_hash: Mapped[str | None] = mapped_column(Text)


class Message(Base):
    __tablename__ = "messages"
    __table_args__ = (CheckConstraint("sender IN ('client','agent')", name="ck_sender"),)
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    sender: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    audio_object_key: Mapped[str | None] = mapped_column(Text)
    transcript_confidence: Mapped[float | None] = mapped_column(Float)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)


class Figure(Base):
    __tablename__ = "figures"
    __table_args__ = (CheckConstraint(
        "provenance IN ('user_stated','suggested_range','computed')", name="ck_provenance"),)
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    name: Mapped[str] = mapped_column(Text, nullable=False)
    value_low: Mapped[float] = mapped_column(Numeric, nullable=False)
    value_high: Mapped[float] = mapped_column(Numeric, nullable=False)
    unit: Mapped[str] = mapped_column(Text, nullable=False)
    provenance: Mapped[str] = mapped_column(Text, nullable=False)
    source_msg_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"))


class WarStory(Base):
    __tablename__ = "war_stories"
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    summary: Mapped[str] = mapped_column(Text, nullable=False)
    consequence: Mapped[str | None] = mapped_column(Text)
    priced_cost: Mapped[float | None] = mapped_column(Numeric)
    source_msg_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("messages.id", ondelete="SET NULL"))


class Coverage(Base):
    __tablename__ = "coverage"
    __table_args__ = (CheckConstraint(
        "status IN ('pending','active','covered','parked')", name="ck_coverage_status"),)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True)
    dimension: Mapped[str] = mapped_column(Text, primary_key=True)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="pending")
    q_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)


class Finding(Base):
    __tablename__ = "findings"
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True)
    dimension: Mapped[str] = mapped_column(Text, primary_key=True)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    confirmed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    corrected_from: Mapped[str | None] = mapped_column(Text)


class GateResult(Base):
    __tablename__ = "gate_results"
    __table_args__ = (CheckConstraint(
        "classification IN ('now','later')", name="ck_classification"),)
    session_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("sessions.id", ondelete="CASCADE"),
        primary_key=True)
    g1: Mapped[bool] = mapped_column(Boolean, nullable=False)
    g2: Mapped[bool] = mapped_column(Boolean, nullable=False)
    g3: Mapped[bool] = mapped_column(Boolean, nullable=False)
    g4: Mapped[bool] = mapped_column(Boolean, nullable=False)
    classification: Mapped[str] = mapped_column(Text, nullable=False)
    failed_reason: Mapped[str | None] = mapped_column(Text)
    evaluated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)


class Document(Base):
    __tablename__ = "documents"
    __table_args__ = (
        CheckConstraint("kind IN ('proposal','later_memo')", name="ck_doc_kind"),
        CheckConstraint("status IN ('draft','approved','sent')", name="ck_doc_status"),
    )
    id: Mapped[uuid.UUID] = _uuid_pk()
    session_id: Mapped[uuid.UUID] = _session_fk()
    kind: Mapped[str] = mapped_column(Text, nullable=False)
    md_key: Mapped[str | None] = mapped_column(Text)
    pdf_key: Mapped[str | None] = mapped_column(Text)
    docx_key: Mapped[str | None] = mapped_column(Text)
    config_version: Mapped[str | None] = mapped_column(Text)
    checks: Mapped[dict | None] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(Text, nullable=False, default="draft")
    approved_by: Mapped[str | None] = mapped_column(Text)


class AuditLog(Base):
    __tablename__ = "audit_log"
    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    # Deliberately NOT a ForeignKey: audit rows must survive session deletion.
    session_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), index=True)
    actor: Mapped[str] = mapped_column(Text, nullable=False)
    event_type: Mapped[str] = mapped_column(Text, nullable=False)
    payload: Mapped[dict | None] = mapped_column(JSONB)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), nullable=False)
