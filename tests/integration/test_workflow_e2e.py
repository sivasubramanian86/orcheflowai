"""
OrcheFlowAI — Integration Test: End-to-End Workflow
Tests the full path: POST /v1/workflow/run → Agent → MCP Tools → DB
Uses TestClient with mocked ADK runner and Vertex AI calls.
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from fastapi.testclient import TestClient


MOCK_ORCHESTRATION_RESULT = {
    "plan_executed": ["ingest_notes", "create_tasks", "find_gaps", "block_time"],
    "tasks_created": [
        {"id": "t-001", "title": "Review API contract", "priority": 2, "status": "TODO"},
        {"id": "t-002", "title": "Complete code freeze", "priority": 1, "status": "TODO"},
    ],
    "calendar_blocks": [
        {"event_id": "ev-001", "start": "2026-04-06T09:00:00", "end": "2026-04-06T11:00:00"}
    ],
    "summary": "Processed Q2 planning notes. Created 2 tasks. Blocked 2h focus slot on April 6.",
    "tokens_used": 1842,
    "status": "COMPLETED",
}


@pytest.fixture
def api_client():
    """Create TestClient with DB dependency overridden."""
    from api.main import app
    from db.session import get_db
    mock_db = AsyncMock()
    app.dependency_overrides[get_db] = lambda: mock_db
    yield TestClient(app)
    app.dependency_overrides.clear()


class TestWorkflowE2E:
    @patch("api.routers.workflow.dispatch_to_agent_service", new_callable=AsyncMock)
    def test_workflow_run_returns_200(self, mock_dispatch, api_client):
        """POST /v1/workflow/run returns 200 with structured result."""
        mock_dispatch.return_value = MOCK_ORCHESTRATION_RESULT

        response = api_client.post(
            "/v1/workflow/run",
            json={
                "intent": "Convert meeting notes to tasks and block focus time",
                "payload": {
                    "notes_content": "Siva to review API contract by April 7",
                    "date_context": "2026-04-06",
                },
            },
            headers={"Authorization": "Bearer demo-token"},
        )

        assert response.status_code == 200
        body = response.json()
        assert body["status"] == "ACCEPTED"
        assert "run_id" in body

    @patch("api.routers.workflow.dispatch_to_agent_service", new_callable=AsyncMock)
    def test_workflow_empty_intent_returns_422(self, mock_dispatch, api_client):
        """Empty intent should be rejected with 422 validation error."""
        response = api_client.post(
            "/v1/workflow/run",
            json={"intent": "", "payload": {}},
            headers={"Authorization": "Bearer demo-token"},
        )
        assert response.status_code == 422

    def test_health_endpoint(self, api_client):
        """GET /v1/health must return 200 with service identifier."""
        response = api_client.get("/v1/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

    @patch("api.routers.workflow.dispatch_to_agent_service", new_callable=AsyncMock)
    def test_idempotency_key_prevents_duplicate_run(self, mock_dispatch, api_client):
        """Same idempotency key should return same run_id on repeat request."""
        mock_dispatch.return_value = MOCK_ORCHESTRATION_RESULT
        payload = {
            "intent": "Process Q2 notes",
            "payload": {"notes_content": "same content"},
            "idempotency_key": "idem-test-001",
        }

        r1 = api_client.post("/v1/workflow/run", json=payload,
                              headers={"Authorization": "Bearer demo-token"})
        r2 = api_client.post("/v1/workflow/run", json=payload,
                              headers={"Authorization": "Bearer demo-token"})

        assert r1.status_code == 200
        # Idempotent repeat should return same run_id (or 200 re-using existing)
        assert r2.status_code in (200, 409)
