@echo off
echo ========================================
echo   MarketingIQ Platform Startup
echo ========================================
echo.
echo Starting all services...
echo.

REM Start Data API (port 8000)
echo [1/3] Starting Data API on port 8000...
start "Data API" cmd /k "cd /d %~dp0api && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
timeout /t 3 /nobreak >nul

REM Start Agent API (port 8001)
echo [2/3] Starting Agent API on port 8001...
start "Agent API" cmd /k "cd /d %~dp0google-ads-multiagent && venv\Scripts\activate && python agent_api.py"
timeout /t 3 /nobreak >nul

REM Start Frontend (port 3001)
echo [3/3] Starting Frontend Dashboard on port 3001...
start "Frontend" cmd /k "cd /d %~dp0marketingiq-platform\web && npm start"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo   All services are starting...
echo ========================================
echo.
echo   Data API:     http://localhost:8000
echo   Agent API:    http://localhost:8001
echo   Dashboard:    http://localhost:3001
echo.
echo   Waiting 15 seconds for servers to start...
echo ========================================

timeout /t 15 /nobreak >nul

REM Open browser
echo Opening dashboard in browser...
start http://localhost:3001

echo.
echo Setup complete! Check the terminal windows for any errors.
echo Press any key to exit this window (services will keep running)...
pause >nul
