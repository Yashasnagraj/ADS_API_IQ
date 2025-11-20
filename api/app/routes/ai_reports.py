"""
AI Reports Generator API Endpoints
Generates executive summaries and reports from real campaign data
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

class ReportConfig(BaseModel):
    report_name: str
    report_type: str  # executive, client, campaign, weekly, performance
    customer_id: int
    start_date: str
    end_date: str
    campaigns: str = "all"  # "all" or comma-separated campaign IDs
    include_sections: dict = {
        "executive_summary": True,
        "performance_trends": True,
        "ai_insights": True,
        "top_campaigns": True,
        "improvements": True,
        "budget_analysis": True
    }
    branding: dict = {
        "color_scheme": "#667eea"
    }

@router.post("/reports/generate")
async def generate_report(config: ReportConfig):
    """Generate AI-powered marketing report from real data"""

    conn = get_warehouse_connection()
    cursor = conn.cursor()

    try:
        # Get customer info
        cursor.execute("SELECT * FROM customers WHERE customer_id = ?", (config.customer_id,))
        customer = cursor.fetchone()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Query campaign performance data from fact table
        query = """
            SELECT
                c.campaign_name,
                SUM(f.impressions) as total_impressions,
                SUM(f.clicks) as total_clicks,
                SUM(f.spend_micros) / 1000000.0 as total_cost,
                SUM(f.conversions) as total_conversions,
                SUM(f.conversion_value_micros) / 1000000.0 as total_revenue,
                AVG(f.ctr) as avg_ctr,
                AVG(f.cpc_micros) / 1000000.0 as avg_cpc
            FROM fact_campaign_performance_daily f
            JOIN dim_campaign_unified c ON f.campaign_unified_id = c.campaign_unified_id
            WHERE f.customer_id = ?
            AND f.date_id >= ?
            AND f.date_id <= ?
            GROUP BY c.campaign_name
            ORDER BY total_cost DESC
        """

        cursor.execute(query, (config.customer_id, config.start_date, config.end_date))
        campaigns = cursor.fetchall()

        # Calculate overall metrics
        total_spend = sum(c['total_cost'] or 0 for c in campaigns)
        total_revenue = sum(c['total_revenue'] or 0 for c in campaigns)
        total_conversions = sum(c['total_conversions'] or 0 for c in campaigns)
        total_clicks = sum(c['total_clicks'] or 0 for c in campaigns)
        total_impressions = sum(c['total_impressions'] or 0 for c in campaigns)

        roas = (total_revenue / total_spend) if total_spend > 0 else 0
        avg_ctr = (total_clicks / total_impressions * 100) if total_impressions > 0 else 0
        avg_cpc = (total_spend / total_clicks) if total_clicks > 0 else 0

        # Generate AI narrative
        narrative = f"""# {config.report_name}

## Executive Summary

**Report Period**: {config.start_date} to {config.end_date}
**Customer**: {customer['customer_name']}

### Key Performance Indicators

- **Total Spend**: ₹{total_spend:,.2f}
- **Revenue Generated**: ₹{total_revenue:,.2f}
- **ROAS**: {roas:.2f}x
- **Conversions**: {int(total_conversions)}
- **Average CPC**: ₹{avg_cpc:.2f}
- **Average CTR**: {avg_ctr:.2f}%

## Performance Analysis

"""

        if roas > 3.0:
            narrative += "✅ **Excellent Performance** - Your campaigns are generating strong returns with a ROAS above 3x. This indicates highly efficient ad spend.\n\n"
        elif roas > 2.0:
            narrative += "👍 **Good Performance** - Your campaigns are profitable with a healthy ROAS above 2x. There's room for optimization to push even higher.\n\n"
        elif roas > 1.0:
            narrative += "⚠️ **Moderate Performance** - Your campaigns are profitable but could benefit from optimization. Focus on improving conversion rates and reducing costs.\n\n"
        else:
            narrative += "🚨 **Needs Attention** - Your campaigns are not generating positive returns. Immediate action required to improve ROAS.\n\n"

        narrative += "## Top Performing Campaigns\n\n"

        # Sort campaigns by ROAS
        campaigns_with_roas = []
        for c in campaigns:
            camp_roas = (c['total_revenue'] / c['total_cost']) if c['total_cost'] and c['total_cost'] > 0 else 0
            campaigns_with_roas.append({
                'name': c['campaign_name'],
                'spend': c['total_cost'] or 0,
                'revenue': c['total_revenue'] or 0,
                'roas': camp_roas,
                'conversions': c['total_conversions'] or 0
            })

        campaigns_with_roas.sort(key=lambda x: x['roas'], reverse=True)

        for i, camp in enumerate(campaigns_with_roas[:5], 1):
            narrative += f"{i}. **{camp['name']}**\n"
            narrative += f"   - ROAS: {camp['roas']:.2f}x\n"
            narrative += f"   - Spend: ₹{camp['spend']:,.2f}\n"
            narrative += f"   - Revenue: ₹{camp['revenue']:,.2f}\n"
            narrative += f"   - Conversions: {int(camp['conversions'])}\n\n"

        narrative += "## AI Recommendations\n\n"

        if roas < 2.0:
            narrative += "1. **Optimize Budget Allocation**: Shift more budget to your top-performing campaigns\n"
            narrative += "2. **Review Keywords**: Identify and pause low-converting keywords\n"
            narrative += "3. **Improve Ad Copy**: Test new ad variations focusing on value propositions\n"
        else:
            narrative += "1. **Scale What Works**: Increase budgets on top-performing campaigns by 20-30%\n"
            narrative += "2. **Expand Reach**: Consider adding similar keywords to successful campaigns\n"
            narrative += "3. **Test New Creatives**: Continue A/B testing to maintain performance\n"

        # Get daily performance for chart
        chart_query = """
            SELECT
                date_id as date,
                SUM(spend_micros) / 1000000.0 as spend,
                SUM(conversion_value_micros) / 1000000.0 as revenue,
                SUM(conversion_value_micros) / (SUM(spend_micros) / 1000000.0) as roas
            FROM fact_campaign_performance_daily
            WHERE customer_id = ?
            AND date_id >= ?
            AND date_id <= ?
            GROUP BY date_id
            ORDER BY date_id
        """

        cursor.execute(chart_query, (config.customer_id, config.start_date, config.end_date))
        daily_data = cursor.fetchall()

        chart_data = [
            {
                "date": row['date'],
                "spend": round(row['spend'] or 0, 2),
                "revenue": round(row['revenue'] or 0, 2),
                "roas": round(row['roas'] or 0, 2) if row['spend'] and row['spend'] > 0 else 0
            }
            for row in daily_data
        ]

        return {
            "success": True,
            "report": {
                "report_name": config.report_name,
                "report_type": config.report_type,
                "generated_at": datetime.now().isoformat(),
                "customer_name": customer['customer_name'],
                "date_range": {
                    "start": config.start_date,
                    "end": config.end_date
                },
                "metrics": {
                    "total_spend": round(total_spend, 2),
                    "total_revenue": round(total_revenue, 2),
                    "roas": round(roas, 2),
                    "conversions": int(total_conversions),
                    "avg_cpc": round(avg_cpc, 2),
                    "avg_ctr": round(avg_ctr, 2)
                },
                "narrative": narrative,
                "chart_data": chart_data,
                "top_campaigns": campaigns_with_roas[:10]
            }
        }

    finally:
        conn.close()
