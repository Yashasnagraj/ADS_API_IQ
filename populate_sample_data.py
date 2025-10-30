"""
Populate Marketing Warehouse with Sample Data

Creates realistic demo data across all platforms:
- Google Ads campaigns and performance
- Meta Ads campaigns and performance
- GA4 traffic sources
- Shopify orders with attribution
- Cross-platform campaign mapping
- Multi-touch attribution journeys

Usage:
    python populate_sample_data.py
"""

import sys
import os
import sqlite3
from pathlib import Path
from datetime import datetime, timedelta
import random
import json

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(__file__).parent / 'marketing_warehouse.db'

def create_sample_customer(conn):
    """Create a sample customer"""
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO dim_customer (
            customer_id, customer_name, descriptive_name,
            google_ads_customer_id, meta_business_id, ga4_account_id, shopify_domain,
            industry_vertical, timezone, currency, is_active
        ) VALUES (1, 'Demo Ecommerce Store', 'Fashion Retailer',
                  '3341907700', 'act_1595713968470185', '123456789', 'demo-store.myshopify.com',
                  'ecommerce', 'America/New_York', 'USD', 1)
    """)

    conn.commit()
    print("✅ Created customer: Demo Ecommerce Store")


def create_google_ads_campaigns(conn):
    """Create Google Ads campaigns with performance"""
    cursor = conn.cursor()

    campaigns = [
        {'name': 'Summer Sale 2024', 'budget': 5000, 'target_roas': 4.5},
        {'name': 'Brand Keywords', 'budget': 2000, 'target_roas': 6.0},
        {'name': 'Shopping Feed', 'budget': 8000, 'target_roas': 3.5},
    ]

    google_campaign_ids = []

    for camp in campaigns:
        cursor.execute("""
            INSERT INTO dim_google_ads_campaign (
                customer_id, campaign_id, campaign_name, status, serving_status,
                channel_type, bidding_strategy_type, target_roas,
                budget_amount_micros, budget_period, optimization_score,
                start_date, end_date
            ) VALUES (1, ?, ?, 'ENABLED', 'SERVING',
                     'SEARCH', 'TARGET_ROAS', ?,
                     ?, 'DAILY', 0.82,
                     '2024-01-01', '2024-12-31')
        """, (
            f"google_{camp['name'].replace(' ', '_').lower()}",
            camp['name'],
            camp['target_roas'],
            camp['budget'] * 1000000
        ))

        google_campaign_ids.append((cursor.lastrowid, camp['name'], camp))

    conn.commit()
    print(f"✅ Created {len(campaigns)} Google Ads campaigns")

    # Create performance data for last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    current_date = start_date
    records = 0

    while current_date <= end_date:
        date_id = current_date.strftime("%Y%m%d")

        for google_id, name, config in google_campaign_ids:
            # Generate realistic metrics
            impressions = random.randint(5000, 15000)
            ctr = random.uniform(2.5, 5.5) / 100
            clicks = int(impressions * ctr)
            cpc = random.uniform(0.80, 2.50)
            spend = clicks * cpc
            conv_rate = random.uniform(2, 5) / 100
            conversions = int(clicks * conv_rate)
            roas = config['target_roas'] * random.uniform(0.9, 1.1)
            conversion_value = spend * roas

            cursor.execute("""
                INSERT INTO fact_campaign_performance_daily (
                    customer_id, platform_id, date_id, google_campaign_id,
                    impressions, clicks, spend_micros, conversions, conversion_value_micros,
                    ctr, cpc_micros, cpm_micros, cpa_micros, roas,
                    google_ads_metrics
                ) VALUES (1, 1, ?, ?,
                         ?, ?, ?, ?, ?,
                         ?, ?, ?, ?, ?,
                         ?)
            """, (
                date_id, google_id,
                impressions, clicks, int(spend * 1000000), conversions, int(conversion_value * 1000000),
                round(ctr * 100, 2),
                int(cpc * 1000000),
                int((spend / impressions * 1000) * 1000000),
                int((spend / conversions) * 1000000) if conversions > 0 else 0,
                round(roas, 2),
                json.dumps({
                    'quality_score': random.randint(7, 10),
                    'search_impression_share': random.uniform(60, 90),
                    'search_top_impression_share': random.uniform(40, 70)
                })
            ))

            records += 1

        current_date += timedelta(days=1)

    conn.commit()
    print(f"✅ Created {records} Google Ads performance records")

    return google_campaign_ids


def create_meta_campaigns(conn):
    """Create Meta Ads campaigns with performance"""
    cursor = conn.cursor()

    campaigns = [
        {'name': 'Summer Sale 2024', 'budget': 3000, 'objective': 'OUTCOME_SALES'},
        {'name': 'Retargeting Campaign', 'budget': 1500, 'objective': 'OUTCOME_SALES'},
        {'name': 'Lookalike Audiences', 'budget': 2500, 'objective': 'OUTCOME_AWARENESS'},
    ]

    meta_campaign_ids = []

    for camp in campaigns:
        cursor.execute("""
            INSERT INTO dim_meta_campaign (
                customer_id, account_id, campaign_id, name, status, effective_status,
                objective, daily_budget, bid_strategy, buying_type,
                created_time, updated_time, start_time
            ) VALUES (1, 'act_1595713968470185', ?, ?, 'ACTIVE', 'ACTIVE',
                     ?, ?, 'LOWEST_COST_WITHOUT_CAP', 'AUCTION',
                     ?, ?, ?)
        """, (
            f"meta_{camp['name'].replace(' ', '_').lower()}",
            camp['name'],
            camp['objective'],
            camp['budget'] * 10000,  # Meta uses different scale
            datetime(2024, 1, 1).isoformat(),
            datetime.now().isoformat(),
            datetime(2024, 1, 1).isoformat()
        ))

        meta_campaign_ids.append((cursor.lastrowid, camp['name'], camp))

    conn.commit()
    print(f"✅ Created {len(campaigns)} Meta Ads campaigns")

    # Create performance data
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)

    current_date = start_date
    records = 0

    while current_date <= end_date:
        date_id = current_date.strftime("%Y%m%d")

        for meta_id, name, config in meta_campaign_ids:
            impressions = random.randint(8000, 20000)
            ctr = random.uniform(1.8, 4.2) / 100
            clicks = int(impressions * ctr)
            cpc = random.uniform(0.60, 1.80)
            spend = clicks * cpc
            conv_rate = random.uniform(1.5, 4) / 100
            conversions = int(clicks * conv_rate)
            roas = random.uniform(2.5, 4.5)
            conversion_value = spend * roas

            cursor.execute("""
                INSERT INTO fact_campaign_performance_daily (
                    customer_id, platform_id, date_id, meta_campaign_id,
                    impressions, clicks, spend_micros, conversions, conversion_value_micros,
                    ctr, cpc_micros, cpm_micros, cpa_micros, roas,
                    meta_ads_metrics
                ) VALUES (1, 2, ?, ?,
                         ?, ?, ?, ?, ?,
                         ?, ?, ?, ?, ?,
                         ?)
            """, (
                date_id, meta_id,
                impressions, clicks, int(spend * 1000000), conversions, int(conversion_value * 1000000),
                round(ctr * 100, 2),
                int(cpc * 1000000),
                int((spend / impressions * 1000) * 1000000),
                int((spend / conversions) * 1000000) if conversions > 0 else 0,
                round(roas, 2),
                json.dumps({
                    'reach': int(impressions * random.uniform(0.6, 0.9)),
                    'frequency': random.uniform(1.1, 2.5),
                    'inline_link_clicks': int(clicks * random.uniform(0.8, 0.95))
                })
            ))

            records += 1

        current_date += timedelta(days=1)

    conn.commit()
    print(f"✅ Created {records} Meta Ads performance records")

    return meta_campaign_ids


def create_unified_campaigns(conn, google_campaigns, meta_campaigns):
    """Create unified campaign mappings"""
    cursor = conn.cursor()

    # Map "Summer Sale 2024" across both platforms
    cursor.execute("""
        INSERT INTO dim_campaign_unified (
            customer_id, campaign_name, campaign_objective, campaign_type,
            start_date, end_date, is_active
        ) VALUES (1, 'Summer Sale 2024', 'sales', 'search_and_social',
                 '2024-01-01', '2024-12-31', 1)
    """)
    unified_id = cursor.lastrowid

    # Find matching campaigns
    google_summer = [g for g in google_campaigns if 'Summer Sale' in g[1]][0]
    meta_summer = [m for m in meta_campaigns if 'Summer Sale' in m[1]][0]

    # Create mapping
    cursor.execute("""
        INSERT INTO map_campaign_cross_platform (
            campaign_unified_id, customer_id,
            google_ads_campaign_id, meta_campaign_id,
            mapping_method, mapping_confidence, created_by, is_verified
        ) VALUES (?, 1, ?, ?, 'auto_name_match', 95, 'system', 1)
    """, (unified_id, google_summer[0], meta_summer[0]))

    conn.commit()
    print("✅ Created unified campaign with cross-platform mapping")


def create_shopify_orders(conn):
    """Create Shopify orders with attribution"""
    cursor = conn.cursor()

    # Create orders over last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)

    orders_created = 0

    for _ in range(150):  # 150 orders
        order_date = start_date + timedelta(days=random.randint(0, 30))
        date_id = order_date.strftime("%Y%m%d")

        # Random attribution
        attribution_source = random.choice(['google', 'meta', 'organic', 'direct'])

        google_campaign_id = None
        meta_campaign_id = None
        gclid = None
        fbclid = None
        utm_campaign = None
        attribution_confidence = 0

        if attribution_source == 'google':
            google_campaign_id = random.randint(1, 3)
            gclid = f"gclid_{random.randint(10000, 99999)}"
            utm_campaign = "summer_sale_2024"
            attribution_confidence = 100
        elif attribution_source == 'meta':
            meta_campaign_id = random.randint(1, 3)
            fbclid = f"fbclid_{random.randint(10000, 99999)}"
            utm_campaign = "summer_sale_2024"
            attribution_confidence = 100
        elif attribution_source == 'organic':
            utm_campaign = None
            attribution_confidence = 0
        else:  # direct
            attribution_confidence = 0

        # Order value
        total_price = random.uniform(50, 500)

        cursor.execute("""
            INSERT INTO fact_shopify_orders (
                order_id, customer_id, store_id, date_id,
                google_campaign_id, meta_campaign_id,
                total_price_micros, subtotal_micros, tax_micros,
                financial_status, fulfillment_status,
                line_items_count, gclid, fbclid, utm_campaign,
                attribution_model, attribution_confidence,
                order_created_at, synced_at
            ) VALUES (?, 1, 'demo-store', ?,
                     ?, ?,
                     ?, ?, ?,
                     'paid', 'fulfilled',
                     ?, ?, ?, ?,
                     'last_click', ?,
                     ?, ?)
        """, (
            f"order_{orders_created + 1}",
            date_id,
            google_campaign_id,
            meta_campaign_id,
            int(total_price * 1000000),
            int(total_price * 0.9 * 1000000),
            int(total_price * 0.1 * 1000000),
            random.randint(1, 5),
            gclid,
            fbclid,
            utm_campaign,
            attribution_confidence,
            order_date.isoformat(),
            datetime.now().isoformat()
        ))

        orders_created += 1

    conn.commit()
    print(f"✅ Created {orders_created} Shopify orders with attribution")


def update_platform_sync_times(conn):
    """Update platform last sync times"""
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE dim_platform
        SET last_sync_at = ?
        WHERE platform_name IN ('google_ads', 'meta_ads', 'shopify')
    """, (datetime.now().isoformat(),))

    conn.commit()


def main():
    """Populate warehouse with sample data"""

    print("=" * 70)
    print("POPULATING WAREHOUSE WITH SAMPLE DATA")
    print("=" * 70)

    conn = sqlite3.connect(DB_PATH)

    print("\n📊 Creating sample data...\n")

    # Create customer
    create_sample_customer(conn)

    # Create campaigns and performance
    google_campaigns = create_google_ads_campaigns(conn)
    meta_campaigns = create_meta_campaigns(conn)

    # Create unified mappings
    create_unified_campaigns(conn, google_campaigns, meta_campaigns)

    # Create orders
    create_shopify_orders(conn)

    # Update sync times
    update_platform_sync_times(conn)

    conn.close()

    print("\n" + "=" * 70)
    print("✅ SAMPLE DATA CREATED SUCCESSFULLY!")
    print("=" * 70)
    print("\n📊 Next Steps:")
    print("   1. Run: python show_warehouse_summary.py")
    print("   2. View cross-platform analytics")
    print("   3. Explore attribution tracking")
    print("\n" + "=" * 70)


if __name__ == "__main__":
    main()
