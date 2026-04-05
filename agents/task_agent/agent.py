"""
OrcheFlowAI — Task Agent (ADK-native)
Handles task creation, updates, listing, and priority scoring via MCP tools.
"""
import os
import time
import httpx
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from agents.base_agent import GEMINI_SUBAGENT_MODEL, log_tool_call

MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

TASK_AGENT_PROMPT = """
You are OrcheFlowAI Task Agent — specialist in task lifecycle management.

Your capabilities:
- create_task: Create a new task with title, priority, due date, and tags
- update_task: Update task status or metadata
- list_tasks: Retrieve tasks filtered by status, priority, or due date
- prioritize_tasks: Rank a task list using urgency × impact scoring

Priority scoring rules:
- Priority 1 (Critical): Deadline within 24h OR explicitly marked urgent
- Priority 2 (High): Deadline within 3 days OR client-facing
- Priority 3 (Medium): Deadline within 1 week OR standard work item
- Priority 4 (Low): No hard deadline, internal
- Priority 5 (Backlog): Nice-to-have, no deadline

When given action items to create:
1. Call create_task for each item
2. Return all created task objects as tasks_created[]
Always include source_note_id if provided in input context.
"""


async def create_task(
    title: str,
    priority: int = 3,
    due_date: str = None,
    description: str = "",
    tags: list = None,
    source_note_id: str = None,
) -> dict:
    """Create a task in the OrcheFlowAI task store via MCP."""
    start = time.monotonic()
    payload = {
        "title": title,
        "priority": priority,
        "description": description,
        "tags": tags or [],
    }
    if due_date:
        payload["due_date"] = due_date
    if source_note_id:
        payload["source_note_id"] = source_note_id

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{MCP_URL}/tools/task_manager/create_task",
                json=payload,
            )
            resp.raise_for_status()
            result = resp.json()
            await log_tool_call(
                step_id="", tool_name="task_manager.create_task",
                tool_input=payload, tool_output=result,
                success=True, latency_ms=int((time.monotonic() - start) * 1000),
            )
            return result
    except Exception as e:
        return {"error": str(e), "id": None}


async def list_tasks(status: str = "TODO", limit: int = 20) -> dict:
    """Retrieve tasks by status from the task store."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{MCP_URL}/tools/task_manager/list_tasks",
            params={"status": status, "limit": limit},
        )
        resp.raise_for_status()
        return resp.json()


async def update_task(task_id: str, status: str = None, priority: int = None) -> dict:
    """Update an existing task's status or priority."""
    payload = {"task_id": task_id}
    if status:
        payload["status"] = status
    if priority:
        payload["priority"] = priority
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.patch(
            f"{MCP_URL}/tools/task_manager/update_task",
            json=payload,
        )
        resp.raise_for_status()
        return resp.json()


async def prioritize_tasks(tasks: list) -> dict:
    """Re-rank a list of tasks by urgency × impact."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.post(
            f"{MCP_URL}/tools/task_manager/prioritize",
            json={"tasks": tasks},
        )
        resp.raise_for_status()
        return resp.json()


def build_task_agent() -> Agent:
    """Construct the ADK Task Agent with MCP-backed function tools."""
    return Agent(
        name="task_agent",
        model=GEMINI_SUBAGENT_MODEL,
        description="Specialist in creating, updating, listing, and prioritizing tasks.",
        instruction=TASK_AGENT_PROMPT,
        tools=[
            FunctionTool(create_task),
            FunctionTool(list_tasks),
            FunctionTool(update_task),
            FunctionTool(prioritize_tasks),
        ],
    )
