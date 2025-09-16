"""
Search Terms endpoints
"""
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.db.models import SearchTerm
from app.schemas.search_term import SearchTermListResponse, SearchTermDetail, SearchTermMetrics
from app.core.config import settings

router = APIRouter(prefix="/search-terms", tags=["search_terms"])

@router.get("", response_model=SearchTermListResponse)
def get_search_terms(
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    campaign_id: Optional[int] = None,
    ad_group_id: Optional[int] = None,
    search_term: Optional[str] = None,
    min_impressions: Optional[int] = None,
    db: Session = Depends(get_db)
):
    """
    Get all search terms with performance data
    """
    query = db.query(SearchTerm)

    if campaign_id:
        query = query.filter(SearchTerm.campaign_id == campaign_id)
    if ad_group_id:
        query = query.filter(SearchTerm.ad_group_id == ad_group_id)
    if search_term:
        query = query.filter(SearchTerm.search_term.ilike(f"%{search_term}%"))
    if min_impressions:
        query = query.filter(SearchTerm.impressions >= min_impressions)

    # Order by impressions descending for relevance
    query = query.order_by(SearchTerm.impressions.desc())

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