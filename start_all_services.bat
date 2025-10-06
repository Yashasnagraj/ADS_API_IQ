@echo off
echo ========================================
echo MarketingIQ Platform - Starting All Services
echo ========================================
echo.

REM Start SQLite API (Port 8004)
echo [1/3] Starting Data Warehouse API (Port 8004)...
start "Data API" cmd /k "python api_sqlite.py"
timeout /t 3 /nobreak >nul

REM Start Multi-Agent API (Port 8001)
echo [2/3] Starting Multi-Agent System (Port 8001)...
cd google-ads-multiagent
start "Agent API" cmd /k "python agent_api.py"
cd ..
timeout /t 3 /nobreak >nul

REM Start Chatbot API (Port 8002)
echo [3/3] Starting AI Chatbot API (Port 8002)...
start "Chatbot API" cmd /k "python chatbot_api.py"
timeout /t 2 /nobreak >nul

echo.
echo ========================================
echo All Services Started!
echo ========================================
echo.
echo Services Running:
echo   [Port 8004] Data Warehouse API
echo   [Port 8001] Multi-Agent System
echo   [Port 8002] AI Chatbot API
echo.
echo To start the React frontend:
echo   cd marketingiq-platform\web
echo   npm start
echo.
echo Press any key to exit (services will keep running)...
pause >nul
