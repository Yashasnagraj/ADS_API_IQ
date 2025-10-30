"""
Meta Ads ETL Pipeline → Marketing Warehouse

Fetches LIVE data from Meta Marketing API and loads into marketing_warehouse.db

Features:
- Fetches campaigns with performance metrics
- Fetches ad sets and ads
- Daily insights data
- Writes to dimensional star schema

Usage:
    python warehouse_meta_ads_etl.py [--customer-id=1] [--days=30]
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adsinsights import AdsInsights
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from warehouse_etl_helpers import (
    get_warehouse_connection,
    get_or_create_customer,
    get_platform_id,
    get_date_id,
    log_etl_sync,
    update_etl_sync,
    update_platform_last_sync
)


def load_meta_config():
    """Load Meta Ads API configuration"""
    env_path = project_root / '.env.meta'

    if not env_path.exists():
        print(f"❌ ERROR: .env.meta file not found at {env_path}")
        sys.exit(1)

    load_dotenv(env_path)

    app_id = os.getenv('META_APP_ID')
    app_secret = os.getenv('META_APP_SECRET')
    access_token = os.getenv('META_ACCESS_TOKEN')
    ad_account_id = os.getenv('META_AD_ACCOUNT_ID')
    customer_id = os.getenv('CUSTOMER_ID', '1')
    api_version = os.getenv('META_API_VERSION', 'v19.0')

    if not all([app_id, app_secret, access_token, ad_account_id]):
        print("❌ ERROR: Missing Meta configuration in .env.meta")
        sys.exit(1)

    return {
        'app_id': app_id,
        'app_secret': app_secret,
        'access_token': access_token,
        'ad_account_id': ad_account_id,
        'customer_id': int(customer_id),
        'api_version': api_version
    }


def init_meta_api(config):
    """Initialize Meta Marketing API"""
    FacebookAdsApi.init(
        app_id=config['app_id'],
        app_secret=config['app_secret'],
        access_token=config['access_token'],
        api_version=config['api_version']
    )
    print("✅ Meta Marketing API initialized")


def fetch_campaigns(ad_account_id):
    """
    Fetch campaigns from Meta Ads

    Returns: List of campaign dicts
    """
    print("\n📊 Fetching campaigns from Meta API...")

    try:
        ad_account = AdAccount(ad_account_id)

        campaigns = ad_account.get_campaigns(fields=[
            Campaign.Field.id,
            Campaign.Field.name,
            Campaign.Field.status,
            Campaign.Field.effective_status,
            Campaign.Field.objective,
            Campaign.Field.daily_budget,
            Campaign.Field.lifetime_budget,
            Campaign.Field.budget_remaining,
            Campaign.Field.bid_strategy,
            Campaign.Field.buying_type,
            Campaign.Field.created_time,
            Campaign.Field.updated_time,
            Campaign.Field.start_time,
            Campaign.Field.stop_time,
        ])

        campaign_list = []
        for campaign in campaigns:
            # Convert budgets from cents to micros
            daily_budget = int(float(campaign.get('daily_budget', 0)) * 10000) if campaign.get('daily_budget') else None
            lifetime_budget = int(float(campaign.get('lifetime_budget', 0)) * 10000) if campaign.get('lifetime_budget') else None
            budget_remaining = int(float(campaign.get('budget_remaining', 0)) * 10000) if campaign.get('budget_remaining') else None

            campaign_list.append({
                'campaign_id': campaign.get('id'),
                'name': campaign.get('name'),
                'status': campaign.get('status'),
                'effective_status': campaign.get('effective_status'),
                'objective': campaign.get('objective'),
                'daily_budget': daily_budget,
                'lifetime_budget': lifetime_budget,
                'budget_remaining': budget_remaining,
                'bid_strategy': campaign.get('bid_strategy'),
                'buying_type': campaign.get('buying_type'),
                'created_time': campaign.get('created_time'),
                'updated_time': campaign.get('updated_time'),
                'start_time': campaign.get('start_time'),
                'stop_time': campaign.get('stop_time')
            })

        print(f"   ✅ Fetched {len(campaign_list)} campaigns")
        return campaign_list

    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        return []


def fetch_campaign_insights(ad_account_id, days=30):
    """
    Fetch daily campaign insights (performance metrics)

    Returns: Dict of {campaign_id: {date: metrics}}
    """
    print(f"\n📊 Fetching campaign insights (last {days} days)...")

    try:
        ad_account = AdAccount(ad_account_id)

        # Date range
        end_date = datetime.now().date() - timedelta(days=1)  # Yesterday
        start_date = end_date - timedelta(days=days)

        insights = ad_account.get_insights(
            fields=[
                AdsInsights.Field.campaign_id,
                AdsInsights.Field.date_start,
                AdsInsights.Field.date_stop,
                AdsInsights.Field.impressions,
                AdsInsights.Field.clicks,
                AdsInsights.Field.spend,
                AdsInsights.Field.reach,
                AdsInsights.Field.frequency,
                AdsInsights.Field.inline_link_clicks,
                AdsInsights.Field.ctr,
                AdsInsights.Field.cpc,
                AdsInsights.Field.cpm,
                AdsInsights.Field.actions,
                AdsInsights.Field.action_values,
            ],
            params={
                'time_range': {
                    'since': start_date.strftime('%Y-%m-%d'),
                    'until': end_date.strftime('%Y-%m-%d')
                },
                'level': 'campaign',
                'time_increment': 1,  # Daily breakdown
            }
        )

        performance = {}
        record_count = 0

        for insight in insights:
            campaign_id = insight.get('campaign_id')
            date_start = insight.get('date_start')

            if not campaign_id or not date_start:
                continue

            # Parse conversions from actions
            conversions = 0
            conversion_value = 0

            actions = insight.get('actions', [])
            for action in actions:
                action_type = action.get('action_type')
                value = float(action.get('value', 0))

                if action_type in ['purchase', 'omni_purchase', 'lead']:
                    conversions += value

            action_values = insight.get('action_values', [])
            for action_value in action_values:
                action_type = action_value.get('action_type')
                value = float(action_value.get('value', 0))

                if action_type in ['purchase', 'omni_purchase']:
                    conversion_value += value

            # Convert spend to micros
            spend = float(insight.get('spend', 0))
            spend_micros = int(spend * 1000000)

            # Conversion value to micros
            conversion_value_micros = int(conversion_value * 1000000)

            if campaign_id not in performance:
                performance[campaign_id] = {}

            performance[campaign_id][date_start] = {
                'impressions': int(insight.get('impressions', 0)),
                'clicks': int(insight.get('clicks', 0)),
                'spend_micros': spend_micros,
                'conversions': conversions,
                'conversion_value_micros': conversion_value_micros,
                'reach': int(insight.get('reach', 0)),
                'frequency': float(insight.get('frequency', 0)),
                'inline_link_clicks': int(insight.get('inline_link_clicks', 0)),
                'ctr': float(insight.get('ctr', 0)),
                'cpc': float(insight.get('cpc', 0)),
                'cpm': float(insight.get('cpm', 0))
            }
            record_count += 1

        print(f"   ✅ Fetched {record_count} daily insight records for {len(performance)} campaigns")
        return performance

    except Exception as e:
        print(f"   ❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return {}


def upsert_meta_campaign(conn, customer_id, account_id, campaign_data):
    """Insert or update Meta campaign dimension"""
    cursor = conn.cursor()

    # Check if exists
    cursor.execute("""
        SELECT meta_campaign_id FROM dim_meta_campaign
        WHERE customer_id = ? AND campaign_id = ?
    """, (customer_id, campaign_data['campaign_id']))

    existing = cursor.fetchone()

    # Parse timestamps
    def parse_timestamp(ts_str):
        if not ts_str:
            return None
        try:
            return datetime.strptime(ts_str, '%Y-%m-%dT%H:%M:%S%z').replace(tzinfo=None).isoformat()
        except:
            return None

    if existing:
        # Update
        meta_campaign_id = existing[0]
        cursor.execute("""
            UPDATE dim_meta_campaign SET
                name = ?,
                status = ?,
                effective_status = ?,
                objective = ?,
                daily_budget = ?,
                lifetime_budget = ?,
                budget_remaining = ?,
                bid_strategy = ?,
                buying_type = ?,
                updated_time = ?,
                start_time = ?,
                stop_time = ?,
                synced_at = ?
            WHERE meta_campaign_id = ?
        """, (
            campaign_data['name'],
            campaign_data['status'],
            campaign_data['effective_status'],
            campaign_data['objective'],
            campaign_data['daily_budget'],
            campaign_data['lifetime_budget'],
            campaign_data['budget_remaining'],
            campaign_data['bid_strategy'],
            campaign_data['buying_type'],
            parse_timestamp(campaign_data['updated_time']),
            parse_timestamp(campaign_data['start_time']),
            parse_timestamp(campaign_data['stop_time']),
            datetime.now().isoformat(),
            meta_campaign_id
        ))
    else:
        # Insert
        cursor.execute("""
            INSERT INTO dim_meta_campaign (
                customer_id, account_id, campaign_id, name, status,
                effective_status, objective, daily_budget, lifetime_budget,
                budget_remaining, bid_strategy, buying_type,
                created_time, updated_time, start_time, stop_time
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id,
            account_id,
            campaign_data['campaign_id'],
            campaign_data['name'],
            campaign_data['status'],
            campaign_data['effective_status'],
            campaign_data['objective'],
            campaign_data['daily_budget'],
            campaign_data['lifetime_budget'],
            campaign_data['budget_remaining'],
            campaign_data['bid_strategy'],
            campaign_data['buying_type'],
            parse_timestamp(campaign_data['created_time']),
            parse_timestamp(campaign_data['updated_time']),
            parse_timestamp(campaign_data['start_time']),
            parse_timestamp(campaign_data['stop_time'])
        ))
        meta_campaign_id = cursor.lastrowid

    conn.commit()
    return meta_campaign_id


