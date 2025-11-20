"""
Search Term schemas
"""
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
from .base import PaginatedResponse

class SearchTermBase(BaseModel):
    search_term_id: int
    keyword_id: Optional[str] = None
    ad_group_id: int
    campaign_id: int
    customer_id: int
    search_term: str
    keyword_text: Optional[str] = None
    match_type: Optional[str] = None
    search_term_match_type: Optional[str] = None

class SearchTermMetrics(BaseModel):
    date: Optional[str] = None
    clicks: int = 0
    impressions: int = 0
    cost: float = 0
    conversions: float = 0
    conversion_value: float = 0
    ctr: float = 0
    avg_cpc: float = 0

class SearchTermDetail(SearchTermBase):
    metrics: SearchTermMetrics
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SearchTermListResponse(PaginatedResponse):
    search_terms: List[SearchTermDetail]