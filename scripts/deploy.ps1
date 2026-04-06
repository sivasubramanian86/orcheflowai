# OrcheFlowAI — Cloud Run Deployment Script (v1.2.6)
# Usage: ./deploy.ps1 -ProjectId your-project-id

param (
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,
    [string]$Region = "us-central1",
    [string]$ServiceAccount = "orcheflow-sa"
)

Write-Host "🚀 Starting OrcheFlowAI Cloud Deployment..." -ForegroundColor Cyan

# 1. Build Container with Cloud Build
Write-Host "📦 Building container..." -ForegroundColor Yellow
gcloud builds submit --tag gcr.io/$ProjectId/orcheflow-api . --project $ProjectId

# 2. Deploy to Cloud Run with Workload Identity
Write-Host "🌐 Deploying to Cloud Run..." -ForegroundColor Yellow
gcloud run deploy orchestrator-api `
    --image gcr.io/$ProjectId/orcheflow-api `
    --platform managed `
    --region $Region `
    --allow-unauthenticated `
    --service-account $ServiceAccount@$ProjectId.iam.gserviceaccount.com `
    --set-env-vars="GOOGLE_CLOUD_PROJECT=$ProjectId" `
    --project $ProjectId

Write-Host "✅ Deployment Complete!" -ForegroundColor Green
