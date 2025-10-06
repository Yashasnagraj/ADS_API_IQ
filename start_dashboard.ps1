# MarketingIQ Dashboard Launcher PowerShell Script

Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "                    MARKETINGIQ DASHBOARD LAUNCHER                     " -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Function to check if a command exists
function Test-Command {
    param($Command)
    try {
        Get-Command $Command -ErrorAction Stop | Out-Null
        return $true
    }
    catch {
        return $false
    }
}

# Check Python
Write-Host "[1/5] Checking Python installation..." -ForegroundColor Green
if (Test-Command python) {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} else {
    Write-Host "✗ Python not found! Please install Python first." -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

# Check and install dependencies
Write-Host ""
Write-Host "[2/5] Checking dependencies..." -ForegroundColor Green
$requirements = @(
    "flask",
    "flask-cors",
    "pandas",
    "numpy",
    "scikit-learn",
    "scipy",
    "tabulate",
    "sqlite3"
)

foreach ($package in $requirements) {
    $installed = pip show $package 2>&1 | Select-String "Name:"
    if ($installed) {
        Write-Host "✓ $package is installed" -ForegroundColor Gray
    } else {
        Write-Host "Installing $package..." -ForegroundColor Yellow
        pip install $package -q
    }
}

# Check database
Write-Host ""
Write-Host "[3/5] Checking database..." -ForegroundColor Green
if (Test-Path "google_ads_data.db") {
    $fileInfo = Get-Item "google_ads_data.db"
    $sizeMB = [math]::Round($fileInfo.Length / 1MB, 2)
    Write-Host "✓ Database found: google_ads_data.db ($sizeMB MB)" -ForegroundColor Green

    # Quick data check
    $tableCount = python -c "import sqlite3; conn=sqlite3.connect('google_ads_data.db'); cursor=conn.cursor(); cursor.execute(""SELECT COUNT(*) FROM sqlite_master WHERE type='table'""); print(cursor.fetchone()[0]); conn.close()" 2>$null
    if ($tableCount) {
        Write-Host "  Tables in database: $tableCount" -ForegroundColor Gray
    }
} else {
    Write-Host "⚠ Database not found! Run ETL pipeline first:" -ForegroundColor Yellow
    Write-Host "  python google_ads_etl_pipeline.py" -ForegroundColor Yellow
}

# Check KPI algorithms module
Write-Host ""
Write-Host "[4/5] Checking KPI algorithms module..." -ForegroundColor Green
if (Test-Path "kpi_algorithms.py") {
    Write-Host "✓ KPI algorithms module found" -ForegroundColor Green
} else {
    Write-Host "⚠ KPI algorithms module not found!" -ForegroundColor Yellow
}

# Start the server
Write-Host ""
Write-Host "[5/5] Starting Enhanced Dashboard Server..." -ForegroundColor Green
Write-Host ""
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host "Dashboard Features:" -ForegroundColor Yellow
Write-Host "  • Customer Filtering - Filter all metrics by customer" -ForegroundColor White
Write-Host "  • Real-time Metrics - Live data from last 24 hours" -ForegroundColor White
Write-Host "  • Advanced KPIs - ROAS, CLV, CAC calculations" -ForegroundColor White
Write-Host "  • Anomaly Detection - Statistical outlier detection" -ForegroundColor White
Write-Host "  • Trend Analysis - 90-day trends with forecasting" -ForegroundColor White
Write-Host ""
Write-Host "Dashboard URL: " -NoNewline -ForegroundColor Yellow
Write-Host "http://localhost:5000" -ForegroundColor Cyan
Write-Host ""
Write-Host "API Endpoints:" -ForegroundColor Yellow
Write-Host "  http://localhost:5000/api/customers              - List customers" -ForegroundColor Gray
Write-Host "  http://localhost:5000/api/realtime/metrics       - Real-time metrics" -ForegroundColor Gray
Write-Host "  http://localhost:5000/api/kpi/roas               - ROAS analysis" -ForegroundColor Gray
Write-Host "  http://localhost:5000/api/kpi/clv                - Customer LTV" -ForegroundColor Gray
Write-Host "  http://localhost:5000/api/kpi/cac                - Acquisition cost" -ForegroundColor Gray
Write-Host "  http://localhost:5000/api/kpi/anomalies          - Anomaly detection" -ForegroundColor Gray
Write-Host "  http://localhost:5000/api/kpi/trends             - Trend analysis" -ForegroundColor Gray
Write-Host ""
Write-Host "Press Ctrl+C to stop the server" -ForegroundColor Yellow
Write-Host "========================================================================" -ForegroundColor Cyan
Write-Host ""

# Start the server
python enhanced_dashboard_app.py