"""
Campaign endpoints - Real-time Google Ads API queries
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.google_ads_service import get_google_ads_service
from app.services.gaql_builder import DateRange
from app.schemas.campaign import CampaignListResponse, CampaignDetail, CampaignSummary, CampaignMetrics
from app.schemas.ad_group import AdGroupListResponse, AdGroupDetail, AdGroupMetrics
from app.core.config import settings
from loguru import logger

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


def calculate_quality_score(metrics: dict) -> float:
    """Calculate quality score from metrics (1-10 scale)"""
    clicks = float(metrics.get("clicks", 0) or 0)
    impressions = float(metrics.get("impressions", 0) or 0)
    cost_micros = float(metrics.get("cost_micros", 0) or 0)
    conversions = float(metrics.get("conversions", 0) or 0)

    ctr = (clicks / impressions) if impressions > 0 else 0
    avg_cpc = (cost_micros / clicks / 1_000_000) if clicks > 0 else 0
    conversion_rate = (conversions / clicks) if clicks > 0 else 0

    # CTR Score (40%)
    ctr_score = min(ctr * 100, 10) * 0.4

    # CPC Efficiency Score (20%)
    cpc_score = 5.0
    if avg_cpc > 0:
        if avg_cpc < 0.5:
            cpc_score = 9.0
        elif avg_cpc < 1.0:
            cpc_score = 7.0
        elif avg_cpc < 2.0:
            cpc_score = 5.0
        else:
            cpc_score = 3.0
    cpc_score = cpc_score * 0.2

    # Conversion Rate Score (20%)
    conv_score = min(conversion_rate * 50, 10) * 0.2

    # Budget utilization score (20%)
    budget_score = 5.0
    if ctr > 0.05 and conversion_rate > 0.02:
        budget_score = 8.0
    elif ctr > 0.03 and conversion_rate > 0.01:
        budget_score = 6.5
    elif ctr < 0.01:
        budget_score = 3.0
    budget_score = budget_score * 0.2

    return min(max(ctr_score + cpc_score + conv_score + budget_score, 1), 10)


def determine_competition(metrics: dict) -> str:
    """Determine competition level from metrics"""
    avg_cpc = float(metrics.get("average_cpc", 0) or 0)
    impressions = float(metrics.get("impressions", 0) or 0)

    if avg_cpc > 2.0 or impressions > 100000:
        return "HIGH"
    elif avg_cpc > 0.5 or impressions > 10000:
        return "MEDIUM"
    else:
        return "LOW"


@router.get("", response_model=CampaignListResponse)
def get_campaigns(
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = None,
    customer_id: Optional[int] = Query(default=None, description="Filter by customer ID"),
    channel_type: Optional[str] = Query(default=None, description="Filter by campaign type (SEARCH, DISPLAY, SMART, etc.)"),
):
    """
    List all campaigns with summary metrics
    Real-time query from Google Ads API
    """
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id is required")

    try:
        # Try to get Google Ads service - may fail if credentials not configured
        try:
            ads_service = get_google_ads_service()
        except Exception as service_error:
            logger.warning(f"Google Ads service not available: {service_error}")
            # Return empty result if service unavailable
            return CampaignListResponse(
                campaigns=[],
                total=0,
                limit=limit,
                offset=offset,
                has_more=False
            )

        customer_id_str = str(customer_id)

        # Get campaigns from Google Ads API
        campaigns_data = ads_service.get_campaigns(
            customer_id_str,
            status=status,
            date_range="LAST_30_DAYS"
        )

        # Filter by channel_type if provided
        if channel_type:
            campaigns_data = [
                c for c in campaigns_data
                if c.get("campaign", {}).get("advertising_channel_type") == channel_type
            ]

        # Apply pagination
        total = len(campaigns_data)
        paginated_campaigns = campaigns_data[offset:offset + limit]

        campaign_summaries = []
        for campaign_row in paginated_campaigns:
            campaign = campaign_row.get("campaign", {})
            campaign_budget = campaign_row.get("campaign_budget", {})
            metrics = campaign_row.get("metrics", {})

            # Calculate quality score
            quality_score = calculate_quality_score(metrics)
            competition = determine_competition(metrics)

            # Build metrics object
            clicks_val = float(metrics.get("clicks", 0) or 0)
            conversions_val = float(metrics.get("conversions", 0) or 0)

            campaign_metrics = CampaignMetrics(
                clicks=metrics.get("clicks", 0),
                impressions=metrics.get("impressions", 0),
                cost=metrics.get("cost", 0),
                conversions=metrics.get("conversions", 0),
                ctr=metrics.get("ctr", 0),
                conversion_rate=(conversions_val / clicks_val) if clicks_val > 0 else 0,
                avg_cpc=metrics.get("average_cpc", 0)
            )

            summary = CampaignSummary(
                campaign_id=campaign.get("id", 0),
                customer_id=customer_id,
                campaign_name=campaign.get("name", ""),
                status=campaign.get("status", ""),
                serving_status=campaign.get("serving_status", ""),
                channel_type=campaign.get("advertising_channel_type", ""),
                channel_subtype=campaign.get("advertising_channel_sub_type", ""),
                bidding_strategy_type=campaign.get("bidding_strategy_type", ""),
                budget_amount_micros=campaign_budget.get("amount_micros", 0),
                start_date=campaign.get("start_date", ""),
                end_date=campaign.get("end_date", ""),
                quality_score=round(quality_score, 2),
                competition=competition,
                metrics=campaign_metrics
            )
            campaign_summaries.append(summary)

        return CampaignListResponse(
            campaigns=campaign_summaries,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )

    except Exception as e:
        import traceback
        logger.warning(f"Error fetching campaigns: {e}")
        logger.warning(f"Traceback: {traceback.format_exc()}")
        # Return empty result instead of raising error
        return CampaignListResponse(
            campaigns=[],
            total=0,
            limit=limit,
            offset=offset,
            has_more=False
        )


@router.get("/{campaign_id}", response_model=CampaignDetail)
def get_campaign(campaign_id: int, customer_id: int = Query(..., description="Customer ID")):
    """
    Get campaign detail with aggregated metrics
    Real-time query from Google Ads API
    """
    try:
        ads_service = get_google_ads_service()
        customer_id_str = str(customer_id)

        # Get all campaigns and find the specific one
        campaigns_data = ads_service.get_campaigns(
            customer_id_str,
            date_range="LAST_30_DAYS"
        )

        # Find the matching campaign
        campaign_row = None
        for row in campaigns_data:
            if row.get("campaign", {}).get("id") == campaign_id:
                campaign_row = row
                break

        if not campaign_row:
            raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

        campaign = campaign_row.get("campaign", {})
        campaign_budget = campaign_row.get("campaign_budget", {})
        metrics = campaign_row.get("metrics", {})

        # Build metrics object
        clicks_val = float(metrics.get("clicks", 0) or 0)
        conversions_val = float(metrics.get("conversions", 0) or 0)

        campaign_metrics = CampaignMetrics(
            clicks=metrics.get("clicks", 0),
            impressions=metrics.get("impressions", 0),
            cost=metrics.get("cost", 0),
            conversions=metrics.get("conversions", 0),
            ctr=metrics.get("ctr", 0),
            conversion_rate=(conversions_val / clicks_val) if clicks_val > 0 else 0,
            avg_cpc=metrics.get("average_cpc", 0)
        )

        return CampaignDetail(
            campaign_id=campaign.get("id", 0),
            customer_id=customer_id,
            campaign_name=campaign.get("name", ""),
            status=campaign.get("status", ""),
            serving_status=campaign.get("serving_status", ""),
            channel_type=campaign.get("advertising_channel_type", ""),
            channel_subtype=campaign.get("advertising_channel_sub_type", ""),
            bidding_strategy_type=campaign.get("bidding_strategy_type", ""),
            budget_amount_micros=campaign_budget.get("amount_micros", 0),
            start_date=campaign.get("start_date", ""),
            end_date=campaign.get("end_date", ""),
            optimization_score=campaign.get("optimization_score", 0),
            target_cpa_micros=campaign.get("target_cpa_micros", 0),
            target_roas=campaign.get("target_roas", 0),
            network_target_search=campaign.get("network_settings", {}).get("target_search_network", False),
            network_target_content=campaign.get("network_settings", {}).get("target_content_network", False),
            network_target_partner=campaign.get("network_settings", {}).get("target_partner_search_network", False),
            geo_target_type_positive=None,
            geo_target_type_negative=None,
            created_at=None,
            metrics=campaign_metrics
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch campaign: {str(e)}")


@router.get("/{campaign_id}/adgroups", response_model=AdGroupListResponse)
def get_campaign_ad_groups(
    campaign_id: int,
    customer_id: int = Query(..., description="Customer ID"),
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
):
    """
    List ad groups under a campaign
    Real-time query from Google Ads API
    """
    try:
        ads_service = get_google_ads_service()
        customer_id_str = str(customer_id)

        # Get ad groups for this campaign
        ad_groups_data = ads_service.get_ad_groups(
            customer_id_str,
            campaign_id=campaign_id,
            date_range="LAST_30_DAYS"
        )

        # Apply pagination
        total = len(ad_groups_data)
        paginated_ad_groups = ad_groups_data[offset:offset + limit]

        ad_group_details = []
        for ag_row in paginated_ad_groups:
            ag = ag_row.get("ad_group", {})
            campaign = ag_row.get("campaign", {})
            metrics = ag_row.get("metrics", {})

            # Build metrics object
            ag_metrics = AdGroupMetrics(
                clicks=metrics.get("clicks", 0),
                impressions=metrics.get("impressions", 0),
                cost=metrics.get("cost", 0),
                conversions=metrics.get("conversions", 0),
                ctr=metrics.get("ctr", 0),
                avg_cpc=metrics.get("average_cpc", 0)
            )

            detail = AdGroupDetail(
                ad_group_id=ag.get("id", 0),
                campaign_id=campaign.get("id", 0),
                customer_id=customer_id,
                ad_group_name=ag.get("name", ""),
                status=ag.get("status", ""),
                type=ag.get("type", ""),
                cpc_bid_micros=ag.get("cpc_bid_micros", 0),
                cpm_bid_micros=ag.get("cpm_bid_micros", 0),
                target_cpa_micros=ag.get("target_cpa_micros", 0),
                target_roas=ag.get("target_roas", 0),
                ad_rotation_mode=ag.get("ad_rotation_mode", ""),
                created_at=None,
                metrics=ag_metrics
            )
            ad_group_details.append(detail)

        return AdGroupListResponse(
            ad_groups=ad_group_details,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )

    except Exception as e:
        logger.error(f"Error fetching ad groups for campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch ad groups: {str(e)}")

