"""
OrcheFlowAI — Pytest Root Configuration

Shared fixtures and test utilities for unit, integration, and contract tests.
Loads environment variables from .env.example for CI (no real secrets required).
"""
import os
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock
from typing import AsyncGenerator

# ─── Test Environment Setup ───────────────────────────────────────────────────
# Override env vars for testing — no real credentials needed
os.environ.setdefault("GOOGLE_CLOUD_PROJECT", "test-project")
os.environ.setdefault("GOOGLE_CLOUD_LOCATION", "us-central1")
os.environ.setdefault("GEMINI_ORCHESTRATOR_MODEL", "gemini-2.5-flash")
os.environ.setdefault("GEMINI_SUBAGENT_MODEL", "gemini-2.0-flash")
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost:5432/test_orcheflow")
os.environ.setdefault("JWT_SECRET", "test-jwt-secret-min-32-chars-long-enough")
os.environ.setdefault("MCP_SERVER_URL", "http://localhost:8001")
os.environ.setdefault("AGENT_SERVICE_URL", "http://localhost:8002")
os.environ.setdefault("API_SERVICE_URL", "http://localhost:8000")
os.environ.setdefault("LOG_LEVEL", "WARNING")


# ─── Event Loop ──────────────────────────────────────────────────────────────
@pytest.fixture(scope="session")
def event_loop():
    """Shared event loop for all async tests in the session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


# ─── Mock Vertex AI / ADK ─────────────────────────────────────────────────────
@pytest.fixture
def mock_vertex_model():
    """Mock Vertex AI GenerativeModel — returns deterministic responses."""
    model = MagicMock()
    response_mock = MagicMock()
    response_mock.text = '{"status": "success", "confidence": 0.92, "tasks": []}'
    model.generate_content_async = AsyncMock(return_value=response_mock)
    return model


@pytest.fixture
def mock_adk_agent():
    """Mock ADK Agent and Runner — bypasses real LLM calls."""
    agent = MagicMock()
    runner = MagicMock()

    async def fake_run_async(*args, **kwargs):
        mock_event = MagicMock()
        mock_event.is_final_response.return_value = True
        mock_event.content.parts = [MagicMock(text="Mock agent response")]
        yield mock_event

    runner.run_async = fake_run_async
    return agent, runner


@pytest.fixture
def mock_mcp_client():
    """Mock HTTP client for MCP tool calls."""
    client = AsyncMock()
    client.post.return_value.json.return_value = {"status": "ok", "items": []}
    client.post.return_value.status_code = 200
    return client


# ─── Sample Payloads ──────────────────────────────────────────────────────────
@pytest.fixture
def sample_workflow_request() -> dict:
    """Standard workflow request for testing."""
    return {
        "intent": "Convert these meeting notes into prioritized tasks and schedule focus time",
        "user_id": "test-user-001",
        "payload": {
            "notes_content": "Meeting with team: agreed to deliver API contract by Friday, review ML model on Monday",
            "date_context": "2026-04-07",
        },
    }


@pytest.fixture
def sample_task() -> dict:
    """A valid task object for test assertions."""
    return {
        "id": "task-001",
        "title": "Deliver API contract",
        "priority": "P1",
        "due_date": "2026-04-11",
        "status": "TODO",
        "source_agent": "task_agent",
    }
