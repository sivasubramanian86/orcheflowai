# OrcheFlowAI — Database Migration Tool
# Environment: production or local-preview.
# Requires: Psql installed on path.

param (
    [string]$DBHost,
    [string]$Database = "orcheflow",
    [string]$User = "orcheflow",
    [string]$DBPassword = $null,
    [string]$MigrationPath = "db\migrations\V001__initial_schema.sql"
)

Write-Host "🚀 OrcheFlowAI — Running Migrations on $DBHost..." -ForegroundColor Cyan

if ($DBPassword) {
    $env:PGPASSWORD = $DBPassword
}

# Run the SQL migration
psql -h $DBHost -U $User -d $Database -f $MigrationPath

if ($LASTEXITCODE -eq 0) {
    Write-OK "Migration successful."
} else {
    Write-Error "Migration failed with exit code $LASTEXITCODE"
}

# Cleanup env
$env:PGPASSWORD = $null
