@echo off
echo ============================================================
echo Starting ADK Multi-Agent System Web Interface
echo ============================================================
echo.

REM Check if API server needs to be started
echo [Step 1] Starting API Server on port 8003...
start /B cmd /c "cd /d C:\Users\yashr\Desktop\ADS_API && python api_sqlserver.py"
timeout /t 3 /nobreak > nul

REM Activate virtual environment if it exists
if exist ".venv\Scripts\activate.bat" (
    echo [Step 2] Activating virtual environment...
    call .venv\Scripts\activate.bat
) else (
    echo [Step 2] No virtual environment found, using global Python
)

echo.
echo [Step 3] Launching ADK Web Interface...
echo ============================================================
echo.
echo ADK Web Interface will open at: http://localhost:8000
echo API Documentation available at: http://localhost:8003/docs
echo.
echo Available agents:
echo   - GoogleAdsOrchestrator (Main)
echo   - DataAgent
echo   - InsightAgent
echo   - OptimizationAgent
echo   - ForecastingAgent
echo.
echo ============================================================
echo.

REM Run ADK web with the orchestrator
adk web orchestration_agent.agent:root_agent

pause