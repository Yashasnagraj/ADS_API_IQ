"""
Pydantic schemas for Google Analytics 4 (GA4) API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==============================================================================
# INTEGRATION STATUS
# ==============================================================================

class GA4IntegrationStatusResponse(BaseModel):
    """GA4 integration status for a customer"""
    customer_id: int
    is_connected: bool
    properties_count: int
    total_sessions: int
    total_events: int
    total_conversions: int
    attribution_coverage: float = Field(description="% of sessions with campaign attribution")
    last_sync_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==============================================================================
# PROPERTIES
# ==============================================================================

class GA4PropertyResponse(BaseModel):
    """GA4 property details"""
    property_id: str
    customer_id: int
    property_name: str
    display_name: Optional[str]
    website_url: Optional[str]
    currency_code: str
    time_zone: Optional[str]
    is_active: bool
    connected_at: datetime
    last_sync_at: Optional[datetime]

    class Config:
        from_attributes = True


# ==============================================================================
# SESSIONS
# ==============================================================================

class GA4SessionMetrics(BaseModel):
    """Session behavior metrics"""
    date: str
    source: str
    medium: str
    campaign: Optional[str]
    device_category: str
    sessions: int
    users: int
    new_users: int
    engaged_sessions: int
    bounce_rate: float = Field(description="Bounce rate %")
    engagement_rate: float = Field(description="Engagement rate %")
    avg_session_duration: float = Field(description="Average session duration in seconds")
    pages_per_session: float
    page_views: int
    conversions: int
    conversion_value: float = 0.0

    class Config:
        from_attributes = True


class GA4SessionsResponse(BaseModel):
    """List of session metrics"""
    sessions: List[GA4SessionMetrics]
    total_count: int


class GA4BehaviorBySourceResponse(BaseModel):
    """Behavior metrics grouped by source"""
    source: str
    sessions: int
    users: int
    bounce_rate: float
    avg_session_duration: float
    pages_per_session: float
    conversions: int
    conversion_rate: float


class GA4BehaviorByCampaignResponse(BaseModel):
    """Behavior metrics grouped by campaign"""
    campaign: str
    source: str
    sessions: int
    users: int
    bounce_rate: float
    avg_session_duration: float
    pages_per_session: float
    conversions: int
    conversion_rate: float


# ==============================================================================
# EVENTS
# ==============================================================================

class GA4EventMetrics(BaseModel):
    """Event tracking metrics"""
    date: str
    event_name: str
    source: Optional[str]
    campaign: Optional[str]
    event_count: int
    event_value: float
    users: int

    class Config:
        from_attributes = True


class GA4EventsResponse(BaseModel):
    """List of event metrics"""
    events: List[GA4EventMetrics]
    total_count: int


class GA4TopEventsResponse(BaseModel):
    """Top events summary"""
    event_name: str
    total_count: int
    total_value: float
    unique_users: int


# ==============================================================================
# CONVERSION PATHS (MULTI-TOUCH ATTRIBUTION)
# ==============================================================================

class GA4Touchpoint(BaseModel):
    """Single touchpoint in customer journey"""
    source: str
    medium: str
    campaign: str
    timestamp: str
    order: int


class GA4ConversionPathResponse(BaseModel):
    """Conversion path with all touchpoints"""
    conversion_event: str
    conversion_date: str
    conversion_value: float
    touchpoints: List[GA4Touchpoint]
    touchpoints_count: int
    days_to_conversion: int
    first_touch_source: str
    first_touch_campaign: str
    last_touch_source: str
    last_touch_campaign: str

    class Config:
        from_attributes = True


class GA4ConversionPathsResponse(BaseModel):
    """List of conversion paths"""
    paths: List[GA4ConversionPathResponse]
    total_count: int


class GA4AttributionModelResponse(BaseModel):
    """Attribution credit by source/campaign"""
    source: str
    campaign: str
    first_touch_conversions: int
    last_touch_conversions: int
    linear_attribution_credit: float = Field(description="Equal credit across all touchpoints")
    time_decay_credit: float = Field(description="More credit to recent touchpoints")
    total_conversion_value: float


# ==============================================================================
# AUDIENCE INSIGHTS
# ==============================================================================

class GA4AudienceSegment(BaseModel):
    """Audience segment with demographics and behavior"""
    segment_name: str
    segment_type: str
    country: Optional[str]
    device_category: str
    operating_system: Optional[str]
    browser: Optional[str]
    users: int
    new_users: int
    sessions: int
    engagement_rate: float
    avg_session_duration: float
    pages_per_session: float
    conversions: int
    conversion_rate: float
    revenue: float
    avg_revenue_per_user: float

    class Config:
        from_attributes = True


class GA4AudienceInsightsResponse(BaseModel):
    """Audience insights summary"""
    segments: List[GA4AudienceSegment]
    total_count: int


class GA4DeviceBreakdown(BaseModel):
    """Device category breakdown"""
    device_category: str
    users: int
    sessions: int
    bounce_rate: float
    conversion_rate: float


class GA4CountryBreakdown(BaseModel):
    """Country breakdown"""
    country: str
    users: int
    sessions: int
    conversions: int
    revenue: float


# ==============================================================================
# CAMPAIGN ENRICHMENT
# ==============================================================================

class GA4CampaignEnrichment(BaseModel):
    """GA4 behavior data for a Google Ads campaign"""
    campaign_name: str
    utm_campaign: str

    # Google Ads metrics (from your existing data)
    ad_clicks: Optional[int] = 0
    ad_impressions: Optional[int] = 0
    ad_cost: Optional[float] = 0.0
    ad_conversions: Optional[int] = 0
    ad_roas: Optional[float] = 0.0

    # GA4 behavior metrics (from GA4 sessions)
    ga4_sessions: int
    ga4_users: int
    ga4_bounce_rate: float
    ga4_avg_session_duration: float
    ga4_pages_per_session: float
    ga4_engagement_rate: float
    ga4_conversions: int

    # Combined insights
    quality_score: float = Field(description="Overall traffic quality score (0-100)")
    recommendation: str = Field(description="Action recommendation based on quality")


class GA4CampaignEnrichmentResponse(BaseModel):
    """List of enriched campaigns"""
    campaigns: List[GA4CampaignEnrichment]
    total_count: int


# ==============================================================================
# KEYWORD ENRICHMENT (GA4 + GOOGLE ADS KEYWORDS)
# ==============================================================================

class GA4KeywordEnrichment(BaseModel):
    """Keyword enriched with GA4 behavior data"""
    keyword_text: str
    keyword_id: int

    # Google Ads metrics
    ad_clicks: int
    ad_impressions: int
    ad_cost: float
    ad_ctr: float
    ad_conversions: int

    # GA4 behavior metrics
    ga4_sessions: int
    ga4_users: int
    ga4_bounce_rate: float
    ga4_avg_session_duration: float
    ga4_pages_per_session: float
    ga4_engagement_rate: float
    ga4_conversions: int

    # Quality score and recommendations
    quality_score: float
    recommendation: str

    class Config:
        from_attributes = True


class GA4KeywordEnrichmentResponse(BaseModel):
    """Response with enriched keyword data"""
    keywords: List[GA4KeywordEnrichment]
    total_count: int

    class Config:
        from_attributes = True


# ==============================================================================
# AD GROUP ENRICHMENT (GA4 + GOOGLE ADS AD GROUPS)
# ==============================================================================

class GA4AdGroupEnrichment(BaseModel):
    """Ad group enriched with GA4 behavior data"""
    ad_group_name: str
    ad_group_id: int
    campaign_name: Optional[str]

    # Google Ads metrics
    ad_clicks: int
    ad_impressions: int
    ad_cost: float
    ad_ctr: float
    ad_conversions: int

    # GA4 behavior metrics
    ga4_sessions: int
    ga4_users: int
    ga4_bounce_rate: float
    ga4_avg_session_duration: float
    ga4_pages_per_session: float
    ga4_engagement_rate: float
    ga4_conversions: int

    # Quality score and recommendations
    quality_score: float
    recommendation: str

    class Config:
        from_attributes = True


class GA4AdGroupEnrichmentResponse(BaseModel):
    """Response with enriched ad group data"""
    ad_groups: List[GA4AdGroupEnrichment]
    total_count: int

    class Config:
        from_attributes = True


# ==============================================================================
# USER BEHAVIOR BY CAMPAIGN
# ==============================================================================

class GA4UserBehaviorByCampaignResponse(BaseModel):
    """Detailed user behavior for a specific campaign"""
    campaign_id: Optional[int]
    campaign_name: str
    utm_campaign: Optional[str]

    # Session metrics
    sessions: int
    users: int
    new_users: int

    # Engagement metrics
    bounce_rate: float
    engagement_rate: float
    avg_session_duration: float
    pages_per_session: float

    # Conversion metrics
    conversions: int
    conversion_rate: float
    conversion_value: float

    # Device breakdown
    desktop_sessions: int
    mobile_sessions: int
    tablet_sessions: int

    # Top landing pages
    top_landing_pages: List[str] = []

    class Config:
        from_attributes = True


# ==============================================================================
# ERROR RESPONSES
# ==============================================================================

class GA4ErrorResponse(BaseModel):
    """Error response"""
    error: str
    message: str
    details: Optional[dict] = None


# ==============================================================================
# QUERY PARAMETERS
# ==============================================================================

class GA4DateRange(BaseModel):
    """Date range filter"""
    start_date: str = Field(description="YYYY-MM-DD format")
    end_date: str = Field(description="YYYY-MM-DD format")
