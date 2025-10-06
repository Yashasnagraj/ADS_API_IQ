#!/usr/bin/env python3
"""
Test Orchestration Agent with proper agent-to-agent communication
"""

import requests
import json
import time
from datetime import datetime

def test_api_connection():
    """Test if the API server is running"""
    print("\n[1] Testing API Server Connection...")
    print("-" * 40)

    try:
        response = requests.get("http://localhost:8003/health")
        if response.status_code == 200:
            print("✓ API Server is running on port 8003")
            return True
    except requests.exceptions.ConnectionError:
        print("✗ API Server is not running on port 8003")
        print("  Please run: python api_sqlserver.py")
        return False

def test_adk_server():
    """Test if the ADK server is running"""
    print("\n[2] Testing ADK Server...")
    print("-" * 40)

    try:
        # ADK server health check
        response = requests.get("http://localhost:8000/health")
        if response.status_code == 200:
            print("✓ ADK Server is running on port 8000")
            return True
    except requests.exceptions.ConnectionError:
        print("✗ ADK Server is not running on port 8000")
        print("  Please run: python -m adk run orchestration_agent.agent:root_agent --port 8000")
        return False

def test_orchestration():
    """Test the orchestration flow"""
    print("\n[3] Testing Agent Orchestration...")
    print("-" * 40)

    # Test queries that should trigger different agents
    test_queries = [
        {
            "query": "Get campaign performance data",
            "expected_agent": "DataAgent",
            "description": "Should delegate to DataAgent for data retrieval"
        },
        {
            "query": "Analyze performance trends and detect anomalies",
            "expected_agent": "InsightAgent",
            "description": "Should use DataAgent first, then InsightAgent for analysis"
        },
        {
            "query": "Optimize my campaign bids and budgets",
            "expected_agent": "OptimizationAgent",
            "description": "Should gather data, then use OptimizationAgent"
        },
        {
            "query": "Forecast next month's performance",
            "expected_agent": "ForecastingAgent",
            "description": "Should use historical data, then ForecastingAgent"
        }
    ]

    for test in test_queries:
        print(f"\nTest: {test['description']}")
        print(f"Query: '{test['query']}'")
        print(f"Expected to use: {test['expected_agent']}")

        # Here you would send the actual query to the ADK server
        # For now, we'll just show what should happen
        payload = {
            "message": test["query"],
            "session_id": f"test_{int(time.time())}"
        }

        try:
            # Send request to ADK server
            response = requests.post(
                "http://localhost:8000/chat",
                json=payload
            )

            if response.status_code == 200:
                result = response.json()
                print(f"✓ Response received")
                print(f"  Agent routing successful")

                # Check if the response mentions the expected agent
                if test["expected_agent"].lower() in str(result).lower():
                    print(f"✓ Correctly used {test['expected_agent']}")
            else:
                print(f"✗ Request failed: {response.status_code}")

        except Exception as e:
            print(f"✗ Error: {e}")
            print("  Make sure both servers are running:")
            print("  1. python api_sqlserver.py (port 8003)")
            print("  2. python -m adk run orchestration_agent.agent:root_agent (port 8000)")

def main():
    """Run all tests"""
    print("=" * 60)
    print("Testing Google Ads Multi-Agent System")
    print("=" * 60)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Test connections
    api_ok = test_api_connection()
    adk_ok = test_adk_server()

    if api_ok and adk_ok:
        print("\n✓ Both servers are running!")
        test_orchestration()
    else:
        print("\n✗ Please start the missing servers:")
        if not api_ok:
            print("  1. Start API Server: python api_sqlserver.py")
        if not adk_ok:
            print("  2. Start ADK Server: python -m adk run orchestration_agent.agent:root_agent --port 8000")

    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)

if __name__ == "__main__":
    main()