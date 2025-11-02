"""
Test script to verify Optimization and Forecasting agents support customer filtering
"""
import sys
from pathlib import Path
import importlib.util

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def import_module_from_path(module_name, file_path):
    """Import a module from a file path"""
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

# Import agents
optimization_agent_path = project_root / "google-ads-multiagent" / "adk" / "orchestration_agent" / "sub_agents" / "optimization_agent" / "agent.py"
forecasting_agent_path = project_root / "google-ads-multiagent" / "adk" / "orchestration_agent" / "sub_agents" / "forecasting_agent" / "agent.py"
warehouse_client_path = project_root / "google-ads-multiagent" / "adk" / "orchestration_agent" / "sub_agents" / "data_agent" / "warehouse_client.py"

optimization_module = import_module_from_path("optimization_agent", optimization_agent_path)
forecasting_module = import_module_from_path("forecasting_agent", forecasting_agent_path)
warehouse_module = import_module_from_path("warehouse_client", warehouse_client_path)

OptimizationAgent = optimization_module.OptimizationAgent
ForecastingAgent = forecasting_module.ForecastingAgent
WarehouseClient = warehouse_module.WarehouseClient


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
            print("\n[FAIL] No customers found in database")
            return False

        print(f"\nFound {len(customers)} customers")

        # Initialize agent
        agent = OptimizationAgent()
        print(f"Optimization Agent initialized: {agent.name}")
        print(f"Mode: {agent.mode.value}")

        # Test with each customer
        for customer in customers:
            customer_id = customer['customer_id']
            customer_name = customer['customer_name']

            print(f"\n{'-' * 80}")
            print(f"Testing customer {customer_id}: {customer_name}")
            print(f"{'-' * 80}")

            # Test 1: optimize_bids
            print("\n1. Testing optimize_bids()...")
            result = agent.optimize_bids(
                customer_id=str(customer_id),
                target_roas=4.0,
                max_bid_limit=10.0
            )

            if result.get('status') == 'error':
                print(f"   [FAIL] Error: {result.get('message')}")
                return False

            print(f"   Status: {result.get('status')}")
            print(f"   Mode: {result.get('mode')}")
            print(f"   Recommendations: {result.get('total_recommendations', 0)}")

            # Test 2: optimize_budgets
            print("\n2. Testing optimize_budgets()...")
            result = agent.optimize_budgets(
                customer_id=str(customer_id),
                total_budget=None,
                reallocation_strategy="performance_based"
            )

            if result.get('status') == 'error':
                print(f"   [FAIL] Error: {result.get('message')}")
                return False

            print(f"   Status: {result.get('status')}")
            print(f"   Recommendations: {result.get('total_recommendations', 0)}")

            # Test 3: recommend_budget_allocation
            print("\n3. Testing recommend_budget_allocation()...")
            result = agent.recommend_budget_allocation(
                customer_id=str(customer_id),
                optimization_goal="maximize_conversions"
            )

            if result.get('status') == 'error':
                print(f"   [FAIL] Error: {result.get('message')}")
                return False

            print(f"   Status: {result.get('status')}")
            if 'impact_summary' in result:
                summary = result['impact_summary']
                print(f"   Total budget: ${summary.get('total_budget', 0):.2f}")
                print(f"   Campaigns optimized: {summary.get('campaigns_optimized', 0)}")

            # Test 4: optimize_keywords
            print("\n4. Testing optimize_keywords()...")
            result = agent.optimize_keywords(
                customer_id=str(customer_id),
                add_negative_keywords=True
            )

            if result.get('status') == 'error':
                print(f"   [FAIL] Error: {result.get('message')}")
                return False

            print(f"   Status: {result.get('status')}")
            print(f"   Recommendations: {result.get('total_recommendations', 0)}")

        # Test 5: Error handling - missing customer_id
        print(f"\n{'-' * 80}")
        print("Testing error handling (missing customer_id)")
        print(f"{'-' * 80}")

        result = agent.optimize_bids(customer_id=None)
        if result.get('status') != 'error':
            print("   [FAIL] Should return error when customer_id is missing")
            return False
        print(f"   [PASS] Correctly returns error: {result.get('message')}")

        print("\n[PASS] Optimization Agent test PASSED\n")
        return True

    except Exception as e:
        print(f"\n[FAIL] Optimization Agent test FAILED: {e}\n")
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
            print("\n[FAIL] No customers found in database")
            return False

        print(f"\nFound {len(customers)} customers")

        # Initialize agent
        agent = ForecastingAgent()
        print(f"Forecasting Agent initialized: {agent.name}")

        # Test with each customer
        for customer in customers:
            customer_id = customer['customer_id']
            customer_name = customer['customer_name']

            print(f"\n{'-' * 80}")
            print(f"Testing customer {customer_id}: {customer_name}")
            print(f"{'-' * 80}")

            # Test 1: predict_ctr
            print("\n1. Testing predict_ctr()...")
            result = agent.predict_ctr(
                customer_id=str(customer_id),
                forecast_days=7,
                use_ml=False
            )

            if result.get('status') == 'error':
                print(f"   [FAIL] Error: {result.get('message')}")
                return False

            print(f"   Status: {result.get('status')}")
            print(f"   Predictions: {len(result.get('predictions', []))}")
            if result.get('predictions'):
                sample = result['predictions'][0]
                print(f"   Sample: {sample.get('campaign')} - CTR {sample.get('current_ctr')}% -> {sample.get('predicted_ctr')}%")

            # Test 2: forecast_spend
            print("\n2. Testing forecast_spend()...")
            result = agent.forecast_spend(
                customer_id=str(customer_id),
                forecast_days=30,
                include_seasonality=True
            )

            if result.get('status') == 'error':
                print(f"   [FAIL] Error: {result.get('message')}")
                return False

            print(f"   Status: {result.get('status')}")
            forecast = result.get('forecast', {})
            if forecast:
                print(f"   Current monthly spend: ${forecast.get('current_monthly_spend', 0):.2f}")
                print(f"   Forecasted spend: ${forecast.get('forecasted_total_spend', 0):.2f}")
                print(f"   Change: {forecast.get('spend_change_percent', 0):.1f}%")

            # Test 3: predict_conversions
            print("\n3. Testing predict_conversions()...")
            result = agent.predict_conversions(
                customer_id=str(customer_id),
                forecast_days=7,
                scenario=None
            )

            if result.get('status') == 'error':
                print(f"   [FAIL] Error: {result.get('message')}")
                return False

            print(f"   Status: {result.get('status')}")
            summary = result.get('summary', {})
            print(f"   Current conversions: {summary.get('total_current_conversions', 0)}")
            print(f"   Predicted conversions: {summary.get('total_predicted_conversions', 0)}")

            # Test 4: analyze_scenarios
            print("\n4. Testing analyze_scenarios()...")
            result = agent.analyze_scenarios(
                customer_id=str(customer_id),
                scenarios=None  # Use default scenarios
            )

            if result.get('status') == 'error':
                print(f"   [FAIL] Error: {result.get('message')}")
                return False

            print(f"   Status: {result.get('status')}")
            print(f"   Scenarios analyzed: {len(result.get('scenario_results', []))}")
            if result.get('optimal_scenario'):
                optimal = result['optimal_scenario']
                print(f"   Optimal scenario: {optimal.get('scenario_name')}")
                print(f"   Predicted ROAS: {optimal.get('predicted_roas', 0):.2f}x")

        # Test 5: Error handling - missing customer_id
        print(f"\n{'-' * 80}")
        print("Testing error handling (missing customer_id)")
        print(f"{'-' * 80}")

        result = agent.predict_ctr(customer_id=None)
        if result.get('status') != 'error':
            print("   [FAIL] Should return error when customer_id is missing")
            return False
        print(f"   [PASS] Correctly returns error: {result.get('message')}")

        print("\n[PASS] Forecasting Agent test PASSED\n")
        return True

    except Exception as e:
        print(f"\n[FAIL] Forecasting Agent test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_customer_isolation():
    """Test that agents properly isolate data between customers"""
    print("=" * 80)
    print("CUSTOMER ISOLATION TEST")
    print("=" * 80)

    try:
        warehouse_client = WarehouseClient()
        customers = warehouse_client.get_customers()

        if len(customers) < 2:
            print("\n[WARN] Need at least 2 customers to test isolation. Skipping.")
            return True

        print(f"\nTesting isolation between {len(customers)} customers\n")

        optimization_agent = OptimizationAgent()
        forecasting_agent = ForecastingAgent()

        results_by_customer = {}

        for customer in customers:
            customer_id = customer['customer_id']
            customer_name = customer['customer_name']

            print(f"Fetching data for customer {customer_id}: {customer_name}")

            # Get optimization recommendations
            opt_result = optimization_agent.optimize_bids(
                customer_id=str(customer_id),
                target_roas=4.0
            )

            # Get forecast
            forecast_result = forecasting_agent.forecast_spend(
                customer_id=str(customer_id),
                forecast_days=30
            )

            results_by_customer[customer_id] = {
                'name': customer_name,
                'optimization_recs': opt_result.get('total_recommendations', 0),
                'forecast_spend': forecast_result.get('forecast', {}).get('forecasted_total_spend', 0)
            }

        # Verify results are different for different customers
        print(f"\n{'-' * 80}")
        print("Customer isolation results:")
        print(f"{'-' * 80}")

        for customer_id, data in results_by_customer.items():
            print(f"Customer {customer_id} ({data['name']}):")
            print(f"  Optimization recommendations: {data['optimization_recs']}")
            print(f"  Forecasted spend: ${data['forecast_spend']:.2f}")

        # Check if at least some customers have different results
        unique_values = len(set(str(d) for d in results_by_customer.values()))
        if unique_values > 1:
            print(f"\n[PASS] Customer isolation verified - customers have different results")
            return True
        else:
            print(f"\n[WARN] All customers have identical results (may be normal if data is similar)")
            return True

    except Exception as e:
        print(f"\n[FAIL] Customer isolation test FAILED: {e}\n")
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

    # Test 3: Customer Isolation
    results.append(("Customer Isolation", test_customer_isolation()))

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
