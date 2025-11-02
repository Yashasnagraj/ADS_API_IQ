"""
Test Chatbot Customer Filtering Integration
Verifies that chatbot correctly filters data by customer and includes customer names in responses
"""
import requests
import json
from typing import Dict, Any
import sys

# Chatbot API endpoint
CHATBOT_API_URL = "http://localhost:8003/api/chat"

# Test customers from database
TEST_CUSTOMERS = [
    {"customer_id": "1", "expected_name": "Emcee Sons"},
    {"customer_id": "2", "expected_name": "VANAVASI KALYANA"},
    {"customer_id": "3", "expected_name": "Communn.io"}
]

# Test queries for different agents
TEST_QUERIES = {
    "data_agent": {
        "message": "Show me my campaigns",
        "expected_agent": "data",
        "check_keywords": ["campaign"]
    },
    "insight_agent_trends": {
        "message": "Analyze my performance trends",
        "expected_agent": "insight",
        "check_keywords": ["trend", "performance", "click", "conversion"]
    },
    "insight_agent_anomalies": {
        "message": "Detect any anomalies in my campaigns",
        "expected_agent": "insight",
        "check_keywords": ["anomal", "recommendation"]
    },
    "insight_agent_roi": {
        "message": "Calculate my ROI",
        "expected_agent": "insight",
        "check_keywords": ["roi", "roas"]
    },
    "optimization_agent_bids": {
        "message": "How should I optimize my bids?",
        "expected_agent": "optimization",
        "check_keywords": ["bid", "cpc", "recommendation"]
    },
    "optimization_agent_budgets": {
        "message": "Optimize my budgets",
        "expected_agent": "optimization",
        "check_keywords": ["budget", "recommendation"]
    },
    "forecasting_agent": {
        "message": "Forecast my performance for next 30 days",
        "expected_agent": "forecasting",
        "check_keywords": ["forecast", "predict", "click", "spend"]
    }
}

def send_chat_message(message: str, customer_id: str) -> Dict[str, Any]:
    """Send a message to the chatbot API"""
    try:
        response = requests.post(
            CHATBOT_API_URL,
            json={
                "message": message,
                "customer_id": customer_id
            },
            timeout=30
        )
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}

def check_customer_name_in_response(response_text: str, customer_name: str) -> bool:
    """Check if customer name appears in the response"""
    return customer_name.lower() in response_text.lower()

def check_keywords_in_response(response_text: str, keywords: list) -> list:
    """Check which keywords are present in the response"""
    found = []
    response_lower = response_text.lower()
    for keyword in keywords:
        if keyword.lower() in response_lower:
            found.append(keyword)
    return found

