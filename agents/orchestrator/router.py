"""
OrcheFlowAI — Orchestrator Intent Router
Classifies a free-text user intent into the appropriate agent pipeline.
Pure Python utility (no LLM) for fast pre-routing before full ADK orchestration.
"""
from __future__ import annotations

import re
from typing import Final

_ROUTING_RULES: Final[list[tuple[str, str]]] = [
    (r"\b(notes?|meetings?|transcripts?|brain.?dump|capture|raw)\b", "notes_agent"),
    (r"\b(tasks?|todos?|action.?items?|prioriti[sz]e?|backlogs?|assign|deliverables?)\b", "task_agent"),
    (r"\b(schedul(e|ing)|calendars?|blocks?|focus.?times?|slots?|books?)\b", "schedule_agent"),
    (r"\b(plans?|summari[sz]e?|compile|overview|reports?|organis[ze]d?)\b", "workflow_agent"),
]

_ORDER: Final[list[str]] = ["notes_agent", "task_agent", "schedule_agent", "workflow_agent"]


def classify_intent(intent: str) -> list[str]:
    """
    Classify a user intent string into an ordered list of agent names.

    Args:
        intent: Free-text user intent.

    Returns:
        Ordered list of agent name strings, e.g. ["notes_agent", "task_agent", "workflow_agent"]

    Raises:
        ValueError: If intent is empty or only whitespace.
    """
    if not intent or not intent.strip():
        raise ValueError("Intent must be a non-empty string.")

    lower = intent.lower()
    selected: list[str] = []

    for pattern, agent in _ROUTING_RULES:
        if re.search(pattern, lower) and agent not in selected:
            selected.append(agent)

    # Fallback: default to full pipeline
    if not selected:
        return list(_ORDER)

    # Auto-append workflow_agent when 2+ specialist agents selected
    specialist_count = sum(1 for a in selected if a != "workflow_agent")
    if specialist_count >= 2 and "workflow_agent" not in selected:
        selected.append("workflow_agent")

    return sorted(selected, key=lambda a: _ORDER.index(a) if a in _ORDER else 99)
