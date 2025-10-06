#!/usr/bin/env python3
"""
Start both API server and ADK server for the multi-agent system
"""

import subprocess
import time
import sys
import os
from pathlib import Path

def start_servers():
    """Start both API and ADK servers"""

    # Get the root directory (two levels up from this script)
    script_dir = Path(__file__).parent
    root_dir = script_dir.parent.parent

    print("=" * 60)
    print("Starting MarketingIQ Multi-Agent System")
    print("=" * 60)
    print()

    try:
        # Start API Server
        print("[1/2] Starting API Server on port 8003...")
        api_process = subprocess.Popen(
            [sys.executable, "api_sqlserver.py"],
            cwd=str(root_dir),
            creationflags=subprocess.CREATE_NEW_CONSOLE if sys.platform == "win32" else 0
        )
        print("    ✓ API Server started (PID: {})".format(api_process.pid))

        # Wait for API server to initialize
        print("    Waiting for API server to initialize...")
        time.sleep(5)

        # Start ADK Server
        print("\n[2/2] Starting ADK Server on port 8000...")
        adk_process = subprocess.Popen(
            [sys.executable, "-m", "adk", "run", "orchestration_agent.agent:root_agent", "--port", "8000"],
            cwd=str(script_dir)
        )
        print("    ✓ ADK Server started (PID: {})".format(adk_process.pid))

        print("\n" + "=" * 60)
        print("Both servers are now running!")
        print("-" * 60)
        print("  • API Server: http://localhost:8003")
        print("  • API Docs:   http://localhost:8003/docs")
        print("  • ADK Server: http://localhost:8000")
        print("=" * 60)
        print("\nPress Ctrl+C to stop both servers...")

        # Keep the script running
        while True:
            time.sleep(1)

    except KeyboardInterrupt:
        print("\n\nShutting down servers...")
        api_process.terminate()
        adk_process.terminate()
        print("Servers stopped.")

    except Exception as e:
        print(f"Error starting servers: {e}")
        sys.exit(1)

if __name__ == "__main__":
    start_servers()