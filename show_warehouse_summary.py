"""
Show Marketing Warehouse Summary

Displays current warehouse status, tables, and data counts.
"""

import sys
import os
import sqlite3
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

DB_PATH = Path(__file__).parent / 'marketing_warehouse.db'

def show_summary():
    """Show warehouse summary"""

    if not DB_PATH.exists():
        print("❌ Warehouse database not found!")
        return

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 70)
    print("📊 MARKETING DATA WAREHOUSE SUMMARY")
    print("=" * 70)

    # Tables
    print("\n📋 TABLES:\n")

    cursor.execute("""
        SELECT name FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        ORDER BY
            CASE
                WHEN name LIKE 'dim_%' THEN 1
                WHEN name LIKE 'fact_%' THEN 2
                WHEN name LIKE 'map_%' THEN 3
                WHEN name LIKE 'attribution_%' THEN 4
                ELSE 5
            END,
            name
    """)

    tables = [row[0] for row in cursor.fetchall()]

    # Group by category
    dim_tables = [t for t in tables if t.startswith('dim_')]
    fact_tables = [t for t in tables if t.startswith('fact_')]
    map_tables = [t for t in tables if t.startswith('map_')]
    attr_tables = [t for t in tables if t.startswith('attribution_')]
    other_tables = [t for t in tables if t not in dim_tables + fact_tables + map_tables + attr_tables]

    print(f"  📐 Dimension Tables ({len(dim_tables)}):")
    for table in dim_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"     • {table:<35} {count:>7} records")

    print(f"\n  📊 Fact Tables ({len(fact_tables)}):")
    for table in fact_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"     • {table:<35} {count:>7} records")

    print(f"\n  🔗 Mapping Tables ({len(map_tables)}):")
    for table in map_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"     • {table:<35} {count:>7} records")

    print(f"\n  🎯 Attribution Tables ({len(attr_tables)}):")
    for table in attr_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"     • {table:<35} {count:>7} records")

    if other_tables:
        print(f"\n  📦 Other Tables ({len(other_tables)}):")
        for table in other_tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            print(f"     • {table:<35} {count:>7} records")

    # Platforms
    print("\n" + "=" * 70)
    print("🌐 PLATFORMS:")
    print("=" * 70 + "\n")

    cursor.execute("""
        SELECT platform_name, platform_category, last_sync_at
        FROM dim_platform
        ORDER BY platform_id
    """)

    for row in cursor.fetchall():
        platform, category, last_sync = row
        sync_status = last_sync if last_sync else "Never"
        print(f"  • {platform:<15} ({category:<12}) Last Sync: {sync_status}")

    # Customers
    print("\n" + "=" * 70)
    print("👥 CUSTOMERS:")
    print("=" * 70 + "\n")

    cursor.execute("""
        SELECT customer_id, customer_name,
               google_ads_customer_id, meta_business_id,
               ga4_account_id, shopify_domain
        FROM dim_customer
    """)

    customers = cursor.fetchall()

    if customers:
        for row in customers:
            cust_id, name, google_id, meta_id, ga4_id, shopify = row
            print(f"  Customer #{cust_id}: {name}")
            if google_id:
                print(f"     • Google Ads: {google_id}")
            if meta_id:
                print(f"     • Meta Ads: {meta_id}")
            if ga4_id:
                print(f"     • GA4: {ga4_id}")
            if shopify:
                print(f"     • Shopify: {shopify}")
            print()
    else:
        print("  (No customers in warehouse yet)")

    # ETL Sync Log
    print("=" * 70)
    print("🔄 RECENT ETL SYNCS:")
    print("=" * 70 + "\n")

    cursor.execute("""
        SELECT
            s.sync_id,
            p.platform_name,
            s.sync_started_at,
            s.sync_status,
            s.records_inserted + s.records_updated as total_records
        FROM etl_sync_log s
        JOIN dim_platform p ON s.platform_id = p.platform_id
        ORDER BY s.sync_id DESC
        LIMIT 10
    """)

    syncs = cursor.fetchall()

    if syncs:
        print(f"  {'ID':<5} {'Platform':<15} {'Status':<10} {'Records':<10} {'Time'}")
        print("  " + "-" * 65)
        for sync_id, platform, started, status, records in syncs:
            time_str = started[:19] if started else "N/A"
            print(f"  {sync_id:<5} {platform:<15} {status:<10} {records:<10} {time_str}")
    else:
        print("  (No ETL syncs yet)")

    # Data Summary
    print("\n" + "=" * 70)
    print("📈 DATA SUMMARY:")
    print("=" * 70 + "\n")

    # Total campaigns across platforms
    cursor.execute("SELECT COUNT(*) FROM dim_campaign_unified")
    unified_campaigns = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM dim_google_ads_campaign")
    google_campaigns = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM dim_meta_campaign")
    meta_campaigns = cursor.fetchone()[0]

    print(f"  Unified Campaigns:        {unified_campaigns:>7}")
    print(f"  Google Ads Campaigns:     {google_campaigns:>7}")
    print(f"  Meta Ads Campaigns:       {meta_campaigns:>7}")

    # Performance facts
    cursor.execute("SELECT COUNT(*) FROM fact_campaign_performance_daily")
    perf_records = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(DISTINCT date_id) FROM fact_campaign_performance_daily")
    perf_days = cursor.fetchone()[0]

    print(f"\n  Performance Records:      {perf_records:>7}")
    print(f"  Days of Data:             {perf_days:>7}")

    # Orders
    cursor.execute("SELECT COUNT(*) FROM fact_shopify_orders")
    orders = cursor.fetchone()[0]

    print(f"\n  Shopify Orders:           {orders:>7}")

    print("\n" + "=" * 70)
    print(f"📂 Database: {DB_PATH}")
    print(f"💾 Size: {DB_PATH.stat().st_size / 1024:.1f} KB")
    print("=" * 70)

    conn.close()


if __name__ == "__main__":
    show_summary()
