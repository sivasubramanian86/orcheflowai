"""
OrcheFlowAI — Vertex AI Initializer
Single place to initialize Vertex AI via ADC (no API key needed).
Called at startup by agents and MCP tools alike.
"""
import os
import vertexai
from vertexai.generative_models import GenerativeModel, GenerationConfig
import structlog

log = structlog.get_logger()

GCP_PROJECT = os.getenv("GOOGLE_CLOUD_PROJECT", "genai-apac-2026-491004")
GCP_LOCATION = os.getenv("GOOGLE_CLOUD_LOCATION", "us-central1")

# ADK-compatible model string format (skill 11: vertex-ai prefix required for ADK)
ORCHESTRATOR_MODEL = os.getenv("GEMINI_ORCHESTRATOR_MODEL", "vertex-ai:gemini-2.5-flash")
SUBAGENT_MODEL     = os.getenv("GEMINI_SUBAGENT_MODEL",     "vertex-ai:gemini-2.0-flash")

# Vertex AI raw model IDs for direct SDK calls (notes_manager extraction)
ORCHESTRATOR_MODEL_RAW = "gemini-2.5-flash"
SUBAGENT_MODEL_RAW     = "gemini-2.0-flash"

# Fallback hierarchy (skill 11: primary → fallback → cross-region)
MODEL_FALLBACK_CHAIN = [
    "gemini-2.5-flash",
    "gemini-2.0-flash",
    "gemini-1.5-flash-002",
]


def init_vertex_ai() -> None:
    """
    Initialize Vertex AI using Application Default Credentials (ADC).
    - Local dev: gcloud auth application-default login
    - Cloud Run: Service Account attached to the Cloud Run service
    No API key required.
    """
    vertexai.init(project=GCP_PROJECT, location=GCP_LOCATION)
    log.info("vertex_ai_initialized", project=GCP_PROJECT, location=GCP_LOCATION)


def get_generative_model(
    model_id: str = SUBAGENT_MODEL_RAW,
    temperature: float = 0.2,
    max_output_tokens: int = 1024,
) -> GenerativeModel:
    """
    Returns a Vertex AI GenerativeModel instance with standard config.
    Used by MCP tools for direct Gemini inference (no ADK runner needed).
    """
    return GenerativeModel(
        model_name=model_id,
        generation_config=GenerationConfig(
            temperature=temperature,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json",
        ),
    )
