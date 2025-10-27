"""
Orchestration Agent for Google Ads Multi-Agent System
Following ADK Multi-Agent Pattern with Real API Integration
"""
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import requests
from google.adk.agents import Agent

logger = logging.getLogger(__name__)

# API Configuration
# Use port 8001 for main MarketingIQ API (ADK web runs on port 8000)
API_BASE_URL = "http://localhost:8001/api/v1"


# Helper function for API calls
def make_api_request(endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Make a request to the API endpoint.

    Args:
        endpoint: API endpoint path
        params: Optional query parameters

    Returns:
        JSON response from the API
    """
    try:
        url = f"{API_BASE_URL}{endpoint}"
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {str(e)}")
        return {"error": str(e), "status": "failed"}


# Tool functions for Data Agent
def get_campaign_performance(customer_id: Optional[str] = None, campaign_type: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve campaign performance data from Google Ads API.

    Args:
        customer_id: Google Ads customer ID (optional for now as API doesn't filter by customer)

    Returns:
        Campaign performance metrics including impressions, clicks, conversions
    """
    params = {}
    if customer_id:
        params["customer_id"] = customer_id
    if campaign_type:
        params["channel_type"] = campaign_type

    response = make_api_request("/campaigns", params=params)
    if "error" not in response:
        # Extract campaigns array from response
        campaigns_list = response.get("campaigns", [])

        # Get summary metrics
        summary = make_api_request("/metrics/summary")
        return {
            "status": "success",
            "customer_id": customer_id or "all",
            "campaigns": campaigns_list,  # Return just the array
            "summary": summary,
            "total": response.get("total", len(campaigns_list))
        }
    return response


def get_campaign_details(campaign_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific campaign.

    Args:
        campaign_id: Campaign ID

    Returns:
        Detailed campaign information including performance over time
    """
    campaign = make_api_request(f"/campaigns/{campaign_id}")
    if "error" not in campaign:
        performance = make_api_request(f"/campaigns/{campaign_id}/performance")
        ads = make_api_request(f"/campaigns/{campaign_id}/ads")
        return {
            "status": "success",
            "campaign": campaign,
            "performance_history": performance,
            "ads": ads
        }
    return campaign


def get_ad_group_performance(customer_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve ad group performance data from Google Ads API.

    Args:
        customer_id: Google Ads customer ID (optional)

    Returns:
        Ad group performance metrics
    """
    params = {}
    if customer_id:
        params["customer_id"] = customer_id

    response = make_api_request("/ad-groups", params=params)
    if "error" not in response:
        ad_groups_list = response.get("ad_groups", [])
        return {
            "status": "success",
            "customer_id": customer_id or "all",
            "ad_groups": ad_groups_list,
            "total": response.get("total", len(ad_groups_list))
        }
    return response


def get_keyword_performance(customer_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve keyword performance data from Google Ads API.

    Args:
        customer_id: Google Ads customer ID (optional)

    Returns:
        Keyword performance metrics including quality scores
    """
    params = {"limit": 100}
    if customer_id:
        params["customer_id"] = customer_id

    response = make_api_request("/keywords", params=params)

    if "error" not in response:
        keywords_list = response.get("keywords", [])

        # Find underperformers: low quality score, high cost, low conversions
        underperformers = [
            kw for kw in keywords_list
            if (kw.get("quality_score", 10) < 5 and
                kw.get("metrics", {}).get("cost", 0) > 1000)
        ]

        return {
            "status": "success",
            "customer_id": customer_id or "all",
            "keywords": keywords_list,
            "underperforming_keywords": underperformers,
            "total": response.get("total", len(keywords_list))
        }
    return response


def get_search_terms_data(customer_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Retrieve search terms data and negative keyword suggestions.

    Args:
        customer_id: Google Ads customer ID (optional)

    Returns:
        Search terms data and negative keyword recommendations
    """
    search_terms = make_api_request("/search-terms")
    negative_suggestions = make_api_request("/search-terms/negative")

    if "error" not in search_terms:
        return {
            "status": "success",
            "customer_id": customer_id or "all",
            "search_terms": search_terms,
            "negative_keyword_suggestions": negative_suggestions
        }
    return search_terms


def get_top_performers(metric: str = "roas") -> Dict[str, Any]:
    """
    Get top performing campaigns by specified metric.

    Args:
        metric: Metric to sort by (roas, conversions, ctr)

    Returns:
        Top performing campaigns
    """
    return make_api_request("/campaigns/top-performers", params={"metric": metric})


# Tool functions for Insight Agent
def analyze_performance_trends(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Analyze performance trends in campaign data.

    Args:
        data: Campaign performance data (optional, will fetch if not provided)

    Returns:
        Performance trend analysis with INR currency formatting
    """
    trends = make_api_request("/metrics/trends")
    by_day = make_api_request("/metrics/by-day-of-week")

    if "error" not in trends:
        insights = []

        # Analyze trends from the data
        if isinstance(trends, list) and len(trends) > 0:
            # Calculate trend direction
            if len(trends) > 1:
                recent = trends[-1] if trends else {}
                older = trends[0] if trends else {}

                if recent.get('clicks', 0) > older.get('clicks', 0):
                    insights.append("Click volume is trending upward")
                if recent.get('conversions', 0) > older.get('conversions', 0):
                    insights.append("Conversion rate is improving")
                if recent.get('cost', 0) < older.get('cost', 0):
                    insights.append("Cost efficiency is improving")

                # Format CPC values in INR
                recent_cpc = recent.get('cpc', 0)
                older_cpc = older.get('cpc', 0)
                insights.append(f"CPC trend: ₹{older_cpc:.2f} → ₹{recent_cpc:.2f}")

        # Analyze day of week patterns
        if isinstance(by_day, list) and len(by_day) > 0:
            best_day = max(by_day, key=lambda x: x.get('conversions', 0))
            worst_day = min(by_day, key=lambda x: x.get('conversions', 0))
            insights.append(f"Best performing day: {best_day.get('day_of_week', 'Unknown')}")
            insights.append(f"Worst performing day: {worst_day.get('day_of_week', 'Unknown')}")

        return {
            "status": "success",
            "trends_data": trends,
            "day_of_week_performance": by_day,
            "insights": insights if insights else ["Analyzing historical trends for patterns"]
        }
    return {"status": "error", "message": "Failed to fetch trends data"}


def detect_anomalies(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Detect anomalies in campaign performance using real data.

    Args:
        data: Campaign performance data (optional)

    Returns:
        Detected anomalies and recommendations
    """
    # Get underperforming keywords as anomalies
    underperformers = make_api_request("/keywords/underperformers")

    anomalies = []
    recommendations = []

    if "error" not in underperformers and isinstance(underperformers, list):
        for keyword in underperformers[:5]:  # Top 5 problematic keywords
            anomalies.append({
                "type": "underperforming_keyword",
                "keyword": keyword.get('keyword_text', 'Unknown'),
                "cost": keyword.get('cost', 0),
                "conversions": keyword.get('conversions', 0)
            })
            recommendations.append(f"Consider pausing keyword '{keyword.get('keyword_text', 'Unknown')}' - high cost with no conversions")

    # Check for campaigns with unusual patterns
    campaigns = make_api_request("/campaigns")
    if "error" not in campaigns and isinstance(campaigns, list):
        for campaign in campaigns:
            ctr = campaign.get('ctr', 0)
            if ctr < 1.0:  # CTR below 1% is concerning
                anomalies.append({
                    "type": "low_ctr",
                    "campaign": campaign.get('campaign_name', 'Unknown'),
                    "ctr": ctr
                })
                recommendations.append(f"Campaign '{campaign.get('campaign_name', 'Unknown')}' has low CTR ({ctr:.2f}%) - review ad copy and targeting")

    return {
        "status": "success",
        "anomalies": anomalies,
        "recommendations": recommendations if recommendations else ["All metrics within expected ranges"]
    }


def calculate_roi(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Calculate ROI metrics for campaigns using real data.

    Args:
        data: Campaign performance data (optional)

    Returns:
        ROI calculations and metrics
    """
    summary = make_api_request("/metrics/summary")

    if "error" not in summary:
        total_cost = summary.get('total_cost', 0)
        total_conversions = summary.get('total_conversions', 0)
        total_conversion_value = summary.get('total_conversion_value', 0)

        roi = 0
        roas = 0
        cost_per_conversion = 0

        if total_cost > 0:
            roi = ((total_conversion_value - total_cost) / total_cost) * 100 if total_conversion_value else 0
            roas = total_conversion_value / total_cost if total_conversion_value else 0
            cost_per_conversion = total_cost / total_conversions if total_conversions > 0 else total_cost

        return {
            "status": "success",
            "roi_percentage": round(roi, 2),
            "roas": round(roas, 2),
            "cost_per_conversion": round(cost_per_conversion, 2),
            "total_cost": round(total_cost, 2),
            "total_conversions": total_conversions,
            "total_conversion_value": round(total_conversion_value, 2) if total_conversion_value else 0
        }
    return {"status": "error", "message": "Failed to calculate ROI"}


def compare_time_periods(period1_start: Optional[str] = None, period1_end: Optional[str] = None,
                         period2_start: Optional[str] = None, period2_end: Optional[str] = None) -> Dict[str, Any]:
    """
    Compare performance between two time periods.

    Args:
        period1_start: Start date for first period
        period1_end: End date for first period
        period2_start: Start date for second period
        period2_end: End date for second period

    Returns:
        Comparison analysis between periods
    """
    comparison = make_api_request("/metrics/compare")
    return comparison if "error" not in comparison else {"status": "error", "message": "Comparison data unavailable"}


# Tool functions for Optimization Agent
def optimize_bids(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate bid optimization recommendations based on real performance data.

    Args:
        data: Campaign performance data (optional)

    Returns:
        Bid optimization recommendations
    """
    campaigns = make_api_request("/campaigns")
    recommendations = []

    if "error" not in campaigns and isinstance(campaigns, list):
        for campaign in campaigns:
            cpc = campaign.get('average_cpc', 0)
            conversions = campaign.get('conversions', 0)
            clicks = campaign.get('clicks', 0)
            conv_rate = (conversions / clicks * 100) if clicks > 0 else 0

            if conv_rate > 5:  # High converting campaign
                recommendations.append({
                    "campaign_id": campaign.get('campaign_id'),
                    "campaign_name": campaign.get('campaign_name'),
                    "current_avg_cpc": round(cpc, 2),
                    "recommended_action": "increase_bid",
                    "recommended_bid_adjustment": "+20%",
                    "rationale": f"High conversion rate ({conv_rate:.2f}%) - increase bids to capture more traffic"
                })
            elif conv_rate < 1 and cpc > 2:  # Low converting, expensive campaign
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


def optimize_budgets(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate budget optimization recommendations based on real performance.

    Args:
        data: Campaign performance data (optional)

    Returns:
        Budget optimization recommendations
    """
    top_performers = make_api_request("/campaigns/top-performers", params={"metric": "roas"})
    all_campaigns = make_api_request("/campaigns")
    recommendations = []

    if "error" not in top_performers and isinstance(top_performers, list):
        # Recommend budget increases for top performers
        for campaign in top_performers[:3]:  # Top 3 campaigns
            recommendations.append({
                "campaign_id": campaign.get('campaign_id'),
                "campaign_name": campaign.get('campaign_name'),
                "current_spend": round(campaign.get('cost', 0), 2),
                "recommended_action": "increase_budget",
                "recommended_change": "+30%",
                "rationale": f"Top performing campaign with ROAS of {campaign.get('roas', 0):.2f}"
            })

    # Find underperformers to reduce budget
    if "error" not in all_campaigns and isinstance(all_campaigns, list):
        for campaign in all_campaigns:
            roas = campaign.get('roas', 0)
            if roas < 1 and campaign.get('cost', 0) > 100:  # Poor ROAS and significant spend
                recommendations.append({
                    "campaign_id": campaign.get('campaign_id'),
                    "campaign_name": campaign.get('campaign_name'),
                    "current_spend": round(campaign.get('cost', 0), 2),
                    "recommended_action": "decrease_budget",
                    "recommended_change": "-50%",
                    "rationale": f"Poor ROAS ({roas:.2f}) - reallocate budget to better performing campaigns"
                })

    return {
        "status": "success",
        "recommendations": recommendations if recommendations else [{"message": "Current budget allocation is optimal"}]
    }


def optimize_keywords(data: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Generate keyword optimization recommendations using real search term data.

    Args:
        data: Campaign and keyword performance data (optional)

    Returns:
        Keyword optimization recommendations
    """
    underperformers = make_api_request("/keywords/underperformers")
    negative_suggestions = make_api_request("/search-terms/negative")
    search_terms = make_api_request("/search-terms")

    recommendations = {
        "add_keywords": [],
        "remove_keywords": [],
        "negative_keywords": [],
        "bid_adjustments": []
    }

    # Remove underperforming keywords
    if "error" not in underperformers and isinstance(underperformers, list):
        for keyword in underperformers[:10]:  # Top 10 worst performers
            recommendations["remove_keywords"].append({
                "keyword": keyword.get('keyword_text'),
                "reason": f"High cost ({keyword.get('cost', 0):.2f}) with no conversions"
            })

    # Add negative keywords
    if "error" not in negative_suggestions and isinstance(negative_suggestions, list):
        for term in negative_suggestions[:10]:  # Top 10 negative suggestions
            recommendations["negative_keywords"].append({
                "keyword": term.get('search_term'),
                "reason": f"Irrelevant search term with {term.get('clicks', 0)} wasted clicks"
            })

    # Find high-performing search terms to add as keywords
    if "error" not in search_terms and isinstance(search_terms, list):
        for term in search_terms:
            if term.get('conversions', 0) > 0 and term.get('conversion_rate', 0) > 5:
                recommendations["add_keywords"].append({
                    "keyword": term.get('search_term'),
                    "match_type": "EXACT",
                    "reason": f"High converting search term ({term.get('conversion_rate', 0):.2f}% CR)"
                })

    return {
        "status": "success",
        "recommendations": recommendations
    }


# Tool functions for Forecasting Agent
def forecast_performance(days: int = 30) -> Dict[str, Any]:
    """
    Forecast future campaign performance based on current metrics.

    Args:
        days: Number of days to forecast (default 30)

    Returns:
        Performance forecasts
    """
    summary = make_api_request("/metrics/summary")

    if "error" not in summary:
        # Use LAST_30_DAYS metrics to calculate daily averages
        total_clicks = summary.get('total_clicks', 0)
        total_impressions = summary.get('total_impressions', 0)
        total_cost = summary.get('total_cost', 0)
        total_conversions = summary.get('total_conversions', 0)

        # Calculate daily averages (assuming 30-day period)
        avg_daily_clicks = total_clicks / 30
        avg_daily_impressions = total_impressions / 30
        avg_daily_cost = total_cost / 30
        avg_daily_conversions = total_conversions / 30

        # Project forward for requested period
        forecast = {
            "status": "success",
            "forecast_period": f"{days} days",
            "based_on": "Last 30 days average performance",
            "predicted_metrics": {
                "impressions": round(avg_daily_impressions * days),
                "clicks": round(avg_daily_clicks * days),
                "conversions": round(avg_daily_conversions * days, 1),
                "cost": round(avg_daily_cost * days, 2),
                "ctr": summary.get('avg_ctr', 0),
                "avg_cpc": summary.get('avg_cpc', 0)
            },
            "daily_averages": {
                "impressions": round(avg_daily_impressions),
                "clicks": round(avg_daily_clicks),
                "conversions": round(avg_daily_conversions, 2),
                "cost": round(avg_daily_cost, 2)
            },
            "confidence": "medium"
        }
        return forecast

    return {"status": "error", "message": "Insufficient data for forecasting"}


def analyze_scenarios(budget_change_percent: int = 0) -> Dict[str, Any]:
    """
    Analyze different budget and bid scenarios based on real data.

    Args:
        budget_change_percent: Percentage change in budget to analyze

    Returns:
        Scenario analysis results
    """
    summary = make_api_request("/metrics/summary")
    campaigns = make_api_request("/campaigns")

    if "error" not in summary:
        current_cost = summary.get('total_cost', 0)
        current_conversions = summary.get('total_conversions', 0)
        current_roas = summary.get('average_roas', 0)

        scenarios = [
            {
                "name": "Current State",
                "budget": round(current_cost, 2),
                "expected_conversions": current_conversions,
                "expected_roas": round(current_roas, 2)
            },
            {
                "name": "Conservative (-20% budget)",
                "budget": round(current_cost * 0.8, 2),
                "expected_conversions": round(current_conversions * 0.85),  # Slightly less than proportional
                "expected_roas": round(current_roas * 1.1, 2)  # Better ROAS with lower budget
            },
            {
                "name": "Moderate Growth (+20% budget)",
                "budget": round(current_cost * 1.2, 2),
                "expected_conversions": round(current_conversions * 1.15),  # Diminishing returns
                "expected_roas": round(current_roas * 0.95, 2)
            },
            {
                "name": "Aggressive Growth (+50% budget)",
                "budget": round(current_cost * 1.5, 2),
                "expected_conversions": round(current_conversions * 1.35),  # Further diminishing returns
                "expected_roas": round(current_roas * 0.9, 2)
            }
        ]

        # Add custom scenario if budget_change_percent provided
        if budget_change_percent != 0:
            multiplier = 1 + (budget_change_percent / 100)
            conversion_multiplier = 1 + (budget_change_percent / 100 * 0.7)  # Diminishing returns
            roas_multiplier = 1 - (abs(budget_change_percent) / 200)  # ROAS decreases with scale

            scenarios.append({
                "name": f"Custom ({budget_change_percent:+d}% budget)",
                "budget": round(current_cost * multiplier, 2),
                "expected_conversions": round(current_conversions * conversion_multiplier),
                "expected_roas": round(current_roas * roas_multiplier, 2)
            })

        return {
            "status": "success",
            "current_performance": summary,
            "scenarios": scenarios,
            "recommendation": "Consider moderate growth for optimal balance of scale and efficiency"
        }

    return {"status": "error", "message": "Failed to analyze scenarios"}


# GA4 Tool Functions for Data Agent
def get_ga4_session_behavior(
    customer_id: int = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    source: Optional[str] = None,
    campaign: Optional[str] = None,
    device: Optional[str] = None,
    limit: int = 100
) -> Dict[str, Any]:
    """
    Get GA4 session behavior data including bounce rate, engagement, and session duration.

    Args:
        customer_id: Customer ID (default: 1)
        start_date: Start date in YYYYMMDD format (optional)
        end_date: End date in YYYYMMDD format (optional)
        source: Filter by traffic source (optional)
        campaign: Filter by campaign name (optional)
        device: Filter by device category (optional)
        limit: Maximum number of records to return (default: 100)

    Returns:
        Session behavior data with bounce rate, engagement rate, avg session duration, etc.
    """
    params = {"customer_id": customer_id, "limit": limit}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date
    if source:
        params["source"] = source
    if campaign:
        params["campaign"] = campaign
    if device:
        params["device"] = device

    response = make_api_request("/ga4/sessions", params=params)
    if "error" not in response:
        return {
            "status": "success",
            "data": response,
            "total_sessions": len(response) if isinstance(response, list) else 0
        }
    return response


def get_ga4_campaign_quality(
    customer_id: int = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get GA4 campaign quality scores (0-100) based on bounce rate, engagement, and pages per session.

    Args:
        customer_id: Customer ID (default: 1)
        start_date: Start date in YYYYMMDD format (optional)
        end_date: End date in YYYYMMDD format (optional)

    Returns:
        Campaign quality scores with detailed metrics
    """
    params = {"customer_id": customer_id}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    response = make_api_request("/ga4/campaign-enrichment", params=params)
    if "error" not in response:
        return {
            "status": "success",
            "quality_scores": response,
            "description": "Quality scores range from 0-100, based on bounce rate (40%), engagement (30%), and pages per session (30%)"
        }
    return response


def get_ga4_behavior_by_campaign(
    customer_id: int = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get aggregated GA4 behavior metrics grouped by campaign.

    Args:
        customer_id: Customer ID (default: 1)
        start_date: Start date in YYYYMMDD format (optional)
        end_date: End date in YYYYMMDD format (optional)

    Returns:
        Campaign-level aggregated behavior data
    """
    params = {"customer_id": customer_id}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    response = make_api_request("/ga4/sessions/by-campaign", params=params)
    if "error" not in response:
        return {
            "status": "success",
            "campaigns": response,
            "total_campaigns": len(response) if isinstance(response, list) else 0
        }
    return response


def get_ga4_conversion_paths(
    customer_id: int = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    min_touchpoints: int = 2,
    limit: int = 50
) -> Dict[str, Any]:
    """
    Get GA4 multi-touch attribution data showing conversion paths.

    Args:
        customer_id: Customer ID (default: 1)
        start_date: Start date in YYYYMMDD format (optional)
        end_date: End date in YYYYMMDD format (optional)
        min_touchpoints: Minimum number of touchpoints to include (default: 2)
        limit: Maximum number of paths to return (default: 50)

    Returns:
        Conversion path data for multi-touch attribution analysis
    """
    params = {
        "customer_id": customer_id,
        "min_touchpoints": min_touchpoints,
        "limit": limit
    }
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    response = make_api_request("/ga4/conversion-paths", params=params)
    if "error" not in response:
        return {
            "status": "success",
            "conversion_paths": response,
            "total_paths": len(response) if isinstance(response, list) else 0
        }
    return response


def get_ga4_device_performance(
    customer_id: int = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """
    Get GA4 device performance breakdown (desktop, mobile, tablet).

    Args:
        customer_id: Customer ID (default: 1)
        start_date: Start date in YYYYMMDD format (optional)
        end_date: End date in YYYYMMDD format (optional)

    Returns:
        Device-level performance metrics including engagement and conversion data
    """
    params = {"customer_id": customer_id}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    response = make_api_request("/ga4/audience-insights/devices", params=params)
    if "error" not in response:
        return {
            "status": "success",
            "device_performance": response,
            "total_devices": len(response) if isinstance(response, list) else 0
        }
    return response


def get_ga4_audience_insights(
    customer_id: int = 1,
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    segment_type: str = "country"
) -> Dict[str, Any]:
    """
    Get GA4 audience insights including demographics and geographic data.

    Args:
        customer_id: Customer ID (default: 1)
        start_date: Start date in YYYYMMDD format (optional)
        end_date: End date in YYYYMMDD format (optional)
        segment_type: Type of segmentation - 'country', 'device', or 'all' (default: 'country')

    Returns:
        Audience segment data with engagement and conversion metrics
    """
    params = {"customer_id": customer_id, "segment_type": segment_type}
    if start_date:
        params["start_date"] = start_date
    if end_date:
        params["end_date"] = end_date

    response = make_api_request("/ga4/audience-insights", params=params)
    if "error" not in response:
        return {
            "status": "success",
            "audience_segments": response,
            "segment_type": segment_type,
            "total_segments": len(response) if isinstance(response, list) else 0
        }
    return response


# Create specialized sub-agents following ADK pattern
data_agent = Agent(
    name="DataAgent",
    model="gemini-2.0-flash",
    description="Retrieves and processes real Google Ads campaign data, ad groups, keywords, search terms, and GA4 analytics data from the API.",
    instruction="""You are responsible for collecting and organizing Google Ads and GA4 analytics data from the API.
    Use the available tools to retrieve campaign, ad group, keyword, and search term performance metrics.
    Also use GA4 tools to get session behavior, campaign quality scores, device performance, and audience insights.
    Always ensure data is properly formatted and includes relevant metrics.
    The API is available at http://localhost:8001 with various endpoints for Google Ads and GA4 data.""",
    tools=[
        # Google Ads tools
        get_campaign_performance, get_campaign_details, get_ad_group_performance,
        get_keyword_performance, get_search_terms_data, get_top_performers,
        # GA4 tools
        get_ga4_session_behavior, get_ga4_campaign_quality, get_ga4_behavior_by_campaign,
        get_ga4_conversion_paths, get_ga4_device_performance, get_ga4_audience_insights
    ]
)

insight_agent = Agent(
    name="InsightAgent",
    model="gemini-2.0-flash",
    description="Analyzes real campaign performance data, detects trends, anomalies, calculates ROI metrics, and evaluates campaign quality using Google Ads and GA4 data.",
    instruction="""You analyze real Google Ads and GA4 analytics data from the API to provide actionable insights.
    Use your tools to identify trends, detect anomalies, calculate ROI, and compare time periods.
    Use GA4 tools to get campaign quality scores, session behavior, and audience insights.
    Combine Google Ads metrics with GA4 behavior data to provide comprehensive campaign analysis.
    Focus on providing clear, data-driven insights that help improve campaign performance.
    All analysis should be based on actual data from the API, not mock data.""",
    tools=[
        # Google Ads analysis tools
        analyze_performance_trends, detect_anomalies, calculate_roi, compare_time_periods,
        # GA4 tools for quality insights
        get_ga4_campaign_quality, get_ga4_behavior_by_campaign, get_ga4_device_performance,
        get_ga4_audience_insights
    ]
)

optimization_agent = Agent(
    name="OptimizationAgent",
    model="gemini-2.0-flash",
    description="Provides data-driven optimization recommendations for bids, budgets, and keywords based on real Google Ads and GA4 performance data.",
    instruction="""You are an optimization specialist for Google Ads campaigns using real data from both Google Ads and GA4.
    Analyze actual performance data from the API and provide specific recommendations for:
    - Bid adjustments based on conversion rates, CPC, and GA4 quality scores
    - Budget reallocation based on ROAS, performance, and GA4 engagement metrics
    - Keyword optimization including additions, removals, and negative keywords
    - Use GA4 campaign quality scores to prioritize high-quality traffic sources
    - Consider GA4 device performance when making device bid adjustments
    Always base recommendations on actual performance metrics from the API.""",
    tools=[
        # Google Ads optimization tools
        optimize_bids, optimize_budgets, optimize_keywords,
        # GA4 tools for quality-based optimization
        get_ga4_campaign_quality, get_ga4_behavior_by_campaign, get_ga4_device_performance
    ]
)

forecasting_agent = Agent(
    name="ForecastingAgent",
    model="gemini-2.0-flash",
    description="Forecasts future campaign performance and analyzes scenarios based on historical Google Ads and GA4 data.",
    instruction="""You provide performance forecasts and scenario analysis using real Google Ads and GA4 data.
    Use historical data from the API to predict future performance.
    Analyze different budget and bid scenarios to help with strategic planning.
    Use GA4 conversion paths for multi-touch attribution modeling.
    Use GA4 session behavior trends to improve forecast accuracy.
    Base all forecasts on actual trends and patterns in the data.
    Include confidence levels and assumptions in your forecasts.""",
    tools=[
        # Google Ads forecasting tools
        forecast_performance, analyze_scenarios,
        # GA4 tools for attribution and trend analysis
        get_ga4_conversion_paths, get_ga4_session_behavior, get_ga4_behavior_by_campaign
    ]
)

# Create the root orchestrator agent with sub-agents
root_agent = Agent(
    name="GoogleAdsOrchestrator",
    model="gemini-2.0-flash",
    description="Orchestrates multiple specialized agents for comprehensive Google Ads and GA4 analytics management using real API data.",
    instruction="""You are the main orchestrator for Google Ads campaign management using real data from both Google Ads and GA4 Analytics APIs at http://localhost:8001.

    You coordinate between four specialized agents with GA4 analytics capabilities:
    1. DataAgent - For retrieving real Google Ads and GA4 data from the API
       - Google Ads: campaigns, ad groups, keywords, search terms
       - GA4: session behavior, campaign quality scores, conversion paths, device performance, audience insights
    2. InsightAgent - For analyzing actual performance, trends, and campaign quality
       - Combines Google Ads metrics with GA4 behavior data
       - Evaluates campaign quality scores (bounce rate, engagement, pages/session)
    3. OptimizationAgent - For data-driven optimization recommendations
       - Uses GA4 quality scores for bid and budget optimization
       - Considers GA4 device performance for device bid adjustments
    4. ForecastingAgent - For performance predictions based on historical data
       - Uses GA4 conversion paths for multi-touch attribution
       - Analyzes GA4 session behavior trends for improved forecasts

    Based on user requests:
    - If they ask for data or metrics, delegate to DataAgent to fetch from API (Google Ads or GA4)
    - If they want campaign quality analysis, use GA4 tools to get quality scores and behavior metrics
    - If they want analysis or insights, use DataAgent first to get real data, then InsightAgent
    - If they need optimization advice, gather actual data first (including GA4 quality), then use OptimizationAgent
    - If they want forecasts, collect historical data from API (including GA4 attribution), then use ForecastingAgent
    - For comprehensive analysis, coordinate all agents to provide complete insights from real data

    Always provide clear, structured responses with actionable recommendations based on actual data.
    Never use mock data - all information should come from the API endpoints.
    If the API is not available, inform the user that real-time data cannot be accessed.""",
    sub_agents=[data_agent, insight_agent, optimization_agent, forecasting_agent]
)