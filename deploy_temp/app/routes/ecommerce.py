"""
E-commerce Performance Dashboard Endpoints
Provides e-commerce analytics for the dashboard
"""
from typing import Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, case
from app.db.database import get_db
from app.db.models import Campaign, CampaignKeyword
from app.schemas.ecommerce import (
    EcommerceOverview, EcommerceKPI, FunnelData, FunnelStage,
    ChannelPerformance, ChannelMetrics, ProductPerformance, ProductMetrics,
    CustomerSegmentation, CustomerSegment, RevenueForecast, ForecastDataPoint,
    AnomalyDetection, AnomalyAlert
)
from app.services.ecommerce_insights import EcommerceInsightsService

router = APIRouter(prefix="/ecommerce", tags=["ecommerce"])
insights_service = EcommerceInsightsService()


def calculate_trend(current: float, previous: float) -> float:
    """Calculate percentage trend"""
    if previous == 0:
        return 0
    return ((current - previous) / previous) * 100


@router.get("/overview", response_model=EcommerceOverview)
def get_ecommerce_overview(
    customer_id: Optional[int] = Query(default=None),
    date_range: str = Query(default="LAST_30_DAYS"),
    db: Session = Depends(get_db)
):
    """
    Get complete e-commerce dashboard overview
    All-in-one endpoint for the dashboard
    """
    kpis = get_ecommerce_kpis(customer_id=customer_id, date_range=date_range, db=db)
    funnel = get_funnel_data(customer_id=customer_id, date_range=date_range, db=db)
    channels = get_channel_performance(customer_id=customer_id, date_range=date_range, db=db)
    products = get_product_performance(customer_id=customer_id, date_range=date_range, db=db)
    segments = get_customer_segmentation(customer_id=customer_id, date_range=date_range, db=db)
    forecast = get_revenue_forecast(customer_id=customer_id, db=db)
    anomalies = get_anomaly_detection(customer_id=customer_id, db=db)

    return EcommerceOverview(
        kpis=kpis,
        funnel=funnel,
        channels=channels,
        products=products,
        segments=segments,
        forecast=forecast,
        anomalies=anomalies,
        customer_id=customer_id,
        date_range=date_range
    )


@router.get("/kpis", response_model=EcommerceKPI)
def get_ecommerce_kpis(
    customer_id: Optional[int] = Query(default=None),
    date_range: str = Query(default="LAST_30_DAYS"),
    db: Session = Depends(get_db)
):
    """
    Get header KPI metrics with trends
    """
    # Calculate date range
    days_map = {
        "LAST_7_DAYS": 7,
        "LAST_30_DAYS": 30,
        "LAST_90_DAYS": 90
    }
    days = days_map.get(date_range, 30)
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    previous_cutoff = (datetime.now() - timedelta(days=days * 2)).strftime("%Y-%m-%d")

    # Current period metrics
    current_query = db.query(
        func.coalesce(func.sum(CampaignKeyword.conversion_value), 0).label("revenue"),
        func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("orders"),
        func.coalesce(func.sum(CampaignKeyword.clicks), 0).label("clicks"),
        func.coalesce(func.sum(CampaignKeyword.impressions), 0).label("impressions")
    ).filter(CampaignKeyword.date >= cutoff_date)

    if customer_id:
        current_query = current_query.filter(CampaignKeyword.customer_id == customer_id)

    current = current_query.first()

    # Previous period metrics for trends
    previous_query = db.query(
        func.coalesce(func.sum(CampaignKeyword.conversion_value), 0).label("revenue"),
        func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("orders"),
        func.coalesce(func.sum(CampaignKeyword.clicks), 0).label("clicks")
    ).filter(
        and_(
            CampaignKeyword.date >= previous_cutoff,
            CampaignKeyword.date < cutoff_date
        )
    )

    if customer_id:
        previous_query = previous_query.filter(CampaignKeyword.customer_id == customer_id)

    previous = previous_query.first()

    # Calculate KPIs
    revenue = float(current.revenue or 0)
    orders = int(current.orders or 0)
    clicks = int(current.clicks or 0)
    impressions = int(current.impressions or 0)

    conversion_rate = (orders / clicks * 100) if clicks > 0 else 0
    avg_order_value = (revenue / orders) if orders > 0 else 0

    # Trends
    prev_revenue = float(previous.revenue or 0)
    prev_orders = int(previous.orders or 0)
    prev_clicks = int(previous.clicks or 0)
    prev_cvr = (prev_orders / prev_clicks * 100) if prev_clicks > 0 else 0
    prev_aov = (prev_revenue / prev_orders) if prev_orders > 0 else 0

    # Simulate returning customer rate and refund rate
    # TODO: Replace with real data when available
    returning_customer_rate = 22.0  # Mock value
    refund_rate = 3.5  # Mock value

    return EcommerceKPI(
        total_revenue=revenue,
        total_orders=orders,
        conversion_rate=conversion_rate,
        avg_order_value=avg_order_value,
        returning_customer_rate=returning_customer_rate,
        refund_rate=refund_rate,
        revenue_trend=calculate_trend(revenue, prev_revenue),
        orders_trend=calculate_trend(orders, prev_orders),
        cvr_trend=calculate_trend(conversion_rate, prev_cvr),
        aov_trend=calculate_trend(avg_order_value, prev_aov)
    )


