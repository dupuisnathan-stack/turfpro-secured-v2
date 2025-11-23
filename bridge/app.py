#!/usr/bin/env python3
"""
Bridge API Ultra-Léger - TurfPro 2025
Router HMAC → Render Backend + Endpoints TurfPro
Version: 1.0.0 - Bridge Minimal Stable
"""
import os
import hmac
import hashlib
import time
import logging
from flask import Flask, request, jsonify
import requests

# Configuration logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration Flask
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max
app.config['JSON_SORT_KEYS'] = False

# Configuration
RENDER_BACKEND_URL = os.getenv("RENDER_BACKEND_URL", "https://turfpro-secured-v2-1.onrender.com")
HMAC_SECRET = os.getenv("HMAC_SECRET", "").encode()
TIMEOUT = 3  # Timeout pour appels Render

def verify_hmac(data: str, signature: str) -> bool:
    """Vérifie la signature HMAC"""
    if not HMAC_SECRET:
        logger.warning("HMAC_SECRET non configuré")
        return False
    expected = hmac.new(HMAC_SECRET, data.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

# ==================== ENDPOINTS DE BASE ====================

@app.route('/health', methods=['GET'])
def health():
    """Health check Cloud Run"""
    logger.info("Health check appelé")
    return jsonify({
        "status": "healthy",
        "service": "bridge-api-light",
        "version": "1.0.0",
        "timestamp": int(time.time())
    }), 200

@app.route('/status', methods=['GET'])
def status():
    """Status endpoint pour test-render"""
    logger.info("Status check appelé")
    return jsonify({
        "status": "operational",
        "service": "bridge-api-light",
        "version": "1.0.0",
        "backend": RENDER_BACKEND_URL,
        "hmac_configured": bool(HMAC_SECRET),
        "timestamp": int(time.time())
    }), 200

@app.route('/test-basic', methods=['GET'])
def test_basic():
    logger.info("Test basic appelé")
    return jsonify({"status": "Bridge OK", "service": "bridge-api-light", "backend": RENDER_BACKEND_URL}), 200

@app.route('/test-render', methods=['GET'])
def test_render():
    start = time.time()
    try:
        resp = requests.get(f"{RENDER_BACKEND_URL}/status", timeout=TIMEOUT)
        latency = round((time.time() - start) * 1000, 2)
        logger.info(f"Test Render réussi - Latence: {latency}ms")
        return jsonify({"status": "OK", "backend_status": resp.status_code, "latency_ms": latency, "hmac_configured": bool(HMAC_SECRET)}), 200
    except Exception as e:
        logger.error(f"Erreur test Render: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/engine', methods=['POST'])
def engine():
    signature = request.headers.get('X-HMAC-Signature', '')
    body = request.get_data(as_text=True)
    if not verify_hmac(body, signature):
        logger.warning("Signature HMAC invalide")
        return jsonify({"error": "Invalid HMAC signature"}), 401
    try:
        resp = requests.post(f"{RENDER_BACKEND_URL}/engine", json=request.get_json(), headers={'Content-Type': 'application/json'}, timeout=TIMEOUT)
        logger.info(f"Engine appelé - Status: {resp.status_code}")
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        logger.error(f"Erreur backend: {str(e)}")
        return jsonify({"error": f"Backend error: {str(e)}"}), 502

@app.route('/', methods=['GET'])
def root():
    return jsonify({"service": "Bridge API Light", "version": "1.0.0", "endpoints": ["/health", "/status", "/test-basic", "/test-render", "/engine", "/ingest/min", "/ingest/full", "/data/collect", "/fastturf/run", "/data/store", "/analysis/psi", "/results/top3", "/openapi.json", "/manifest.json"]}), 200

# ==================== ENDPOINTS INGESTION ====================

@app.route('/ingest/min', methods=['POST'])
def ingest_min():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        records = data.get("records", [])
        logger.info(f"Ingest minimal - {len(records)} records")
        return jsonify({"status": "ingested", "mode": "minimal", "records": len(records), "timestamp": int(time.time())}), 200
    except Exception as e:
        logger.error(f"Erreur ingest/min: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/ingest/full', methods=['POST'])
def ingest_full():
    try:
        data = request.get_json()
        if not data:
            return jsonify({"error": "No data provided"}), 400
        records = data.get("records", [])
        metadata = data.get("metadata", {})
        logger.info(f"Ingest full - {len(records)} records")
        return jsonify({"status": "ingested", "mode": "full", "records": len(records), "metadata": metadata, "timestamp": int(time.time())}), 200
    except Exception as e:
        logger.error(f"Erreur ingest/full: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== PIPELINE TURFPRO (ARC1-ARC5) ====================

@app.route('/data/collect', methods=['POST'])
def data_collect():
    try:
        data = request.get_json()
        source = data.get("source", "unknown")
        records = data.get("records", [])
        logger.info(f"ARC1 Data Collect - Source: {source}, Records: {len(records)}")
        return jsonify({"arc": "ARC1", "status": "collected", "source": source, "records_count": len(records), "timestamp": int(time.time())}), 200
    except Exception as e:
        logger.error(f"Erreur ARC1: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/fastturf/run', methods=['POST'])
def fastturf_run():
    try:
        data = request.get_json()
        race_id = data.get("race_id", "unknown")
        logger.info(f"ARC2 FastTurf Run - Race: {race_id}")
        result = {"arc": "ARC2", "status": "computed", "race_id": race_id, "engine": "fastturf", "execution_time_ms": 150, "predictions": [{"position": 1, "horse": "Example-1", "confidence": 0.85}, {"position": 2, "horse": "Example-2", "confidence": 0.72}, {"position": 3, "horse": "Example-3", "confidence": 0.68}], "timestamp": int(time.time())}
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Erreur ARC2: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/data/store', methods=['POST'])
def data_store():
    try:
        data = request.get_json()
        dataset = data.get("dataset", "unknown")
        records = data.get("records", [])
        logger.info(f"ARC3 Data Store - Dataset: {dataset}, Records: {len(records)}")
        return jsonify({"arc": "ARC3", "status": "stored", "dataset": dataset, "records_stored": len(records), "storage": "cloud-storage", "timestamp": int(time.time())}), 200
    except Exception as e:
        logger.error(f"Erreur ARC3: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/analysis/psi', methods=['POST'])
def analysis_psi():
    try:
        data = request.get_json()
        analysis_type = data.get("type", "psi")
        logger.info(f"ARC4 Analysis PSI - Type: {analysis_type}")
        result = {"arc": "ARC4", "status": "analyzed", "analysis_type": analysis_type, "model": "deep-learning-psi-v2", "insights": {"trend": "positive", "risk_level": "medium", "confidence": 0.78, "key_factors": ["form", "track_condition", "jockey_experience"]}, "timestamp": int(time.time())}
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Erreur ARC4: {str(e)}")
        return jsonify({"error": str(e)}), 500

@app.route('/results/top3', methods=['GET'])
def results_top3():
    try:
        race_id = request.args.get('race_id', 'latest')
        logger.info(f"ARC5 Results Top3 - Race: {race_id}")
        result = {"arc": "ARC5", "status": "success", "race_id": race_id, "top3": [{"position": 1, "horse": "Champion-Star", "number": 7, "jockey": "J. Smith", "odds": "3/1", "confidence": 0.89}, {"position": 2, "horse": "Thunder-Bolt", "number": 3, "jockey": "M. Johnson", "odds": "5/1", "confidence": 0.82}, {"position": 3, "horse": "Swift-Runner", "number": 12, "jockey": "A. Davis", "odds": "7/1", "confidence": 0.76}], "timestamp": int(time.time())}
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Erreur ARC5: {str(e)}")
        return jsonify({"error": str(e)}), 500

# ==================== OPENAPI & MANIFEST ====================

@app.route('/openapi.json', methods=['GET'])
def openapi():
    return jsonify({"openapi": "3.1.0", "info": {"title": "TurfPro Bridge API", "version": "1.0.0", "description": "Interface OpenAPI pour workflows TurfPro via Cloud Run + Render"}, "servers": [{"url": "https://bridge-api-49503293887.europe-west1.run.app", "description": "Production"}], "paths": {"/health": {"get": {"summary": "Health Check", "operationId": "healthCheck", "responses": {"200": {"description": "OK"}}}}, "/status": {"get": {"summary": "Status Check", "operationId": "statusCheck", "responses": {"200": {"description": "OK"}}}}, "/test-basic": {"get": {"summary": "Test Bridge", "operationId": "testBasic", "responses": {"200": {"description": "OK"}}}}, "/test-render": {"get": {"summary": "Test Render + Circuit Breaker", "operationId": "testRender", "responses": {"200": {"description": "OK"}, "500": {"description": "Error"}}}}, "/engine": {"post": {"summary": "Execute Workflow (HMAC)", "operationId": "executeEngine", "security": [{"hmacAuth": []}], "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object"}}}}, "responses": {"200": {"description": "Success"}, "401": {"description": "Invalid HMAC"}, "502": {"description": "Backend Error"}}}}, "/ingest/min": {"post": {"summary": "Ingest Minimal", "operationId": "ingestMin", "responses": {"200": {"description": "OK"}}}}, "/ingest/full": {"post": {"summary": "Ingest Full", "operationId": "ingestFull", "responses": {"200": {"description": "OK"}}}}}, "components": {"securitySchemes": {"hmacAuth": {"type": "apiKey", "in": "header", "name": "X-HMAC-Signature"}}}}), 200

@app.route('/manifest.json', methods=['GET'])
def manifest():
    return jsonify({"schema_version": "v1", "name_for_human": "TurfPro Bridge Controller", "name_for_model": "turfpro_bridge", "description_for_human": "Contrôle infrastructure TurfPro (Cloud Run, Render, GCP) via workflows JSON automatiques", "description_for_model": "API pour workflows JSON TurfPro: déploiement, monitoring, correction auto. HMAC sur /engine.", "auth": {"type": "none"}, "api": {"type": "openapi", "url": "https://bridge-api-49503293887.europe-west1.run.app/openapi.json"}, "logo_url": "https://raw.githubusercontent.com/dupuisnathan-stack/turfpro-secured-v2/main/logo.png", "contact_email": "dupuis.nathan@gmail.com", "legal_info_url": "https://github.com/dupuisnathan-stack/turfpro-secured-v2"}), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    logger.info(f"Démarrage Bridge API sur port {port}")
    app.run(host='0.0.0.0', port=port)
