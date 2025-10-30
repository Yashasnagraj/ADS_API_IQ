"""
Google Ads ETL Pipeline → Marketing Warehouse

Fetches LIVE data from Google Ads API and loads into marketing_warehouse.db

Features:
- Fetches campaigns with performance metrics
- Fetches ad groups and keywords
- Daily performance data
- Writes to dimensional star schema

Usage:
    python warehouse_google_ads_etl.py [--customer-id=1] [--days=30]
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime, timedelta
from dotenv import load_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

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
    upsert_google_ads_campaign,
    upsert_campaign_performance_fact,
    upsert_ad_group,
    upsert_keyword,
    upsert_keyword_performance_fact,
    log_etl_sync,
    update_etl_sync,
    update_platform_last_sync
)


def load_google_ads_config():
    """Load Google Ads API configuration"""
    env_path = project_root / '.env'

    if not env_path.exists():
        print(f"❌ ERROR: .env file not found at {env_path}")
        sys.exit(1)

    load_dotenv(env_path)

    # Get credentials
    customer_id = os.getenv('GOOGLE_ADS_CUSTOMER_ID')

    if not customer_id:
        print("❌ ERROR: GOOGLE_ADS_CUSTOMER_ID not found in .env")
        sys.exit(1)

    return {
        'customer_id': customer_id.replace('-', ''),  # Remove dashes
        'internal_customer_id': int(os.getenv('CUSTOMER_ID', 1))
    }


def init_google_ads_client():
    """Initialize Google Ads API client"""
    try:
        # Look for google-ads.yaml
        yaml_path = project_root / 'google-ads.yaml'
        if not yaml_path.exists():
            print(f"❌ ERROR: google-ads.yaml not found at {yaml_path}")
            sys.exit(1)

        client = GoogleAdsClient.load_from_storage(str(yaml_path))
        print("✅ Google Ads API client initialized")
        return client
    except Exception as e:
        print(f"❌ ERROR: Failed to initialize Google Ads client: {e}")
        sys.exit(1)


def fetch_campaigns(client, customer_id):
    """
    Fetch campaigns from Google Ads API

    Returns: List of campaign dicts
    """
    print("\n📊 Fetching campaigns from Google Ads API...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            campaign.target_cpa.target_cpa_micros,
            campaign.target_roas.target_roas,
            campaign_budget.amount_micros,
            campaign_budget.period,
            campaign.optimization_score,
            campaign.start_date,
            campaign.end_date,
            campaign.serving_status
        FROM campaign
        WHERE campaign.status != 'REMOVED'
        ORDER BY campaign.name
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)

        campaigns = []
        for row in response:
            campaign = row.campaign
            budget = row.campaign_budget

            campaigns.append({
                'campaign_id': str(campaign.id),
                'campaign_name': campaign.name,
                'status': campaign.status.name,
                'serving_status': campaign.serving_status.name,
                'channel_type': campaign.advertising_channel_type.name,
                'bidding_strategy_type': campaign.bidding_strategy_type.name,
                'target_cpa_micros': campaign.target_cpa.target_cpa_micros if campaign.target_cpa else None,
                'target_roas': campaign.target_roas.target_roas if campaign.target_roas else None,
                'budget_amount_micros': budget.amount_micros if budget else None,
                'budget_period': budget.period.name if budget else None,
                'optimization_score': campaign.optimization_score if campaign.optimization_score else None,
                'start_date': campaign.start_date if campaign.start_date else None,
                'end_date': campaign.end_date if campaign.end_date else None
            })

        print(f"   ✅ Fetched {len(campaigns)} campaigns")
        return campaigns

    except GoogleAdsException as ex:
        print(f"   ❌ ERROR: {ex}")
        return []


def fetch_campaign_performance(client, customer_id, days=30):
    """
    Fetch daily campaign performance metrics

    Returns: Dict of {campaign_id: {date: metrics}}
    """
    print(f"\n📊 Fetching campaign performance (last {days} days)...")

    ga_service = client.get_service("GoogleAdsService")

    # Date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    query = f"""
        SELECT
            campaign.id,
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.search_impression_share,
            metrics.search_top_impression_share,
            metrics.search_rank_lost_impression_share,
            metrics.average_cpc,
            metrics.cost_per_conversion,
            metrics.interaction_rate
        FROM campaign
        WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}'
          AND '{end_date.strftime('%Y-%m-%d')}'
          AND campaign.status != 'REMOVED'
        ORDER BY campaign.id, segments.date
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)

        performance = {}
        record_count = 0

        for row in response:
            campaign_id = str(row.campaign.id)
            date = row.segments.date
            metrics = row.metrics

            if campaign_id not in performance:
                performance[campaign_id] = {}

            performance[campaign_id][date] = {
                'impressions': metrics.impressions,
                'clicks': metrics.clicks,
                'spend_micros': metrics.cost_micros,
                'conversions': metrics.conversions,
                'conversion_value_micros': int(metrics.conversions_value * 1000000),  # Convert to micros
                'search_impression_share': metrics.search_impression_share,
                'search_top_impression_share': metrics.search_top_impression_share,
                'search_rank_lost_impression_share': metrics.search_rank_lost_impression_share,
                'average_cpc': metrics.average_cpc,
                'cost_per_conversion': metrics.cost_per_conversion,
                'interaction_rate': metrics.interaction_rate
            }
            record_count += 1

        print(f"   ✅ Fetched {record_count} daily performance records for {len(performance)} campaigns")
        return performance

    except GoogleAdsException as ex:
        print(f"   ❌ ERROR: {ex}")
        return {}


