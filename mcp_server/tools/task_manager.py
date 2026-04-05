"""
OrcheFlowAI — MCP Task Manager Tool
CRUD and priority operations on tasks backed by AlloyDB/Postgres.
"""
import uuid
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from db.session import get_db
from db.models import Task

router = APIRouter()


class CreateTaskRequest(BaseModel):
    title: str
    description: Optional[str] = ""
    priority: int = 3
    due_date: Optional[str] = None
    tags: list[str] = []
    source_note_id: Optional[str] = None
    user_id: str = "demo-user"


class PrioritizeRequest(BaseModel):
    tasks: list[dict]


@router.post("/create_task")
async def create_task(body: CreateTaskRequest, db: AsyncSession = Depends(get_db)):
    task = Task(
        id=str(uuid.uuid4()),
        user_id=body.user_id,
        title=body.title,
        description=body.description,
        priority=body.priority,
        tags=body.tags,
        source_note_id=body.source_note_id,
        status="TODO",
    )
    if body.due_date:
        from datetime import date
        task.due_date = date.fromisoformat(body.due_date)

    db.add(task)
    await db.commit()
    await db.refresh(task)
    return {
        "id": task.id,
        "title": task.title,
        "status": task.status,
        "priority": task.priority,
        "due_date": str(task.due_date) if task.due_date else None,
        "created_at": task.created_at.isoformat(),
    }


@router.get("/list_tasks")
async def list_tasks(
    status: str = "TODO",
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Task)
        .where(Task.status == status)
        .order_by(Task.priority.asc(), Task.due_date.asc())
        .limit(limit)
    )
    tasks = result.scalars().all()
    return {
        "tasks": [
            {
                "id": t.id,
                "title": t.title,
                "status": t.status,
                "priority": t.priority,
                "due_date": str(t.due_date) if t.due_date else None,
                "tags": t.tags,
            }
            for t in tasks
        ]
    }


@router.patch("/update_task")
async def update_task(body: dict, db: AsyncSession = Depends(get_db)):
    task_id = body.get("task_id")
    updates = {k: v for k, v in body.items() if k != "task_id"}
    updates["updated_at"] = datetime.utcnow()
    await db.execute(update(Task).where(Task.id == task_id).values(**updates))
    await db.commit()
    return {"updated": True, "task_id": task_id}


@router.post("/prioritize")
async def prioritize_tasks(body: PrioritizeRequest):
    """
    Re-sorts tasks by urgency × impact heuristic.
    Priority 1 tasks with earliest due dates rank first.
    """
    from datetime import date, timedelta

    def score(t):
        p = t.get("priority", 3)
        due = t.get("due_date")
        if due:
            days_left = (date.fromisoformat(due) - date.today()).days
            urgency = max(0, 10 - days_left)
        else:
            urgency = 0
        return (p * 10) - urgency  # lower = higher priority

    sorted_tasks = sorted(body.tasks, key=score)
    return {"tasks": sorted_tasks}
