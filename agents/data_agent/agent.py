"""
OrcheFlowAI — Data Ingestion Agent (ADK-native)
Specialist in bulk data operations: GCS to AlloyDB ingestion, complex SQL querying, and reporting.
"""
import os
import time
import httpx
import json
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from agents.base_agent import GEMINI_SUBAGENT_MODEL, log_tool_call

MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

DATA_AGENT_PROMPT = """
You are OrcheFlowAI Data Ingestion Agent — specialist in high-volume data migration and advanced database querying.

Your capabilities:
- ingest_bulk_data: Import structured data (matching notes/tasks) from a GCS URI into AlloyDB.
- run_complex_query: Execute safe, read-only SQL queries to answer high-level business or productivity questions.
- sync_external_source: Placeholder for future API-to-DB sync capabilities.

Rules:
- When asked to 'ingest' or 'import' data from Cloud Storage, use ingest_bulk_data.
- When asked complex questions about history (e.g., 'What was my average task completion time last month?'), use run_complex_query.
- Always validate the GCS URI starts with gs://.
- Return a summary of how many records were processed/found.
"""

async def ingest_bulk_data(gcs_uri: str, target_type: str = "notes") -> dict:
    """Ingest bulk data from GCS into AlloyDB via MCP tools."""
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{MCP_URL}/tools/data_manager/ingest",
                json={"gcs_uri": gcs_uri, "target_type": target_type},
            )
            resp.raise_for_status()
            result = resp.json()
            await log_tool_call(
                step_id="", tool_name="data_manager.ingest",
                tool_input={"uri": gcs_uri, "type": target_type},
                tool_output=result, success=True,
                latency_ms=int((time.monotonic() - start) * 1000),
            )
            return result
    except Exception as e:
        return {"error": str(e), "processed": 0}

async def run_complex_query(query_intent: str) -> dict:
    """Translate natural language intent into SQL for AlloyDB and return results."""
    start = time.monotonic()
    try:
        # Note: In a real production system, this would use a Text-to-SQL layer.
        # For the hackathon, it routes to an AlloyDB-aware tool in MCP.
        async with httpx.AsyncClient(timeout=30.0) as client:
            resp = await client.post(
                f"{MCP_URL}/tools/data_manager/query",
                json={"intent": query_intent},
            )
            resp.raise_for_status()
            result = resp.json()
            await log_tool_call(
                step_id="", tool_name="data_manager.query",
                tool_input={"intent": query_intent}, tool_output={"count": len(result.get("data", []))},
                success=True, latency_ms=int((time.monotonic() - start) * 1000),
            )
            return result
    except Exception as e:
        return {"error": str(e), "data": []}

def build_data_agent() -> Agent:
    """Construct the ADK Data Ingestion Agent."""
    return Agent(
        name="data_agent",
        model=GEMINI_SUBAGENT_MODEL,
        description="Specialist in bulk data ingestion from GCS to AlloyDB and complex SQL reporting.",
        instruction=DATA_AGENT_PROMPT,
        tools=[
            FunctionTool(ingest_bulk_data),
            FunctionTool(run_complex_query),
        ],
    )
