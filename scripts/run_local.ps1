#!/usr/bin/env pwsh
# =============================================================================
# OrcheFlowAI — Local Development Runner (Windows / PowerShell)
# Run this script from the project root.
# Usage:
#   .\scripts\run_local.ps1           # start all services
#   .\scripts\run_local.ps1 -Stop     # stop all services
#   .\scripts\run_local.ps1 -Reset    # wipe volumes and restart
# =============================================================================

param(
    [switch]$Stop,
    [switch]$Reset,
    [switch]$LogsOnly,
    [string]$Service = ""
)

$ErrorActionPreference = "Stop"
$proj = $PSScriptRoot | Split-Path -Parent

function Write-Step($msg) { Write-Host "`n>> $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "   OK  $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "   WARN $msg" -ForegroundColor Yellow }
function Write-Fail($msg) { Write-Host "   FAIL $msg" -ForegroundColor Red }

# ── 0. Pre-flight checks ──────────────────────────────────────────
Write-Step "Pre-flight checks"

if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Fail "Docker not found. Install Docker Desktop: https://www.docker.com/products/docker-desktop"
    exit 1
}
if (-not (Get-Command gcloud -ErrorAction SilentlyContinue)) {
    Write-Warn "gcloud CLI not found. Vertex AI features will not work locally without ADC."
} else {
    $adcPath = "$env:APPDATA\gcloud\application_default_credentials.json"
    if (Test-Path $adcPath) {
        Write-OK "Application Default Credentials found"
    } else {
        Write-Warn "ADC not configured. Run: gcloud auth application-default login"
    }
}

$envFile = Join-Path $proj ".env"
if (-not (Test-Path $envFile)) {
    Write-Step "Creating .env from .env.example"
    Copy-Item (Join-Path $proj ".env.example") $envFile
    Write-OK ".env created. Edit it if needed before running."
} else {
    Write-OK ".env exists"
}

# ── Handle flags ──────────────────────────────────────────────────
if ($Stop) {
    Write-Step "Stopping all services"
    docker compose -f (Join-Path $proj "docker-compose.yml") down
    Write-OK "All services stopped"
    exit 0
}

if ($Reset) {
    Write-Step "Resetting volumes and containers"
    docker compose -f (Join-Path $proj "docker-compose.yml") down -v --remove-orphans
    Write-OK "Reset complete"
}

if ($LogsOnly) {
    $svcArg = if ($Service) { $Service } else { "" }
    docker compose -f (Join-Path $proj "docker-compose.yml") logs -f $svcArg
    exit 0
}

# ── 1. Start services ─────────────────────────────────────────────
Write-Step "Starting OrcheFlowAI services (docker compose)"
docker compose -f (Join-Path $proj "docker-compose.yml") up -d --build

# ── 2. Wait for health ────────────────────────────────────────────
Write-Step "Waiting for API health check (up to 60s)..."
$maxWait = 60; $waited = 0; $healthy = $false
while ($waited -lt $maxWait) {
    Start-Sleep -Seconds 3; $waited += 3
    try {
        $resp = Invoke-RestMethod "http://localhost:8000/v1/health" -TimeoutSec 3
        if ($resp.status -eq "ok" -or $resp.status -eq "healthy") { $healthy = $true; break }
    } catch { }
    Write-Host "   Waiting... ($waited/${maxWait}s)" -NoNewline; Write-Host ""
}

if ($healthy) {
    Write-OK "API is healthy at http://localhost:8000"
} else {
    Write-Warn "API did not report healthy within ${maxWait}s. Check logs:"
    Write-Host "   docker compose logs api" -ForegroundColor Gray
}

# ── 3. Summary ────────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " OrcheFlowAI Local Environment Ready" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Frontend:     " -NoNewline; Write-Host "open frontend/index.html in browser" -ForegroundColor Yellow
Write-Host " API:          " -NoNewline; Write-Host "http://localhost:8000/v1/health" -ForegroundColor Green
Write-Host " API Docs:     " -NoNewline; Write-Host "http://localhost:8000/docs" -ForegroundColor Green
Write-Host " MCP Server:   " -NoNewline; Write-Host "http://localhost:8001" -ForegroundColor Green
Write-Host " Agents:       " -NoNewline; Write-Host "http://localhost:8002" -ForegroundColor Green
Write-Host " Postgres:     " -NoNewline; Write-Host "localhost:5432 (user: orcheflow)" -ForegroundColor Green
Write-Host ""
Write-Host " Live logs:    " -NoNewline; Write-Host ".\scripts\run_local.ps1 -LogsOnly" -ForegroundColor Gray
Write-Host " Stop:         " -NoNewline; Write-Host ".\scripts\run_local.ps1 -Stop" -ForegroundColor Gray
Write-Host " Reset all:    " -NoNewline; Write-Host ".\scripts\run_local.ps1 -Reset" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
