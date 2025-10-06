"""
Ad Group schemas
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .base import PaginatedResponse

class AdGroupBase(BaseModel):
    ad_group_id: int
    campaign_id: int
    customer_id: int
    ad_group_name: str
    status: str
    type: str

class AdGroupMetrics(BaseModel):
    clicks: int = 0
    impressions: int = 0
    cost: float = 0
    conversions: float = 0
    ctr: float = 0
    avg_cpc: float = 0

class AdGroupDetail(AdGroupBase):
    cpc_bid_micros: Optional[int] = None
    cpm_bid_micros: Optional[int] = None
    target_cpa_micros: Optional[int] = None
    target_roas: Optional[float] = None
    ad_rotation_mode: Optional[str] = None
    created_at: Optional[datetime] = None
    quality_score: Optional[float] = None
    competition: Optional[str] = "UNKNOWN"
    metrics: AdGroupMetrics

    class Config:
        from_attributes = True

class AdGroupListResponse(PaginatedResponse):
    ad_groups: List[AdGroupDetail]