#!/bin/bash
SERVICE_URL=$(gcloud run services describe bridge-api --region=europe-west1 --format='value(status.url)')

echo "🧪 Tests Bridge API: ${SERVICE_URL}"
echo ""
echo "1️⃣ Health Check:"
curl -s "${SERVICE_URL}/health" | jq .
echo ""
echo "2️⃣ Test Basic:"
curl -s "${SERVICE_URL}/test-basic" | jq .
echo ""
echo "3️⃣ Test Render:"
curl -s "${SERVICE_URL}/test-render" | jq .
echo ""
echo "✅ Tests terminés !"
