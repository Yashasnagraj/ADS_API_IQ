"""
Metrics endpoints for aggregation and time series
"""
from typing import Optional, List
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from app.db.database import get_db
from app.db.models import Campaign, CampaignKeyword, Keyword
from app.schemas.metrics import MetricsSummary, TimeSeriesResponse, TimeSeriesDataPoint
from app.core.config import settings

router = APIRouter(prefix="/metrics", tags=["metrics"])

@router.get("/summary", response_model=MetricsSummary)
def get_metrics_summary(
    date_range: str = Query(default="LAST_30_DAYS"),
    customer_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Get global metrics aggregation
    """
    # Validate date_range
    valid_ranges = ["LAST_7_DAYS", "LAST_30_DAYS", "LAST_90_DAYS", "THIS_MONTH", "LAST_MONTH", "THIS_YEAR", "ALL_TIME"]
    if date_range not in valid_ranges:
        raise HTTPException(status_code=422, detail=f"Invalid date_range. Must be one of: {', '.join(valid_ranges)}")

    # Build date filter
    date_filter = None
    if date_range != "ALL_TIME":
        if date_range in ["LAST_7_DAYS", "LAST_30_DAYS", "LAST_90_DAYS"]:
            days = {"LAST_7_DAYS": 7, "LAST_30_DAYS": 30, "LAST_90_DAYS": 90}[date_range]
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
        elif date_range == "THIS_MONTH":
            cutoff_date = datetime.now().replace(day=1).strftime("%Y-%m-%d")
        elif date_range == "LAST_MONTH":
            last_month = datetime.now().replace(day=1) - timedelta(days=1)
            cutoff_date = last_month.replace(day=1).strftime("%Y-%m-%d")
        elif date_range == "THIS_YEAR":
            cutoff_date = datetime.now().replace(month=1, day=1).strftime("%Y-%m-%d")

        date_filter = CampaignKeyword.date >= cutoff_date

    # Base query
    query = db.query(
        func.coalesce(func.sum(CampaignKeyword.clicks), 0).label("total_clicks"),
        func.coalesce(func.sum(CampaignKeyword.impressions), 0).label("total_impressions"),
        func.coalesce(func.sum(CampaignKeyword.cost_micros), 0).label("total_cost_micros"),
        func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("total_conversions"),
        func.coalesce(func.sum(CampaignKeyword.conversion_value), 0).label("total_conversion_value"),
        func.coalesce(func.avg(CampaignKeyword.ctr), 0).label("avg_ctr"),
        func.coalesce(func.avg(CampaignKeyword.conversion_rate), 0).label("avg_conversion_rate"),
    )

    if customer_id:
        query = query.filter(CampaignKeyword.customer_id == customer_id)
    if date_filter is not None:
        query = query.filter(date_filter)

    metrics = query.first()

    # Get counts
    campaign_query = db.query(func.count(func.distinct(Campaign.campaign_id)))
    keyword_query = db.query(func.count(func.distinct(Keyword.keyword_id)))

    if customer_id:
        campaign_query = campaign_query.filter(Campaign.customer_id == customer_id)
        keyword_query = keyword_query.filter(Keyword.customer_id == customer_id)

    campaigns_count = campaign_query.scalar() or 0
    keywords_count = keyword_query.scalar() or 0

    total_clicks = metrics.total_clicks or 0
    total_cost_micros = metrics.total_cost_micros or 0

    return MetricsSummary(
        date_range=date_range,
        total_clicks=total_clicks,
        total_impressions=metrics.total_impressions or 0,
        total_cost=total_cost_micros / 1_000_000 if total_cost_micros else 0,
        total_conversions=metrics.total_conversions or 0,
        total_conversion_value=metrics.total_conversion_value or 0,
        avg_ctr=metrics.avg_ctr or 0,
        avg_conversion_rate=metrics.avg_conversion_rate or 0,
        avg_cpc=total_cost_micros / total_clicks / 1_000_000 if total_clicks > 0 else 0,
        campaigns_count=campaigns_count,
        keywords_count=keywords_count
    )

@router.get("/timeseries", response_model=TimeSeriesResponse)
def get_timeseries_metrics(
    interval: str = Query(default="daily"),
    campaign_id: Optional[int] = Query(default=None),
    days: int = Query(default=30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """
    Get time series data for charts
    """
    # Validate interval
    valid_intervals = ["daily", "weekly", "monthly"]
    if interval not in valid_intervals:
        raise HTTPException(status_code=422, detail=f"Invalid interval. Must be one of: {', '.join(valid_intervals)}")
    # Calculate date range
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    # Query campaign keywords data
    query = db.query(
        CampaignKeyword.date,
        func.sum(CampaignKeyword.clicks).label("clicks"),
        func.sum(CampaignKeyword.impressions).label("impressions"),
        func.sum(CampaignKeyword.cost_micros).label("cost_micros"),
        func.sum(CampaignKeyword.conversions).label("conversions"),
    ).filter(
        CampaignKeyword.date >= start_date.strftime("%Y-%m-%d")
    )

    if campaign_id:
        query = query.filter(CampaignKeyword.campaign_id == campaign_id)
        # Verify campaign exists
        campaign = db.query(Campaign).filter(Campaign.campaign_id == campaign_id).first()
        if not campaign:
            raise HTTPException(status_code=404, detail=f"Campaign {campaign_id} not found")

    # Group by date based on interval
    if interval == "daily":
        query = query.group_by(CampaignKeyword.date)
    elif interval == "weekly":
        # Group by week (SQLite specific)
        query = query.group_by(func.strftime('%Y-%W', CampaignKeyword.date))
    else:  # monthly
        query = query.group_by(func.strftime('%Y-%m', CampaignKeyword.date))

    query = query.order_by(CampaignKeyword.date)
    results = query.all()

    # Process results
    data_points = []
    for row in results:
        clicks = row.clicks or 0
        impressions = row.impressions or 0
        cost_micros = row.cost_micros or 0
        conversions = row.conversions or 0

        data_point = TimeSeriesDataPoint(
            date=row.date,
            clicks=clicks,
            impressions=impressions,
            cost=cost_micros / 1_000_000 if cost_micros else 0,
            conversions=conversions,
            ctr=clicks / impressions if impressions > 0 else 0,
            conversion_rate=conversions / clicks if clicks > 0 else 0
        )
        data_points.append(data_point)

    return TimeSeriesResponse(
        campaign_id=campaign_id,
        interval=interval,
        data_points=data_points
    )