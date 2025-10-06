@echo off
echo Starting MarketingIQ Services for ADK...
echo.

REM Start the main API server (if not already running)
echo Checking if API server is running...
curl -s http://localhost:8000/health >nul 2>&1
if %errorlevel% neq 0 (
    echo Starting API server on port 8000...
    cd ..\..\
    start "MarketingIQ API" cmd /c "python api_sqlserver.py"
    timeout /t 5 /nobreak >nul
) else (
    echo API server already running on port 8000
)

REM Start the ADK server
echo.
echo Starting ADK server...
cd %~dp0
echo Current directory: %cd%
echo.

REM Check Python and ADK installation
python -c "from google.adk import run; print('ADK installed successfully')" 2>nul
if %errorlevel% neq 0 (
    echo ERROR: ADK not installed properly
    echo Please run: pip install google-ads-api google-adk
    pause
    exit /b 1
)

echo Starting ADK with orchestration agent...
google-adk run

pause