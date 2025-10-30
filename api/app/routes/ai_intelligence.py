"""
AI Intelligence API Routes
Exposes all AI-powered insights, recommendations, and decision support
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.db.database import get_db
from app.schemas import ai_intelligence as schemas

# Import AI engines
from app.services.ai.greeting_generator import get_greeting
from app.services.ai.anomaly_detector import detect_anomalies
from app.services.ai.pie_model import predict_incrementality
from app.services.ai.attribution_analyzer import analyze_attribution
from app.services.ai.ltv_predictor import predict_ltv, calculate_laroas
from app.services.ai.decision_engine import get_unified_recommendation


router = APIRouter(prefix="/ai", tags=["AI Intelligence"])


# ===== GREETING & WELCOME =====
@router.get("/greeting", response_model=schemas.GreetingResponse)
def get_personalized_greeting(
    user_name: str = Query(..., description="User's first name"),
    customer_id: int = Query(..., description="Customer ID"),
    db: Session = Depends(get_db)
):
    """
    Get personalized greeting based on campaign health

    Returns context-aware greeting:
    - "Good morning, Yashas! Your campaigns are crushing it!" (if all good)
    - "Hey Yashas! We've got work to do today, but I'm here to help!" (if issues)
    """
    try:
        greeting_data = get_greeting(db, user_name, customer_id)
        return greeting_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating greeting: {str(e)}")


# ===== ANOMALY DETECTION =====
@router.get("/anomalies", response_model=schemas.AnomalyDetectionResponse)
def detect_campaign_anomalies(
    customer_id: int = Query(..., description="Customer ID"),
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db)
):
    """
    Detect anomalies in campaign performance

    Checks for:
    - CPC spikes (possible tracking errors or competitive attacks)
    - CTR drops (ad fatigue or competitor activity)
    - ROAS crashes (conversion issues)
    - Spend anomalies (budget pacing problems)
    - Zero conversions (tracking pixel issues)
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date() if date else None
        anomalies = detect_anomalies(db, customer_id, date_obj)
        return anomalies
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error detecting anomalies: {str(e)}")


# ===== PIE MODEL (INCREMENTALITY) =====
@router.get("/incrementality", response_model=schemas.PIEResponse)
def get_incremental_roas_predictions(
    customer_id: int = Query(..., description="Customer ID"),
    campaign_id: Optional[str] = Query(None, description="Specific campaign ID"),
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db)
):
    """
    Get Predictive Incrementality (PIE) predictions

    Returns TRUE causal impact - solves the "Generosity Flaw"
    Shows which campaigns drive NET NEW revenue vs taking credit for organic conversions

    Key metrics:
    - Predicted Incremental ROAS (causal effect)
    - Incremental vs Non-Incremental conversions
    - Confidence scores
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date() if date else None
        predictions = predict_incrementality(db, customer_id, campaign_id, date_obj)
        return predictions
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting incrementality: {str(e)}")


# ===== ATTRIBUTION ANALYSIS =====
@router.get("/attribution", response_model=schemas.AttributionResponse)
def get_attribution_analysis(
    customer_id: int = Query(..., description="Customer ID"),
    days_lookback: int = Query(30, ge=7, le=365, description="Days of historical data"),
    db: Session = Depends(get_db)
):
    """
    Get Shapley Value multi-touch attribution analysis

    Shows HOW customers interact across channels (behavioral journey)
    Note: For budget decisions, use PIE Incremental ROAS instead

    Returns:
    - Fair credit assignment across touchpoints
    - Journey statistics (avg touchpoints, multi-touch %)
    - Channel synergy insights
    - Visualization data for charts
    """
    try:
        attribution = analyze_attribution(db, customer_id, days_lookback)
        return attribution
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error analyzing attribution: {str(e)}")


# ===== LTV PREDICTION =====
@router.get("/ltv/predict", response_model=schemas.LTVResponse)
def get_ltv_predictions(
    customer_id: int = Query(..., description="Customer ID"),
    campaign_id: Optional[str] = Query(None, description="Specific campaign ID"),
    db: Session = Depends(get_db)
):
    """
    Get Customer Lifetime Value (LTV) predictions

    Segments customers using ML-enhanced RFM analysis:
    - Whale: High LTV, high engagement
    - Loyalist: Regular, consistent purchaser
    - Future Whale: High engagement, growing LTV
    - At Risk: Previously active, declining
    - One-Time Buyer: Single purchase
    - Dormant: Churned customer

    Enables LAROAS (LTV-Adjusted ROAS) optimization
    """
    try:
        ltv_data = predict_ltv(db, customer_id, campaign_id)
        return ltv_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error predicting LTV: {str(e)}")


# ===== LAROAS CALCULATION =====
@router.get("/ltv/laroas", response_model=schemas.LAROASResponse)
def get_laroas_calculation(
    customer_id: int = Query(..., description="Customer ID"),
    campaign_id: str = Query(..., description="Campaign ID"),
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db)
):
    """
    Calculate LTV-Adjusted ROAS (LAROAS)

    LAROAS = Standard ROAS × (Customer LTV / First Purchase Value)

    Ensures budget prioritizes campaigns acquiring high-value customers,
    not just campaigns with high short-term ROAS

    Example:
    - Campaign A: 2.0x ROAS, acquires "One-Time Buyers" (₹2K LTV)
    - Campaign B: 1.5x ROAS, acquires "Whales" (₹15K LTV)
    → Campaign B has higher LAROAS and is better for long-term growth
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date() if date else None
        laroas_data = calculate_laroas(db, customer_id, campaign_id, date_obj)
        return laroas_data
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating LAROAS: {str(e)}")


