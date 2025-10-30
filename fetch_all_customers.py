"""
Fetch Data from All Customer Accounts

Runs Google Ads ETL for all three customer accounts:
1. Emcee Sons (5032737756)
2. VANAVASI KALYANA (7613138874)
3. Communn.io (6265362093)
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
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
    upsert_google_ads_campaign,
    upsert_campaign_performance_fact,
    upsert_ad_group,
    upsert_keyword,
    upsert_keyword_performance_fact,
    log_etl_sync,
    update_etl_sync,
    update_platform_last_sync
)

# Customer accounts to fetch
CUSTOMERS = [
    {'internal_id': 1, 'google_id': '5032737756', 'name': 'Emcee Sons', 'currency': 'INR'},
    {'internal_id': 2, 'google_id': '7613138874', 'name': 'VANAVASI KALYANA', 'currency': 'USD'},
    {'internal_id': 3, 'google_id': '6265362093', 'name': 'Communn.io', 'currency': 'INR'},
]


def init_google_ads_client():
    """Initialize Google Ads client"""
    yaml_path = project_root / 'google-ads.yaml'
    return GoogleAdsClient.load_from_storage(str(yaml_path))


def fetch_campaigns(client, customer_id):
    """Fetch campaigns from Google Ads"""
    print(f"\n📊 Fetching campaigns from {customer_id}...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.advertising_channel_type,
            campaign.bidding_strategy_type,
            campaign.campaign_budget,
            campaign.start_date,
            campaign.end_date
        FROM campaign
        WHERE campaign.status != 'REMOVED'
        ORDER BY campaign.name
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)

        campaigns = []
        for row in response:
            camp = row.campaign
            campaigns.append({
                'campaign_id': str(camp.id),
                'campaign_name': camp.name,
                'status': camp.status.name,
                'channel_type': camp.advertising_channel_type.name,
                'bidding_strategy_type': camp.bidding_strategy_type.name,
                'start_date': camp.start_date,
                'end_date': camp.end_date if camp.end_date else None
            })

        print(f"   ✅ Found {len(campaigns)} campaigns")
        return campaigns

    except GoogleAdsException as ex:
        print(f"   ❌ ERROR: {ex}")
        return []


def fetch_campaign_performance(client, customer_id, days=30):
    """Fetch campaign performance metrics"""
    print(f"\n📈 Fetching {days} days of performance data...")

    ga_service = client.get_service("GoogleAdsService")

    # Calculate date range
    from datetime import datetime, timedelta
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=days)

    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            segments.date,
            metrics.impressions,
            metrics.clicks,
            metrics.cost_micros,
            metrics.conversions,
            metrics.conversions_value,
            metrics.ctr,
            metrics.average_cpc,
            metrics.cost_per_conversion,
            metrics.search_impression_share
        FROM campaign
        WHERE segments.date >= '{start_date.strftime("%Y-%m-%d")}'
          AND segments.date <= '{end_date.strftime("%Y-%m-%d")}'
          AND campaign.status != 'REMOVED'
        ORDER BY campaign.id, segments.date
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)

        # Organize by campaign_id -> date -> metrics
        performance = {}
        record_count = 0

        for row in response:
            campaign_id = str(row.campaign.id)
            date_str = row.segments.date
            metrics = row.metrics

            if campaign_id not in performance:
                performance[campaign_id] = {}

            performance[campaign_id][date_str] = {
                'impressions': metrics.impressions,
                'clicks': metrics.clicks,
                'spend_micros': metrics.cost_micros,
                'conversions': metrics.conversions,
                'conversion_value_micros': int(metrics.conversions_value * 1000000),
                'ctr': metrics.ctr * 100,  # Convert to percentage
                'cpc_micros': int(metrics.average_cpc * 1000000) if metrics.average_cpc else 0,
                'cpa_micros': int(metrics.cost_per_conversion * 1000000) if metrics.cost_per_conversion else 0,
                'search_impression_share': metrics.search_impression_share
            }
            record_count += 1

        print(f"   ✅ Fetched {record_count} performance records")
        return performance

    except GoogleAdsException as ex:
        print(f"   ❌ ERROR: {ex}")
        return {}


def fetch_ad_groups(client, customer_id):
    """Fetch ad groups from Google Ads"""
    print(f"\n📊 Fetching ad groups from {customer_id}...")

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
            ag = row.ad_group
            campaign_id = ag.campaign.split('/')[-1]

            ad_groups.append({
                'ad_group_id': str(ag.id),
                'campaign_id': campaign_id,
                'ad_group_name': ag.name,
                'status': ag.status.name,
                'ad_group_type': ag.type.name,
                'cpc_bid_micros': ag.cpc_bid_micros if ag.cpc_bid_micros else None,
                'target_cpa_micros': ag.target_cpa_micros if ag.target_cpa_micros else None
            })

        print(f"   ✅ Found {len(ad_groups)} ad groups")
        return ad_groups

    except GoogleAdsException as ex:
        print(f"   ❌ ERROR: {ex}")
        return []


def fetch_keywords(client, customer_id):
    """Fetch keywords from Google Ads"""
    print(f"\n📊 Fetching keywords from {customer_id}...")

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
            kw = row.ad_group_criterion
            ad_group_id = kw.ad_group.split('/')[-1]

            keywords.append({
                'keyword_id': str(kw.criterion_id),
                'ad_group_id': ad_group_id,
                'keyword_text': kw.keyword.text,
                'match_type': kw.keyword.match_type.name,
                'status': kw.status.name,
                'quality_score': kw.quality_info.quality_score if kw.quality_info.quality_score else None,
                'cpc_bid_micros': kw.cpc_bid_micros if kw.cpc_bid_micros else None,
                'final_urls': ','.join(kw.final_urls) if kw.final_urls else None
            })

        print(f"   ✅ Found {len(keywords)} keywords")
        return keywords

    except GoogleAdsException as ex:
        print(f"   ❌ ERROR: {ex}")
        return []


def fetch_keyword_performance(client, customer_id, days=30):
    """Fetch keyword performance metrics using keyword_view"""
    print(f"\n📈 Fetching {days} days of keyword performance data...")

    ga_service = client.get_service("GoogleAdsService")

    # Calculate date range
    from datetime import datetime, timedelta
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
        WHERE segments.date >= '{start_date.strftime("%Y-%m-%d")}'
          AND segments.date <= '{end_date.strftime("%Y-%m-%d")}'
          AND ad_group_criterion.status != 'REMOVED'
    """

    try:
        response = ga_service.search(customer_id=customer_id, query=query)

        # Organize by (ad_group_id, keyword_text, match_type) -> date -> metrics
        performance = {}
        record_count = 0

        for row in response:
            ad_group_id = str(row.ad_group.id)
            keyword_text = row.ad_group_criterion.keyword.text
            match_type = row.ad_group_criterion.keyword.match_type.name
            date_str = row.segments.date
            metrics = row.metrics

            key = (ad_group_id, keyword_text, match_type)

            if key not in performance:
                performance[key] = {}

            performance[key][date_str] = {
                'impressions': metrics.impressions,
                'clicks': metrics.clicks,
                'cost_micros': metrics.cost_micros,
                'conversions': metrics.conversions,
                'conversion_value_micros': int(metrics.conversions_value * 1000000),
                'quality_score': row.ad_group_criterion.quality_info.quality_score if row.ad_group_criterion.quality_info.quality_score else None
            }
            record_count += 1

        print(f"   ✅ Fetched {record_count} keyword performance records")
        return performance

    except GoogleAdsException as ex:
        print(f"   ❌ ERROR: {ex}")
        return {}


