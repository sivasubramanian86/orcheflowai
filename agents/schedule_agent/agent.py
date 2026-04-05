"""
OrcheFlowAI — Schedule Agent (ADK-native)
Handles calendar operations: reading events, finding free gaps, blocking focus time.
"""
import os
import time
import httpx
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from agents.base_agent import GEMINI_SUBAGENT_MODEL, log_tool_call

MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

SCHEDULE_AGENT_PROMPT = """
You are OrcheFlowAI Schedule Agent — specialist in calendar management and time optimization.

Your capabilities:
- list_events: Fetch existing calendar events for a given date range
- find_free_slots: Identify genuine free slots on a given date (accounting for buffer time)
- block_focus_time: Create a focus block in the calendar for deep work
- move_event: Reschedule an existing event

Focus block rules:
- Minimum block duration: 90 minutes
- Add 15-min buffer before and after blocks
- Label: "OrcheFlow Focus: [top task title]"
- Prefer morning slots (9am-12pm) for deep work unless user preference differs
- Never double-book over an existing confirmed meeting

When asked to find time and block it:
1. Call list_events to understand what's already scheduled
2. Call find_free_slots to identify available windows
3. Call block_focus_time for the best available slot
4. Return blocks_created[] with ISO datetimes
"""


async def list_events(date: str, days: int = 1) -> dict:
    """Fetch calendar events for a given date range."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{MCP_URL}/tools/calendar_manager/events",
            params={"date": date, "days": days},
        )
        resp.raise_for_status()
        return resp.json()


async def find_free_slots(
    date: str,
    min_duration_minutes: int = 90,
    work_start_hour: int = 9,
    work_end_hour: int = 18,
) -> dict:
    """Find free time slots on a given date."""
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(
                f"{MCP_URL}/tools/calendar_manager/free_slots",
                params={
                    "date": date,
                    "min_duration_minutes": min_duration_minutes,
                    "work_start_hour": work_start_hour,
                    "work_end_hour": work_end_hour,
                },
            )
            resp.raise_for_status()
            result = resp.json()
            await log_tool_call(
                step_id="", tool_name="calendar_manager.find_free_slots",
                tool_input={"date": date, "min_duration_minutes": min_duration_minutes},
                tool_output=result, success=True,
                latency_ms=int((time.monotonic() - start) * 1000),
            )
            return result
    except Exception as e:
        return {"error": str(e), "gaps": []}


async def block_focus_time(
    date: str,
    start_time: str,
    duration_minutes: int,
    title: str = "OrcheFlow Focus Block",
) -> dict:
    """Create a focus block in the calendar."""
    start = time.monotonic()
    payload = {
        "date": date,
        "start_time": start_time,
        "duration_minutes": duration_minutes,
        "title": title,
        "event_type": "FOCUS_BLOCK",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{MCP_URL}/tools/calendar_manager/block_time",
                json=payload,
            )
            resp.raise_for_status()
            result = resp.json()
            await log_tool_call(
                step_id="", tool_name="calendar_manager.block_focus_time",
                tool_input=payload, tool_output=result, success=True,
                latency_ms=int((time.monotonic() - start) * 1000),
            )
            return result
    except Exception as e:
        return {"error": str(e), "event_id": None}


def build_schedule_agent() -> Agent:
    """Construct the ADK Schedule Agent with MCP-backed calendar tools."""
    return Agent(
        name="schedule_agent",
        model=GEMINI_SUBAGENT_MODEL,
        description="Specialist in reading calendar events, finding free time, and blocking focus windows.",
        instruction=SCHEDULE_AGENT_PROMPT,
        tools=[
            FunctionTool(list_events),
            FunctionTool(find_free_slots),
            FunctionTool(block_focus_time),
        ],
    )
