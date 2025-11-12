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
    total_conversion_value: float
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

class MetricComparison(BaseModel):
    """Single metric comparison between two periods"""
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    change_direction: str  # 'increase', 'decrease', 'no_change'

class MetricComparisonResponse(BaseModel):
    """Detailed metric comparison response"""
    metric_name: str
    current_value: float
    previous_value: float
    change_percentage: float
    change_direction: str  # 'increase', 'decrease', 'no_change'
    is_positive_change: bool  # Whether the change is considered positive
    current_period_start: str
    current_period_end: str
    previous_period_start: str
    previous_period_end: str

class BenchmarkResponse(BaseModel):
    """Industry benchmark data"""
    benchmark_id: int
    industry_vertical: str
    industry_sub_vertical: Optional[str] = None
    platform: str
    metric_name: str
    metric_category: Optional[str] = None
    benchmark_value: float
    benchmark_unit: str
    excellent_threshold: Optional[float] = None
    good_threshold: Optional[float] = None
    average_threshold: Optional[float] = None
    poor_threshold: Optional[float] = None
    data_source: Optional[str] = None
    sample_size: Optional[int] = None
    confidence_score: Optional[int] = None
    country_code: str
    currency: str
    valid_from: str
    valid_until: Optional[str] = None
    notes: Optional[str] = None

class BenchmarkListResponse(BaseModel):
    """List of benchmarks response"""
    industry_vertical: str
    platform: str
    country_code: str
    benchmarks_count: int
    benchmarks: List[Dict[str, Any]]