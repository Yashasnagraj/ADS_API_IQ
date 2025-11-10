"""
AI Copilot API Endpoints
Natural language interface for marketing data queries
"""
from fastapi import APIRouter, HTTPException
from datetime import datetime, timedelta
from typing import Optional, List
from pydantic import BaseModel
import sqlite3
from pathlib import Path

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

class ChatRequest(BaseModel):
    message: str
    context: dict  # customer_id, date_range, current_page

class ChatResponse(BaseModel):
    response: str
    chart_data: Optional[dict] = None
    actions: Optional[List[dict]] = None
    suggested_queries: Optional[List[str]] = None

@router.post("/chat")
async def chat(request: ChatRequest):
    """Process natural language queries about marketing data"""

    message = request.message.lower()
    customer_id = request.context.get('customer_id')

    if not customer_id:
        return {
            "response": "Please select a customer first to view their data.",
            "actions": []
        }

    conn = get_warehouse_connection()
    cursor = conn.cursor()

    try:
        # Get customer info
        cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (customer_id,))
        customer = cursor.fetchone()

        # Query: CPC increase
        if "cpc" in message and ("increase" in message or "increasing" in message or "higher" in message):
            # Get CPC trend
            query = """
                SELECT
                    date_id as date,
                    AVG(cpc_micros) / 1000000.0 as avg_cpc
                FROM fact_keyword_performance_daily
                WHERE customer_id = ?
                AND date_id >= date('now', '-30 days')
                GROUP BY date_id
                ORDER BY date_id
            """

            cursor.execute(query, (customer_id,))
            cpc_data = cursor.fetchall()

            if cpc_data and len(cpc_data) > 1:
                latest_cpc = cpc_data[-1]['avg_cpc'] or 0
                first_cpc = cpc_data[0]['avg_cpc'] or 1
                cpc_change = ((latest_cpc - first_cpc) / first_cpc * 100) if first_cpc > 0 else 0

                response = f"""Your CPC has {'increased' if cpc_change > 0 else 'decreased'} by {abs(cpc_change):.1f}% over the last 30 days.

**Main Reasons:**
1. **Competitive Landscape**: More advertisers bidding on similar keywords
2. **Market Trends**: Seasonal demand may be driving costs {'up' if cpc_change > 0 else 'down'}

**Recommendations:**
• Focus on improving Quality Score (better ad relevance, landing pages)
• Consider adding negative keywords to filter irrelevant traffic
• Test bid adjustments during lower-competition hours
• Review and pause underperforming keywords"""

                chart_data = {
                    "type": "line",
                    "title": "CPC Trend (Last 30 Days)",
                    "data": [{"date": str(d['date']), "cpc": round(d['avg_cpc'] or 0, 2)} for d in cpc_data]
                }

                return {
                    "response": response,
                    "chart_data": chart_data,
                    "actions": [
                        {"label": "View Keywords", "path": "/dashboard/data/keywords"},
                        {"label": "Optimize Bids", "path": "/dashboard/optimization/keywords"}
                    ]
                }

        # Query: ROAS / performance
        elif "roas" in message or "performance" in message or "how am i doing" in message:
            query = """
                SELECT
                    SUM(spend_micros) / 1000000.0 as total_cost,
                    SUM(conversion_value_micros) / 1000000.0 as total_revenue,
                    SUM(conversions) as total_conversions
                FROM fact_campaign_performance_daily
                WHERE customer_id = ?
                AND date_id >= date('now', '-30 days')
            """

            cursor.execute(query, (customer_id,))
            recent_perf = cursor.fetchone()

            total_spend = recent_perf['total_cost'] or 0
            total_revenue = recent_perf['total_revenue'] or 0
            total_conversions = recent_perf['total_conversions'] or 0
            roas = (total_revenue / total_spend) if total_spend > 0 else 0

            if roas > 3.0:
                status = "**excellent** 🎉"
                advice = "Consider increasing your budget by 20-30% to scale these results!"
            elif roas > 2.0:
                status = "**good** 👍"
                advice = "Focus budget on your top-performing campaigns to improve further."
            elif roas > 1.0:
                status = "**moderate** ⚠️"
                advice = "Review underperforming campaigns and optimize ad copy and keywords."
            else:
                status = "**needs attention** 🚨"
                advice = "Immediate action required: Pause low-performers and reallocate budget."

            response = f"""Your performance over the last 30 days is {status}

**Key Metrics:**
• Total Spend: ₹{total_spend:,.2f}
• Revenue Generated: ₹{total_revenue:,.2f}
• ROAS: {roas:.2f}x
• Conversions: {int(total_conversions)}

**AI Recommendation:**
{advice}"""

            return {
                "response": response,
                "actions": [
                    {"label": "View Campaign Performance", "path": "/dashboard/data/campaigns"},
                    {"label": "Generate Full Report", "path": "/ai/reports"}
                ]
            }

        # Query: Best/worst campaigns
        elif (("best" in message or "top" in message or "worst" in message) and "campaign" in message):
            query = """
                SELECT
                    c.campaign_name,
                    SUM(f.spend_micros) / 1000000.0 as total_cost,
                    SUM(f.conversion_value_micros) / 1000000.0 as total_revenue,
                    SUM(f.conversions) as total_conversions
                FROM fact_campaign_performance_daily f
                JOIN dim_campaign_unified c ON f.campaign_unified_id = c.campaign_unified_id
                WHERE c.customer_id = ?
                AND f.date_id >= date('now', '-30 days')
                GROUP BY c.campaign_name
            """

            cursor.execute(query, (customer_id,))
            campaigns = cursor.fetchall()

            campaigns_with_roas = []
            for c in campaigns:
                spend = c['total_cost'] or 0
                if spend > 0:
                    campaigns_with_roas.append({
                        "name": c['campaign_name'],
                        "roas": (c['total_revenue'] or 0) / spend,
                        "spend": spend,
                        "revenue": c['total_revenue'] or 0
                    })

            if "best" in message or "top" in message:
                sorted_campaigns = sorted(campaigns_with_roas, key=lambda x: x['roas'], reverse=True)[:5]
                title = "**Top 5 Performing Campaigns:**"
            else:
                sorted_campaigns = sorted(campaigns_with_roas, key=lambda x: x['roas'])[:5]
                title = "**Campaigns Needing Attention:**"

            response = f"{title}\n\n"
            for i, camp in enumerate(sorted_campaigns, 1):
                response += f"{i}. **{camp['name']}**\n"
                response += f"   - ROAS: {camp['roas']:.2f}x\n"
                response += f"   - Spend: ₹{camp['spend']:,.2f}\n"
                response += f"   - Revenue: ₹{camp['revenue']:,.2f}\n\n"

            return {
                "response": response,
                "actions": [
                    {"label": "View All Campaigns", "path": "/dashboard/data/campaigns"},
                    {"label": "Optimize Budget", "path": "/dashboard/optimization/budget"}
                ]
            }

        # Query: Keywords
        elif "keyword" in message:
            query = """
                SELECT
                    k.keyword_text,
                    AVG(f.ctr) as avg_ctr,
                    SUM(f.conversions) as total_conversions,
                    AVG(f.cpc_micros) / 1000000.0 as avg_cpc
                FROM fact_keyword_performance_daily f
                JOIN dim_keyword k ON f.keyword_id = k.keyword_id
                WHERE k.customer_id = ?
                AND f.impressions > 100
                GROUP BY k.keyword_text
                ORDER BY avg_ctr DESC
                LIMIT 10
            """

            cursor.execute(query, (customer_id,))
            keywords = cursor.fetchall()

            if keywords:
                response = "**Your Top 10 Keywords by CTR:**\n\n"
                for i, kw in enumerate(keywords, 1):
                    response += f"{i}. **{kw['keyword_text']}**\n"
                    response += f"   - CTR: {kw['avg_ctr']:.2f}%\n"
                    response += f"   - CPC: ₹{kw['avg_cpc']:.2f}\n"
                    response += f"   - Conversions: {int(kw['total_conversions'] or 0)}\n\n"

                return {
                    "response": response,
                    "actions": [
                        {"label": "View All Keywords", "path": "/dashboard/data/keywords"},
                        {"label": "Keyword Optimizer", "path": "/dashboard/optimization/keywords"}
                    ]
                }

        # Default: General help
        else:
            response = f"""Hi! I'm your AI Marketing Copilot for **{customer['customer_name']}**.

I can help you with:
• Campaign performance analysis
• Keyword insights and optimization
• Budget recommendations
• ROAS and ROI calculations
• Trend analysis and predictions

**Try asking:**
• "Why is my CPC increasing?"
• "Show me my best campaigns"
• "How is my ROAS?"
• "What are my top keywords?"
• "How's my budget today?"
"""

            return {
                "response": response,
                "suggested_queries": [
                    "Why is my CPC increasing?",
                    "Show me my best campaigns",
                    "What's my current ROAS?",
                    "Show my top performing keywords",
                    "Budget status today"
                ]
            }

    finally:
        conn.close()
