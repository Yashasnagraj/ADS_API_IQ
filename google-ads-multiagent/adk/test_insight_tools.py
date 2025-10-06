"""
Comprehensive Testing Script for InsightAgent Tools
Tests query parsing and all tool functionality
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from loguru import logger
from datetime import datetime
import json
from typing import Dict, Any, List

# Import the InsightAgent components
from orchestration_agent.sub_agents.insight_agent.tools import (
    PerformanceAnalyzer,
    TrendAnalyzer,
    ROICalculator,
    CompetitorAnalysis,
    AnomalyDetector,
    get_tool_registry
)


class InsightToolsTester:
    """Test all InsightAgent tools with various queries"""

    def __init__(self):
        """Initialize tester with tool registry"""
        self.tool_registry = get_tool_registry()
        self.test_results = {
            'timestamp': datetime.now().isoformat(),
            'tests_passed': 0,
            'tests_failed': 0,
            'details': []
        }

        # Sample test queries covering all tool scenarios
        self.test_queries = {
            'performance': [
                "Show me campaign performance for the last 30 days",
                "What are my top performing campaigns?",
                "Analyze campaign metrics with CTR above 3%",
                "Show underperforming campaigns with CPC below $5"
            ],
            'trends': [
                "What are the trends in conversions over the past month?",
                "Show me seasonality patterns in impressions",
                "Forecast next week's performance",
                "Analyze keyword trends for top 10 keywords"
            ],
            'roi': [
                "Calculate ROI for all campaigns",
                "What's my ROAS for the last quarter?",
                "Show profit margins by campaign",
                "Which campaigns are unprofitable?"
            ],
            'competitor': [
                "How do I compare to competitors?",
                "Show auction insights analysis",
                "What's my impression share vs market?",
                "Analyze competitive positioning"
            ],
            'anomaly': [
                "Detect any unusual spikes in spend",
                "Are there any anomalies in conversion rates?",
                "Alert me to outliers in campaign performance",
                "Find unusual patterns in click data"
            ],
            'complex': [
                "Analyze performance trends and calculate ROI for campaigns with anomalies",
                "Compare my performance to competitors and show optimization opportunities",
                "Forecast next month's conversions and identify risk factors",
                "Show me everything about campaign performance including trends and anomalies"
            ]
        }

        logger.info("InsightToolsTester initialized")

    def test_query_parsing(self) -> Dict[str, Any]:
        """Test query parsing functionality"""
        print("\n" + "="*60)
        print("TESTING QUERY PARSING")
        print("="*60)

        parsing_results = []

        for category, queries in self.test_queries.items():
            print(f"\n📊 Testing {category.upper()} queries:")
            print("-" * 40)

            for query in queries:
                try:
                    parsed = self.tool_registry.parse_query(query)

                    print(f"\n📝 Query: '{query[:50]}...'")
                    print(f"   ✅ Intents detected: {parsed['intents']}")
                    print(f"   📅 Date range: {parsed['parameters']['date_range']}")
                    print(f"   📈 Metrics: {parsed['parameters']['metrics'][:3] if parsed['parameters']['metrics'] else 'default'}")

                    parsing_results.append({
                        'query': query,
                        'category': category,
                        'parsed': parsed,
                        'status': 'success'
                    })

                except Exception as e:
                    print(f"   ❌ Error parsing: {str(e)}")
                    parsing_results.append({
                        'query': query,
                        'category': category,
                        'error': str(e),
                        'status': 'failed'
                    })

        # Summary
        successful = len([r for r in parsing_results if r['status'] == 'success'])
        failed = len([r for r in parsing_results if r['status'] == 'failed'])

        print(f"\n📊 Parsing Summary: {successful} successful, {failed} failed")

        return {
            'total': len(parsing_results),
            'successful': successful,
            'failed': failed,
            'results': parsing_results
        }

    def test_individual_tools(self) -> Dict[str, Any]:
        """Test each tool individually with mock data"""
        print("\n" + "="*60)
        print("TESTING INDIVIDUAL TOOLS")
        print("="*60)

        tool_results = {}

        # Test PerformanceAnalyzer
        print("\n🔧 Testing PerformanceAnalyzer:")
        print("-" * 40)
        try:
            analyzer = PerformanceAnalyzer()

            # Test with mock campaign data
            mock_campaign = {
                'campaigns': [
                    {
                        'name': 'Test Campaign 1',
                        'impressions': 10000,
                        'clicks': 500,
                        'conversions': 50,
                        'cost': 1000,
                        'ctr': 5.0,
                        'cpc': 2.0,
                        'conversion_rate': 10.0,
                        'roas': 5.0
                    }
                ]
            }

            result = analyzer.analyze_campaign_performance(
                campaign_data=mock_campaign,
                performance_threshold={'min_ctr': 3.0, 'max_cpc': 5.0}
            )

            if result and 'error' not in result:
                print("   ✅ PerformanceAnalyzer: Working")
                tool_results['PerformanceAnalyzer'] = 'success'
            else:
                print(f"   ⚠️ PerformanceAnalyzer: {result.get('error', 'Unknown error')}")
                tool_results['PerformanceAnalyzer'] = 'warning'

        except Exception as e:
            print(f"   ❌ PerformanceAnalyzer: {str(e)}")
            tool_results['PerformanceAnalyzer'] = 'failed'

        # Test TrendAnalyzer
        print("\n🔧 Testing TrendAnalyzer:")
        print("-" * 40)
        try:
            trend_analyzer = TrendAnalyzer()

            # Generate mock time series data
            import pandas as pd
            from datetime import timedelta

            dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
            mock_time_series = [
                {
                    'date': date.strftime('%Y-%m-%d'),
                    'impressions': 5000 + i * 100,
                    'clicks': 250 + i * 5,
                    'conversions': 25 + i * 2,
                    'cost': 500 + i * 20,
                    'ctr': 5.0 + i * 0.1,
                    'conversion_rate': 10.0 + i * 0.2
                }
                for i, date in enumerate(dates)
            ]

            result = trend_analyzer.analyze_performance_trends(
                performance_data=mock_time_series,
                metrics=['impressions', 'clicks', 'conversions'],
                period='daily'
            )

            if result and 'error' not in result:
                print("   ✅ TrendAnalyzer: Working")
                if 'metrics' in result:
                    print(f"      Analyzed {len(result['metrics'])} metrics")
                tool_results['TrendAnalyzer'] = 'success'
            else:
                print(f"   ⚠️ TrendAnalyzer: {result.get('error', 'Unknown error')}")
                tool_results['TrendAnalyzer'] = 'warning'

        except Exception as e:
            print(f"   ❌ TrendAnalyzer: {str(e)}")
            tool_results['TrendAnalyzer'] = 'failed'

        # Test ROICalculator
        print("\n🔧 Testing ROICalculator:")
        print("-" * 40)
        try:
            roi_calc = ROICalculator()

            mock_campaigns = [
                {
                    'name': f'Campaign {i}',
                    'cost': 1000 * (i + 1),
                    'conversions': 50 * (i + 1),
                    'conversion_value': 2500 * (i + 1)
                }
                for i in range(5)
            ]

            result = roi_calc.calculate_campaign_roi(
                campaign_data=mock_campaigns,
                conversion_value=50.0
            )

            if result and 'error' not in result:
                print("   ✅ ROICalculator: Working")
                if 'overall_metrics' in result:
                    print(f"      ROI: {result['overall_metrics'].get('roi_percentage', 'N/A')}%")
                tool_results['ROICalculator'] = 'success'
            else:
                print(f"   ⚠️ ROICalculator: {result.get('error', 'Unknown error')}")
                tool_results['ROICalculator'] = 'warning'

        except Exception as e:
            print(f"   ❌ ROICalculator: {str(e)}")
            tool_results['ROICalculator'] = 'failed'

        # Test CompetitorAnalysis
        print("\n🔧 Testing CompetitorAnalysis:")
        print("-" * 40)
        try:
            comp_analyzer = CompetitorAnalysis()

            mock_auction_data = [
                {
                    'domain': f'competitor{i}.com',
                    'impression_share': 20.0 + i * 5,
                    'overlap_rate': 40.0 + i * 10,
                    'outranking_share': 50.0 - i * 5,
                    'top_of_page_rate': 60.0 + i * 5,
                    'is_you': i == 0
                }
                for i in range(5)
            ]

            result = comp_analyzer.analyze_auction_insights(
                auction_data=mock_auction_data,
                competitor_domains=['competitor1.com', 'competitor2.com']
            )

            if result and 'error' not in result:
                print("   ✅ CompetitorAnalysis: Working")
                if 'summary' in result:
                    print(f"      Analyzed {len(mock_auction_data)} competitors")
                tool_results['CompetitorAnalysis'] = 'success'
            else:
                print(f"   ⚠️ CompetitorAnalysis: {result.get('error', 'Unknown error')}")
                tool_results['CompetitorAnalysis'] = 'warning'

        except Exception as e:
            print(f"   ❌ CompetitorAnalysis: {str(e)}")
            tool_results['CompetitorAnalysis'] = 'failed'

        # Test AnomalyDetector
        print("\n🔧 Testing AnomalyDetector:")
        print("-" * 40)
        try:
            anomaly_detector = AnomalyDetector()

            # Create data with anomalies
            normal_data = [
                {
                    'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d'),
                    'impressions': 5000 + (i % 7) * 100,
                    'clicks': 250 + (i % 7) * 10,
                    'conversions': 25 + (i % 7) * 2,
                    'cost': 500 + (i % 7) * 20,
                    'ctr': 5.0,
                    'conversion_rate': 10.0
                }
                for i in range(28)
            ]

            # Add anomalies
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

            if result and 'error' not in result:
                print("   ✅ AnomalyDetector: Working")
                if 'anomalies' in result:
                    print(f"      Detected {len(result['anomalies'])} anomalies")
                tool_results['AnomalyDetector'] = 'success'
            else:
                print(f"   ⚠️ AnomalyDetector: {result.get('error', 'Unknown error')}")
                tool_results['AnomalyDetector'] = 'warning'

        except Exception as e:
            print(f"   ❌ AnomalyDetector: {str(e)}")
            tool_results['AnomalyDetector'] = 'failed'

        # Summary
        successful = len([v for v in tool_results.values() if v == 'success'])
        failed = len([v for v in tool_results.values() if v == 'failed'])
        warnings = len([v for v in tool_results.values() if v == 'warning'])

        print(f"\n📊 Tool Testing Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ⚠️ Warnings: {warnings}")
        print(f"   ❌ Failed: {failed}")

        return tool_results

    def test_tool_integration(self) -> Dict[str, Any]:
        """Test tool integration through the registry"""
        print("\n" + "="*60)
        print("TESTING TOOL INTEGRATION")
        print("="*60)

        integration_results = []

        # Test queries that should trigger specific tools
        test_cases = [
            {
                'query': "Show me campaign performance metrics",
                'expected_tool': 'performance',
                'tool_method': 'analyze_performance'
            },
            {
                'query': "What are the trends in my conversion rates?",
                'expected_tool': 'trends',
                'tool_method': 'analyze_trends'
            },
            {
                'query': "Calculate ROI for all campaigns",
                'expected_tool': 'roi',
                'tool_method': 'calculate_roi'
            },
            {
                'query': "How do I compare to competitors in auction insights?",
                'expected_tool': 'competitor',
                'tool_method': 'analyze_competitors'
            },
            {
                'query': "Detect anomalies in spending patterns",
                'expected_tool': 'anomaly',
                'tool_method': 'detect_anomalies'
            }
        ]

        for test_case in test_cases:
            print(f"\n🧪 Testing: '{test_case['query'][:50]}...'")
            print(f"   Expected tool: {test_case['expected_tool']}")

            try:
                # Parse query
                parsed = self.tool_registry.parse_query(test_case['query'])

                # Check if correct intent was detected
                if test_case['expected_tool'] in parsed['intents']:
                    print(f"   ✅ Correct intent detected")
                else:
                    print(f"   ⚠️ Intent mismatch. Detected: {parsed['intents']}")

                # Try to execute the tool
                if hasattr(self.tool_registry, test_case['tool_method']):
                    method = getattr(self.tool_registry, test_case['tool_method'])
                    result = method(test_case['query'])

                    if result and 'status' not in result or result.get('status') != 'error':
                        print(f"   ✅ Tool execution successful")
                        integration_results.append({
                            'query': test_case['query'],
                            'status': 'success',
                            'tool': test_case['expected_tool']
                        })
                    else:
                        print(f"   ⚠️ Tool execution warning: {result.get('message', 'Unknown')}")
                        integration_results.append({
                            'query': test_case['query'],
                            'status': 'warning',
                            'tool': test_case['expected_tool']
                        })
                else:
                    print(f"   ❌ Tool method not found: {test_case['tool_method']}")
                    integration_results.append({
                        'query': test_case['query'],
                        'status': 'failed',
                        'tool': test_case['expected_tool']
                    })

            except Exception as e:
                print(f"   ❌ Integration test failed: {str(e)}")
                integration_results.append({
                    'query': test_case['query'],
                    'status': 'failed',
                    'error': str(e)
                })

        # Test complex multi-tool query
        print("\n🧪 Testing complex multi-tool query:")
        complex_query = "Analyze performance trends, calculate ROI, and detect anomalies for all campaigns"

        try:
            parsed = self.tool_registry.parse_query(complex_query)
            print(f"   Query: '{complex_query[:50]}...'")
            print(f"   Detected intents: {parsed['intents']}")

            if len(parsed['intents']) >= 2:
                print(f"   ✅ Multiple intents detected correctly")
            else:
                print(f"   ⚠️ Expected multiple intents, got: {parsed['intents']}")

        except Exception as e:
            print(f"   ❌ Complex query parsing failed: {str(e)}")

        # Summary
        successful = len([r for r in integration_results if r['status'] == 'success'])
        warnings = len([r for r in integration_results if r['status'] == 'warning'])
        failed = len([r for r in integration_results if r['status'] == 'failed'])

        print(f"\n📊 Integration Testing Summary:")
        print(f"   ✅ Successful: {successful}")
        print(f"   ⚠️ Warnings: {warnings}")
        print(f"   ❌ Failed: {failed}")

        return {
            'results': integration_results,
            'summary': {
                'successful': successful,
                'warnings': warnings,
                'failed': failed
            }
        }

    def test_data_validation(self) -> Dict[str, Any]:
        """Test data validation and error handling"""
        print("\n" + "="*60)
        print("TESTING DATA VALIDATION & ERROR HANDLING")
        print("="*60)

        validation_results = []

        # Test cases with invalid data
        test_cases = [
            {
                'name': 'Empty data',
                'tool': PerformanceAnalyzer(),
                'method': 'analyze_campaign_performance',
                'data': {},
                'expected': 'handle_gracefully'
            },
            {
                'name': 'None data',
                'tool': TrendAnalyzer(),
                'method': 'analyze_performance_trends',
                'data': None,
                'expected': 'handle_gracefully'
            },
            {
                'name': 'Invalid data structure',
                'tool': ROICalculator(),
                'method': 'calculate_campaign_roi',
                'data': "invalid_string_data",
                'expected': 'handle_gracefully'
            },
            {
                'name': 'Missing required fields',
                'tool': CompetitorAnalysis(),
                'method': 'analyze_auction_insights',
                'data': [{'incomplete': 'data'}],
                'expected': 'handle_gracefully'
            }
        ]

        for test_case in test_cases:
            print(f"\n🧪 Testing: {test_case['name']}")

            try:
                method = getattr(test_case['tool'], test_case['method'])
                result = method(test_case['data'])

                if 'error' in result or (isinstance(result, dict) and result.get('status') == 'error'):
                    print(f"   ✅ Error handled gracefully")
                    validation_results.append({
                        'test': test_case['name'],
                        'status': 'success',
                        'handled': True
                    })
                else:
                    print(f"   ⚠️ Unexpected success with invalid data")
                    validation_results.append({
                        'test': test_case['name'],
                        'status': 'warning',
                        'result': result
                    })

            except Exception as e:
                print(f"   ❌ Unhandled exception: {str(e)[:100]}")
                validation_results.append({
                    'test': test_case['name'],
                    'status': 'failed',
                    'error': str(e)
                })

        # Test response validation
        print("\n🧪 Testing response validation:")

        valid_response = {
            'status': 'success',
            'report': {'data': 'valid'},
            'timestamp': datetime.now().isoformat()
        }

        invalid_response = {
            'error': 'Something went wrong',
            'status': 'error'
        }

        print(f"   Valid response: {self.tool_registry.validate_tool_response(valid_response)}")
        print(f"   Invalid response: {self.tool_registry.validate_tool_response(invalid_response)}")

        # Summary
        successful = len([r for r in validation_results if r['status'] == 'success'])
        warnings = len([r for r in validation_results if r['status'] == 'warning'])
        failed = len([r for r in validation_results if r['status'] == 'failed'])

        print(f"\n📊 Validation Testing Summary:")
        print(f"   ✅ Handled gracefully: {successful}")
        print(f"   ⚠️ Warnings: {warnings}")
        print(f"   ❌ Failed: {failed}")

        return {
            'results': validation_results,
            'summary': {
                'successful': successful,
                'warnings': warnings,
                'failed': failed
            }
        }

    def run_all_tests(self) -> Dict[str, Any]:
        """Run all tests and generate comprehensive report"""
        print("\n" + "="*80)
        print(" COMPREHENSIVE INSIGHTAGENT TOOLS TESTING ")
        print("="*80)
        print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        all_results = {
            'timestamp': datetime.now().isoformat(),
            'tests': {}
        }

        # Run all test suites
        print("\n🚀 Starting comprehensive testing suite...")

        # 1. Query Parsing Tests
        all_results['tests']['query_parsing'] = self.test_query_parsing()

        # 2. Individual Tool Tests
        all_results['tests']['individual_tools'] = self.test_individual_tools()

        # 3. Tool Integration Tests
        all_results['tests']['tool_integration'] = self.test_tool_integration()

        # 4. Data Validation Tests
        all_results['tests']['data_validation'] = self.test_data_validation()

        # Generate final report
        print("\n" + "="*80)
        print(" FINAL TEST REPORT ")
        print("="*80)

        total_tests = 0
        total_passed = 0
        total_failed = 0

        for test_suite, results in all_results['tests'].items():
            if isinstance(results, dict):
                if 'successful' in results:
                    passed = results.get('successful', 0)
                    failed = results.get('failed', 0)
                    total = results.get('total', passed + failed)
                elif 'summary' in results:
                    passed = results['summary'].get('successful', 0)
                    failed = results['summary'].get('failed', 0)
                    total = passed + failed + results['summary'].get('warnings', 0)
                else:
                    # For tool results
                    passed = len([v for v in results.values() if v == 'success'])
                    failed = len([v for v in results.values() if v == 'failed'])
                    total = len(results)

                total_tests += total
                total_passed += passed
                total_failed += failed

                print(f"\n📊 {test_suite.replace('_', ' ').title()}:")
                print(f"   Total: {total}")
                print(f"   Passed: {passed}")
                print(f"   Failed: {failed}")

                if total > 0:
                    success_rate = (passed / total) * 100
                    print(f"   Success Rate: {success_rate:.1f}%")

        # Overall summary
        print("\n" + "-"*40)
        print("📈 OVERALL RESULTS:")
        print(f"   Total Tests: {total_tests}")
        print(f"   Passed: {total_passed}")
        print(f"   Failed: {total_failed}")

        if total_tests > 0:
            overall_success_rate = (total_passed / total_tests) * 100
            print(f"   Overall Success Rate: {overall_success_rate:.1f}%")

            if overall_success_rate >= 90:
                print("\n✅ EXCELLENT: System is production-ready!")
            elif overall_success_rate >= 75:
                print("\n⚠️ GOOD: System is mostly functional with minor issues")
            elif overall_success_rate >= 50:
                print("\n⚠️ NEEDS ATTENTION: Several components need fixing")
            else:
                print("\n❌ CRITICAL: Major issues detected, immediate attention required")

        print(f"\nCompleted at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("="*80)

        all_results['summary'] = {
            'total_tests': total_tests,
            'passed': total_passed,
            'failed': total_failed,
            'success_rate': (total_passed / total_tests * 100) if total_tests > 0 else 0
        }

        return all_results


def main():
    """Main execution function"""
    print("\n🚀 InsightAgent Tools Testing Suite")
    print("Ready for billion-dollar company demo standards")
    print("-"*50)

    try:
        tester = InsightToolsTester()
        results = tester.run_all_tests()

        # Save results to file
        output_file = f"test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)

        print(f"\n📁 Detailed results saved to: {output_file}")

        return results

    except Exception as e:
        print(f"\n❌ Critical error during testing: {str(e)}")
        logger.error(f"Testing failed: {e}", exc_info=True)
        return None


if __name__ == "__main__":
    results = main()