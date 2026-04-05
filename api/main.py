"""
OrcheFlowAI — FastAPI Application Entry Point
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routers import (
    workflow, tasks, notes, schedule, audit, 
    canvas, modes, learning
)
from api.middleware.logging import StructuredLoggingMiddleware

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify DB and downstream services
    print("OrcheFlowAI API starting up...")
    yield
    print("OrcheFlowAI API shutting down...")


app = FastAPI(
    title="OrcheFlowAI",
    description="Multi-Agent Productivity Assistant — Orchestrate your flow, let agents do the rest.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(StructuredLoggingMiddleware)

# Routers
app.include_router(workflow.router, prefix="/v1/workflow", tags=["Workflow"])
app.include_router(tasks.router, prefix="/v1/tasks", tags=["Tasks"])
app.include_router(notes.router, prefix="/v1/notes", tags=["Notes"])
app.include_router(schedule.router, prefix="/v1/schedule", tags=["Schedule"])
app.include_router(audit.router, prefix="/v1/audit", tags=["Audit"])
app.include_router(canvas.router, prefix="/v1/canvas", tags=["Canvas"])
app.include_router(modes.router, prefix="/v1/modes", tags=["Mode"])
app.include_router(learning.router, prefix="/v1/learning", tags=["Learning"])


@app.get("/v1/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "service": "OrcheFlowAI API",
        "version": "1.0.0",
    }
