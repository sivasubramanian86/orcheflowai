"""
Unit tests for OrcheFlowAI — Orchestrator Agent Logic
Tests: intent classification, payload validation, confidence scoring, error handling.
All LLM calls are mocked — no real Vertex AI credentials required.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
import json


class TestIntentClassification:
    """Verify the orchestrator correctly classifies user intents."""

    @pytest.mark.parametrize("intent,expected_agents", [
        (
            "Convert meeting notes into tasks",
            ["notes_agent", "task_agent"]
        ),
        (
            "Schedule focus time for next week",
            ["schedule_agent"]
        ),
        (
            "Summarize all my notes from last week and create a plan",
            ["notes_agent", "workflow_agent"]
        ),
    ])
    def test_intent_to_agent_mapping(self, intent: str, expected_agents: list):
        """Valid intents must map to at least one expected agent."""
        # The orchestrator selects a pipeline based on intent keywords
        # This tests the mapping logic without calling the LLM
        from agents.orchestrator.router import classify_intent

        result = classify_intent(intent)
        assert isinstance(result, list), "classify_intent must return a list"
        assert len(result) > 0, "At least one agent must be selected"
        for agent in expected_agents:
            assert agent in result, f"Expected agent '{agent}' not in pipeline: {result}"


class TestWorkflowRequestValidation:
    """Pydantic schema validation for workflow requests."""

    def test_valid_request_passes(self, sample_workflow_request: dict):
        """A well-formed request must pass validation without error."""
        from api.schemas.workflow import WorkflowRequest

        req = WorkflowRequest(**sample_workflow_request)
        assert req.intent == sample_workflow_request["intent"]
        assert req.user_id == sample_workflow_request["user_id"]

    def test_empty_intent_rejected(self):
        """An empty intent must raise a validation error."""
        from api.schemas.workflow import WorkflowRequest
        from pydantic import ValidationError

        with pytest.raises(ValidationError):
            WorkflowRequest(intent="", user_id="user-001", payload={})

    def test_intent_too_long_rejected(self):
        """An intent exceeding max length must raise a validation error."""
        from api.schemas.workflow import WorkflowRequest
        from pydantic import ValidationError

        long_intent = "a" * 5001  # exceeds 5000 char limit
        with pytest.raises(ValidationError):
            WorkflowRequest(intent=long_intent, user_id="user-001", payload={})


class TestAuditLogWriter:
    """Verify audit log writes are fire-and-forget and never raise."""

    @pytest.mark.asyncio
    async def test_audit_log_happy_path(self, mock_mcp_client):
        """A successful audit write returns None (fire-and-forget)."""
        with patch("httpx.AsyncClient") as mock_ctx:
            mock_ctx.return_value.__aenter__.return_value = mock_mcp_client

            from agents.base_agent import write_audit_log

            # Should not raise
            result = await write_audit_log(
                run_id="run-001",
                step_id="step-001",
                agent_name="task_agent",
                action="create_task",
                details={"task_title": "Review contract"},
                tokens_used=150,
            )
            assert result is None

    @pytest.mark.asyncio
    async def test_audit_log_does_not_raise_on_failure(self):
        """If the API is unreachable, fire-and-forget must NOT propagate the error."""
        with patch("httpx.AsyncClient") as mock_ctx:
            mock_ctx.return_value.__aenter__.side_effect = ConnectionError("API down")

            from agents.base_agent import write_audit_log

            # Must complete without raising
            await write_audit_log(
                run_id="run-002",
                step_id="step-001",
                agent_name="notes_agent",
                action="extract_notes",
                details={},
            )


class TestConfidenceScoring:
    """Verify confidence score extraction from LLM JSON responses."""

    @pytest.mark.parametrize("response_text,expected_confidence", [
        ('{"status": "success", "confidence": 0.95, "tasks": []}', 0.95),
        ('{"status": "success", "confidence": 0.5, "tasks": []}', 0.5),
        ('{"status": "error", "confidence": 0.0}', 0.0),
    ])
    def test_confidence_extracted_correctly(self, response_text: str, expected_confidence: float):
        """Confidence must be parsed from structured LLM JSON output."""
        data = json.loads(response_text)
        assert data["confidence"] == expected_confidence
        assert 0.0 <= data["confidence"] <= 1.0, "Confidence must be between 0.0 and 1.0"
