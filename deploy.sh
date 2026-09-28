#!/bin/bash
# 🚀 Cloud Run 1-Click Deployment Script for KSR Biology Portal
set -e

SERVICE_NAME="ksrbiology"
REGION="asia-south1" # Or us-central1 / your preferred region
BUCKET_NAME="pika-wil"
FOLDER_PREFIX="ksr-biology"

echo "=========================================="
echo "🌿 Deploying KSR Biology to Google Cloud Run"
echo "=========================================="

gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --region "$REGION" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars="GCS_BUCKET_NAME=$BUCKET_NAME,GCS_FOLDER_PREFIX=$FOLDER_PREFIX,ADMIN_PASSWORD=ksradmin2026,SECRET_KEY=ksr-biology-cloud-run-key-2026"

echo "=========================================="
echo "✅ Deployment Complete!"
echo "=========================================="
