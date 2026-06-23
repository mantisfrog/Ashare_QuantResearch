$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSCommandPath
$Python = Join-Path $Root ".venv\Scripts\python.exe"

if (-not (Test-Path -LiteralPath $Python)) {
    Write-Host "Python venv not found: $Python" -ForegroundColor Red
    exit 1
}

function Run-Step($Name, $Script) {
    & $Python (Join-Path $Root $Script)
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$Name failed, exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Run-Step "ETL" "update_etl.py"
Run-Step "Factor update" "update_factors.py"

Write-Host "Pipeline completed." -ForegroundColor Green
