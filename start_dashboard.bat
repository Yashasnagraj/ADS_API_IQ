@echo off
echo ========================================================================
echo                    MARKETINGIQ DASHBOARD LAUNCHER
echo ========================================================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python and try again
    pause
    exit /b 1
)

echo [1/4] Checking Python environment...
python --version

echo.
echo [2/4] Installing/Updating dependencies...
pip install flask flask-cors flask-socketio pandas numpy scikit-learn scipy tabulate -q 2>nul
if %errorlevel% neq 0 (
    echo Warning: Some dependencies might not be installed
)

echo.
echo [3/4] Checking database...
if exist google_ads_data.db (
    echo Database found: google_ads_data.db
) else (
    echo WARNING: Database not found! Please run ETL pipeline first.
)

echo.
echo [4/4] Starting Enhanced Dashboard Server...
echo.
echo ========================================================================
echo Dashboard will be available at:
echo.
echo   http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================================================
echo.

REM Start the enhanced dashboard with KPI algorithms
python enhanced_dashboard_app.py

pause