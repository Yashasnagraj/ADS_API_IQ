#!/bin/bash
# Start MarketingIQ Backend API

echo "Starting MarketingIQ Backend API..."
echo "Backend will be available at: http://localhost:8000"
echo "API Docs: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"
echo ""

cd api
source venv/bin/activate
python -m uvicorn app.main:app --reload --port 8000
