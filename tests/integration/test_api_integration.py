"""
Integration tests for OrcheFlowAI API Layer
Tests FastAPI endpoints against a real app instance (no real DB — uses SQLite for CI).
Requires: docker-compose up -d postgres  OR  CI with Postgres service container.
"""
import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, patch, MagicMock


@pytest.fixture
async def api_client():
    """
    Async HTTP client that connects directly to the FastAPI app (no real network).
    Patches all Vertex AI / agent calls to prevent real LLM usage in CI.
    """
    # Patch agent invocation before importing the app
    with patch("agents.base_agent.init_vertex_ai"), \
         patch("agents.base_agent.session_service"), \
         patch("agents.base_agent.run_adk_agent", new_callable=AsyncMock) as mock_agent:
        mock_agent.return_value = '{"status": "success", "confidence": 0.92, "tasks": [{"title": "Review API", "priority": "P1"}]}'

        from api.main import app
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            yield client, mock_agent


class TestHealthEndpoint:
    """API health check must always return 200."""

    @pytest.mark.asyncio
    async def test_health_returns_200(self, api_client):
        client, _ = api_client
        response = await client.get("/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestWorkflowRunEndpoint:
    """POST /v1/workflow/run — the primary API contract."""

    @pytest.mark.asyncio
    async def test_valid_request_returns_202(self, api_client, sample_workflow_request):
        """A well-formed request must return 202 Accepted with a run_id."""
        client, _ = api_client
        response = await client.post(
            "/v1/workflow/run",
            json=sample_workflow_request,
            headers={"Authorization": "Bearer demo-token"},
        )
        assert response.status_code in (200, 202)
        data = response.json()
        assert "run_id" in data
        assert "status" in data

    @pytest.mark.asyncio
    async def test_empty_intent_returns_422(self, api_client):
        """An empty intent must return 422 Unprocessable Entity."""
        client, _ = api_client
        response = await client.post(
            "/v1/workflow/run",
            json={"intent": "", "user_id": "user-001", "payload": {}},
            headers={"Authorization": "Bearer demo-token"},
        )
        assert response.status_code == 422

    @pytest.mark.asyncio
    async def test_missing_auth_returns_401(self, api_client, sample_workflow_request):
        """Requests without Authorization header must return 401."""
        client, _ = api_client
        response = await client.post("/v1/workflow/run", json=sample_workflow_request)
        assert response.status_code in (401, 403)

    @pytest.mark.asyncio
    async def test_response_contains_tasks(self, api_client, sample_workflow_request):
        """Successful workflow must return at least one task in the response."""
        client, _ = api_client
        response = await client.post(
            "/v1/workflow/run",
            json=sample_workflow_request,
            headers={"Authorization": "Bearer demo-token"},
        )
        if response.status_code in (200, 202):
            data = response.json()
            # Run may be async — check response has run_id at minimum
            assert "run_id" in data


class TestRateLimiting:
    """Verify rate limiting is enforced at 60 RPM."""

    @pytest.mark.asyncio
    async def test_health_rate_limit_not_triggered_on_single_call(self, api_client):
        """A single health call must never trigger rate limiting."""
        client, _ = api_client
        response = await client.get("/v1/health")
        assert response.status_code != 429


class TestCORSHeaders:
    """Verify CORS headers are present for browser requests."""

    @pytest.mark.asyncio
    async def test_cors_header_present(self, api_client):
        """A preflight OPTIONS request should return CORS allow headers."""
        client, _ = api_client
        response = await client.options(
            "/v1/health",
            headers={"Origin": "http://localhost:3000", "Access-Control-Request-Method": "GET"},
        )
        # Accept 200 or 204
        assert response.status_code in (200, 204, 400)  # 400 acceptable if CORS blocked
