"""
Campaign endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models import Campaign, CampaignKeyword, AdGroup
from app.schemas.campaign import CampaignListResponse, CampaignDetail, CampaignSummary, CampaignMetrics
from app.schemas.ad_group import AdGroupListResponse, AdGroupDetail, AdGroupMetrics
from app.core.config import settings

router = APIRouter(prefix="/campaigns", tags=["campaigns"])

def get_campaign_metrics(campaign_id: int, db: Session) -> CampaignMetrics:
    """Get aggregated metrics for a campaign"""
    metrics = db.query(
        func.coalesce(func.sum(CampaignKeyword.clicks), 0).label("clicks"),
        func.coalesce(func.sum(CampaignKeyword.impressions), 0).label("impressions"),
        func.coalesce(func.sum(CampaignKeyword.cost_micros), 0).label("cost_micros"),
        func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("conversions"),
    ).filter(CampaignKeyword.campaign_id == campaign_id).first()

    clicks = metrics.clicks or 0
    impressions = metrics.impressions or 0
    cost_micros = metrics.cost_micros or 0
    conversions = metrics.conversions or 0

    return CampaignMetrics(
        clicks=clicks,
        impressions=impressions,
        cost=cost_micros / 1_000_000 if cost_micros else 0,
        conversions=conversions,
        ctr=clicks / impressions if impressions > 0 else 0,
        conversion_rate=conversions / clicks if clicks > 0 else 0,
        avg_cpc=cost_micros / clicks / 1_000_000 if clicks > 0 else 0
    )

@router.get("", response_model=CampaignListResponse)
def get_campaigns(
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    status: Optional[str] = None,
    customer_id: Optional[int] = Query(default=None, description="Filter by customer ID"),
    db: Session = Depends(get_db)
):
    """
    List all campaigns with summary metrics
    Filter by customer_id to show only specific customer's campaigns
    """
    query = db.query(Campaign)

    if customer_id:
        query = query.filter(Campaign.customer_id == customer_id)

    if status:
        query = query.filter(Campaign.status == status)

    total = query.count()
    campaigns = query.offset(offset).limit(limit).all()

    campaign_summaries = []
    for campaign in campaigns:
        metrics = get_campaign_metrics(campaign.campaign_id, db)

        # Calculate quality score dynamically (1-10 scale)
        # Based on: CTR (40%), CPC efficiency (20%), Conversion Rate (20%), Budget utilization (20%)
        ctr_score = min(metrics.ctr * 100, 10) * 0.4

        # CPC Efficiency Score
        cpc_score = 5.0
        if metrics.avg_cpc > 0:
            if metrics.avg_cpc < 0.5:
                cpc_score = 9.0
            elif metrics.avg_cpc < 1.0:
                cpc_score = 7.0
            elif metrics.avg_cpc < 2.0:
                cpc_score = 5.0
            else:
                cpc_score = 3.0
        cpc_score = cpc_score * 0.2

        # Conversion Rate Score
        conv_score = min(metrics.conversion_rate * 50, 10) * 0.2

        # Budget utilization score (based on performance)
        budget_score = 5.0
        if metrics.ctr > 0.05 and metrics.conversion_rate > 0.02:
            budget_score = 8.0
        elif metrics.ctr > 0.03 and metrics.conversion_rate > 0.01:
            budget_score = 6.5
        elif metrics.ctr < 0.01:
            budget_score = 3.0
        budget_score = budget_score * 0.2

        quality_score = min(max(ctr_score + cpc_score + conv_score + budget_score, 1), 10)

        # Calculate competition level
        competition = "UNKNOWN"
        if metrics.avg_cpc > 0 and metrics.impressions > 0:
            if metrics.avg_cpc > 2.0 or metrics.impressions > 100000:
                competition = "HIGH"
            elif metrics.avg_cpc > 0.5 or metrics.impressions > 10000:
                competition = "MEDIUM"
            else:
                competition = "LOW"

        summary = CampaignSummary(
            campaign_id=campaign.campaign_id,
            customer_id=campaign.customer_id,
            campaign_name=campaign.campaign_name,
            status=campaign.status,
            serving_status=campaign.serving_status,
            channel_type=campaign.channel_type,
            channel_subtype=campaign.channel_subtype,
            bidding_strategy_type=campaign.bidding_strategy_type,
            budget_amount_micros=campaign.budget_amount_micros,
            start_date=campaign.start_date,
            end_date=campaign.end_date,
            quality_score=round(quality_score, 2),
            competition=competition,
            metrics=metrics
        )
        campaign_summaries.append(summary)

    return CampaignListResponse(
        campaigns=campaign_summaries,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total
    )

@router.get("/{campaign_id}", response_model=CampaignDetail)
def get_campaign(campaign_id: int, db: Session = Depends(get_db)):
    """
    Get campaign detail with aggregated metrics
    """
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()

    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

    metrics = get_campaign_metrics(campaign_id, db)

    return CampaignDetail(
        campaign_id=campaign.campaign_id,
        customer_id=campaign.customer_id,
        campaign_name=campaign.campaign_name,
        status=campaign.status,
        serving_status=campaign.serving_status,
        channel_type=campaign.channel_type,
        channel_subtype=campaign.channel_subtype,
        bidding_strategy_type=campaign.bidding_strategy_type,
        budget_amount_micros=campaign.budget_amount_micros,
        start_date=campaign.start_date,
        end_date=campaign.end_date,
        optimization_score=campaign.optimization_score,
        target_cpa_micros=campaign.target_cpa_micros,
        target_roas=campaign.target_roas,
        network_target_search=campaign.network_target_search,
        network_target_content=campaign.network_target_content,
        network_target_partner=campaign.network_target_partner,
        geo_target_type_positive=campaign.geo_target_type_positive,
        geo_target_type_negative=campaign.geo_target_type_negative,
        created_at=campaign.created_at,
        metrics=metrics
    )

@router.get("/{campaign_id}/adgroups", response_model=AdGroupListResponse)
def get_campaign_ad_groups(
    campaign_id: int,
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List ad groups under a campaign
    """
    # Check if campaign exists
    campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
    if not campaign:
        raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

    query = db.query(AdGroup).filter(AdGroup.campaign_id == campaign_id)
    total = query.count()
    ad_groups = query.offset(offset).limit(limit).all()

    ad_group_details = []
    for ag in ad_groups:
        # Get metrics for ad group from campaign_keywords
        metrics = db.query(
            func.coalesce(func.sum(CampaignKeyword.clicks), 0).label("clicks"),
            func.coalesce(func.sum(CampaignKeyword.impressions), 0).label("impressions"),
            func.coalesce(func.sum(CampaignKeyword.cost_micros), 0).label("cost_micros"),
            func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("conversions"),
        ).join(
            db.query(func.distinct(CampaignKeyword.keyword_id).label("keyword_id"))
            .filter(CampaignKeyword.campaign_id == campaign_id)
            .subquery(),
            CampaignKeyword.keyword_id == db.query(func.distinct(CampaignKeyword.keyword_id))
        ).first()

        clicks = metrics.clicks if metrics else 0
        impressions = metrics.impressions if metrics else 0
        cost_micros = metrics.cost_micros if metrics else 0
        conversions = metrics.conversions if metrics else 0

        ag_metrics = AdGroupMetrics(
            clicks=clicks,
            impressions=impressions,
            cost=cost_micros / 1_000_000 if cost_micros else 0,
            conversions=conversions,
            ctr=clicks / impressions if impressions > 0 else 0,
            avg_cpc=cost_micros / clicks / 1_000_000 if clicks > 0 else 0
        )

        detail = AdGroupDetail(
            ad_group_id=ag.ad_group_id,
            campaign_id=ag.campaign_id,
            customer_id=ag.customer_id,
            ad_group_name=ag.ad_group_name,
            status=ag.status,
            type=ag.type,
            cpc_bid_micros=ag.cpc_bid_micros,
            cpm_bid_micros=ag.cpm_bid_micros,
            target_cpa_micros=ag.target_cpa_micros,
            target_roas=ag.target_roas,
            ad_rotation_mode=ag.ad_rotation_mode,
            created_at=ag.created_at,
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