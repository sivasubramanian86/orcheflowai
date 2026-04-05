"""OrcheFlowAI — Tasks Router"""
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import Task

router = APIRouter()


class CreateTaskBody(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: int = 3
    due_date: Optional[str] = None
    tags: list[str] = []


@router.get("")
async def list_tasks(
    status: Optional[str] = None,
    priority_lte: Optional[int] = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
):
    query = select(Task).order_by(Task.priority.asc(), Task.due_date.asc()).limit(limit)
    if status:
        query = query.where(Task.status == status)
    if priority_lte:
        query = query.where(Task.priority <= priority_lte)
    result = await db.execute(query)
    tasks = result.scalars().all()
    return {
        "tasks": [
            {"id": t.id, "title": t.title, "status": t.status,
             "priority": t.priority, "due_date": str(t.due_date) if t.due_date else None}
            for t in tasks
        ]
    }
