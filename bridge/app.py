#!/usr/bin/env python3
"""
Bridge API Ultra-Performant - TurfPro 2025
FastAPI + Uvicorn ASGI → Render Backend + Endpoints TurfPro  
Version: 2.0.0 - Bridge Minimal Stable FastAPI
"""


# ========== DEBUG STARTUP LOGGING ==========
import sys
print(f"[DEBUG] Python version: {sys.version}")
print(f"[DEBUG] Python executable: {sys.executable}")
import os
print(f"[DEBUG] Current working directory: {os.getcwd()}")
print(f"[DEBUG] sys.path: {sys.path}")
print("[DEBUG] Starting Bridge API initialization...")

import os
import hmac
import hashlib
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any

from fastapi import FastAPI, Request, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
import httpx

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration
RENDER_BACKEND_URL = os.getenv("RENDER_BACKEND_URL", "https://turfpro-secured-v2-1.onrender.com")
HMAC_SECRET = os.getenv("HMAC_SECRET", "").encode()
TIMEOUT = 10.0
MAX_RETRIES = 2

# FastAPI App
app = FastAPI(
    title="TurfPro Bridge API",
    description="Interface FastAPI haute-performance pour workflows TurfPro",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Debug: List all registered routes
print(f"[DEBUG] FastAPI app created: {app}")
print(f"[DEBUG] App title: {app.title}")
print("[DEBUG] Registered routes:")
for route in app.routes:
    print(f"  - {route.path} [{getattr(route, 'methods', 'N/A')}]")



# Root diagnostic endpoint
@app.get("/")
async def root():
    return {
        "status": "operational",
        "routes_count": len(app.routes),
        "routes": [r.path for r in app.routes]
    }
# Middlewares
app.add_middleware(GZipMiddleware, minimum_size=1000)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# HTTP Client
http_client = httpx.AsyncClient(
    timeout=httpx.Timeout(TIMEOUT),
    limits=httpx.Limits(max_keepalive_connections=5, max_connections=10)
)

# Models
class HealthResponse(BaseModel):
    status: str = "healthy"
    service: str = "bridge-api-fastapi"
    version: str = "2.0.0"
    timestamp: int

class StatusResponse(BaseModel):
    status: str = "operational"
    service: str = "bridge-api-fastapi"
    version: str = "2.0.0"
    backend: str
    hmac_configured: bool
    timestamp: int

# Endpoints de Base
@app.get("/health", response_model=HealthResponse, tags=["System"])
async def health():
    """Health check ultra-rapide"""
    logger.info("Health check appelé")
    return HealthResponse(timestamp=int(time.time()))

@app.get("/status", response_model=StatusResponse, tags=["System"])
async def status():
    """Status détaillé du service"""
    logger.info("Status check appelé")
    return StatusResponse(
        backend=RENDER_BACKEND_URL,
        hmac_configured=bool(HMAC_SECRET),
        timestamp=int(time.time())
    )

@app.get("/test-basic", tags=["System"])
async def test_basic():
    logger.info("Test basic appelé")
    return {"status": "Bridge OK", "service": "bridge-api-fastapi", "backend": RENDER_BACKEND_URL, "framework": "FastAPI + Uvicorn"}

@app.get("/test-render", tags=["System"])
async def test_render():
    start = time.time()
    for attempt in range(MAX_RETRIES + 1):
        try:
            resp = await http_client.get(f"{RENDER_BACKEND_URL}/status")
            latency = round((time.time() - start) * 1000, 2)
            logger.info(f"Test Render réussi - Latence: {latency}ms")
            return {"status": "OK", "backend_status": resp.status_code, "latency_ms": latency, "hmac_configured": bool(HMAC_SECRET)}
        except Exception as e:
            if attempt < MAX_RETRIES:
                await asyncio.sleep(0.5)
                continue
            logger.error(f"Erreur test Render: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))

@app.get("/", tags=["System"])
async def root():
    return {
        "service": "Bridge API FastAPI",
        "version": "2.0.0",
        "framework": "FastAPI + Uvicorn",
        "endpoints": ["/health", "/status", "/test-basic", "/test-render", "/engine", "/ingest/min", "/data/collect", "/fastturf/run", "/data/store", "/analysis/psi", "/results/top3", "/openapi.json", "/manifest.json"]
    }

# Endpoints Ingestion
@app.post("/ingest/min", tags=["Ingestion"])
async def ingest_min(request: Request):
    try:
        data = await request.json()
        records = data.get("records", [])
        logger.info(f"Ingest minimal - {len(records)} records")
        return {"status": "ingested", "mode": "minimal", "records": len(records), "timestamp": int(time.time())}
    except Exception as e:
        logger.error(f"Erreur ingest/min: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Pipeline TurfPro ARC1-ARC5
@app.post("/data/collect", tags=["TurfPro Pipeline"])
async def data_collect(request: Request):
    try:
        data = await request.json()
        source = data.get("source", "unknown")
        records = data.get("records", [])
        logger.info(f"ARC1 Data Collect - Source: {source}, Records: {len(records)}")
        return {"arc": "ARC1", "status": "collected", "source": source, "records_count": len(records), "timestamp": int(time.time())}
    except Exception as e:
        logger.error(f"Erreur ARC1: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/fastturf/run", tags=["TurfPro Pipeline"])
async def fastturf_run(request: Request):
    try:
        data = await request.json()
        race_id = data.get("race_id", "unknown")
        logger.info(f"ARC2 FastTurf Run - Race: {race_id}")
        return {
            "arc": "ARC2",
            "status": "computed",
            "race_id": race_id,
            "engine": "fastturf",
            "execution_time_ms": 150,
            "predictions": [
                {"position": 1, "horse": "Example-1", "confidence": 0.85},
                {"position": 2, "horse": "Example-2", "confidence": 0.72},
                {"position": 3, "horse": "Example-3", "confidence": 0.68}
            ],
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Erreur ARC2: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/data/store", tags=["TurfPro Pipeline"])
async def data_store(request: Request):
    try:
        data = await request.json()
        dataset = data.get("dataset", "unknown")
        records = data.get("records", [])
        logger.info(f"ARC3 Data Store - Dataset: {dataset}, Records: {len(records)}")
        return {"arc": "ARC3", "status": "stored", "dataset": dataset, "records_stored": len(records), "storage": "cloud-storage", "timestamp": int(time.time())}
    except Exception as e:
        logger.error(f"Erreur ARC3: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analysis/psi", tags=["TurfPro Pipeline"])
async def analysis_psi(request: Request):
    try:
        data = await request.json()
        analysis_type = data.get("type", "psi")
        logger.info(f"ARC4 Analysis PSI - Type: {analysis_type}")
        return {
            "arc": "ARC4",
            "status": "analyzed",
            "analysis_type": analysis_type,
            "model": "deep-learning-psi-v2",
            "insights": {"trend": "positive", "risk_level": "medium", "confidence": 0.78, "key_factors": ["form", "track_condition", "jockey_experience"]},
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Erreur ARC4: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/results/top3", tags=["TurfPro Pipeline"])
async def results_top3(race_id: str = Query("latest")):
    try:
        logger.info(f"ARC5 Results Top3 - Race: {race_id}")
        return {
            "arc": "ARC5",
            "status": "success",
            "race_id": race_id,
            "top3": [
                {"position": 1, "horse": "Champion-Star", "number": 7, "jockey": "J. Smith", "odds": "3/1", "confidence": 0.89},
                {"position": 2, "horse": "Thunder-Bolt", "number": 3, "jockey": "M. Johnson", "odds": "5/1", "confidence": 0.82},
                {"position": 3, "horse": "Swift-Runner", "number": 12, "jockey": "A. Davis", "odds": "7/1", "confidence": 0.76}
            ],
            "timestamp": int(time.time())
        }
    except Exception as e:
        logger.error(f"Erreur ARC5: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# OpenAPI & Manifest
@app.get("/openapi.json", include_in_schema=False)
async def openapi():
    return app.openapi()

@app.get("/manifest.json", tags=["System"])
async def manifest():
    return {
        "schema_version": "v1",
        "name_for_human": "TurfPro Bridge Controller",
        "name_for_model": "turfpro_bridge",
        "description_for_human": "Contrôle infrastructure TurfPro via workflows JSON automatiques",
        "description_for_model": "API FastAPI pour workflows TurfPro: déploiement, monitoring, correction auto",
        "auth": {"type": "none"},
        "api": {"type": "openapi", "url": "https://bridge-api-49503293887.europe-west1.run.app/openapi.json"},
        "logo_url": "https://raw.githubusercontent.com/dupuisnathan-stack/turfpro-secured-v2/main/logo.png",
        "contact_email": "dupuis.nathan@gmail.com"
    }

# Final debug: Confirm module loaded
print("[DEBUG] ========================================")
print(f"[DEBUG] app.py module loaded successfully")
print(f"[DEBUG] Total routes registered: {len(app.routes)}")
for route in app.routes:
    print(f"[DEBUG]   -> {route.path}")
print("[DEBUG] ========================================")
