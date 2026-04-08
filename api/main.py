"""
OrcheFlowAI — FastAPI Application Entry Point
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from api.routers import (
    workflow, tasks, notes, schedule, audit, 
    canvas, modes, learning, google_auth, location
)
from api.middleware.logging import StructuredLoggingMiddleware

load_dotenv()


from db.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: verify DB and downstream services
    print("OrcheFlowAI API starting up...")
    try:
        await init_db()
    except Exception as e:
        print(f"Failed to initialize database on startup: {e}")
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
app.include_router(google_auth.router, prefix="/v1/auth/google", tags=["Auth"])
app.include_router(location.router, prefix="/v1/location", tags=["Location"])


@app.get("/v1/health", tags=["Health"])
async def health():
    return {
        "status": "ok",
        "service": "OrcheFlowAI API",
        "version": "1.0.0",
    }
    
from fastapi.responses import FileResponse, JSONResponse
from fastapi import Request

# Serve static frontend dashboard with SPA support
@app.get("/{full_path:path}", include_in_schema=False)
async def catch_all(request: Request, full_path: str):
    # 1. API routes should not be caught here if they are matched by routers above
    # but if they reach here, it's a genuine 404 for an API endpoint
    if full_path.startswith("v1/"):
        return JSONResponse(status_code=404, content={"detail": "API endpoint not found"})
    
    # 2. Check if a physical file exists in static/ (for assets, icons, etc.)
    static_file = os.path.join("static", full_path)
    if os.path.isfile(static_file):
        return FileResponse(static_file)
        
    # 3. Fallback to index.html for SPA client-side routing
    index_path = os.path.join("static", "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
        
    return JSONResponse(status_code=404, content={"detail": "Not Found"})
