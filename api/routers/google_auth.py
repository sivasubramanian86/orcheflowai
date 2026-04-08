"""
OrcheFlowAI — Google OAuth 2.0 Router
Handles secure authentication and token synchronization.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from db.session import get_db
from db.models import UserCredential, User
from google_auth_oauthlib.flow import Flow
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

router = APIRouter()

# SCENARIO: Hackathon / Local Dev
# In production, these would be fetched from GCP Secret Manager
# Redirect URI is dynamically set during requests
CLIENT_CONFIG = {
    "web": {
        "client_id": (os.getenv("GOOGLE_CLIENT_ID") or "").strip(),
        "client_secret": (os.getenv("GOOGLE_CLIENT_SECRET") or "").strip(),
        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
        "token_uri": "https://oauth2.googleapis.com/token",
        "redirect_uris": ["http://placeholder"]
    }
}

SCOPES = [
    "openid", 
    "https://www.googleapis.com/auth/userinfo.email",
    "https://www.googleapis.com/auth/userinfo.profile",
    "https://www.googleapis.com/auth/calendar.readonly",
    "https://www.googleapis.com/auth/fitness.activity.read"
]

@router.get("/login")
async def login(request: Request):
    """Initiates Google OAuth 2.0 flow."""
    flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
    # Dynamically inject the callback url to avoid environment variable mismatch
    redirect_uri = str(request.url_for("callback")).replace("http://", "https://") if "run.app" in str(request.url) else str(request.url_for("callback"))
    flow.redirect_uri = redirect_uri
    
    authorization_url, state = flow.authorization_url(
        access_type="offline",
        include_granted_scopes="true",
        prompt="select_account consent"
    )
    # Store 'state' in session/secure cookie in prod
    return RedirectResponse(authorization_url)

@router.get("/callback")
async def callback(request: Request, db: AsyncSession = Depends(get_db)):
    """Handles the OAuth 2.0 callback and status token storage."""
    # In a real app, verify the 'state' from cookie
    
    flow = Flow.from_client_config(CLIENT_CONFIG, scopes=SCOPES)
    redirect_uri = str(request.url_for("callback")).replace("http://", "https://") if "run.app" in str(request.url) else str(request.url_for("callback"))
    flow.redirect_uri = redirect_uri
    
    try:
        # Force HTTPS because Cloud Run TLS termination makes request.url look like HTTP to Uvicorn
        auth_response = str(request.url).replace("http://", "https://")
        flow.fetch_token(authorization_response=auth_response)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch token: {str(e)}")

    creds = flow.credentials
    
    # Identify user exactly by the chosen Google account
    user_info = id_token.verify_oauth2_token(
        creds.id_token, 
        google_requests.Request(), 
        CLIENT_CONFIG["web"]["client_id"]
    )
    user_email = user_info.get("email")
    display_name = user_info.get("name", "Demo User")
    
    if not user_email:
        raise HTTPException(status_code=400, detail="Could not extract email from Google token")
    
    result = await db.execute(select(User).where(User.email == user_email))
    user = result.scalar_one_or_none()
    
    if not user:
        # Create user if this is the first sync with this account
        user = User(email=user_email, display_name=display_name)
        db.add(user)
        await db.flush()
    
    # Upsert Credentials
    cred_result = await db.execute(select(UserCredential).where(UserCredential.user_id == user.id))
    existing_cred = cred_result.scalar_one_or_none()
    
    if existing_cred:
        existing_cred.access_token = creds.token
        existing_cred.refresh_token = creds.refresh_token or existing_cred.refresh_token
        existing_cred.token_expiry = creds.expiry
        existing_cred.scopes = list(creds.scopes)
    else:
        new_cred = UserCredential(
            user_id=user.id,
            access_token=creds.token,
            refresh_token=creds.refresh_token,
            token_expiry=creds.expiry,
            scopes=list(creds.scopes)
        )
        db.add(new_cred)
    
    await db.commit()
    
    # Redirect back to frontend dynamically
    frontend_url = str(request.base_url).replace("http://", "https://") if "run.app" in str(request.url) else str(request.base_url)
    frontend_url = frontend_url.rstrip("/")
    return RedirectResponse(f"{frontend_url}/canvas?sync=success")

@router.get("/status")
async def get_sync_status(db: AsyncSession = Depends(get_db)):
    """Check if the user has active Google integration."""
    # Retrieve the most recently active or only credential for demo
    result = await db.execute(
        select(User, UserCredential)
        .join(UserCredential, User.id == UserCredential.user_id)
        .order_by(UserCredential.updated_at.desc())
        .limit(1)
    )
    res = result.first()
    
    if not res:
        return {"connected": False}
        
    user, cred = res
    return {
        "connected": True,
        "name": user.display_name,
        "email": user.email,
        "last_sync": cred.updated_at,
        "scopes": cred.scopes
    }
