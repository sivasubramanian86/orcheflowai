#!/usr/bin/env pwsh
# =============================================================================
# OrcheFlowAI — Test Runner (Windows / PowerShell)
# Runs unit, integration, and security checks locally.
# Usage:
#   .\scripts\run_tests.ps1            # full suite
#   .\scripts\run_tests.ps1 -Unit      # unit tests only (fast, no Docker)
#   .\scripts\run_tests.ps1 -Lint      # lint + type check only
#   .\scripts\run_tests.ps1 -Security  # pip-audit + bandit only
# =============================================================================

param(
    [switch]$Unit,
    [switch]$Integration,
    [switch]$Lint,
    [switch]$Security,
    [switch]$All
)

$ErrorActionPreference = "Continue"
$proj = $PSScriptRoot | Split-Path -Parent
$PASS = 0; $FAIL = 0

function Write-Step($msg) { Write-Host "`n>> $msg" -ForegroundColor Cyan }
function Write-OK($msg)   { Write-Host "   PASS $msg" -ForegroundColor Green;  $global:PASS++ }
function Write-Fail($msg) { Write-Host "   FAIL $msg" -ForegroundColor Red;    $global:FAIL++ }

# Detect virtual environment
$venvPy = Join-Path $proj ".venv\Scripts\python.exe"
$py = if (Test-Path $venvPy) { $venvPy } else { "python" }
Write-Host "Python: $((& $py --version 2>&1) | Select-Object -First 1)" -ForegroundColor Gray

# ── Install dev deps if needed ────────────────────────────────────
Write-Step "Checking dev dependencies"
& $py -m pip install -q -r (Join-Path $proj "requirements-dev.txt") 2>&1 | Out-Null
& $py -m pip install -q -r (Join-Path $proj "agents\requirements.txt") 2>&1 | Out-Null
& $py -m pip install -q -r (Join-Path $proj "api\requirements.txt") 2>&1 | Out-Null
Write-OK "Dependencies installed"

# ── LINT (always run unless only -Security) ───────────────────────
if (-not $Security -or $Lint -or $All -or (-not $Unit -and -not $Integration)) {
    Write-Step "Ruff lint"
    $ruffResult = & $py -m ruff check $proj --exclude ".venv,__pycache__,node_modules" 2>&1
    if ($LASTEXITCODE -eq 0) { Write-OK "Ruff lint clean" }
    else { Write-Fail "Ruff found issues:`n$ruffResult" }

    Write-Step "Black format check"
    $blackResult = & $py -m black $proj --check --quiet --exclude "\.venv|__pycache__|node_modules" 2>&1
    if ($LASTEXITCODE -eq 0) { Write-OK "Black formatting consistent" }
    else { Write-Fail "Black would reformat files. Run: black . to fix`n$blackResult" }
}

# ── UNIT TESTS ────────────────────────────────────────────────────
if ($Unit -or $All -or (-not $Integration -and -not $Lint -and -not $Security)) {
    Write-Step "Unit tests (fast — no I/O)"
    $unitResult = & $py -m pytest (Join-Path $proj "tests\unit") -v -x `
        --tb=short --no-header -q 2>&1
    if ($LASTEXITCODE -eq 0) { Write-OK "Unit tests passed" }
    else { Write-Fail "Unit tests failed:`n$unitResult" }
}

# ── INTEGRATION TESTS ─────────────────────────────────────────────
if ($Integration -or $All) {
    Write-Step "Integration tests (requires services or mocks)"
    $intResult = & $py -m pytest (Join-Path $proj "tests\integration") -v -x `
        --tb=short --no-header -q 2>&1
    if ($LASTEXITCODE -eq 0) { Write-OK "Integration tests passed" }
    else { Write-Fail "Integration tests failed:`n$intResult" }
}

# ── SECURITY SCAN ─────────────────────────────────────────────────
if ($Security -or $All -or (-not $Unit -and -not $Integration -and -not $Lint)) {
    Write-Step "pip-audit (dependency vulnerability scan)"
    $auditResult = & $py -m pip_audit -r (Join-Path $proj "agents\requirements.txt") 2>&1
    if ($LASTEXITCODE -eq 0) { Write-OK "No known vulnerabilities" }
    else { Write-Fail "Vulnerabilities found:`n$auditResult" }

    Write-Step "Bandit (static security analysis)"
    $banditResult = & $py -m bandit -r (Join-Path $proj "agents") (Join-Path $proj "api") `
        -ll -q --exclude ".venv,__pycache__" 2>&1
    if ($LASTEXITCODE -eq 0) { Write-OK "Bandit security scan clean" }
    else { Write-Fail "Bandit found issues:`n$banditResult" }
}

# ── Coverage Report (unit + integration) ─────────────────────────
if ($All -or (-not $Unit -and -not $Integration -and -not $Lint -and -not $Security)) {
    Write-Step "Coverage report"
    & $py -m pytest (Join-Path $proj "tests") `
        --cov=agents --cov=api --cov-report=term-missing --no-header -q 2>&1
}

# ── Summary ───────────────────────────────────────────────────────
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Test Summary" -ForegroundColor White
Write-Host "========================================" -ForegroundColor Cyan
Write-Host " Passed: $PASS" -ForegroundColor Green
if ($FAIL -gt 0) {
    Write-Host " Failed: $FAIL" -ForegroundColor Red
    Write-Host " Status: BLOCKED — fix failures before pushing" -ForegroundColor Red
    exit 1
} else {
    Write-Host " Status: ALL CHECKS PASSED" -ForegroundColor Green
    Write-Host " Ready to commit and push." -ForegroundColor Green
    exit 0
}
