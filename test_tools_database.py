"""
Test script to verify all agent tools can fetch data from the database
"""
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

import sqlite3
import importlib.util

# Import WarehouseClient using importlib
warehouse_client_path = project_root / "google-ads-multiagent" / "adk" / "orchestration_agent" / "sub_agents" / "data_agent" / "warehouse_client.py"
spec = importlib.util.spec_from_file_location("warehouse_client", warehouse_client_path)
warehouse_client_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(warehouse_client_module)
WarehouseClient = warehouse_client_module.WarehouseClient

def test_database_connection():
    """Test basic database connectivity"""
    print("=" * 80)
    print("DATABASE CONNECTION TEST")
    print("=" * 80)

    db_path = project_root / "marketing_warehouse.db"
    print(f"\nDatabase path: {db_path}")
    print(f"Database exists: {db_path.exists()}")

    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
        tables = [row[0] for row in cursor.fetchall()]
        print(f"\nTotal tables: {len(tables)}")
        print(f"Tables: {', '.join(tables[:10])}...")

        # Get record counts
        print("\n" + "-" * 80)
        print("TABLE RECORD COUNTS")
        print("-" * 80)

        important_tables = [
            'dim_customer',
            'dim_google_ads_campaign',
            'dim_ga4_source_medium',
            'campaigns',
            'fact_campaign_performance_daily',
            'ga4_sessions',
            'shopify_orders',
            'keywords',
            'ad_groups'
        ]

        for table in important_tables:
            if table in tables:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table:40} : {count:>6} records")

        conn.close()
        print("\n[PASS] Database connection test PASSED\n")
        return True

    except Exception as e:
        print(f"\n[FAIL] Database connection test FAILED: {e}\n")
        return False


def test_warehouse_client():
    """Test WarehouseClient methods"""
    print("=" * 80)
    print("WAREHOUSE CLIENT TEST")
    print("=" * 80)

    try:
        client = WarehouseClient()

        # Test 1: Get customers
        print("\n1. Testing get_customers()...")
        customers = client.get_customers()
        print(f"   Found {len(customers)} customers")
        for customer in customers:
            print(f"   - {customer['customer_id']}: {customer['customer_name']}")

        if len(customers) == 0:
            print("   [WARN] WARNING: No customers found in database")
            return False

        customer_id = customers[0]['customer_id']
        print(f"\n   Using customer_id {customer_id} for remaining tests\n")

        # Test 2: Fetch campaigns
        print("2. Testing fetch_campaigns()...")
        result = client.fetch_campaigns(customer_id=customer_id)
        if 'error' in result:
            print(f"   [FAIL] ERROR: {result['error']}")
            return False
        print(f"   Found {result['total']} campaigns")
        if result['total'] > 0:
            campaign = result['campaigns'][0]
            print(f"   Sample: {campaign['name']} - {campaign['status']}")
        else:
            print("   [WARN] WARNING: No campaigns found")

        # Test 3: Fetch traffic sources
        print("\n3. Testing fetch_traffic_sources()...")
        result = client.fetch_traffic_sources(customer_id=customer_id)
        if 'error' in result:
            print(f"   [FAIL] ERROR: {result['error']}")
            return False
        print(f"   Found {result['total']} traffic sources")
        if result['total'] > 0:
            source = result['traffic_sources'][0]
            print(f"   Sample: {source['source']}/{source['medium']} - {source['sessions']} sessions")
        else:
            print("   [WARN] WARNING: No traffic sources found")

        # Test 4: Fetch metrics summary
        print("\n4. Testing fetch_metrics_summary()...")
        result = client.fetch_metrics_summary(customer_id=customer_id)
        if 'error' in result:
            print(f"   [FAIL] ERROR: {result['error']}")
            return False
        summary = result.get('summary', {})
        print(f"   Total campaigns: {summary.get('total_campaigns', 0)}")
        print(f"   Total impressions: {summary.get('total_impressions', 0)}")
        print(f"   Total clicks: {summary.get('total_clicks', 0)}")
        print(f"   Total cost: ${summary.get('total_cost', 0):.2f}")
        print(f"   Total conversions: {summary.get('total_conversions', 0)}")

        # Test 5: Fetch campaign performance (if we have campaigns)
        campaigns_result = client.fetch_campaigns(customer_id=customer_id)
        if campaigns_result['total'] > 0:
            campaign_id = campaigns_result['campaigns'][0]['id']
            print(f"\n5. Testing fetch_campaign_performance() for campaign {campaign_id}...")
            result = client.fetch_campaign_performance(campaign_id=str(campaign_id), customer_id=customer_id)
            if 'error' in result:
                print(f"   [FAIL] ERROR: {result['error']}")
                return False
            print(f"   Found {result['data_points']} performance records")

        print("\n[PASS] WarehouseClient test PASSED\n")
        return True

    except Exception as e:
        print(f"\n[FAIL] WarehouseClient test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def test_customer_filtering():
    """Test customer_id filtering across all methods"""
    print("=" * 80)
    print("CUSTOMER FILTERING TEST")
    print("=" * 80)

    try:
        client = WarehouseClient()
        customers = client.get_customers()

        if len(customers) < 2:
            print("\n[WARN] Need at least 2 customers to test filtering. Skipping.")
            return True

        print(f"\nTesting filtering with {len(customers)} customers\n")

        for customer in customers:
            customer_id = customer['customer_id']
            customer_name = customer['customer_name']

            print(f"Testing customer {customer_id}: {customer_name}")

            # Test campaigns filtering
            campaigns = client.fetch_campaigns(customer_id=customer_id)
            print(f"  - Campaigns: {campaigns['total']}")

            # Verify all campaigns belong to this customer
            if campaigns['total'] > 0:
                for campaign in campaigns['campaigns']:
                    if campaign.get('customer_name') != customer_name:
                        print(f"  [FAIL] ERROR: Found campaign from different customer!")
                        return False

            # Test traffic sources filtering
            sources = client.fetch_traffic_sources(customer_id=customer_id)
            print(f"  - Traffic sources: {sources['total']}")

            # Test metrics summary filtering
            summary = client.fetch_metrics_summary(customer_id=customer_id)
            print(f"  - Total impressions: {summary['summary'].get('total_impressions', 0)}")

        print("\n[PASS] Customer filtering test PASSED\n")
        return True

    except Exception as e:
        print(f"\n[FAIL] Customer filtering test FAILED: {e}\n")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "=" * 80)
    print("MARKETING IQ - DATABASE & TOOLS TEST SUITE")
    print("=" * 80 + "\n")

    results = []

    # Test 1: Database connection
    results.append(("Database Connection", test_database_connection()))

    # Test 2: WarehouseClient
    results.append(("WarehouseClient Methods", test_warehouse_client()))

    # Test 3: Customer filtering
    results.append(("Customer Filtering", test_customer_filtering()))

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
        print("\n[SUCCESS] ALL TESTS PASSED! Database and tools are working correctly.\n")
    else:
        print(f"\n[WARN] {total - passed} test(s) failed. Please review errors above.\n")

    return passed == total


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
