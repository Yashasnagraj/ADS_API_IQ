#!/usr/bin/env python3
"""
AI Chatbot API with ADK Orchestrator Integration
Powered by Google Gemini 2.0 Flash for natural language understanding
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime
import requests
import google.generativeai as genai
import os
from loguru import logger

# Initialize FastAPI
app = FastAPI(
    title="MarketingIQ Chatbot API",
    description="AI Chatbot with ADK Multi-Agent Integration",
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

# Configure Gemini
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "AIzaSyBl0nVSVKcQGZBT-kdjTr4c8pZ1DnJqNKs")
genai.configure(api_key=GEMINI_API_KEY)

# Initialize Gemini model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# ADK Orchestrator URL
# The root_agent from orchestration_agent.agent can be accessed via ADK server (port 9001)
# OR we can use the custom agent_api.py wrapper (port 8001) - NOT WORKING
# For now, we'll call the Data API directly and use Gemini for responses
ADK_ORCHESTRATOR_URL = os.getenv("ADK_URL", "http://localhost:9001")
DATA_API_URL = "http://localhost:8004"

# Request/Response Models
class ChatRequest(BaseModel):
    message: str
    customer_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None

class ChatResponse(BaseModel):
    response: str
    metadata: Optional[Dict[str, Any]] = None
    timestamp: datetime

# Conversation history (in-memory, can be replaced with Redis/DB)
conversation_history: Dict[str, List[Dict]] = {}

def classify_intent(message: str) -> Dict[str, Any]:
    """
    Use Gemini to classify user intent and extract entities
    """
    prompt = f"""
You are an AI assistant for a Google Ads management platform. Analyze this user message and classify its intent.

User Message: "{message}"

Respond in this exact JSON format:
{{
  "intent": "one of: campaign_query, keyword_analysis, budget_optimization, performance_forecast, general_question, anomaly_detection",
  "entities": {{
    "metric": "if mentioned: impressions, clicks, ctr, conversions, roas, cost, etc.",
    "time_period": "if mentioned: today, yesterday, last_week, last_month, etc.",
    "campaign_name": "if mentioned",
    "specific_request": "brief description of what user wants"
  }},
  "requires_data": true/false
}}

Examples:
- "Show top campaigns" → intent: campaign_query, requires_data: true
- "What are my underperforming keywords?" → intent: keyword_analysis, requires_data: true
- "How should I optimize my budget?" → intent: budget_optimization, requires_data: true
- "What is ROAS?" → intent: general_question, requires_data: false
"""

    try:
        response = model.generate_content(prompt)
        import json
        intent_data = json.loads(response.text.strip())
        return intent_data
    except Exception as e:
        logger.error(f"Intent classification error: {e}")
        return {
            "intent": "general_question",
            "entities": {},
            "requires_data": False
        }

def query_adk_orchestrator(intent_data: Dict, customer_id: Optional[str]) -> Dict:
    """
    Query the data API directly based on classified intent
    Falls back to Data API (port 8004) since ADK orchestrator may not be running
    """
    try:
        intent = intent_data.get("intent")
        entities = intent_data.get("entities", {})

        # Map intent to Data API endpoints (direct calls)
        if intent == "campaign_query":
            # Get top campaigns from Data API
            response = requests.get(
                f"{DATA_API_URL}/campaigns/top-performers",
                params={"metric": "ctr"},
                timeout=10
            )
            campaigns = response.json()

            # Also get metrics summary
            metrics_response = requests.get(f"{DATA_API_URL}/metrics/summary", timeout=10)
            metrics = metrics_response.json()

            return {
                "success": True,
                "campaigns": campaigns,
                "metrics": metrics
            }

        elif intent == "keyword_analysis":
            # Get keywords from Data API
            response = requests.get(f"{DATA_API_URL}/keywords", timeout=10)
            keywords = response.json()

            # Filter underperformers (quality score < 5)
            underperformers = [k for k in keywords if k.get('quality_score', 10) < 5]

            return {
                "success": True,
                "total_keywords": len(keywords),
                "underperformers": underperformers[:10],
                "message": f"Found {len(underperformers)} underperforming keywords"
            }

        elif intent == "budget_optimization":
            # Get campaign performance data
            response = requests.get(f"{DATA_API_URL}/metrics/by-campaign", timeout=10)
            campaigns = response.json()

            return {
                "success": True,
                "campaigns": campaigns,
                "message": "Budget optimization recommendations based on campaign performance"
            }

        elif intent == "performance_forecast":
            # Get trends data
            response = requests.get(f"{DATA_API_URL}/metrics/trends", timeout=10)
            trends = response.json()

            return {
                "success": True,
                "trends": trends,
                "message": "Performance forecast based on historical trends"
            }

        elif intent == "anomaly_detection":
            # Get campaign metrics
            response = requests.get(f"{DATA_API_URL}/metrics/by-campaign", timeout=10)
            campaigns = response.json()

            # Simple anomaly detection: campaigns with low CTR or high cost
            anomalies = []
            for c in campaigns:
                if c.get('ctr', 0) < 1.0:
                    anomalies.append({"campaign": c.get('campaign_name'), "issue": "Low CTR", "value": c.get('ctr')})
                if c.get('cost', 0) > 1000:
                    anomalies.append({"campaign": c.get('campaign_name'), "issue": "High Cost", "value": c.get('cost')})

            return {
                "success": True,
                "anomalies": anomalies,
                "message": f"Detected {len(anomalies)} potential issues"
            }

        else:
            # General question - no API call needed
            return {"data": None}

    except Exception as e:
        logger.error(f"Data API query error: {e}")
        return {"error": str(e), "data": None}

def format_response_with_gemini(
    user_message: str,
    intent_data: Dict,
    adk_data: Dict
) -> str:
    """
    Use Gemini to format a natural, conversational response
    """
    intent = intent_data.get("intent")
    requires_data = intent_data.get("requires_data", False)

    if not requires_data:
        # Answer general questions directly
        prompt = f"""
