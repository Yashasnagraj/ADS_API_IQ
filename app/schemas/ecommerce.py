"""
E-commerce Performance Dashboard Schemas
Pydantic models for e-commerce analytics endpoints
"""
from typing import List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class EcommerceKPI(BaseModel):
    """Header KPI metrics"""
    total_revenue: float = Field(..., description="Total revenue (conversion value)")
    total_orders: int = Field(..., description="Total number of orders (conversions)")
    conversion_rate: float = Field(..., description="Overall conversion rate")
    avg_order_value: float = Field(..., description="Average order value (AOV)")
    returning_customer_rate: float = Field(..., description="% of returning customers")
    refund_rate: float = Field(..., description="Refund/return rate %")

    # Trend indicators (vs previous period)
    revenue_trend: float = Field(..., description="% change in revenue")
    orders_trend: float = Field(..., description="% change in orders")
    cvr_trend: float = Field(..., description="% change in conversion rate")
    aov_trend: float = Field(..., description="% change in AOV")


class FunnelStage(BaseModel):
    """Funnel stage data"""
    stage: str = Field(..., description="Stage name")
    value: int = Field(..., description="Count at this stage")
    percentage: float = Field(..., description="% of previous stage")
    dropoff: float = Field(..., description="Drop-off % from previous stage")
    insight: Optional[str] = Field(None, description="AI-generated insight")


class FunnelData(BaseModel):
    """Complete funnel visualization data"""
    stages: List[FunnelStage]
    overall_conversion_rate: float


class ChannelMetrics(BaseModel):
    """Channel performance metrics"""
    channel: str = Field(..., description="Channel name")
    spend: float = Field(..., description="Total ad spend")
    revenue: float = Field(..., description="Revenue generated")
    roas: float = Field(..., description="Return on ad spend")
    orders: int = Field(..., description="Number of orders")
    impressions: int = Field(..., description="Total impressions")
    clicks: int = Field(..., description="Total clicks")
    ctr: float = Field(..., description="Click-through rate")
    cvr: float = Field(..., description="Conversion rate")


class ChannelPerformance(BaseModel):
    """Channel performance response"""
    channels: List[ChannelMetrics]
    insight: Optional[str] = Field(None, description="AI-generated insight")


class ProductMetrics(BaseModel):
    """Product performance metrics"""
    product_id: str
    product_name: str
    revenue: float
    orders: int
    conversion_rate: float
    refund_rate: float
    stock_status: str = Field(..., description="IN_STOCK, LOW_STOCK, OUT_OF_STOCK")
    rank: int = Field(..., description="Performance rank (1=best)")


class ProductPerformance(BaseModel):
    """Product performance response"""
    products: List[ProductMetrics]
    top_products: List[str] = Field(..., description="Top 3 product names")
    bottom_products: List[str] = Field(..., description="Bottom 3 product names")
    insight: Optional[str] = Field(None, description="AI-generated insight")


class CustomerSegment(BaseModel):
    """Customer segmentation data"""
    segment: str = Field(..., description="NEW or RETURNING")
    count: int
    percentage: float
    revenue: float
    revenue_percentage: float
    avg_order_value: float
    conversion_rate: float


class CustomerSegmentation(BaseModel):
    """Customer segmentation response"""
    segments: List[CustomerSegment]
    insight: Optional[str] = Field(None, description="AI-generated insight")


class ForecastDataPoint(BaseModel):
    """Forecast time series point"""
    date: str
    predicted_revenue: float
    confidence_lower: float
    confidence_upper: float


class RevenueForecast(BaseModel):
    """7-day revenue forecast"""
    forecast: List[ForecastDataPoint]
    trend: str = Field(..., description="INCREASING, DECREASING, STABLE")


class AnomalyAlert(BaseModel):
    """Anomaly detection alert"""
    severity: str = Field(..., description="LOW, MEDIUM, HIGH, CRITICAL")
    title: str
    description: str
    metric: str
    value: float
    expected_value: float
    deviation_percentage: float
    recommendation: str
    detected_at: datetime


class AnomalyDetection(BaseModel):
    """Anomaly detection response"""
    anomalies: List[AnomalyAlert]
    total_anomalies: int


class EcommerceOverview(BaseModel):
    """Complete e-commerce dashboard overview"""
    kpis: EcommerceKPI
    funnel: FunnelData
    channels: ChannelPerformance
    products: ProductPerformance
    segments: CustomerSegmentation
    forecast: RevenueForecast
    anomalies: AnomalyDetection
    customer_id: Optional[int] = None
    date_range: str