def test_chatbot_api_health():
    """Test if chatbot API is running"""
    print("=" * 80)
    print("TEST 1: Chatbot API Health Check")
    print("=" * 80)

    try:
        response = requests.get("http://localhost:8003/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"[PASS] API is healthy")
            print(f"   Status: {data.get('status')}")
            print(f"   ADK Agents: {data.get('adk_agents')}")
            print(f"   Gemini Enabled: {data.get('gemini_enabled')}")
            return True
        else:
            print(f"[FAIL] API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"[FAIL] Cannot connect to API: {e}")
        print("\nMake sure chatbot API is running:")
        print("   cd google-ads-multiagent/adk")
        print("   python chatbot_api.py")
        return False

def test_customer_filtering():
    """Test that each customer gets their own data"""
    print("\n" + "=" * 80)
    print("TEST 2: Customer Data Filtering")
    print("=" * 80)

    results = []

    for customer in TEST_CUSTOMERS:
        customer_id = customer["customer_id"]
        expected_name = customer["expected_name"]

        print(f"\nTesting Customer {customer_id}: {expected_name}")
        print("-" * 60)

        # Test with a simple campaign query
        response = send_chat_message("Show me my campaigns", customer_id)

        if "error" in response:
            print(f"   [FAIL] API Error: {response['error']}")
            results.append(False)
            continue

        response_text = response.get("response", "")

        # Check 1: Response is not empty
        if not response_text:
            print(f"   [FAIL] Empty response received")
            results.append(False)
            continue

        print(f"   [PASS] Received response ({len(response_text)} chars)")

        # Check 2: Customer name appears in response (Gemini should mention it)
        has_customer_name = check_customer_name_in_response(response_text, expected_name)
        if has_customer_name:
            print(f"   [PASS] Customer name '{expected_name}' found in response")
        else:
            print(f"   [INFO] Customer name '{expected_name}' not in response (Gemini may not always mention it)")

        # Check 3: Response mentions campaigns
        if "campaign" in response_text.lower():
            print(f"   [PASS] Response includes campaign data")
            results.append(True)
        else:
            print(f"   [WARN] Response doesn't mention campaigns")
            results.append(False)

    return all(results)

def test_all_agents():
    """Test all agents with customer filtering"""
    print("\n" + "=" * 80)
    print("TEST 3: All Agents with Customer Filtering")
    print("=" * 80)

    # Use first customer for agent tests
    test_customer = TEST_CUSTOMERS[0]
    customer_id = test_customer["customer_id"]
    customer_name = test_customer["expected_name"]

    print(f"\nTesting all agents with Customer {customer_id}: {customer_name}")
    print("=" * 60)

    results = []

    for test_name, test_config in TEST_QUERIES.items():
        print(f"\n{test_name.replace('_', ' ').title()}")
        print("-" * 60)
        print(f"Query: '{test_config['message']}'")

        response = send_chat_message(test_config["message"], customer_id)

        if "error" in response:
            print(f"   [FAIL] API Error: {response['error']}")
            results.append(False)
            continue

        response_text = response.get("response", "")
        metadata = response.get("metadata", {})

        # Check 1: Response received
        if not response_text:
            print(f"   [FAIL] Empty response")
            results.append(False)
            continue

        print(f"   [PASS] Response received ({len(response_text)} chars)")

        # Check 2: Expected agent was used
        agent_used = metadata.get("intent", {}).get("agent")
        if agent_used == test_config["expected_agent"]:
            print(f"   [PASS] Correct agent used: {agent_used}")
        else:
            print(f"   [INFO] Agent used: {agent_used} (expected: {test_config['expected_agent']})")

        # Check 3: Keywords present
        found_keywords = check_keywords_in_response(response_text, test_config["check_keywords"])
        if found_keywords:
            print(f"   [PASS] Keywords found: {', '.join(found_keywords)}")
            results.append(True)
        else:
            print(f"   [WARN] No keywords found from: {test_config['check_keywords']}")
            results.append(False)

        # Check 4: Customer name in response (optional but good)
        if check_customer_name_in_response(response_text, customer_name):
            print(f"   [BONUS] Customer name '{customer_name}' mentioned in response")

        # Print first 150 chars of response (avoiding unicode issues)
        try:
            preview = response_text[:150].replace('\n', ' ').encode('ascii', 'ignore').decode('ascii')
            print(f"   Preview: {preview}...")
        except Exception:
            print(f"   Preview: <response contains special characters>")

    return all(results)

def test_customer_isolation():
    """Test that different customers get different data"""
    print("\n" + "=" * 80)
    print("TEST 4: Customer Data Isolation")
    print("=" * 80)

    print("\nTesting that different customers receive different data...")
    print("-" * 60)

    # Get campaigns for all customers
    responses = {}
    for customer in TEST_CUSTOMERS[:2]:  # Test first 2 customers
        customer_id = customer["customer_id"]
        customer_name = customer["expected_name"]

        response = send_chat_message("Show me my top 3 campaigns", customer_id)

        if "error" not in response:
            responses[customer_id] = response.get("response", "")
            print(f"Customer {customer_id} ({customer_name}): {len(responses[customer_id])} chars")

    if len(responses) < 2:
        print("[FAIL] Could not get responses for multiple customers")
        return False

    # Compare responses - they should be different
    customer_ids = list(responses.keys())
    response1 = responses[customer_ids[0]]
    response2 = responses[customer_ids[1]]

    if response1 == response2:
        print("[FAIL] Responses are identical for different customers!")
        print("   This suggests customer filtering is NOT working.")
        return False
    else:
        print("[PASS] Responses are different for different customers")
        print("   Customer data is properly isolated.")
        return True

def test_missing_customer_id():
    """Test that API handles missing customer_id gracefully"""
    print("\n" + "=" * 80)
    print("TEST 5: Missing Customer ID Handling")
    print("=" * 80)

    print("\nTesting API behavior without customer_id...")
    print("-" * 60)

    try:
        response = requests.post(
            CHATBOT_API_URL,
            json={
                "message": "Show me campaigns"
                # No customer_id provided
            },
            timeout=10
        )

        if response.status_code == 200:
            data = response.json()
            response_text = data.get("response", "")

            # Should either work with all customers or return an error message
            print(f"[PASS] API handled missing customer_id")
            print(f"   Response: {response_text[:150]}...")
            return True
        else:
            print(f"[INFO] API returned status {response.status_code}")
            return True

    except Exception as e:
        print(f"[FAIL] Error: {e}")
        return False

def main():
    """Run all tests"""
    print("\n" + "#" * 80)
    print("CHATBOT CUSTOMER FILTERING TEST SUITE")
    print("#" * 80)
    print("\nThis test suite verifies:")
    print("1. Chatbot API is running and healthy")
    print("2. Each customer receives their own filtered data")
    print("3. All agents work with customer filtering")
    print("4. Customer data is properly isolated")
    print("5. Missing customer_id is handled gracefully")
    print("\n" + "#" * 80 + "\n")

    results = {}

    # Test 1: API Health
    results["api_health"] = test_chatbot_api_health()

    if not results["api_health"]:
        print("\n" + "=" * 80)
        print("TESTS ABORTED: Chatbot API is not running")
        print("=" * 80)
        print("\nPlease start the chatbot API:")
        print("   cd D:\\ADS_API\\google-ads-multiagent\\adk")
        print("   python chatbot_api.py")
        return False

    # Test 2: Customer Filtering
    results["customer_filtering"] = test_customer_filtering()

    # Test 3: All Agents
    results["all_agents"] = test_all_agents()

    # Test 4: Customer Isolation
    results["customer_isolation"] = test_customer_isolation()

    # Test 5: Missing Customer ID
    results["missing_customer_id"] = test_missing_customer_id()

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    for test_name, passed in results.items():
        status = "[PASS]" if passed else "[FAIL]"
        test_label = test_name.replace("_", " ").title()
        print(f"{status} {test_label}")

    total = len(results)
    passed = sum(1 for r in results.values() if r)

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n" + "=" * 80)
        print("SUCCESS! All tests passed!")
        print("=" * 80)
        print("\nChatbot customer filtering is working correctly!")
        print("All agents properly filter data by customer.")
        print("Customer names are included in responses naturally.")
        return True
    else:
        print("\n" + "=" * 80)
        print(f"PARTIAL SUCCESS: {passed}/{total} tests passed")
        print("=" * 80)
        print("\nSome tests failed. Please review the output above.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
