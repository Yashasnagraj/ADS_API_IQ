@echo off
echo ========================================
echo   MarketingIQ Analytics Dashboard
echo ========================================
echo.
echo Starting the enhanced analytics dashboard...
echo.
echo Features:
echo   - Descriptive Analytics (What happened?)
echo   - Diagnostic Analytics (Why did it happen?)
echo   - Predictive Analytics (What will happen?)
echo   - Prescriptive Analytics (What should you do?)
echo.
echo ----------------------------------------

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH
    echo Please install Python 3.8+ from python.org
    pause
    exit /b 1
)

REM Check if required packages are installed
echo Checking dependencies...
pip show flask >nul 2>&1
if errorlevel 1 (
    echo Installing Flask...
    pip install flask flask-cors
)

pip show pandas >nul 2>&1
if errorlevel 1 (
    echo Installing pandas...
    pip install pandas numpy scikit-learn
)

echo.
echo ========================================
echo Starting MarketingIQ Dashboard Server...
echo ========================================
echo.
echo The dashboard will open at:
echo http://localhost:5000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Start the Flask application
python enhanced_dashboard_app.py

pause