"""
Keyword schemas
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .base import PaginatedResponse

class KeywordBase(BaseModel):
    keyword_id: str
    ad_group_id: int
    campaign_id: int
    customer_id: int
    keyword_text: str
    match_type: str
    status: str

class KeywordMetrics(BaseModel):
    clicks: int = 0
    impressions: int = 0
    cost: float = 0
    conversions: float = 0
    ctr: float = 0
    conversion_rate: float = 0
    avg_cpc: float = 0

class KeywordSummary(KeywordBase):
    quality_score: Optional[int] = None
    metrics: KeywordMetrics

    class Config:
        from_attributes = True

class KeywordDetail(KeywordBase):
    quality_score: Optional[int] = None
    creative_quality_score: Optional[str] = None
    landing_page_quality_score: Optional[str] = None
    search_predicted_ctr: Optional[str] = None
    cpc_bid_micros: Optional[int] = None
    first_page_cpc_micros: Optional[int] = None
    first_position_cpc_micros: Optional[int] = None
    top_of_page_cpc_micros: Optional[int] = None
    approval_status: Optional[str] = None
    system_serving_status: Optional[str] = None
    is_negative: Optional[bool] = None
    bid_modifier: Optional[float] = None
    created_at: Optional[datetime] = None
    metrics: KeywordMetrics

    class Config:
        from_attributes = True

class KeywordListResponse(PaginatedResponse):
    keywords: List[KeywordSummary]