#!/usr/bin/env python3
"""
FastAPI REST API for Google Ads Multi-Agent System
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any, Literal
from datetime import datetime
import asyncio
import os
import sys
from loguru import logger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.google_ads.client_manager import GoogleAdsClientManager
from src.agents.orchestrator_agent import OrchestratorAgent

app = FastAPI(
    title="Google Ads Multi-Agent API",
    description="REST API for Multi-Agent Google Ads Management System",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client_manager = None
orchestrator = None

class AgentRequest(BaseModel):
    agent_type: Literal["data", "insight", "optimization", "forecasting", "orchestrator"]
    customer_id: str
    action: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = {}

class OrchestratorRequest(BaseModel):
    customer_id: str
    analysis_type: Literal["comprehensive", "performance", "optimization", "forecasting"] = "comprehensive"
    workflow: Optional[Dict[str, Any]] = None

class AgentInfo(BaseModel):
    name: str
    type: str
    description: str
    available_actions: List[str]
    status: str

class AgentResponse(BaseModel):
    success: bool
    agent: str
    action: str
    data: Any
    timestamp: datetime
    error: Optional[str] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the Google Ads client and orchestrator on startup"""
    global client_manager, orchestrator
    try:
        client_manager = GoogleAdsClientManager()
        orchestrator = OrchestratorAgent(client_manager)
        logger.info("Multi-Agent system initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize multi-agent system: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "Google Ads Multi-Agent API",
        "version": "1.0.0",
        "status": "active",
        "endpoints": {
            "agents": "/api/agents",
            "orchestrate": "/api/orchestrate",
            "execute": "/api/agent/execute",
            "agent_status": "/api/agents/status"
        }
    }

@app.get("/api/agents", response_model=List[AgentInfo])
async def list_agents():
    """List all available agents for UI dropdown"""
    agents = [
        AgentInfo(
            name="Data Agent",
            type="data",
            description="Retrieves and processes Google Ads campaign, ad group, keyword, and search term data",
            available_actions=[
                "get_campaign_performance",
                "get_ad_group_performance",
                "get_keyword_performance",
                "get_search_terms",
                "get_ml_features"
            ],
            status="active"
        ),
        AgentInfo(
            name="Insight Agent",
            type="insight",
            description="Analyzes performance data to generate insights, detect anomalies, and identify trends",
            available_actions=[
                "analyze_performance",
                "detect_anomalies",
                "analyze_trends",
                "competitor_analysis",
                "calculate_roi"
            ],
            status="active"
        ),
        AgentInfo(
            name="Optimization Agent",
            type="optimization",
            description="Provides optimization recommendations for bids, budgets, and campaigns",
            available_actions=[
                "optimize_bids",
                "optimize_budgets",
                "optimize_campaigns",
                "keyword_recommendations",
                "ad_copy_suggestions"
            ],
            status="active"
        ),
        AgentInfo(
            name="Forecasting Agent",
            type="forecasting",
            description="Predicts future performance and analyzes different scenarios",
            available_actions=[
                "forecast_performance",
                "analyze_scenarios",
                "predict_conversions",
                "budget_forecasting"
            ],
            status="active"
        ),
        AgentInfo(
            name="Orchestrator Agent",
            type="orchestrator",
            description="Coordinates multiple agents to perform comprehensive analysis",
            available_actions=[
                "comprehensive_analysis",
                "performance_analysis",
                "optimization_analysis",
                "forecasting_analysis"
            ],
            status="active"
        )
    ]
    return agents

@app.get("/api/agents/status")
async def get_agents_status():
    """Get the status of all agents"""
    if not orchestrator:
        raise HTTPException(status_code=503, detail="Orchestrator not initialized")

    return orchestrator.get_agent_status()

