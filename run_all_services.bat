@echo off
title MarketingIQ Platform - Unified Service Launcher
color 0A

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║        MarketingIQ Platform - Unified Service Launcher        ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo This will start ALL required services:
echo.
echo   [1] SQLite Data API          → Port 8004
echo   [2] ADK Chatbot API          → Port 8003
echo   [3] React Dashboard          → Port 3000
echo.
echo ────────────────────────────────────────────────────────────────
echo  Prerequisites Check:
echo ────────────────────────────────────────────────────────────────
echo   ✓ Python 3.8+ installed
echo   ✓ Node.js 16+ installed
echo   ✓ pip install -r requirements.txt (Backend)
echo   ✓ npm install (Frontend)
echo   ✓ Google Ads data in google_ads_data.db
echo.
pause
echo.

REM ============================================================================
REM Check if ports are already in use
REM ============================================================================
echo [INFO] Checking if ports are available...
echo.

netstat -ano | findstr ":3000" >nul
if %errorlevel%==0 (
    echo [WARNING] Port 3000 is already in use!
    echo           Kill the process or the new service may fail.
    echo.
)

netstat -ano | findstr ":8003" >nul
if %errorlevel%==0 (
    echo [WARNING] Port 8003 is already in use!
    echo           Kill the process or the new service may fail.
    echo.
)

netstat -ano | findstr ":8004" >nul
if %errorlevel%==0 (
    echo [WARNING] Port 8004 is already in use!
    echo           Kill the process or the new service may fail.
    echo.
)

echo.
echo ════════════════════════════════════════════════════════════════
echo  Starting Services...
echo ════════════════════════════════════════════════════════════════
echo.

REM ============================================================================
REM SERVICE 1: SQLite Data API (Port 8004)
REM ============================================================================
echo [1/3] Starting SQLite Data API on port 8004...
echo       Location: api_sqlite.py
echo.

start "🗄️  SQLite Data API - Port 8004" cmd /k "echo Starting SQLite Data API... && echo. && python api_sqlite.py"

timeout /t 5 /nobreak >nul
echo       ✓ SQLite Data API started
echo.

REM ============================================================================
REM SERVICE 2: ADK Chatbot API (Port 8003)
REM ============================================================================
echo [2/3] Starting ADK Chatbot API on port 8003...
echo       Location: google-ads-multiagent\adk\chatbot_api.py
echo.

start "💬 ADK Chatbot API - Port 8003" cmd /k "echo Starting ADK Chatbot API... && echo. && cd google-ads-multiagent\adk && python chatbot_api.py"

timeout /t 5 /nobreak >nul
echo       ✓ ADK Chatbot API started
echo.

REM ============================================================================
REM SERVICE 3: React Dashboard (Port 3000)
REM ============================================================================
echo [3/3] Starting React Dashboard on port 3000...
echo       Location: marketingiq-platform\web
echo.

start "⚛️  React Dashboard - Port 3000" cmd /k "echo Starting React Dashboard... && echo. && cd marketingiq-platform\web && npm start"

timeout /t 8 /nobreak >nul
echo       ✓ React Dashboard starting (may take 30-60 seconds)
echo.

echo.
echo ════════════════════════════════════════════════════════════════
echo  All Services Started Successfully!
echo ════════════════════════════════════════════════════════════════
echo.
echo  📊 Service Dashboard:
echo  ──────────────────────────────────────────────────────────────
echo   SQLite Data API      http://localhost:8004
echo   ADK Chatbot API      http://localhost:8003
echo   React Dashboard      http://localhost:3000
echo  ──────────────────────────────────────────────────────────────
echo.
echo  🧪 Quick Tests:
echo  ──────────────────────────────────────────────────────────────
echo   Data API Health:     curl http://localhost:8004/health
echo   Chatbot Health:      curl http://localhost:8003/health
echo   Test Chatbot:        cd google-ads-multiagent\adk ^&^& python test_chatbot.py
echo  ──────────────────────────────────────────────────────────────
echo.
echo  💡 Usage:
echo  ──────────────────────────────────────────────────────────────
echo   1. Wait for React to compile (30-60 seconds)
echo   2. Browser will auto-open to http://localhost:3000
echo   3. Click the chat icon (💬) in bottom-right corner
echo   4. Try: "Show top performing campaigns"
echo  ──────────────────────────────────────────────────────────────
echo.
echo  ⚠️  To Stop Services:
echo  ──────────────────────────────────────────────────────────────
echo   Close each service window individually, OR
echo   Run: taskkill /F /FI "WINDOWTITLE eq *Port*"
echo  ──────────────────────────────────────────────────────────────
echo.

REM Wait for React to compile then open browser
echo [INFO] Waiting for React to compile...
timeout /t 30 /nobreak >nul

echo [INFO] Opening dashboard in browser...
start http://localhost:3000

echo.
echo ════════════════════════════════════════════════════════════════
echo  Platform is Running!
echo ════════════════════════════════════════════════════════════════
echo.
echo  This window can be closed - services run in separate windows.
echo  Check the individual service windows for logs and errors.
echo.
echo  Press any key to exit this launcher window...
pause >nul
