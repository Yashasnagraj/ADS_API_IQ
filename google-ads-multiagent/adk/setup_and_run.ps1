# PowerShell script to setup and run ADK with your orchestrator

Write-Host "Setting up ADK Multi-Agent System..." -ForegroundColor Green
Write-Host "=" * 60

# Check if venv exists, if not create it
if (!(Test-Path ".venv")) {
    Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
} else {
    Write-Host "[1/4] Virtual environment already exists" -ForegroundColor Cyan
}

# Activate virtual environment
Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

# Install/upgrade ADK if needed
Write-Host "[3/4] Checking ADK installation..." -ForegroundColor Yellow
pip install -q google-genai google-generativeai

# Set API key if not already set
if (!$env:GOOGLE_API_KEY) {
    Write-Host "Please set your GOOGLE_API_KEY environment variable" -ForegroundColor Red
    $apiKey = Read-Host "Enter your Google API Key"
    $env:GOOGLE_API_KEY = $apiKey
}

Write-Host "[4/4] Starting servers..." -ForegroundColor Yellow

# Start API server in background
Write-Host "Starting API server on port 8003..." -ForegroundColor Cyan
$apiJob = Start-Job -ScriptBlock {
    Set-Location "C:\Users\yashr\Desktop\ADS_API"
    python api_sqlserver.py
}

# Wait for API server to start
Start-Sleep -Seconds 3

# Start ADK web interface with your orchestrator
Write-Host "Starting ADK web interface..." -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host "ADK Web Interface will open at: http://localhost:8000" -ForegroundColor Green
Write-Host "API Server running at: http://localhost:8003" -ForegroundColor Green
Write-Host "=" * 60

# Run ADK web with your orchestrator
adk web orchestration_agent.agent:root_agent

# Cleanup when done
Write-Host "`nShutting down servers..." -ForegroundColor Yellow
Stop-Job $apiJob
Remove-Job $apiJob