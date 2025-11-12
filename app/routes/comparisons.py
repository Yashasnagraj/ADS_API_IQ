"""
Historical Comparison API Routes
Provides week-over-week, month-over-month, and custom period comparisons
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.db.database import get_db
from app.schemas.metrics import MetricComparison, MetricComparisonResponse

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/comparisons",
    tags=["comparisons"]
)


def calculate_comparison_period(date_range: str, start_date: Optional[str], end_date: Optional[str]) -> tuple:
    """
    Calculate current and previous period dates based on comparison type
    Returns: (current_start, current_end, previous_start, previous_end)
    """
    if date_range == "CUSTOM" and start_date and end_date:
        current_end = datetime.strptime(end_date, "%Y-%m-%d")
        current_start = datetime.strptime(start_date, "%Y-%m-%d")
    else:
        current_end = datetime.now()
        if date_range == "LAST_7_DAYS":
            current_start = current_end - timedelta(days=7)
        elif date_range == "LAST_30_DAYS":
            current_start = current_end - timedelta(days=30)
        elif date_range == "LAST_90_DAYS":
            current_start = current_end - timedelta(days=90)
        elif date_range == "THIS_MONTH":
            current_start = current_end.replace(day=1)
        elif date_range == "LAST_MONTH":
            first_day_this_month = current_end.replace(day=1)
            current_end = first_day_this_month - timedelta(days=1)
            current_start = current_end.replace(day=1)
        else:
            current_start = current_end - timedelta(days=30)

    # Calculate previous period of same length
    period_length = (current_end - current_start).days
    previous_end = current_start - timedelta(days=1)
    previous_start = previous_end - timedelta(days=period_length)

    return (
        current_start.strftime("%Y-%m-%d"),
        current_end.strftime("%Y-%m-%d"),
        previous_start.strftime("%Y-%m-%d"),
        previous_end.strftime("%Y-%m-%d")
    )


@router.get("/metrics", response_model=MetricComparisonResponse)
async def get_metric_comparison(
    customer_id: str = Query(..., description="Customer ID"),
    metric: str = Query(..., description="Metric name: spend, conversions, roas, ctr, cpc, sessions, bounce_rate"),
    date_range: str = Query("LAST_30_DAYS", description="Date range for comparison"),
    start_date: Optional[str] = Query(None, description="Start date for custom range (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for custom range (YYYY-MM-DD)"),
    platform: Optional[str] = Query(None, description="Filter by platform: google_ads, meta_ads, ga4"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    db: Session = Depends(get_db)
):
    """
    Get week-over-week or period-over-period comparison for a specific metric

    Supported metrics:
    - spend: Total spend
    - conversions: Total conversions
    - roas: Return on ad spend
    - ctr: Click-through rate
    - cpc: Cost per click
    - cpm: Cost per mille (1000 impressions)
    - sessions: Total sessions (GA4)
    - bounce_rate: Bounce rate (GA4)
    - conversion_rate: Conversion rate
    """
    try:
        # Calculate period dates
        current_start, current_end, previous_start, previous_end = calculate_comparison_period(
            date_range, start_date, end_date
        )

        logger.info(f"Comparing metric '{metric}' for customer {customer_id}")
        logger.info(f"Current period: {current_start} to {current_end}")
        logger.info(f"Previous period: {previous_start} to {previous_end}")

        # Build metric query based on metric name
        metric_sql_map = {
            "spend": "SUM(spend_micros) / 1000000.0",
            "conversions": "SUM(conversions)",
            "roas": "CASE WHEN SUM(spend_micros) > 0 THEN SUM(conversion_value_micros) / SUM(spend_micros) ELSE 0 END",
            "ctr": "CASE WHEN SUM(impressions) > 0 THEN (SUM(clicks) * 100.0 / SUM(impressions)) ELSE 0 END",
            "cpc": "CASE WHEN SUM(clicks) > 0 THEN SUM(spend_micros) / SUM(clicks) / 1000000.0 ELSE 0 END",
            "cpm": "CASE WHEN SUM(impressions) > 0 THEN (SUM(spend_micros) / SUM(impressions) * 1000) / 1000000.0 ELSE 0 END",
            "conversion_rate": "CASE WHEN SUM(clicks) > 0 THEN (SUM(conversions) * 100.0 / SUM(clicks)) ELSE 0 END",
            "impressions": "SUM(impressions)",
            "clicks": "SUM(clicks)"
        }

        if metric not in metric_sql_map:
            raise HTTPException(status_code=400, detail=f"Unsupported metric: {metric}")

        metric_sql = metric_sql_map[metric]

        # Build WHERE clause
        where_clauses = ["customer_id = :customer_id"]
        params = {
            "customer_id": customer_id,
            "current_start": current_start,
            "current_end": current_end,
            "previous_start": previous_start,
            "previous_end": previous_end
        }

        if platform:
            where_clauses.append("platform_id = (SELECT platform_id FROM dim_platform WHERE platform_name = :platform)")
            params["platform"] = platform

        if campaign_id:
            where_clauses.append("(google_campaign_id = :campaign_id OR meta_campaign_id = :campaign_id)")
            params["campaign_id"] = campaign_id

        where_sql = " AND ".join(where_clauses)

        # Query for current period
        current_query = text(f"""
            SELECT {metric_sql} as metric_value
            FROM fact_campaign_performance_daily
            WHERE {where_sql}
                AND date_id BETWEEN REPLACE(:current_start, '-', '') AND REPLACE(:current_end, '-', '')
        """)

        # Query for previous period
        previous_query = text(f"""
            SELECT {metric_sql} as metric_value
            FROM fact_campaign_performance_daily
            WHERE {where_sql}
                AND date_id BETWEEN REPLACE(:previous_start, '-', '') AND REPLACE(:previous_end, '-', '')
        """)

        current_result = db.execute(current_query, params).fetchone()
        previous_result = db.execute(previous_query, params).fetchone()

        current_value = float(current_result[0]) if current_result and current_result[0] is not None else 0.0
        previous_value = float(previous_result[0]) if previous_result and previous_result[0] is not None else 0.0

        # Calculate change percentage and direction
        if previous_value > 0:
            change_percentage = ((current_value - previous_value) / previous_value) * 100
        else:
            change_percentage = 100.0 if current_value > 0 else 0.0

        if current_value > previous_value:
            change_direction = "increase"
        elif current_value < previous_value:
            change_direction = "decrease"
        else:
            change_direction = "no_change"

        # Determine if the change is positive based on metric type
        # For metrics like bounce_rate, cpc, cpa - decrease is good
        inverse_metrics = ["bounce_rate", "cpc", "cpm", "cpa"]
        if metric in inverse_metrics:
            is_positive = change_direction == "decrease"
        else:
            is_positive = change_direction == "increase"

        return MetricComparisonResponse(
            metric_name=metric,
            current_value=round(current_value, 2),
            previous_value=round(previous_value, 2),
            change_percentage=round(change_percentage, 2),
            change_direction=change_direction,
            is_positive_change=is_positive,
            current_period_start=current_start,
            current_period_end=current_end,
            previous_period_start=previous_start,
            previous_period_end=previous_end
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing metric: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare metric: {str(e)}")


@router.get("/metrics/batch", response_model=List[MetricComparisonResponse])
async def get_batch_metric_comparisons(
    customer_id: str = Query(..., description="Customer ID"),
    metrics: str = Query(..., description="Comma-separated list of metrics"),
    date_range: str = Query("LAST_30_DAYS", description="Date range for comparison"),
    start_date: Optional[str] = Query(None, description="Start date for custom range"),
    end_date: Optional[str] = Query(None, description="End date for custom range"),
    platform: Optional[str] = Query(None, description="Filter by platform"),
    campaign_id: Optional[str] = Query(None, description="Filter by campaign ID"),
    db: Session = Depends(get_db)
):
    """
    Get comparisons for multiple metrics in a single request
    Example: ?metrics=spend,conversions,roas,ctr
    """
    metric_list = [m.strip() for m in metrics.split(",")]
    results = []

    for metric in metric_list:
        try:
            result = await get_metric_comparison(
                customer_id=customer_id,
                metric=metric,
                date_range=date_range,
                start_date=start_date,
                end_date=end_date,
                platform=platform,
                campaign_id=campaign_id,
                db=db
            )
            results.append(result)
        except Exception as e:
            logger.warning(f"Failed to get comparison for metric {metric}: {e}")
            # Continue with other metrics
            continue

    return results


@router.get("/ga4/metrics", response_model=MetricComparisonResponse)
async def get_ga4_metric_comparison(
    customer_id: str = Query(..., description="Customer ID"),
    metric: str = Query(..., description="Metric: sessions, bounce_rate, conversion_rate, avg_session_duration"),
    date_range: str = Query("LAST_30_DAYS", description="Date range for comparison"),
    start_date: Optional[str] = Query(None, description="Start date for custom range"),
    end_date: Optional[str] = Query(None, description="End date for custom range"),
    db: Session = Depends(get_db)
):
    """
    Get GA4-specific metric comparisons

    Note: GA4 metrics are stored in the ga4_metrics JSON field
    """
    try:
        current_start, current_end, previous_start, previous_end = calculate_comparison_period(
            date_range, start_date, end_date
        )

        # GA4 metric queries
        ga4_metric_queries = {
            "sessions": "SUM(CAST(json_extract(ga4_metrics, '$.sessions') AS INTEGER))",
            "bounce_rate": "AVG(CAST(json_extract(ga4_metrics, '$.bounce_rate') AS REAL))",
            "conversion_rate": "AVG(CAST(json_extract(ga4_metrics, '$.conversion_rate') AS REAL))",
            "avg_session_duration": "AVG(CAST(json_extract(ga4_metrics, '$.avg_session_duration') AS REAL))",
            "pages_per_session": "AVG(CAST(json_extract(ga4_metrics, '$.pages_per_session') AS REAL))"
        }

        if metric not in ga4_metric_queries:
            raise HTTPException(status_code=400, detail=f"Unsupported GA4 metric: {metric}")

        metric_sql = ga4_metric_queries[metric]

        # Query current period
        current_query = text(f"""
            SELECT {metric_sql} as metric_value
            FROM fact_campaign_performance_daily
            WHERE customer_id = :customer_id
                AND platform_id = (SELECT platform_id FROM dim_platform WHERE platform_name = 'ga4')
                AND ga4_metrics IS NOT NULL
                AND date_id BETWEEN REPLACE(:current_start, '-', '') AND REPLACE(:current_end, '-', '')
        """)

        # Query previous period
        previous_query = text(f"""
            SELECT {metric_sql} as metric_value
            FROM fact_campaign_performance_daily
            WHERE customer_id = :customer_id
                AND platform_id = (SELECT platform_id FROM dim_platform WHERE platform_name = 'ga4')
                AND ga4_metrics IS NOT NULL
                AND date_id BETWEEN REPLACE(:previous_start, '-', '') AND REPLACE(:previous_end, '-', '')
        """)

        params = {
            "customer_id": customer_id,
            "current_start": current_start,
            "current_end": current_end,
            "previous_start": previous_start,
            "previous_end": previous_end
        }

        current_result = db.execute(current_query, params).fetchone()
        previous_result = db.execute(previous_query, params).fetchone()

        current_value = float(current_result[0]) if current_result and current_result[0] is not None else 0.0
        previous_value = float(previous_result[0]) if previous_result and previous_result[0] is not None else 0.0

        # Calculate change
        if previous_value > 0:
            change_percentage = ((current_value - previous_value) / previous_value) * 100
        else:
            change_percentage = 100.0 if current_value > 0 else 0.0

        change_direction = "increase" if current_value > previous_value else ("decrease" if current_value < previous_value else "no_change")

        # Bounce rate decrease is good
        is_positive = (change_direction == "decrease" if metric == "bounce_rate" else change_direction == "increase")

        return MetricComparisonResponse(
            metric_name=metric,
            current_value=round(current_value, 2),
            previous_value=round(previous_value, 2),
            change_percentage=round(change_percentage, 2),
            change_direction=change_direction,
            is_positive_change=is_positive,
            current_period_start=current_start,
            current_period_end=current_end,
            previous_period_start=previous_start,
            previous_period_end=previous_end
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error comparing GA4 metric: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to compare GA4 metric: {str(e)}")
