"""OrcheFlowAI — Notes Router"""
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from db.session import get_db

router = APIRouter()


class NoteBody(BaseModel):
    title: Optional[str] = "Untitled"
    content: str
    content_type: str = "REFERENCE"
    tags: list[str] = []
    extract_tasks: bool = False


@router.post("", status_code=201)
async def create_note(body: NoteBody, db: AsyncSession = Depends(get_db)):
    """Create a note. If extract_tasks=True, triggers background notes_agent."""
    import uuid, httpx, os
    from db.models import Note
    note = Note(
        id=str(uuid.uuid4()),
        user_id="01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f",
        title=body.title,
        content=body.content,
        content_type=body.content_type,
        tags=body.tags,
    )
    db.add(note)
    await db.commit()
    await db.refresh(note)

    result = {"id": note.id, "title": note.title, "created_at": note.created_at.isoformat()}

    if body.extract_tasks:
        # Trigger notes agent async (fire and forget)
        try:
            mcp_url = os.getenv("MCP_SERVER_URL", "http://localhost:8001")
            async with httpx.AsyncClient(timeout=5.0) as client:
                await client.post(
                    f"{mcp_url}/tools/notes_manager/extract_action_items",
                    json={"note_id": note.id, "content": body.content},
                )
        except Exception:
            pass
        result["extraction_triggered"] = True

    return result
