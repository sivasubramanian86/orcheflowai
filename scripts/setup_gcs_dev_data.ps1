# OrcheFlowAI — GCS Ingestion Setup & Test Script
# ─── Requirements: gcloud CLI authenticated ──────────────────────────────────

param (
    [string]$BucketName = "orcheflowai-demo-data-$(Get-Random -Minimum 1000 -Maximum 9999)",
    [string]$SampleFile = "demo\sample_meeting_notes.txt"
)

Write-Host "🚀 OrcheFlowAI — Provisioning GCS Verification Environment" -ForegroundColor Cyan

# 1. Get Project ID
$ProjectID = $(gcloud config get-value project)
if (-not $ProjectID) {
    Write-Error "GCP Project ID not found. Run 'gcloud auth login' and 'gcloud config set project [PROJECT_ID]'"
    return
}

# 2. Create Bucket (if not exists)
Write-Host "Creating bucket: gs://$BucketName in project $ProjectID..."
gsutil mb -p $ProjectID gs://$BucketName/ 2>$null

# 3. Upload Sample Data
Write-Host "Uploading sample data: $SampleFile..."
gsutil cp $SampleFile "gs://$BucketName/notes/kickoff.txt"

# 4. Success Output
Write-Host "`n✅ Verification Data Ready!" -ForegroundColor Green
Write-Host "--------------------------------------------------------"
Write-Host "GCS URI: gs://$BucketName/notes/kickoff.txt" -ForegroundColor Yellow
Write-Host "--------------------------------------------------------"
Write-Host "`nYou can now verify the agent flow by prompt:"
Write-Host "`"Ingest the notes from gs://$BucketName/notes/kickoff.txt, extract action items, and create tasks for them.`"" -ForegroundColor Gray
