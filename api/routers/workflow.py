"""
OrcheFlowAI — Workflow Router
Core endpoint: POST /v1/workflow/run
"""
import os
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from pydantic import BaseModel, Field
import httpx

from db.session import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models import WorkflowRun

router = APIRouter()

AGENT_SERVICE_URL = os.getenv("AGENT_SERVICE_URL", "http://localhost:8002")


# ─── Request / Response Schemas ───────────────────────────────────

class WorkflowRunRequest(BaseModel):
    intent: str = Field(..., min_length=5, max_length=2000)
    payload: dict = Field(default_factory=dict)
    idempotency_key: Optional[str] = None
    mode: str = Field(default="sync", pattern="^(sync|async)$")


class WorkflowRunResponse(BaseModel):
    run_id: str
    status: str
    plan_executed: list[str]
    tasks_created: list[dict]
    calendar_blocks: list[dict]
    summary: str
    tokens_used: int
    duration_ms: int


# ─── Endpoints ────────────────────────────────────────────────────

@router.post("/run", response_model=WorkflowRunResponse, status_code=200)
async def run_workflow(
    body: WorkflowRunRequest,
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(...),
):
    """
    Trigger a multi-agent workflow from a natural language intent.
    Supports idempotency via idempotency_key.
    """
    # Check idempotency
    if body.idempotency_key:
        existing = await db.execute(
            select(WorkflowRun).where(WorkflowRun.idempotency_key == body.idempotency_key)
        )
        run = existing.scalar_one_or_none()
        if run and run.status == "COMPLETED":
            raise HTTPException(status_code=409, detail="Duplicate request — workflow already completed.")

    # Create WorkflowRun record
    run_id = str(uuid.uuid4())
    run = WorkflowRun(
        id=run_id,
        user_id="demo-user",  # Replace with JWT-parsed user_id in production
        idempotency_key=body.idempotency_key,
        intent=body.intent,
        status="PENDING",
        input_payload=body.payload,
    )
    db.add(run)
    await db.commit()

    # Dispatch to Agent Service
    start = datetime.utcnow()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{AGENT_SERVICE_URL}/internal/orchestrate",
                json={
                    "run_id": run_id,
                    "intent": body.intent,
                    "payload": body.payload,
                    "user_id": "demo-user",
                },
            )
            response.raise_for_status()
            result = response.json()
    except httpx.HTTPError as e:
        run.status = "FAILED"
        run.error_details = {"error": str(e)}
        await db.commit()
        raise HTTPException(status_code=502, detail=f"Agent service error: {str(e)}")

    duration_ms = int((datetime.utcnow() - start).total_seconds() * 1000)

    return WorkflowRunResponse(
        run_id=run_id,
        status=result.get("status", "COMPLETED"),
        plan_executed=result.get("plan_executed", []),
        tasks_created=result.get("tasks_created", []),
        calendar_blocks=result.get("calendar_blocks", []),
        summary=result.get("summary", ""),
        tokens_used=result.get("tokens_used", 0),
        duration_ms=duration_ms,
    )


@router.get("/runs")
async def list_runs(
    db: AsyncSession = Depends(get_db),
    limit: int = 20,
    status: Optional[str] = None,
):
    """List past workflow runs for the current user."""
    query = select(WorkflowRun).order_by(WorkflowRun.created_at.desc()).limit(limit)
    if status:
        query = query.where(WorkflowRun.status == status)
    result = await db.execute(query)
    runs = result.scalars().all()
    return {
        "items": [
            {
                "run_id": r.id,
                "intent": r.intent,
                "status": r.status,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in runs
        ]
    }


@router.get("/runs/{run_id}/steps")
async def get_run_steps(run_id: str, db: AsyncSession = Depends(get_db)):
    """Get step-by-step execution trace for a workflow run."""
    run_result = await db.execute(select(WorkflowRun).where(WorkflowRun.id == run_id))
    run = run_result.scalar_one_or_none()
    if not run:
        raise HTTPException(status_code=404, detail="Workflow run not found.")

    return {
        "run_id": run_id,
        "intent": run.intent,
        "status": run.status,
        "steps": [
            {
                "step_index": s.step_index,
                "step_name": s.step_name,
                "agent_name": s.agent_name,
                "status": s.status,
                "output_result": s.output_result,
                "error_message": s.error_message,
                "retry_count": s.retry_count,
                "started_at": s.started_at.isoformat() if s.started_at else None,
                "completed_at": s.completed_at.isoformat() if s.completed_at else None,
            }
            for s in run.steps
        ],
    }
