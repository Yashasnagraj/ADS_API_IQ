"""
Keywords endpoints - Real-time Google Ads API queries
"""
from typing import Optional
from fastapi import APIRouter, HTTPException, Query
from app.services.google_ads_service import get_google_ads_service
from app.schemas.keyword import KeywordListResponse, KeywordDetail, KeywordSummary, KeywordMetrics
from app.schemas.search_term import SearchTermListResponse, SearchTermDetail, SearchTermMetrics
from app.core.config import settings
from loguru import logger

router = APIRouter(prefix="/keywords", tags=["keywords"])


@router.get("", response_model=KeywordListResponse)
def get_keywords(
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
    customer_id: Optional[int] = Query(default=None, description="Filter by customer ID"),
    campaign_id: Optional[int] = None,
    status: Optional[str] = None,
    quality_score_min: Optional[int] = Query(None, ge=1, le=10),
):
    """
    Get all keywords with performance metrics
    Real-time query from Google Ads API
    """
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id is required")

    try:
        ads_service = get_google_ads_service()
        customer_id_str = str(customer_id)

        # Get keywords from Google Ads API
        keywords_data = ads_service.get_keywords(
            customer_id_str,
            campaign_id=campaign_id,
            date_range="LAST_30_DAYS",
            min_quality_score=quality_score_min
        )

        # Filter by status if provided
        if status:
            keywords_data = [
                k for k in keywords_data
                if k.get("ad_group_criterion", {}).get("status") == status
            ]

        # Apply pagination
        total = len(keywords_data)
        paginated_keywords = keywords_data[offset:offset + limit]

        keyword_summaries = []
        for keyword_row in paginated_keywords:
            ad_group_criterion = keyword_row.get("ad_group_criterion", {})
            keyword_info = ad_group_criterion.get("keyword", {})
            quality_info = ad_group_criterion.get("quality_info", {})
            ad_group = keyword_row.get("ad_group", {})
            campaign = keyword_row.get("campaign", {})
            metrics = keyword_row.get("metrics", {})

            # Extract keyword ID
            criterion_id = ad_group_criterion.get("criterion_id", 0)
            keyword_id = f"{customer_id}_{campaign.get('id', 0)}_{ad_group.get('id', 0)}_{criterion_id}"

            # Calculate quality score
            quality_score = quality_info.get("quality_score", 0)
            clicks_val = float(metrics.get("clicks", 0) or 0)
            if quality_score == 0 and clicks_val > 0:
                # Estimate quality score from metrics
                ctr = float(metrics.get("ctr", 0) or 0)
                quality_score = min(max(int(ctr * 200), 1), 10)

            # Determine competition level
            avg_cpc = float(metrics.get("average_cpc", 0) or 0)
            impressions = float(metrics.get("impressions", 0) or 0)
            if avg_cpc > 2.0 or impressions > 100000:
                competition = "HIGH"
            elif avg_cpc > 0.5 or impressions > 10000:
                competition = "MEDIUM"
            else:
                competition = "LOW"

            # Build metrics object
            conversions_val = float(metrics.get("conversions", 0) or 0)
            keyword_metrics = KeywordMetrics(
                clicks=metrics.get("clicks", 0),
                impressions=metrics.get("impressions", 0),
                cost=metrics.get("cost", 0),
                conversions=metrics.get("conversions", 0),
                ctr=metrics.get("ctr", 0),
                conversion_rate=(conversions_val / clicks_val) if clicks_val > 0 else 0,
                avg_cpc=avg_cpc
            )

            summary = KeywordSummary(
                keyword_id=keyword_id,
                ad_group_id=ad_group.get("id", 0),
                campaign_id=campaign.get("id", 0),
                customer_id=customer_id,
                keyword_text=keyword_info.get("text", ""),
                match_type=keyword_info.get("match_type", ""),
                status=ad_group_criterion.get("status", ""),
                quality_score=quality_score,
                competition=competition,
                metrics=keyword_metrics
            )
            keyword_summaries.append(summary)

        return KeywordListResponse(
            keywords=keyword_summaries,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )

    except Exception as e:
        logger.error(f"Error fetching keywords: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch keywords: {str(e)}")


