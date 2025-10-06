"""
Ad Group endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models import AdGroup, CampaignKeyword, Keyword
from app.schemas.ad_group import AdGroupDetail, AdGroupMetrics, AdGroupListResponse
from app.schemas.keyword import KeywordListResponse, KeywordSummary, KeywordMetrics
from app.core.config import settings

router = APIRouter(prefix="/adgroups", tags=["ad_groups"])

@router.get("", response_model=AdGroupListResponse)
def list_ad_groups(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    campaign_id: Optional[int] = Query(None, description="Filter by campaign ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    List all ad groups with optional filters
    """
    query = db.query(AdGroup)

    # Apply filters
    if customer_id:
        query = query.filter(AdGroup.customer_id == customer_id)
    if campaign_id:
        query = query.filter(AdGroup.campaign_id == campaign_id)
    if status:
        query = query.filter(AdGroup.status == status)

    total = query.count()
    ad_groups = query.offset(offset).limit(limit).all()

    ad_group_details = []
    for ad_group in ad_groups:
        metrics = get_ad_group_metrics(ad_group.ad_group_id, db)

        # Calculate quality score dynamically
        ctr_score = min(metrics.ctr * 100, 10) * 0.4

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

        conv_rate = metrics.conversions / metrics.clicks if metrics.clicks > 0 else 0
        conv_score = min(conv_rate * 50, 10) * 0.2

        perf_score = 5.0
        if metrics.ctr > 0.05 and conv_rate > 0.02:
            perf_score = 8.0
        elif metrics.ctr > 0.03 and conv_rate > 0.01:
            perf_score = 6.5
        elif metrics.ctr < 0.01:
            perf_score = 3.0
        perf_score = perf_score * 0.2

        quality_score = min(max(ctr_score + cpc_score + conv_score + perf_score, 1), 10)

        # Calculate competition
        competition = "UNKNOWN"
        if metrics.avg_cpc > 0 and metrics.impressions > 0:
            if metrics.avg_cpc > 2.0 or metrics.impressions > 50000:
                competition = "HIGH"
            elif metrics.avg_cpc > 0.5 or metrics.impressions > 5000:
                competition = "MEDIUM"
            else:
                competition = "LOW"

        detail = AdGroupDetail(
            ad_group_id=ad_group.ad_group_id,
            campaign_id=ad_group.campaign_id,
            customer_id=ad_group.customer_id,
            ad_group_name=ad_group.ad_group_name,
            status=ad_group.status,
            type=ad_group.type,
            cpc_bid_micros=ad_group.cpc_bid_micros,
            cpm_bid_micros=ad_group.cpm_bid_micros,
            target_cpa_micros=ad_group.target_cpa_micros,
            target_roas=ad_group.target_roas,
            ad_rotation_mode=ad_group.ad_rotation_mode,
            created_at=ad_group.created_at,
            quality_score=round(quality_score, 2),
            competition=competition,
            metrics=metrics
        )
        ad_group_details.append(detail)

    return AdGroupListResponse(
        ad_groups=ad_group_details,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total
    )

def get_ad_group_metrics(ad_group_id: int, db: Session) -> AdGroupMetrics:
    """Get aggregated metrics for an ad group"""
    # Get keyword IDs for this ad group
    keyword_ids = db.query(Keyword.keyword_id).filter(Keyword.ad_group_id == ad_group_id).subquery()

    metrics = db.query(
        func.coalesce(func.sum(CampaignKeyword.clicks), 0).label("clicks"),
        func.coalesce(func.sum(CampaignKeyword.impressions), 0).label("impressions"),
        func.coalesce(func.sum(CampaignKeyword.cost_micros), 0).label("cost_micros"),
        func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("conversions"),
    ).filter(CampaignKeyword.keyword_id.in_(keyword_ids)).first()

    clicks = metrics.clicks or 0
    impressions = metrics.impressions or 0
    cost_micros = metrics.cost_micros or 0
    conversions = metrics.conversions or 0

    return AdGroupMetrics(
        clicks=clicks,
        impressions=impressions,
        cost=cost_micros / 1_000_000 if cost_micros else 0,
        conversions=conversions,
        ctr=clicks / impressions if impressions > 0 else 0,
        avg_cpc=cost_micros / clicks / 1_000_000 if clicks > 0 else 0
    )

