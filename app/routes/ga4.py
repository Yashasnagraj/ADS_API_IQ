"""
Google Analytics 4 (GA4) API Routes

Endpoints:
- Integration status
- Session metrics (behavior by campaign, source)
- Event tracking
- Multi-touch attribution (conversion paths)
- Audience insights
- Campaign enrichment (combine GA4 + Google Ads data)
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_
from typing import List, Optional, Tuple
import json
from datetime import datetime, timedelta

from app.db.database import get_db
from app.db import models
from app.schemas import ga4 as schemas


router = APIRouter(prefix="/ga4", tags=["ga4"])


# ==============================================================================
# DATE RANGE HELPER
# ==============================================================================

def convert_date_range(date_range: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    Convert date_range enum to start_date and end_date

    Supported ranges:
    - LAST_7_DAYS
    - LAST_14_DAYS
    - LAST_30_DAYS
    - LAST_90_DAYS
    - THIS_MONTH
    - LAST_MONTH
    - THIS_YEAR
    - ALL_TIME (returns None, None)
    """
    if not date_range or date_range == 'ALL_TIME':
        return None, None

    today = datetime.now().date()

    if date_range == 'LAST_7_DAYS':
        start = today - timedelta(days=7)
        return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    elif date_range == 'LAST_14_DAYS':
        start = today - timedelta(days=14)
        return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    elif date_range == 'LAST_30_DAYS':
        start = today - timedelta(days=30)
        return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    elif date_range == 'LAST_90_DAYS':
        start = today - timedelta(days=90)
        return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    elif date_range == 'THIS_MONTH':
        start = today.replace(day=1)
        return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    elif date_range == 'LAST_MONTH':
        first_this_month = today.replace(day=1)
        last_day_last_month = first_this_month - timedelta(days=1)
        first_last_month = last_day_last_month.replace(day=1)
        return first_last_month.strftime('%Y-%m-%d'), last_day_last_month.strftime('%Y-%m-%d')
    elif date_range == 'THIS_YEAR':
        start = today.replace(month=1, day=1)
        return start.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')
    else:
        # Unknown range, return None
        return None, None


# ==============================================================================
# INTEGRATION STATUS
# ==============================================================================

@router.get("/integration/status", response_model=schemas.GA4IntegrationStatusResponse)
def get_integration_status(
    customer_id: int = Query(..., description="Customer ID"),
    db: Session = Depends(get_db)
):
    """
    Check GA4 integration status for a customer

    Returns:
    - Connection status
    - Number of properties
    - Total sessions, events, conversions
    - Attribution coverage %
    """

    # Check if customer has GA4 properties
    properties = db.query(models.GA4Property).filter(
        models.GA4Property.customer_id == customer_id,
        models.GA4Property.is_active == True
    ).all()

    if not properties:
        return schemas.GA4IntegrationStatusResponse(
            customer_id=customer_id,
            is_connected=False,
            properties_count=0,
            total_sessions=0,
            total_events=0,
            total_conversions=0,
            attribution_coverage=0.0
        )

    # Get metrics
    total_sessions = db.query(func.sum(models.GA4Session.sessions)).filter(
        models.GA4Session.customer_id == customer_id
    ).scalar() or 0

    total_events = db.query(func.sum(models.GA4Event.event_count)).filter(
        models.GA4Event.customer_id == customer_id
    ).scalar() or 0

    total_conversions = db.query(func.sum(models.GA4Session.conversions)).filter(
        models.GA4Session.customer_id == customer_id
    ).scalar() or 0

    # Calculate attribution coverage
    sessions_with_campaign = db.query(func.sum(models.GA4Session.sessions)).filter(
        models.GA4Session.customer_id == customer_id,
        models.GA4Session.utm_campaign.isnot(None)
    ).scalar() or 0

    attribution_coverage = round((sessions_with_campaign / total_sessions) * 100, 2) if total_sessions > 0 else 0

    # Get last sync time
    last_sync = db.query(func.max(models.GA4Property.last_sync_at)).filter(
        models.GA4Property.customer_id == customer_id
    ).scalar()

    return schemas.GA4IntegrationStatusResponse(
        customer_id=customer_id,
        is_connected=True,
        properties_count=len(properties),
        total_sessions=int(total_sessions),
        total_events=int(total_events),
        total_conversions=int(total_conversions),
        attribution_coverage=attribution_coverage,
        last_sync_at=last_sync
    )


# ==============================================================================
# PROPERTIES
# ==============================================================================

@router.get("/properties", response_model=List[schemas.GA4PropertyResponse])
def get_properties(
    customer_id: int = Query(..., description="Customer ID"),
    db: Session = Depends(get_db)
):
    """Get all GA4 properties for a customer"""

    properties = db.query(models.GA4Property).filter(
        models.GA4Property.customer_id == customer_id
    ).all()

    return properties


# ==============================================================================
# SESSIONS
# ==============================================================================

