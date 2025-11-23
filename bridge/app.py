#!/usr/bin/env python3
"""
Bridge API Ultra-Léger - TurfPro 2025
Router HMAC → Render Backend uniquement
Aucune logique métier, performances maximales
"""
import os
import hmac
import hashlib
import time
from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Configuration Flask
app.config['MAX_CONTENT_LENGTH'] = 5 * 1024 * 1024  # 5MB max

# Configuration
RENDER_BACKEND_URL = "https://turfpro-secured-v2-1.onrender.com"
HMAC_SECRET = os.getenv("HMAC_SECRET", "").encode()
TIMEOUT = 3  # Timeout pour appels Render
def verify_hmac(data: str, signature: str) -> bool:
    """Vérifie la signature HMAC"""
    if not HMAC_SECRET:
        return False
    expected = hmac.new(HMAC_SECRET, data.encode(), hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature)

@app.route('/health', methods=['GET'])
def health():
    """Health check Cloud Run"""
    return jsonify({
        "status": "healthy",
        "service": "bridge-api-light",
        "version": "1.0.0",
        "timestamp": int(time.time())
    }), 200

@app.route('/test-basic', methods=['GET'])
def test_basic():
    """Test endpoint pour ChatGPT"""
    return jsonify({
        "status": "Bridge OK",
        "service": "bridge-api-light",
        "backend": RENDER_BACKEND_URL
    }), 200

@app.route('/test-render', methods=['GET'])
def test_render():
    """Test ping Render + latence"""
    start = time.time()
    try:
        resp = requests.get(f"{RENDER_BACKEND_URL}/status", timeout=TIMEOUT)
        latency = round((time.time() - start) * 1000, 2)
        return jsonify({
            "status": "OK",
            "backend_status": resp.status_code,
            "latency_ms": latency,
            "hmac_configured": bool(HMAC_SECRET)
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/engine', methods=['POST'])
def engine():
    """Proxy vers Render /engine avec HMAC"""
    # Vérification HMAC
    signature = request.headers.get('X-HMAC-Signature', '')
    body = request.get_data(as_text=True)
    
    if not verify_hmac(body, signature):
        return jsonify({"error": "Invalid HMAC signature"}), 401
    
    # Proxy vers Render
    try:
        resp = requests.post(
            f"{RENDER_BACKEND_URL}/engine",
            json=request.get_json(),
            headers={'Content-Type': 'application/json'},
            timeout=TIMEOUT
        )
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": f"Backend error: {str(e)}"}), 502

@app.route('/', methods=['GET'])
def root():
    """Root endpoint"""
    return jsonify({
        "service": "Bridge API Light",
        "version": "1.0.0",
        "endpoints": ["/health", "/test-basic", "/test-render", "/engine"]
    }), 200

@app.route('/openapi.json', methods=['GET'])
def openapi():
    """OpenAPI specification pour ChatGPT Actions"""
    return jsonify({
        "openapi": "3.1.0",
        "info": {
            "title": "TurfPro Bridge API",
            "version": "1.0.0",
            "description": "Interface OpenAPI pour workflows TurfPro via Cloud Run + Render"
        },
        "servers": [
            {"url": "https://bridge-api-49503293887.europe-west1.run.app", "description": "Production"}
        ],
        "paths": {
            "/health": {
                "get": {
                    "summary": "Health Check",
                    "operationId": "healthCheck",
                    "responses": {"200": {"description": "OK"}}
                }
            },
            "/test-basic": {
                "get": {
                    "summary": "Test Bridge",
                    "operationId": "testBasic",
                    "responses": {"200": {"description": "OK"}}
                }
            },
            "/test-render": {
                "get": {
                    "summary": "Test Render + Circuit Breaker",
                    "operationId": "testRender",
                    "responses": {"200": {"description": "OK"}, "500": {"description": "Error"}}
                }
            },
            "/engine": {
                "post": {
                    "summary": "Execute Workflow (HMAC)",
                    "operationId": "executeEngine",
                    "security": [{"hmacAuth": []}],
                    "requestBody": {
                        "required": true,
                        "content": {"application/json": {"schema": {"type": "object"}}}
                    },
                    "responses": {
                        "200": {"description": "Success"},
                        "401": {"description": "Invalid HMAC"},
                        "502": {"description": "Backend Error"}
                    }
                }
            }
        },
        "components": {
            "securitySchemes": {
                "hmacAuth": {
                    "type": "apiKey",
                    "in": "header",
                    "name": "X-HMAC-Signature"
                }
            }
        }
    }), 200

@app.route('/manifest.json', methods=['GET'])
def manifest():
    """Manifest ChatGPT Actions"""
    return jsonify({
        "schema_version": "v1",
        "name_for_human": "TurfPro Bridge Controller",
        "name_for_model": "turfpro_bridge",
        "description_for_human": "Contrôle infrastructure TurfPro (Cloud Run, Render, GCP) via workflows JSON automatiques",
        "description_for_model": "API pour workflows JSON TurfPro: déploiement, monitoring, correction auto. HMAC sur /engine.",
        "auth": {"type": "none"},
        "api": {
            "type": "openapi",
            "url": "https://bridge-api-49503293887.europe-west1.run.app/openapi.json"
        },
        "logo_url": "https://raw.githubusercontent.com/dupuisnathan-stack/turfpro-secured-v2/main/logo.png",
        "contact_email": "dupuis.nathan@gmail.com",
        "legal_info_url": "https://github.com/dupuisnathan-stack/turfpro-secured-v2"
    }), 200

if __name__ == '__main__':
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
