@echo off
echo Starting MarketingIQ Multi-Agent System...
echo =========================================
echo.

REM Start the API server on port 8003
echo [1/2] Starting API Server (port 8003)...
start cmd /k "cd /d %~dp0\..\..\ && python api_sqlserver.py"
timeout /t 5 /nobreak > nul

REM Start the ADK server on port 8000
echo [2/2] Starting ADK Server (port 8000)...
cd /d %~dp0
python -m adk run orchestration_agent.agent:root_agent --port 8000

echo.
echo Both servers are running!
echo - API Server: http://localhost:8003
echo - ADK Server: http://localhost:8000
echo.
echo Press any key to stop the servers...
pause > nul