@router.get("/funnel", response_model=FunnelData)
def get_funnel_data(
    customer_id: Optional[int] = Query(default=None),
    date_range: str = Query(default="LAST_30_DAYS"),
    db: Session = Depends(get_db)
):
    """
    Get conversion funnel data
    Visitors → Product Views → Add to Cart → Checkout → Purchase
    """
    # Calculate from existing data
    # For this MVP, we'll derive funnel from clicks, impressions, conversions
    days_map = {"LAST_7_DAYS": 7, "LAST_30_DAYS": 30, "LAST_90_DAYS": 90}
    days = days_map.get(date_range, 30)
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    query = db.query(
        func.coalesce(func.sum(CampaignKeyword.impressions), 0).label("impressions"),
        func.coalesce(func.sum(CampaignKeyword.clicks), 0).label("clicks"),
        func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("conversions")
    ).filter(CampaignKeyword.date >= cutoff_date)

    if customer_id:
        query = query.filter(CampaignKeyword.customer_id == customer_id)

    metrics = query.first()

    # Derive funnel stages
    visitors = int(metrics.impressions or 0)
    product_views = int(metrics.clicks or 0)  # Clicks = product page views
    add_to_cart = int(product_views * 0.35)  # Estimate: 35% add to cart
    checkout = int(add_to_cart * 0.68)  # Estimate: 68% proceed to checkout
    purchases = int(metrics.conversions or 0)

    stages = []
    values = [visitors, product_views, add_to_cart, checkout, purchases]
    stage_names = ["Visitors", "Product Views", "Add to Cart", "Checkout", "Purchase"]

    for i, (name, value) in enumerate(zip(stage_names, values)):
        if i == 0:
            stages.append({
                'stage': name,
                'value': value,
                'percentage': 100.0,
                'dropoff': 0.0
            })
        else:
            prev_value = values[i - 1]
            percentage = (value / prev_value * 100) if prev_value > 0 else 0
            dropoff = 100 - percentage

            stages.append({
                'stage': name,
                'value': value,
                'percentage': percentage,
                'dropoff': dropoff
            })

    # Generate insights
    insights_list = insights_service.generate_funnel_insights(stages)

    # Add insights to stages
    funnel_stages = []
    for i, stage in enumerate(stages):
        funnel_stages.append(FunnelStage(
            **stage,
            insight=insights_list[i] if i < len(insights_list) else None
        ))

    overall_cvr = (purchases / visitors * 100) if visitors > 0 else 0

    return FunnelData(
        stages=funnel_stages,
        overall_conversion_rate=overall_cvr
    )


@router.get("/channels", response_model=ChannelPerformance)
def get_channel_performance(
    customer_id: Optional[int] = Query(default=None),
    date_range: str = Query(default="LAST_30_DAYS"),
    db: Session = Depends(get_db)
):
    """
    Get channel performance with ROAS
    Channels: Google, Meta, Email, Organic, Referral
    """
    days_map = {"LAST_7_DAYS": 7, "LAST_30_DAYS": 30, "LAST_90_DAYS": 90}
    days = days_map.get(date_range, 30)
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Query campaigns grouped by channel_type
    query = db.query(
        Campaign.channel_type.label("channel"),
        func.coalesce(func.sum(CampaignKeyword.cost_micros), 0).label("spend_micros"),
        func.coalesce(func.sum(CampaignKeyword.conversion_value), 0).label("revenue"),
        func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("orders"),
        func.coalesce(func.sum(CampaignKeyword.impressions), 0).label("impressions"),
        func.coalesce(func.sum(CampaignKeyword.clicks), 0).label("clicks")
    ).join(
        CampaignKeyword,
        Campaign.campaign_id == CampaignKeyword.campaign_id
    ).filter(CampaignKeyword.date >= cutoff_date)

    if customer_id:
        query = query.filter(Campaign.customer_id == customer_id)

    query = query.group_by(Campaign.channel_type)
    results = query.all()

    channels = []
    for row in results:
        spend = float(row.spend_micros or 0) / 1_000_000
        revenue = float(row.revenue or 0)
        roas = (revenue / spend) if spend > 0 else 0
        clicks = int(row.clicks or 0)
        impressions = int(row.impressions or 0)
        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        cvr = (row.orders / clicks * 100) if clicks > 0 else 0

        # Map channel types to friendly names
        channel_map = {
            'SEARCH': 'Google Search',
            'DISPLAY': 'Google Display',
            'SHOPPING': 'Google Shopping',
            'VIDEO': 'YouTube',
            'MULTI_CHANNEL': 'Multi-Channel',
            'PERFORMANCE_MAX': 'Performance Max'
        }

        channels.append(ChannelMetrics(
            channel=channel_map.get(row.channel, row.channel or 'Unknown'),
            spend=spend,
            revenue=revenue,
            roas=roas,
            orders=int(row.orders or 0),
            impressions=impressions,
            clicks=clicks,
            ctr=ctr,
            cvr=cvr
        ))

    # Generate insight
    channel_dicts = [
        {
            'channel': c.channel,
            'spend': c.spend,
            'revenue': c.revenue,
            'roas': c.roas
        }
        for c in channels
    ]
    insight = insights_service.generate_channel_insight(channel_dicts)

    return ChannelPerformance(
        channels=channels,
        insight=insight
    )


