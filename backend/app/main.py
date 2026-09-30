"""
Swasthya Records - Main Application Entry Point
National Healthcare Supply-Chain & Resource Resilience Platform
Track 3: Smart Health & Supply Chain Resilience
"""

import time
import uuid
import json
import logging
import datetime
import os
import sqlite3
import sys
import asyncio

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.api.router import api_router

# Configure Structured Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("swasthya.audit")

app = FastAPI(
    title="Swasthya Records API",
    description="National Healthcare Resource & Supply-Chain Resilience Command Center API (Track 3: Smart Health & Supply Chain Resilience)",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration with Explicit Origin Whitelist
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Structured JSON Logging Middleware
@app.middleware("http")
async def structured_logging_middleware(request: Request, call_next):
    request_id = str(uuid.uuid4())
    start_time = time.time()
    user_role = request.headers.get("x-user-role", "ANONYMOUS")
    
    # Redact sensitive header values if any
    safe_endpoint = request.url.path
    
    try:
        response = await call_next(request)
        latency_ms = round((time.time() - start_time) * 1000, 2)
        
        # Log structured JSON payload
        log_payload = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "request_id": request_id,
            "endpoint": safe_endpoint,
            "method": request.method,
            "user_role": user_role,
            "status_code": response.status_code,
            "latency_ms": latency_ms
        }
        logger.info(json.dumps(log_payload))
        response.headers["X-Request-ID"] = request_id
        return response
    except Exception as exc:
        latency_ms = round((time.time() - start_time) * 1000, 2)
        log_payload = {
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "request_id": request_id,
            "endpoint": safe_endpoint,
            "method": request.method,
            "user_role": user_role,
            "status_code": 500,
            "latency_ms": latency_ms,
            "error": str(exc)
        }
        logger.error(json.dumps(log_payload))
        return JSONResponse(
            status_code=500,
            content={
                "detail": "An internal server error occurred while processing the request.",
                "request_id": request_id
            }
        )

# Attach API Router
app.include_router(api_router, prefix=settings.API_V1_STR)

@app.get("/", tags=["Health"])
def root():
    return {
        "app": "Swasthya Records",
        "tagline": "Predict. Prevent. Redistribute.",
        "status": "ONLINE",
        "version": "1.0.0",
        "gcp_project": settings.GCP_PROJECT_ID,
        "docs_url": "/docs"
    }

@app.get("/health", tags=["Health"])
def health_check():
    """Liveness probe endpoint."""
    return {"status": "ok", "health": "HEALTHY", "code": 200}

@app.get("/health/dependencies", tags=["Health"])
def health_dependencies():
    """
    Readiness and subsystem dependency health check.
    Validates BigQuery, SQLite database, Gemini AI configuration, and simulation engine.
    """
    dep_status = {
        "status": "ok",
        "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "environment": settings.ENVIRONMENT,
        "subsystems": {}
    }
    
    # 1. Database Subsystem
    db_ok = False
    try:
        if os.path.exists(settings.SQLITE_DB_PATH):
            conn = sqlite3.connect(settings.SQLITE_DB_PATH)
            cur = conn.cursor()
            cur.execute("SELECT count(*) FROM sqlite_master WHERE type='table';")
            count = cur.fetchone()[0]
            conn.close()
            db_ok = count > 0
    except Exception:
        db_ok = False
    dep_status["subsystems"]["database"] = "HEALTHY" if db_ok else "DEGRADED"

    # 2. BigQuery Configuration
    bq_configured = bool(settings.GCP_PROJECT_ID and settings.BIGQUERY_DATASET)
    dep_status["subsystems"]["bigquery"] = "CONFIGURED" if bq_configured else "UNCONFIGURED"

    # 3. Gemini Operations Copilot
    gemini_key_present = bool(os.getenv("GEMINI_API_KEY"))
    dep_status["subsystems"]["gemini_ai"] = "READY" if gemini_key_present else "MOCK_GROUNDED_FALLBACK"

    # 4. Simulation Engine & Master Dataset
    facility_master_exists = os.path.exists(os.path.join(settings.GOV_DATA_DIR, "clean_facility_master.csv"))
    dep_status["subsystems"]["simulation_engine"] = "READY" if facility_master_exists else "MISSING_DATA"

    return dep_status