@router.get("/{keyword_id}", response_model=KeywordDetail)
def get_keyword(
    keyword_id: str,
    customer_id: int = Query(..., description="Customer ID")
):
    """
    Get keyword detail with performance metrics
    Real-time query from Google Ads API
    """
    try:
        ads_service = get_google_ads_service()
        customer_id_str = str(customer_id)

        # Parse keyword_id: format is customer_campaign_adgroup_criterion
        parts = keyword_id.split("_")
        if len(parts) < 4:
            raise HTTPException(status_code=400, detail="Invalid keyword_id format")

        criterion_id = parts[3]

        # Get all keywords and find the matching one
        keywords_data = ads_service.get_keywords(
            customer_id_str,
            date_range="LAST_30_DAYS"
        )

        # Find matching keyword
        keyword_row = None
        for row in keywords_data:
            ad_group_criterion = row.get("ad_group_criterion", {})
            if str(ad_group_criterion.get("criterion_id", 0)) == criterion_id:
                keyword_row = row
                break

        if not keyword_row:
            raise HTTPException(status_code=404, detail=f"Keyword {keyword_id} not found")

        ad_group_criterion = keyword_row.get("ad_group_criterion", {})
        keyword_info = ad_group_criterion.get("keyword", {})
        quality_info = ad_group_criterion.get("quality_info", {})
        ad_group = keyword_row.get("ad_group", {})
        campaign = keyword_row.get("campaign", {})
        metrics = keyword_row.get("metrics", {})

        # Build metrics object
        clicks_val = float(metrics.get("clicks", 0) or 0)
        conversions_val = float(metrics.get("conversions", 0) or 0)

        keyword_metrics = KeywordMetrics(
            clicks=metrics.get("clicks", 0),
            impressions=metrics.get("impressions", 0),
            cost=metrics.get("cost", 0),
            conversions=metrics.get("conversions", 0),
            ctr=metrics.get("ctr", 0),
            conversion_rate=(conversions_val / clicks_val) if clicks_val > 0 else 0,
            avg_cpc=metrics.get("average_cpc", 0)
        )

        return KeywordDetail(
            keyword_id=keyword_id,
            ad_group_id=ad_group.get("id", 0),
            campaign_id=campaign.get("id", 0),
            customer_id=customer_id,
            keyword_text=keyword_info.get("text", ""),
            match_type=keyword_info.get("match_type", ""),
            status=ad_group_criterion.get("status", ""),
            quality_score=quality_info.get("quality_score", 0),
            creative_quality_score=quality_info.get("creative_quality_score", ""),
            landing_page_quality_score=quality_info.get("post_click_quality_score", ""),
            search_predicted_ctr=quality_info.get("search_predicted_ctr", ""),
            cpc_bid_micros=ad_group_criterion.get("cpc_bid_micros", 0),
            first_page_cpc_micros=0,
            first_position_cpc_micros=0,
            top_of_page_cpc_micros=0,
            approval_status=ad_group_criterion.get("approval_status", ""),
            system_serving_status=ad_group_criterion.get("system_serving_status", ""),
            is_negative=ad_group_criterion.get("negative", False),
            bid_modifier=0,
            created_at=None,
            metrics=keyword_metrics
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching keyword {keyword_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch keyword: {str(e)}")


@router.get("/{keyword_id}/search-terms", response_model=SearchTermListResponse)
def get_keyword_search_terms(
    keyword_id: str,
    customer_id: int = Query(..., description="Customer ID"),
    limit: int = Query(default=settings.PAGINATION_DEFAULT_LIMIT, ge=1, le=settings.PAGINATION_MAX_LIMIT),
    offset: int = Query(default=0, ge=0),
):
    """
    Get search terms linked to a specific keyword
    Real-time query from Google Ads API
    """
    try:
        ads_service = get_google_ads_service()
        customer_id_str = str(customer_id)

        # Parse keyword_id to get keyword text
        parts = keyword_id.split("_")
        if len(parts) < 4:
            raise HTTPException(status_code=400, detail="Invalid keyword_id format")

        # Get all search terms for this customer
        search_terms_data = ads_service.get_search_terms(
            customer_id_str,
            date_range="LAST_30_DAYS"
        )

        # Filter by keyword (match on keyword text)
        # Note: We'll need to fetch the keyword first to get its text
        keywords_data = ads_service.get_keywords(customer_id_str, date_range="LAST_30_DAYS")
        criterion_id = parts[3]

        target_keyword_text = None
        for kw_row in keywords_data:
            ad_group_criterion = kw_row.get("ad_group_criterion", {})
            if str(ad_group_criterion.get("criterion_id", 0)) == criterion_id:
                target_keyword_text = ad_group_criterion.get("keyword", {}).get("text", "")
                break

        if not target_keyword_text:
            raise HTTPException(status_code=404, detail=f"Keyword {keyword_id} not found")

        # Filter search terms by keyword text
        filtered_search_terms = [
            st for st in search_terms_data
            if st.get("segments", {}).get("keyword", {}).get("info", {}).get("text", "") == target_keyword_text
        ]

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

            detail = SearchTermDetail(
                search_term_id=idx + offset,
                keyword_id=keyword_id,
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

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching search terms for keyword {keyword_id}: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch search terms: {str(e)}")