@router.get("/{ad_group_id}", response_model=AdGroupDetail)
def get_ad_group(ad_group_id: int, db: Session = Depends(get_db)):
    """
    Get ad group details with metrics
    """
    ad_group = db.query(AdGroup).filter(AdGroup.ad_group_id == ad_group_id).first()

    if not ad_group:
        raise HTTPException(status_code=404, detail=f"Ad group {ad_group_id} not found")

    metrics = get_ad_group_metrics(ad_group_id, db)

    return AdGroupDetail(
        ad_group_id=ad_group.ad_group_id,
        campaign_id=ad_group.campaign_id,
        customer_id=ad_group.customer_id,
        ad_group_name=ad_group.ad_group_name,
        status=ad_group.status,
        type=ad_group.type,
        cpc_bid_micros=ad_group.cpc_bid_micros,
        cpm_bid_micros=ad_group.cpm_bid_micros,
        target_cpa_micros=ad_group.target_cpa_micros,
        target_roas=ad_group.target_roas,
        ad_rotation_mode=ad_group.ad_rotation_mode,
        created_at=ad_group.created_at,
        metrics=metrics
    )

@router.get("/{ad_group_id}/keywords", response_model=KeywordListResponse)
def get_ad_group_keywords(
    ad_group_id: int,
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get keywords in an ad group
    """
    # Check if ad group exists
    ad_group = db.query(AdGroup).filter(AdGroup.ad_group_id == ad_group_id).first()
    if not ad_group:
        raise HTTPException(status_code=404, detail=f"Ad group {ad_group_id} not found")

    query = db.query(Keyword).filter(Keyword.ad_group_id == ad_group_id)
    total = query.count()
    keywords = query.offset(offset).limit(limit).all()

    keyword_summaries = []
    for keyword in keywords:
        # Get metrics for keyword
        metrics = db.query(
            func.coalesce(func.sum(CampaignKeyword.clicks), 0).label("clicks"),
            func.coalesce(func.sum(CampaignKeyword.impressions), 0).label("impressions"),
            func.coalesce(func.sum(CampaignKeyword.cost_micros), 0).label("cost_micros"),
            func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("conversions"),
            func.coalesce(func.avg(CampaignKeyword.ctr), 0).label("ctr"),
            func.coalesce(func.avg(CampaignKeyword.conversion_rate), 0).label("conversion_rate"),
        ).filter(CampaignKeyword.keyword_id == keyword.keyword_id).first()

        clicks = metrics.clicks or 0
        impressions = metrics.impressions or 0
        cost_micros = metrics.cost_micros or 0
        conversions = metrics.conversions or 0

        kw_metrics = KeywordMetrics(
            clicks=clicks,
            impressions=impressions,
            cost=cost_micros / 1_000_000 if cost_micros else 0,
            conversions=conversions,
            ctr=metrics.ctr or 0,
            conversion_rate=metrics.conversion_rate or 0,
            avg_cpc=cost_micros / clicks / 1_000_000 if clicks > 0 else 0
        )

        summary = KeywordSummary(
            keyword_id=keyword.keyword_id,
            ad_group_id=keyword.ad_group_id,
            campaign_id=keyword.campaign_id,
            customer_id=keyword.customer_id,
            keyword_text=keyword.keyword_text,
            match_type=keyword.match_type,
            status=keyword.status,
            quality_score=keyword.quality_score,
            metrics=kw_metrics
        )
        keyword_summaries.append(summary)

    return KeywordListResponse(
        keywords=keyword_summaries,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total
    )