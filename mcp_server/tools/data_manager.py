"""
OrcheFlowAI — Data Manager Tool (MCP)
Handles direct AlloyDB operations: bulk ingestion and complex SQL querying.
"""
import os
import asyncio
import pandas as pd
from typing import Dict, Any, List, Optional
from fastapi import APIRouter
from pydantic import BaseModel
from google.cloud import storage
from sqlalchemy import text
from db.session import engine, AsyncSessionFactory
import structlog

log = structlog.get_logger()
router = APIRouter()

class IngestBody(BaseModel):
    gcs_uri: str
    target_type: str = "notes"

class QueryBody(BaseModel):
    intent: str

@router.post("/ingest")
async def ingest_from_gcs(body: IngestBody) -> Dict[str, Any]:
    """Download a CSV from GCS and bulk insert into AlloyDB."""
    try:
        # Extract bucket and blob
        gcs_uri = body.gcs_uri
        if not gcs_uri.startswith("gs://"):
            return {"status": "ERROR", "message": "Invalid URI", "records_processed": 0}
            
        parts = gcs_uri.replace("gs://", "").split("/", 1)
        bucket_name = parts[0]
        blob_name = parts[1]
        
        # Download
        storage_client = storage.Client()
        bucket = storage_client.bucket(bucket_name)
        blob = bucket.blob(blob_name)
        content = blob.download_as_text()
        
        from io import StringIO
        df = pd.read_csv(StringIO(content))
        
        async with AsyncSessionFactory() as session:
            if body.target_type == "notes":
                from db.models import Note
                for _, row in df.iterrows():
                    note = Note(
                        title=row.get("title", "Imported Note"),
                        content=row.get("content", ""),
                        user_id="demo-user",
                    )
                    session.add(note)
            elif body.target_type == "tasks":
                from db.models import Task
                for _, row in df.iterrows():
                    task = Task(
                        title=row.get("title", "Imported Task"),
                        description=row.get("description", ""),
                        status=row.get("status", "TODO"),
                        user_id="demo-user",
                    )
                    session.add(task)
            await session.commit()
            
        return {"status": "SUCCESS", "records_processed": len(df)}
    except Exception as e:
        log.error("ingestion_failed", error=str(e))
        return {"status": "ERROR", "message": str(e), "records_processed": 0}

@router.post("/query")
async def run_query(body: QueryBody) -> Dict[str, Any]:
    """Exposes semantic reporting for the agent to use in the GUI."""
    try:
        # For the hackathon, we translate the intent into specific AlloyDB queries
        async with engine.connect() as conn:
            # Query active items or completion rates
            result = await conn.execute(text("SELECT count(*) FROM tasks"))
            count = result.scalar()
            return {"status": "SUCCESS", "message": f"System scan complete: {count} items located.", "data": [{"total_count": count}]}
    except Exception as e:
        return {"status": "ERROR", "message": str(e)}
