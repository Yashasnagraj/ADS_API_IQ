"""
Enhanced Orchestration Agent with Retry Logic and Error Handling
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import requests
from google.adk.agents import Agent
import time

logger = logging.getLogger(__name__)

# API Configuration
API_BASE_URL = "http://localhost:8003"
MAX_RETRIES = 3
RETRY_DELAY = 2  # seconds

def make_api_request_with_retry(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Make a request to the API endpoint with retry logic.
    """
    for attempt in range(MAX_RETRIES):
        try:
            url = f"{API_BASE_URL}{endpoint}"
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.warning(f"API request attempt {attempt + 1} failed: {str(e)}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(RETRY_DELAY)
            else:
                logger.error(f"API request failed after {MAX_RETRIES} attempts")
                return {
                    "error": f"API unavailable after {MAX_RETRIES} attempts",
                    "status": "failed",
                    "fallback_data": True
                }

# Wrapper functions with fallback data
def get_campaign_performance(customer_id: str = None) -> Dict[str, Any]:
    """
    Retrieve campaign performance data with fallback.
    """
    result = make_api_request_with_retry("/campaigns")

    # If API fails, return sample data for demonstration
    if "error" in result and result.get("fallback_data"):
        logger.info("Using fallback sample data for demonstration")
        return {
            "status": "success",
            "customer_id": customer_id or "sample",
            "note": "Using sample data (API temporarily unavailable)",
            "campaigns": [
                {
                    "campaign_id": 1,
                    "campaign_name": "Sample Campaign 1",
                    "status": "ENABLED",
                    "impressions": 10000,
                    "clicks": 500,
                    "cost": 250.00,
                    "conversions": 25,
                    "ctr": 5.0,
                    "average_cpc": 0.50,
                    "roas": 4.0
                },
                {
                    "campaign_id": 2,
                    "campaign_name": "Sample Campaign 2",
                    "status": "ENABLED",
                    "impressions": 5000,
                    "clicks": 150,
                    "cost": 100.00,
                    "conversions": 10,
                    "ctr": 3.0,
                    "average_cpc": 0.67,
                    "roas": 2.5
                }
            ]
        }

    if "error" not in result:
        summary = make_api_request_with_retry("/metrics/summary")
        return {
            "status": "success",
            "customer_id": customer_id or "all",
            "campaigns": result,
            "summary": summary
        }
    return result

def optimize_bids_with_fallback(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate bid optimization recommendations with fallback logic.
    """
    campaigns = make_api_request_with_retry("/campaigns")

    # Use fallback logic if API is unavailable
    if "error" in campaigns:
        # Provide recommendations based on general best practices
        return {
            "status": "success",
            "note": "Generated recommendations based on best practices (API temporarily unavailable)",
            "recommendations": [
                {
                    "campaign_name": "High-Converting Campaigns",
                    "recommended_action": "increase_bid",
                    "recommended_bid_adjustment": "+15-20%",
                    "rationale": "Campaigns with conversion rates above 5% typically benefit from increased bids to capture more traffic"
                },
                {
                    "campaign_name": "Low-Performing Campaigns",
                    "recommended_action": "decrease_bid",
                    "recommended_bid_adjustment": "-20-30%",
                    "rationale": "Campaigns with CTR below 1% and high CPC should have reduced bids to improve efficiency"
                },
                {
                    "campaign_name": "Testing Strategy",
                    "recommended_action": "test_smart_bidding",
                    "rationale": "Consider testing Target CPA or Target ROAS strategies for automated optimization"
                }
            ],
            "general_tips": [
                "Review Quality Score and improve ad relevance",
                "Test different bid strategies (Manual CPC, Enhanced CPC, Target CPA)",
                "Adjust bids by device, location, and time of day",
                "Monitor search term reports for negative keyword opportunities"
            ]
        }

    # Process real data if available
    recommendations = []
    for campaign in campaigns:
        if isinstance(campaign, dict):
            cpc = campaign.get('average_cpc', 0)
            conversions = campaign.get('conversions', 0)
            clicks = campaign.get('clicks', 0)
            conv_rate = (conversions / clicks * 100) if clicks > 0 else 0

            if conv_rate > 5:
                recommendations.append({
                    "campaign_id": campaign.get('campaign_id'),
                    "campaign_name": campaign.get('campaign_name'),
                    "current_avg_cpc": round(cpc, 2),
                    "recommended_action": "increase_bid",
                    "recommended_bid_adjustment": "+20%",
                    "rationale": f"High conversion rate ({conv_rate:.2f}%) - increase bids to capture more traffic"
                })
            elif conv_rate < 1 and cpc > 2:
                recommendations.append({
                    "campaign_id": campaign.get('campaign_id'),
                    "campaign_name": campaign.get('campaign_name'),
                    "current_avg_cpc": round(cpc, 2),
                    "recommended_action": "decrease_bid",
                    "recommended_bid_adjustment": "-30%",
                    "rationale": f"Low conversion rate ({conv_rate:.2f}%) with high CPC - reduce bids to improve efficiency"
                })

    return {
        "status": "success",
        "recommendations": recommendations if recommendations else [{"message": "No bid adjustments needed at this time"}]
    }

# Import original functions from agent.py
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from agent import (
    get_campaign_details,
    get_ad_group_performance,
    get_keyword_performance,
    get_search_terms_data,
    get_top_performers,
    analyze_performance_trends,
    detect_anomalies,
    calculate_roi,
    compare_time_periods,
    optimize_budgets,
    optimize_keywords,
    forecast_performance,
    analyze_scenarios
)

# Create enhanced agents with better error handling
data_agent = Agent(
    name="DataAgent",
    model="gemini-2.0-flash",
    description="Retrieves and processes real Google Ads campaign data with fallback support.",
    instruction="""You retrieve Google Ads data from the API.
    If the API is temporarily unavailable, you can provide sample data for demonstration.
    Always indicate whether you're using real or sample data.""",
    tools=[get_campaign_performance, get_campaign_details, get_ad_group_performance,
           get_keyword_performance, get_search_terms_data, get_top_performers]
)

optimization_agent = Agent(
    name="OptimizationAgent",
    model="gemini-2.0-flash",
    description="Provides optimization recommendations with fallback to best practices.",
    instruction="""You provide optimization recommendations for Google Ads campaigns.
    If real data is unavailable, provide recommendations based on industry best practices.
    Always explain your reasoning clearly.""",
    tools=[optimize_bids_with_fallback, optimize_budgets, optimize_keywords]
)

# Keep other agents as they were
insight_agent = Agent(
    name="InsightAgent",
    model="gemini-2.0-flash",
    description="Analyzes campaign performance and provides insights.",
    instruction="""You analyze Google Ads data to provide actionable insights.
    Focus on trends, anomalies, and ROI calculations.""",
    tools=[analyze_performance_trends, detect_anomalies, calculate_roi, compare_time_periods]
)

forecasting_agent = Agent(
    name="ForecastingAgent",
    model="gemini-2.0-flash",
    description="Forecasts future performance based on historical data.",
    instruction="""You provide performance forecasts and scenario analysis.
    Base forecasts on historical trends when available.""",
    tools=[forecast_performance, analyze_scenarios]
)

# Enhanced root orchestrator
root_agent_enhanced = Agent(
    name="GoogleAdsOrchestrator",
    model="gemini-2.0-flash",
    description="Orchestrates multiple specialized agents for Google Ads management with robust error handling.",
    instruction="""You orchestrate Google Ads campaign management with resilience.

    Coordinate between specialized agents:
    1. DataAgent - Retrieves campaign data (with fallback support)
    2. InsightAgent - Analyzes performance and trends
    3. OptimizationAgent - Provides optimization recommendations
    4. ForecastingAgent - Generates performance predictions

    If the API is temporarily unavailable:
    - Use fallback data for demonstration
    - Provide best practice recommendations
    - Always inform the user about data availability

    Provide clear, actionable responses regardless of API availability.""",
    sub_agents=[data_agent, insight_agent, optimization_agent, forecasting_agent]
)