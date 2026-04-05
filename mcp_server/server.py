"""
OrcheFlowAI — MCP Tool Server
Exposes task_manager, calendar_manager, and notes_manager tools as HTTP endpoints.
In production, this would implement the full MCP protocol via SSE transport.
"""
import os
from fastapi import FastAPI
from mcp_server.tools import task_manager, calendar_manager, notes_manager, data_manager

app = FastAPI(title="OrcheFlowAI MCP Server", version="1.0.0")

# Mount each tool namespace as a sub-router
app.include_router(task_manager.router, prefix="/tools/task_manager")
app.include_router(calendar_manager.router, prefix="/tools/calendar_manager")
app.include_router(notes_manager.router, prefix="/tools/notes_manager")
app.include_router(data_manager.router, prefix="/tools/data_manager")


@app.get("/health")
async def health():
    return {"status": "ok", "service": "OrcheFlowAI MCP Server"}


@app.get("/tools")
async def list_tools():
    """Returns all registered MCP tool names for discovery."""
    return {
        "tools": [
            "task_manager.create_task",
            "task_manager.list_tasks",
            "task_manager.update_task",
            "task_manager.prioritize",
            "calendar_manager.events",
            "calendar_manager.free_slots",
            "calendar_manager.block_time",
            "notes_manager.create_note",
            "notes_manager.extract_action_items",
            "notes_manager.search",
            "data_manager.ingest",
            "data_manager.query",
        ]
    }
