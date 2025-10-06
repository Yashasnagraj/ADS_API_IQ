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
    customer_id: Optional[int] = Query(default=None, description="Filter by customer ID"),
    campaign_id: Optional[int] = None,
    status: Optional[str] = None,
    quality_score_min: Optional[int] = Query(None, ge=1, le=10),
    db: Session = Depends(get_db)
):
    """
    Get all keywords with performance metrics
    Filter by customer_id to show only specific customer's keywords
    """
    query = db.query(Keyword)

    if customer_id:
        query = query.filter(Keyword.customer_id == customer_id)
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

        # Calculate quality score if missing (based on CTR, CPC efficiency, conversion rate)
        calculated_quality_score = keyword.quality_score
        if calculated_quality_score is None or calculated_quality_score == 0:
            # Quality Score calculation (1-10 scale)
            # Based on: CTR (40%), CPC efficiency (20%), Conversion Rate (20%), Landing Page (20%)

            # CTR Score: Higher CTR = Higher Quality (0-10%)
            ctr_score = min(metrics.ctr * 100, 10) * 0.4

            # CPC Efficiency Score: Lower CPC relative to performance = Higher Quality
            # Benchmark: Good CPC is < $1, Excellent < $0.50
            cpc_score = 5.0  # Default
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

            # Landing page score (estimated from performance)
            landing_score = 5.0  # Default middle score
            if metrics.ctr > 0.05 and metrics.conversion_rate > 0.02:
                landing_score = 8.0
            elif metrics.ctr > 0.03 and metrics.conversion_rate > 0.01:
                landing_score = 6.5
            elif metrics.ctr < 0.01 or metrics.conversion_rate < 0.005:
                landing_score = 3.0
            landing_score = landing_score * 0.2

            calculated_quality_score = min(max(ctr_score + cpc_score + conv_score + landing_score, 1), 10)

        # Calculate competition level based on CPC and impressions
        competition = "UNKNOWN"
        if metrics.avg_cpc > 0 and metrics.impressions > 0:
            # High competition: High CPC (>$2) OR very high impressions
            if metrics.avg_cpc > 2.0 or metrics.impressions > 100000:
                competition = "HIGH"
            # Medium competition: Moderate CPC ($0.50-$2) OR moderate impressions
            elif metrics.avg_cpc > 0.5 or metrics.impressions > 10000:
                competition = "MEDIUM"
            # Low competition: Low CPC (<$0.50) AND low impressions
            else:
                competition = "LOW"

        summary = KeywordSummary(
            keyword_id=keyword.keyword_id,
            ad_group_id=keyword.ad_group_id,
            campaign_id=keyword.campaign_id,
            customer_id=keyword.customer_id,
            keyword_text=keyword.keyword_text,
            match_type=keyword.match_type,
            status=keyword.status,
            quality_score=round(calculated_quality_score, 2),
            competition=competition,
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