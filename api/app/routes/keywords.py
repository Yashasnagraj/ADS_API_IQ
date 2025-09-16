"""
Keyword endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db.database import get_db
from app.db.models import Keyword, CampaignKeyword, SearchTerm
from app.schemas.keyword import KeywordListResponse, KeywordDetail, KeywordSummary, KeywordMetrics
from app.schemas.search_term import SearchTermListResponse, SearchTermDetail, SearchTermMetrics
from app.core.config import settings

router = APIRouter(prefix="/keywords", tags=["keywords"])

def get_keyword_metrics(keyword_id: str, db: Session) -> KeywordMetrics:
    """Get aggregated metrics for a keyword"""
    metrics = db.query(
        func.coalesce(func.sum(CampaignKeyword.clicks), 0).label("clicks"),
        func.coalesce(func.sum(CampaignKeyword.impressions), 0).label("impressions"),
        func.coalesce(func.sum(CampaignKeyword.cost_micros), 0).label("cost_micros"),
        func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("conversions"),
        func.coalesce(func.avg(CampaignKeyword.ctr), 0).label("ctr"),
        func.coalesce(func.avg(CampaignKeyword.conversion_rate), 0).label("conversion_rate"),
    ).filter(CampaignKeyword.keyword_id == keyword_id).first()

    clicks = metrics.clicks or 0
    impressions = metrics.impressions or 0
    cost_micros = metrics.cost_micros or 0
    conversions = metrics.conversions or 0

    return KeywordMetrics(
        clicks=clicks,
        impressions=impressions,
        cost=cost_micros / 1_000_000 if cost_micros else 0,
        conversions=conversions,
        ctr=metrics.ctr or 0,
        conversion_rate=metrics.conversion_rate or 0,
        avg_cpc=cost_micros / clicks / 1_000_000 if clicks > 0 else 0
    )

@router.get("", response_model=KeywordListResponse)
def get_keywords(
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    campaign_id: Optional[int] = None,
    status: Optional[str] = None,
    quality_score_min: Optional[int] = Query(None, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """
    Get all keywords with performance metrics
    """
    query = db.query(Keyword)

    if campaign_id:
        query = query.filter(Keyword.campaign_id == campaign_id)
    if status:
        query = query.filter(Keyword.status == status)
    if quality_score_min:
        query = query.filter(Keyword.quality_score >= quality_score_min)

    total = query.count()
    keywords = query.offset(offset).limit(limit).all()

    keyword_summaries = []
    for keyword in keywords:
        metrics = get_keyword_metrics(keyword.keyword_id, db)
        summary = KeywordSummary(
            keyword_id=keyword.keyword_id,
            ad_group_id=keyword.ad_group_id,
            campaign_id=keyword.campaign_id,
            customer_id=keyword.customer_id,
            keyword_text=keyword.keyword_text,
            match_type=keyword.match_type,
            status=keyword.status,
            quality_score=keyword.quality_score,
            metrics=metrics
        )
        keyword_summaries.append(summary)

    return KeywordListResponse(
        keywords=keyword_summaries,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total
    )

@router.get("/{keyword_id}", response_model=KeywordDetail)
def get_keyword(keyword_id: str, db: Session = Depends(get_db)):
    """
    Get keyword detail with performance metrics
    """
    keyword = db.query(Keyword).filter(Keyword.keyword_id == keyword_id).first()

    if not keyword:
        raise HTTPException(status_code=404, detail=f"Keyword {keyword_id} not found")

    metrics = get_keyword_metrics(keyword_id, db)

    return KeywordDetail(
        keyword_id=keyword.keyword_id,
        ad_group_id=keyword.ad_group_id,
        campaign_id=keyword.campaign_id,
        customer_id=keyword.customer_id,
        keyword_text=keyword.keyword_text,
        match_type=keyword.match_type,
        status=keyword.status,
        quality_score=keyword.quality_score,
        creative_quality_score=keyword.creative_quality_score,
        landing_page_quality_score=keyword.landing_page_quality_score,
        search_predicted_ctr=keyword.search_predicted_ctr,
        cpc_bid_micros=keyword.cpc_bid_micros,
        first_page_cpc_micros=keyword.first_page_cpc_micros,
        first_position_cpc_micros=keyword.first_position_cpc_micros,
        top_of_page_cpc_micros=keyword.top_of_page_cpc_micros,
        approval_status=keyword.approval_status,
        system_serving_status=keyword.system_serving_status,
        is_negative=keyword.is_negative,
        bid_modifier=keyword.bid_modifier,
        created_at=keyword.created_at,
        metrics=metrics
    )

@router.get("/{keyword_id}/search-terms", response_model=SearchTermListResponse)
def get_keyword_search_terms(
    keyword_id: str,
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db)
):
    """
    Get search terms linked to a specific keyword
    """
    # Check if keyword exists
    keyword = db.query(Keyword).filter(Keyword.keyword_id == keyword_id).first()
    if not keyword:
        raise HTTPException(status_code=404, detail=f"Keyword {keyword_id} not found")

    # Query search terms that match the keyword pattern
    # Since keyword_id might have wildcards in search_terms table, we need flexible matching
    query = db.query(SearchTerm).filter(
        SearchTerm.keyword_text == keyword.keyword_text,
        SearchTerm.ad_group_id == keyword.ad_group_id
    )

    total = query.count()
    search_terms = query.offset(offset).limit(limit).all()

    search_term_details = []
    for st in search_terms:
        st_metrics = SearchTermMetrics(
            date=st.date,
            clicks=st.clicks or 0,
            impressions=st.impressions or 0,
            cost=(st.cost_micros / 1_000_000) if st.cost_micros else 0,
            conversions=st.conversions or 0,
            conversion_value=st.conversion_value or 0,
            ctr=st.ctr or 0,
            avg_cpc=(st.avg_cpc_micros / 1_000_000) if st.avg_cpc_micros else 0
        )

        detail = SearchTermDetail(
            search_term_id=st.search_term_id,
            keyword_id=st.keyword_id,
            ad_group_id=st.ad_group_id,
            campaign_id=st.campaign_id,
            customer_id=st.customer_id,
            search_term=st.search_term,
            keyword_text=st.keyword_text,
            match_type=st.match_type,
            search_term_match_type=st.search_term_match_type,
            metrics=st_metrics,
            created_at=st.created_at
        )
        search_term_details.append(detail)

    return SearchTermListResponse(
        search_terms=search_term_details,
        total=total,
        limit=limit,
        offset=offset,
        has_more=(offset + limit) < total
    )