def load_to_warehouse(conn, customer_info, campaigns, performance, ad_groups=None, keywords=None, keyword_performance=None):
    """Load data into warehouse"""
    print(f"\n💾 Loading {customer_info['name']} data into warehouse...")

    # Ensure customer exists
    get_or_create_customer(
        conn,
        customer_id=customer_info['internal_id'],
        customer_name=customer_info['name'],
        google_ads_customer_id=customer_info['google_id'],
        currency=customer_info['currency']
    )

    campaigns_loaded = 0
    ad_groups_loaded = 0
    keywords_loaded = 0
    campaign_facts_loaded = 0
    keyword_facts_loaded = 0

    # Load campaigns
    print("   Loading campaigns...")
    campaign_id_map = {}

    for campaign_data in campaigns:
        google_campaign_id = upsert_google_ads_campaign(
            conn,
            customer_info['internal_id'],
            campaign_data
        )
        campaign_id_map[campaign_data['campaign_id']] = google_campaign_id
        campaigns_loaded += 1

    print(f"   ✅ Loaded {campaigns_loaded} campaigns")

    # Load campaign performance facts
    print("   Loading campaign performance metrics...")

    for campaign_id, daily_metrics in performance.items():
        if campaign_id not in campaign_id_map:
            continue

        google_campaign_id = campaign_id_map[campaign_id]

        for date_str, metrics in daily_metrics.items():
            upsert_campaign_performance_fact(
                conn,
                customer_id=customer_info['internal_id'],
                platform_name='google_ads',
                date_value=date_str,
                google_campaign_id=google_campaign_id,
                metrics=metrics
            )
            campaign_facts_loaded += 1

    print(f"   ✅ Loaded {campaign_facts_loaded} campaign performance records")

    # Load ad groups
    if ad_groups:
        print("   Loading ad groups...")
        ad_group_id_map = {}  # Map (google_ad_group_id) → (internal_ad_group_id, google_campaign_id)

        for ad_group_data in ad_groups:
            campaign_id = ad_group_data['campaign_id']
            if campaign_id not in campaign_id_map:
                continue

            google_campaign_id = campaign_id_map[campaign_id]
            internal_ad_group_id = upsert_ad_group(conn, customer_info['internal_id'], google_campaign_id, ad_group_data)
            ad_group_id_map[ad_group_data['ad_group_id']] = (internal_ad_group_id, google_campaign_id)
            ad_groups_loaded += 1

        print(f"   ✅ Loaded {ad_groups_loaded} ad groups")

        # Load keywords
        if keywords:
            print("   Loading keywords...")
            keyword_id_map = {}  # Map (ad_group_id, keyword_text, match_type) → (internal_keyword_id, internal_ad_group_id, google_campaign_id)

            for keyword_data in keywords:
                google_ad_group_id = keyword_data['ad_group_id']

                if google_ad_group_id not in ad_group_id_map:
                    continue

                internal_ad_group_id, google_campaign_id = ad_group_id_map[google_ad_group_id]
                internal_keyword_id = upsert_keyword(
                    conn, customer_info['internal_id'], internal_ad_group_id,
                    google_campaign_id, keyword_data
                )
                key = (google_ad_group_id, keyword_data['keyword_text'], keyword_data.get('match_type'))
                keyword_id_map[key] = (internal_keyword_id, internal_ad_group_id, google_campaign_id)
                keywords_loaded += 1

            print(f"   ✅ Loaded {keywords_loaded} keywords")

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
                        customer_id=customer_info['internal_id'],
                        google_campaign_id=google_campaign_id,
                        internal_ad_group_id=internal_ad_group_id,
                        internal_keyword_id=internal_keyword_id,
                        date_value=date_str,
                        metrics=metrics
                    )
                    keyword_facts_loaded += 1

            print(f"   ✅ Loaded {keyword_facts_loaded} keyword performance records")

    return {
        'campaigns': campaigns_loaded,
        'ad_groups': ad_groups_loaded,
        'keywords': keywords_loaded,
        'campaign_facts': campaign_facts_loaded,
        'keyword_facts': keyword_facts_loaded
    }


