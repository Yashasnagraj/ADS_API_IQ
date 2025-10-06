#!/usr/bin/env python3
"""
ADK Chatbot API - Connects Google ADK Orchestration Agent to MarketingIQ Platform
Provides conversational interface to multi-agent system
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import the root agent from orchestration_agent
try:
    from adk.orchestration_agent.agent import (
        root_agent,
        get_campaign_performance,
        get_keyword_performance,
        get_ad_group_performance,
        analyze_performance_trends,
        detect_anomalies,
        optimize_bids,
        optimize_budgets,
        forecast_performance
    )
    ADK_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Could not import ADK agents: {e}")
    ADK_AVAILABLE = False

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
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime
    agent_used: Optional[str] = None

# Simple intent mapping (no Gemini needed for basic routing)
def classify_user_intent(message: str) -> Dict[str, Any]:
    """
    Simple keyword-based intent classification
    """
    message_lower = message.lower()

    # Campaign queries
    if any(word in message_lower for word in ['campaign', 'campaigns', 'top performer', 'best campaign']):
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

    # Performance analysis/trends
    if any(word in message_lower for word in ['trend', 'performance', 'analyze', 'insight', 'how is']):
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
    if any(word in message_lower for word in ['budget', 'spend', 'allocate', 'reallocate']):
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

    # Forecasting
    if any(word in message_lower for word in ['forecast', 'predict', 'projection', 'future', 'next month']):
        return {
            "agent": "forecasting",
            "action": "forecast_performance",
            "keywords": ["forecast"]
        }

    # Default to orchestrator for comprehensive analysis
    return {
        "agent": "orchestrator",
        "action": "comprehensive",
        "keywords": []
    }

def execute_agent_action(intent: Dict, customer_id: Optional[str] = None) -> Dict[str, Any]:
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

        # Data Agent actions
        if agent == "data":
            if action == "campaign_performance":
                return get_campaign_performance(customer_id)
            elif action == "keyword_performance":
                return get_keyword_performance(customer_id)
            elif action == "adgroup_performance":
                return get_ad_group_performance(customer_id)

        # Insight Agent actions
        elif agent == "insight":
            if action == "analyze_trends":
                return analyze_performance_trends()
            elif action == "detect_anomalies":
                return detect_anomalies()

        # Optimization Agent actions
        elif agent == "optimization":
            if action == "optimize_budgets":
                return optimize_budgets()
            elif action == "optimize_bids":
                return optimize_bids()

        # Forecasting Agent actions
        elif agent == "forecasting":
            if action == "forecast_performance":
                return forecast_performance(30)  # Default 30 days

        # Orchestrator - use root agent for complex queries
        elif agent == "orchestrator":
            # For now, return a combined summary
            campaign_data = get_campaign_performance(customer_id)
            trends = analyze_performance_trends()
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
        if action == "campaign_performance":
            campaigns = agent_data.get("campaigns", [])
            if isinstance(campaigns, list) and len(campaigns) > 0:
                top_5 = campaigns[:5]
                response = "📊 **Top Performing Campaigns:**\n\n"
                for i, c in enumerate(top_5, 1):
                    name = c.get('campaign_name', 'Unknown')
                    clicks = c.get('clicks', 0)
                    cost = c.get('cost', 0)
                    conv = c.get('conversions', 0)
                    response += f"{i}. **{name}**\n   - Clicks: {clicks:,} | Cost: ₹{cost:,.2f} | Conversions: {conv}\n\n"
                return response

        elif action == "keyword_performance":
            keywords = agent_data.get("keywords", [])
            underperformers = agent_data.get("underperforming_keywords", [])

            response = f"🔑 **Keyword Analysis:**\n\n"
            response += f"Total Keywords: {len(keywords) if isinstance(keywords, list) else 0}\n"
            response += f"Underperforming: {len(underperformers) if isinstance(underperformers, list) else 0}\n\n"

            if isinstance(underperformers, list) and len(underperformers) > 0:
                response += "**Top Underperformers:**\n"
                for kw in underperformers[:3]:
                    response += f"- {kw.get('keyword_text', 'Unknown')} (Quality Score: {kw.get('quality_score', 'N/A')})\n"

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
        response = "🔮 **30-Day Forecast:**\n\n"
        response += f"Expected Clicks: {forecast.get('clicks', 'N/A'):,}\n"
        response += f"Expected Conversions: {forecast.get('conversions', 'N/A')}\n"
        response += f"Projected Cost: ₹{forecast.get('cost', 0):,.2f}\n"
        return response

    # Default response
    return "I've processed your request. Here's what I found:\n\n" + str(agent_data.get("message", "Analysis complete"))


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

        # Step 1: Classify intent
        intent = classify_user_intent(user_message)

        # Step 2: Execute agent action
        agent_data = execute_agent_action(intent, customer_id)

        # Step 3: Format response
        formatted_response = format_response(user_message, intent, agent_data)

        return ChatResponse(
            response=formatted_response,
            metadata={
                "intent": intent,
                "data_available": "error" not in agent_data
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
