#!/usr/bin/env bash
# ==============================================================================
# JobMentor AI - Google Cloud Run Automated Deployment Script
# Mandatory Label: dev-tutorial=cloud-run-ai-challenge
# ==============================================================================

set -e

SERVICE_NAME="jobmentor-ai"
REGION="${REGION:-us-central1}"
PROJECT_ID="$(gcloud config get-value project 2>/dev/null)"

echo "========================================================"
echo " Deploying JobMentor AI to Google Cloud Run"
echo " Challenge Label: dev-tutorial=cloud-run-ai-challenge"
echo "========================================================"

if [ -z "$PROJECT_ID" ]; then
  echo "Error: No active GCP project configured."
  echo "Run: gcloud config set project <YOUR_PROJECT_ID>"
  exit 1
fi

echo "Active Project: $PROJECT_ID"
echo "Target Region:  $REGION"
echo "Service Name:   $SERVICE_NAME"
echo ""

# Enable required Google Cloud APIs
echo "Ensuring required GCP APIs are enabled..."
gcloud services enable \
  run.googleapis.com \
  cloudbuild.googleapis.com \
  firestore.googleapis.com \
  artifactregistry.googleapis.com \
  iam.googleapis.com

# Fix Storage Object Viewer permission for Compute Service Account
PROJECT_NUMBER=$(gcloud projects describe "$PROJECT_ID" --format='value(projectNumber)' 2>/dev/null || echo "")
if [ -n "$PROJECT_NUMBER" ]; then
  echo "Granting Cloud Storage permissions to Compute Service Account (${PROJECT_NUMBER}-compute@developer.gserviceaccount.com)..."
  gcloud projects add-iam-policy-binding "$PROJECT_ID" \
    --member="serviceAccount:${PROJECT_NUMBER}-compute@developer.gserviceaccount.com" \
    --role="roles/storage.admin" --quiet 2>/dev/null || true
fi

# Check for GEMINI_API_KEY
if [ -z "$GEMINI_API_KEY" ]; then
  echo "Warning: GEMINI_API_KEY environment variable is not set locally."
  read -r -p "Enter your Gemini API Key (or press enter to deploy in demo mode): " USER_KEY
  if [ -n "$USER_KEY" ]; then
    GEMINI_API_KEY="$USER_KEY"
  fi
fi

ENV_VARS="ENVIRONMENT=production,GEMINI_MODEL=gemini-2.5-flash,GOOGLE_CLOUD_PROJECT=${PROJECT_ID}"
if [ -n "$GEMINI_API_KEY" ]; then
  ENV_VARS="${ENV_VARS},GEMINI_API_KEY=${GEMINI_API_KEY}"
fi

echo ""
echo "Building container and deploying to Cloud Run..."
gcloud run deploy "$SERVICE_NAME" \
  --source . \
  --platform managed \
  --region "$REGION" \
  --allow-unauthenticated \
  --labels="dev-tutorial=cloud-run-ai-challenge" \
  --set-env-vars="$ENV_VARS" \
  --memory=1Gi \
  --cpu=1 \
  --min-instances=0 \
  --max-instances=10 \
  --timeout=300

echo ""
echo "========================================================"
echo " Successfully Deployed!"
SERVICE_URL=$(gcloud run services describe "$SERVICE_NAME" --region "$REGION" --format 'value(status.url)')
echo " Live Cloud Run URL: $SERVICE_URL"
echo " Verified Label: dev-tutorial=cloud-run-ai-challenge"
echo "========================================================"
