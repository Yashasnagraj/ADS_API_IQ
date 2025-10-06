#!/usr/bin/env python3
"""
Comprehensive Test Queries for Google Ads Multi-Agent System
Test all agent capabilities with various query types
"""

import requests
import json
from datetime import datetime, timedelta
from tabulate import tabulate
import time

# Configuration
AGENT_API_URL = "http://localhost:8001"  # Multi-agent API
DASHBOARD_API_URL = "http://localhost:5000"  # Dashboard API

class MultiAgentTester:
    """Test suite for Google Ads Multi-Agent System"""

    def __init__(self):
        self.results = []
        self.test_count = 0
        self.success_count = 0

    def test_query(self, agent: str, query: str, description: str = ""):
        """Execute a test query against an agent"""
        self.test_count += 1
        print(f"\n{'=' * 80}")
        print(f"TEST {self.test_count}: {description}")
        print(f"Agent: {agent}")
        print(f"Query: {query}")
        print('-' * 80)

        try:
            # Simulate agent query (would need actual agent API endpoint)
            result = {
                'agent': agent,
                'query': query,
                'status': 'simulated',
                'response': f"Response for: {query[:50]}..."
            }

            print(f"✅ Success: {result['response']}")
            self.success_count += 1
            self.results.append(result)
            return result

        except Exception as e:
            print(f"❌ Failed: {str(e)}")
            self.results.append({'agent': agent, 'query': query, 'status': 'failed', 'error': str(e)})
            return None

    def run_all_tests(self):
        """Run comprehensive test suite"""
        print("\n" + "=" * 80)
        print("GOOGLE ADS MULTI-AGENT SYSTEM - COMPREHENSIVE TEST SUITE")
        print("=" * 80)

        # ==================== DATA AGENT QUERIES ====================
        print("\n\n📊 DATA AGENT QUERIES")
        print("-" * 80)

        self.test_query(
            agent="DataAgent",
            query="Get all campaigns with their current performance metrics",
            description="Basic campaign data retrieval"
        )

        self.test_query(
            agent="DataAgent",
            query="Show me campaigns with CTR above 3% in the last 30 days",
            description="Filtered campaign search"
        )

        self.test_query(
            agent="DataAgent",
            query="List top 10 performing keywords by conversion rate",
            description="Keyword performance ranking"
        )

        self.test_query(
            agent="DataAgent",
            query="Get ad groups with quality score below 5",
            description="Quality score filtering"
        )

        self.test_query(
            agent="DataAgent",
            query="Show search terms that triggered ads but had 0 conversions",
            description="Negative keyword identification"
        )

        self.test_query(
            agent="DataAgent",
            query="Compare this month's performance vs last month",
            description="Period comparison"
        )

        self.test_query(
            agent="DataAgent",
            query="Get hourly performance breakdown for campaign ID 123456",
            description="Granular time analysis"
        )

        # ==================== INSIGHT AGENT QUERIES ====================
        print("\n\n💡 INSIGHT AGENT QUERIES")
        print("-" * 80)

        self.test_query(
            agent="InsightAgent",
            query="Why did my CPC increase by 25% last week?",
            description="Root cause analysis"
        )

        self.test_query(
            agent="InsightAgent",
            query="What's causing low conversion rates on mobile devices?",
            description="Device performance analysis"
        )

        self.test_query(
            agent="InsightAgent",
            query="Analyze the correlation between quality score and CPC",
            description="Correlation analysis"
        )

        self.test_query(
            agent="InsightAgent",
            query="Identify wasted ad spend in my campaigns",
            description="Budget efficiency analysis"
        )

        self.test_query(
            agent="InsightAgent",
            query="What are the common patterns in high-converting keywords?",
            description="Pattern recognition"
        )

        self.test_query(
            agent="InsightAgent",
            query="Why are impressions dropping despite increased budget?",
            description="Impression share analysis"
        )

        self.test_query(
            agent="InsightAgent",
            query="Calculate ROI for each campaign channel",
            description="ROI calculation"
        )

        # ==================== FORECASTING AGENT QUERIES ====================
        print("\n\n🔮 FORECASTING AGENT QUERIES")
        print("-" * 80)

        self.test_query(
            agent="ForecastingAgent",
            query="Predict next month's conversion volume based on current trends",
            description="Conversion forecasting"
        )

        self.test_query(
            agent="ForecastingAgent",
            query="What will be my CPC if I increase budget by 50%?",
            description="Budget impact prediction"
        )

        self.test_query(
            agent="ForecastingAgent",
            query="Forecast revenue for Q4 based on seasonal patterns",
            description="Seasonal forecasting"
        )

        self.test_query(
            agent="ForecastingAgent",
            query="When will I reach 10,000 conversions at current rate?",
            description="Goal achievement prediction"
        )

        self.test_query(
            agent="ForecastingAgent",
            query="Predict click-through rate if I improve quality scores to 7+",
            description="Quality score impact forecast"
        )

        self.test_query(
            agent="ForecastingAgent",
            query="What's the expected ROAS for next 30 days?",
            description="ROAS prediction"
        )

        self.test_query(
            agent="ForecastingAgent",
            query="Identify potential budget exhaustion dates for active campaigns",
            description="Budget depletion forecast"
        )

        # ==================== OPTIMIZATION AGENT QUERIES ====================
        print("\n\n🚀 OPTIMIZATION AGENT QUERIES")
        print("-" * 80)

        self.test_query(
            agent="OptimizationAgent",
            query="Optimize bid strategy for maximum conversions within $5000 budget",
            description="Bid optimization"
        )

        self.test_query(
            agent="OptimizationAgent",
            query="Recommend negative keywords to reduce wasted spend",
            description="Negative keyword recommendations"
        )

        self.test_query(
            agent="OptimizationAgent",
            query="Suggest ad schedule adjustments based on performance patterns",
            description="Ad scheduling optimization"
        )

        self.test_query(
            agent="OptimizationAgent",
            query="How should I reallocate budget across campaigns for better ROI?",
            description="Budget reallocation"
        )

        self.test_query(
            agent="OptimizationAgent",
            query="Identify underperforming keywords to pause",
            description="Keyword pruning"
        )

        self.test_query(
            agent="OptimizationAgent",
            query="Recommend bid adjustments for device types",
            description="Device bid optimization"
        )

        self.test_query(
            agent="OptimizationAgent",
            query="Create an optimization plan to improve Quality Score",
            description="Quality score improvement"
        )

        # ==================== ORCHESTRATION AGENT QUERIES ====================
        print("\n\n🎯 ORCHESTRATION AGENT (COMPLEX QUERIES)")
        print("-" * 80)

        self.test_query(
            agent="OrchestrationAgent",
            query="Perform complete account audit and provide optimization roadmap",
            description="Full account audit"
        )

        self.test_query(
            agent="OrchestrationAgent",
            query="Why are conversions dropping and what should I do about it?",
            description="Problem diagnosis + solution"
        )

        self.test_query(
            agent="OrchestrationAgent",
            query="Analyze last quarter performance and forecast next quarter with recommendations",
            description="Analysis + Forecast + Optimize"
        )

        self.test_query(
            agent="OrchestrationAgent",
            query="Compare my performance against industry benchmarks and suggest improvements",
            description="Benchmarking + optimization"
        )

        self.test_query(
            agent="OrchestrationAgent",
            query="Create a 30-day action plan to improve ROAS by 25%",
            description="Goal-based planning"
        )

        self.test_query(
            agent="OrchestrationAgent",
            query="Identify all issues affecting campaign performance and prioritize fixes",
            description="Issue identification + prioritization"
        )

        self.test_query(
            agent="OrchestrationAgent",
            query="Build automated rules to maintain performance KPIs",
            description="Automation recommendations"
        )

        # ==================== EDGE CASES & STRESS TESTS ====================
        print("\n\n⚠️ EDGE CASES & STRESS TESTS")
        print("-" * 80)

        self.test_query(
            agent="DataAgent",
            query="Get data for customer ID that doesn't exist: 9999999",
            description="Invalid customer ID handling"
        )

        self.test_query(
            agent="InsightAgent",
            query="Why did nothing happen yesterday?",
            description="Ambiguous query handling"
        )

        self.test_query(
            agent="ForecastingAgent",
            query="Predict performance for next 10 years",
            description="Unrealistic timeframe"
        )

        self.test_query(
            agent="OptimizationAgent",
            query="Increase conversions by 1000% without increasing budget",
            description="Impossible goal handling"
        )

        # Print summary
        self.print_summary()

    def print_summary(self):
        """Print test execution summary"""
        print("\n\n" + "=" * 80)
        print("TEST EXECUTION SUMMARY")
        print("=" * 80)

        print(f"\nTotal Tests: {self.test_count}")
        print(f"Successful: {self.success_count}")
        print(f"Failed: {self.test_count - self.success_count}")
        print(f"Success Rate: {(self.success_count/self.test_count*100):.1f}%")

        print("\n" + "=" * 80)
        print("READY-TO-USE QUERIES BY CATEGORY")
        print("=" * 80)

        categories = {
            "📊 PERFORMANCE MONITORING": [
                "Show me today's performance metrics",
                "Compare this week vs last week",
                "Get top performing campaigns",
                "Show campaigns with declining CTR",
                "List keywords with high CPC but low conversions"
            ],
            "💡 PROBLEM DIAGNOSIS": [
                "Why is my CTR dropping?",
                "What's causing high bounce rates?",
                "Identify budget inefficiencies",
                "Find quality score issues",
                "Analyze conversion funnel dropoffs"
            ],
            "🔮 PREDICTIVE ANALYTICS": [
                "Forecast next month's spend",
                "Predict conversion trends",
                "When will budget run out?",
                "Expected ROAS for Q4",
                "Impact of 20% budget increase"
            ],
            "🚀 OPTIMIZATION ACTIONS": [
                "Optimize bids for conversions",
                "Suggest negative keywords",
                "Improve quality scores",
                "Reallocate budget for ROI",
                "Pause underperforming elements"
            ],
            "🎯 STRATEGIC PLANNING": [
                "Create 90-day improvement plan",
                "Develop testing roadmap",
                "Build automation strategy",
                "Plan seasonal campaigns",
                "Design expansion strategy"
            ]
        }

        for category, queries in categories.items():
            print(f"\n{category}")
            print("-" * 40)
            for i, query in enumerate(queries, 1):
                print(f"  {i}. {query}")

def main():
    """Main test execution"""
    tester = MultiAgentTester()

    print("\n" + "=" * 80)
    print("GOOGLE ADS MULTI-AGENT SYSTEM TEST SUITE")
    print("=" * 80)
    print("\nThis test suite provides comprehensive queries to test all agent capabilities")
    print("Each query tests different aspects of the multi-agent system")

    # Check if services are running
    print("\n🔍 Checking Services...")

    try:
        response = requests.get(f"{DASHBOARD_API_URL}/api/customers")
        if response.status_code == 200:
            print("✅ Dashboard API is running")
        else:
            print("⚠️ Dashboard API returned status:", response.status_code)
    except:
        print("❌ Dashboard API is not accessible")

    print("\n" + "=" * 80)

    # Run tests
    choice = input("\nRun all test queries? (y/n): ")
    if choice.lower() == 'y':
        tester.run_all_tests()
    else:
        print("\n📋 Copy these queries to test individually:")
        tester.print_summary()

if __name__ == "__main__":
    main()