"""
AI Campaign Builder API Endpoints
Assists in creating optimized campaign structures
"""
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from pydantic import BaseModel
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta

router = APIRouter()

# Path to marketing warehouse database
WAREHOUSE_DB = Path(__file__).parent.parent.parent.parent / "marketing_warehouse.db"

def get_warehouse_connection():
    """Get connection to warehouse database"""
    if not WAREHOUSE_DB.exists():
        raise HTTPException(status_code=500, detail="Warehouse database not found")

    conn = sqlite3.connect(WAREHOUSE_DB)
    conn.row_factory = sqlite3.Row
    return conn

class CampaignBuildRequest(BaseModel):
    customer_id: int
    business_type: str
    goal: str
    budget: float
    target_location: str
    product_service: str
    use_best_practices: bool = True

@router.get("/campaign-builder/templates")
async def get_campaign_templates():
    """Get pre-built campaign templates"""

    templates = [
        {
            "id": "ecommerce_sales",
            "name": "E-commerce Sales Campaign",
            "description": "Optimized for online stores driving product sales",
            "structure": {
                "campaigns": 2,
                "ad_groups_per_campaign": 5,
                "keywords_per_ad_group": 15,
                "ads_per_ad_group": 3
            },
            "budget_range": "₹500-5000/day",
            "best_for": ["Online stores", "Product sales", "Shopping campaigns"],
            "features": [
                "Product-focused ad groups",
                "Shopping feed integration",
                "Dynamic remarketing",
                "Conversion tracking"
            ]
        },
        {
            "id": "lead_generation",
            "name": "Lead Generation Campaign",
            "description": "Capture qualified leads with form submissions",
            "structure": {
                "campaigns": 1,
                "ad_groups_per_campaign": 8,
                "keywords_per_ad_group": 12,
                "ads_per_ad_group": 3
            },
            "budget_range": "₹300-3000/day",
            "best_for": ["B2B services", "Consultations", "Free trials"],
            "features": [
                "Lead form extensions",
                "Call-to-action focus",
                "Quality score optimization",
                "Remarketing lists"
            ]
        },
        {
            "id": "brand_awareness",
            "name": "Brand Awareness Campaign",
            "description": "Maximize reach and brand visibility",
            "structure": {
                "campaigns": 2,
                "ad_groups_per_campaign": 4,
                "keywords_per_ad_group": 20,
                "ads_per_ad_group": 5
            },
            "budget_range": "₹1000-10000/day",
            "best_for": ["New product launch", "Brand building", "Market expansion"],
            "features": [
                "Display network campaigns",
                "Video campaigns",
                "Broad reach targeting",
                "Frequency capping"
            ]
        },
        {
            "id": "local_business",
            "name": "Local Business Campaign",
            "description": "Drive foot traffic to physical locations",
            "structure": {
                "campaigns": 1,
                "ad_groups_per_campaign": 6,
                "keywords_per_ad_group": 10,
                "ads_per_ad_group": 3
            },
            "budget_range": "₹200-2000/day",
            "best_for": ["Restaurants", "Retail stores", "Local services"],
            "features": [
                "Location extensions",
                "Call extensions",
                "Local inventory ads",
                "Store visit tracking"
            ]
        }
    ]

    return {
        "success": True,
        "templates": templates
    }

