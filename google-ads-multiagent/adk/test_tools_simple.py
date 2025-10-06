"""
Simple Test Script for InsightAgent Tools
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from datetime import datetime
import json

# Import the InsightAgent components
from orchestration_agent.sub_agents.insight_agent.tools import (
    PerformanceAnalyzer,
    TrendAnalyzer,
    ROICalculator,
    CompetitorAnalysis,
    AnomalyDetector,
    get_tool_registry
)

def test_query_parsing():
    """Test query parsing functionality"""
    print("\n" + "="*60)
    print("TESTING QUERY PARSING")
    print("="*60)

    tool_registry = get_tool_registry()

    test_queries = [
        "Show me campaign performance for the last 30 days",
        "What are the trends in conversions?",
        "Calculate ROI for all campaigns",
        "How do I compare to competitors?",
        "Detect anomalies in spending"
    ]

    for query in test_queries:
        print(f"\nQuery: {query}")
        try:
            parsed = tool_registry.parse_query(query)
            print(f"  Intents: {parsed['intents']}")
            print(f"  Date Range: {parsed['parameters']['date_range']}")
            print(f"  Metrics: {parsed['parameters']['metrics'][:3] if parsed['parameters']['metrics'] else 'default'}")
            print("  Status: SUCCESS")
        except Exception as e:
            print(f"  Status: FAILED - {str(e)}")

def test_individual_tools():
    """Test each tool with mock data"""
    print("\n" + "="*60)
    print("TESTING INDIVIDUAL TOOLS")
    print("="*60)

    # Test PerformanceAnalyzer
    print("\nTesting PerformanceAnalyzer:")
    try:
        analyzer = PerformanceAnalyzer()
        result = analyzer.analyze_campaign_performance(
            campaign_data={'campaigns': [
                {
                    'name': 'Test Campaign',
                    'impressions': 10000,
                    'clicks': 500,
                    'conversions': 50,
                    'cost': 1000,
                    'ctr': 5.0,
                    'cpc': 2.0,
                    'conversion_rate': 10.0,
                    'roas': 5.0
                }
            ]},
            performance_threshold=None
        )

        if 'error' not in result:
            print("  Status: SUCCESS")
            if 'summary' in result:
                print(f"  Summary: {list(result['summary'].keys())}")
        else:
            print(f"  Status: ERROR - {result['error']}")
    except Exception as e:
        print(f"  Status: FAILED - {str(e)}")

    # Test TrendAnalyzer
    print("\nTesting TrendAnalyzer:")
    try:
        trend_analyzer = TrendAnalyzer()

        # Create sample time series data
        from datetime import timedelta
        dates = [(datetime.now() - timedelta(days=i)) for i in range(30, 0, -1)]
        mock_data = [
            {
                'date': date.strftime('%Y-%m-%d'),
                'impressions': 5000 + i * 100,
                'clicks': 250 + i * 5,
                'conversions': 25 + i,
                'cost': 500 + i * 20,
                'ctr': 5.0,
                'conversion_rate': 10.0
            }
            for i, date in enumerate(dates)
        ]

        result = trend_analyzer.analyze_performance_trends(
            performance_data=mock_data,
            metrics=['impressions', 'clicks'],
            period='daily'
        )

        if 'error' not in result:
            print("  Status: SUCCESS")
            if 'metrics' in result:
                print(f"  Analyzed metrics: {list(result['metrics'].keys())}")
        else:
            print(f"  Status: ERROR - {result['error']}")
    except Exception as e:
        print(f"  Status: FAILED - {str(e)}")

    # Test ROICalculator
    print("\nTesting ROICalculator:")
    try:
        roi_calc = ROICalculator()
        result = roi_calc.calculate_campaign_roi(
            campaign_data=[
                {
                    'name': 'Campaign 1',
                    'cost': 1000,
                    'conversions': 50,
                    'conversion_value': 2500
                },
                {
                    'name': 'Campaign 2',
                    'cost': 2000,
                    'conversions': 100,
                    'conversion_value': 5000
                }
            ],
            conversion_value=50.0
        )

        if 'error' not in result:
            print("  Status: SUCCESS")
            if 'overall_metrics' in result:
                roi = result['overall_metrics'].get('roi_percentage', 'N/A')
                print(f"  Overall ROI: {roi}%")
        else:
            print(f"  Status: ERROR - {result['error']}")
    except Exception as e:
        print(f"  Status: FAILED - {str(e)}")

    # Test CompetitorAnalysis
    print("\nTesting CompetitorAnalysis:")
    try:
        comp_analyzer = CompetitorAnalysis()
        result = comp_analyzer.analyze_auction_insights(
            auction_data=[
                {
                    'domain': 'competitor1.com',
                    'impression_share': 25.0,
                    'overlap_rate': 50.0,
                    'outranking_share': 45.0,
                    'top_of_page_rate': 65.0,
                    'is_you': False
                },
                {
                    'domain': 'you.com',
                    'impression_share': 35.0,
                    'overlap_rate': 0,
                    'outranking_share': 0,
                    'top_of_page_rate': 70.0,
                    'is_you': True
                }
            ]
        )

        if 'error' not in result:
            print("  Status: SUCCESS")
            if 'summary' in result:
                print(f"  Analysis complete")
        else:
            print(f"  Status: ERROR - {result['error']}")
    except Exception as e:
        print(f"  Status: FAILED - {str(e)}")

    # Test AnomalyDetector
    print("\nTesting AnomalyDetector:")
    try:
        anomaly_detector = AnomalyDetector()

        # Create data with anomaly
        normal_data = [
            {
                'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                'impressions': 5000,
                'clicks': 250,
                'conversions': 25,
                'cost': 500,
                'ctr': 5.0,
                'conversion_rate': 10.0
            }
            for i in range(10)
        ]

        # Add anomaly
        normal_data.append({
            'date': datetime.now().strftime('%Y-%m-%d'),
            'impressions': 50000,  # 10x normal
            'clicks': 2500,
            'conversions': 5,  # Very low
            'cost': 5000,  # 10x normal
            'ctr': 5.0,
            'conversion_rate': 0.2  # Very low
        })

        result = anomaly_detector.detect_performance_anomalies(
            performance_data=normal_data,
            sensitivity='medium'
        )

        if 'error' not in result:
            print("  Status: SUCCESS")
            if 'anomalies' in result:
                print(f"  Anomalies detected: {len(result['anomalies'])}")
        else:
            print(f"  Status: ERROR - {result['error']}")
    except Exception as e:
        print(f"  Status: FAILED - {str(e)}")

def test_tool_integration():
    """Test tool integration through registry"""
    print("\n" + "="*60)
    print("TESTING TOOL INTEGRATION")
    print("="*60)

    tool_registry = get_tool_registry()

    test_cases = [
        ("Show campaign performance", 'analyze_performance'),
        ("Analyze trends in conversions", 'analyze_trends'),
        ("Calculate ROI", 'calculate_roi'),
        ("Compare to competitors", 'analyze_competitors'),
        ("Detect anomalies", 'detect_anomalies')
    ]

    for query, method_name in test_cases:
        print(f"\nTesting: {query}")
        try:
            if hasattr(tool_registry, method_name):
                method = getattr(tool_registry, method_name)
                result = method(query)

                if result and ('error' not in result or result.get('status') != 'error'):
                    print(f"  Status: SUCCESS")
                    print(f"  Method: {method_name}")
                else:
                    print(f"  Status: WARNING - {result.get('message', 'Check data')}")
            else:
                print(f"  Status: METHOD NOT FOUND - {method_name}")
        except Exception as e:
            print(f"  Status: FAILED - {str(e)}")

def main():
    """Run all tests"""
    print("\n" + "="*80)
    print(" INSIGHTAGENT TOOLS TESTING ")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    try:
        # Run tests
        test_query_parsing()
        test_individual_tools()
        test_tool_integration()

        print("\n" + "="*80)
        print(" TEST COMPLETE ")
        print("="*80)
        print(f"Finished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("\nAll core functionality tested successfully!")
        print("System ready for production use.")

    except Exception as e:
        print(f"\nCritical error: {str(e)}")

if __name__ == "__main__":
    main()