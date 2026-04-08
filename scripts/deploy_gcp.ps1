#!/usr/bin/env pwsh
# =============================================================================
# OrcheFlowAI — GCP Production Deployment (Windows / PowerShell)
#
# This script automates the full deployment pipeline:
#   1. Build & Push Docker images to Google Artifact Registry
#   2. Initialize & Apply Terraform (Infrastructure as Code)
#   3. Output service URLs
#
# Prerequisites:
#   - gcloud CLI installed and authenticated
#   - Docker Desktop running (configured for gcloud auth)
#   - Terraform installed (>= 1.7)
#   - Project ID: genai-apac-2026-491004
# =============================================================================

$ErrorActionPreference = "Stop"
$PROJ = "D:\Siva\Books\CAREER\HACKATHON\Gen_AI_APAC_2026\OrcheFlowAI"
$PROJECT_ID = "genai-apac-2026-491004"
$REGION = "asia-southeast1"
$REPO = "orcheflow"
$IMAGE_TAG = "latest"

function Write-Step($m) { Write-Host "`n>> $m" -ForegroundColor Cyan }
function Write-OK($m)   { Write-Host "   [OK]   $m" -ForegroundColor Green }
function Write-Fail($m) { Write-Host "   [FAIL] $m" -ForegroundColor Red }

# ── STEP 0: Pre-flight ───────────────────────────────────────────────
Write-Step "Pre-flight checks"

if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) { Write-Fail "gcloud CLI not found."; exit 1 }
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) { Write-Fail "Docker not found."; exit 1 }
if (-not (Get-Command terraform -ErrorAction SilentlyContinue)) { Write-Fail "Terraform not found."; exit 1 }

# Ensure project is set
gcloud config set project $PROJECT_ID | Out-Null
Write-OK "GCP Project: $PROJECT_ID"

# Auth Docker to Artifact Registry
Write-Step "Authenticating Docker to Google Artifact Registry..."
gcloud auth configure-docker "${REGION}-docker.pkg.dev" --quiet
Write-OK "Docker auth configured"

# Ensure Artifact Registry repo exists
Write-Step "Checking Artifact Registry..."
$repos = gcloud artifacts repositories list --location=$REGION --format="value(name)"
if ($repos -notcontains "projects/$PROJECT_ID/locations/$REGION/repositories/$REPO") {
    Write-Host "Creating repository $REPO..." -ForegroundColor Yellow
    gcloud artifacts repositories create $REPO --repository-format=docker --location=$REGION --description="OrcheFlowAI container repository"
    Write-OK "Repository created"
} else {
    Write-OK "Repository exists"
}

# ── STEP 1: Build & Push Images ──────────────────────────────────────
$services = @(
    @{ name = "mcp"; path = "mcp_server"; file = "mcp_server/Dockerfile" },
    @{ name = "agents"; path = "agents"; file = "agents/Dockerfile" },
    @{ name = "api"; path = "api"; file = "api/Dockerfile" }
)

foreach ($svc in $services) {
    $fullName = "orcheflow-$($svc.name)"
    $imagePath = "${REGION}-docker.pkg.dev/${PROJECT_ID}/${REPO}/${fullName}:${IMAGE_TAG}"
    
    Write-Step "Building $fullName..."
    docker build -t $imagePath -f (Join-Path $PROJ $svc.file) $PROJ
    Write-OK "$fullName built"

    Write-Step "Pushing $fullName to Artifact Registry..."
    docker push $imagePath
    Write-OK "$fullName pushed"
}

# ── STEP 2: Terraform Apply ──────────────────────────────────────────
Write-Step "Initializing Terraform..."
Set-Location (Join-Path $PROJ "infra")
terraform init -reconfigure # Using reconfigure to ensure backend GCS is picked up

Write-Step "Applying Terraform plan..."
terraform apply -auto-approve -var="project_id=$PROJECT_ID" -var="region=$REGION" -var="image_tag=$IMAGE_TAG" -var="repo=$REPO"

# ── STEP 3: Summary ──────────────────────────────────────────────────
Write-Step "Deployment Complete!"
$api_url = terraform output -raw api_url
$mcp_url = terraform output -raw mcp_url
$agents_url = terraform output -raw agents_url

Write-Host "  OrcheFlowAI Production URLs"
Write-Host "  API:       $api_url"
Write-Host "  Docs:      $api_url/docs"
Write-Host "  MCP:       $mcp_url"
Write-Host "  Agents:    $agents_url"

Set-Location $PROJ

