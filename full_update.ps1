function Run-Step($Name, $Script) {
    python $Script
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$Name failed, exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

Run-Step "ETL" "update_etl.py"
Run-Step "Factor update" "update_factors.py"

Write-Host "Pipeline completed." -ForegroundColor Green