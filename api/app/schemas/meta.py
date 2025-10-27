"""
Pydantic schemas for Meta (Facebook) Ads API endpoints
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ==============================================================================
# INTEGRATION STATUS
# ==============================================================================

class MetaIntegrationStatusResponse(BaseModel):
    """Meta Ads integration status for a customer"""
    customer_id: int
    is_connected: bool
    accounts_count: int
    active_accounts: int
    total_campaigns: int
    total_adsets: int
    total_ads: int
    total_spend: float = Field(description="Total spend across all campaigns")
    total_clicks: int
    total_conversions: float
    last_sync_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# ==============================================================================
# AD ACCOUNTS
# ==============================================================================

class MetaAdAccountResponse(BaseModel):
    """Meta ad account details"""
    account_id: str
    customer_id: int
    account_name: Optional[str]
    business_id: Optional[str]
    currency: str
    timezone_name: Optional[str]
    account_status: Optional[str]
    is_active: bool
    installed_at: datetime
    last_sync_at: Optional[datetime]

    class Config:
        from_attributes = True


class MetaAdAccountsListResponse(BaseModel):
    """List of Meta ad accounts"""
    accounts: List[MetaAdAccountResponse]
    total_count: int


# ==============================================================================
# CAMPAIGNS
# ==============================================================================

class MetaCampaignResponse(BaseModel):
    """Meta campaign details"""
    campaign_id: str
    account_id: str
    customer_id: int
    name: str
    status: Optional[str]
    effective_status: Optional[str]
    objective: Optional[str] = Field(description="Campaign objective (e.g., OUTCOME_SALES, OUTCOME_TRAFFIC)")
    daily_budget: Optional[float] = Field(description="Daily budget in account currency")
    lifetime_budget: Optional[float] = Field(description="Lifetime budget in account currency")
    budget_remaining: Optional[float]
    bid_strategy: Optional[str]
    buying_type: Optional[str] = Field(description="AUCTION or RESERVED")
    created_time: Optional[datetime]
    updated_time: Optional[datetime]
    start_time: Optional[datetime]
    stop_time: Optional[datetime]

    class Config:
        from_attributes = True


class MetaCampaignsListResponse(BaseModel):
    """List of Meta campaigns"""
    campaigns: List[MetaCampaignResponse]
    total_count: int


# ==============================================================================
# AD SETS
# ==============================================================================

class MetaAdSetResponse(BaseModel):
    """Meta ad set details"""
    adset_id: str
    campaign_id: str
    account_id: str
    customer_id: int
    name: str
    status: Optional[str]
    effective_status: Optional[str]
    daily_budget: Optional[float]
    lifetime_budget: Optional[float]
    bid_amount: Optional[float]
    bid_strategy: Optional[str]
    targeting: Optional[str] = Field(description="Targeting criteria as JSON string")
    optimization_goal: Optional[str] = Field(description="e.g., REACH, LINK_CLICKS, IMPRESSIONS")
    billing_event: Optional[str] = Field(description="e.g., IMPRESSIONS, LINK_CLICKS")
    created_time: Optional[datetime]
    updated_time: Optional[datetime]
    start_time: Optional[datetime]
    end_time: Optional[datetime]

    class Config:
        from_attributes = True


class MetaAdSetsListResponse(BaseModel):
    """List of Meta ad sets"""
    adsets: List[MetaAdSetResponse]
    total_count: int


# ==============================================================================
# ADS
# ==============================================================================

class MetaAdResponse(BaseModel):
    """Meta ad (creative) details"""
    ad_id: str
    adset_id: str
    campaign_id: str
    account_id: str
    customer_id: int
    name: str
    status: Optional[str]
    effective_status: Optional[str]
    creative_id: Optional[str]
    creative_name: Optional[str]
    creative_title: Optional[str]
    creative_body: Optional[str]
    creative_image_url: Optional[str]
    creative_video_url: Optional[str]
    call_to_action_type: Optional[str] = Field(description="e.g., LEARN_MORE, SHOP_NOW, SIGN_UP")
    created_time: Optional[datetime]
    updated_time: Optional[datetime]

    class Config:
        from_attributes = True


class MetaAdsListResponse(BaseModel):
    """List of Meta ads"""
    ads: List[MetaAdResponse]
    total_count: int


# ==============================================================================
# INSIGHTS (PERFORMANCE METRICS)
# ==============================================================================

class MetaInsightsMetrics(BaseModel):
    """Meta insights performance metrics"""
    insight_id: str
    entity_type: str = Field(description="campaign, adset, or ad")
    entity_id: str
    campaign_id: Optional[str]
    customer_id: int
    date_start: str
    date_stop: str

    # Core metrics
    impressions: int
    clicks: int
    spend: float = Field(description="Spend in account currency")
    reach: int
    frequency: float

    # Engagement metrics
    inline_link_clicks: int
    inline_post_engagement: int
    post_reactions: int = 0
    post_comments: int = 0
    post_shares: int = 0
    video_views: int = 0

    # Conversion metrics
    conversions: float
    conversion_values: float = 0
    purchases: int = 0
    purchase_value: float = 0
    adds_to_cart: int = 0
    checkouts_initiated: int = 0
    leads: int = 0

    # Calculated metrics
    ctr: float = Field(description="Click-through rate %")
    cpc: float = Field(description="Cost per click")
    cpm: float = Field(description="Cost per 1000 impressions")
    cpp: float = Field(description="Cost per purchase")
    roas: float = Field(description="Return on ad spend")

    class Config:
        from_attributes = True


class MetaInsightsListResponse(BaseModel):
    """List of Meta insights"""
    insights: List[MetaInsightsMetrics]
    total_count: int


class MetaInsightsSummaryResponse(BaseModel):
    """Aggregated insights summary"""
    customer_id: int
    date_start: str
    date_stop: str
    total_impressions: int
    total_clicks: int
    total_spend: float
    total_reach: int
    avg_frequency: float
    total_conversions: float
    total_purchase_value: float
    avg_ctr: float
    avg_cpc: float
    avg_cpm: float
    overall_roas: float


# ==============================================================================
# CROSS-PLATFORM COMPARISON
# ==============================================================================

class PlatformMetrics(BaseModel):
    """Generic platform metrics for comparison"""
    total_spend: float
    total_clicks: int
    total_impressions: int
    total_conversions: float
    avg_cpc: float
    ctr: float = Field(description="Click-through rate %")
    roas: float = Field(description="Return on ad spend")
    conversion_rate: float = Field(description="Conversion rate %")


class CrossPlatformComparisonResponse(BaseModel):
    """Comparison of Google Ads vs Meta Ads performance"""
    customer_id: int
    date_range: str

    google_ads: PlatformMetrics
    meta_ads: PlatformMetrics

    # Comparison insights
    meta_vs_google_spend_ratio: float = Field(description="Meta spend / Google spend")
    meta_vs_google_cpc_diff: float = Field(description="Meta CPC - Google CPC (negative = Meta cheaper)")
    meta_vs_google_roas_diff: float = Field(description="Meta ROAS - Google ROAS (positive = Meta better)")

    recommendation: str = Field(description="AI-generated budget allocation recommendation")


class UnifiedMetricsResponse(BaseModel):
    """Combined metrics across all platforms"""
    customer_id: int
    date_range: str

    # Total across all platforms
    total_spend: float
    total_clicks: int
    total_impressions: int
    total_conversions: float
    total_revenue: float

    # Platform breakdown
    google_ads_spend: float
    meta_ads_spend: float
    ga4_sessions: int
    shopify_orders: int

    # Unified KPIs
    overall_roas: float
    blended_cpc: float
    blended_conversion_rate: float


# ==============================================================================
# FILTERS & QUERY PARAMS
# ==============================================================================

class MetaCampaignStatus(str):
    """Campaign status filter options"""
    ACTIVE = "ACTIVE"
    PAUSED = "PAUSED"
    DELETED = "DELETED"
    ARCHIVED = "ARCHIVED"


class MetaObjective(str):
    """Campaign objective filter options"""
    OUTCOME_SALES = "OUTCOME_SALES"
    OUTCOME_LEADS = "OUTCOME_LEADS"
    OUTCOME_ENGAGEMENT = "OUTCOME_ENGAGEMENT"
    OUTCOME_TRAFFIC = "OUTCOME_TRAFFIC"
    OUTCOME_AWARENESS = "OUTCOME_AWARENESS"
    OUTCOME_APP_PROMOTION = "OUTCOME_APP_PROMOTION"
