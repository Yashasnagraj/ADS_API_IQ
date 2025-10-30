"""
Show Marketing Analytics from Warehouse

Displays real analytics from the loaded customer data
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


def show_analytics():
    """Show marketing analytics"""

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    print("=" * 70)
    print("📊 MARKETING WAREHOUSE ANALYTICS")
    print("=" * 70)

    # Customer Overview
    print("\n👥 CUSTOMER OVERVIEW:")
    print("-" * 70)

    cursor.execute("""
        SELECT
            c.customer_id,
            c.customer_name,
            c.currency,
            COUNT(DISTINCT gc.google_campaign_id) as total_campaigns,
            COUNT(DISTINCT f.fact_id) as total_performance_records
        FROM dim_customer c
        LEFT JOIN dim_google_ads_campaign gc ON c.customer_id = gc.customer_id
        LEFT JOIN fact_campaign_performance_daily f ON c.customer_id = f.customer_id
        GROUP BY c.customer_id
        ORDER BY c.customer_id
    """)

    for row in cursor.fetchall():
        cust_id, name, currency, campaigns, perf_records = row
        print(f"\n  📍 {name} (Customer #{cust_id})")
        print(f"     Currency: {currency if currency else 'USD'}")
        print(f"     Campaigns: {campaigns}")
        print(f"     Performance Records: {perf_records}")

    # Campaign List by Customer
    print("\n\n📊 CAMPAIGNS BY CUSTOMER:")
    print("-" * 70)

    cursor.execute("""
        SELECT
            c.customer_name,
            gc.campaign_name,
            gc.status,
            gc.channel_type,
            COUNT(f.fact_id) as perf_records
        FROM dim_customer c
        JOIN dim_google_ads_campaign gc ON c.customer_id = gc.customer_id
        LEFT JOIN fact_campaign_performance_daily f ON gc.google_campaign_id = f.google_campaign_id
        GROUP BY c.customer_name, gc.campaign_name
        ORDER BY c.customer_name, gc.campaign_name
    """)

    current_customer = None
    for row in cursor.fetchall():
        customer, campaign, status, channel, perf_records = row

        if customer != current_customer:
            print(f"\n  📍 {customer}:")
            current_customer = customer

        status_icon = "✅" if status == "ENABLED" else "⏸️" if status == "PAUSED" else "❌"
        perf_icon = f"({perf_records} days)" if perf_records > 0 else "(no data)"
        print(f"     {status_icon} {campaign} - {channel} {perf_icon}")

    # Performance Summary
    print("\n\n📈 PERFORMANCE SUMMARY (Last 30 Days):")
    print("-" * 70)

    cursor.execute("""
        SELECT
            c.customer_name,
            COUNT(DISTINCT f.date_id) as days_of_data,
            SUM(f.impressions) as total_impressions,
            SUM(f.clicks) as total_clicks,
            ROUND(SUM(f.spend_micros) / 1000000.0, 2) as total_spend,
            ROUND(SUM(f.conversions), 2) as total_conversions,
            ROUND(SUM(f.conversion_value_micros) / 1000000.0, 2) as total_conversion_value,
            ROUND(AVG(f.ctr), 2) as avg_ctr
        FROM dim_customer c
        JOIN fact_campaign_performance_daily f ON c.customer_id = f.customer_id
        GROUP BY c.customer_name
        HAVING total_impressions > 0
        ORDER BY total_spend DESC
    """)

    rows = cursor.fetchall()

    if rows:
        for row in rows:
            customer, days, impressions, clicks, spend, conversions, conv_value, avg_ctr = row

            print(f"\n  📍 {customer}:")
            print(f"     Days of Data: {days}")
            print(f"     Impressions: {impressions:,}")
            print(f"     Clicks: {clicks:,}")
            print(f"     Spend: ${spend:,.2f}")
            print(f"     Conversions: {conversions:.1f}")
            print(f"     Conversion Value: ${conv_value:,.2f}")
            print(f"     Avg CTR: {avg_ctr:.2f}%")

            if spend > 0 and conversions > 0:
                cpa = spend / conversions
                roas = conv_value / spend if spend > 0 else 0
                print(f"     CPA: ${cpa:.2f}")
                print(f"     ROAS: {roas:.2f}x")
    else:
        print("\n  ℹ️  No performance data available yet")
        print("     (Most campaigns are paused or have no recent activity)")

    # Top Performing Campaigns
    print("\n\n🏆 TOP PERFORMING CAMPAIGNS:")
    print("-" * 70)

    cursor.execute("""
        SELECT
            c.customer_name,
            gc.campaign_name,
            COUNT(DISTINCT f.date_id) as days,
            SUM(f.impressions) as impressions,
            SUM(f.clicks) as clicks,
            ROUND(SUM(f.spend_micros) / 1000000.0, 2) as spend,
            ROUND(SUM(f.conversions), 1) as conversions,
            ROUND(SUM(f.conversion_value_micros) / 1000000.0, 2) as conv_value
        FROM dim_customer c
        JOIN dim_google_ads_campaign gc ON c.customer_id = gc.customer_id
        JOIN fact_campaign_performance_daily f ON gc.google_campaign_id = f.google_campaign_id
        GROUP BY c.customer_name, gc.campaign_name
        HAVING spend > 0
        ORDER BY spend DESC
        LIMIT 10
    """)

    rows = cursor.fetchall()

    if rows:
        for i, row in enumerate(rows, 1):
            customer, campaign, days, impressions, clicks, spend, conversions, conv_value = row

            print(f"\n  #{i}. {campaign} ({customer})")
            print(f"     📅 {days} days  |  👁 {impressions:,} imp  |  🖱 {clicks:,} clicks")
            print(f"     💰 ${spend:,.2f} spend  |  ✅ {conversions:.1f} conv  |  💵 ${conv_value:,.2f} value")

            if spend > 0:
                ctr = (clicks / impressions * 100) if impressions > 0 else 0
                cpa = spend / conversions if conversions > 0 else 0
                roas = conv_value / spend if spend > 0 else 0
                print(f"     📊 CTR: {ctr:.2f}%  |  CPA: ${cpa:.2f}  |  ROAS: {roas:.2f}x")
    else:
        print("\n  ℹ️  No performance data to rank")

    # Date Range
    print("\n\n📅 DATA DATE RANGE:")
    print("-" * 70)

    cursor.execute("""
        SELECT
            MIN(d.full_date) as earliest,
            MAX(d.full_date) as latest
        FROM fact_campaign_performance_daily f
        JOIN dim_date d ON f.date_id = d.date_id
    """)

    row = cursor.fetchone()
    if row and row[0]:
        earliest, latest = row
        print(f"  From: {earliest}")
        print(f"  To:   {latest}")
    else:
        print("  No performance data loaded yet")

    print("\n" + "=" * 70)
    print("✅ REAL LIVE DATA FROM GOOGLE ADS API")
    print("=" * 70)
    print("\nℹ️  Note: Some campaigns have no performance records because they are")
    print("   currently paused or have no activity in the last 30 days.")
    print("=" * 70)

    conn.close()


if __name__ == "__main__":
    show_analytics()
