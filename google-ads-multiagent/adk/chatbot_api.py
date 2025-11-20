#!/usr/bin/env python3
"""
ADK Chatbot API - Connects Google ADK Orchestration Agent to MarketingIQ Platform
Provides conversational interface to multi-agent system with Gemini-powered friendly responses
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys
import os
from pathlib import Path
import google as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / ".env")

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import WarehouseClient first (independent of ADK)
warehouse_client = None
try:
    # Try to import WarehouseClient from the data_agent module
    import sys
    warehouse_path = Path(__file__).parent / "orchestration_agent" / "sub_agents" / "data_agent"
    if str(warehouse_path) not in sys.path:
        sys.path.insert(0, str(warehouse_path))

    from warehouse_client import WarehouseClient
    warehouse_client = WarehouseClient()
    print("[OK] WarehouseClient initialized for customer lookup")
except Exception as e:
    print(f"[WARNING] WarehouseClient initialization failed: {e}")
    warehouse_client = None

# Import the root agent from orchestration_agent
try:
    from adk.orchestration_agent.agent import (
        root_agent,
        get_campaign_performance,
        get_keyword_performance,
        get_ad_group_performance,
        analyze_performance_trends,
        detect_anomalies,
        calculate_roi,
        optimize_bids,
        optimize_budgets,
        forecast_performance
    )
    ADK_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import ADK agents: {e}")
    ADK_AVAILABLE = False

# Configure Gemini
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY", "")
GEMINI_ENABLED = bool(GEMINI_API_KEY)

if GEMINI_ENABLED:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        gemini_model = genai.GenerativeModel('gemini-2.5-flash')
        print("[OK] Gemini API configured for friendly responses")
    except Exception as e:
        print(f"[WARNING] Gemini configuration failed: {e}")
        GEMINI_ENABLED = False
else:
    print("[WARNING] GOOGLE_API_KEY not found - using default formatting")

# Initialize FastAPI
app = FastAPI(
    title="ADK Chatbot API",
    description="Chatbot interface for Google ADK Multi-Agent System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    customer_id: Optional[str] = None
    campaign_type: Optional[str] = None
    date_range: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime
    agent_used: Optional[str] = None

# Helper function to find warehouse database
def find_warehouse_db() -> Optional[Path]:
    """
    Find the marketing_warehouse.db file by searching common locations
    """
    # Start from chatbot_api.py location: google-ads-multiagent/adk/chatbot_api.py
    current_file = Path(__file__).resolve()
    
    # Try different paths
    search_paths = [
        # From chatbot_api.py: go up 3 levels (adk -> google-ads-multiagent -> root)
        current_file.parent.parent.parent / "marketing_warehouse.db",
        # From chatbot_api.py: go up 2 levels (adk -> google-ads-multiagent)
        current_file.parent.parent / "marketing_warehouse.db",
        # Current working directory
        Path.cwd() / "marketing_warehouse.db",
        # Parent of current working directory
        Path.cwd().parent / "marketing_warehouse.db",
        # Absolute path from root (if we're in the project)
        Path("/Users/kushal/Desktop/ads/ADS_API_IQ/marketing_warehouse.db"),
    ]
    
    for db_path in search_paths:
        if db_path.exists():
            print(f"[OK] Found warehouse database at: {db_path}", flush=True)
            return db_path
    
    print(f"[ERROR] Warehouse database not found. Searched paths:", flush=True)
    for p in search_paths:
        print(f"  - {p}", flush=True)
    return None

# Helper function to get customer information
def get_customer_info(customer_id: str) -> Optional[Dict[str, Any]]:
    """
    Get customer name and details from customer ID

    Args:
        customer_id: Customer ID (string)

    Returns:
        Dictionary with customer_id and customer_name, or None if not found
    """
    if not warehouse_client or not customer_id:
        return None

    try:
        customers = warehouse_client.get_customers()
        for c in customers:
            if str(c['customer_id']) == str(customer_id):
                return {
                    'customer_id': c['customer_id'],
                    'customer_name': c['customer_name']
                }
        return None
    except Exception as e:
        print(f"[ERROR] Failed to get customer info: {e}")
        return None

# Simple intent mapping (no Gemini needed for basic routing)
def classify_user_intent(message: str) -> Dict[str, Any]:
    """
    Simple keyword-based intent classification
    """
    message_lower = message.lower()

    # Meta Ads queries (check BEFORE generic campaign/keyword queries)
    if any(word in message_lower for word in ['meta', 'facebook', 'instagram', 'meta ads', 'fb ads']):
        if any(word in message_lower for word in ['keyword', 'keywords', 'top keyword']):
            # Meta Ads doesn't have keywords, so treat as campaign query
            return {
                "agent": "data",
                "action": "meta_campaign_performance",
                "keywords": ["meta", "campaign"]
            }
        else:
            return {
                "agent": "data",
                "action": "meta_campaign_performance",
                "keywords": ["meta", "campaign"]
            }

    # Google Ads performance queries (check before generic campaign queries)
    if any(word in message_lower for word in ['google ads', 'google ad', 'googleads']) and any(word in message_lower for word in ['performance', 'how', 'show', 'what']):
        return {
            "agent": "data",
            "action": "campaign_performance",
            "keywords": ["google_ads", "campaign", "performance"]
        }

    # Campaign queries
    if any(word in message_lower for word in ['campaign', 'campaigns', 'top performer', 'best campaign', 'performance']):
        return {
            "agent": "data",
            "action": "campaign_performance",
            "keywords": ["campaign"]
        }

    # Keyword analysis
    if any(word in message_lower for word in ['keyword', 'keywords', 'quality score', 'underperform']):
        return {
            "agent": "data",
            "action": "keyword_performance",
            "keywords": ["keyword"]
        }

    # Ad group queries
    if any(word in message_lower for word in ['ad group', 'adgroup', 'ad groups']):
        return {
            "agent": "data",
            "action": "adgroup_performance",
            "keywords": ["ad_group"]
        }

    # Forecasting (check this BEFORE performance analysis to avoid conflicts)
    if any(word in message_lower for word in ['forecast', 'predict', 'projection', 'future', 'next month', 'next week', 'next 30 days']):
        return {
            "agent": "forecasting",
            "action": "forecast_performance",
            "keywords": ["forecast"]
        }

    # Performance analysis/trends
    if any(word in message_lower for word in ['trend', 'analyze', 'insight', 'how is']):
        return {
            "agent": "insight",
            "action": "analyze_trends",
            "keywords": ["trends", "performance"]
        }

    # Anomaly detection
    if any(word in message_lower for word in ['anomaly', 'anomalies', 'issue', 'problem', 'wrong', 'alert']):
        return {
            "agent": "insight",
            "action": "detect_anomalies",
            "keywords": ["anomaly"]
        }

    # Budget optimization
    if any(word in message_lower for word in ['budget', 'allocate', 'reallocate']):
        return {
            "agent": "optimization",
            "action": "optimize_budgets",
            "keywords": ["budget"]
        }

    # Bid optimization
    if any(word in message_lower for word in ['bid', 'bids', 'cpc', 'cost per click']):
        return {
            "agent": "optimization",
            "action": "optimize_bids",
            "keywords": ["bid"]
        }

    # Default to orchestrator for comprehensive analysis
    return {
        "agent": "orchestrator",
        "action": "comprehensive",
        "keywords": []
    }

def get_meta_campaign_performance(customer_id: Optional[str] = None) -> Dict[str, Any]:
    """
    Get Meta Ads campaign performance from warehouse
    Note: Meta Ads doesn't have keywords like Google Ads, so we return top campaigns
    """
    try:
        import sqlite3
        
        # Find warehouse database using helper function
        db_path = find_warehouse_db()
        if not db_path:
            return {
                "error": "Warehouse database not found. Please ensure marketing_warehouse.db exists in the project root.",
                "campaigns": []
            }
        
        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        # Query Meta campaigns with performance metrics
        query = """
            SELECT
                c.campaign_id,
                c.name,
                c.status,
                c.objective,
                c.daily_budget,
                COALESCE(SUM(i.impressions), 0) as impressions,
                COALESCE(SUM(i.clicks), 0) as clicks,
                COALESCE(SUM(i.spend), 0) as cost,
                COALESCE(SUM(i.conversions), 0) as conversions,
                COALESCE(SUM(i.purchase_value), 0) as conversion_value,
                CASE
                    WHEN SUM(i.impressions) > 0
                    THEN (CAST(SUM(i.clicks) AS FLOAT) / SUM(i.impressions)) * 100
                    ELSE 0
                END as ctr,
                CASE
                    WHEN SUM(i.clicks) > 0
                    THEN SUM(i.spend) / SUM(i.clicks)
                    ELSE 0
                END as cpc
            FROM meta_campaigns c
            LEFT JOIN meta_insights i ON c.campaign_id = i.campaign_id AND i.customer_id = c.customer_id
            WHERE 1=1
        """
        
        params = []
        if customer_id:
            query += " AND c.customer_id = ?"
            params.append(int(customer_id))
        
        query += """
            GROUP BY c.campaign_id, c.name, c.status, c.objective, c.daily_budget
            ORDER BY COALESCE(SUM(i.clicks), 0) DESC
            LIMIT 20
        """
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        campaigns = []
        for row in rows:
            campaigns.append({
                'campaign_id': row['campaign_id'],
                'name': row['name'],
                'campaign_name': row['name'],
                'status': row['status'],
                'objective': row['objective'],
                'daily_budget': row['daily_budget'],
                'impressions': int(row['impressions']),
                'clicks': int(row['clicks']),
                'cost': float(row['cost']),
                'conversions': float(row['conversions']),
                'conversion_value': float(row['conversion_value']),
                'ctr': float(row['ctr']),
                'cpc': float(row['cpc']),
                'metrics': {
                    'impressions': int(row['impressions']),
                    'clicks': int(row['clicks']),
                    'cost': float(row['cost']),
                    'conversions': float(row['conversions']),
                    'ctr': float(row['ctr']),
                    'cpc': float(row['cpc'])
                }
            })
        
        return {
            'campaigns': campaigns,
            'total': len(campaigns),
            'platform': 'Meta Ads',
            'note': 'Meta Ads uses campaigns and ad sets instead of keywords. Showing top campaigns by performance.'
        }
    except Exception as e:
        print(f"[ERROR] Failed to get Meta campaigns: {e}", flush=True)
        return {
            "error": str(e),
            "campaigns": [],
            "message": "Failed to fetch Meta Ads campaigns"
        }

def execute_agent_action(intent: Dict, customer_id: Optional[str] = None, campaign_type: Optional[str] = None, date_range: Optional[str] = None) -> Dict[str, Any]:
    """
    Execute the appropriate agent action based on intent
    """
    if not ADK_AVAILABLE:
        return {
            "error": "ADK agents not available",
            "message": "Please ensure the ADK system is properly installed"
        }

    try:
        agent = intent.get("agent")
        action = intent.get("action")

        print(f"\n{'='*80}", flush=True)
        print(f"[ADK AGENT INVOCATION]", flush=True)
        print(f"{'='*80}", flush=True)
        print(f"Agent: {agent.upper()}", flush=True)
        print(f"Action: {action}", flush=True)
        print(f"Customer ID: {customer_id or 'ALL'}", flush=True)
        print(f"Campaign Type: {campaign_type or 'ALL'}", flush=True)
        print(f"Date Range: {date_range or 'ALL_TIME'}", flush=True)
        print(f"{'='*80}\n", flush=True)

        # Data Agent actions
        if agent == "data":
            if action == "campaign_performance":
                print(f">> Querying database: campaigns_performance table for customer {customer_id}", flush=True)
                result = get_campaign_performance(customer_id, campaign_type)
                print(f">> Database returned {len(result.get('campaigns', []))} campaigns", flush=True)
                return result
            elif action == "meta_campaign_performance":
                print(f">> Querying database: meta_campaigns table for customer {customer_id}", flush=True)
                result = get_meta_campaign_performance(customer_id)
                print(f">> Database returned {len(result.get('campaigns', []))} Meta campaigns", flush=True)
                return result
            elif action == "keyword_performance":
                print(f">> Querying database: keywords_performance table for customer {customer_id}", flush=True)
                result = get_keyword_performance(customer_id)
                print(f">> Database returned {len(result.get('keywords', []))} keywords", flush=True)
                return result
            elif action == "adgroup_performance":
                print(f">> Querying database: adgroups_performance table for customer {customer_id}", flush=True)
                result = get_ad_group_performance(customer_id)
                print(f">> Database returned {len(result.get('adgroups', []))} ad groups", flush=True)
                return result

        # Insight Agent actions
        elif agent == "insight":
            if action == "analyze_trends":
                print(f">> Analyzing performance trends for customer {customer_id}...", flush=True)
                result = analyze_performance_trends(customer_id)
                print(f">> Trends analysis complete: {len(result.get('insights', []))} insights detected", flush=True)
                return result
            elif action == "detect_anomalies":
                print(f">> Running anomaly detection for customer {customer_id}...", flush=True)
                result = detect_anomalies(customer_id)
                print(f">> Anomaly detection complete: {result.get('summary', {}).get('total_anomalies', 0)} anomalies found", flush=True)
                return result
            elif action == "calculate_roi":
                print(f">> Calculating ROI for customer {customer_id}...", flush=True)
                result = calculate_roi(customer_id)
                print(f">> ROI calculation complete", flush=True)
                return result

        # Optimization Agent actions
        elif agent == "optimization":
            if action == "optimize_budgets":
                print(f">> Running budget optimization algorithm for customer {customer_id}...", flush=True)
                result = optimize_budgets(customer_id)
                print(f">> Budget optimization complete: {len(result.get('recommendations', []))} recommendations", flush=True)
                return result
            elif action == "optimize_bids":
                print(f">> Running bid optimization algorithm for customer {customer_id}...", flush=True)
                result = optimize_bids(customer_id)
                print(f">> Bid optimization complete: {len(result.get('recommendations', []))} recommendations", flush=True)
                return result

        # Forecasting Agent actions
        elif agent == "forecasting":
            if action == "forecast_performance":
                print(f">> Running ML forecasting model (30-day horizon) for customer {customer_id}...", flush=True)
                result = forecast_performance(customer_id, 30)  # Pass customer_id and default 30 days
                print(f">> Forecast complete: Predicted {result.get('predicted_metrics', {}).get('clicks', 0):,} clicks", flush=True)
                return result

        # Orchestrator - use root agent for complex queries
        elif agent == "orchestrator":
            print(f">> Orchestrator coordinating multiple agents for customer {customer_id}...", flush=True)
            print(f"  -> Invoking Data Agent for campaigns...", flush=True)
            campaign_data = get_campaign_performance(customer_id)
            print(f"  -> Invoking Insight Agent for trends...", flush=True)
            trends = analyze_performance_trends(customer_id)
            print(f">> Orchestrator analysis complete", flush=True)
            return {
                "status": "success",
                "campaigns": campaign_data,
                "trends": trends,
                "message": "Comprehensive analysis from orchestrator"
            }

        return {"error": "Unknown agent or action"}

    except Exception as e:
        return {
            "error": str(e),
            "message": "Failed to execute agent action"
        }

def format_response(user_message: str, intent: Dict, agent_data: Dict) -> str:
    """
    Format the agent response into natural language
    """
    agent = intent.get("agent")
    action = intent.get("action")

    # Check for errors
    if "error" in agent_data:
        return f"⚠️ I encountered an issue: {agent_data.get('message', agent_data['error'])}"

    # Format based on agent type
    if agent == "data":
        if action == "meta_campaign_performance":
            campaigns = agent_data.get("campaigns", [])
            note = agent_data.get("note", "")
            
            if isinstance(campaigns, list) and len(campaigns) > 0:
                # Sort by clicks descending
                campaigns.sort(key=lambda x: x.get('clicks', x.get('metrics', {}).get('clicks', 0)), reverse=True)
                
                top_5 = campaigns[:5]
                response = f"📱 **Meta Ads Campaign Performance**\n"
                response += f"_{len(top_5)} campaigns shown, {len(campaigns)} total_\n\n"
                
                if note:
                    response += f"ℹ️ _{note}_\n\n"
                
                for i, c in enumerate(top_5, 1):
                    name = c.get('name', c.get('campaign_name', 'Unknown'))
                    status = c.get('status', 'ACTIVE')
                    objective = c.get('objective', 'N/A')
                    
                    # Get metrics from either direct properties or nested metrics object
                    clicks = c.get('clicks', c.get('metrics', {}).get('clicks', 0))
                    cost = c.get('cost', c.get('metrics', {}).get('cost', 0))
                    conv = c.get('conversions', c.get('metrics', {}).get('conversions', 0))
                    impressions = c.get('impressions', c.get('metrics', {}).get('impressions', 0))
                    ctr = c.get('ctr', c.get('metrics', {}).get('ctr', 0))
                    cpc = c.get('cpc', c.get('metrics', {}).get('cpc', 0))
                    
                    # Calculate CTR if it's 0 but we have impressions and clicks
                    if ctr == 0 and impressions > 0 and clicks > 0:
                        ctr = (clicks / impressions) * 100
                    elif ctr < 1 and ctr > 0:
                        # CTR is stored as decimal, convert to percentage
                        ctr = ctr * 100
                    
                    response += f"{i}. **{name}** ({status})\n"
                    response += f"   Objective: {objective}\n"
                    response += f"   Impressions: {impressions:,} | Clicks: {clicks:,}\n"
                    response += f"   CTR: {ctr:.2f}% | Cost: ₹{cost:,.2f}\n"
                    response += f"   CPC: ₹{cpc:.2f} | Conversions: {conv:.1f}\n\n"
                return response
            else:
                return "📱 No Meta Ads campaigns found in the database. Make sure Meta Ads ETL has been run."
        
        if action == "campaign_performance":
            campaigns = agent_data.get("campaigns", [])
            if isinstance(campaigns, list) and len(campaigns) > 0:
                # Handle both warehouse format (clicks directly on object) and API format (metrics nested)
                # Filter campaigns with actual performance (clicks > 0)
                active_campaigns = []
                for c in campaigns:
                    # Try to get clicks from either location
                    clicks = c.get('clicks', c.get('metrics', {}).get('clicks', 0))
                    if clicks > 0:
                        active_campaigns.append(c)

                # Sort by clicks descending
                active_campaigns.sort(key=lambda x: x.get('clicks', x.get('metrics', {}).get('clicks', 0)), reverse=True)

                if len(active_campaigns) == 0:
                    # Still show all campaigns even if no clicks
                    active_campaigns = campaigns[:5]  # Show up to 5 campaigns
                    if len(active_campaigns) == 0:
                        return "📊 No campaigns found in the database."

                top_5 = active_campaigns[:5]
                response = f"📊 **Campaign Performance**\n"
                response += f"_{len(top_5)} campaigns shown, {len(campaigns)} total_\n\n"
                
                for i, c in enumerate(top_5, 1):
                    # Handle both warehouse and API formats
                    name = c.get('name', c.get('campaign_name', 'Unknown'))
                    status = c.get('status', 'ACTIVE')

                    # Get metrics from either direct properties or nested metrics object
                    clicks = c.get('clicks', c.get('metrics', {}).get('clicks', 0))
                    cost = c.get('cost', c.get('metrics', {}).get('cost', 0))
                    conv = c.get('conversions', c.get('metrics', {}).get('conversions', 0))
                    impressions = c.get('impressions', c.get('metrics', {}).get('impressions', 0))
                    ctr = c.get('ctr', c.get('metrics', {}).get('ctr', 0))

                    # Calculate CTR if it's 0 but we have impressions and clicks
                    if ctr == 0 and impressions > 0 and clicks > 0:
                        ctr = (clicks / impressions) * 100
                    elif ctr < 1 and ctr > 0:
                        # CTR is stored as decimal, convert to percentage
                        ctr = ctr * 100

                    response += f"{i}. **{name}** ({status})\n"
                    response += f"   Impressions: {impressions:,} | Clicks: {clicks:,}\n"
                    response += f"   CTR: {ctr:.2f}% | Cost: ₹{cost:,.2f}\n"
                    response += f"   Conversions: {conv:.1f}\n\n"
                return response

        elif action == "keyword_performance":
            keywords = agent_data.get("keywords", [])
            underperformers = agent_data.get("underperforming_keywords", [])

            response = f"🔑 **Keyword Analysis:**\n\n"
            response += f"Total Keywords Analyzed: {len(keywords) if isinstance(keywords, list) else 0}\n"
            response += f"Underperforming Keywords: {len(underperformers) if isinstance(underperformers, list) else 0}\n\n"

            if isinstance(underperformers, list) and len(underperformers) > 0:
                response += "**Top Underperformers** (Low Quality Score + High Cost):\n\n"
                for i, kw in enumerate(underperformers[:5], 1):
                    text = kw.get('keyword_text', 'Unknown')
                    qs = kw.get('quality_score', 'N/A')
                    metrics = kw.get('metrics', {})
                    cost = metrics.get('cost', 0)
                    conv = metrics.get('conversions', 0)
                    ctr = metrics.get('ctr', 0)
                    response += f"{i}. **{text}**\n"
                    response += f"   - Quality Score: {qs}/10 | Cost: ₹{cost:,.2f}\n"
                    response += f"   - CTR: {ctr:.2f}% | Conversions: {conv:.1f}\n\n"
            else:
                response += "✅ All keywords are performing well! No major underperformers detected.\n"

            return response

    elif agent == "insight":
        if action == "analyze_trends":
            insights = agent_data.get("insights", [])
            response = "📈 **Performance Trends:**\n\n"
            if insights:
                for insight in insights[:5]:
                    response += f"• {insight}\n"
            else:
                response += "No significant trends detected in recent data."
            return response

        elif action == "detect_anomalies":
            anomalies = agent_data.get("anomalies", [])
            recommendations = agent_data.get("recommendations", [])

            response = "🔍 **Anomaly Detection:**\n\n"
            if anomalies:
                response += f"Found {len(anomalies)} anomalies:\n\n"
                for anom in anomalies[:5]:
                    response += f"⚠️ {anom.get('type', 'Unknown')}: {anom.get('keyword', anom.get('campaign', 'N/A'))}\n"

                response += "\n**Recommendations:**\n"
                for rec in recommendations[:3]:
                    response += f"• {rec}\n"
            else:
                response += "✅ All metrics within expected ranges!"
            return response

    elif agent == "optimization":
        recommendations = agent_data.get("recommendations", [])

        if action == "optimize_budgets":
            response = "💰 **Budget Optimization:**\n\n"
        else:
            response = "📊 **Bid Optimization:**\n\n"

        if isinstance(recommendations, list) and len(recommendations) > 0:
            for rec in recommendations[:5]:
                if isinstance(rec, dict):
                    campaign = rec.get('campaign_name', 'Unknown')
                    action_type = rec.get('recommended_action', 'No action')
                    change = rec.get('recommended_change', rec.get('recommended_bid_adjustment', 'N/A'))
                    rationale = rec.get('rationale', '')

                    response += f"**{campaign}**\n"
                    response += f"Action: {action_type} ({change})\n"
                    response += f"Why: {rationale}\n\n"
                else:
                    response += f"• {rec.get('message', str(rec))}\n"
        else:
            response += "✅ Current allocation is optimal!"

        return response

    elif agent == "forecasting":
        forecast = agent_data.get("predicted_metrics", {})
        period = agent_data.get("forecast_period", "30 days")
        based_on = agent_data.get("based_on", "historical data")

        response = f"🔮 **Performance Forecast ({period}):**\n\n"
        response += f"_Based on: {based_on}_\n\n"
        response += "**Projected Metrics:**\n"
        response += f"• Impressions: {forecast.get('impressions', 0):,}\n"
        response += f"• Clicks: {forecast.get('clicks', 0):,}\n"
        response += f"• Conversions: {forecast.get('conversions', 0):.1f}\n"
        response += f"• Cost: ₹{forecast.get('cost', 0):,.2f}\n"
        response += f"• CTR: {forecast.get('ctr', 0):.2f}%\n"
        response += f"• Avg CPC: ₹{forecast.get('avg_cpc', 0):.2f}\n\n"

        daily = agent_data.get("daily_averages", {})
        if daily:
            response += "**Daily Averages:**\n"
            response += f"• ~{daily.get('clicks', 0):,} clicks/day\n"
            response += f"• ~₹{daily.get('cost', 0):,.2f} spend/day\n"

        return response

    elif agent == "orchestrator":
        # Orchestrator combines multiple agents - format campaigns and trends
        response = "📊 **Comprehensive Performance Analysis**\n\n"
        
        # Format campaigns data
        campaigns_data = agent_data.get("campaigns", {})
        if isinstance(campaigns_data, dict):
            campaigns = campaigns_data.get("campaigns", [])
            if isinstance(campaigns, list) and len(campaigns) > 0:
                # Sort by clicks descending
                active_campaigns = [c for c in campaigns if c.get('clicks', c.get('metrics', {}).get('clicks', 0)) > 0]
                if len(active_campaigns) == 0:
                    active_campaigns = campaigns[:5]
                
                active_campaigns.sort(key=lambda x: x.get('clicks', x.get('metrics', {}).get('clicks', 0)), reverse=True)
                top_5 = active_campaigns[:5]
                
                response += "**📈 Campaign Performance**\n"
                response += f"_{len(top_5)} campaigns shown, {len(campaigns)} total_\n\n"
                
                for i, c in enumerate(top_5, 1):
                    name = c.get('name', c.get('campaign_name', 'Unknown'))
                    status = c.get('status', 'ACTIVE')
                    clicks = c.get('clicks', c.get('metrics', {}).get('clicks', 0))
                    cost = c.get('cost', c.get('metrics', {}).get('cost', 0))
                    impressions = c.get('impressions', c.get('metrics', {}).get('impressions', 0))
                    ctr = c.get('ctr', c.get('metrics', {}).get('ctr', 0))
                    conv = c.get('conversions', c.get('metrics', {}).get('conversions', 0))
                    
                    if ctr == 0 and impressions > 0 and clicks > 0:
                        ctr = (clicks / impressions) * 100
                    elif ctr < 1 and ctr > 0:
                        ctr = ctr * 100
                    
                    response += f"{i}. **{name}** ({status})\n"
                    response += f"   Impressions: {impressions:,} | Clicks: {clicks:,}\n"
                    response += f"   CTR: {ctr:.2f}% | Cost: ₹{cost:,.2f}\n"
                    response += f"   Conversions: {conv:.1f}\n\n"
        
        # Format trends/insights data
        trends_data = agent_data.get("trends", {})
        if isinstance(trends_data, dict):
            insights = trends_data.get("insights", [])
            if isinstance(insights, list) and len(insights) > 0:
                response += "\n**💡 Key Insights:**\n\n"
                for insight in insights[:5]:
                    if isinstance(insight, str):
                        response += f"• {insight}\n"
                    elif isinstance(insight, dict):
                        response += f"• {insight.get('message', insight.get('insight', str(insight)))}\n"
                response += "\n"
        
        # If no data found, provide helpful message
        if len(response) < 150:  # Very short response means no data
            response += "I couldn't find detailed performance data. Please ensure:\n"
            response += "• Customer ID is correct\n"
            response += "• Data has been synced via ETL\n"
            response += "• Try asking more specific questions like 'show me top campaigns' or 'keyword performance'\n"
        
        return response

    # Default response
    return "I've processed your request. Here's what I found:\n\n" + str(agent_data.get("message", "Analysis complete"))

def enhance_with_gemini(user_query: str, technical_response: str, customer_name: Optional[str] = None) -> str:
    """
    Use Gemini to transform technical ADK responses into friendly, conversational replies
    """
    if not GEMINI_ENABLED:
        return technical_response

    try:
        customer_context = f"This data is for {customer_name}." if customer_name else ""

        prompt = f"""You are a friendly AI Marketing Assistant helping a marketing professional understand their Google Ads performance.