@app.post("/api/agent/execute", response_model=AgentResponse)
async def execute_agent_action(request: AgentRequest):
    """Execute a specific action with a selected agent"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=503, detail="System not initialized")

        agent = None
        result = None

        if request.agent_type == "data":
            agent = orchestrator.data_agent

            if request.action == "get_campaign_performance":
                result = agent.get_campaign_performance(request.customer_id)
            elif request.action == "get_ad_group_performance":
                result = agent.get_ad_group_performance(request.customer_id)
            elif request.action == "get_keyword_performance":
                result = agent.get_keyword_performance(request.customer_id)
            elif request.action == "get_search_terms":
                result = agent.get_search_terms(request.customer_id)
            elif request.action == "get_ml_features":
                result = agent.get_ml_features(request.customer_id)
            else:
                raise ValueError(f"Unknown action for data agent: {request.action}")

        elif request.agent_type == "insight":
            agent = orchestrator.insight_agent

            campaign_data = request.parameters.get("campaign_data")
            if not campaign_data:
                data_agent = orchestrator.data_agent
                campaign_data = data_agent.get_campaign_performance(request.customer_id)

            if request.action == "analyze_performance":
                result = agent.analyze_performance(campaign_data)
            elif request.action == "detect_anomalies":
                result = agent.detect_anomalies(campaign_data)
            elif request.action == "analyze_trends":
                result = agent.analyze_trends(campaign_data)
            elif request.action == "competitor_analysis":
                result = agent.competitor_analysis(campaign_data)
            elif request.action == "calculate_roi":
                result = agent.calculate_roi(campaign_data)
            else:
                raise ValueError(f"Unknown action for insight agent: {request.action}")

        elif request.agent_type == "optimization":
            agent = orchestrator.optimization_agent

            campaign_data = request.parameters.get("campaign_data")
            if not campaign_data:
                data_agent = orchestrator.data_agent
                campaign_data = data_agent.get_campaign_performance(request.customer_id)

            if request.action == "optimize_bids":
                result = agent.optimize_bids(campaign_data)
            elif request.action == "optimize_budgets":
                result = agent.optimize_budgets(campaign_data)
            elif request.action == "optimize_campaigns":
                result = agent.optimize_campaigns(campaign_data)
            else:
                raise ValueError(f"Unknown action for optimization agent: {request.action}")

        elif request.agent_type == "forecasting":
            agent = orchestrator.forecasting_agent

            campaign_data = request.parameters.get("campaign_data")
            if not campaign_data:
                data_agent = orchestrator.data_agent
                campaign_data = data_agent.get_campaign_performance(request.customer_id)

            if request.action == "forecast_performance":
                result = agent.forecast_performance(campaign_data)
            elif request.action == "analyze_scenarios":
                result = agent.analyze_scenarios(campaign_data)
            else:
                raise ValueError(f"Unknown action for forecasting agent: {request.action}")

        elif request.agent_type == "orchestrator":
            analysis_type = request.parameters.get("analysis_type", "comprehensive")
            result = await orchestrator.coordinate_analysis(request.customer_id, analysis_type)
        else:
            raise ValueError(f"Unknown agent type: {request.agent_type}")

        return AgentResponse(
            success=True,
            agent=request.agent_type,
            action=request.action or "default",
            data=result,
            timestamp=datetime.now()
        )

    except Exception as e:
        logger.error(f"Error executing agent action: {str(e)}")
        return AgentResponse(
            success=False,
            agent=request.agent_type,
            action=request.action or "unknown",
            data=None,
            timestamp=datetime.now(),
            error=str(e)
        )

@app.post("/api/orchestrate")
async def orchestrate_analysis(request: OrchestratorRequest):
    """Trigger the orchestrator to coordinate multiple agents"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")

        if request.workflow:
            result = await orchestrator.execute_workflow({
                "customer_id": request.customer_id,
                **request.workflow
            })
        else:
            result = await orchestrator.coordinate_analysis(
                request.customer_id,
                request.analysis_type
            )

        return {
            "success": True,
            "customer_id": request.customer_id,
            "analysis_type": request.analysis_type,
            "data": result,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"Error in orchestration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/agent/{agent_type}/actions")
async def get_agent_actions(agent_type: str):
    """Get available actions for a specific agent type"""
    actions_map = {
        "data": [
            {"name": "get_campaign_performance", "description": "Get campaign performance metrics"},
            {"name": "get_ad_group_performance", "description": "Get ad group performance metrics"},
            {"name": "get_keyword_performance", "description": "Get keyword performance metrics"},
            {"name": "get_search_terms", "description": "Get search term data"},
            {"name": "get_ml_features", "description": "Get ML features for analysis"}
        ],
        "insight": [
            {"name": "analyze_performance", "description": "Analyze overall performance"},
            {"name": "detect_anomalies", "description": "Detect anomalies in data"},
            {"name": "analyze_trends", "description": "Analyze trends over time"},
            {"name": "competitor_analysis", "description": "Analyze competitive landscape"},
            {"name": "calculate_roi", "description": "Calculate ROI metrics"}
        ],
        "optimization": [
            {"name": "optimize_bids", "description": "Optimize bidding strategies"},
            {"name": "optimize_budgets", "description": "Optimize budget allocation"},
            {"name": "optimize_campaigns", "description": "Optimize campaign settings"}
        ],
        "forecasting": [
            {"name": "forecast_performance", "description": "Forecast future performance"},
            {"name": "analyze_scenarios", "description": "Analyze what-if scenarios"}
        ],
        "orchestrator": [
            {"name": "comprehensive_analysis", "description": "Run comprehensive multi-agent analysis"},
            {"name": "performance_analysis", "description": "Run performance-focused analysis"},
            {"name": "optimization_analysis", "description": "Run optimization-focused analysis"},
            {"name": "forecasting_analysis", "description": "Run forecasting-focused analysis"}
        ]
    }

    if agent_type not in actions_map:
        raise HTTPException(status_code=404, detail=f"Agent type '{agent_type}' not found")

    return {
        "agent_type": agent_type,
        "actions": actions_map[agent_type]
    }

@app.post("/api/workflow/create")
async def create_custom_workflow(workflow: Dict[str, Any]):
    """Create and execute a custom workflow with multiple agents"""
    try:
        if not orchestrator:
            raise HTTPException(status_code=503, detail="Orchestrator not initialized")

        result = await orchestrator.execute_workflow(workflow)

        return {
            "success": True,
            "workflow": workflow,
            "result": result,
            "timestamp": datetime.now()
        }

    except Exception as e:
        logger.error(f"Error executing workflow: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Google Ads Multi-Agent API",
        "timestamp": datetime.now(),
        "orchestrator_status": "active" if orchestrator else "not_initialized"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)