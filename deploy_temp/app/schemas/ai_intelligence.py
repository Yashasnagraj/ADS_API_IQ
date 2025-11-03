"""
Pydantic schemas for AI Intelligence API
"""
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


# ===== GREETING SCHEMAS =====
class MetricsSummary(BaseModel):
    """Summary metrics for greeting"""
    total_campaigns: int
    healthy_campaigns: int
    roas: float
    total_spend: float
    total_revenue: float


class GreetingResponse(BaseModel):
    """Personalized greeting response"""
    greeting: str
    mood: str  # "positive", "neutral", "focused", "alert"
    message: str
    call_to_action: str
    metrics_summary: MetricsSummary
    status: str  # "excellent", "good", "needs_attention", "critical", "no_data"


# ===== ANOMALY DETECTION SCHEMAS =====
class AnomalyAlertSchema(BaseModel):
    """Individual anomaly alert"""
    metric_name: str
    current_value: float
    expected_range: List[float]
    severity: str  # "critical", "warning", "info"
    message: str
    affected_entity: Optional[str] = None
    detected_at: str


class AnomalyDetectionResponse(BaseModel):
    """Anomaly detection report"""
    has_critical_anomalies: bool
    total_anomalies: int
    critical_count: int
    warning_count: int
    info_count: int
    alerts: List[AnomalyAlertSchema]
    recommendation: str  # "PAUSE_OPTIMIZATION", "PROCEED_WITH_CAUTION", "PROCEED"
    summary_message: str


# ===== PIE MODEL SCHEMAS =====
class IncrementalityPredictionSchema(BaseModel):
    """Individual campaign incrementality prediction"""
    campaign_id: str
    campaign_name: str
    predicted_incremental_roas: float
    confidence_score: float
    total_conversions: float
    incremental_conversions: float
    non_incremental_conversions: float
    incremental_percentage: float
    explanation: str


class PIESummary(BaseModel):
    """Summary of PIE predictions"""
    total_campaigns: int
    avg_incremental_roas: float
    total_incremental_revenue: float
    total_non_incremental_revenue: float
    incremental_percentage: float


class PIEResponse(BaseModel):
    """PIE model prediction response"""
    customer_id: int
    date: str
    baseline_conversion_rate: float
    baseline_explanation: str
    predictions: List[IncrementalityPredictionSchema]
    summary: PIESummary
    note: str


# ===== ATTRIBUTION SCHEMAS =====
class JourneyStatistics(BaseModel):
    """Customer journey statistics"""
    avg_touchpoints_per_journey: float
    max_touchpoints: int
    min_touchpoints: int
    avg_conversion_value: float
    single_touch_journeys: int
    multi_touch_journeys: int
    multi_touch_percentage: float


class VisualizationData(BaseModel):
    """Data for frontend visualization"""
    channel: str
    contribution_percentage: float
    color: str


class AttributionResponse(BaseModel):
    """Shapley attribution analysis response"""
    customer_id: int
    date_range: str
    total_journeys: int
    attribution: Dict[str, float]
    insights: List[str]
    journey_statistics: JourneyStatistics
    note: str
    visualization_data: List[VisualizationData]


# ===== LTV SCHEMAS =====
class SegmentData(BaseModel):
    """Customer segment data"""
    count: int
    avg_ltv: float
    total_ltv: float
    avg_recency_days: float
    avg_purchase_frequency: float
    avg_order_value: float
    avg_churn_probability: float


class LTVResponse(BaseModel):
    """LTV prediction response"""
    customer_id: int
    total_customers: int
    segments: Dict[str, SegmentData]
    insights: List[str]


class LAROASResponse(BaseModel):
    """LAROAS calculation response"""
    campaign_id: str
    campaign_name: str
    date: str
    standard_roas: float
    laroas: float
    acquired_segment: str
    avg_customer_ltv: float
    ltv_multiplier: float
    explanation: str


# ===== DECISION ENGINE SCHEMAS =====
class UnifiedRecommendationResponse(BaseModel):
    """Unified AI recommendation"""
    action_type: str  # "BUDGET_SHIFT", "PAUSE_CAMPAIGN", "SCALE_UP", "OPTIMIZE", "MAINTAIN", "PAUSE_AND_INVESTIGATE"
    title: str
    message: str
    expected_outcome: str
    confidence_score: float
    priority: str  # "critical", "high", "medium", "low"
    supporting_data: Dict[str, Any]
    actionable_steps: List[str]
    generated_at: str


# ===== DAILY INSIGHTS SCHEMAS =====
class DailyInsightItem(BaseModel):
    """Individual daily insight"""
    type: str  # "opportunity", "alert", "achievement", "recommendation"
    title: str
    message: str
    priority: str
    icon: str  # Emoji or icon name
    action_available: bool
    action_label: Optional[str] = None


class DailyInsightsResponse(BaseModel):
    """Daily insights collection"""
    customer_id: int
    date: str
    greeting: GreetingResponse
    top_recommendation: UnifiedRecommendationResponse
    insights: List[DailyInsightItem]
    anomaly_alerts: List[AnomalyAlertSchema]
    quick_stats: Dict[str, Any]


# ===== CHAT SCHEMAS =====
class ChatMessage(BaseModel):
    """Chat message schema"""
    user_message: str = Field(..., min_length=1, max_length=500)
    customer_id: int
    context: Optional[Dict[str, Any]] = None


class ChatResponse(BaseModel):
    """AI chat response"""
    ai_response: str
    data_backing: Optional[Dict[str, Any]] = None
    suggested_actions: List[str] = []
    related_insights: List[str] = []


# ===== FORECASTING SCHEMAS =====
class ForecastPrediction(BaseModel):
    """Forecast prediction"""
    scenario: str
    budget_change: float
    budget_change_percentage: float
    predicted_revenue: float
    predicted_roas: float
    confidence_interval: List[float]  # [lower, upper]
    probability: float


class ForecastingResponse(BaseModel):
    """Forecasting response"""
    customer_id: int
    current_metrics: Dict[str, float]
    predictions: List[ForecastPrediction]
    recommendation: str
    note: str


# ===== EXECUTION SCHEMAS =====
class RecommendationExecutionRequest(BaseModel):
    """Request to execute a recommendation"""
    recommendation_id: str
    customer_id: int
    confirm: bool = Field(True, description="Confirmation to execute")


class ExecutionResponse(BaseModel):
    """Execution result"""
    success: bool
    message: str
    changes_applied: List[Dict[str, Any]]
    rollback_available: bool


# ===== INTEGRATION STATUS =====
class AIIntegrationStatus(BaseModel):
    """AI system integration status"""
    customer_id: int
    models_available: Dict[str, bool]
    data_quality_score: float
    recommendations_enabled: bool
    last_training_date: Optional[str] = None
    notes: List[str]