def fetch_ad_groups(client, customer_id):
    """
    Fetch ad groups from Google Ads API

    Returns: List of ad group dicts
    """
    print("\n📊 Fetching ad groups from Google Ads API...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            ad_group.id,
            ad_group.name,
            ad_group.campaign,
            ad_group.status,
            ad_group.type,
            ad_group.cpc_bid_micros,
            ad_group.target_cpa_micros
        FROM ad_group
        WHERE ad_group.status != 'REMOVED'
        ORDER BY ad_group.name
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)

        ad_groups = []
        for row in response:
            ad_group = row.ad_group

            # Extract campaign_id from resource name (format: customers/XXX/campaigns/YYY)
            campaign_id = ad_group.campaign.split('/')[-1]

            ad_groups.append({
                'ad_group_id': str(ad_group.id),
                'campaign_id': campaign_id,
                'ad_group_name': ad_group.name,
                'status': ad_group.status.name,
                'ad_group_type': ad_group.type.name,
                'cpc_bid_micros': ad_group.cpc_bid_micros if ad_group.cpc_bid_micros else None,
                'target_cpa_micros': ad_group.target_cpa_micros if ad_group.target_cpa_micros else None
            })

        print(f"   ✅ Fetched {len(ad_groups)} ad groups")
        return ad_groups

    except GoogleAdsException as ex:
        print(f"   ❌ ERROR: {ex}")
        return []


def fetch_keywords(client, customer_id):
    """
    Fetch keywords from Google Ads API (without performance metrics)

    Returns: List of keyword dicts
    """
    print("\n📊 Fetching keywords from Google Ads API...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            ad_group_criterion.criterion_id,
            ad_group_criterion.ad_group,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            ad_group_criterion.quality_info.quality_score,
            ad_group_criterion.cpc_bid_micros,
            ad_group_criterion.final_urls
        FROM ad_group_criterion
        WHERE ad_group_criterion.type = 'KEYWORD'
          AND ad_group_criterion.status != 'REMOVED'
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)

        keywords = []
        for row in response:
            criterion = row.ad_group_criterion

            # Extract ad_group_id from resource name
            ad_group_id = criterion.ad_group.split('/')[-1]

            keywords.append({
                'keyword_id': str(criterion.criterion_id),
                'ad_group_id': ad_group_id,
                'keyword_text': criterion.keyword.text,
                'match_type': criterion.keyword.match_type.name,
                'status': criterion.status.name,
                'quality_score': criterion.quality_info.quality_score if criterion.quality_info.quality_score else None,
                'cpc_bid_micros': criterion.cpc_bid_micros if criterion.cpc_bid_micros else None,
                'final_urls': ','.join(criterion.final_urls) if criterion.final_urls else None
            })

        print(f"   ✅ Fetched {len(keywords)} keywords")
        return keywords

    except GoogleAdsException as ex:
        print(f"   ❌ ERROR: {ex}")
        return []


