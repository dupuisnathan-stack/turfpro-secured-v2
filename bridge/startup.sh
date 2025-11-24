#!/bin/bash
echo "=== STARTUP DEBUG ==="
echo "PWD: $(pwd)"
echo "Files in /app:"
ls -la
echo "PORT=$PORT"
echo "Python version: $(python --version)"
echo "Uvicorn version: $(python -m uvicorn --version)"
echo "Starting Uvicorn..."
python -m uvicorn app:app --host 0.0.0.0 --port $PORT --log-level debug