@router.get("/products", response_model=ProductPerformance)
def get_product_performance(
    customer_id: Optional[int] = Query(default=None),
    date_range: str = Query(default="LAST_30_DAYS"),
    db: Session = Depends(get_db)
):
    """
    Get product performance metrics
    TODO: Replace with real product data when available
    """
    # Mock product data for now
    # In production, this would come from product feed or merchant center integration
    products = [
        ProductMetrics(
            product_id="PROD001",
            product_name="Premium Wireless Headphones",
            revenue=45000.00,
            orders=150,
            conversion_rate=8.5,
            refund_rate=2.1,
            stock_status="IN_STOCK",
            rank=1
        ),
        ProductMetrics(
            product_id="PROD002",
            product_name="Smart Fitness Watch",
            revenue=38000.00,
            orders=190,
            conversion_rate=7.2,
            refund_rate=3.5,
            stock_status="IN_STOCK",
            rank=2
        ),
        ProductMetrics(
            product_id="PROD003",
            product_name="Portable Bluetooth Speaker",
            revenue=29000.00,
            orders=220,
            conversion_rate=6.8,
            refund_rate=1.8,
            stock_status="LOW_STOCK",
            rank=3
        ),
        ProductMetrics(
            product_id="PROD004",
            product_name="USB-C Fast Charger",
            revenue=12000.00,
            orders=300,
            conversion_rate=5.1,
            refund_rate=12.5,
            stock_status="IN_STOCK",
            rank=4
        ),
        ProductMetrics(
            product_id="PROD005",
            product_name="Phone Screen Protector",
            revenue=8000.00,
            orders=160,
            conversion_rate=4.2,
            refund_rate=8.2,
            stock_status="OUT_OF_STOCK",
            rank=5
        )
    ]

    top_products = [p.product_name for p in products[:3]]
    bottom_products = [p.product_name for p in products[-3:]]

    # Generate insight
    product_dicts = [
        {
            'product_name': p.product_name,
            'revenue': p.revenue,
            'refund_rate': p.refund_rate
        }
        for p in products
    ]
    insight = insights_service.generate_product_insight(
        product_dicts,
        top_products,
        bottom_products
    )

    return ProductPerformance(
        products=products,
        top_products=top_products,
        bottom_products=bottom_products,
        insight=insight
    )


@router.get("/segments", response_model=CustomerSegmentation)
def get_customer_segmentation(
    customer_id: Optional[int] = Query(default=None),
    date_range: str = Query(default="LAST_30_DAYS"),
    db: Session = Depends(get_db)
):
    """
    Get customer segmentation: New vs Returning
    TODO: Replace with real user tracking data when available
    """
    days_map = {"LAST_7_DAYS": 7, "LAST_30_DAYS": 30, "LAST_90_DAYS": 90}
    days = days_map.get(date_range, 30)
    cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")

    # Get total metrics
    query = db.query(
        func.coalesce(func.sum(CampaignKeyword.conversion_value), 0).label("total_revenue"),
        func.coalesce(func.sum(CampaignKeyword.conversions), 0).label("total_orders")
    ).filter(CampaignKeyword.date >= cutoff_date)

    if customer_id:
        query = query.filter(CampaignKeyword.customer_id == customer_id)

    totals = query.first()
    total_revenue = float(totals.total_revenue or 0)
    total_orders = int(totals.total_orders or 0)

    # Mock segmentation (22% returning, 78% new)
    # In production, this would come from user tracking
    returning_pct = 22.0
    new_pct = 78.0

    returning_revenue_pct = 61.0  # Returning users drive 61% of revenue
    new_revenue_pct = 39.0

    returning_count = int(total_orders * returning_pct / 100)
    new_count = int(total_orders * new_pct / 100)

    returning_revenue = total_revenue * returning_revenue_pct / 100
    new_revenue = total_revenue * new_revenue_pct / 100

    segments = [
        CustomerSegment(
            segment="RETURNING",
            count=returning_count,
            percentage=returning_pct,
            revenue=returning_revenue,
            revenue_percentage=returning_revenue_pct,
            avg_order_value=returning_revenue / returning_count if returning_count > 0 else 0,
            conversion_rate=8.5  # Mock
        ),
        CustomerSegment(
            segment="NEW",
            count=new_count,
            percentage=new_pct,
            revenue=new_revenue,
            revenue_percentage=new_revenue_pct,
            avg_order_value=new_revenue / new_count if new_count > 0 else 0,
            conversion_rate=6.2  # Mock
        )
    ]

    # Generate insight
    segment_dicts = [
        {
            'segment': s.segment,
            'percentage': s.percentage,
            'revenue_percentage': s.revenue_percentage,
            'avg_order_value': s.avg_order_value
        }
        for s in segments
    ]
    insight = insights_service.generate_segment_insight(segment_dicts)

    return CustomerSegmentation(
        segments=segments,
        insight=insight
    )