def fetch_keyword_performance(client, customer_id, days=30):
    """
    Fetch daily keyword performance metrics using keyword_view

    Returns: Dict of {(ad_group_id, keyword_text, match_type): {date: metrics}}
    """
    print(f"\n📊 Fetching keyword performance (last {days} days)...")

    ga_service = client.get_service("GoogleAdsService")

    # Date range
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    query = f"""
        SELECT
            ad_group.id,
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            ad_group_criterion.quality_info.quality_score
        FROM keyword_view
        WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}'
          AND '{end_date.strftime('%Y-%m-%d')}'
          AND ad_group_criterion.status != 'REMOVED'
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)

        performance = {}
        record_count = 0

        for row in response:
            ad_group_id = str(row.ad_group.id)
            keyword_text = row.ad_group_criterion.keyword.text
            match_type = row.ad_group_criterion.keyword.match_type.name
            date = row.segments.date
            metrics = row.metrics

            key = (ad_group_id, keyword_text, match_type)

            if key not in performance:
                performance[key] = {}

            performance[key][date] = {
                'impressions': metrics.impressions,
                'clicks': metrics.clicks,
                'cost_micros': metrics.cost_micros,
                'conversions': metrics.conversions,
                'conversion_value_micros': int(metrics.conversions_value * 1000000),
                'quality_score': row.ad_group_criterion.quality_info.quality_score if row.ad_group_criterion.quality_info.quality_score else None
            }
            record_count += 1

        print(f"   ✅ Fetched {record_count} daily keyword performance records for {len(performance)} keywords")
        return performance

    except GoogleAdsException as ex:
        print(f"   ❌ ERROR: {ex}")
        return {}


def load_to_warehouse(conn, internal_customer_id, google_ads_customer_id, campaigns, performance,
                      ad_groups=None, keywords=None, keyword_performance=None):
    """Load data into warehouse"""
    print("\n💾 Loading data into warehouse...")

    # Ensure customer exists
    get_or_create_customer(
        conn,
        customer_id=internal_customer_id,
        customer_name=f"Customer {internal_customer_id}",
        google_ads_customer_id=google_ads_customer_id
    )

    campaigns_inserted = 0
    ad_groups_inserted = 0
    keywords_inserted = 0
    campaign_facts_inserted = 0
    keyword_facts_inserted = 0

    # Load campaigns
    print("   Loading campaigns...")
    campaign_id_map = {}  # Map Google campaign_id → internal google_campaign_id

    for campaign_data in campaigns:
        google_campaign_id = upsert_google_ads_campaign(conn, internal_customer_id, campaign_data)
        campaign_id_map[campaign_data['campaign_id']] = google_campaign_id
        campaigns_inserted += 1

    print(f"   ✅ Loaded {campaigns_inserted} campaigns")

    # Load campaign performance facts
    print("   Loading campaign performance metrics...")

    for campaign_id, daily_metrics in performance.items():
        if campaign_id not in campaign_id_map:
            continue  # Skip if campaign not in dimension table

        google_campaign_id = campaign_id_map[campaign_id]

        for date_str, metrics in daily_metrics.items():
            upsert_campaign_performance_fact(
                conn,
                customer_id=internal_customer_id,
                platform_name='google_ads',
                date_value=date_str,
                google_campaign_id=google_campaign_id,
                metrics=metrics
            )
            campaign_facts_inserted += 1

    print(f"   ✅ Loaded {campaign_facts_inserted} campaign performance records")

    # Load ad groups
    if ad_groups:
        print("   Loading ad groups...")
        ad_group_id_map = {}  # Map (campaign_id, ad_group_id) → internal google_ad_group_id

        for ad_group_data in ad_groups:
            campaign_id = ad_group_data['campaign_id']
            if campaign_id not in campaign_id_map:
                continue  # Skip if campaign not loaded

            google_campaign_id = campaign_id_map[campaign_id]
            google_ad_group_id = upsert_ad_group(conn, internal_customer_id, google_campaign_id, ad_group_data)
            ad_group_id_map[(campaign_id, ad_group_data['ad_group_id'])] = google_ad_group_id
            ad_groups_inserted += 1

        print(f"   ✅ Loaded {ad_groups_inserted} ad groups")

        # Load keywords
        if keywords:
            print("   Loading keywords...")
            keyword_id_map = {}  # Map (ad_group_id, keyword_text, match_type) → (internal_keyword_id, internal_ad_group_id, google_campaign_id)

            for keyword_data in keywords:
                google_ad_group_id = keyword_data['ad_group_id']

                # Find matching ad group
                matching_key = None
                for key in ad_group_id_map.keys():
                    if key[1] == google_ad_group_id:
                        matching_key = key
                        break

                if not matching_key:
                    continue  # Skip if ad group not loaded

                internal_ad_group_id = ad_group_id_map[matching_key]
                google_campaign_id = campaign_id_map[matching_key[0]]  # Get campaign_id from the key

                internal_keyword_id = upsert_keyword(
                    conn, internal_customer_id, internal_ad_group_id,
                    google_campaign_id, keyword_data
                )
                key = (google_ad_group_id, keyword_data['keyword_text'], keyword_data.get('match_type'))
                keyword_id_map[key] = (internal_keyword_id, internal_ad_group_id, google_campaign_id)
                keywords_inserted += 1

            print(f"   ✅ Loaded {keywords_inserted} keywords")

        # Load keyword performance facts
        if keyword_performance:
            print("   Loading keyword performance metrics...")

            for key, daily_metrics in keyword_performance.items():
                # key = (ad_group_id, keyword_text, match_type)
                if key not in keyword_id_map:
                    continue

                internal_keyword_id, internal_ad_group_id, google_campaign_id = keyword_id_map[key]

                for date_str, metrics in daily_metrics.items():
                    upsert_keyword_performance_fact(
                        conn,
                        customer_id=internal_customer_id,
                        google_campaign_id=google_campaign_id,
                        internal_ad_group_id=internal_ad_group_id,
                        internal_keyword_id=internal_keyword_id,
                        date_value=date_str,
                        metrics=metrics
                    )
                    keyword_facts_inserted += 1

            print(f"   ✅ Loaded {keyword_facts_inserted} keyword performance records")

    return {
        'campaigns_inserted': campaigns_inserted,
        'ad_groups_inserted': ad_groups_inserted,
        'keywords_inserted': keywords_inserted,
        'campaign_facts_inserted': campaign_facts_inserted,
        'keyword_facts_inserted': keyword_facts_inserted
    }


def main():
    """Main ETL flow"""
    parser = argparse.ArgumentParser(description='Google Ads → Warehouse ETL')
    parser.add_argument('--customer-id', type=int, help='Internal customer ID override')
    parser.add_argument('--days', type=int, default=30, help='Days of performance data to fetch')
    args = parser.parse_args()

    print("=" * 70)
    print("GOOGLE ADS → WAREHOUSE ETL PIPELINE")
    print("=" * 70)

    # Load config
    config = load_google_ads_config()
    internal_customer_id = args.customer_id if args.customer_id else config['internal_customer_id']
    google_ads_customer_id = config['customer_id']

    print(f"\n📋 Configuration:")
    print(f"   Internal Customer ID: {internal_customer_id}")
    print(f"   Google Ads Customer ID: {google_ads_customer_id}")
    print(f"   Performance Days: {args.days}")

    # Connect to warehouse
    print("\n🔌 Connecting to warehouse...")
    conn = get_warehouse_connection()
    print("   ✅ Connected")

    # Start ETL sync log
    sync_id = log_etl_sync(conn, internal_customer_id, 'google_ads', 'running')

    try:
        # Initialize Google Ads client
        print("\n🔐 Initializing Google Ads API...")
        client = init_google_ads_client()

        # Fetch campaigns
        campaigns = fetch_campaigns(client, google_ads_customer_id)

        if not campaigns:
            print("\n⚠️  No campaigns found")
            update_etl_sync(conn, sync_id, 'success', error_message="No campaigns found")
            return

        # Fetch campaign performance
        performance = fetch_campaign_performance(client, google_ads_customer_id, args.days)

        # Fetch ad groups
        ad_groups = fetch_ad_groups(client, google_ads_customer_id)

        # Fetch keywords
        keywords = fetch_keywords(client, google_ads_customer_id)

        # Fetch keyword performance
        keyword_performance = fetch_keyword_performance(client, google_ads_customer_id, args.days)

        # Load to warehouse
        stats = load_to_warehouse(
            conn, internal_customer_id, google_ads_customer_id,
            campaigns, performance,
            ad_groups, keywords, keyword_performance
        )

        # Calculate total records
        total_inserted = (
            stats['campaigns_inserted'] +
            stats['ad_groups_inserted'] +
            stats['keywords_inserted'] +
            stats['campaign_facts_inserted'] +
            stats['keyword_facts_inserted']
        )

        # Update sync log
        update_etl_sync(
            conn, sync_id, 'success',
            records_inserted=total_inserted,
            records_updated=0
        )

        # Update platform last sync
        update_platform_last_sync(conn, 'google_ads')

        # Summary
        print("\n" + "=" * 70)
        print("✅ GOOGLE ADS ETL COMPLETED")
        print("=" * 70)
        print(f"\n📊 Summary:")
        print(f"   Campaigns loaded:              {stats['campaigns_inserted']}")
        print(f"   Ad groups loaded:              {stats['ad_groups_inserted']}")
        print(f"   Keywords loaded:               {stats['keywords_inserted']}")
        print(f"   Campaign performance records:  {stats['campaign_facts_inserted']}")
        print(f"   Keyword performance records:   {stats['keyword_facts_inserted']}")
        print(f"   Total records:                 {total_inserted}")
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
