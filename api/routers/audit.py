"""OrcheFlowAI — Audit Router"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import AgentAuditLog, ToolCallLog
from typing import Optional

router = APIRouter()


@router.get("")
async def get_audit_log(
    run_id: Optional[str] = None,
    agent: Optional[str] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
):
    query = select(AgentAuditLog).order_by(AgentAuditLog.logged_at.desc()).limit(limit)
    if run_id:
        query = query.where(AgentAuditLog.run_id == run_id)
    if agent:
        query = query.where(AgentAuditLog.agent_name == agent)
    result = await db.execute(query)
    logs = result.scalars().all()
    return {
        "entries": [
            {
                "id": l.id,
                "run_id": l.run_id,
                "agent_name": l.agent_name,
                "action": l.action,
                "details": l.details,
                "tokens_used": l.tokens_used,
                "logged_at": l.logged_at.isoformat(),
            }
            for l in logs
        ]
    }


@router.post("/internal/audit")
async def write_audit(body: dict, db: AsyncSession = Depends(get_db)):
    """Internal endpoint for agents to write audit log entries."""
    from datetime import datetime
    log_entry = AgentAuditLog(
        run_id=body.get("run_id"),
        step_id=body.get("step_id"),
        agent_name=body.get("agent_name", "unknown"),
        action=body.get("action", "UNKNOWN"),
        details=body.get("details"),
        tokens_used=body.get("tokens_used", 0),
    )
    db.add(log_entry)
    await db.commit()
    return {"written": True}