def main():
    """Main ETL flow for all customers"""
    parser = argparse.ArgumentParser(description='Fetch all customer data into warehouse')
    parser.add_argument('--days', type=int, default=30, help='Days of performance data')
    args = parser.parse_args()

    print("=" * 70)
    print("FETCHING ALL CUSTOMER DATA → WAREHOUSE")
    print("=" * 70)
    print(f"\n📋 Will fetch data from {len(CUSTOMERS)} customers:")
    for cust in CUSTOMERS:
        print(f"   • {cust['name']} (ID: {cust['google_id']})")

    # Connect to warehouse
    print("\n🔌 Connecting to warehouse...")
    conn = get_warehouse_connection()
    print("   ✅ Connected")

    # Initialize Google Ads client
    print("\n🔐 Initializing Google Ads API...")
    client = init_google_ads_client()
    print("   ✅ Authenticated")

    # Process each customer
    total_campaigns = 0
    total_ad_groups = 0
    total_keywords = 0
    total_campaign_facts = 0
    total_keyword_facts = 0

    for customer in CUSTOMERS:
        print("\n" + "=" * 70)
        print(f"📊 PROCESSING: {customer['name']}")
        print("=" * 70)

        # Start ETL sync log
        sync_id = log_etl_sync(conn, customer['internal_id'], 'google_ads', 'running')

        try:
            # Fetch campaigns
            campaigns = fetch_campaigns(client, customer['google_id'])

            if not campaigns:
                print(f"   ⚠️  No campaigns found for {customer['name']}")
                update_etl_sync(conn, sync_id, 'success', error_message="No campaigns")
                continue

            # Fetch campaign performance
            performance = fetch_campaign_performance(client, customer['google_id'], args.days)

            # Fetch ad groups
            ad_groups = fetch_ad_groups(client, customer['google_id'])

            # Fetch keywords
            keywords = fetch_keywords(client, customer['google_id'])

            # Fetch keyword performance
            keyword_performance = fetch_keyword_performance(client, customer['google_id'], args.days)

            # Load to warehouse
            stats = load_to_warehouse(
                conn, customer, campaigns, performance,
                ad_groups, keywords, keyword_performance
            )

            # Calculate total records
            total_records = (
                stats['campaigns'] +
                stats['ad_groups'] +
                stats['keywords'] +
                stats['campaign_facts'] +
                stats['keyword_facts']
            )

            # Update sync log
            update_etl_sync(
                conn, sync_id, 'success',
                records_inserted=total_records
            )

            total_campaigns += stats['campaigns']
            total_ad_groups += stats['ad_groups']
            total_keywords += stats['keywords']
            total_campaign_facts += stats['campaign_facts']
            total_keyword_facts += stats['keyword_facts']

            print(f"\n   ✅ {customer['name']}:")
            print(f"      Campaigns: {stats['campaigns']}, Ad Groups: {stats['ad_groups']}, Keywords: {stats['keywords']}")
            print(f"      Campaign Performance: {stats['campaign_facts']}, Keyword Performance: {stats['keyword_facts']}")

        except Exception as e:
            print(f"\n   ❌ ERROR processing {customer['name']}: {e}")
            import traceback
            traceback.print_exc()
            update_etl_sync(conn, sync_id, 'failed', error_message=str(e))

    # Update platform last sync
    update_platform_last_sync(conn, 'google_ads')

    # Calculate grand total
    grand_total = total_campaigns + total_ad_groups + total_keywords + total_campaign_facts + total_keyword_facts

    # Final summary
    print("\n" + "=" * 70)
    print("✅ ALL CUSTOMERS ETL COMPLETED")
    print("=" * 70)
    print(f"\n📊 Summary:")
    print(f"   Customers processed:             {len(CUSTOMERS)}")
    print(f"   Total campaigns:                 {total_campaigns}")
    print(f"   Total ad groups:                 {total_ad_groups}")
    print(f"   Total keywords:                  {total_keywords}")
    print(f"   Total campaign performance:      {total_campaign_facts}")
    print(f"   Total keyword performance:       {total_keyword_facts}")
    print(f"   Total records:                   {grand_total}")
    print(f"\n💾 Data stored in: marketing_warehouse.db")
    print(f"\n📈 Next step: python show_warehouse_summary.py")
    print("=" * 70)

    conn.close()


if __name__ == "__main__":
    main()