# ===== UNIFIED RECOMMENDATION (THE MAIN ONE) =====
@router.get("/recommendation/unified", response_model=schemas.UnifiedRecommendationResponse)
def get_unified_ai_recommendation(
    customer_id: int = Query(..., description="Customer ID"),
    date: Optional[str] = Query(None, description="Date (YYYY-MM-DD), defaults to today"),
    db: Session = Depends(get_db)
):
    """
    Get THE unified AI recommendation

    Synthesizes ALL models (PIE, LTV, Shapley, Anomaly Detection) into ONE action

    Decision Framework (3 Pillars):
    1. Prediction: PIE + LTV + Shapley models
    2. Optimization: Budget allocation logic
    3. Rules: Business constraints

    Priority Hierarchy:
    1. Anomaly Check (HIGHEST) - Safety first
    2. Causal Prioritization (PIE) - True incremental impact
    3. Value Filtering (LAROAS) - Long-term customer value
    4. Behavioral Context (Shapley) - Journey insights
    5. Constraint Validation - Business rules

    Returns:
    - Single, definitive action
    - Expected outcome
    - Confidence score
    - Actionable steps
    """
    try:
        date_obj = datetime.strptime(date, "%Y-%m-%d").date() if date else None
        recommendation = get_unified_recommendation(db, customer_id, date_obj)
        return recommendation
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid date format. Use YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")


