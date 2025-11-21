#!/bin/bash
set -euo pipefail

PROJECT_ID="turfo-service"
REGION="europe-west1"
SERVICE_NAME="bridge-api"

echo "🚀 Déploiement Bridge API Light..."

gcloud run deploy ${SERVICE_NAME} \
  --source=. \
  --region=${REGION} \
  --platform=managed \
  --m512Mi256Mi \
  --cpu=1 \
  --concurrency=80 \
  --timeout=30s \
  --min-instances=0 \
  --max-instances200 \
  --port=8080 \
  --service-account=bridge-api-sa@turfo-service.iam.gserviceaccount.com \
  --set-secrets=HMAC_SECRET=bridge-hmac-key:latest \
  --allow-unauthenticated \
  --project=${PROJECT_ID}

echo "✅ URL: $(gcloud run services describe ${SERVICE_NAME} --region=${REGION} --format='value(status.url)')"
