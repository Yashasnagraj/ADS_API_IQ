"""
Simple test script to verify Optimization and Forecasting agents support customer filtering
"""
import sys
from pathlib import Path

# Add all necessary paths
project_root = Path(__file__).parent
agents_root = project_root / "google-ads-multiagent" / "adk" / "orchestration_agent" / "sub_agents"

sys.path.insert(0, str(project_root))
sys.path.insert(0, str(agents_root))
sys.path.insert(0, str(agents_root / "optimization_agent"))
sys.path.insert(0, str(agents_root / "forecasting_agent"))
sys.path.insert(0, str(agents_root / "data_agent"))

from data_agent.warehouse_client import WarehouseClient
from optimization_agent.agent import OptimizationAgent
from forecasting_agent.agent import ForecastingAgent


def test_optimization_agent():
    """Test Optimization Agent with customer filtering"""
    print("=" * 80)
    print("OPTIMIZATION AGENT TEST")
    print("=" * 80)

    try:
        # Get customers
        warehouse_client = WarehouseClient()
        customers = warehouse_client.get_customers()

        if not customers:
            print("\n[FAIL] No customers found")
            return False

        print(f"\nFound {len(customers)} customers")

        # Initialize agent
        agent = OptimizationAgent()

        # Test with first customer
        customer = customers[0]
        customer_id = str(customer['customer_id'])
        customer_name = customer['customer_name']

        print(f"\nTesting with customer {customer_id}: {customer_name}")

        # Test optimize_bids
        print("\n1. Testing optimize_bids()...")
        result = agent.optimize_bids(customer_id=customer_id, target_roas=4.0)

        if result.get('status') == 'error':
            print(f"   [FAIL] Error: {result.get('message')}")
            return False

        print(f"   [PASS] Status: {result.get('status')}")
        print(f"   Recommendations: {result.get('total_recommendations', 0)}")

        # Test optimize_budgets
        print("\n2. Testing optimize_budgets()...")
        result = agent.optimize_budgets(customer_id=customer_id)

        if result.get('status') == 'error':
            print(f"   [FAIL] Error: {result.get('message')}")
            return False

        print(f"   [PASS] Status: {result.get('status')}")
        print(f"   Recommendations: {result.get('total_recommendations', 0)}")

        # Test without customer_id (should fail)
        print("\n3. Testing without customer_id (should fail)...")
        result = agent.optimize_bids(customer_id=None)

        if result.get('status') != 'error':
            print("   [FAIL] Should return error when customer_id is missing")
            return False

        print(f"   [PASS] Correctly returns error: {result.get('message')}")

        print("\n[PASS] Optimization Agent test PASSED\n")
        return True

    except Exception as e:
        print(f"\n[FAIL] Test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_forecasting_agent():
    """Test Forecasting Agent with customer filtering"""
    print("=" * 80)
    print("FORECASTING AGENT TEST")
    print("=" * 80)

    try:
        # Get customers
        warehouse_client = WarehouseClient()
        customers = warehouse_client.get_customers()

        if not customers:
            print("\n[FAIL] No customers found")
            return False

        print(f"\nFound {len(customers)} customers")

        # Initialize agent
        agent = ForecastingAgent()

        # Test with first customer
        customer = customers[0]
        customer_id = str(customer['customer_id'])
        customer_name = customer['customer_name']

        print(f"\nTesting with customer {customer_id}: {customer_name}")

        # Test predict_ctr
        print("\n1. Testing predict_ctr()...")
        result = agent.predict_ctr(customer_id=customer_id, forecast_days=7)

        if result.get('status') == 'error':
            print(f"   [FAIL] Error: {result.get('message')}")
            return False

        print(f"   [PASS] Status: {result.get('status')}")
        print(f"   Predictions: {len(result.get('predictions', []))}")

        # Test forecast_spend
        print("\n2. Testing forecast_spend()...")
        result = agent.forecast_spend(customer_id=customer_id, forecast_days=30)

        if result.get('status') == 'error':
            print(f"   [FAIL] Error: {result.get('message')}")
            return False

        print(f"   [PASS] Status: {result.get('status')}")
        forecast = result.get('forecast', {})
        print(f"   Forecasted spend: ${forecast.get('forecasted_total_spend', 0):.2f}")

        # Test without customer_id (should fail)
        print("\n3. Testing without customer_id (should fail)...")
        result = agent.predict_ctr(customer_id=None)

        if result.get('status') != 'error':
            print("   [FAIL] Should return error when customer_id is missing")
            return False

        print(f"   [PASS] Correctly returns error: {result.get('message')}")

        print("\n[PASS] Forecasting Agent test PASSED\n")
        return True

    except Exception as e:
        print(f"\n[FAIL] Test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("AGENT CUSTOMER FILTERING TEST SUITE")
    print("=" * 80 + "\n")

    results = []

    # Test 1: Optimization Agent
    results.append(("Optimization Agent", test_optimization_agent()))

    # Test 2: Forecasting Agent
    results.append(("Forecasting Agent", test_forecasting_agent()))

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS] PASSED" if result else "[FAIL] FAILED"
        print(f"{test_name:40} : {status}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED! Agents now support customer filtering.\n")
    else:
        print(f"\n[WARN] {total - passed} test(s) failed. Please review errors above.\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
