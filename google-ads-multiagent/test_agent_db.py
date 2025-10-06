"""
Test script to verify agent database connectivity and data fetching
"""
import sys
import os
import io

# Set stdout to handle Unicode
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'adk'))

from adk.orchestration_agent.sub_agents.data_agent.db_client import DatabaseClient
from adk.orchestration_agent.sub_agents.insight_agent.insight_agent import InsightAgent


def test_database_connection():
    """Test direct database connection"""
    print("\n" + "="*60)
    print("Testing Database Connection")
    print("="*60)

    try:
        db_client = DatabaseClient()

        # Test fetching campaigns
        print("\n1. Testing fetch_campaigns()...")
        campaigns = db_client.fetch_campaigns(limit=5)

        if "error" in campaigns:
            print(f"   ❌ Error: {campaigns['error']}")
        else:
            print(f"   ✅ Success! Fetched {len(campaigns.get('campaigns', []))} campaigns")
            if campaigns.get('campaigns'):
                campaign = campaigns['campaigns'][0]
                print(f"   Sample campaign: {campaign.get('name')} - Cost: ${campaign.get('cost', 0):.2f}")

        # Test fetching keywords
        print("\n2. Testing fetch_keywords()...")
        keywords = db_client.fetch_keywords(limit=5)

        if "error" in keywords:
            print(f"   ❌ Error: {keywords['error']}")
        else:
            print(f"   ✅ Success! Fetched {len(keywords.get('keywords', []))} keywords")
            if keywords.get('keywords'):
                keyword = keywords['keywords'][0]
                print(f"   Sample keyword: {keyword.get('text')} - QS: {keyword.get('quality_score', 0)}")

        # Test fetching search terms
        print("\n3. Testing fetch_search_terms()...")
        search_terms = db_client.fetch_search_terms(limit=5)

        if "error" in search_terms:
            print(f"   ❌ Error: {search_terms['error']}")
        else:
            print(f"   ✅ Success! Fetched {len(search_terms.get('search_terms', []))} search terms")
            if search_terms.get('search_terms'):
                term = search_terms['search_terms'][0]
                print(f"   Sample term: {term.get('search_term')} - Cost: ${term.get('cost', 0):.2f}")

        # Test fetching ML features
        print("\n4. Testing fetch_ml_features()...")
        ml_features = db_client.fetch_ml_features(entity_type="campaign")

        if "error" in ml_features:
            print(f"   ❌ Error: {ml_features['error']}")
        else:
            print(f"   ✅ Success! Fetched {len(ml_features.get('features', []))} ML features")
            if ml_features.get('features'):
                feature = ml_features['features'][0]
                print(f"   Sample feature: Campaign {feature.get('campaign_name')} - CTR: {feature.get('ctr', 0):.2f}%")

        # Test fetching metrics summary
        print("\n5. Testing fetch_metrics_summary()...")
        metrics = db_client.fetch_metrics_summary()

        if "error" in metrics:
            print(f"   ❌ Error: {metrics['error']}")
        else:
            print(f"   ✅ Success! Fetched metrics summary")
            summary = metrics.get('summary', {})
            print(f"   Total campaigns: {summary.get('total_campaigns', 0)}")
            print(f"   Total cost: ${summary.get('total_cost', 0):.2f}")
            print(f"   Avg CTR: {summary.get('avg_ctr', 0):.2f}%")

        return True

    except Exception as e:
        print(f"\n❌ Database connection test failed: {str(e)}")
        return False


def test_insight_agent():
    """Test InsightAgent functionality"""
    print("\n" + "="*60)
    print("Testing InsightAgent")
    print("="*60)

    try:
        agent = InsightAgent()

        # Test campaign performance analysis
        print("\n1. Testing analyze_campaign_performance()...")
        result = agent.analyze_campaign_performance()

        if result.get('status') == 'success':
            print(f"   ✅ Success!")
            report = result.get('report', {})
            summary = report.get('summary', {})
            print(f"   Total campaigns: {summary.get('total_campaigns', 0)}")
            print(f"   Total spend: ${summary.get('total_spend', 0):.2f}")
            print(f"   Top performers: {len(report.get('top_performers', []))}")
            print(f"   Recommendations: {len(report.get('recommendations', []))}")
        else:
            print(f"   ❌ Error: {result.get('message', 'Unknown error')}")

        # Test keyword performance analysis
        print("\n2. Testing analyze_keyword_performance()...")
        result = agent.analyze_keyword_performance()

        if result.get('status') == 'success':
            print(f"   ✅ Success!")
            report = result.get('report', {})
            summary = report.get('summary', {})
            print(f"   Total keywords: {summary.get('total_keywords', 0)}")
            print(f"   Avg quality score: {summary.get('avg_quality_score', 0)}")
            print(f"   Wasted spend: ${summary.get('total_wasted_spend', 0):.2f}")
        else:
            print(f"   ❌ Error: {result.get('message', 'Unknown error')}")

        # Test anomaly detection
        print("\n3. Testing detect_anomalies()...")
        result = agent.detect_anomalies()

        if result.get('status') == 'success':
            print(f"   ✅ Success!")
            anomalies = result.get('anomalies', [])
            print(f"   Total anomalies detected: {len(anomalies)}")
            if anomalies:
                anomaly = anomalies[0]
                print(f"   Sample anomaly: {anomaly.get('type')} - {anomaly.get('entity')}")
        else:
            print(f"   ❌ Error: {result.get('message', 'Unknown error')}")

        # Test ROI calculation
        print("\n4. Testing calculate_roi()...")
        result = agent.calculate_roi()

        if result.get('status') == 'success':
            print(f"   ✅ Success!")
            roi_analysis = result.get('roi_analysis', {})
            overall = roi_analysis.get('overall', {})
            print(f"   Total spend: ${overall.get('total_spend', 0):.2f}")
            print(f"   Total revenue: ${overall.get('total_revenue', 0):.2f}")
            print(f"   ROI: {overall.get('roi_percentage', 0):.2f}%")
            print(f"   ROAS: {overall.get('roas', 0):.2f}x")
        else:
            print(f"   ❌ Error: {result.get('message', 'Unknown error')}")

        return True

    except Exception as e:
        print(f"\n❌ InsightAgent test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "#"*60)
    print("#" + " "*20 + "AGENT DATABASE TESTS" + " "*18 + "#")
    print("#"*60)

    # Test database connection
    db_success = test_database_connection()

    # Test InsightAgent
    agent_success = test_insight_agent()

    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"Database Connection: {'✅ PASSED' if db_success else '❌ FAILED'}")
    print(f"InsightAgent: {'✅ PASSED' if agent_success else '❌ FAILED'}")

    if db_success and agent_success:
        print("\n🎉 All tests passed successfully!")
    else:
        print("\n⚠️  Some tests failed. Please check the output above.")


if __name__ == "__main__":
    main()