def upsert_meta_performance_fact(conn, customer_id, date_value, meta_campaign_id, metrics):
    """Insert or update Meta campaign performance fact"""
    cursor = conn.cursor()

    platform_id = get_platform_id(conn, 'meta_ads')
    date_id = get_date_id(date_value)

    # Calculate derived metrics
    impressions = metrics.get('impressions', 0)
    clicks = metrics.get('clicks', 0)
    spend_micros = metrics.get('spend_micros', 0)
    conversions = metrics.get('conversions', 0)
    conversion_value_micros = metrics.get('conversion_value_micros', 0)

    ctr = round((clicks / impressions * 100), 2) if impressions > 0 else 0
    cpc_micros = int(spend_micros / clicks) if clicks > 0 else 0
    cpm_micros = int(spend_micros / impressions * 1000) if impressions > 0 else 0
    cpa_micros = int(spend_micros / conversions) if conversions > 0 else 0
    roas = round((conversion_value_micros / spend_micros), 2) if spend_micros > 0 else 0

    # Meta-specific metrics (JSON)
    meta_ads_metrics = json.dumps({
        'reach': metrics.get('reach'),
        'frequency': metrics.get('frequency'),
        'inline_link_clicks': metrics.get('inline_link_clicks'),
        'ctr': metrics.get('ctr'),
        'cpc': metrics.get('cpc'),
        'cpm': metrics.get('cpm')
    })

    # Check if exists
    cursor.execute("""
        SELECT fact_id FROM fact_campaign_performance_daily
        WHERE customer_id = ? AND platform_id = ? AND date_id = ? AND meta_campaign_id = ?
    """, (customer_id, platform_id, date_id, meta_campaign_id))

    existing = cursor.fetchone()

    if existing:
        # Update
        cursor.execute("""
            UPDATE fact_campaign_performance_daily SET
                impressions = ?,
                clicks = ?,
                spend_micros = ?,
                conversions = ?,
                conversion_value_micros = ?,
                ctr = ?,
                cpc_micros = ?,
                cpm_micros = ?,
                cpa_micros = ?,
                roas = ?,
                meta_ads_metrics = ?,
                updated_at = ?
            WHERE fact_id = ?
        """, (
            impressions, clicks, spend_micros, conversions, conversion_value_micros,
            ctr, cpc_micros, cpm_micros, cpa_micros, roas,
            meta_ads_metrics,
            datetime.now().isoformat(),
            existing[0]
        ))
    else:
        # Insert
        cursor.execute("""
            INSERT INTO fact_campaign_performance_daily (
                customer_id, platform_id, date_id, meta_campaign_id,
                impressions, clicks, spend_micros, conversions, conversion_value_micros,
                ctr, cpc_micros, cpm_micros, cpa_micros, roas,
                meta_ads_metrics
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id, platform_id, date_id, meta_campaign_id,
            impressions, clicks, spend_micros, conversions, conversion_value_micros,
            ctr, cpc_micros, cpm_micros, cpa_micros, roas,
            meta_ads_metrics
        ))

    conn.commit()


def load_to_warehouse(conn, customer_id, account_id, campaigns, performance):
    """Load data into warehouse"""
    print("\n💾 Loading data into warehouse...")

    # Ensure customer exists
    get_or_create_customer(
        conn,
        customer_id=customer_id,
        customer_name=f"Customer {customer_id}",
        meta_business_id=account_id
    )

    campaigns_inserted = 0
    facts_inserted = 0

    # Load campaigns
    print("   Loading campaigns...")
    campaign_id_map = {}

    for campaign_data in campaigns:
        meta_campaign_id = upsert_meta_campaign(conn, customer_id, account_id, campaign_data)
        campaign_id_map[campaign_data['campaign_id']] = meta_campaign_id
        campaigns_inserted += 1

    print(f"   ✅ Loaded {campaigns_inserted} campaigns")

    # Load performance
    print("   Loading performance metrics...")

    for campaign_id, daily_metrics in performance.items():
        if campaign_id not in campaign_id_map:
            continue

        meta_campaign_id = campaign_id_map[campaign_id]

        for date_str, metrics in daily_metrics.items():
            upsert_meta_performance_fact(
                conn,
                customer_id=customer_id,
                date_value=date_str,
                meta_campaign_id=meta_campaign_id,
                metrics=metrics
            )
            facts_inserted += 1

    print(f"   ✅ Loaded {facts_inserted} performance records")

    return {
        'campaigns_inserted': campaigns_inserted,
        'facts_inserted': facts_inserted
    }


def main():
    """Main ETL flow"""
    parser = argparse.ArgumentParser(description='Meta Ads → Warehouse ETL')
    parser.add_argument('--customer-id', type=int, help='Internal customer ID override')
    parser.add_argument('--days', type=int, default=30, help='Days of insights to fetch')
    args = parser.parse_args()

    print("=" * 70)
    print("META ADS → WAREHOUSE ETL PIPELINE")
    print("=" * 70)

    # Load config
    config = load_meta_config()
    customer_id = args.customer_id if args.customer_id else config['customer_id']
    ad_account_id = config['ad_account_id']

    print(f"\n📋 Configuration:")
    print(f"   Customer ID: {customer_id}")
    print(f"   Meta Ad Account: {ad_account_id}")
    print(f"   Days: {args.days}")

    # Connect to warehouse
    print("\n🔌 Connecting to warehouse...")
    conn = get_warehouse_connection()
    print("   ✅ Connected")

    # Start sync log
    sync_id = log_etl_sync(conn, customer_id, 'meta_ads', 'running')

    try:
        # Initialize Meta API
        print("\n🔐 Initializing Meta API...")
        init_meta_api(config)

        # Fetch campaigns
        campaigns = fetch_campaigns(ad_account_id)

        if not campaigns:
            print("\n⚠️  No campaigns found")
            update_etl_sync(conn, sync_id, 'success', error_message="No campaigns found")
            return

        # Fetch insights
        performance = fetch_campaign_insights(ad_account_id, args.days)

        # Load to warehouse
        stats = load_to_warehouse(conn, customer_id, ad_account_id, campaigns, performance)

        # Update sync log
        update_etl_sync(
            conn, sync_id, 'success',
            records_inserted=stats['campaigns_inserted'] + stats['facts_inserted']
        )

        # Update platform last sync
        update_platform_last_sync(conn, 'meta_ads')

        # Summary
        print("\n" + "=" * 70)
        print("✅ META ADS ETL COMPLETED")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   Campaigns loaded:       {stats['campaigns_inserted']}")
        print(f"   Performance records:    {stats['facts_inserted']}")
        print(f"   Total records:          {stats['campaigns_inserted'] + stats['facts_inserted']}")
        print(f"\n💾 Data stored in: marketing_warehouse.db")
        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

        update_etl_sync(conn, sync_id, 'failed', error_message=str(e))

    finally:
        conn.close()


if __name__ == "__main__":
    main()
