"""
OrcheFlowAI — ADK Base Agent
All sub-agents are built as google.adk.agents.Agent instances.
Uses Vertex AI (ADC) — no API key required.
This module provides shared utilities: audit logging, structured output, session management.
"""
import os
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Optional

import httpx
import structlog
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from google.adk.agents import Agent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner

# Initialize Vertex AI at module load (ADC — no API key)
from agents.vertex_init import init_vertex_ai, ORCHESTRATOR_MODEL, SUBAGENT_MODEL
init_vertex_ai()

log = structlog.get_logger()

# Expose for sub-agents to import
GEMINI_ORCHESTRATOR_MODEL = ORCHESTRATOR_MODEL   # vertex-ai:gemini-2.5-flash
GEMINI_SUBAGENT_MODEL     = SUBAGENT_MODEL        # vertex-ai:gemini-2.0-flash


# ─── Shared ADK Session Service (in-process, swap for DB-backed in prod) ──────
session_service = InMemorySessionService()

APP_NAME = "orcheflow"


async def create_adk_session(user_id: str, run_id: str) -> str:
    """Create a new ADK session for a workflow run. Returns session_id."""
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=user_id,
        session_id=run_id,          # reuse run_id as session_id for traceability
    )
    return session.id


async def run_adk_agent(
    agent: Agent,
    user_id: str,
    session_id: str,
    message: str,
) -> str:
    """
    Execute an ADK agent with a single user message.
    Returns the final text response from the agent.
    """
    runner = Runner(
        agent=agent,
        app_name=APP_NAME,
        session_service=session_service,
    )

    from google.adk.types import Content, Part
    user_content = Content(role="user", parts=[Part(text=message)])

    final_response = ""
    async for event in runner.run_async(
        user_id=user_id,
        session_id=session_id,
        new_message=user_content,
    ):
        if event.is_final_response() and event.content:
            for part in event.content.parts:
                if part.text:
                    final_response += part.text

    return final_response


# ─── Audit Logging Utility (shared across all agents) ─────────────────────────

async def write_audit_log(
    run_id: str,
    step_id: str,
    agent_name: str,
    action: str,
    details: dict,
    tokens_used: int = 0,
    api_base: str = "",
):
    """
    Append an entry to agent_audit_log via internal API.
    Fire-and-forget — never raises on failure.
    """
    api_base = api_base or os.getenv("API_SERVICE_URL", "http://localhost:8000")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{api_base}/internal/audit",
                json={
                    "run_id": run_id,
                    "step_id": step_id,
                    "agent_name": agent_name,
                    "action": action,
                    "details": details,
                    "tokens_used": tokens_used,
                    "logged_at": datetime.now(timezone.utc).isoformat(),
                },
            )
    except Exception as e:
        log.warning("audit_write_failed", agent=agent_name, error=str(e))


# ─── MCP Tool Call Logger ──────────────────────────────────────────────────────

async def log_tool_call(
    step_id: str,
    tool_name: str,
    tool_input: dict,
    tool_output: dict,
    success: bool,
    latency_ms: int,
    error_code: Optional[str] = None,
    api_base: str = "",
):
    """Appends a tool_call_log entry. Fire-and-forget."""
    api_base = api_base or os.getenv("API_SERVICE_URL", "http://localhost:8000")
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            await client.post(
                f"{api_base}/internal/tool-log",
                json={
                    "step_id": step_id,
                    "tool_name": tool_name,
                    "tool_input": tool_input,
                    "tool_output": tool_output,
                    "success": success,
                    "latency_ms": latency_ms,
                    "error_code": error_code,
                },
            )
    except Exception as e:
        log.warning("tool_log_write_failed", tool=tool_name, error=str(e))
