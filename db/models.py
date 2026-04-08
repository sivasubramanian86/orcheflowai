"""
OrcheFlowAI — SQLAlchemy ORM Models
Mirrors the V001 SQL schema exactly.
"""
import os
import uuid
from datetime import datetime, date
from typing import Optional, List

from sqlalchemy import (
    String, Text, Integer, Boolean, ForeignKey,
    DateTime, Date, BigInteger, JSON, func, TypeDecorator
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, JSONB as PG_JSONB, ARRAY as PG_ARRAY
try:
    from pgvector.sqlalchemy import Vector as PG_Vector
except ImportError:
    PG_Vector = Text

# Resilient Type Mapping — These classes handle the translation between PG and SQLite at runtime
class JSONB_Type(TypeDecorator):
    impl = JSON
    cache_ok = True
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_JSONB())
        return dialect.type_descriptor(JSON())

class ARRAY_Type(TypeDecorator):
    impl = JSON
    cache_ok = True
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_ARRAY(Text))
        return dialect.type_descriptor(JSON())

class UUID_Type(TypeDecorator):
    impl = String
    cache_ok = True
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_UUID())
        return dialect.type_descriptor(String(36))

class Vector_Type(TypeDecorator):
    impl = JSON
    cache_ok = True
    def __init__(self, dim=768):
        self.dim = dim
        super().__init__()
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PG_Vector(self.dim))
        return dialect.type_descriptor(JSON())

# Alias for models
JSONB = JSONB_Type
ARRAY = ARRAY_Type
UUID = UUID_Type
Vector = Vector_Type

from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(Text)
    timezone: Mapped[str] = mapped_column(Text, default="UTC")
    preferences: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tasks: Mapped[List["Task"]] = relationship(back_populates="user")
    notes: Mapped[List["Note"]] = relationship(back_populates="user")
    workflow_runs: Mapped[List["WorkflowRun"]] = relationship(back_populates="user")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(UUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="TODO")
    priority: Mapped[int] = mapped_column(Integer, default=3)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    tags: Mapped[List[str]] = mapped_column(ARRAY(), default=list)
    source_note_id: Mapped[Optional[str]] = mapped_column(UUID())
    source_event_id: Mapped[Optional[str]] = mapped_column(UUID())
    extra_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="tasks")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(UUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(20), default="REFERENCE")
    tags: Mapped[List[str]] = mapped_column(ARRAY(), default=list)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(768))
    extra_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="notes")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[str] = mapped_column(UUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(), ForeignKey("users.id", ondelete="CASCADE"))
    external_id: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(20), default="MEETING")
    attendees: Mapped[list] = mapped_column(JSON, default=list)
    notes_id: Mapped[Optional[str]] = mapped_column(UUID(), ForeignKey("notes.id"))
    extra_metadata: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(UUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(), ForeignKey("users.id", ondelete="CASCADE"))
    idempotency_key: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    intent: Mapped[str] = mapped_column(Text, nullable=False)
    plan: Mapped[Optional[dict]] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    input_payload: Mapped[dict] = mapped_column(JSON, default=dict)
    output_summary: Mapped[Optional[str]] = mapped_column(Text)
    error_details: Mapped[Optional[dict]] = mapped_column(JSON)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="workflow_runs")
    steps: Mapped[List["WorkflowStep"]] = relationship(back_populates="run", order_by="WorkflowStep.step_index")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id: Mapped[str] = mapped_column(UUID(), primary_key=True, default=_uuid)
    run_id: Mapped[str] = mapped_column(UUID(), ForeignKey("workflow_runs.id", ondelete="CASCADE"))
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(Text, nullable=False)
    agent_name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    input_context: Mapped[Optional[dict]] = mapped_column(JSON)
    output_result: Mapped[Optional[dict]] = mapped_column(JSON)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    run: Mapped["WorkflowRun"] = relationship(back_populates="steps")


class AgentAuditLog(Base):
    __tablename__ = "agent_audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[Optional[str]] = mapped_column(UUID(), ForeignKey("workflow_runs.id"))
    step_id: Mapped[Optional[str]] = mapped_column(UUID(), ForeignKey("workflow_steps.id"))
    agent_name: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSON)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ToolCallLog(Base):
    __tablename__ = "tool_call_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    step_id: Mapped[Optional[str]] = mapped_column(UUID(), ForeignKey("workflow_steps.id"))
    tool_name: Mapped[str] = mapped_column(Text, nullable=False)
    tool_input: Mapped[Optional[dict]] = mapped_column(JSON)
    tool_output: Mapped[Optional[dict]] = mapped_column(JSON)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(Text)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    called_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserMode(Base):
    """Stores the current active personality/constraint of the system per user."""

    __tablename__ = "user_modes"

    user_id: Mapped[str] = mapped_column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True)
    active_mode: Mapped[str] = mapped_column(String(20), default="FOCUS")  # FOCUS, SOCIAL, RECOVERY
    auto_switch_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class HealthSnapshot(Base):
    """Aggregated metrics from Google Fit for Radar/Timeline Visualization."""

    __tablename__ = "health_snapshots"

    id: Mapped[str] = mapped_column(UUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(), ForeignKey("users.id", ondelete="CASCADE"))
    snapshot_date: Mapped[date] = mapped_column(Date, index=True)
    steps: Mapped[int] = mapped_column(Integer, default=0)
    sleep_minutes: Mapped[int] = mapped_column(Integer, default=0)
    readiness_score: Mapped[int] = mapped_column(Integer, default=80)  # 1-100 derived from biometric delta
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)  # HRV, HR, Activity Intensity
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class LearningCapsule(Base):
    """YouTube-based educational timeboxes."""

    __tablename__ = "learning_capsules"

    id: Mapped[str] = mapped_column(UUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(), ForeignKey("users.id", ondelete="CASCADE"))
    video_id: Mapped[str] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text)
    url: Mapped[str] = mapped_column(Text)
    topic: Mapped[str] = mapped_column(Text)
    duration_minutes: Mapped[int] = mapped_column(Integer, default=30)
    status: Mapped[str] = mapped_column(String(20), default="PLANNED")  # PLANNED, COMPLETED, SKIPPED
    scheduled_event_id: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class CommuteSegment(Base):
    """Predictive travel time between calendar events using Maps Distance Matrix."""

    __tablename__ = "commute_segments"

    id: Mapped[str] = mapped_column(UUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(), ForeignKey("users.id", ondelete="CASCADE"))
    event_id: Mapped[Optional[str]] = mapped_column(UUID(), ForeignKey("calendar_events.id", ondelete="CASCADE"))
    origin_address: Mapped[str] = mapped_column(Text)
    destination_address: Mapped[str] = mapped_column(Text)
    travel_time_minutes: Mapped[int] = mapped_column(Integer)
    transport_mode: Mapped[str] = mapped_column(String(20), default="DRIVING")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class UserCredential(Base):
    """Securely stores OAuth 2.0 credentials for external services (Google)."""

    __tablename__ = "user_credentials"

    id: Mapped[str] = mapped_column(UUID(), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(), ForeignKey("users.id", ondelete="CASCADE"), unique=True)
    service_name: Mapped[str] = mapped_column(String(50), default="google")
    access_token: Mapped[str] = mapped_column(Text)
    refresh_token: Mapped[Optional[str]] = mapped_column(Text)
    token_expiry: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    scopes: Mapped[List[str]] = mapped_column(ARRAY(), default=list)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
