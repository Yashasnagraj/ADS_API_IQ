#!/bin/bash

echo "========================================"
echo "  MarketingIQ Platform Startup"
echo "========================================"
echo ""
echo "Starting all services..."
echo ""

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Start Data API (port 8000) in background
echo "[1/3] Starting Data API on port 8000..."
cd "$SCRIPT_DIR/api"
if [ -d "venv" ]; then
    source venv/bin/activate
    uvicorn app.main:app --reload --port 8000 > ../logs/data_api.log 2>&1 &
    DATA_API_PID=$!
    echo "Data API started with PID: $DATA_API_PID"
else
    echo "ERROR: Virtual environment not found in api/"
    echo "Please run: cd api && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

sleep 3

# Start Agent API (port 8001) in background
echo "[2/3] Starting Agent API on port 8001..."
cd "$SCRIPT_DIR/google-ads-multiagent"
if [ -d "venv" ]; then
    source venv/bin/activate
    python agent_api.py > ../logs/agent_api.log 2>&1 &
    AGENT_API_PID=$!
    echo "Agent API started with PID: $AGENT_API_PID"
else
    echo "ERROR: Virtual environment not found in google-ads-multiagent/"
    echo "Please run: cd google-ads-multiagent && python -m venv venv && source venv/bin/activate && pip install -r requirements.txt"
    exit 1
fi

sleep 3

# Start Frontend (port 3001) in background
echo "[3/3] Starting Frontend Dashboard on port 3001..."
cd "$SCRIPT_DIR/marketingiq-platform/web"
if [ -d "node_modules" ]; then
    npm start > ../../logs/frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "Frontend started with PID: $FRONTEND_PID"
else
    echo "ERROR: node_modules not found in marketingiq-platform/web/"
    echo "Please run: cd marketingiq-platform/web && npm install --legacy-peer-deps"
    exit 1
fi

echo ""
echo "========================================"
echo "  All services are starting..."
echo "========================================"
echo ""
echo "  Data API:     http://localhost:8000"
echo "  Agent API:    http://localhost:8001"
echo "  Dashboard:    http://localhost:3001"
echo ""
echo "  Logs saved to: logs/"
echo ""
echo "  PIDs:"
echo "    Data API:  $DATA_API_PID"
echo "    Agent API: $AGENT_API_PID"
echo "    Frontend:  $FRONTEND_PID"
echo ""
echo "  Waiting 15 seconds for servers to start..."
echo "========================================"

sleep 15

# Open browser (works on macOS and most Linux)
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    open http://localhost:3001
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v xdg-open > /dev/null; then
        xdg-open http://localhost:3001
    elif command -v gnome-open > /dev/null; then
        gnome-open http://localhost:3001
    fi
fi

echo ""
echo "Setup complete!"
echo ""
echo "To stop all services, run: ./stop_all.sh"
echo "Or press Ctrl+C to stop this script (services will keep running)"
echo ""

# Save PIDs to file for stop script
echo "$DATA_API_PID" > "$SCRIPT_DIR/.pids"
echo "$AGENT_API_PID" >> "$SCRIPT_DIR/.pids"
echo "$FRONTEND_PID" >> "$SCRIPT_DIR/.pids"

# Wait for user interrupt
wait
