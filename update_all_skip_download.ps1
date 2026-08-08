$ErrorActionPreference = "Stop"

$Root = Split-Path -Parent $PSCommandPath
$Python = Join-Path $Root ".venv\Scripts\python.exe"
$WslDistribution = "Ubuntu-24.04"

if (-not (Test-Path -LiteralPath $Python)) {
    Write-Host "Python venv not found: $Python" -ForegroundColor Red
    exit 1
}

function Initialize-WslPostgres {
    param([string]$Distribution)

    & wsl.exe -d $Distribution -u root -- systemctl start postgresql
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to start PostgreSQL in WSL distribution: $Distribution" -ForegroundColor Red
        exit $LASTEXITCODE
    }

    $AddressOutput = & wsl.exe -d $Distribution -- hostname -I
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to resolve the WSL address: $Distribution" -ForegroundColor Red
        exit $LASTEXITCODE
    }

    $WslAddress = (($AddressOutput -join " ") -split "\s+" | Where-Object {
        $_ -match "^(?:\d{1,3}\.){3}\d{1,3}$"
    } | Select-Object -First 1)
    if (-not $WslAddress) {
        Write-Host "No IPv4 address found for WSL distribution: $Distribution" -ForegroundColor Red
        exit 1
    }

    $env:POSTGRES_HOST = $WslAddress
    Write-Host "Using PostgreSQL in $Distribution at ${WslAddress}:5432"
}

function Start-WslKeepAlive {
    param([string]$Distribution)

    $Process = Start-Process -FilePath "wsl.exe" `
        -ArgumentList @("-d", $Distribution, "--", "sleep", "infinity") `
        -WindowStyle Hidden `
        -PassThru
    Start-Sleep -Seconds 1
    if ($Process.HasExited) {
        Write-Host "Failed to keep WSL distribution running: $Distribution" -ForegroundColor Red
        exit 1
    }
    return $Process
}

function Run-Step {
    param(
        [string]$Name,
        [string]$Script,
        [string[]]$Arguments = @()
    )

    & $Python (Join-Path $Root $Script) @Arguments
    if ($LASTEXITCODE -ne 0) {
        Write-Host "$Name failed, exit code: $LASTEXITCODE" -ForegroundColor Red
        exit $LASTEXITCODE
    }
}

$WslKeepAlive = Start-WslKeepAlive $WslDistribution
try {
    Initialize-WslPostgres $WslDistribution

    Run-Step "ETL (skip raw download)" "update_etl.py" @("--skip-raw-download")
    Run-Step "Factor update" "update_factors.py"
    Run-Step "Factor panel snapshot" "archived\简历展示页\build_factor_panel_snapshot.py"
    Run-Step "Tableau CSV" "archived\update_tableau_csv.py"
    Run-Step "Portfolio panel snapshot" "factor\build_portfolio_panel_snapshot.py"
    Run-Step "Style group backtest" "factor\build_style_group_backtest.py"
    Run-Step "Tableau display CSV" "build_tableau_display_csv.py"

    Write-Host "Pipeline completed (raw download skipped)." -ForegroundColor Green
}
finally {
    if ($null -ne $WslKeepAlive -and -not $WslKeepAlive.HasExited) {
        & wsl.exe -d $WslDistribution -u root -- systemctl stop postgresql
        Stop-Process -Id $WslKeepAlive.Id -ErrorAction SilentlyContinue
    }
}
