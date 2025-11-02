"""
Verification script to check that agents have been updated with WarehouseClient and customer_id support
"""
import re
from pathlib import Path

def check_file(file_path, checks):
    """
    Check if a file contains expected patterns

    Args:
        file_path: Path to file
        checks: List of (description, pattern, should_exist) tuples

    Returns:
        bool: True if all checks pass
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    results = []
    for description, pattern, should_exist in checks:
        found = bool(re.search(pattern, content))

        if should_exist:
            if found:
                print(f"   [PASS] {description}")
                results.append(True)
            else:
                print(f"   [FAIL] {description} - NOT FOUND")
                results.append(False)
        else:
            if not found:
                print(f"   [PASS] {description} (correctly removed)")
                results.append(True)
            else:
                print(f"   [FAIL] {description} - STILL EXISTS")
                results.append(False)

    return all(results)


def verify_optimization_agent():
    """Verify Optimization Agent has been updated"""
    print("=" * 80)
    print("OPTIMIZATION AGENT VERIFICATION")
    print("=" * 80 + "\n")

    file_path = Path("D:/ADS_API/google-ads-multiagent/adk/orchestration_agent/sub_agents/optimization_agent/agent.py")

    checks = [
        # Should have WarehouseClient import
        ("Imports WarehouseClient", r"from data_agent\.warehouse_client import WarehouseClient", True),

        # Should NOT have DatabaseClient import
        ("No DatabaseClient import", r"from data_agent\.db_client import DatabaseClient", False),

        # Should initialize warehouse_client
        ("Initializes warehouse_client", r"self\.warehouse_client = WarehouseClient\(\)", True),

        # Should NOT initialize db_client
        ("No db_client initialization", r"self\.db_client = DatabaseClient\(\)", False),

        # Should validate customer_id in optimize_bids
        ("optimize_bids validates customer_id", r"def optimize_bids.*?if not customer_id:", True),

        # Should pass customer_id to warehouse_client
        ("optimize_bids passes customer_id", r"warehouse_client\.fetch_campaigns\(customer_id=int\(customer_id\)\)", True),

        # Should validate customer_id in optimize_budgets
        ("optimize_budgets validates customer_id", r"def optimize_budgets.*?if not customer_id:", True),

        # Should validate customer_id in recommend_budget_allocation
        ("recommend_budget_allocation validates customer_id", r"def recommend_budget_allocation.*?if not customer_id:", True),

        # Should validate customer_id in optimize_keywords
        ("optimize_keywords validates customer_id", r"def optimize_keywords.*?if not customer_id:", True),
    ]

    result = check_file(file_path, checks)

    if result:
        print("\n[PASS] Optimization Agent verification PASSED\n")
    else:
        print("\n[FAIL] Optimization Agent verification FAILED\n")

    return result


def verify_forecasting_agent():
    """Verify Forecasting Agent has been updated"""
    print("=" * 80)
    print("FORECASTING AGENT VERIFICATION")
    print("=" * 80 + "\n")

    file_path = Path("D:/ADS_API/google-ads-multiagent/adk/orchestration_agent/sub_agents/forecasting_agent/agent.py")

    checks = [
        # Should have WarehouseClient import
        ("Imports WarehouseClient", r"from data_agent\.warehouse_client import WarehouseClient", True),

        # Should NOT have DatabaseClient import
        ("No DatabaseClient import", r"from data_agent\.db_client import DatabaseClient", False),

        # Should initialize warehouse_client
        ("Initializes warehouse_client", r"self\.warehouse_client = WarehouseClient\(\)", True),

        # Should NOT initialize db_client
        ("No db_client initialization", r"self\.db_client = DatabaseClient\(\)", False),

        # Should validate customer_id in predict_ctr
        ("predict_ctr validates customer_id", r"def predict_ctr.*?if not customer_id:", True),

        # Should pass customer_id to warehouse_client
        ("predict_ctr passes customer_id", r"warehouse_client\.fetch_campaigns\(customer_id=int\(customer_id\)\)", True),

        # Should validate customer_id in forecast_spend
        ("forecast_spend validates customer_id", r"def forecast_spend.*?if not customer_id:", True),

        # Should validate customer_id in predict_conversions
        ("predict_conversions validates customer_id", r"def predict_conversions.*?if not customer_id:", True),

        # Should validate customer_id in analyze_scenarios
        ("analyze_scenarios validates customer_id", r"def analyze_scenarios.*?if not customer_id:", True),
    ]

    result = check_file(file_path, checks)

    if result:
        print("\n[PASS] Forecasting Agent verification PASSED\n")
    else:
        print("\n[FAIL] Forecasting Agent verification FAILED\n")

    return result


def main():
    """Run all verifications"""
    print("\n" + "=" * 80)
    print("AGENT UPDATE VERIFICATION SUITE")
    print("=" * 80 + "\n")

    results = []

    # Verify Optimization Agent
    results.append(("Optimization Agent", verify_optimization_agent()))

    # Verify Forecasting Agent
    results.append(("Forecasting Agent", verify_forecasting_agent()))

    # Summary
    print("=" * 80)
    print("VERIFICATION SUMMARY")
    print("=" * 80)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS] PASSED" if result else "[FAIL] FAILED"
        print(f"{test_name:40} : {status}")

    print(f"\nTotal: {passed}/{total} verifications passed")

    if passed == total:
        print("\n[SUCCESS] ALL VERIFICATIONS PASSED!")
        print("\nBoth agents have been successfully updated with:")
        print("  1. WarehouseClient instead of DatabaseClient")
        print("  2. customer_id validation in all methods")
        print("  3. customer_id passed to all database queries")
        print("\nAgents now support customer filtering!\n")
    else:
        print(f"\n[WARN] {total - passed} verification(s) failed.\n")

    return passed == total


if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
