"""
ML Feature schemas
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .base import PaginatedResponse

class MLFeatureBase(BaseModel):
    id: int
    customer_id: int
    campaign_id: Optional[int] = None
    campaign_name: Optional[str] = None
    channel_type: Optional[str] = None
    bidding_strategy: Optional[str] = None
    budget_amount: Optional[float] = None
    keyword_id: Optional[str] = None
    keyword_text: Optional[str] = None
    match_type: Optional[str] = None
    quality_score: Optional[int] = None
    avg_cpc: Optional[float] = None
    ctr: Optional[float] = None
    conversion_rate: Optional[float] = None
    conversions: Optional[float] = None
    cost: Optional[float] = None
    impressions: Optional[int] = None
    clicks: Optional[int] = None
    competition_index: Optional[float] = None
    search_volume_trend: Optional[float] = None
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class MLFeatureListResponse(PaginatedResponse):
    features: List[MLFeatureBase]