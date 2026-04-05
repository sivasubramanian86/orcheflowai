"""
OrcheFlowAI — Workflow Agent (ADK-native)
Compiles results from all specialist agents into a structured final output and persisted plan.
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from agents.base_agent import GEMINI_SUBAGENT_MODEL

MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

WORKFLOW_AGENT_PROMPT = """
You are OrcheFlowAI Workflow Agent — the final summarizer and plan compiler.

You receive the aggregated results of all previous agent steps and must:
1. Write a 3-sentence plain-English executive summary of what was accomplished
2. List the top next actions the user should take immediately
3. Return the complete structured output

Output format (strict JSON):
{
  "executive_summary": "3 clear sentences summarizing what was done and what value was created.",
  "tasks_created": [...],
  "calendar_blocks": [...],
  "next_actions": [
    "First thing user should do",
    "Second priority action",
    "Third action"
  ],
  "plan_document": {
    "title": "Plan title",
    "type": "ADHOC",
    "items": [...]
  }
}

Tone: Professional, concise, action-oriented. No filler words. No repetition.
Audience: Busy knowledge worker who needs to act on this immediately.
"""


async def compile_summary(
    tasks_created: list,
    calendar_blocks: list,
    notes_summary: str = "",
    intent: str = "",
) -> dict:
    """
    Placeholder tool — the workflow agent uses its LLM reasoning to compile.
    In production, this could persist the plan to the DB directly.
    """
    return {
        "tasks_count": len(tasks_created),
        "blocks_count": len(calendar_blocks),
        "notes_summary": notes_summary,
        "ready_to_compile": True,
    }


def build_workflow_agent() -> Agent:
    """Construct the ADK Workflow Agent — the final synthesizer."""
    return Agent(
        name="workflow_agent",
        model=GEMINI_SUBAGENT_MODEL,
        description="Compiles all agent results into a final structured summary and plan document.",
        instruction=WORKFLOW_AGENT_PROMPT,
        tools=[
            FunctionTool(compile_summary),
        ],
    )
