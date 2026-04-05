"""OrcheFlowAI — Schedule Router"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db
import httpx, os

router = APIRouter()
MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")


@router.get("/gaps")
async def get_gaps(date: str, min_duration_minutes: int = 60):
    """Proxy to MCP calendar_manager free_slots."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{MCP_URL}/tools/calendar_manager/free_slots",
            params={"date": date, "min_duration_minutes": min_duration_minutes},
        )
        resp.raise_for_status()
        return resp.json()


@router.get("/events")
async def get_events(date: str, days: int = 1):
    """Proxy to MCP calendar_manager events."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{MCP_URL}/tools/calendar_manager/events",
            params={"date": date, "days": days},
        )
        resp.raise_for_status()
        return resp.json()
