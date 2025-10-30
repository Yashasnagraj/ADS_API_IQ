"""
Google Analytics 4 (GA4) ETL Pipeline

Extracts data from GA4 and loads into local database:
- Session metrics (by campaign, source, date)
- Event tracking (page_view, purchase, add_to_cart, etc.)
- Conversion paths (multi-touch attribution)
- Audience insights (demographics, technology)

Usage:
    python ga4_etl.py [--days=30] [--customer-id=1]

    --days: Number of days to extract (default: 30)
    --customer-id: Customer ID to extract for (default: from .env.ga4)
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    RunReportRequest,
    DateRange,
    Dimension,
    Metric,
    OrderBy
)
from google.oauth2 import service_account
import json

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from api.app.db.database import SessionLocal, engine
from api.app.db import models

# Create all tables
models.Base.metadata.create_all(bind=engine)


def load_config():
    """Load configuration from .env.ga4"""
    env_path = Path(__file__).parent / '.env.ga4'

    if not env_path.exists():
        print("❌ ERROR: .env.ga4 file not found!")
        print("   Please run setup_ga4.py first")
        sys.exit(1)

    load_dotenv(env_path)

    property_id = os.getenv('GA4_PROPERTY_ID')
    credentials_path = os.getenv('GA4_CREDENTIALS_PATH')
    customer_id = os.getenv('CUSTOMER_ID')

    if not all([property_id, credentials_path, customer_id]):
        print("❌ ERROR: Missing configuration in .env.ga4")
        sys.exit(1)

    return {
        'property_id': property_id,
        'credentials_path': credentials_path,
        'customer_id': int(customer_id)
    }


def create_ga4_client(credentials_path):
    """Create GA4 Analytics Data API client"""
    credentials = service_account.Credentials.from_service_account_file(
        credentials_path,
        scopes=['https://www.googleapis.com/auth/analytics.readonly']
    )
    return BetaAnalyticsDataClient(credentials=credentials)


def extract_sessions(client, property_id, customer_id, days=30):
    """
    Extract session data aggregated by date, source, campaign

    Metrics:
    - Sessions
    - Engaged sessions
    - Bounce rate
    - Session duration
    - Users
    - Page views
    - Conversions
    """
    print(f"\n📊 Extracting session data (last {days} days)...")

    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    try:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sessionSource"),
                Dimension(name="sessionMedium"),
                Dimension(name="sessionCampaignName"),
                Dimension(name="deviceCategory"),
            ],
            metrics=[
                Metric(name="sessions"),
                Metric(name="engagedSessions"),
                Metric(name="bounceRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="activeUsers"),
                Metric(name="newUsers"),
                Metric(name="screenPageViews"),
                Metric(name="conversions"),
            ],
            order_bys=[OrderBy(dimension={'dimension_name': 'date'}, desc=False)]
        )

        response = client.run_report(request)

        # Process results
        db = SessionLocal()
        sessions_count = 0

        for row in response.rows:
            date = row.dimension_values[0].value
            source = row.dimension_values[1].value or '(direct)'
            medium = row.dimension_values[2].value or '(none)'
            campaign = row.dimension_values[3].value or '(not set)'
            device = row.dimension_values[4].value or 'desktop'

            # Parse metrics
            sessions = int(row.metric_values[0].value or 0)
            engaged_sessions = int(row.metric_values[1].value or 0)
            bounce_rate = float(row.metric_values[2].value or 0) * 100  # Convert to percentage
            avg_duration = float(row.metric_values[3].value or 0)
            users = int(row.metric_values[4].value or 0)
            new_users = int(row.metric_values[5].value or 0)
            page_views = int(row.metric_values[6].value or 0)
            conversions = int(row.metric_values[7].value or 0)

            # Calculate derived metrics
            pages_per_session = round(page_views / sessions, 2) if sessions > 0 else 0
            engagement_rate = round((engaged_sessions / sessions) * 100, 2) if sessions > 0 else 0
            bounced_sessions = round((bounce_rate / 100) * sessions) if bounce_rate > 0 else 0

            # Create unique session ID
            session_id = f"{property_id}_{date}_{source}_{campaign}_{device}".replace(' ', '_')

            # Check if session record exists
            existing = db.query(models.GA4Session).filter(
                models.GA4Session.session_id == session_id
            ).first()

            if existing:
                # Update existing record
                existing.sessions = sessions
                existing.engaged_sessions = engaged_sessions
                existing.bounced_sessions = bounced_sessions
                existing.session_duration = avg_duration * sessions
                existing.avg_session_duration = avg_duration
                existing.users = users
                existing.new_users = new_users
                existing.page_views = page_views
                existing.pages_per_session = pages_per_session
                existing.bounce_rate = bounce_rate
                existing.engagement_rate = engagement_rate
                existing.conversions = conversions
            else:
                # Create new record
                session = models.GA4Session(
                    session_id=session_id,
                    property_id=property_id,
                    customer_id=customer_id,
                    date=date,
                    utm_source=source if 'utm' in source else None,
                    utm_medium=medium if 'utm' in medium else None,
                    utm_campaign=campaign if campaign != '(not set)' else None,
                    source=source,
                    medium=medium,
                    sessions=sessions,
                    engaged_sessions=engaged_sessions,
                    bounced_sessions=bounced_sessions,
                    session_duration=avg_duration * sessions,
                    avg_session_duration=avg_duration,
                    users=users,
                    new_users=new_users,
                    page_views=page_views,
                    pages_per_session=pages_per_session,
                    bounce_rate=bounce_rate,
                    engagement_rate=engagement_rate,
                    conversions=conversions,
                    device_category=device
                )
                db.add(session)
                sessions_count += 1

        db.commit()
        db.close()

        print(f"   ✅ Extracted {sessions_count} session records")
        return sessions_count

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return 0


def extract_events(client, property_id, customer_id, days=30):
    """
    Extract event data

    Common events:
    - page_view
    - purchase
    - add_to_cart
    - begin_checkout
    - sign_up
    - video_complete
    """
    print(f"\n📊 Extracting event data (last {days} days)...")

    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    try:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="date"),
                Dimension(name="eventName"),
                Dimension(name="sessionSource"),
                Dimension(name="sessionCampaignName"),
            ],
            metrics=[
                Metric(name="eventCount"),
                Metric(name="eventValue"),
                Metric(name="totalUsers"),
            ],
            order_bys=[
                OrderBy(dimension={'dimension_name': 'date'}, desc=False),
                OrderBy(metric={'metric_name': 'eventCount'}, desc=True)
            ],
            limit=1000  # Limit to top 1000 events
        )

        response = client.run_report(request)

        # Process results
        db = SessionLocal()
        events_count = 0

        for row in response.rows:
            date = row.dimension_values[0].value
            event_name = row.dimension_values[1].value
            source = row.dimension_values[2].value or '(direct)'
            campaign = row.dimension_values[3].value or '(not set)'

            # Parse metrics
            event_count = int(row.metric_values[0].value or 0)
            event_value = float(row.metric_values[1].value or 0)
            users = int(row.metric_values[2].value or 0)

            # Create unique event ID
            event_id = f"{property_id}_{event_name}_{date}_{source}".replace(' ', '_')

            # Check if event record exists
            existing = db.query(models.GA4Event).filter(
                models.GA4Event.event_id == event_id
            ).first()

            if existing:
                # Update existing record
                existing.event_count = event_count
                existing.event_value = event_value
                existing.users = users
            else:
                # Create new record
                event = models.GA4Event(
                    event_id=event_id,
                    property_id=property_id,
                    customer_id=customer_id,
                    event_name=event_name,
                    date=date,
                    utm_source=source if 'utm' in source else None,
                    utm_campaign=campaign if campaign != '(not set)' else None,
                    event_count=event_count,
                    event_value=event_value,
                    users=users
                )
                db.add(event)
                events_count += 1

        db.commit()
        db.close()

        print(f"   ✅ Extracted {events_count} event records")
        return events_count

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return 0


def extract_conversion_paths(client, property_id, customer_id, days=30):
    """
    Extract conversion paths for multi-touch attribution

    This shows the customer journey from first touch to conversion
    """
    print(f"\n📊 Extracting conversion paths (last {days} days)...")

    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    try:
        # Get conversion events with user journey
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="date"),
                Dimension(name="sessionSource"),
                Dimension(name="sessionMedium"),
                Dimension(name="sessionCampaignName"),
                Dimension(name="eventName"),
            ],
            metrics=[
                Metric(name="conversions"),
                Metric(name="totalRevenue"),
            ],
            dimension_filter={
                "filter": {
                    "field_name": "eventName",
                    "string_filter": {
                        "match_type": "CONTAINS",
                        "value": "purchase"
                    }
                }
            },
            limit=500
        )

        response = client.run_report(request)

        # Process results
        db = SessionLocal()
        paths_count = 0

        # Group by user pseudo ID (simplified - in reality you'd need user-level data)
        for row in response.rows:
            date = row.dimension_values[0].value
            source = row.dimension_values[1].value or '(direct)'
            medium = row.dimension_values[2].value or '(none)'
            campaign = row.dimension_values[3].value or '(not set)'
            event_name = row.dimension_values[4].value

            conversions = float(row.metric_values[0].value or 0)
            revenue = float(row.metric_values[1].value or 0)

            if conversions > 0:
                # Create simplified conversion path
                # In a real implementation, you'd use the User Explorer API or BigQuery
                touchpoints = [
                    {
                        "source": source,
                        "medium": medium,
                        "campaign": campaign,
                        "timestamp": date,
                        "order": 1
                    }
                ]

                path_id = f"{property_id}_{date}_{source}_{campaign}".replace(' ', '_')

                # Check if path exists
                existing = db.query(models.GA4ConversionPath).filter(
                    models.GA4ConversionPath.path_id == path_id
                ).first()

                if not existing:
                    conversion_path = models.GA4ConversionPath(
                        path_id=path_id,
                        property_id=property_id,
                        customer_id=customer_id,
                        conversion_event=event_name,
                        conversion_date=date,
                        conversion_value=revenue,
                        touchpoints_json=json.dumps(touchpoints),
                        touchpoints_count=len(touchpoints),
                        days_to_conversion=0,
                        first_touch_source=source,
                        first_touch_campaign=campaign,
                        last_touch_source=source,
                        last_touch_campaign=campaign
                    )
                    db.add(conversion_path)
                    paths_count += 1

        db.commit()
        db.close()

        print(f"   ✅ Extracted {paths_count} conversion paths")
        print(f"   ℹ️  Note: For full multi-touch attribution, export GA4 to BigQuery")
        return paths_count

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return 0


def extract_audience_insights(client, property_id, customer_id, days=30):
    """
    Extract audience demographics and technology insights
    """
    print(f"\n📊 Extracting audience insights (last {days} days)...")

    start_date = (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d')
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')

    try:
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date=start_date, end_date=end_date)],
            dimensions=[
                Dimension(name="date"),
                Dimension(name="country"),
                Dimension(name="deviceCategory"),
                Dimension(name="operatingSystem"),
                Dimension(name="browser"),
            ],
            metrics=[
                Metric(name="activeUsers"),
                Metric(name="newUsers"),
                Metric(name="sessions"),
                Metric(name="engagementRate"),
                Metric(name="averageSessionDuration"),
                Metric(name="screenPageViewsPerSession"),
                Metric(name="conversions"),
                Metric(name="totalRevenue"),
            ],
            limit=500
        )

        response = client.run_report(request)

        # Process results
        db = SessionLocal()
        audience_count = 0

        for row in response.rows:
            date = row.dimension_values[0].value
            country = row.dimension_values[1].value or 'Unknown'
            device = row.dimension_values[2].value or 'desktop'
            os = row.dimension_values[3].value or 'Unknown'
            browser = row.dimension_values[4].value or 'Unknown'

            # Parse metrics
            users = int(row.metric_values[0].value or 0)
            new_users = int(row.metric_values[1].value or 0)
            sessions = int(row.metric_values[2].value or 0)
            engagement_rate = float(row.metric_values[3].value or 0) * 100
            avg_duration = float(row.metric_values[4].value or 0)
            pages_per_session = float(row.metric_values[5].value or 0)
            conversions = int(row.metric_values[6].value or 0)
            revenue = float(row.metric_values[7].value or 0)

            # Calculate conversion rate and ARPU
            conversion_rate = round((conversions / sessions) * 100, 2) if sessions > 0 else 0
            arpu = round(revenue / users, 2) if users > 0 else 0

            # Create unique audience ID
            audience_id = f"{property_id}_{country}_{device}_{date}".replace(' ', '_')

            # Check if audience record exists
            existing = db.query(models.GA4Audience).filter(
                models.GA4Audience.audience_id == audience_id
            ).first()

            if existing:
                # Update existing record
                existing.users = users
                existing.new_users = new_users
                existing.sessions = sessions
                existing.engagement_rate = engagement_rate
                existing.avg_session_duration = avg_duration
                existing.pages_per_session = pages_per_session
                existing.conversions = conversions
                existing.conversion_rate = conversion_rate
                existing.revenue = revenue
                existing.avg_revenue_per_user = arpu
            else:
                # Create new record
                audience = models.GA4Audience(
                    audience_id=audience_id,
                    property_id=property_id,
                    customer_id=customer_id,
                    segment_name="All Users",
                    segment_type="technology",
                    date=date,
                    country=country,
                    device_category=device,
                    operating_system=os,
                    browser=browser,
                    users=users,
                    new_users=new_users,
                    sessions=sessions,
                    engagement_rate=engagement_rate,
                    avg_session_duration=avg_duration,
                    pages_per_session=pages_per_session,
                    conversions=conversions,
                    conversion_rate=conversion_rate,
                    revenue=revenue,
                    avg_revenue_per_user=arpu
                )
                db.add(audience)
                audience_count += 1

        db.commit()
        db.close()

        print(f"   ✅ Extracted {audience_count} audience segments")
        return audience_count

    except Exception as e:
        print(f"   ❌ ERROR: {str(e)}")
        return 0


def update_property_sync_time(property_id):
    """Update last_sync_at timestamp for property"""
    db = SessionLocal()
    try:
        property_record = db.query(models.GA4Property).filter(
            models.GA4Property.property_id == property_id
        ).first()

        if property_record:
            property_record.last_sync_at = datetime.now()
            db.commit()
    finally:
        db.close()


def main():
    """Main ETL flow"""
    parser = argparse.ArgumentParser(description='GA4 ETL Pipeline')
    parser.add_argument('--days', type=int, default=30, help='Number of days to extract')
    parser.add_argument('--customer-id', type=int, help='Customer ID override')
    args = parser.parse_args()

    print("=" * 70)
    print("GOOGLE ANALYTICS 4 ETL PIPELINE")
    print("=" * 70)

    # Load configuration
    config = load_config()

    # Override customer ID if provided
    if args.customer_id:
        config['customer_id'] = args.customer_id

    print(f"\n📋 Configuration:")
    print(f"   Property ID: {config['property_id']}")
    print(f"   Customer ID: {config['customer_id']}")
    print(f"   Days to extract: {args.days}")

    # Create GA4 client
    print(f"\n🔐 Authenticating with GA4...")
    client = create_ga4_client(config['credentials_path'])
    print(f"   ✅ Authenticated")

    # Run ETL tasks
    total_sessions = extract_sessions(client, config['property_id'], config['customer_id'], args.days)
    total_events = extract_events(client, config['property_id'], config['customer_id'], args.days)
    total_paths = extract_conversion_paths(client, config['property_id'], config['customer_id'], args.days)
    total_audience = extract_audience_insights(client, config['property_id'], config['customer_id'], args.days)

    # Update sync timestamp
    update_property_sync_time(config['property_id'])

    # Summary
    print("\n" + "=" * 70)
    print("✅ GA4 ETL PIPELINE COMPLETED")
    print("=" * 70)
    print(f"\n📊 Data Summary:")
    print(f"   Sessions:          {total_sessions}")
    print(f"   Events:            {total_events}")
    print(f"   Conversion Paths:  {total_paths}")
    print(f"   Audience Segments: {total_audience}")
    print(f"\n📝 Next Steps:")
    print(f"   1. Start API server: cd api && uvicorn app.main:app --reload")
    print(f"   2. View docs: http://localhost:8000/docs")
    print(f"   3. Test endpoint: http://localhost:8000/api/v1/ga4/sessions?customer_id={config['customer_id']}")
    print()


if __name__ == "__main__":
    main()
