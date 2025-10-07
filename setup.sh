#!/bin/bash
# MarketingIQ Platform - Mac/Linux Setup Script
# Run this to set up the entire platform

echo "========================================"
echo " MarketingIQ Platform Setup"
echo "========================================"
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python is not installed!"
    echo "Please install Python 3.11+ from https://www.python.org/downloads/"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "ERROR: Node.js is not installed!"
    echo "Please install Node.js 18+ from https://nodejs.org/"
    exit 1
fi

echo "[1/5] Setting up Python virtual environment..."
cd api
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate

echo ""
echo "[2/5] Installing Python dependencies..."
pip install -r requirements.txt

echo ""
echo "[3/5] Checking .env configuration..."
if [ ! -f ".env" ]; then
    echo "WARNING: .env file not found!"
    echo "Please create api/.env with your Google Ads credentials."
    echo "See api/.env.example for template."
    cp .env.example .env
    echo ""
    echo "Edit api/.env now and press Enter to continue..."
    read
fi

echo ""
echo "[4/5] Installing frontend dependencies..."
cd ../marketingiq-platform/web
npm install --legacy-peer-deps

echo ""
echo "[5/5] Setup complete!"
echo ""
echo "========================================"
echo " Next Steps:"
echo "========================================"
echo ""
echo "1. Edit api/.env with your Google Ads API credentials"
echo "2. Run the ETL pipeline: python etl_pipeline.py"
echo "3. Start backend: cd api && python -m uvicorn app.main:app --reload"
echo "4. Start frontend: cd marketingiq-platform/web && npm start"
echo ""
echo "Or use the start scripts:"
echo "  - ./start-backend.sh"
echo "  - ./start-frontend.sh"
echo ""
