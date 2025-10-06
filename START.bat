@echo off
REM ============================================================================
REM MarketingIQ Platform - Simple Launcher
REM Just double-click this file to start everything!
REM ============================================================================

title Starting MarketingIQ Platform...
color 0B

echo.
echo  ███╗   ███╗ █████╗ ██████╗ ██╗  ██╗███████╗████████╗██╗███╗   ██╗ ██████╗
echo  ████╗ ████║██╔══██╗██╔══██╗██║ ██╔╝██╔════╝╚══██╔══╝██║████╗  ██║██╔════╝
echo  ██╔████╔██║███████║██████╔╝█████╔╝ █████╗     ██║   ██║██╔██╗ ██║██║  ███╗
echo  ██║╚██╔╝██║██╔══██║██╔══██╗██╔═██╗ ██╔══╝     ██║   ██║██║╚██╗██║██║   ██║
echo  ██║ ╚═╝ ██║██║  ██║██║  ██║██║  ██╗███████╗   ██║   ██║██║ ╚████║╚██████╔╝
echo  ╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚══════╝   ╚═╝   ╚═╝╚═╝  ╚═══╝ ╚═════╝
echo                                 IQ Platform
echo.
echo  🚀 Starting all services...
echo.

REM Start services
echo  [■□□] Starting backend services...
start "Data API" /MIN cmd /k "python api_sqlite.py"
timeout /t 3 /nobreak >nul

echo  [■■□] Starting chatbot...
start "Chatbot API" /MIN cmd /k "cd google-ads-multiagent\adk && python chatbot_api.py"
timeout /t 3 /nobreak >nul

echo  [■■■] Starting dashboard...
start "React Dashboard" cmd /k "cd marketingiq-platform\web && npm start"
timeout /t 5 /nobreak >nul

echo.
echo  ✅ All services started!
echo.
echo  📍 Dashboard will open at: http://localhost:3000
echo  💬 Chatbot available in bottom-right corner
echo.
echo  ⏳ Please wait 30-60 seconds for React to compile...
echo.

REM Wait for React to be ready
timeout /t 35 /nobreak >nul

REM Open browser
start http://localhost:3000

echo  🌐 Browser opened!
echo.
echo  ═══════════════════════════════════════════════════════════
echo   Platform is ready!
echo   Close this window anytime - services continue running.
echo  ═══════════════════════════════════════════════════════════
echo.
timeout /t 3 /nobreak >nul
exit
