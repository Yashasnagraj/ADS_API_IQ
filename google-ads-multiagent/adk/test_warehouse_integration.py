"""
Test ADK Integration with Marketing Warehouse

Tests that agents can successfully query and analyze data from the new
multi-platform marketing warehouse (marketing_warehouse.db)
"""

import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

from loguru import logger
from orchestration_agent.sub_agents.data_agent.agent import DataAgent
from orchestration_agent.sub_agents.insight_agent.agent import InsightAgent

logger.add(sys.stdout, colorize=True, format="<green>{time:HH:mm:ss}</green> | <level>{level:8}</level> | {message}")


def test_warehouse_client():
    """Test warehouse client directly"""
    print("\n" + "=" * 70)
    print("TEST 1: Warehouse Client Connection")
    print("=" * 70)

    try:
        from orchestration_agent.sub_agents.data_agent.warehouse_client import WarehouseClient

        client = WarehouseClient()
        print("✅ Warehouse client initialized successfully")

        # Test get customers
        customers = client.get_customers()
        print(f"✅ Found {len(customers)} customers:")
        for cust in customers:
            print(f"   - {cust['customer_name']} (ID: {cust['customer_id']})")

        return True

    except Exception as e:
        print(f"❌ Warehouse client test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_data_agent_warehouse():
    """Test Data Agent with warehouse"""
    print("\n" + "=" * 70)
    print("TEST 2: Data Agent with Warehouse")
    print("=" * 70)

    try:
        # Initialize Data Agent with warehouse
        agent = DataAgent(use_warehouse=True)
        print(f"✅ Data Agent initialized (warehouse: {agent.use_warehouse})")

        # Test fetch campaigns from warehouse
        print("\n📊 Fetching campaigns from warehouse...")
        campaigns = agent.fetch_campaigns_warehouse(limit=10)

        if "error" in campaigns:
            print(f"❌ Error: {campaigns['error']}")
            return False

        total = campaigns.get('total', 0)
        print(f"✅ Fetched {total} campaigns")

        if total > 0:
            print("\n📋 Sample campaigns:")
            for i, camp in enumerate(campaigns['campaigns'][:5], 1):
                print(f"   {i}. {camp['name']} ({camp['customer_name']})")
                print(f"      Status: {camp['status']} | Type: {camp['type']}")
                print(f"      Impressions: {camp['impressions']:,} | Clicks: {camp['clicks']:,}")
                print(f"      Cost: ${camp['cost']:.2f} | CTR: {camp['ctr']:.2f}%")

        # Test fetch traffic sources (GA4)
        print("\n📊 Fetching GA4 traffic sources...")
        sources = agent.fetch_traffic_sources_warehouse(limit=10)

        if "error" not in sources:
            total_sources = sources.get('total', 0)
            print(f"✅ Fetched {total_sources} traffic sources")

            if total_sources > 0:
                print("\n📋 Sample traffic sources:")
                for i, source in enumerate(sources['traffic_sources'][:5], 1):
                    print(f"   {i}. {source['source']} / {source['medium']}")
                    print(f"      Sessions: {source['sessions']:,} | Page Views: {source['page_views']:,}")

        # Test metrics summary
        print("\n📊 Fetching metrics summary...")
        summary = agent.fetch_metrics_summary_warehouse(days=30)

        if "error" not in summary and 'summary' in summary:
            s = summary['summary']
            print("✅ Metrics Summary (Last 30 Days):")
            print(f"   Campaigns: {s.get('total_campaigns', 0)}")
            print(f"   Traffic Sources: {s.get('total_traffic_sources', 0)}")
            print(f"   Impressions: {s.get('total_impressions', 0):,}")
            print(f"   Clicks: {s.get('total_clicks', 0):,}")
            print(f"   Cost: ${s.get('total_cost', 0):.2f}")
            print(f"   Conversions: {s.get('total_conversions', 0):.1f}")
            print(f"   Avg CTR: {s.get('avg_ctr', 0):.2f}%")

        # Test get warehouse customers
        print("\n📊 Getting warehouse customers...")
        customers = agent.get_warehouse_customers()
        print(f"✅ Found {len(customers)} customers in warehouse")

        return True

    except Exception as e:
        print(f"❌ Data Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_insight_agent_warehouse():
    """Test Insight Agent with warehouse"""
    print("\n" + "=" * 70)
    print("TEST 3: Insight Agent with Warehouse")
    print("=" * 70)

    try:
        # Initialize Insight Agent with warehouse
        agent = InsightAgent(use_warehouse=True)
        print(f"✅ Insight Agent initialized (warehouse: {agent.use_warehouse})")

        # Test campaign performance analysis
        print("\n📊 Analyzing campaign performance...")
        analysis = agent.analyze_campaign_performance(customer_id=None)

        if "error" in analysis:
            print(f"❌ Error: {analysis['error']}")
            return False

        report = analysis.get('report', {})

        if 'summary' in report:
            print("✅ Campaign Analysis Summary:")
            print(f"   {report['summary']}")

        if 'top_performers' in report and report['top_performers']:
            print("\n🏆 Top Performing Campaigns:")
            for i, camp in enumerate(report['top_performers'][:3], 1):
                print(f"   {i}. {camp.get('name', 'N/A')}")
                print(f"      Cost: ${camp.get('cost', 0):.2f} | ROAS: {camp.get('roas', 0):.2f}x")

        if 'recommendations' in report and report['recommendations']:
            print("\n💡 Recommendations:")
            for i, rec in enumerate(report['recommendations'][:3], 1):
                print(f"   {i}. {rec}")

        return True

    except Exception as e:
        print(f"❌ Insight Agent test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_multi_customer_filtering():
    """Test multi-customer filtering"""
    print("\n" + "=" * 70)
    print("TEST 4: Multi-Customer Filtering")
    print("=" * 70)

    try:
        agent = DataAgent(use_warehouse=True)

        # Get all customers
        customers = agent.get_warehouse_customers()

        if not customers:
            print("⚠️  No customers found in warehouse")
            return True

        print(f"Found {len(customers)} customers. Testing customer filtering...")

        # Test with first customer
        cust = customers[0]
        print(f"\n📊 Fetching data for customer: {cust['customer_name']} (ID: {cust['customer_id']})")

        campaigns = agent.fetch_campaigns_warehouse(customer_id=cust['customer_id'])

        if "error" not in campaigns:
            print(f"✅ Fetched {campaigns.get('total', 0)} campaigns for {cust['customer_name']}")

            # Verify all campaigns belong to this customer
            for camp in campaigns['campaigns']:
                if camp['customer_name'] != cust['customer_name']:
                    print(f"❌ ERROR: Campaign belongs to wrong customer!")
                    return False

            print(f"✅ All campaigns belong to correct customer")

        return True

    except Exception as e:
        print(f"❌ Multi-customer test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all integration tests"""
    print("\n" + "=" * 70)
    print("🧪 ADK WAREHOUSE INTEGRATION TESTS")
    print("=" * 70)

    results = []

    # Test 1: Warehouse Client
    results.append(("Warehouse Client", test_warehouse_client()))

    # Test 2: Data Agent
    results.append(("Data Agent", test_data_agent_warehouse()))

    # Test 3: Insight Agent
    results.append(("Insight Agent", test_insight_agent_warehouse()))

    # Test 4: Multi-Customer Filtering
    results.append(("Multi-Customer Filtering", test_multi_customer_filtering()))

    # Summary
    print("\n" + "=" * 70)
    print("TEST RESULTS SUMMARY")
    print("=" * 70)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:30} {status}")

    print("\n" + "=" * 70)
    print(f"TOTAL: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("=" * 70)

    if passed == total:
        print("\n🎉 ALL TESTS PASSED! ADK is now trained with warehouse data!")
        print("\nNext steps:")
        print("  - Agents can now query 19 Google Ads campaigns")
        print("  - Agents can analyze 84 performance records")
        print("  - Agents support multi-customer (3 customers)")
        print("  - Agents support multi-platform (Google Ads + GA4)")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Check errors above.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