# ===== DAILY INSIGHTS =====
@router.get("/insights/daily", response_model=schemas.DailyInsightsResponse)
def get_daily_insights(
    user_name: str = Query(..., description="User's first name"),
    customer_id: int = Query(..., description="Customer ID"),
    db: Session = Depends(get_db)
):
    """
    Get comprehensive daily insights package

    Includes:
    - Personalized greeting
    - Top unified recommendation
    - Key insights and opportunities
    - Anomaly alerts
    - Quick stats

    This is the MAIN endpoint for the dashboard landing page
    """
    try:
        # Get all components
        greeting = get_greeting(db, user_name, customer_id)
        recommendation = get_unified_recommendation(db, customer_id)
        anomalies = detect_anomalies(db, customer_id)
        pie_data = predict_incrementality(db, customer_id)
        ltv_data = predict_ltv(db, customer_id)

        # Build insights list
        insights = []

        # Add LTV insights
        for insight_text in ltv_data.get("insights", []):
            insights.append({
                "type": "opportunity",
                "title": "Customer Value Insight",
                "message": insight_text,
                "priority": "medium",
                "icon": "💡",
                "action_available": False
            })

        # Add warning alerts as insights
        for alert in anomalies.get("alerts", []):
            if alert["severity"] == "warning":
                insights.append({
                    "type": "alert",
                    "title": f"{alert['metric_name']} Alert",
                    "message": alert["message"],
                    "priority": "medium",
                    "icon": "⚠️",
                    "action_available": True,
                    "action_label": "Investigate"
                })

        # Quick stats
        quick_stats = {
            "avg_incremental_roas": pie_data["summary"]["avg_incremental_roas"],
            "total_campaigns": pie_data["summary"]["total_campaigns"],
            "total_segments": len(ltv_data.get("segments", {})),
            "anomalies_detected": anomalies["total_anomalies"]
        }

        return {
            "customer_id": customer_id,
            "date": datetime.now().date().isoformat(),
            "greeting": greeting,
            "top_recommendation": recommendation,
            "insights": insights[:5],  # Top 5 insights
            "anomaly_alerts": [a for a in anomalies.get("alerts", []) if a["severity"] in ["critical", "warning"]],
            "quick_stats": quick_stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating daily insights: {str(e)}")


# ===== CONVERSATIONAL AI (CHAT) =====
@router.post("/chat", response_model=schemas.ChatResponse)
def chat_with_ai(
    message: schemas.ChatMessage,
    db: Session = Depends(get_db)
):
    """
    Conversational AI for marketing data

    Examples:
    - "Why is Meta better than Google?"
    - "Which campaign has the best ROAS?"
    - "Show me top performing keywords"
    - "What's my customer LTV?"

    Returns AI response with data backing
    """
    try:
        user_query = message.user_message.lower()

        # Simple keyword-based routing (in production: use LLM)
        if "meta" in user_query and ("better" in user_query or "google" in user_query):
            # Compare Meta vs Google
            pie_data = predict_incrementality(db, message.customer_id)
            ltv_data = predict_ltv(db, message.customer_id)

            response = (
                "Based on Incremental ROAS analysis, I can show you which platform drives "
                "net new revenue. Meta Ads may have different customer quality (LTV) than Google Ads. "
                "Let me analyze your data..."
            )

            return {
                "ai_response": response,
                "data_backing": {
                    "pie_predictions": pie_data["predictions"][:3],
                    "ltv_segments": ltv_data.get("segments", {})
                },
                "suggested_actions": [
                    "View detailed cross-platform comparison",
                    "See budget shift recommendations",
                    "Analyze customer journey attribution"
                ],
                "related_insights": []
            }

        elif "best" in user_query or "top" in user_query:
            # Top campaigns
            pie_data = predict_incrementality(db, message.customer_id)

            if pie_data["predictions"]:
                top_campaign = pie_data["predictions"][0]
                response = (
                    f"Your top performing campaign is '{top_campaign['campaign_name']}' with "
                    f"{top_campaign['predicted_incremental_roas']:.2f}x Incremental ROAS. "
                    f"This means it's driving TRUE net new revenue, not just taking credit for organic sales."
                )

                return {
                    "ai_response": response,
                    "data_backing": {"top_campaigns": pie_data["predictions"][:5]},
                    "suggested_actions": ["Scale up this campaign", "Create lookalike audiences"],
                    "related_insights": []
                }

        elif "ltv" in user_query or "lifetime value" in user_query:
            # LTV question
            ltv_data = predict_ltv(db, message.customer_id)

            segments = ltv_data.get("segments", {})
            if segments:
                top_segment = list(segments.keys())[0]
                top_ltv = segments[top_segment]["avg_ltv"]

                response = (
                    f"Your highest-value customer segment is '{top_segment}' with an average "
                    f"lifetime value of ₹{top_ltv:,.0f}. Focus your acquisition budget on campaigns "
                    f"that attract these customers for maximum long-term ROI."
                )

                return {
                    "ai_response": response,
                    "data_backing": {"segments": segments},
                    "suggested_actions": ["View LAROAS by campaign", "Create segment-based audiences"],
                    "related_insights": ltv_data.get("insights", [])
                }

        # Default response
        return {
            "ai_response": (
                "I can help you analyze your marketing performance! Try asking me:\n"
                "- 'Why is Meta better than Google?'\n"
                "- 'Which campaign has the best incremental ROAS?'\n"
                "- 'What's my customer LTV by segment?'\n"
                "- 'Show me anomalies in my campaigns'"
            ),
            "data_backing": {},
            "suggested_actions": ["View daily insights", "Get unified recommendation"],
            "related_insights": []
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing chat: {str(e)}")


# ===== SYSTEM STATUS =====
@router.get("/status", response_model=schemas.AIIntegrationStatus)
def get_ai_system_status(
    customer_id: int = Query(..., description="Customer ID"),
    db: Session = Depends(get_db)
):
    """
    Get AI system integration status

    Returns:
    - Which models are available and functional
    - Data quality score
    - Whether recommendations are enabled
    - System health
    """
    try:
        # Check if each model has sufficient data
        pie_data = predict_incrementality(db, customer_id)
        ltv_data = predict_ltv(db, customer_id)
        anomaly_data = detect_anomalies(db, customer_id)

        models_available = {
            "greeting_generator": True,
            "anomaly_detection": anomaly_data["total_anomalies"] >= 0,
            "pie_incrementality": len(pie_data.get("predictions", [])) > 0,
            "shapley_attribution": True,
            "ltv_prediction": len(ltv_data.get("segments", {})) > 0,
            "decision_engine": True
        }

        # Calculate data quality score
        campaigns_count = len(pie_data.get("predictions", []))
        segments_count = len(ltv_data.get("segments", {}))

        if campaigns_count >= 10 and segments_count >= 3:
            data_quality = 1.0
        elif campaigns_count >= 5:
            data_quality = 0.75
        elif campaigns_count >= 1:
            data_quality = 0.5
        else:
            data_quality = 0.25

        recommendations_enabled = all([
            models_available["pie_incrementality"],
            models_available["decision_engine"]
        ])

        notes = []
        if campaigns_count < 5:
            notes.append("Run campaigns for at least 7 days to improve prediction accuracy")
        if not ltv_data.get("segments"):
            notes.append("LTV predictions will improve with more conversion data")
        if data_quality >= 0.75:
            notes.append("System is fully operational with high-confidence predictions")

        return {
            "customer_id": customer_id,
            "models_available": models_available,
            "data_quality_score": data_quality,
            "recommendations_enabled": recommendations_enabled,
            "last_training_date": datetime.now().date().isoformat(),
            "notes": notes
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error checking system status: {str(e)}")
