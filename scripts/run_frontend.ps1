#!/usr/bin/env pwsh
# =============================================================================
# OrcheFlowAI — Frontend Dev Server (Windows / PowerShell)
# Starts the Vite dev server with proxy to FastAPI on :8000
# Usage:  .\scripts\run_frontend.ps1
# =============================================================================

$ErrorActionPreference = "Stop"
$proj = $PSScriptRoot | Split-Path -Parent
$fe   = Join-Path $proj "frontend"

function Write-Step($msg) { Write-Host "`n>> $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "   OK  $msg" -ForegroundColor Green }
function Write-Warn($msg) { Write-Host "   WARN $msg" -ForegroundColor Yellow }

# ── Check Node ───────────────────────────────────────────────────────
Write-Step "Pre-flight"
if (-not (Get-Command node -ErrorAction SilentlyContinue)) {
    Write-Host "Node.js not found. Install from https://nodejs.org" -ForegroundColor Red
    exit 1
}
Write-OK "Node $(node --version)"

# ── Install deps if node_modules missing ─────────────────────────────
if (-not (Test-Path (Join-Path $fe "node_modules"))) {
    Write-Step "Installing npm dependencies"
    Push-Location $fe
    npm install
    Pop-Location
    Write-OK "Dependencies installed"
} else {
    Write-OK "node_modules exists"
}

# ── Start Vite dev server ─────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " OrcheFlowAI — Frontend Dev Server" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Dashboard:  http://localhost:3000" -ForegroundColor Green
Write-Host " API proxy:  /v1  ->  http://localhost:8000/v1" -ForegroundColor Gray
Write-Host " Hot reload: enabled (Vite HMR)" -ForegroundColor Gray
Write-Host ""
Write-Host " TIP: Start the API first:" -ForegroundColor Yellow
Write-Host "   .\scripts\run_local.ps1" -ForegroundColor Gray
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Push-Location $fe
npx vite
Pop-Location
