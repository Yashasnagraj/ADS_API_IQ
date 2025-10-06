"""
Campaign schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from .base import PaginatedResponse

class CampaignBase(BaseModel):
    campaign_id: int
    customer_id: int
    campaign_name: str
    status: str
    serving_status: Optional[str] = None
    channel_type: str
    channel_subtype: Optional[str] = None
    bidding_strategy_type: str
    budget_amount_micros: Optional[int] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None

class CampaignMetrics(BaseModel):
    clicks: int = 0
    impressions: int = 0
    cost: float = 0
    conversions: float = 0
    ctr: float = 0
    conversion_rate: float = 0
    avg_cpc: float = 0

class CampaignSummary(CampaignBase):
    quality_score: Optional[float] = None
    competition: Optional[str] = "UNKNOWN"
    metrics: CampaignMetrics

    class Config:
        from_attributes = True

class CampaignDetail(CampaignBase):
    optimization_score: Optional[float] = None
    target_cpa_micros: Optional[int] = None
    target_roas: Optional[float] = None
    network_target_search: Optional[bool] = None
    network_target_content: Optional[bool] = None
    network_target_partner: Optional[bool] = None
    geo_target_type_positive: Optional[str] = None
    geo_target_type_negative: Optional[str] = None
    created_at: Optional[datetime] = None
    metrics: CampaignMetrics

    class Config:
        from_attributes = True

class CampaignListResponse(PaginatedResponse):
    campaigns: List[CampaignSummary]