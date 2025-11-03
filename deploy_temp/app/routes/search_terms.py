"""
Search Terms endpoints - Real-time Google Ads API queries
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.google_ads_service import get_google_ads_service
from app.schemas.search_term import SearchTermListResponse, SearchTermDetail, SearchTermMetrics
from app.core.config import settings
from loguru import logger

router = APIRouter(prefix="/search-terms", tags=["search_terms"])

@router.get("", response_model=SearchTermListResponse)
def get_search_terms(
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    customer_id: Optional[int] = Query(default=None, description="Filter by customer ID"),
    campaign_id: Optional[int] = None,
    ad_group_id: Optional[int] = None,
    search_term: Optional[str] = None,
    min_impressions: Optional[int] = None,
):
    """
    Get all search terms with performance data
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
            return SearchTermListResponse(
                search_terms=[],
                total=0,
                limit=limit,
                offset=offset,
                has_more=False
            )

        customer_id_str = str(customer_id)

        # Get search terms from Google Ads API
        search_terms_data = ads_service.get_search_terms(
            customer_id_str,
            campaign_id=campaign_id,
            date_range="LAST_30_DAYS"
        )

        # Apply filters
        filtered_search_terms = search_terms_data

        if ad_group_id:
            filtered_search_terms = [
                st for st in filtered_search_terms
                if st.get("ad_group", {}).get("id") == ad_group_id
            ]

        if search_term:
            search_term_lower = search_term.lower()
            filtered_search_terms = [
                st for st in filtered_search_terms
                if search_term_lower in st.get("search_term_view", {}).get("search_term", "").lower()
            ]

        if min_impressions:
            filtered_search_terms = [
                st for st in filtered_search_terms
                if st.get("metrics", {}).get("impressions", 0) >= min_impressions
            ]

        # Sort by impressions descending
        filtered_search_terms.sort(
            key=lambda x: x.get("metrics", {}).get("impressions", 0),
            reverse=True
        )

        # Apply pagination
        total = len(filtered_search_terms)
        paginated_search_terms = filtered_search_terms[offset:offset + limit]

        search_term_details = []
        for idx, st_row in enumerate(paginated_search_terms):
            search_term_view = st_row.get("search_term_view", {})
            segments = st_row.get("segments", {})
            keyword_segment = segments.get("keyword", {}).get("info", {})
            metrics = st_row.get("metrics", {})
            ad_group = st_row.get("ad_group", {})
            campaign = st_row.get("campaign", {})

            st_metrics = SearchTermMetrics(
                date=segments.get("date", ""),
                clicks=metrics.get("clicks", 0),
                impressions=metrics.get("impressions", 0),
                cost=metrics.get("cost", 0),
                conversions=metrics.get("conversions", 0),
                conversion_value=metrics.get("conversions_value", 0),
                ctr=metrics.get("ctr", 0),
                avg_cpc=metrics.get("average_cpc", 0)
            )

            # Create a unique ID for search term
            search_term_id = idx + offset

            detail = SearchTermDetail(
                search_term_id=search_term_id,
                keyword_id=None,  # Would need to match with keyword
                ad_group_id=ad_group.get("id", 0),
                campaign_id=campaign.get("id", 0),
                customer_id=customer_id,
                search_term=search_term_view.get("search_term", ""),
                keyword_text=keyword_segment.get("text", ""),
                match_type=keyword_segment.get("match_type", ""),
                search_term_match_type=search_term_view.get("search_term_match_type", ""),
                metrics=st_metrics,
                created_at=None
            )
            search_term_details.append(detail)

        return SearchTermListResponse(
            search_terms=search_term_details,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )

    except Exception as e:
        logger.warning(f"Error fetching search terms: {e}")
        # Return empty result instead of raising error
        return SearchTermListResponse(
            search_terms=[],
            total=0,
            limit=limit,
            offset=offset,
            has_more=False
        )
