@echo off
echo Starting ADK Chatbot API...
echo.
echo This will start the chatbot API on port 8003
echo Make sure you have the following running:
echo   - SQLite Data API on port 8004
echo   - Google ADK dependencies installed
echo.
pause

cd /d "%~dp0"
python chatbot_api.py
