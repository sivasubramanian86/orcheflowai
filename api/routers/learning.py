"""
OrcheFlowAI — Learning Capsules Router
Manages YouTube learning timeboxes.
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from db.session import get_db
from db.models import LearningCapsule

router = APIRouter()

# --- Schemas ---

class CapsuleResponse(BaseModel):
    id: str
    video_id: str
    title: str
    url: str
    topic: str
    duration_minutes: int
    status: str # PLANNED, COMPLETED, SKIPPED
    scheduled_event_id: Optional[str] = None

class CreateCapsuleRequest(BaseModel):
    video_id: str
    title: str
    topic: str
    duration_minutes: int = 30

# --- Endpoints ---

@router.get("/", response_model=List[CapsuleResponse])
async def list_capsules(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """List YouTube learning capsules for the user."""
    user_id = "01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f"
    query = select(LearningCapsule).where(LearningCapsule.user_id == user_id)
    if status:
        query = query.where(LearningCapsule.status == status)
    
    result = await db.execute(query)
    capsules = result.scalars().all()
    
    return [
        {
            "id": c.id,
            "video_id": c.video_id,
            "title": c.title,
            "url": f"https://www.youtube.com/watch?v={c.video_id}",
            "topic": c.topic,
            "duration_minutes": c.duration_minutes,
            "status": c.status,
            "scheduled_event_id": c.scheduled_event_id
        } for c in capsules
    ]

@router.post("/create")
async def create_capsule(body: CreateCapsuleRequest, db: AsyncSession = Depends(get_db)):
    """Add a new learning capsule manually (eventually automated by ContentAgent)."""
    user_id = "01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f"
    
    capsule = LearningCapsule(
        user_id=user_id,
        video_id=body.video_id,
        title=body.title,
        url=f"https://www.youtube.com/watch?v={body.video_id}",
        topic=body.topic,
        duration_minutes=body.duration_minutes,
        status="PLANNED"
    )
    db.add(capsule)
    await db.commit()
    return {"status": "ok", "id": capsule.id}

@router.post("/{capsule_id}/status")
async def update_capsule_status(
    capsule_id: str, 
    status: str, 
    db: AsyncSession = Depends(get_db)
):
    """Mark a learning capsule as completed or skipped."""
    if status not in ["PLANNED", "COMPLETED", "SKIPPED"]:
        raise HTTPException(status_code=400, detail="Invalid status.")
        
    user_id = "01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f"
    result = await db.execute(select(LearningCapsule).where(
        LearningCapsule.id == capsule_id,
        LearningCapsule.user_id == user_id
    ))
    capsule = result.scalar_one_or_none()
    
    if not capsule:
        raise HTTPException(status_code=404, detail="Capsule not found.")
        
    capsule.status = status
    await db.commit()
    return {"status": "ok", "updated_to": status}
