"""
OrcheFlowAI API — Workflow schemas (Pydantic v2)
Used by the workflow router for request/response validation.
"""
from __future__ import annotations

from typing import Any, Optional
from pydantic import BaseModel, Field


class WorkflowPayload(BaseModel):
    """Optional payload to supplement the workflow intent."""
    notes_content: Optional[str] = Field(None, max_length=50_000)
    date_context: Optional[str] = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")


class WorkflowRequest(BaseModel):
    """
    Incoming workflow request from the frontend or API consumer.
    Validates intent length and optional payload fields.
    """
    intent: str = Field(..., min_length=1, max_length=5000)
    user_id: str = Field(default="anonymous", max_length=128)
    payload: WorkflowPayload = Field(default_factory=WorkflowPayload)


class WorkflowResponse(BaseModel):
    """Returned immediately after workflow submission (202 Accepted)."""
    run_id: str
    status: str
    message: str = "Workflow accepted and processing"
