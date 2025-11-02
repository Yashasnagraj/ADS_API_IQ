@echo off
echo ========================================
echo Marketing IQ Platform - Starting All Services
echo ========================================
echo.
echo This will start:
echo 1. Backend API (port 8000)
echo 2. ADK Chatbot API (port 8003)
echo.
echo Press Ctrl+C to stop all services
echo ========================================
echo.

REM Start Backend API in new window
echo [1/2] Starting Backend API on port 8000...
start "Marketing IQ - Backend API" cmd /k "cd /d D:\ADS_API\api && uvicorn app.main:app --reload --port 8000"
timeout /t 3 >nul

REM Start ADK Chatbot API in new window
echo [2/2] Starting ADK Chatbot API on port 8003...
start "Marketing IQ - Chatbot API" cmd /k "cd /d D:\ADS_API\google-ads-multiagent\adk && python chatbot_api.py"
timeout /t 2 >nul

echo.
echo ========================================
echo All Services Started!
echo ========================================
echo.
echo Backend API:     http://localhost:8000/docs
echo Chatbot API:     http://localhost:8003/health
echo Frontend (Vite): http://localhost:5173
echo.
echo Two new windows opened:
echo - Backend API (port 8000)
echo - Chatbot API (port 8003)
echo.
echo To stop: Close both terminal windows
echo ========================================
echo.
pause
