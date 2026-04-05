"""
OrcheFlowAI — MCP Calendar Manager Tool
Provides event listing, gap detection, and focus block creation.
Uses in-memory mock calendar for local dev; swap for Google Calendar API in prod.
"""
import uuid
from datetime import datetime, date, timedelta
from typing import Optional
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.session import get_db
from db.models import CalendarEvent

router = APIRouter()

# ─── Mock calendar seed (local dev only) ──────────────────────────
MOCK_EVENTS = [
    {"start": "09:00", "end": "10:00", "title": "Team Standup", "type": "MEETING"},
    {"start": "11:00", "end": "12:00", "title": "Client Call", "type": "MEETING"},
    {"start": "15:00", "end": "16:00", "title": "Design Review", "type": "MEETING"},
]


@router.get("/events")
async def list_events(date: str, days: int = 1, db: AsyncSession = Depends(get_db)):
    """Read calendar events from DB (or mock for local dev)."""
    try:
        target_date = date_obj = datetime.fromisoformat(date).date()
        end_date = target_date + timedelta(days=days)

        result = await db.execute(
            select(CalendarEvent)
            .where(
                CalendarEvent.start_time >= datetime.combine(target_date, datetime.min.time()),
                CalendarEvent.start_time < datetime.combine(end_date, datetime.min.time()),
            )
            .order_by(CalendarEvent.start_time)
        )
        events = result.scalars().all()

        if not events:
            # Return mock events for demo
            return {"date": date, "events": MOCK_EVENTS}

        return {
            "date": date,
            "events": [
                {
                    "id": e.id,
                    "title": e.title,
                    "start": e.start_time.isoformat(),
                    "end": e.end_time.isoformat(),
                    "type": e.event_type,
                }
                for e in events
            ],
        }
    except Exception:
        return {"date": date, "events": MOCK_EVENTS}


@router.get("/free_slots")
async def find_free_slots(
    date: str,
    min_duration_minutes: int = 90,
    work_start_hour: int = 9,
    work_end_hour: int = 18,
    db: AsyncSession = Depends(get_db),
):
    """Find free time slots by computing gaps between existing events."""
    events_resp = await list_events(date=date, db=db)
    events = events_resp.get("events", [])

    # Build occupied windows
    occupied = []
    for e in events:
        start_str = e.get("start") or f"{date}T{e.get('start_time', '09:00')}:00"
        end_str = e.get("end") or f"{date}T{e.get('end_time', '10:00')}:00"
        try:
            occupied.append((
                datetime.fromisoformat(start_str),
                datetime.fromisoformat(end_str),
            ))
        except ValueError:
            # Handle HH:MM format from mock
            start_t = e.get("start", "09:00")
            end_t = e.get("end", "10:00")
            base = date
            occupied.append((
                datetime.fromisoformat(f"{base}T{start_t}:00"),
                datetime.fromisoformat(f"{base}T{end_t}:00"),
            ))

    occupied.sort()

    # Compute gaps
    work_start = datetime.fromisoformat(f"{date}T{work_start_hour:02d}:00:00")
    work_end = datetime.fromisoformat(f"{date}T{work_end_hour:02d}:00:00")
    gaps = []
    current = work_start

    for occ_start, occ_end in occupied:
        if current + timedelta(minutes=min_duration_minutes) <= occ_start:
            gaps.append({
                "start": current.isoformat(),
                "end": occ_start.isoformat(),
                "duration_minutes": int((occ_start - current).total_seconds() / 60),
            })
        current = max(current, occ_end)

    if current + timedelta(minutes=min_duration_minutes) <= work_end:
        gaps.append({
            "start": current.isoformat(),
            "end": work_end.isoformat(),
            "duration_minutes": int((work_end - current).total_seconds() / 60),
        })

    return {"date": date, "gaps": gaps}


@router.post("/block_time")
async def block_focus_time(body: dict, db: AsyncSession = Depends(get_db)):
    """Create a FOCUS_BLOCK calendar event in the DB."""
    target_date = body.get("date")
    start_time_str = body.get("start_time", "09:00:00")
    duration = body.get("duration_minutes", 120)
    title = body.get("title", "OrcheFlow Focus Block")

    start_dt = datetime.fromisoformat(f"{target_date}T{start_time_str}")
    end_dt = start_dt + timedelta(minutes=duration)

    event = CalendarEvent(
        id=str(uuid.uuid4()),
        user_id="demo-user",
        title=title,
        start_time=start_dt,
        end_time=end_dt,
        event_type="FOCUS_BLOCK",
    )
    db.add(event)
    await db.commit()
    await db.refresh(event)

    return {
        "event_id": event.id,
        "title": event.title,
        "start": event.start_time.isoformat(),
        "end": event.end_time.isoformat(),
        "type": "FOCUS_BLOCK",
    }
