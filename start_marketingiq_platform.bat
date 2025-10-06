@echo off
title MarketingIQ Platform - All Services Launcher
color 0A

echo ========================================
echo MarketingIQ Platform Launcher
echo ========================================
echo.
echo This script will start:
echo   1. SQLite Data API (port 8004)
echo   2. ADK Chatbot API (port 8003)
echo   3. React Dashboard (port 3000)
echo.
echo Make sure you have:
echo   - Python 3.8+ installed
echo   - Node.js 16+ installed
echo   - All dependencies installed
echo.
pause

echo.
echo Starting services in new windows...
echo.

REM Start SQLite Data API
echo [1/3] Starting SQLite Data API on port 8004...
start "SQLite Data API - Port 8004" cmd /k "python api_sqlite.py"
timeout /t 3 /nobreak >nul

REM Start ADK Chatbot API
echo [2/3] Starting ADK Chatbot API on port 8003...
start "ADK Chatbot API - Port 8003" cmd /k "cd google-ads-multiagent\adk && python chatbot_api.py"
timeout /t 3 /nobreak >nul

REM Start React Dashboard
echo [3/3] Starting React Dashboard on port 3000...
start "React Dashboard - Port 3000" cmd /k "cd marketingiq-platform\web && npm start"
timeout /t 3 /nobreak >nul

echo.
echo ========================================
echo All services started!
echo ========================================
echo.
echo Service URLs:
echo   - Data API: http://localhost:8004
echo   - Chatbot API: http://localhost:8003
echo   - Dashboard: http://localhost:3000
echo.
echo Press any key to open the dashboard in your browser...
pause >nul

REM Open dashboard in default browser
start http://localhost:3000

echo.
echo Platform is running!
echo Close this window to keep all services running.
echo To stop services, close their individual windows.
echo.
pause
