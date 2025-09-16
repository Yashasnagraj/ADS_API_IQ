"""
Metrics schemas
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class MetricsSummary(BaseModel):
    date_range: str
    total_clicks: int
    total_impressions: int
    total_cost: float
    total_conversions: float
    avg_ctr: float
    avg_conversion_rate: float
    avg_cpc: float
    campaigns_count: int
    keywords_count: int

class TimeSeriesDataPoint(BaseModel):
    date: str
    clicks: int
    impressions: int
    cost: float
    conversions: float
    ctr: float
    conversion_rate: float

class TimeSeriesResponse(BaseModel):
    campaign_id: Optional[int] = None
    interval: str
    data_points: List[TimeSeriesDataPoint]