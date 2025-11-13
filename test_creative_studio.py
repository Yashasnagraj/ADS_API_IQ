#!/usr/bin/env python3
"""Test Creative Studio endpoints"""
import sys
import os
from pathlib import Path
import sqlite3

# Path to marketing warehouse database
WAREHOUSE_DB = Path(__file__).parent / "marketing_warehouse.db"

def get_warehouse_connection():
    """Get connection to warehouse database"""
    if not WAREHOUSE_DB.exists():
        raise Exception(f"Warehouse database not found at {WAREHOUSE_DB}")

    conn = sqlite3.connect(WAREHOUSE_DB)
    conn.row_factory = sqlite3.Row
    return conn

print("Testing database connection and query...")

try:
    conn = get_warehouse_connection()
    cursor = conn.cursor()

    # Test the top_performers query
    query = """
        SELECT
            k.keyword_text,
            k.match_type,
            AVG(f.ctr) as avg_ctr,
            AVG(f.conversions) as avg_conversions,
            SUM(f.impressions) as total_impressions
        FROM fact_keyword_performance_daily f
        JOIN dim_keyword k ON f.keyword_id = k.keyword_id
        WHERE k.customer_id = ?
        AND f.impressions > 50
        GROUP BY k.keyword_text, k.match_type
        ORDER BY avg_ctr DESC
        LIMIT ?
    """

    cursor.execute(query, (1, 5))
    keywords = cursor.fetchall()

    print(f"SUCCESS: Found {len(keywords)} keywords")
    for kw in keywords:
        print(f"  - {kw['keyword_text']}: CTR={kw['avg_ctr']:.2f}%")

    conn.close()

except Exception as e:
    print(f"ERROR: {e}")
    import traceback
    traceback.print_exc()
