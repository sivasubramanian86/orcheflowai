"""
OrcheFlowAI — MCP Notes Manager Tool
Note storage, Vertex AI-powered action item extraction, and keyword search.
Uses Vertex AI (ADC) — no API key required.
"""
import os
import uuid
import json
from typing import Optional
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_

# Vertex AI SDK (replaces google.generativeai)
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig

from db.session import get_db
from db.models import Note

GCP_PROJECT  = os.getenv("GOOGLE_CLOUD_PROJECT", "genai-apac-2026-491004")
GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")
EXTRACTION_MODEL = os.getenv("GEMINI_SUBAGENT_MODEL_RAW", "gemini-2.0-flash")

# Init Vertex AI using ADC at module load
vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)

router = APIRouter()

EXTRACTION_PROMPT = """
Extract structured action items from the provided notes.
Return ONLY valid JSON:
{
  "action_items": [
    {
      "title": "Short clear task title",
      "owner": "person or 'user'",
      "due_date": "YYYY-MM-DD or null",
      "priority": 1-5,
      "notes": "brief context"
    }
  ]
}
Only extract EXPLICIT commitments. Infer dates from relative references.
Priority: 1=Critical, 2=High, 3=Medium, 4=Low, 5=Backlog
"""


class CreateNoteRequest(BaseModel):
    title: Optional[str] = "Untitled Note"
    content: str
    content_type: str = "REFERENCE"
    tags: list[str] = []
    user_id: str = "demo-user"


@router.post("/create_note")
async def create_note(body: CreateNoteRequest, db: AsyncSession = Depends(get_db)):
    note = Note(
        id=str(uuid.uuid4()),
        user_id=body.user_id,
        title=body.title,
        content=body.content,
        content_type=body.content_type,
        tags=body.tags,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return {
        "id": note.id,
        "title": note.title,
        "content_type": note.content_type,
        "created_at": note.created_at.isoformat(),
    }


@router.post("/extract_action_items")
async def extract_action_items(body: dict, db: AsyncSession = Depends(get_db)):
    """
    Use Gemini to extract structured action items from note content.
    Attaches source_note_id to each action item for traceability.
    """
    note_id = body.get("note_id")
    content = body.get("content", "")
    date_context = body.get("date_context", "today")

    if not content and note_id:
        result = await db.execute(select(Note).where(Note.id == note_id))
        note = result.scalar_one_or_none()
        content = note.content if note else ""

    if not content:
        return {"action_items": [], "note_id": note_id}

    model = GenerativeModel(
        model_name=EXTRACTION_MODEL,
        generation_config=GenerationConfig(
            temperature=0.1,
            max_output_tokens=1024,
            response_mime_type="application/json",
        ),
        system_instruction=EXTRACTION_PROMPT,
    )
    response = model.generate_content(
        f"Date context: {date_context}\n\nNotes:\n{content}"
    )

    try:
        extracted = json.loads(response.text)
        action_items = extracted.get("action_items", [])
    except (json.JSONDecodeError, ValueError):
        action_items = []

    for item in action_items:
        item["source_note_id"] = note_id

    return {
        "action_items": action_items,
        "note_id": note_id,
        "tokens_used": response.usage_metadata.total_token_count if response.usage_metadata else 0,
    }


@router.get("/search")
async def search_notes(query: str, limit: int = 5, db: AsyncSession = Depends(get_db)):
    """Keyword search across note content and titles."""
    result = await db.execute(
        select(Note)
        .where(
            or_(
                Note.content.ilike(f"%{query}%"),
                Note.title.ilike(f"%{query}%"),
            )
        )
        .limit(limit)
    )
    notes = result.scalars().all()
    return {
        "query": query,
        "results": [
            {"id": n.id, "title": n.title, "content_preview": n.content[:200], "content_type": n.content_type}
            for n in notes
        ],
    }
