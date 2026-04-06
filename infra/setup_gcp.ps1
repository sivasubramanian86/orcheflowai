# ⚡ OrcheFlowAI — Automatic GCP Infrastructure Setup (v1.2.6)
# Project: genai-apac-2026-491004

$PROJECT_ID = "genai-apac-2026-491004"
$REGION = "us-central1"
$SA_NAME = "orcheflow-sa"
$SA_EMAIL = "$SA_NAME@$PROJECT_ID.iam.gserviceaccount.com"

Write-Host "⚙️  Starting GCP Environment Configuration..." -ForegroundColor Cyan

# 1. Enable Required Services
Write-Host "🚀 Enabling APIs..." -ForegroundColor Yellow
gcloud services enable `
    aiplatform.googleapis.com `
    routes.googleapis.com `
    secretmanager.googleapis.com `
    calendar-json.googleapis.com `
    fitness.googleapis.com `
    run.googleapis.com `
    cloudbuild.googleapis.com `
    --project $PROJECT_ID

# 2. Create Service Account if not exists
Write-Host "🧙 Creating Service Account ($SA_NAME)..." -ForegroundColor Yellow
gcloud iam service-accounts create $SA_NAME `
    --display-name="OrcheFlowAI System Account" `
    --project $PROJECT_ID `
    --quiet 2>$null

Write-Host "⏳ Waiting for IAM propagation..." -ForegroundColor Gray
Start-Sleep -Seconds 5

# 3. Assign Required IAM Roles
Write-Host "🛡️  Assigning IAM Roles..." -ForegroundColor Yellow
$roles = @(
    "roles/aiplatform.user",
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/monitoring.metricWriter"
)

foreach ($role in $roles) {
    gcloud projects add-iam-policy-binding $PROJECT_ID `
        --member="serviceAccount:$SA_EMAIL" `
        --role="$role" `
        --quiet
}

# 4. Initialize Secret Manager Placeholders
Write-Host "🤫 Initializing Secrets..." -ForegroundColor Yellow
$secrets = @("GOOGLE_CLIENT_ID", "GOOGLE_CLIENT_SECRET")
foreach ($secret in $secrets) {
    gcloud secrets create $secret `
        --replication-policy="automatic" `
    --project $PROJECT_ID `
    --quiet 2>$null
    
    # Allow Service Account to read this secret
    gcloud secrets add-iam-policy-binding $secret `
        --member="serviceAccount:$SA_EMAIL" `
        --role="roles/secretmanager.secretAccessor" `
        --project $PROJECT_ID `
        --quiet
}

Write-Host "✅ GCP Infrastructure Ready for Workload Identity!" -ForegroundColor Green
Write-Host "👉 HANDOFF: Please visit the Google Cloud Console to add your OAuth secrets to Secret Manager." -ForegroundColor White
