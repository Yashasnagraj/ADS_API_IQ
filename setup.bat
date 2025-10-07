@echo off
REM MarketingIQ Platform - Windows Setup Script
REM Run this to set up the entire platform

echo ========================================
echo  MarketingIQ Platform Setup
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Python is not installed!
    echo Please install Python 3.11+ from https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Check if Node.js is installed
node --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERROR: Node.js is not installed!
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

echo [1/5] Setting up Python virtual environment...
cd api
if not exist venv (
    python -m venv venv
)
call venv\Scripts\activate.bat

echo.
echo [2/5] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [3/5] Checking .env configuration...
if not exist .env (
    echo WARNING: .env file not found!
    echo Please create api/.env with your Google Ads credentials.
    echo See api/.env.example for template.
    copy .env.example .env
    echo.
    echo Edit api/.env now and press any key to continue...
    pause
)

echo.
echo [4/5] Installing frontend dependencies...
cd ..\marketingiq-platform\web
call npm install --legacy-peer-deps

echo.
echo [5/5] Setup complete!
echo.
echo ========================================
echo  Next Steps:
echo ========================================
echo.
echo 1. Edit api/.env with your Google Ads API credentials
echo 2. Run the ETL pipeline: python etl_pipeline.py
echo 3. Start backend: cd api ^&^& python -m uvicorn app.main:app --reload
echo 4. Start frontend: cd marketingiq-platform/web ^&^& npm start
echo.
echo Or use the start scripts:
echo   - start-backend.bat
echo   - start-frontend.bat
echo.
pause