User asked: "{user_query}"
{customer_context}

The ADK multi-agent system provided this technical data:
{technical_response}

Your task:
1. Keep all the data and numbers EXACTLY as shown (don't change metrics)
2. Make the response warm, conversational, and encouraging
3. If customer name is provided, naturally reference it (e.g., "for {customer_name}" or "{customer_name}'s campaigns")
4. Add helpful context or insights where appropriate
5. Use emojis sparingly and naturally
6. Keep the markdown formatting for better readability
7. Be concise - don't add unnecessary fluff
8. Maintain a professional yet friendly tone

Transform this into a friendly response that feels like talking to a knowledgeable colleague:"""

        response = gemini_model.generate_content(prompt)
        return response.text

    except Exception as e:
        print(f"Gemini enhancement failed: {e}")
        return technical_response  # Fallback to technical response


@app.get("/")
def root():
    return {
        "service": "ADK Chatbot API",
        "version": "1.0.0",
        "status": "active",
        "adk_available": ADK_AVAILABLE,
        "endpoint": "/api/chat"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "adk_agents": "available" if ADK_AVAILABLE else "unavailable",
        "gemini_enabled": GEMINI_ENABLED,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user messages through ADK agents
    """
    try:
        user_message = request.message
        customer_id = request.customer_id
        campaign_type = request.campaign_type
        date_range = request.date_range

        # Get customer info for better context
        customer_info = get_customer_info(customer_id) if customer_id else None
        customer_name = customer_info.get('customer_name') if customer_info else None

        print(f"\n{'#'*80}", flush=True)
        print(f"[NEW CHAT REQUEST RECEIVED]", flush=True)
        print(f"{'#'*80}", flush=True)
        print(f"User Message: '{user_message}'", flush=True)
        print(f"Customer ID: {customer_id or 'Not specified'}", flush=True)
        print(f"Customer Name: {customer_name or 'Not found'}", flush=True)
        print(f"Campaign Type: {campaign_type or 'All types'}", flush=True)
        print(f"Date Range: {date_range or 'All time'}", flush=True)
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
        print(f"{'#'*80}\n", flush=True)

        # Step 1: Classify intent
        print(f"[STEP 1] Classifying user intent...", flush=True)
        intent = classify_user_intent(user_message)
        print(f">> Intent classified: Agent='{intent.get('agent')}', Action='{intent.get('action')}'", flush=True)
        print(f"   Keywords detected: {intent.get('keywords', [])}\n", flush=True)

        # Step 2: Execute agent action with filters
        print(f"[STEP 2] Executing ADK agent action...", flush=True)
        agent_data = execute_agent_action(intent, customer_id, campaign_type, date_range)
        print(f">> Agent execution complete\n", flush=True)

        # Step 3: Format response
        print(f"[STEP 3] Formatting response for user...", flush=True)
        formatted_response = format_response(user_message, intent, agent_data)
        print(f">> Response formatted ({len(formatted_response)} characters)\n", flush=True)

        # Step 4: Enhance with Gemini for friendly, conversational tone
        print(f"[STEP 4] Enhancing response with Gemini AI...", flush=True)
        final_response = enhance_with_gemini(user_message, formatted_response, customer_name)
        if GEMINI_ENABLED:
            print(f">> Gemini enhancement complete ({len(final_response)} characters)\n", flush=True)
        else:
            print(f"WARNING: Gemini not available, using standard formatting\n", flush=True)

        print(f"{'='*80}", flush=True)
        print(f"[RESPONSE READY] Sending back to frontend", flush=True)
        print(f"   Agent used: {intent.get('agent')}", flush=True)
        print(f"   Data available: {'Yes' if 'error' not in agent_data else 'No'}", flush=True)
        print(f"   Response length: {len(final_response)} chars", flush=True)
        print(f"{'='*80}\n", flush=True)

        return ChatResponse(
            response=final_response,
            metadata={
                "intent": intent,
                "data_available": "error" not in agent_data,
                "gemini_enhanced": GEMINI_ENABLED
            },
            timestamp=datetime.now(),
            agent_used=intent.get("agent")
        )

    except Exception as e:
        return ChatResponse(
            response=f"⚠️ Sorry, I encountered an error: {str(e)}",
            metadata={"error": str(e)},
            timestamp=datetime.now(),
            agent_used="error"
        )

@app.get("/api/agents")
def list_agents():
    """List available ADK agents"""
    return {
        "agents": [
            {"name": "Data Agent", "type": "data", "status": "active" if ADK_AVAILABLE else "unavailable"},
            {"name": "Insight Agent", "type": "insight", "status": "active" if ADK_AVAILABLE else "unavailable"},
            {"name": "Optimization Agent", "type": "optimization", "status": "active" if ADK_AVAILABLE else "unavailable"},
            {"name": "Forecasting Agent", "type": "forecasting", "status": "active" if ADK_AVAILABLE else "unavailable"},
            {"name": "Orchestrator", "type": "orchestrator", "status": "active" if ADK_AVAILABLE else "unavailable"}
        ]
    }

if __name__ == "__main__":
    import uvicorn
    print("Starting ADK Chatbot API on port 8003...")
    print(f"ADK Agents Available: {ADK_AVAILABLE}")
    uvicorn.run(app, host="0.0.0.0", port=8003)