@router.post("/campaign-builder/generate")
async def generate_campaign_structure(request: CampaignBuildRequest):
    """Generate AI-powered campaign structure"""

    conn = get_warehouse_connection()
    cursor = conn.cursor()

    try:
        # Get historical performance metrics for this customer
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        # Get average CPC from historical data
        query_avg_cpc = """
            SELECT AVG(f.cpc) as avg_cpc
            FROM fact_campaign_performance_daily f
            JOIN dim_campaign_unified c ON f.campaign_id = c.campaign_id
            WHERE c.customer_id = ?
            AND f.date >= ?
            AND f.clicks > 0
        """

        cursor.execute(query_avg_cpc, (request.customer_id, start_date))
        cpc_row = cursor.fetchone()
        avg_cpc = cpc_row['avg_cpc'] if cpc_row and cpc_row['avg_cpc'] else 15.0

        # Get average CTR
        query_avg_ctr = """
            SELECT AVG(f.ctr) as avg_ctr
            FROM fact_campaign_performance_daily f
            JOIN dim_campaign_unified c ON f.campaign_id = c.campaign_id
            WHERE c.customer_id = ?
            AND f.date >= ?
            AND f.impressions > 0
        """

        cursor.execute(query_avg_ctr, (request.customer_id, start_date))
        ctr_row = cursor.fetchone()
        avg_ctr = ctr_row['avg_ctr'] if ctr_row and ctr_row['avg_ctr'] else 2.5

        # Get average conversion rate
        query_avg_conv = """
            SELECT AVG(f.conversion_rate) as avg_conv_rate
            FROM fact_campaign_performance_daily f
            JOIN dim_campaign_unified c ON f.campaign_id = c.campaign_id
            WHERE c.customer_id = ?
            AND f.date >= ?
            AND f.clicks > 0
        """

        cursor.execute(query_avg_conv, (request.customer_id, start_date))
        conv_row = cursor.fetchone()
        avg_conv_rate = conv_row['avg_conv_rate'] if conv_row and conv_row['avg_conv_rate'] else 3.0

        # Get top performing keywords for suggestions
        query_top_keywords = """
            SELECT
                k.keyword_text,
                AVG(f.ctr) as avg_ctr,
                AVG(f.conversion_rate) as avg_conv_rate,
                SUM(f.impressions) as total_impressions
            FROM fact_keyword_performance_daily f
            JOIN dim_keyword k ON f.keyword_id = k.keyword_id
            WHERE k.customer_id = ?
            AND f.date >= ?
            AND f.impressions > 50
            GROUP BY k.keyword_text
            ORDER BY avg_conv_rate DESC, avg_ctr DESC
            LIMIT 10
        """

        cursor.execute(query_top_keywords, (request.customer_id, start_date))
        top_keywords = cursor.fetchall()
        top_keyword_list = [kw['keyword_text'] for kw in top_keywords] if top_keywords else []

        # Generate predictions based on real data
        estimated_daily_clicks = round(request.budget / avg_cpc, 0)
        estimated_daily_impressions = round(estimated_daily_clicks / (avg_ctr / 100), 0)
        estimated_daily_conversions = round(estimated_daily_clicks * (avg_conv_rate / 100), 1)
        estimated_cpa = round(request.budget / max(estimated_daily_conversions, 0.1), 2)

        # Generate campaign structure based on business type and historical insights
        ad_groups = [
            {
                "name": f"{request.product_service} - Best Sellers",
                "bid_strategy": "Maximize conversions" if request.goal == "sales" else "Maximize clicks",
                "keywords": top_keyword_list[:5] if top_keyword_list else [f"best {request.product_service}", f"top {request.product_service}"],
                "match_types": ["broad", "phrase", "exact"]
            },
            {
                "name": f"{request.product_service} - Deals & Offers",
                "bid_strategy": "Target ROAS" if avg_conv_rate > 2.0 else "Maximize conversions",
                "keywords": [f"{request.product_service} sale", f"{request.product_service} discount", f"buy {request.product_service}"],
                "match_types": ["phrase", "exact"]
            }
        ]

        # Add third ad group if we have enough historical keywords
        if len(top_keyword_list) > 5:
            ad_groups.append({
                "name": f"{request.product_service} - High Intent",
                "bid_strategy": "Target CPA",
                "keywords": top_keyword_list[5:10],
                "match_types": ["exact"]
            })

        campaign_structure = {
            "campaign_name": f"{request.product_service} - {request.goal.title()} Campaign",
            "budget": {
                "daily": request.budget,
                "monthly": request.budget * 30,
                "allocation": "Start with 70% to top performers, 30% to testing" if top_keyword_list else "Even distribution recommended"
            },
            "targeting": {
                "location": request.target_location,
                "language": "English",
                "network": "Search + Display Select"
            },
            "ad_groups": ad_groups
        }

        # Build best practices based on historical performance
        best_practices = [
            "Use responsive search ads with 3+ headlines and 2+ descriptions",
            "Add sitelink extensions for better visibility",
            "Enable conversion tracking from day 1",
            "Set up negative keyword lists"
        ]

        if avg_conv_rate > 3.0:
            best_practices.append(f"Your conversion rate ({avg_conv_rate:.1f}%) is strong - use Target ROAS bidding")
        else:
            best_practices.append("Start with Maximize Conversions to gather data, then switch to Target ROAS")

        if top_keyword_list:
            best_practices.append(f"Focus budget on proven keywords: {', '.join(top_keyword_list[:3])}")

        predictions = {
            "estimated_daily_clicks": int(estimated_daily_clicks),
            "estimated_daily_impressions": int(estimated_daily_impressions),
            "estimated_daily_conversions": float(estimated_daily_conversions),
            "estimated_cpa": float(estimated_cpa),
            "confidence": 85 if top_keywords else 60,
            "based_on": f"{len(top_keywords)} historical keywords" if top_keywords else "industry benchmarks"
        }

        historical_insights = {
            "top_keywords": [
                {
                    "keyword": kw['keyword_text'],
                    "ctr": round(kw['avg_ctr'], 2),
                    "conv_rate": round(kw['avg_conv_rate'], 2)
                }
                for kw in top_keywords[:5]
            ] if top_keywords else [],
            "avg_cpc": round(avg_cpc, 2),
            "avg_ctr": round(avg_ctr, 2),
            "avg_conv_rate": round(avg_conv_rate, 2),
            "message": f"Based on {len(top_keywords)} keywords from last 30 days" if top_keywords else "No historical data - predictions use industry averages"
        }

        return {
            "success": True,
            "campaign_structure": campaign_structure,
            "best_practices": best_practices if request.use_best_practices else [],
            "predictions": predictions,
            "historical_insights": historical_insights
        }

    finally:
        conn.close()

