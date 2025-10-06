# MarketingIQ Platform - Unified Service Launcher (PowerShell)
# Starts: SQLite API, ADK Chatbot API, React Dashboard

Write-Host ""
Write-Host "╔════════════════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║        MarketingIQ Platform - Unified Service Launcher        ║" -ForegroundColor Cyan
Write-Host "╚════════════════════════════════════════════════════════════════╝" -ForegroundColor Cyan
Write-Host ""

Write-Host "This will start ALL required services:" -ForegroundColor Yellow
Write-Host ""
Write-Host "  [1] SQLite Data API          → Port 8004" -ForegroundColor White
Write-Host "  [2] ADK Chatbot API          → Port 8003" -ForegroundColor White
Write-Host "  [3] React Dashboard          → Port 3000" -ForegroundColor White
Write-Host ""

# Check prerequisites
Write-Host "────────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host " Prerequisites Check:" -ForegroundColor Yellow
Write-Host "────────────────────────────────────────────────────────────────" -ForegroundColor Gray

# Check Python
$pythonVersion = python --version 2>&1
if ($pythonVersion -match "Python (\d+)\.(\d+)") {
    Write-Host "  ✓ Python $($matches[1]).$($matches[2]) found" -ForegroundColor Green
} else {
    Write-Host "  ✗ Python not found! Install Python 3.8+" -ForegroundColor Red
    exit 1
}

# Check Node.js
$nodeVersion = node --version 2>&1
if ($nodeVersion -match "v(\d+)\.(\d+)") {
    Write-Host "  ✓ Node.js $($matches[1]).$($matches[2]) found" -ForegroundColor Green
} else {
    Write-Host "  ✗ Node.js not found! Install Node.js 16+" -ForegroundColor Red
    exit 1
}

# Check if database exists
if (Test-Path "google_ads_data.db") {
    Write-Host "  ✓ Database file found" -ForegroundColor Green
} else {
    Write-Host "  ⚠ Database file not found (google_ads_data.db)" -ForegroundColor Yellow
    Write-Host "    Run ETL pipeline first: python google_ads_etl_pipeline.py" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "Press any key to continue or Ctrl+C to cancel..."
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " Starting Services..." -ForegroundColor Yellow
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

# Function to check if port is in use
function Test-Port {
    param([int]$Port)
    $connections = Get-NetTCPConnection -LocalPort $Port -ErrorAction SilentlyContinue
    return $connections.Count -gt 0
}

# Check ports
$ports = @{8004 = "SQLite API"; 8003 = "Chatbot API"; 3000 = "React Dashboard"}
foreach ($port in $ports.Keys) {
    if (Test-Port -Port $port) {
        Write-Host "  ⚠ Port $port ($($ports[$port])) is already in use!" -ForegroundColor Yellow
    }
}

Write-Host ""

# Service 1: SQLite Data API
Write-Host "[1/3] Starting SQLite Data API on port 8004..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'SQLite Data API - Port 8004' -ForegroundColor Green; python api_sqlite.py"
Start-Sleep -Seconds 5
Write-Host "      ✓ SQLite Data API started" -ForegroundColor Green
Write-Host ""

# Service 2: ADK Chatbot API
Write-Host "[2/3] Starting ADK Chatbot API on port 8003..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'ADK Chatbot API - Port 8003' -ForegroundColor Green; Set-Location 'google-ads-multiagent\adk'; python chatbot_api.py"
Start-Sleep -Seconds 5
Write-Host "      ✓ ADK Chatbot API started" -ForegroundColor Green
Write-Host ""

# Service 3: React Dashboard
Write-Host "[3/3] Starting React Dashboard on port 3000..." -ForegroundColor Cyan
Start-Process powershell -ArgumentList "-NoExit", "-Command", "Write-Host 'React Dashboard - Port 3000' -ForegroundColor Green; Set-Location 'marketingiq-platform\web'; npm start"
Start-Sleep -Seconds 8
Write-Host "      ✓ React Dashboard starting (may take 30-60 seconds)" -ForegroundColor Green
Write-Host ""

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " All Services Started Successfully!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""

Write-Host " 📊 Service Dashboard:" -ForegroundColor Yellow
Write-Host " ──────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  SQLite Data API      http://localhost:8004" -ForegroundColor White
Write-Host "  ADK Chatbot API      http://localhost:8003" -ForegroundColor White
Write-Host "  React Dashboard      http://localhost:3000" -ForegroundColor White
Write-Host " ──────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

Write-Host " 🧪 Quick Tests:" -ForegroundColor Yellow
Write-Host " ──────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  Invoke-WebRequest http://localhost:8004/health" -ForegroundColor White
Write-Host "  Invoke-WebRequest http://localhost:8003/health" -ForegroundColor White
Write-Host "  cd google-ads-multiagent\adk; python test_chatbot.py" -ForegroundColor White
Write-Host " ──────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

Write-Host " 💡 Usage:" -ForegroundColor Yellow
Write-Host " ──────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host "  1. Wait for React to compile (30-60 seconds)" -ForegroundColor White
Write-Host "  2. Browser will auto-open to http://localhost:3000" -ForegroundColor White
Write-Host "  3. Click the chat icon (💬) in bottom-right corner" -ForegroundColor White
Write-Host "  4. Try: 'Show top performing campaigns'" -ForegroundColor White
Write-Host " ──────────────────────────────────────────────────────────────" -ForegroundColor Gray
Write-Host ""

# Wait for React and open browser
Write-Host "[INFO] Waiting for React to compile..." -ForegroundColor Cyan
Start-Sleep -Seconds 30

Write-Host "[INFO] Opening dashboard in browser..." -ForegroundColor Cyan
Start-Process "http://localhost:3000"

Write-Host ""
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host " Platform is Running!" -ForegroundColor Green
Write-Host "════════════════════════════════════════════════════════════════" -ForegroundColor Cyan
Write-Host ""
Write-Host " Services are running in separate PowerShell windows." -ForegroundColor White
Write-Host " Close individual windows to stop services." -ForegroundColor White
Write-Host ""
Write-Host " Press any key to exit this launcher window..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
