"""
OrcheFlowAI — Life Canvas Router
Aggregates data for the Today / This Week timeline view.
"""
from datetime import datetime, date, timedelta
from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from db.models import Task, CalendarEvent, HealthSnapshot, CommuteSegment

router = APIRouter()

# --- Response Schemas ---

class TimelineEvent(BaseModel):
    id: str
    title: str
    start: datetime
    end: datetime
    type: str # MEETING, TASK, COMMUTE, HEALTH
    status: Optional[str] = None
    metadata: dict = {}

class CanvasAggregationResponse(BaseModel):
    date: date
    tracks: dict # { "calendar": [...], "tasks": [...], "commute": [...], "health": [...] }

# --- Endpoints ---

@router.get("/day", response_model=CanvasAggregationResponse)
async def get_day_canvas(
    target_date: date = Query(default_factory=date.today),
    db: AsyncSession = Depends(get_db),
):
    """
    Fetches an aggregated view of the user's day across all tracks.
    In a real system, this would trigger background syncs to Google APIs.
    For the hackathon, it pulls from the local AlloyDB cache.
    """
    # In production, this would come from a JWT/Session
    user_id = "01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f"
    
    # 1. Fetch Calendar Events
    start_dt = datetime.combine(target_date, datetime.min.time())
    end_dt = start_dt + timedelta(days=1)
    
    cal_query = select(CalendarEvent).where(
        CalendarEvent.user_id == user_id,
        CalendarEvent.start_time >= start_dt,
        CalendarEvent.start_time < end_dt
    )
    cal_results = (await db.execute(cal_query)).scalars().all()
    
    # 2. Fetch Tasks due today
    task_query = select(Task).where(
        Task.user_id == user_id,
        Task.due_date == target_date
    )
    task_results = (await db.execute(task_query)).scalars().all()
    
    # 3. Fetch Commute segments
    commute_query = select(CommuteSegment).where(
        CommuteSegment.user_id == user_id,
        CommuteSegment.created_at >= start_dt,
        CommuteSegment.created_at < end_dt
    )
    commute_results = (await db.execute(commute_query)).scalars().all()
    
    # 4. Fetch Health Snapshot
    health_query = select(HealthSnapshot).where(
        HealthSnapshot.user_id == user_id,
        HealthSnapshot.snapshot_date == target_date
    )
    health_result = (await db.execute(health_query)).scalar_one_or_none()
    
    return {
        "date": target_date,
        "tracks": {
            "calendar": [
                {
                    "id": e.id,
                    "title": e.title,
                    "start": e.start_time,
                    "end": e.end_time,
                    "type": "MEETING",
                    "metadata": e.extra_metadata or {}
                } for e in cal_results
            ],
            "tasks": [
                {
                    "id": t.id,
                    "title": t.title,
                    "start": datetime.combine(target_date, datetime.min.time()),
                    "end": datetime.combine(target_date, datetime.min.time()) + timedelta(minutes=30),
                    "type": "TASK",
                    "status": t.status or "PENDING",
                    "metadata": t.extra_metadata or {}
                } for t in task_results
            ],
            "commute": [
                {
                    "id": c.id,
                    "title": f"Commute: {c.origin_address or 'Unknown'} to {c.destination_address or 'Unknown'}",
                    "start": c.created_at or datetime.now(),
                    "end": (c.created_at or datetime.now()) + timedelta(minutes=c.travel_time_minutes or 0),
                    "type": "COMMUTE",
                    "metadata": {"mode": c.transport_mode or "UNKNOWN"}
                } for c in commute_results
            ],
            "health": {
                "steps": health_result.steps if health_result else 0,
                "sleep_minutes": health_result.sleep_minutes if health_result else 0,
                "readiness": health_result.readiness_score if health_result else 80,
                "metrics": health_result.metrics if health_result else {}
            }
        }
    }
