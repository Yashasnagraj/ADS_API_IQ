#!/usr/bin/env python3
"""
Test script for ADK Chatbot API
"""

import requests
import json
from datetime import datetime

CHATBOT_URL = "http://localhost:8003/api"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    try:
        response = requests.get(f"{CHATBOT_URL.replace('/api', '')}/health")
        data = response.json()
        print(f"✅ Health check: {data['status']}")
        print(f"   ADK Agents: {data['adk_agents']}")
        return True
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

def test_chat(message: str, customer_id: str = None):
    """Test chat endpoint"""
    print(f"\n💬 User: {message}")
    try:
        response = requests.post(
            f"{CHATBOT_URL}/chat",
            json={
                "message": message,
                "customer_id": customer_id
            }
        )
        data = response.json()

        print(f"🤖 Assistant:")
        print(data['response'])
        print(f"\n   Agent used: {data.get('agent_used', 'unknown')}")
        print(f"   Timestamp: {data['timestamp']}")

        return True
    except Exception as e:
        print(f"❌ Chat failed: {e}")
        return False

def test_agents():
    """Test agents endpoint"""
    print("\n🔍 Testing agents endpoint...")
    try:
        response = requests.get(f"{CHATBOT_URL}/agents")
        data = response.json()
        print("✅ Available agents:")
        for agent in data['agents']:
            print(f"   - {agent['name']} ({agent['type']}): {agent['status']}")
        return True
    except Exception as e:
        print(f"❌ Agents endpoint failed: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("ADK Chatbot API Test Suite")
    print("=" * 60)

    # Test 1: Health check
    if not test_health():
        print("\n⚠️  API is not running. Start it with:")
        print("   python chatbot_api.py")
        return

    # Test 2: List agents
    test_agents()

    # Test 3: Various chat queries
    test_queries = [
        "Show top performing campaigns",
        "What keywords are underperforming?",
        "Analyze my performance trends",
        "How should I optimize my budget?",
        "Forecast next month's spend",
        "Are there any issues with my campaigns?"
    ]

    print("\n" + "=" * 60)
    print("Testing Chat Queries")
    print("=" * 60)

    for query in test_queries:
        test_chat(query)
        print("\n" + "-" * 60)

    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main()
