"""
OrcheFlowAI — Environmental Agent (ADK-native)
Specialist in weather, traffic, and spatial constraints using MCP tools.
"""
import os
import httpx
from google.adk.agents import Agent
from google.adk.tools import FunctionTool
from agents.base_agent import GEMINI_SUBAGENT_MODEL

MCP_URL = os.getenv("MCP_SERVER_URL", "http://localhost:8001")

ENVIRONMENT_AGENT_PROMPT = """
You are OrcheFlowAI Environmental Agent — specialist in real-time context.

Your capabilities:
- get_current_weather: Retrieve temperature, conditions, and actionable recovery insights.
- analyze_surroundings: (Future) Aggregate traffic and POI data.

Your role:
1. Fetch the weather for the user's current location.
2. Provide a 'Predictive Insight' (e.g., 'Rain expected in 2 hours, do your recovery walk now').
3. Determine if the environment is OPTIMAL for Deep Work or Recovery.

Always include the 'actionable_insight' and 'status' in your report to the orchestrator.
"""

async def get_current_weather(location: str = "Chennai, India") -> dict:
    """Fetch real-time weather and environmental insights via MCP."""
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.post(
                f"{MCP_URL}/tools/weather_manager/current",
                json={"location": location},
            )
            resp.raise_for_status()
            return resp.json().get("data", {})
    except Exception as e:
        return {"error": str(e), "status": "UNKNOWN"}

def build_environment_agent() -> Agent:
    """Construct the ADK Environmental Agent."""
    return Agent(
        name="environment_agent",
        model=GEMINI_SUBAGENT_MODEL,
        description="Specialist in weather, recovery windows, and environmental conditions.",
        instruction=ENVIRONMENT_AGENT_PROMPT,
        tools=[
            FunctionTool(get_current_weather),
        ],
    )