@router.get("/sessions", response_model=schemas.GA4SessionsResponse)
def get_sessions(
    customer_id: int = Query(..., description="Customer ID"),
    date_range: Optional[str] = Query(None, description="Date range (LAST_7_DAYS, LAST_30_DAYS, etc.)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) - overrides date_range"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD) - overrides date_range"),
    source: Optional[str] = Query(None, description="Filter by source"),
    campaign: Optional[str] = Query(None, description="Filter by campaign"),
    device: Optional[str] = Query(None, description="Filter by device category"),
    limit: int = Query(100, description="Max results"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Get session metrics filtered by date, source, campaign, device

    Use this to see user behavior metrics for your ad campaigns
    """

    # Convert date_range to start_date/end_date if provided
    if date_range and not (start_date and end_date):
        start_date, end_date = convert_date_range(date_range)

    # Build query
    query = db.query(models.GA4Session).filter(
        models.GA4Session.customer_id == customer_id
    )

    # Apply filters
    if start_date:
        query = query.filter(models.GA4Session.date >= start_date)
    if end_date:
        query = query.filter(models.GA4Session.date <= end_date)
    if source:
        query = query.filter(models.GA4Session.source == source)
    if campaign:
        query = query.filter(models.GA4Session.utm_campaign == campaign)
    if device:
        query = query.filter(models.GA4Session.device_category == device)

    # Get total count
    total_count = query.count()

    # Get paginated results
    sessions = query.order_by(models.GA4Session.date.desc()).offset(offset).limit(limit).all()

    return schemas.GA4SessionsResponse(
        sessions=sessions,
        total_count=total_count
    )


@router.get("/sessions/by-source", response_model=List[schemas.GA4BehaviorBySourceResponse])
def get_behavior_by_source(
    customer_id: int = Query(..., description="Customer ID"),
    date_range: Optional[str] = Query(None, description="Date range (LAST_7_DAYS, LAST_30_DAYS, etc.)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) - overrides date_range"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD) - overrides date_range"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated behavior metrics grouped by source

    Shows which traffic sources bring the most engaged users
    """

    # Convert date_range to start_date/end_date if provided
    if date_range and not (start_date and end_date):
        start_date, end_date = convert_date_range(date_range)

    query = db.query(
        models.GA4Session.source,
        func.sum(models.GA4Session.sessions).label('total_sessions'),
        func.sum(models.GA4Session.users).label('total_users'),
        func.avg(models.GA4Session.bounce_rate).label('avg_bounce_rate'),
        func.avg(models.GA4Session.avg_session_duration).label('avg_duration'),
        func.avg(models.GA4Session.pages_per_session).label('avg_pages'),
        func.sum(models.GA4Session.conversions).label('total_conversions')
    ).filter(
        models.GA4Session.customer_id == customer_id
    )

    # Apply date filters
    if start_date:
        query = query.filter(models.GA4Session.date >= start_date)
    if end_date:
        query = query.filter(models.GA4Session.date <= end_date)

    # Group and order
    results = query.group_by(models.GA4Session.source).order_by(
        func.sum(models.GA4Session.sessions).desc()
    ).all()

    # Format response
    response = []
    for row in results:
        conversion_rate = round((row.total_conversions / row.total_sessions) * 100, 2) if row.total_sessions > 0 else 0
        response.append(schemas.GA4BehaviorBySourceResponse(
            source=row.source,
            sessions=int(row.total_sessions),
            users=int(row.total_users),
            bounce_rate=round(row.avg_bounce_rate, 2),
            avg_session_duration=round(row.avg_duration, 2),
            pages_per_session=round(row.avg_pages, 2),
            conversions=int(row.total_conversions),
            conversion_rate=conversion_rate
        ))

    return response


@router.get("/sessions/by-campaign", response_model=List[schemas.GA4BehaviorByCampaignResponse])
def get_behavior_by_campaign(
    customer_id: int = Query(..., description="Customer ID"),
    date_range: Optional[str] = Query(None, description="Date range (LAST_7_DAYS, LAST_30_DAYS, etc.)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) - overrides date_range"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD) - overrides date_range"),
    db: Session = Depends(get_db)
):
    """
    Get aggregated behavior metrics grouped by campaign

    Shows which campaigns bring the most engaged users
    """

    # Convert date_range to start_date/end_date if provided
    if date_range and not (start_date and end_date):
        start_date, end_date = convert_date_range(date_range)

    query = db.query(
        models.GA4Session.utm_campaign,
        models.GA4Session.source,
        func.sum(models.GA4Session.sessions).label('total_sessions'),
        func.sum(models.GA4Session.users).label('total_users'),
        func.avg(models.GA4Session.bounce_rate).label('avg_bounce_rate'),
        func.avg(models.GA4Session.avg_session_duration).label('avg_duration'),
        func.avg(models.GA4Session.pages_per_session).label('avg_pages'),
        func.sum(models.GA4Session.conversions).label('total_conversions')
    ).filter(
        models.GA4Session.customer_id == customer_id,
        models.GA4Session.utm_campaign.isnot(None)
    )

    # Apply date filters
    if start_date:
        query = query.filter(models.GA4Session.date >= start_date)
    if end_date:
        query = query.filter(models.GA4Session.date <= end_date)

    # Group and order
    results = query.group_by(
        models.GA4Session.utm_campaign,
        models.GA4Session.source
    ).order_by(
        func.sum(models.GA4Session.sessions).desc()
    ).all()

    # Format response
    response = []
    for row in results:
        conversion_rate = round((row.total_conversions / row.total_sessions) * 100, 2) if row.total_sessions > 0 else 0
        response.append(schemas.GA4BehaviorByCampaignResponse(
            campaign=row.utm_campaign,
            source=row.source,
            sessions=int(row.total_sessions),
            users=int(row.total_users),
            bounce_rate=round(row.avg_bounce_rate, 2),
            avg_session_duration=round(row.avg_duration, 2),
            pages_per_session=round(row.avg_pages, 2),
            conversions=int(row.total_conversions),
            conversion_rate=conversion_rate
        ))

    return response


# ==============================================================================
# EVENTS
# ==============================================================================

@router.get("/events", response_model=schemas.GA4EventsResponse)
def get_events(
    customer_id: int = Query(..., description="Customer ID"),
    event_name: Optional[str] = Query(None, description="Filter by event name"),
    date_range: Optional[str] = Query(None, description="Date range (LAST_7_DAYS, LAST_30_DAYS, etc.)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) - overrides date_range"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD) - overrides date_range"),
    limit: int = Query(100, description="Max results"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Get event tracking data

    Common events: page_view, purchase, add_to_cart, begin_checkout
    """

    # Convert date_range to start_date/end_date if provided
    if date_range and not (start_date and end_date):
        start_date, end_date = convert_date_range(date_range)

    query = db.query(models.GA4Event).filter(
        models.GA4Event.customer_id == customer_id
    )

    # Apply filters
    if event_name:
        query = query.filter(models.GA4Event.event_name == event_name)
    if start_date:
        query = query.filter(models.GA4Event.date >= start_date)
    if end_date:
        query = query.filter(models.GA4Event.date <= end_date)

    # Get total count
    total_count = query.count()

    # Get paginated results
    events = query.order_by(models.GA4Event.date.desc()).offset(offset).limit(limit).all()

    return schemas.GA4EventsResponse(
        events=events,
        total_count=total_count
    )


@router.get("/events/top", response_model=List[schemas.GA4TopEventsResponse])
def get_top_events(
    customer_id: int = Query(..., description="Customer ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(10, description="Top N events"),
    db: Session = Depends(get_db)
):
    """Get top events by count"""

    query = db.query(
        models.GA4Event.event_name,
        func.sum(models.GA4Event.event_count).label('total_count'),
        func.sum(models.GA4Event.event_value).label('total_value'),
        func.sum(models.GA4Event.users).label('unique_users')
    ).filter(
        models.GA4Event.customer_id == customer_id
    )

    # Apply date filters
    if start_date:
        query = query.filter(models.GA4Event.date >= start_date)
    if end_date:
        query = query.filter(models.GA4Event.date <= end_date)

    # Group and order
    results = query.group_by(models.GA4Event.event_name).order_by(
        func.sum(models.GA4Event.event_count).desc()
    ).limit(limit).all()

    # Format response
    response = []
    for row in results:
        response.append(schemas.GA4TopEventsResponse(
            event_name=row.event_name,
            total_count=int(row.total_count),
            total_value=float(row.total_value),
            unique_users=int(row.unique_users)
        ))

    return response


# ==============================================================================
# CONVERSION PATHS (MULTI-TOUCH ATTRIBUTION)
# ==============================================================================

@router.get("/conversion-paths", response_model=schemas.GA4ConversionPathsResponse)
def get_conversion_paths(
    customer_id: int = Query(..., description="Customer ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    min_touchpoints: Optional[int] = Query(None, description="Min touchpoints in path"),
    limit: int = Query(100, description="Max results"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Get conversion paths showing customer journey from first touch to conversion

    This is CRITICAL for understanding multi-touch attribution
    """

    query = db.query(models.GA4ConversionPath).filter(
        models.GA4ConversionPath.customer_id == customer_id
    )

    # Apply filters
    if start_date:
        query = query.filter(models.GA4ConversionPath.conversion_date >= start_date)
    if end_date:
        query = query.filter(models.GA4ConversionPath.conversion_date <= end_date)
    if min_touchpoints:
        query = query.filter(models.GA4ConversionPath.touchpoints_count >= min_touchpoints)

    # Get total count
    total_count = query.count()

    # Get paginated results
    paths = query.order_by(models.GA4ConversionPath.conversion_date.desc()).offset(offset).limit(limit).all()

    # Format response
    formatted_paths = []
    for path in paths:
        touchpoints_data = json.loads(path.touchpoints_json) if path.touchpoints_json else []
        touchpoints = [schemas.GA4Touchpoint(**tp) for tp in touchpoints_data]

        formatted_paths.append(schemas.GA4ConversionPathResponse(
            conversion_event=path.conversion_event,
            conversion_date=path.conversion_date,
            conversion_value=path.conversion_value,
            touchpoints=touchpoints,
            touchpoints_count=path.touchpoints_count,
            days_to_conversion=path.days_to_conversion,
            first_touch_source=path.first_touch_source,
            first_touch_campaign=path.first_touch_campaign,
            last_touch_source=path.last_touch_source,
            last_touch_campaign=path.last_touch_campaign
        ))

    return schemas.GA4ConversionPathsResponse(
        paths=formatted_paths,
        total_count=total_count
    )


@router.get("/attribution", response_model=List[schemas.GA4AttributionModelResponse])
def get_attribution_models(
    customer_id: int = Query(..., description="Customer ID"),
    date_range: Optional[str] = Query(None, description="Date range (LAST_7_DAYS, LAST_30_DAYS, etc.)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) - overrides date_range"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD) - overrides date_range"),
    db: Session = Depends(get_db)
):
    """
    Apply different attribution models to conversion paths

    Models:
    - First-touch: 100% credit to first touchpoint
    - Last-touch: 100% credit to last touchpoint
    - Linear: Equal credit across all touchpoints
    - Time-decay: More credit to recent touchpoints
    """

    # Convert date_range to start_date/end_date if provided
    if date_range and not (start_date and end_date):
        start_date, end_date = convert_date_range(date_range)

    query = db.query(models.GA4ConversionPath).filter(
        models.GA4ConversionPath.customer_id == customer_id
    )

    # Apply date filters
    if start_date:
        query = query.filter(models.GA4ConversionPath.conversion_date >= start_date)
    if end_date:
        query = query.filter(models.GA4ConversionPath.conversion_date <= end_date)

    paths = query.all()

    # Calculate attribution for each source/campaign
    attribution = {}

    for path in paths:
        touchpoints = json.loads(path.touchpoints_json) if path.touchpoints_json else []
        num_touchpoints = len(touchpoints)

        if num_touchpoints == 0:
            continue

        for i, tp in enumerate(touchpoints):
            key = (tp.get('source', 'unknown'), tp.get('campaign', 'unknown'))

            if key not in attribution:
                attribution[key] = {
                    'source': tp.get('source', 'unknown'),
                    'campaign': tp.get('campaign', 'unknown'),
                    'first_touch': 0,
                    'last_touch': 0,
                    'linear': 0,
                    'time_decay': 0,
                    'value': 0
                }

            # First-touch attribution
            if i == 0:
                attribution[key]['first_touch'] += 1

            # Last-touch attribution
            if i == num_touchpoints - 1:
                attribution[key]['last_touch'] += 1

            # Linear attribution (equal credit)
            attribution[key]['linear'] += 1 / num_touchpoints

            # Time-decay attribution (exponential decay, more credit to recent)
            decay_factor = 0.5 ** (num_touchpoints - i - 1)
            attribution[key]['time_decay'] += decay_factor

            # Total value
            attribution[key]['value'] += path.conversion_value / num_touchpoints

    # Format response
    response = []
    for key, data in attribution.items():
        response.append(schemas.GA4AttributionModelResponse(
            source=data['source'],
            campaign=data['campaign'],
            first_touch_conversions=int(data['first_touch']),
            last_touch_conversions=int(data['last_touch']),
            linear_attribution_credit=round(data['linear'], 2),
            time_decay_credit=round(data['time_decay'], 2),
            total_conversion_value=round(data['value'], 2)
        ))

    # Sort by linear attribution credit
    response.sort(key=lambda x: x.linear_attribution_credit, reverse=True)

    return response


# ==============================================================================
# AUDIENCE INSIGHTS
# ==============================================================================

@router.get("/audience-insights", response_model=schemas.GA4AudienceInsightsResponse)
def get_audience_insights(
    customer_id: int = Query(..., description="Customer ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    segment_type: Optional[str] = Query(None, description="Filter by segment type"),
    limit: int = Query(100, description="Max results"),
    offset: int = Query(0, description="Offset for pagination"),
    db: Session = Depends(get_db)
):
    """
    Get audience demographics and technology insights

    Segment types: demographic, behavior, technology
    """

    query = db.query(models.GA4Audience).filter(
        models.GA4Audience.customer_id == customer_id
    )

    # Apply filters
    if start_date:
        query = query.filter(models.GA4Audience.date >= start_date)
    if end_date:
        query = query.filter(models.GA4Audience.date <= end_date)
    if segment_type:
        query = query.filter(models.GA4Audience.segment_type == segment_type)

    # Get total count
    total_count = query.count()

    # Get paginated results
    segments = query.offset(offset).limit(limit).all()

    return schemas.GA4AudienceInsightsResponse(
        segments=segments,
        total_count=total_count
    )


@router.get("/audience-insights/devices", response_model=List[schemas.GA4DeviceBreakdown])
def get_device_breakdown(
    customer_id: int = Query(..., description="Customer ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """Get aggregated metrics by device category"""

    query = db.query(
        models.GA4Audience.device_category,
        func.sum(models.GA4Audience.users).label('total_users'),
        func.sum(models.GA4Audience.sessions).label('total_sessions'),
        func.avg(models.GA4Audience.engagement_rate).label('avg_engagement'),
        func.avg(models.GA4Audience.conversion_rate).label('avg_conversion')
    ).filter(
        models.GA4Audience.customer_id == customer_id
    )

    # Apply date filters
    if start_date:
        query = query.filter(models.GA4Audience.date >= start_date)
    if end_date:
        query = query.filter(models.GA4Audience.date <= end_date)

    # Group and order
    results = query.group_by(models.GA4Audience.device_category).order_by(
        func.sum(models.GA4Audience.sessions).desc()
    ).all()

    # Calculate bounce rate (inverse of engagement)
    response = []
    for row in results:
        bounce_rate = round(100 - row.avg_engagement, 2)
        response.append(schemas.GA4DeviceBreakdown(
            device_category=row.device_category,
            users=int(row.total_users),
            sessions=int(row.total_sessions),
            bounce_rate=bounce_rate,
            conversion_rate=round(row.avg_conversion, 2)
        ))

    return response


@router.get("/audience-insights/countries", response_model=List[schemas.GA4CountryBreakdown])
def get_country_breakdown(
    customer_id: int = Query(..., description="Customer ID"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    limit: int = Query(10, description="Top N countries"),
    db: Session = Depends(get_db)
):
    """Get aggregated metrics by country"""

    query = db.query(
        models.GA4Audience.country,
        func.sum(models.GA4Audience.users).label('total_users'),
        func.sum(models.GA4Audience.sessions).label('total_sessions'),
        func.sum(models.GA4Audience.conversions).label('total_conversions'),
        func.sum(models.GA4Audience.revenue).label('total_revenue')
    ).filter(
        models.GA4Audience.customer_id == customer_id,
        models.GA4Audience.country.isnot(None)
    )

    # Apply date filters
    if start_date:
        query = query.filter(models.GA4Audience.date >= start_date)
    if end_date:
        query = query.filter(models.GA4Audience.date <= end_date)

    # Group and order
    results = query.group_by(models.GA4Audience.country).order_by(
        func.sum(models.GA4Audience.sessions).desc()
    ).limit(limit).all()

    # Format response
    response = []
    for row in results:
        response.append(schemas.GA4CountryBreakdown(
            country=row.country,
            users=int(row.total_users),
            sessions=int(row.total_sessions),
            conversions=int(row.total_conversions),
            revenue=round(row.total_revenue, 2)
        ))

    return response


# ==============================================================================
# CAMPAIGN ENRICHMENT (GA4 + GOOGLE ADS)
# ==============================================================================

@router.get("/campaign-enrichment", response_model=schemas.GA4CampaignEnrichmentResponse)
def enrich_campaigns_with_ga4(
    customer_id: int = Query(..., description="Customer ID"),
    date_range: Optional[str] = Query(None, description="Date range (LAST_7_DAYS, LAST_30_DAYS, etc.)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) - overrides date_range"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD) - overrides date_range"),
    db: Session = Depends(get_db)
):
    """
    Combine Google Ads campaign data with GA4 user behavior metrics

    This enriches your ad campaigns with:
    - Bounce rate
    - Session duration
    - Pages per session
    - Engagement rate

    Result: Better understanding of campaign quality, not just performance

    Date filtering:
    - Use date_range for preset ranges (LAST_30_DAYS, etc.)
    - Or use start_date/end_date for custom ranges
    """

    # Convert date_range to start_date/end_date if provided
    if date_range and not (start_date and end_date):
        start_date, end_date = convert_date_range(date_range)

    # Get Google Ads campaigns
    campaigns_query = db.query(models.Campaign).filter(
        models.Campaign.customer_id == customer_id
    )

    campaigns = campaigns_query.all()

    enriched_campaigns = []

    for campaign in campaigns:
        campaign_name = campaign.campaign_name.lower()

        # Find matching GA4 sessions
        ga4_query = db.query(
            func.sum(models.GA4Session.sessions).label('sessions'),
            func.sum(models.GA4Session.users).label('users'),
            func.avg(models.GA4Session.bounce_rate).label('bounce_rate'),
            func.avg(models.GA4Session.avg_session_duration).label('duration'),
            func.avg(models.GA4Session.pages_per_session).label('pages'),
            func.avg(models.GA4Session.engagement_rate).label('engagement'),
            func.sum(models.GA4Session.conversions).label('conversions')
        ).filter(
            models.GA4Session.customer_id == customer_id,
            func.lower(models.GA4Session.utm_campaign).contains(campaign_name)
        )

        # Apply date filters
        if start_date:
            ga4_query = ga4_query.filter(models.GA4Session.date >= start_date)
        if end_date:
            ga4_query = ga4_query.filter(models.GA4Session.date <= end_date)

        ga4_data = ga4_query.first()

        if ga4_data and ga4_data.sessions:
            # Calculate quality score (0-100)
            # Lower bounce rate = better, higher engagement = better
            quality_score = round(
                (100 - ga4_data.bounce_rate) * 0.4 +  # 40% weight on low bounce
                ga4_data.engagement * 0.3 +  # 30% weight on engagement
                min(ga4_data.pages / 5 * 100, 100) * 0.3,  # 30% weight on pages (capped at 5)
                2
            )

            # Generate recommendation
            if quality_score >= 70:
                recommendation = "High quality traffic - consider increasing budget"
            elif quality_score >= 50:
                recommendation = "Good quality traffic - monitor and optimize"
            else:
                recommendation = "Low quality traffic - review targeting and landing pages"

            enriched_campaigns.append(schemas.GA4CampaignEnrichment(
                campaign_name=campaign.campaign_name,
                utm_campaign=campaign_name,
                ga4_sessions=int(ga4_data.sessions or 0),
                ga4_users=int(ga4_data.users or 0),
                ga4_bounce_rate=round(ga4_data.bounce_rate or 0, 2),
                ga4_avg_session_duration=round(ga4_data.duration or 0, 2),
                ga4_pages_per_session=round(ga4_data.pages or 0, 2),
                ga4_engagement_rate=round(ga4_data.engagement or 0, 2),
                ga4_conversions=int(ga4_data.conversions or 0),
                quality_score=quality_score,
                recommendation=recommendation
            ))

    return schemas.GA4CampaignEnrichmentResponse(
        campaigns=enriched_campaigns,
        total_count=len(enriched_campaigns)
    )


# ==============================================================================
# USER BEHAVIOR BY CAMPAIGN
# ==============================================================================

# Keyword Enrichment Endpoint
@router.get("/keyword-enrichment", response_model=schemas.GA4KeywordEnrichmentResponse)
def enrich_keywords_with_ga4(
    customer_id: int = Query(..., description="Customer ID"),
    date_range: Optional[str] = Query(None, description="Date range (LAST_7_DAYS, LAST_30_DAYS, etc.)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) - overrides date_range"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD) - overrides date_range"),
    db: Session = Depends(get_db)
):
    """
    Combine Google Ads keyword data with GA4 search terms and behavior metrics

    This enriches your keywords with:
    - Search terms from GA4
    - Landing page behavior
    - Engagement metrics
    - Bounce rates for keyword traffic

    Result: Better understanding of keyword quality beyond just Google Ads metrics
    """

    # Convert date_range to start_date/end_date if provided
    if date_range and not (start_date and end_date):
        start_date, end_date = convert_date_range(date_range)

    # Get Google Ads keywords
    keywords_query = db.query(models.Keyword).filter(
        models.Keyword.customer_id == customer_id
    )

    keywords = keywords_query.all()

    enriched_keywords = []

    for keyword in keywords:
        keyword_text = keyword.keyword_text.lower()

        # Get Google Ads performance metrics from CampaignKeyword table
        ads_metrics = db.query(
            func.sum(models.CampaignKeyword.clicks).label('clicks'),
            func.sum(models.CampaignKeyword.impressions).label('impressions'),
            func.sum(models.CampaignKeyword.cost_micros).label('cost_micros'),
            func.avg(models.CampaignKeyword.ctr).label('ctr'),
            func.sum(models.CampaignKeyword.conversions).label('conversions')
        ).filter(
            models.CampaignKeyword.customer_id == customer_id,
            models.CampaignKeyword.keyword_id == keyword.keyword_id
        )

        # Apply date filters to Google Ads metrics
        if start_date:
            ads_metrics = ads_metrics.filter(models.CampaignKeyword.date >= start_date)
        if end_date:
            ads_metrics = ads_metrics.filter(models.CampaignKeyword.date <= end_date)

        ads_data = ads_metrics.first()

        # Find matching GA4 sessions by searching UTM terms or page titles
        ga4_query = db.query(
            func.sum(models.GA4Session.sessions).label('sessions'),
            func.sum(models.GA4Session.users).label('users'),
            func.avg(models.GA4Session.bounce_rate).label('bounce_rate'),
            func.avg(models.GA4Session.avg_session_duration).label('duration'),
            func.avg(models.GA4Session.pages_per_session).label('pages'),
            func.avg(models.GA4Session.engagement_rate).label('engagement'),
            func.sum(models.GA4Session.conversions).label('conversions')
        ).filter(
            models.GA4Session.customer_id == customer_id,
            or_(
                func.lower(models.GA4Session.utm_term).contains(keyword_text),
                func.lower(models.GA4Session.utm_campaign).contains(keyword_text)
            )
        )

        # Apply date filters
        if start_date:
            ga4_query = ga4_query.filter(models.GA4Session.date >= start_date)
        if end_date:
            ga4_query = ga4_query.filter(models.GA4Session.date <= end_date)

        ga4_data = ga4_query.first()

        if ga4_data and ga4_data.sessions:
            # Calculate quality score (0-100)
            quality_score = round(
                (100 - ga4_data.bounce_rate) * 0.4 +  # 40% weight on low bounce
                ga4_data.engagement * 0.3 +  # 30% weight on engagement
                min(ga4_data.pages / 5 * 100, 100) * 0.3,  # 30% weight on pages
                2
            )

            # Generate recommendation
            if quality_score >= 70:
                recommendation = "High quality keyword - consider increasing bids"
            elif quality_score >= 50:
                recommendation = "Good quality - monitor performance"
            else:
                recommendation = "Low engagement - review landing page or pause keyword"

            enriched_keywords.append(schemas.GA4KeywordEnrichment(
                keyword_text=keyword.keyword_text,
                keyword_id=keyword.keyword_id,
                ad_clicks=int(ads_data.clicks or 0) if ads_data else 0,
                ad_impressions=int(ads_data.impressions or 0) if ads_data else 0,
                ad_cost=round((ads_data.cost_micros or 0) / 1_000_000, 2) if ads_data else 0.0,
                ad_ctr=round(ads_data.ctr or 0, 2) if ads_data else 0.0,
                ad_conversions=int(ads_data.conversions or 0) if ads_data else 0,
                ga4_sessions=int(ga4_data.sessions or 0),
                ga4_users=int(ga4_data.users or 0),
                ga4_bounce_rate=round(ga4_data.bounce_rate or 0, 2),
                ga4_avg_session_duration=round(ga4_data.duration or 0, 2),
                ga4_pages_per_session=round(ga4_data.pages or 0, 2),
                ga4_engagement_rate=round(ga4_data.engagement or 0, 2),
                ga4_conversions=int(ga4_data.conversions or 0),
                quality_score=quality_score,
                recommendation=recommendation
            ))

    return schemas.GA4KeywordEnrichmentResponse(
        keywords=enriched_keywords,
        total_count=len(enriched_keywords)
    )


@router.get("/adgroup-enrichment", response_model=schemas.GA4AdGroupEnrichmentResponse)
def enrich_adgroups_with_ga4(
    customer_id: int = Query(..., description="Customer ID"),
    date_range: Optional[str] = Query(None, description="Date range (LAST_7_DAYS, LAST_30_DAYS, etc.)"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD) - overrides date_range"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD) - overrides date_range"),
    db: Session = Depends(get_db)
):
    """
    Combine Google Ads ad group data with GA4 user behavior metrics

    This enriches your ad groups with:
    - GA4 user behavior (bounce rate, engagement, session duration)
    - Traffic quality scores
    - Landing page performance
    - Conversion behavior

    Result: Better understanding of ad group quality beyond just Google Ads metrics
    """

    # Convert date_range to start_date/end_date if provided
    if date_range and not (start_date and end_date):
        start_date, end_date = convert_date_range(date_range)

    # Get Google Ads ad groups with campaign info
    ad_groups_query = db.query(
        models.AdGroup,
        models.Campaign.campaign_name
    ).join(
        models.Campaign,
        models.AdGroup.campaign_id == models.Campaign.campaign_id
    ).filter(
        models.AdGroup.customer_id == customer_id
    )

    ad_groups = ad_groups_query.all()

    enriched_ad_groups = []

    for ad_group, campaign_name in ad_groups:
        ad_group_name = ad_group.ad_group_name.lower()
        campaign_name_lower = campaign_name.lower()

        # Get keyword IDs for this ad group
        keyword_ids_subquery = db.query(models.Keyword.keyword_id).filter(
            models.Keyword.ad_group_id == ad_group.ad_group_id
        ).subquery()

        # Get Google Ads performance metrics from keywords within this ad group
        ads_metrics = db.query(
            func.sum(models.CampaignKeyword.clicks).label('clicks'),
            func.sum(models.CampaignKeyword.impressions).label('impressions'),
            func.sum(models.CampaignKeyword.cost_micros).label('cost_micros'),
            func.avg(models.CampaignKeyword.ctr).label('ctr'),
            func.sum(models.CampaignKeyword.conversions).label('conversions')
        ).filter(
            models.CampaignKeyword.customer_id == customer_id,
            models.CampaignKeyword.keyword_id.in_(keyword_ids_subquery)
        )

        # Apply date filters to Google Ads metrics
        if start_date:
            ads_metrics = ads_metrics.filter(models.CampaignKeyword.date >= start_date)
        if end_date:
            ads_metrics = ads_metrics.filter(models.CampaignKeyword.date <= end_date)

        ads_data = ads_metrics.first()

        # Find matching GA4 sessions by searching UTM campaign or content (ad group name)
        ga4_query = db.query(
            func.sum(models.GA4Session.sessions).label('sessions'),
            func.sum(models.GA4Session.users).label('users'),
            func.avg(models.GA4Session.bounce_rate).label('bounce_rate'),
            func.avg(models.GA4Session.avg_session_duration).label('duration'),
            func.avg(models.GA4Session.pages_per_session).label('pages'),
            func.avg(models.GA4Session.engagement_rate).label('engagement'),
            func.sum(models.GA4Session.conversions).label('conversions')
        ).filter(
            models.GA4Session.customer_id == customer_id,
            or_(
                func.lower(models.GA4Session.utm_content).contains(ad_group_name),
                func.lower(models.GA4Session.utm_campaign).contains(ad_group_name),
                func.lower(models.GA4Session.utm_campaign).contains(campaign_name_lower)
            )
        )

        # Apply date filters
        if start_date:
            ga4_query = ga4_query.filter(models.GA4Session.date >= start_date)
        if end_date:
            ga4_query = ga4_query.filter(models.GA4Session.date <= end_date)

        ga4_data = ga4_query.first()

        if ga4_data and ga4_data.sessions:
            # Calculate quality score (0-100)
            quality_score = round(
                (100 - ga4_data.bounce_rate) * 0.4 +  # 40% weight on low bounce
                ga4_data.engagement * 0.3 +  # 30% weight on engagement
                min(ga4_data.pages / 5 * 100, 100) * 0.3,  # 30% weight on pages
                2
            )

            # Generate recommendation
            if quality_score >= 70:
                recommendation = "High quality ad group - consider increasing bids"
            elif quality_score >= 50:
                recommendation = "Good quality - monitor performance"
            else:
                recommendation = "Low engagement - review targeting or pause ad group"

            enriched_ad_groups.append(schemas.GA4AdGroupEnrichment(
                ad_group_name=ad_group.ad_group_name,
                ad_group_id=ad_group.ad_group_id,
                campaign_name=campaign_name,
                ad_clicks=int(ads_data.clicks or 0) if ads_data else 0,
                ad_impressions=int(ads_data.impressions or 0) if ads_data else 0,
                ad_cost=round((ads_data.cost_micros or 0) / 1_000_000, 2) if ads_data else 0.0,
                ad_ctr=round(ads_data.ctr or 0, 2) if ads_data else 0.0,
                ad_conversions=int(ads_data.conversions or 0) if ads_data else 0,
                ga4_sessions=int(ga4_data.sessions or 0),
                ga4_users=int(ga4_data.users or 0),
                ga4_bounce_rate=round(ga4_data.bounce_rate or 0, 2),
                ga4_avg_session_duration=round(ga4_data.duration or 0, 2),
                ga4_pages_per_session=round(ga4_data.pages or 0, 2),
                ga4_engagement_rate=round(ga4_data.engagement or 0, 2),
                ga4_conversions=int(ga4_data.conversions or 0),
                quality_score=quality_score,
                recommendation=recommendation
            ))

    return schemas.GA4AdGroupEnrichmentResponse(
        ad_groups=enriched_ad_groups,
        total_count=len(enriched_ad_groups)
    )


@router.get("/user-behavior", response_model=schemas.GA4UserBehaviorByCampaignResponse)
def get_user_behavior_by_campaign(
    customer_id: int = Query(..., description="Customer ID"),
    campaign_id: Optional[int] = Query(None, description="Google Ads Campaign ID"),
    utm_campaign: Optional[str] = Query(None, description="UTM campaign name"),
    start_date: Optional[str] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db)
):
    """
    Get detailed user behavior for a specific campaign

    Provides deep insights into how users from this campaign behave on your site
    """

    if not campaign_id and not utm_campaign:
        raise HTTPException(status_code=400, detail="Either campaign_id or utm_campaign is required")

    # Get campaign name
    campaign_name = utm_campaign
    if campaign_id:
        campaign = db.query(models.Campaign).filter(
            models.Campaign.campaign_id == campaign_id,
            models.Campaign.customer_id == customer_id
        ).first()
        if campaign:
            campaign_name = campaign.campaign_name.lower()

    if not campaign_name:
        raise HTTPException(status_code=404, detail="Campaign not found")

    # Query GA4 sessions
    query = db.query(models.GA4Session).filter(
        models.GA4Session.customer_id == customer_id,
        func.lower(models.GA4Session.utm_campaign).contains(campaign_name)
    )

    # Apply date filters
    if start_date:
        query = query.filter(models.GA4Session.date >= start_date)
    if end_date:
        query = query.filter(models.GA4Session.date <= end_date)

    sessions = query.all()

    if not sessions:
        raise HTTPException(status_code=404, detail="No GA4 data found for this campaign")

    # Aggregate metrics
    total_sessions = sum(s.sessions for s in sessions)
    total_users = sum(s.users for s in sessions)
    total_new_users = sum(s.new_users for s in sessions)
    total_conversions = sum(s.conversions for s in sessions)
    total_conversion_value = sum(s.conversion_value for s in sessions)

    avg_bounce_rate = sum(s.bounce_rate * s.sessions for s in sessions) / total_sessions if total_sessions > 0 else 0
    avg_engagement = sum(s.engagement_rate * s.sessions for s in sessions) / total_sessions if total_sessions > 0 else 0
    avg_duration = sum(s.avg_session_duration * s.sessions for s in sessions) / total_sessions if total_sessions > 0 else 0
    avg_pages = sum(s.pages_per_session * s.sessions for s in sessions) / total_sessions if total_sessions > 0 else 0

    conversion_rate = round((total_conversions / total_sessions) * 100, 2) if total_sessions > 0 else 0

    # Device breakdown
    desktop_sessions = sum(s.sessions for s in sessions if s.device_category == 'desktop')
    mobile_sessions = sum(s.sessions for s in sessions if s.device_category == 'mobile')
    tablet_sessions = sum(s.sessions for s in sessions if s.device_category == 'tablet')

    return schemas.GA4UserBehaviorByCampaignResponse(
        campaign_id=campaign_id,
        campaign_name=campaign_name,
        utm_campaign=campaign_name,
        sessions=total_sessions,
        users=total_users,
        new_users=total_new_users,
        bounce_rate=round(avg_bounce_rate, 2),
        engagement_rate=round(avg_engagement, 2),
        avg_session_duration=round(avg_duration, 2),
        pages_per_session=round(avg_pages, 2),
        conversions=total_conversions,
        conversion_rate=conversion_rate,
        conversion_value=round(total_conversion_value, 2),
        desktop_sessions=desktop_sessions,
        mobile_sessions=mobile_sessions,
        tablet_sessions=tablet_sessions,
        top_landing_pages=[]  # TODO: Implement if landing page data is available
    )