You are a helpful AI assistant for Google Ads campaign management. Answer this question concisely and professionally:

Question: {user_message}

Provide a clear, helpful answer in 2-3 sentences. Use markdown formatting for emphasis.
"""
    else:
        # Format data-driven response
        prompt = f"""
You are a helpful AI assistant for Google Ads campaign management. The user asked:

"{user_message}"

Here's the data from our analytics system:
{adk_data}

Create a natural, conversational response that:
1. Directly answers the user's question
2. Highlights key insights from the data
3. Provides 2-3 actionable recommendations
4. Uses markdown formatting for readability (bold, bullets, etc.)
5. Keeps response concise (4-6 sentences max)

Be friendly and professional. Use emojis sparingly (1-2 max).
"""

    try:
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        logger.error(f"Response formatting error: {e}")
        return "I'm sorry, I encountered an error processing your request. Please try rephrasing your question."

@app.get("/")
def root():
    return {
        "service": "MarketingIQ Chatbot API",
        "version": "1.0.0",
        "status": "active",
        "powered_by": "Google Gemini 2.0 Flash + ADK Multi-Agent System"
    }

@app.get("/health")
def health_check():
    """Health check endpoint"""
    # Check ADK connection
    adk_status = "unknown"
    try:
        response = requests.get(f"{ADK_ORCHESTRATOR_URL}/health", timeout=5)
        adk_status = "connected" if response.status_code == 200 else "unreachable"
    except:
        adk_status = "unreachable"

    return {
        "status": "healthy",
        "gemini": "configured",
        "adk_orchestrator": adk_status,
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Main chat endpoint - processes user messages through:
    1. Gemini intent classification
    2. ADK orchestrator query (if needed)
    3. Gemini response formatting
    """
    try:
        user_message = request.message
        customer_id = request.customer_id

        logger.info(f"Chat request: {user_message[:100]}...")

        # Step 1: Classify intent with Gemini
        intent_data = classify_intent(user_message)
        logger.info(f"Intent: {intent_data.get('intent')}")

        # Step 2: Query ADK if data is required
        adk_data = None
        if intent_data.get("requires_data"):
            adk_data = query_adk_orchestrator(intent_data, customer_id)
            logger.info(f"ADK response received")

        # Step 3: Format response with Gemini
        formatted_response = format_response_with_gemini(
            user_message,
            intent_data,
            adk_data
        )

        return ChatResponse(
            response=formatted_response,
            metadata={
                "intent": intent_data.get("intent"),
                "adk_called": intent_data.get("requires_data"),
            },
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat/clear")
async def clear_history(session_id: str):
    """Clear conversation history for a session"""
    if session_id in conversation_history:
        del conversation_history[session_id]
    return {"status": "cleared", "session_id": session_id}

@app.get("/api/intents")
async def get_available_intents():
    """Get list of supported intents"""
    return {
        "intents": [
            {
                "name": "campaign_query",
                "description": "Query campaign performance data",
                "examples": ["Show top campaigns", "List my active campaigns"]
            },
            {
                "name": "keyword_analysis",
                "description": "Analyze keyword performance",
                "examples": ["What keywords are underperforming?", "Show keyword quality scores"]
            },
            {
                "name": "budget_optimization",
                "description": "Get budget optimization recommendations",
                "examples": ["How should I optimize my budget?", "Reallocate my campaign budgets"]
            },
            {
                "name": "performance_forecast",
                "description": "Forecast future performance",
                "examples": ["Predict next month's spend", "Forecast my CTR"]
            },
            {
                "name": "anomaly_detection",
                "description": "Detect performance anomalies",
                "examples": ["Are there any issues with my campaigns?", "Detect anomalies"]
            },
            {
                "name": "general_question",
                "description": "Answer general Google Ads questions",
                "examples": ["What is ROAS?", "How does Quality Score work?"]
            }
        ]
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting Chatbot API on port 8002...")
    uvicorn.run(app, host="0.0.0.0", port=8002)
