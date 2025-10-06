from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
import uvicorn

# Load environment variables
load_dotenv()

# Import agents
from src.agents.data_agent.agent import DataAgent
from src.agents.insight_agent.agent import InsightAgent
from src.agents.optimization_agent.agent import OptimizationAgent
from src.agents.forecasting_agent.agent import ForecastingAgent
from src.google_ads.client_manager import GoogleAdsClientManager

# Initialize FastAPI app
app = FastAPI(
    title="Google Ads Multi-Agent ADK",
    description="AI-powered Google Ads management system",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Google Ads client
client_manager = GoogleAdsClientManager()

# Initialize agents
data_agent = DataAgent(client_manager)
insight_agent = InsightAgent()
optimization_agent = OptimizationAgent()
forecasting_agent = ForecastingAgent()

# Request models
class AgentRequest(BaseModel):
    agent_type: str
    action: str
    parameters: Dict[str, Any]
    customer_id: Optional[str] = None

class CampaignRequest(BaseModel):
    customer_id: str
    campaign_id: Optional[str] = None

class OptimizationRequest(BaseModel):
    customer_id: str
    campaign_id: str
    optimization_type: str
    parameters: Dict[str, Any]

# Routes
@app.get("/")
async def root():
    return {
        "message": "Google Ads Multi-Agent ADK API",
        "status": "running",
        "available_agents": [
            "data_agent",
            "insight_agent",
            "optimization_agent",
            "forecasting_agent"
        ]
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/agent/execute")
async def execute_agent(request: AgentRequest):
    try:
        if request.agent_type == "data":
            result = await data_agent.execute(
                action=request.action,
                parameters=request.parameters,
                customer_id=request.customer_id
            )
        elif request.agent_type == "insight":
            result = await insight_agent.analyze(
                data=request.parameters
            )
        elif request.agent_type == "optimization":
            result = await optimization_agent.optimize(
                parameters=request.parameters
            )
        elif request.agent_type == "forecasting":
            result = await forecasting_agent.forecast(
                parameters=request.parameters
            )
        else:
            raise HTTPException(status_code=400, detail=f"Unknown agent type: {request.agent_type}")

        return {"success": True, "result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns/{customer_id}")
async def get_campaigns(customer_id: str):
    try:
        campaigns = await data_agent.get_campaigns(customer_id)
        return {"success": True, "campaigns": campaigns}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaign/{customer_id}/{campaign_id}/performance")
async def get_campaign_performance(customer_id: str, campaign_id: str):
    try:
        performance = await data_agent.get_campaign_performance(
            customer_id=customer_id,
            campaign_id=campaign_id
        )
        return {"success": True, "performance": performance}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/optimize")
async def optimize_campaign(request: OptimizationRequest):
    try:
        result = await optimization_agent.optimize_campaign(
            customer_id=request.customer_id,
            campaign_id=request.campaign_id,
            optimization_type=request.optimization_type,
            parameters=request.parameters
        )
        return {"success": True, "optimization_result": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/forecast")
async def forecast_performance(request: Dict[str, Any]):
    try:
        result = await forecasting_agent.forecast_performance(
            data=request.get("data"),
            period=request.get("period", 30),
            metrics=request.get("metrics", ["clicks", "impressions", "cost"])
        )
        return {"success": True, "forecast": result}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/insights")
async def get_insights(request: Dict[str, Any]):
    try:
        insights = await insight_agent.generate_insights(
            data=request.get("data"),
            analysis_type=request.get("analysis_type", "comprehensive")
        )
        return {"success": True, "insights": insights}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    port = int(os.getenv("API_PORT", 8000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        reload=True
    )