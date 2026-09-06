# ==============================================================================
# JobMentor AI - Google Cloud Run Deployment Script (PowerShell)
# Mandatory Label: dev-tutorial=cloud-run-ai-challenge
# ==============================================================================

$ErrorActionPreference = "Stop"

$ServiceName = "jobmentor-ai"
$Region = if ($env:REGION) { $env:REGION } else { "us-central1" }
$ProjectId = $(gcloud config get-value project 2>$null)

Write-Host "========================================================" -ForegroundColor Cyan
Write-Host " Deploying JobMentor AI to Google Cloud Run" -ForegroundColor Cyan
Write-Host " Challenge Label: dev-tutorial=cloud-run-ai-challenge" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Cyan

if (-not $ProjectId) {
    Write-Error "No active GCP project found. Run: gcloud config set project <PROJECT_ID>"
    exit 1
}

Write-Host "Active Project: $ProjectId"
Write-Host "Target Region:  $Region"
Write-Host "Service Name:   $ServiceName"

# Enable required APIs
Write-Host "Enabling GCP APIs..." -ForegroundColor Yellow
gcloud services enable run.googleapis.com cloudbuild.googleapis.com firestore.googleapis.com artifactregistry.googleapis.com

$GeminiKey = $env:GEMINI_API_KEY
if (-not $GeminiKey) {
    $GeminiKey = Read-Host "Enter your Gemini API Key (or press Enter to deploy in demo mode)"
}

$EnvVars = "ENVIRONMENT=production,GEMINI_MODEL=gemini-2.5-flash,GOOGLE_CLOUD_PROJECT=$ProjectId"
if ($GeminiKey) {
    $EnvVars += ",GEMINI_API_KEY=$GeminiKey"
}

Write-Host "Deploying container to Google Cloud Run with challenge label..." -ForegroundColor Green
gcloud run deploy $ServiceName `
    --source . `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --labels="dev-tutorial=cloud-run-ai-challenge" `
    --set-env-vars=$EnvVars `
    --memory=1Gi `
    --cpu=1 `
    --min-instances=0 `
    --max-instances=10 `
    --timeout=300

$ServiceUrl = $(gcloud run services describe $ServiceName --region $Region --format 'value(status.url)')

Write-Host ""
Write-Host "========================================================" -ForegroundColor Green
Write-Host " Deployment Complete!" -ForegroundColor Green
Write-Host " Live Cloud Run URL: $ServiceUrl" -ForegroundColor Yellow
Write-Host " Label Applied: dev-tutorial=cloud-run-ai-challenge" -ForegroundColor Cyan
Write-Host "========================================================" -ForegroundColor Green
