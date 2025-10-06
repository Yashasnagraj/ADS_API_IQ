@echo off
REM ============================================================================
REM MarketingIQ Platform - Simple Stop Script
REM Double-click to stop all services
REM ============================================================================

title Stopping MarketingIQ Platform...
color 0C

echo.
echo  ███████╗████████╗ ██████╗ ██████╗
echo  ██╔════╝╚══██╔══╝██╔═══██╗██╔══██╗
echo  ███████╗   ██║   ██║   ██║██████╔╝
echo  ╚════██║   ██║   ██║   ██║██╔═══╝
echo  ███████║   ██║   ╚██████╔╝██║
echo  ╚══════╝   ╚═╝    ╚═════╝ ╚═╝
echo.
echo  🛑 Stopping all MarketingIQ services...
echo.

REM Stop by port
for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8004') do taskkill /F /PID %%a >nul 2>&1
echo  [■□□] Data API stopped
timeout /t 1 /nobreak >nul

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :8003') do taskkill /F /PID %%a >nul 2>&1
echo  [■■□] Chatbot API stopped
timeout /t 1 /nobreak >nul

for /f "tokens=5" %%a in ('netstat -ano ^| findstr :3000') do taskkill /F /PID %%a >nul 2>&1
echo  [■■■] Dashboard stopped
timeout /t 1 /nobreak >nul

REM Close service windows
taskkill /F /FI "WINDOWTITLE eq Data API*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq Chatbot API*" >nul 2>&1
taskkill /F /FI "WINDOWTITLE eq React Dashboard*" >nul 2>&1

echo.
echo  ✅ All services stopped!
echo.
echo  To restart, run: START.bat
echo.
timeout /t 3 /nobreak >nul
exit
