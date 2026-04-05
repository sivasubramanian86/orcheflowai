"""
OrcheFlowAI — User Mode Router
Manages Focus, Social, and Recovery modes.
"""
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update

from db.session import get_db
from db.models import UserMode

router = APIRouter()

# --- Schemas ---

class ModeUpdateRequest(BaseModel):
    mode: str = "FOCUS" # FOCUS, SOCIAL, RECOVERY
    auto_switch: Optional[bool] = None

class ModeResponse(BaseModel):
    user_id: str
    active_mode: str
    auto_switch_enabled: bool
    updated_at: datetime

# --- Endpoints ---

@router.get("/", response_model=ModeResponse)
async def get_current_mode(db: AsyncSession = Depends(get_db)):
    """Retrieve the current user preference mode."""
    # Real ID from global session/context
    user_id = "01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f"
    
    result = await db.execute(select(UserMode).where(UserMode.user_id == user_id))
    mode = result.scalar_one_or_none()
    
    if not mode:
        # Create default mode if missing for demo
        mode = UserMode(user_id=user_id, active_mode="FOCUS", auto_switch_enabled=True)
        db.add(mode)
        await db.commit()
    
    return {
        "user_id": user_id,
        "active_mode": mode.active_mode,
        "auto_switch_enabled": mode.auto_switch_enabled,
        "updated_at": mode.updated_at
    }

@router.post("/update")
async def update_mode(body: ModeUpdateRequest, db: AsyncSession = Depends(get_db)):
    """Update the user preference mode."""
    user_id = "01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f"
    
    if body.mode not in ["FOCUS", "SOCIAL", "RECOVERY"]:
        raise HTTPException(status_code=400, detail="Invalid mode. Must be FOCUS, SOCIAL, or RECOVERY.")

    # Upsert pattern
    result = await db.execute(select(UserMode).where(UserMode.user_id == user_id))
    mode_rec = result.scalar_one_or_none()
    
    if mode_rec:
        mode_rec.active_mode = body.mode
        if body.auto_switch is not None:
            mode_rec.auto_switch_enabled = body.auto_switch
    else:
        mode_rec = UserMode(
            user_id=user_id,
            active_mode=body.mode,
            auto_switch_enabled=body.auto_switch if body.auto_switch is not None else True
        )
        db.add(mode_rec)
    
    await db.commit()
    return {"status": "ok", "mode": body.mode}
