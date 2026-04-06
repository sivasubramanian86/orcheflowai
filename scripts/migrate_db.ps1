# OrcheFlowAI — Database Migration Tool
# Environment: production or local-preview.

param (
    [string]$DBHost,
    [string]$Database = "orcheflow",
    [string]$User = "orcheflow",
    [SecureString]$DBPassword = $null,
    [string]$MigrationPath = "db\migrations\V*.sql"
)

Write-Host "🚀 OrcheFlowAI — Running Migrations on $DBHost..." -ForegroundColor Cyan

if ($DBPassword) {
    $Ptr = [System.Runtime.InteropServices.Marshal]::SecureStringToBSTR($DBPassword)
    try {
        $env:PGPASSWORD = [System.Runtime.InteropServices.Marshal]::PtrToStringAuto($Ptr)
    } finally {
        [System.Runtime.InteropServices.Marshal]::ZeroFreeBSTR($Ptr)
    }
}

$MigrationFiles = Get-ChildItem -Path "db\migrations\V*.sql" | Sort-Object Name
if ($MigrationFiles.Count -eq 0) {
    Write-Warning "⚠️ No migration files found."
} else {
    foreach ($file in $MigrationFiles) {
        Write-Host "📜 Applying $($file.Name)..." -ForegroundColor Gray
        psql -h $DBHost -U $User -d $Database -f $file.FullName
        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ Migration $($file.Name) failed."
            break
        }
    }
    Write-Host "✅ All migrations applied successfully." -ForegroundColor Green
}

$env:PGPASSWORD = $null