@router.get("/forecast", response_model=RevenueForecast)
def get_revenue_forecast(
    customer_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Get 7-day revenue forecast
    Simple linear extrapolation from last 30 days
    """
    # Get last 30 days of data
    cutoff_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

    query = db.query(
        CampaignKeyword.date,
        func.sum(CampaignKeyword.conversion_value).label("revenue")
    ).filter(CampaignKeyword.date >= cutoff_date)

    if customer_id:
        query = query.filter(CampaignKeyword.customer_id == customer_id)

    query = query.group_by(CampaignKeyword.date).order_by(CampaignKeyword.date)
    historical = query.all()

    # Calculate average daily revenue
    if not historical:
        avg_revenue = 0
    else:
        total_revenue = sum(float(h.revenue or 0) for h in historical)
        avg_revenue = total_revenue / len(historical)

    # Simple forecast: last 7 days average ± 15%
    recent_7_days = historical[-7:] if len(historical) >= 7 else historical
    if recent_7_days:
        recent_avg = sum(float(h.revenue or 0) for h in recent_7_days) / len(recent_7_days)
    else:
        recent_avg = avg_revenue

    # Determine trend
    if len(historical) >= 14:
        first_half_avg = sum(float(h.revenue or 0) for h in historical[:14]) / 14
        second_half_avg = sum(float(h.revenue or 0) for h in historical[-14:]) / 14
        trend_pct = (second_half_avg - first_half_avg) / first_half_avg if first_half_avg > 0 else 0

        if trend_pct > 0.05:
            trend = "INCREASING"
        elif trend_pct < -0.05:
            trend = "DECREASING"
        else:
            trend = "STABLE"
    else:
        trend = "STABLE"
        trend_pct = 0

    # Generate 7-day forecast
    forecast_points = []
    base_date = datetime.now()

    for i in range(1, 8):
        forecast_date = (base_date + timedelta(days=i)).strftime("%Y-%m-%d")
        # Apply trend
        predicted = recent_avg * (1 + trend_pct * (i / 7))
        confidence_range = predicted * 0.15  # ±15% confidence interval

        forecast_points.append(ForecastDataPoint(
            date=forecast_date,
            predicted_revenue=predicted,
            confidence_lower=max(0, predicted - confidence_range),
            confidence_upper=predicted + confidence_range
        ))

    return RevenueForecast(
        forecast=forecast_points,
        trend=trend
    )


@router.get("/anomalies", response_model=AnomalyDetection)
def get_anomaly_detection(
    customer_id: Optional[int] = Query(default=None),
    db: Session = Depends(get_db)
):
    """
    Detect anomalies in e-commerce metrics
    """
    # Mock current vs historical metrics
    # In production, calculate from real data
    current_metrics = {
        'mobile_cvr': 4.2,  # Current mobile conversion rate
        'desktop_cvr': 7.5,  # Current desktop conversion rate
        'checkout_abandonment': 32.0,  # Current checkout abandonment %
        'avg_session_duration': 145.0,  # Current avg session (seconds)
        'bounce_rate': 52.0  # Current bounce rate %
    }

    historical_avg = {
        'mobile_cvr': 5.5,  # Historical average
        'desktop_cvr': 7.2,
        'checkout_abandonment': 28.0,
        'avg_session_duration': 180.0,
        'bounce_rate': 48.0
    }

    # Detect anomalies
    anomalies_list = insights_service.detect_anomalies(
        current_metrics,
        historical_avg,
        threshold=0.15
    )

    anomaly_objects = [AnomalyAlert(**anomaly) for anomaly in anomalies_list]

    return AnomalyDetection(
        anomalies=anomaly_objects,
        total_anomalies=len(anomaly_objects)
    )
