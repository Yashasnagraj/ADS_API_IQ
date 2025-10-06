@echo off
title MarketingIQ Platform - Stop All Services
color 0C

echo.
echo ╔════════════════════════════════════════════════════════════════╗
echo ║          MarketingIQ Platform - Stop All Services             ║
echo ╚════════════════════════════════════════════════════════════════╝
echo.
echo This will stop ALL running services:
echo.
echo   [1] SQLite Data API          (Port 8004)
echo   [2] ADK Chatbot API          (Port 8003)
echo   [3] React Dashboard          (Port 3000)
echo.
echo ⚠️  WARNING: This will forcefully terminate all processes!
echo.
pause
echo.

echo ════════════════════════════════════════════════════════════════
echo  Stopping Services...
echo ════════════════════════════════════════════════════════════════
echo.

REM Stop processes by port number
echo [1/3] Stopping SQLite Data API (Port 8004)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8004 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo       ✓ Stopped process on port 8004
    )
)
echo.

echo [2/3] Stopping ADK Chatbot API (Port 8003)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8003 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo       ✓ Stopped process on port 8003
    )
)
echo.

echo [3/3] Stopping React Dashboard (Port 3000)...
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000 ^| findstr LISTENING') do (
    taskkill /F /PID %%a >nul 2>&1
    if !errorlevel! equ 0 (
        echo       ✓ Stopped process on port 3000
    )
)
echo.

REM Also kill by window title (backup method)
echo [INFO] Cleaning up service windows...
taskkill /F /FI "WINDOWTITLE eq *Port 8004*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *Port 8003*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *Port 3000*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *SQLite Data API*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *ADK Chatbot API*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq *React Dashboard*" >nul 2>&1
echo       ✓ Service windows closed
echo.

echo ════════════════════════════════════════════════════════════════
echo  All Services Stopped!
echo ════════════════════════════════════════════════════════════════
echo.
echo  To verify all services are stopped, run:
echo    netstat -ano ^| findstr ":8004 :8003 :3000"
echo.
echo  To restart services, run:
echo    run_all_services.bat
echo.
pause
