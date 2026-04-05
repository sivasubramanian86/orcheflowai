"""
OrcheFlowAI — SQLAlchemy ORM Models
Mirrors the V001 SQL schema exactly.
"""
import uuid
from datetime import datetime, date
from typing import Optional, List
from sqlalchemy import (
    String, Text, Integer, Boolean, ForeignKey,
    DateTime, Date, BigInteger, ARRAY, func
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector
from db.session import Base


def _uuid() -> str:
    return str(uuid.uuid4())


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(Text)
    timezone: Mapped[str] = mapped_column(Text, default="UTC")
    preferences: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    tasks: Mapped[List["Task"]] = relationship(back_populates="user")
    notes: Mapped[List["Note"]] = relationship(back_populates="user")
    workflow_runs: Mapped[List["WorkflowRun"]] = relationship(back_populates="user")


class Task(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[str] = mapped_column(Text, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text)
    status: Mapped[str] = mapped_column(String(20), default="TODO")
    priority: Mapped[int] = mapped_column(Integer, default=3)
    due_date: Mapped[Optional[date]] = mapped_column(Date)
    tags: Mapped[List[str]] = mapped_column(ARRAY(Text), default=list)
    source_note_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))
    source_event_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False))
    extra_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="tasks")


class Note(Base):
    __tablename__ = "notes"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    title: Mapped[Optional[str]] = mapped_column(Text)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    content_type: Mapped[str] = mapped_column(String(20), default="REFERENCE")
    tags: Mapped[List[str]] = mapped_column(ARRAY(Text), default=list)
    embedding: Mapped[Optional[List[float]]] = mapped_column(Vector(768))
    extra_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    user: Mapped["User"] = relationship(back_populates="notes")


class CalendarEvent(Base):
    __tablename__ = "calendar_events"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    external_id: Mapped[Optional[str]] = mapped_column(Text)
    title: Mapped[str] = mapped_column(Text, nullable=False)
    start_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    end_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    event_type: Mapped[str] = mapped_column(String(20), default="MEETING")
    attendees: Mapped[list] = mapped_column(JSONB, default=list)
    notes_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("notes.id"))
    extra_metadata: Mapped[dict] = mapped_column(JSONB, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class WorkflowRun(Base):
    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    user_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("users.id", ondelete="CASCADE"))
    idempotency_key: Mapped[Optional[str]] = mapped_column(Text, unique=True)
    intent: Mapped[str] = mapped_column(Text, nullable=False)
    plan: Mapped[Optional[dict]] = mapped_column(JSONB)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    input_payload: Mapped[dict] = mapped_column(JSONB, default=dict)
    output_summary: Mapped[Optional[str]] = mapped_column(Text)
    error_details: Mapped[Optional[dict]] = mapped_column(JSONB)
    started_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    total_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped["User"] = relationship(back_populates="workflow_runs")
    steps: Mapped[List["WorkflowStep"]] = relationship(back_populates="run", order_by="WorkflowStep.step_index")


class WorkflowStep(Base):
    __tablename__ = "workflow_steps"

    id: Mapped[str] = mapped_column(UUID(as_uuid=False), primary_key=True, default=_uuid)
    run_id: Mapped[str] = mapped_column(UUID(as_uuid=False), ForeignKey("workflow_runs.id", ondelete="CASCADE"))
    step_index: Mapped[int] = mapped_column(Integer, nullable=False)
    step_name: Mapped[str] = mapped_column(Text, nullable=False)
    agent_name: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default="PENDING")
    input_context: Mapped[Optional[dict]] = mapped_column(JSONB)
    output_result: Mapped[Optional[dict]] = mapped_column(JSONB)
    error_message: Mapped[Optional[str]] = mapped_column(Text)
    started_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True))
    retry_count: Mapped[int] = mapped_column(Integer, default=0)

    run: Mapped["WorkflowRun"] = relationship(back_populates="steps")


class AgentAuditLog(Base):
    __tablename__ = "agent_audit_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    run_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("workflow_runs.id"))
    step_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("workflow_steps.id"))
    agent_name: Mapped[str] = mapped_column(Text, nullable=False)
    action: Mapped[str] = mapped_column(Text, nullable=False)
    details: Mapped[Optional[dict]] = mapped_column(JSONB)
    tokens_used: Mapped[Optional[int]] = mapped_column(Integer)
    logged_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class ToolCallLog(Base):
    __tablename__ = "tool_call_log"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    step_id: Mapped[Optional[str]] = mapped_column(UUID(as_uuid=False), ForeignKey("workflow_steps.id"))
    tool_name: Mapped[str] = mapped_column(Text, nullable=False)
    tool_input: Mapped[Optional[dict]] = mapped_column(JSONB)
    tool_output: Mapped[Optional[dict]] = mapped_column(JSONB)
    success: Mapped[bool] = mapped_column(Boolean, nullable=False)
    error_code: Mapped[Optional[str]] = mapped_column(Text)
    latency_ms: Mapped[Optional[int]] = mapped_column(Integer)
    called_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
