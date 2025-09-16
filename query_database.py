#!/usr/bin/env python3
"""
Query the Google Ads SQLite database
"""

import sqlite3
import pandas as pd

def query_database():
    """Query and display database contents."""
    conn = sqlite3.connect("google_ads_data.db")

    print("=" * 80)
    print("GOOGLE ADS DATABASE SUMMARY")
    print("=" * 80)

    # Get table info
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()

    print("\nTables in database:")
    for table in tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
        count = cursor.fetchone()[0]
        print(f"  - {table[0]}: {count} rows")

    # Show sample data from each table with data
    print("\n" + "=" * 80)
    print("SAMPLE DATA")
    print("=" * 80)

    # Keywords sample
    print("\n1. TOP KEYWORDS BY IMPRESSIONS:")
    query = """
        SELECT
            keyword_text,
            match_type,
            quality_score,
            status,
            campaign_id,
            ad_group_id
        FROM keywords
        WHERE keyword_text IS NOT NULL
        LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string())

    # Campaign-Keywords Performance
    print("\n2. KEYWORD PERFORMANCE METRICS:")
    query = """
        SELECT
            k.keyword_text,
            ck.clicks,
            ck.impressions,
            ROUND(ck.cost_micros / 1000000.0, 2) as cost,
            ROUND(ck.ctr, 4) as ctr,
            ck.conversions,
            ROUND(ck.conversion_rate, 4) as conv_rate
        FROM campaign_keywords ck
        JOIN keywords k ON ck.keyword_id = k.keyword_id
        WHERE ck.impressions > 0
        ORDER BY ck.impressions DESC
        LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string())

    # Search Terms
    print("\n3. TOP SEARCH TERMS:")
    query = """
        SELECT
            search_term,
            keyword_text,
            clicks,
            impressions,
            ROUND(cost_micros / 1000000.0, 2) as cost,
            conversions
        FROM search_terms
        WHERE impressions > 0
        ORDER BY impressions DESC
        LIMIT 10
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string())

    # Campaign hierarchy
    print("\n4. CAMPAIGN HIERARCHY:")
    query = """
        SELECT
            ag.customer_id,
            ag.campaign_id,
            ag.ad_group_id,
            ag.ad_group_name,
            ag.status,
            COUNT(k.keyword_id) as keyword_count
        FROM ad_groups ag
        LEFT JOIN keywords k ON ag.ad_group_id = k.ad_group_id
        GROUP BY ag.customer_id, ag.campaign_id, ag.ad_group_id, ag.ad_group_name, ag.status
        ORDER BY ag.customer_id, ag.campaign_id
    """
    df = pd.read_sql_query(query, conn)
    print(df.to_string())

    # ML Features readiness
    print("\n5. ML FEATURES TABLE:")
    cursor.execute("SELECT COUNT(*) FROM ml_features")
    count = cursor.fetchone()[0]
    if count > 0:
        query = "SELECT * FROM ml_features LIMIT 5"
        df = pd.read_sql_query(query, conn)
        print(df.to_string())
    else:
        print("  No ML features generated yet. Need campaign data to join with keywords.")

    conn.close()

    print("\n" + "=" * 80)
    print("You can query this database using SQLite3:")
    print("  sqlite3 google_ads_data.db")
    print("  .tables  -- Show all tables")
    print("  .schema  -- Show table schemas")
    print("  SELECT * FROM keywords LIMIT 10;")
    print("=" * 80)

if __name__ == "__main__":
    query_database()