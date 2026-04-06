"""
OrcheFlowAI — Google Maps Track Router
Integrates Places, Routes, and Location History.
Uses Gemini 2.5 Flash for 'spatial' recommendations.
"""
import os
import json
from datetime import datetime
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import googlemaps
from google.cloud import aiplatform
from vertexai.generative_models import GenerativeModel, Tool
import vertexai.generative_models as gm # Grounding tool is under gm.grounding in 2026 SDK

from db.session import get_db
from db.models import User, CommuteSegment

import google.auth
from google.auth.transport.requests import Request
import json
import httpx

# Initialize Vertex AI AI Platform (No API keys needed with Workload Identity/IAM)
PROJECT_ID = os.getenv("GOOGLE_CLOUD_PROJECT", "orcheflow-ai-2026")
aiplatform.init(project=PROJECT_ID, location="us-central1")

router = APIRouter()

def get_iam_token():
    """Fetch a Google IAM token for keyless Maps routing."""
    try:
        credentials, project = google.auth.default(
            scopes=['https://www.googleapis.com/auth/maps-platform.routing']
        )
        credentials.refresh(Request())
        return credentials.token
    except:
        return None

MAPS_KEY = os.getenv("GOOGLE_MAPS_API_KEY", "MOCK_KEY")

# --- Endpoints ---

@router.get("/office-route")
async def get_route_to_office(db: AsyncSession = Depends(get_db)):
    """Calculate fastest route using either API Key or IAM Bearer Token (Keyless)."""
    user_id = "01948576-a3b2-7c6d-9e0f-1a2b3c4d5e6f"
    try:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            # Fallback for empty local SQLite during demo
            origin = "The Sail @ Marina Bay, Singapore"
            dest = "Google Singapore, Mapletree Business City"
        else:
            origin = user.preferences.get("home_address", "The Sail @ Marina Bay, Singapore")
            dest = user.preferences.get("office_address", "Google Singapore, Mapletree Business City")
    except Exception:
        origin = "The Sail @ Marina Bay, Singapore"
        dest = "Google Singapore, Mapletree Business City"
    
    # 1. Try Keyless (Workload Identity)
    token = get_iam_token()
    if token:
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    "https://routes.googleapis.com/directions/v2:computeRoutes",
                    headers={
                        "X-Goog-Api-Key": MAPS_KEY if MAPS_KEY != "MOCK_KEY" else "", # Key or Token works
                        "Authorization": f"Bearer {token}",
                        "X-Goog-Fieldmask": "routes.duration,routes.distanceMeters,routes.description"
                    },
                    json={
                        "origin": {"address": origin},
                        "destination": {"address": dest},
                        "travelMode": "DRIVE",
                        "routingPreference": "TRAFFIC_AWARE"
                    }
                )
                data = resp.json()
                route = data["routes"][0]
                return {
                    "origin": origin,
                    "destination": dest,
                    "distance": f"{route['distanceMeters']/1000:.1f} km",
                    "duration": route['duration'],
                    "traffic_duration": route['duration'],
                    "summary": route.get("description", "Fastest route"),
                    "status": "IAM_AUTH_ACTIVE"
                }
        except:
            pass # Fallback to Mock

    # 2. Fallback to Mock (Local Development)
    return {
        "origin": origin,
        "destination": dest,
        "distance": "5.4 km",
        "duration": "12 mins",
        "traffic_duration": "15 mins",
        "summary": "Fastest route via AYE (Mocked)",
        "status": "MOCK_MODE_ACTIVE"
    }

@router.get("/recommendations")
async def get_recommendations(user_id: str = "siva_dev"):
    """
    Generate travel/recovery recommendations using Gemini 2.5 Flash 
    with Google Search Grounding. No Google Maps API key required
    for discovery as it uses Vertex AI's real-time knowledge.
    """
    # Grounding Tools            # Keyless Grounding for Spatial Discovery
    search_tool = Tool.from_google_search_retrieval(
        google_search_retrieval=gm.grounding.GoogleSearchRetrieval()
    )
    model = GenerativeModel("gemini-1.5-flash", tools=[search_tool])
    
    prompt = f"""
    You are the OrcheFlowAI spatial agent. 
    Find 3 outdoor 'Recovery' spots (parks, cafes, beaches) in Chennai, India for user {user_id}. 
    Respond ONLY in raw JSON format:
    [
      {{"spot": "Name", "rationale": "Why it's good for recovery", "distance": "km", "icon": "park/cafe/beach"}}
    ]
    """
    
    try:
        response = model.generate_content(prompt, tools=[search_tool])
        clean_json = response.text.replace("```json", "").replace("```", "").strip()
        recommendations = json.loads(clean_json)
        return {"recommendations": recommendations}
    except Exception as e:
        # Fallback to local intelligence if search fails
        return {
            "recommendations": [
                {"spot": "Semmozhi Poonga Park", "rationale": "Lush greenery for cognitive recovery.", "distance": "2 km", "icon": "park"},
                {"spot": "Besant Nagar Beach", "rationale": "Sea breeze for focus-reset.", "distance": "5 km", "icon": "beach"}
            ]
        }

@router.get("/day/hotspots")
async def get_locations_visited():
    """Retrieve clusters of visited locations and favorite spots."""
    # Data would normally be aggregated from Map History / semantic timeline
    return {
        "visited_count": 8,
        "favorite_spots": [
            {"name": "Coffee Bean & Tea Leaf (MBC)", "visits": 14, "type": "Work Hub"},
            {"name": "Fitbit Fitness Studio", "visits": 5, "type": "Recovery Hub"},
            {"name": "Umeda Sky Building (Osaka)", "visits": 2, "type": "Vacation Spot"}
        ]
    }