@router.get("/campaign-builder/recommendations")
async def get_campaign_recommendations(customer_id: int):
    """Get campaign optimization recommendations"""

    conn = get_warehouse_connection()
    cursor = conn.cursor()

    try:
        # Get campaign count and performance
        end_date = datetime.now().date()
        start_date = end_date - timedelta(days=30)

        query_campaigns = """
            SELECT
                COUNT(DISTINCT c.campaign_id) as total_campaigns,
                AVG(f.roas) as avg_roas,
                AVG(f.ctr) as avg_ctr,
                AVG(f.conversion_rate) as avg_conv_rate,
                SUM(f.cost) as total_spend
            FROM fact_campaign_performance_daily f
            JOIN dim_campaign_unified c ON f.campaign_id = c.campaign_id
            WHERE c.customer_id = ?
            AND f.date >= ?
        """

        cursor.execute(query_campaigns, (customer_id, start_date))
        perf_row = cursor.fetchone()

        total_campaigns = perf_row['total_campaigns'] if perf_row else 0
        avg_roas = perf_row['avg_roas'] if perf_row and perf_row['avg_roas'] else 0
        avg_ctr = perf_row['avg_ctr'] if perf_row and perf_row['avg_ctr'] else 0
        avg_conv_rate = perf_row['avg_conv_rate'] if perf_row and perf_row['avg_conv_rate'] else 0
        total_spend = perf_row['total_spend'] if perf_row and perf_row['total_spend'] else 0

        # Build data-driven recommendations
        recommendations = []

        if total_campaigns == 0:
            recommendations = [
                "Start with 2-3 campaigns focusing on your best products/services",
                "Use responsive search ads for better performance",
                "Set daily budgets conservatively and scale up based on data",
                "Enable conversion tracking before launching"
            ]
        else:
            # ROAS recommendations
            if avg_roas > 4.0:
                recommendations.append(f"Excellent ROAS ({avg_roas:.1f}x) - Consider increasing budgets by 20-30% to scale")
            elif avg_roas > 2.0:
                recommendations.append(f"Solid ROAS ({avg_roas:.1f}x) - Maintain current strategy and test new ad variations")
            elif avg_roas > 0:
                recommendations.append(f"Low ROAS ({avg_roas:.1f}x) - Review targeting and keywords, pause underperformers")
            else:
                recommendations.append("No ROAS data - Ensure conversion tracking is properly configured")

            # CTR recommendations
            if avg_ctr > 5.0:
                recommendations.append(f"Strong CTR ({avg_ctr:.2f}%) - Your ads are highly relevant")
            elif avg_ctr < 2.0:
                recommendations.append(f"Low CTR ({avg_ctr:.2f}%) - Test new ad copy with emotional triggers and clear CTAs")

            # Conversion rate recommendations
            if avg_conv_rate > 5.0:
                recommendations.append(f"High conversion rate ({avg_conv_rate:.2f}%) - Landing pages are performing well")
            elif avg_conv_rate < 2.0:
                recommendations.append(f"Low conversion rate ({avg_conv_rate:.2f}%) - Check landing page relevance and load speed")

            # Budget recommendations
            if total_spend < 5000:
                recommendations.append(f"Low spend (₹{total_spend:,.0f}) - Consider increasing daily budgets to gather more data")
            elif total_spend > 50000:
                recommendations.append(f"High spend (₹{total_spend:,.0f}) - Ensure proper attribution and ROAS monitoring")

            # Campaign count recommendations
            if total_campaigns > 10:
                recommendations.append(f"Many campaigns ({total_campaigns}) - Consolidate low performers to simplify management")
            elif total_campaigns < 3:
                recommendations.append(f"Limited campaigns ({total_campaigns}) - Test new campaign types (Shopping, Display)")

        # Get keyword opportunities
        query_keywords = """
            SELECT COUNT(DISTINCT k.keyword_id) as total_keywords
            FROM dim_keyword k
            WHERE k.customer_id = ?
        """

        cursor.execute(query_keywords, (customer_id,))
        kw_row = cursor.fetchone()
        total_keywords = kw_row['total_keywords'] if kw_row else 0

        if total_keywords < 50:
            recommendations.append(f"Limited keywords ({total_keywords}) - Expand keyword list for better reach")
        elif total_keywords > 500:
            recommendations.append(f"Many keywords ({total_keywords}) - Use search term reports to prune low performers")

        return {
            "success": True,
            "total_campaigns": total_campaigns,
            "performance_summary": {
                "avg_roas": round(avg_roas, 2) if avg_roas else None,
                "avg_ctr": round(avg_ctr, 2) if avg_ctr else None,
                "avg_conv_rate": round(avg_conv_rate, 2) if avg_conv_rate else None,
                "total_spend": round(total_spend, 2) if total_spend else 0,
                "total_keywords": total_keywords
            },
            "recommendations": recommendations
        }

    finally:
        conn.close()
