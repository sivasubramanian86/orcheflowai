"""
OrcheFlowAI — Agent Service Entry Point
Internal FastAPI service that the API layer calls to run ADK orchestration.
"""
from fastapi import FastAPI
from pydantic import BaseModel
from agents.orchestrator.agent import run_orchestration

app = FastAPI(title="OrcheFlowAI Agent Service", version="1.0.0")


@app.get("/")
async def root():
    return {
        "message": "OrcheFlowAI Agent Service Mesh is active.",
        "status": "ready",
        "docs": "/docs"
    }


class OrchestrateRequest(BaseModel):
    run_id: str
    intent: str
    payload: dict = {}
    user_id: str = "demo-user"


@app.post("/internal/orchestrate")
async def orchestrate(body: OrchestrateRequest):
    """Triggered by API service. Runs full ADK multi-agent orchestration."""
    result = await run_orchestration(
        run_id=body.run_id,
        user_id=body.user_id,
        intent=body.intent,
        payload=body.payload,
    )
    return result


@app.get("/health")
async def health():
    return {"status": "ok", "service": "OrcheFlowAI Agent Service"}
