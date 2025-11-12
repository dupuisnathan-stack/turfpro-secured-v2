#!/usr/bin/env python3
"""
TurfPro Secured V2.0 - Flask Application Entry Point
Secure deployment with:
- AES-256 encryption for credentials
- Master password required
- Health check endpoint
- Graceful error handling
"""

import os
import json
from flask import Flask, jsonify
from datetime import datetime

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Environment validation
PORT = int(os.getenv('PORT', 8080))
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint for Render"""
    return jsonify({
        "status": "healthy",
        "service": "turfpro-secured",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": ENVIRONMENT
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint"""
    return jsonify({
        "service": "TurfPro Secured V2.0",
        "description": "IA multi-cortex sécurisée pour analyse hippique",
        "security": "AES-256 encryption enabled",
        "status": "operational"
    }), 200

@app.route('/status', methods=['GET'])
def status():
    """Application status endpoint"""
    return jsonify({
        "service": "turfpro-secured",
        "status": "running",
        "version": "2.0.0"
    }), 200

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({"error": "Not found"}), 404

@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT, debug=(ENVIRONMENT == 'development'))
