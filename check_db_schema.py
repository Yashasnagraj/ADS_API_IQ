import sqlite3
import pandas as pd

# Connect to the database
conn = sqlite3.connect('google_ads_data.db')
cursor = conn.cursor()

# Get all table names
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("=" * 80)
print("DATABASE SCHEMA ANALYSIS")
print("=" * 80)
print(f"\nTotal tables found: {len(tables)}\n")

# For each table, get column information
for table in tables:
    table_name = table[0]
    print(f"\n{'='*60}")
    print(f"TABLE: {table_name}")
    print(f"{'='*60}")

    # Get column info
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = cursor.fetchall()

    print(f"Columns ({len(columns)}):")
    for col in columns:
        col_name = col[1]
        col_type = col[2]
        is_null = "NULL" if col[3] == 0 else "NOT NULL"
        is_pk = " [PRIMARY KEY]" if col[5] == 1 else ""
        print(f"  - {col_name}: {col_type} {is_null}{is_pk}")

    # Get row count
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    row_count = cursor.fetchone()[0]
    print(f"\nRow count: {row_count}")

    # Show sample data if exists
    if row_count > 0:
        print(f"\nSample data (first 3 rows):")
        query = f"SELECT * FROM {table_name} LIMIT 3"
        df = pd.read_sql_query(query, conn)
        print(df.to_string())

conn.close()

print("\n" + "=" * 80)
print("MISSING FIELDS ANALYSIS")
print("=" * 80)

print("""
Common fields that might be missing based on Google Ads API:

CAMPAIGNS table should have:
- campaign_id, campaign_name, status, budget, bidding_strategy
- impressions, clicks, cost, conversions, ctr, cpc, conversion_rate

KEYWORDS table should have:
- keyword_id, keyword_text, campaign_id, ad_group_id
- match_type, quality_score, bid, status
- impressions, clicks, cost, conversions, ctr, cpc
- avg_position, conversion_rate

AD_GROUPS table should have:
- ad_group_id, ad_group_name, campaign_id, status
- impressions, clicks, cost, conversions, ctr, cpc

SEARCH_TERMS table should have:
- search_term, keyword_id, campaign_id, ad_group_id
- impressions, clicks, cost, conversions, ctr
- match_type, added_as_keyword

ADS table should have:
- ad_id, ad_group_id, headline1, headline2, headline3
- description1, description2, final_url, status
- impressions, clicks, cost, conversions
""")