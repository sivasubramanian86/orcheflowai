"""
OrcheFlowAI — Orchestrator Agent (ADK-native)
Uses google.adk.agents.Agent as the primary orchestrator.
Sub-agents are registered as AgentTools so the LLM can delegate naturally.
"""
import os
import json
import uuid
from typing import Any

import structlog
from google.adk.agents import Agent
from google.adk.tools import agent_tool

from agents.base_agent import (
    run_adk_agent,
    create_adk_session,
    write_audit_log,
    GEMINI_ORCHESTRATOR_MODEL,
)
from agents.task_agent.agent import build_task_agent
from agents.notes_agent.agent import build_notes_agent
from agents.schedule_agent.agent import build_schedule_agent
from agents.workflow_agent.agent import build_workflow_agent
from agents.data_agent.agent import build_data_agent
from agents.environment_agent.agent import build_environment_agent

log = structlog.get_logger()

ORCHESTRATOR_SYSTEM_PROMPT = """
You are OrcheFlowAI Orchestrator — the primary AI coordinator for a multi-agent productivity system.

Your role:
1. Understand the user's productivity intent precisely.
2. Break it into concrete steps.
3. Delegate each step to the right specialist sub-agent using available agent tools.
4. Collect each result, pass relevant context forward, and compile the final output.

Available sub-agents (use them via their agent tools):
- task_agent: create, update, list, and prioritize tasks
- schedule_agent: find calendar gaps, block focus time, read events
- notes_agent: ingest raw notes, extract action items, search knowledge
- environment_agent: get real-time weather and recovery window statuses
- data_agent: ingest bulk data from GCS to AlloyDB, perform complex SQL querying
- workflow_agent: compile final summary and generate plan documents

Operating rules:
- Delegate work — never execute tool calls yourself
- Always end by calling workflow_agent to summarize all results
- Pass only the minimal required context to each sub-agent
- If a sub-agent returns an error, log it and continue with remaining steps
- Return a final structured JSON with keys: plan_executed, tasks_created, calendar_blocks, environmental_window, summary
- MANDATORY: Include 'Actionable recommendations' and 'Predictions' in the summary.

Response format (final answer only):
{
  "plan_executed": ["step1", "step2", ...],
  "tasks_created": [...],
  "calendar_blocks": [...],
  "environmental_window": {"temp": 0, "condition": "...", "insight": "...", "status": "..."},
  "summary": "3-sentence plain-English summary. MUST include 1 predictive insight and 2 actionable recommendations.",
  "tokens_used": 0,
  "status": "COMPLETED"
}
"""


def build_orchestrator() -> Agent:
    """
    Constructs the ADK Orchestrator Agent with all sub-agents registered as AgentTools.
    The LLM planner decides which sub-agents to call and in what order.
    """
    task_agent = build_task_agent()
    notes_agent = build_notes_agent()
    schedule_agent = build_schedule_agent()
    workflow_agent = build_workflow_agent()
    data_agent = build_data_agent()
    environment_agent = build_environment_agent()

    orchestrator = Agent(
        name="orcheflow_orchestrator",
        model=GEMINI_ORCHESTRATOR_MODEL,
        description="Primary coordinator that plans and delegates to specialist sub-agents.",
        instruction=ORCHESTRATOR_SYSTEM_PROMPT,
        sub_agents=[task_agent, notes_agent, schedule_agent, workflow_agent, data_agent, environment_agent],
    )
    return orchestrator


async def run_orchestration(
    run_id: str,
    user_id: str,
    intent: str,
    payload: dict,
) -> dict:
    """
    Entry point called by the Agent Service API.
    Creates an ADK session, runs the orchestrator, and returns structured results.
    """
    log.info("orchestration_start", run_id=run_id, intent=intent[:80])

    # Create ADK session keyed to this workflow run
    session_id = await create_adk_session(user_id=user_id, run_id=run_id)

    # Build the orchestrator agent
    orchestrator = build_orchestrator()

    # Compose the prompt with full context
    prompt = _build_prompt(intent, payload)

    await write_audit_log(
        run_id=run_id,
        step_id=run_id,
        agent_name="orchestrator",
        action="ORCHESTRATION_STARTED",
        details={"intent": intent, "payload_keys": list(payload.keys())},
    )

    # Run via ADK runner
    raw_response = await run_adk_agent(
        agent=orchestrator,
        user_id=user_id,
        session_id=session_id,
        message=prompt,
    )

    # Parse structured output from LLM response
    result = _parse_response(raw_response)

    await write_audit_log(
        run_id=run_id,
        step_id=run_id,
        agent_name="orchestrator",
        action="ORCHESTRATION_COMPLETE",
        details={"status": result.get("status"), "plan": result.get("plan_executed")},
        tokens_used=result.get("tokens_used", 0),
    )

    log.info("orchestration_done", run_id=run_id, status=result.get("status"))
    return result


def _build_prompt(intent: str, payload: dict) -> str:
    parts = [f"User intent: {intent}"]

    if payload.get("notes_content"):
        notes_preview = payload["notes_content"][:500]
        parts.append(f"\nRaw notes/content provided:\n{notes_preview}")

    if payload.get("date_context"):
        parts.append(f"\nDate context: {payload['date_context']}")

    parts.append(
        "\nPlease plan and execute the necessary steps using your sub-agents. "
        "Return the final structured JSON output as described in your instructions."
    )
    return "\n".join(parts)


def _parse_response(raw: str) -> dict:
    """Extract JSON from ADK agent response. Falls back to partial result."""
    try:
        # Strip markdown code fences if present
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            lines = cleaned.split("\n")
            cleaned = "\n".join(lines[1:-1])
        return json.loads(cleaned)
    except (json.JSONDecodeError, ValueError):
        log.warning("response_parse_failed", raw_preview=raw[:200])
        return {
            "plan_executed": [],
            "tasks_created": [],
            "calendar_blocks": [],
            "summary": raw[:500] if raw else "Orchestration completed.",
            "tokens_used": 0,
            "status": "PARTIAL",
        }
