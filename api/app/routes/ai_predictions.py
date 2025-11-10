"""
AI Predictive Alerts API Endpoints
Monitors performance and predicts potential issues
"""
from fastapi import APIRouter
from datetime import datetime, timedelta
from typing import List
from pydantic import BaseModel

router = APIRouter()

@router.get("/predictions/alerts")
async def get_predictive_alerts(customer_id: int, days: int = 7):
    """Get predictive alerts for potential issues"""

    # Simplified mock alerts - in production would query real data
    alerts = [
        {
            "id": "alert_demo_1",
            "severity": "info",
            "type": "status",
            "title": "All Systems Operational",
            "description": "Your campaigns are performing within expected parameters.",
            "impact": "No immediate action required",
            "recommendation": "Continue monitoring and consider A/B testing new ad copy.",
            "metric_value": None,
            "threshold": None,
            "trend": "stable",
            "affected_entity": "Overall account",
            "created_at": datetime.now().isoformat()
        }
    ]

    return {
        "success": True,
        "total_alerts": len(alerts),
        "critical": 0,
        "warnings": 0,
        "info": len(alerts),
        "alerts": alerts
    }

@router.get("/predictions/forecast")
async def get_performance_forecast(
    customer_id: int,
    metric: str = "spend",
    days_ahead: int = 7
):
    """Forecast future performance based on historical trends"""

    # Simplified mock forecast
    forecast = []
    base_value = 1000 if metric == "spend" else 50

    for i in range(days_ahead):
        future_date = (datetime.now() + timedelta(days=i+1)).date()
        forecast.append({
            "date": str(future_date),
            "value": round(base_value * (1 + i * 0.05), 2),
            "confidence": max(90 - (i * 5), 50)
        })

    return {
        "success": True,
        "metric": metric,
        "forecast": forecast,
        "trend": "increasing",
        "trend_percentage": 5.0
    }
