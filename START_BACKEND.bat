@echo off
echo ========================================
echo Starting MarketingIQ Backend API
echo ========================================
echo.
cd /d D:\ADS_API\api
echo Starting server on http://localhost:8000
echo Press Ctrl+C to stop
echo.
uvicorn app.main:app --reload --port 8000
pause
