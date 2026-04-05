"""
OrcheFlowAI — Notes Agent (ADK-native)
Handles note ingestion and Gemini-powered action item extraction via MCP tools.
"""
import os
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from agents.base_agent import GEMINI_SUBAGENT_MODEL, log_tool_call
import httpx
import json
import time
from google.cloud import storage

MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

NOTES_AGENT_PROMPT = """
You are OrcheFlowAI Notes Agent — specialist in knowledge ingestion and extraction.

Your capabilities:
- fetch_gcs_content: Download raw text content from a Google Cloud Storage URI (gs://bucket/file)
- create_note: Store raw text (meeting notes, brain dumps, references) as structured notes
- extract_action_items: Parse notes to extract explicit commitments and decisions as action items
- search_notes: Retrieve relevant notes by keyword or semantic similarity

Rules:
- If the user provides a GCS URI (gs://...), call fetch_gcs_content FIRST to get the text
- Only extract EXPLICIT commitments — not vague discussions
- Infer deadlines from date references in text (e.g., 'by EOD Thursday')
- Assign priority 1-5 (1=Critical, 5=Backlog)
- Always return structured JSON with: note_id, action_items[]
- Each action item must have: title, owner, due_date (or null), priority, source_note_id

When asked to process notes (if GCS provided):
1. Call fetch_gcs_content to get the raw text
2. Call create_note to store the content
3. Call extract_action_items on the stored note
4. Return the combined result
"""


# ─── GCS Ingestion Tool ────────────────────────────────────────────────────────

async def fetch_gcs_content(gcs_uri: str) -> dict:
    """Download the raw text content of a file from a Google Cloud Storage URI."""
    start = time.monotonic()
    try:
        if not gcs_uri.startswith("gs://"):
            return {"error": "Invalid GCS URI. Must start with gs://"}

        # Extract bucket and blob path
        parts = gcs_uri[5:].split("/", 1)
        if len(parts) < 2:
            return {"error": "Incomplete GCS URI."}
        
        bucket_name, blob_name = parts
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        
        content = blob.download_as_text()
        
        await log_tool_call(
            step_id="", tool_name="notes_agent.fetch_gcs_content",
            tool_input={"uri": gcs_uri}, tool_output={"content_preview": content[:100]},
            success=True, latency_ms=int((time.monotonic() - start) * 1000)
        )
        return {"content": content, "uri": gcs_uri}
    except Exception as e:
        return {"error": f"GCS Fetch failed: {str(e)}", "content": ""}


# ─── MCP-backed Tool Functions ─────────────────────────────────────────────────

async def create_note(title: str, content: str, content_type: str = "MEETING") -> dict:
    """Store a note in the OrcheFlowAI knowledge base via MCP."""
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.post(
                f"{MCP_URL}/tools/notes_manager/create_note",
                json={"title": title, "content": content, "content_type": content_type},
            )
            resp.raise_for_status()
            result = resp.json()
            await log_tool_call(
                step_id="", tool_name="notes_manager.create_note",
                tool_input={"title": title, "content_type": content_type},
                tool_output=result, success=True,
                latency_ms=int((time.monotonic() - start) * 1000),
            )
            return result
    except Exception as e:
        return {"error": str(e), "note_id": None}


async def extract_action_items(note_id: str, content: str, date_context: str = "today") -> dict:
    """Use Gemini via MCP to extract structured action items from note content."""
    start = time.monotonic()
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            resp = await client.post(
                f"{MCP_URL}/tools/notes_manager/extract_action_items",
                json={"note_id": note_id, "content": content, "date_context": date_context},
            )
            resp.raise_for_status()
            result = resp.json()
            await log_tool_call(
                step_id="", tool_name="notes_manager.extract_action_items",
                tool_input={"note_id": note_id}, tool_output=result,
                success=True, latency_ms=int((time.monotonic() - start) * 1000),
            )
            return result
    except Exception as e:
        return {"error": str(e), "action_items": []}


async def search_notes(query: str, limit: int = 5) -> dict:
    """Search notes by keyword across the user's knowledge base."""
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(
            f"{MCP_URL}/tools/notes_manager/search",
            params={"query": query, "limit": limit},
        )
        resp.raise_for_status()
        return resp.json()


def build_notes_agent() -> Agent:
    """Construct the ADK Notes Agent with MCP-backed function tools."""
    return Agent(
        name="notes_agent",
        model=GEMINI_SUBAGENT_MODEL,
        description="Specialist in note ingestion, action item extraction, and knowledge search.",
        instruction=NOTES_AGENT_PROMPT,
        tools=[
            FunctionTool(fetch_gcs_content),
            FunctionTool(create_note),
            FunctionTool(extract_action_items),
            FunctionTool(search_notes),
        ],
    )
