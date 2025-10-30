#!/bin/bash

echo "========================================"
echo "  Stopping MarketingIQ Platform"
echo "========================================"
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Check if PID file exists
if [ -f "$SCRIPT_DIR/.pids" ]; then
    echo "Stopping services from PID file..."
    while read pid; do
        if ps -p $pid > /dev/null 2>&1; then
            echo "Killing process $pid..."
            kill $pid
        else
            echo "Process $pid not found (already stopped)"
        fi
    done < "$SCRIPT_DIR/.pids"

    rm "$SCRIPT_DIR/.pids"
    echo ""
    echo "All services stopped."
else
    echo "No PID file found. Stopping by port..."

    # Kill processes by port
    for port in 8000 8001 3001; do
        pid=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$pid" ]; then
            echo "Killing process on port $port (PID: $pid)..."
            kill $pid 2>/dev/null
        else
            echo "No process found on port $port"
        fi
    done

    echo ""
    echo "Done."
fi

echo "========================================"
