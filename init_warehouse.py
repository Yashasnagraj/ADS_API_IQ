"""
Initialize Multi-Platform Marketing Data Warehouse

This script:
1. Creates the new marketing_warehouse.db database
2. Executes the schema SQL to create all tables
3. Populates the date dimension for 3 years (past 1 year + future 2 years)
4. Inserts default platform records
5. Validates the schema

Usage:
    python init_warehouse.py [--force]

    --force: Drop existing database and recreate (WARNING: deletes all data)
"""

import sys
import os
import sqlite3
import argparse
from pathlib import Path
from datetime import datetime, timedelta
import calendar

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')  # Set console to UTF-8
    sys.stdout.reconfigure(encoding='utf-8')

# Paths
PROJECT_ROOT = Path(__file__).parent
SCHEMA_FILE = PROJECT_ROOT / "warehouse_schema.sql"
DB_FILE = PROJECT_ROOT / "marketing_warehouse.db"


def create_database(force=False):
    """Create the warehouse database"""
    if DB_FILE.exists():
        if not force:
            print(f"❌ Database already exists: {DB_FILE}")
            print("   Use --force to recreate (WARNING: deletes all data)")
            return False
        else:
            print(f"⚠️  Removing existing database: {DB_FILE}")
            DB_FILE.unlink()

    print(f"✅ Creating new database: {DB_FILE}")
    return True


def execute_schema(conn):
    """Execute the schema SQL file"""
    print(f"\n📄 Reading schema from: {SCHEMA_FILE}")

    if not SCHEMA_FILE.exists():
        print(f"❌ Schema file not found: {SCHEMA_FILE}")
        return False

    with open(SCHEMA_FILE, 'r', encoding='utf-8') as f:
        schema_sql = f.read()

    print("📊 Creating tables...")

    try:
        # Execute schema (split by semicolon for multiple statements)
        cursor = conn.cursor()
        cursor.executescript(schema_sql)
        conn.commit()
        print("✅ Schema created successfully")
        return True
    except Exception as e:
        print(f"❌ Error creating schema: {e}")
        return False


def populate_date_dimension(conn):
    """Populate date dimension table"""
    print("\n📅 Populating date dimension...")

    cursor = conn.cursor()

    # Date range: 1 year ago to 2 years in future
    start_date = datetime.now().date() - timedelta(days=365)
    end_date = datetime.now().date() + timedelta(days=730)  # 2 years

    current_date = start_date
    records_inserted = 0

    # US holidays (basic set - can expand)
    us_holidays = {
        (1, 1): "New Year's Day",
        (7, 4): "Independence Day",
        (12, 25): "Christmas Day",
        (11, 24): "Black Friday (approx)",  # 4th Thursday of November
        (11, 25): "Cyber Monday (approx)"
    }

    while current_date <= end_date:
        date_id = current_date.strftime("%Y%m%d")
        year = current_date.year
        quarter = (current_date.month - 1) // 3 + 1
        month = current_date.month
        week = current_date.isocalendar()[1]
        day_of_month = current_date.day
        day_of_week = current_date.weekday()  # 0=Monday, 6=Sunday
        month_name = calendar.month_name[month]
        day_name = calendar.day_name[day_of_week]

        # Flags
        is_weekend = 1 if day_of_week in [5, 6] else 0  # Saturday=5, Sunday=6
        is_holiday = 1 if (month, day_of_month) in us_holidays else 0

        # Fiscal year (assuming Jan start)
        fiscal_year = year
        fiscal_quarter = quarter

        try:
            cursor.execute("""
                INSERT INTO dim_date (
                    date_id, full_date, year, quarter, month, week,
                    day_of_month, day_of_week, month_name, day_name,
                    is_weekend, is_holiday, fiscal_year, fiscal_quarter
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                date_id, current_date.isoformat(), year, quarter, month, week,
                day_of_month, day_of_week, month_name, day_name,
                is_weekend, is_holiday, fiscal_year, fiscal_quarter
            ))
            records_inserted += 1
        except sqlite3.IntegrityError:
            # Date already exists, skip
            pass

        current_date += timedelta(days=1)

    conn.commit()
    print(f"✅ Inserted {records_inserted} date records ({start_date} to {end_date})")


def validate_schema(conn):
    """Validate the schema was created correctly"""
    print("\n🔍 Validating schema...")

    cursor = conn.cursor()

    # Check tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")
    tables = [row[0] for row in cursor.fetchall()]

    expected_tables = [
        'dim_customer',
        'dim_platform',
        'dim_date',
        'dim_campaign_unified',
        'dim_google_ads_campaign',
        'dim_meta_campaign',
        'dim_ga4_source_medium',
        'dim_ad_group',
        'dim_keyword',
        'fact_campaign_performance_daily',
        'fact_keyword_performance_daily',
        'fact_shopify_orders',
        'map_campaign_cross_platform',
        'map_account_platform',
        'map_customer_identifiers',
        'attribution_touchpoints',
        'etl_sync_log'
    ]

    missing_tables = [t for t in expected_tables if t not in tables]

    if missing_tables:
        print(f"❌ Missing tables: {', '.join(missing_tables)}")
        return False

    print(f"✅ All {len(expected_tables)} expected tables created")

    # Check platform pre-population
    cursor.execute("SELECT platform_name FROM dim_platform ORDER BY platform_id")
    platforms = [row[0] for row in cursor.fetchall()]

    if platforms == ['google_ads', 'meta_ads', 'ga4', 'shopify']:
        print(f"✅ Platforms pre-populated: {', '.join(platforms)}")
    else:
        print(f"⚠️  Unexpected platforms: {', '.join(platforms)}")

    # Check date dimension
    cursor.execute("SELECT COUNT(*) FROM dim_date")
    date_count = cursor.fetchone()[0]
    print(f"✅ Date dimension populated with {date_count} records")

    # Check views
    cursor.execute("SELECT name FROM sqlite_master WHERE type='view' ORDER BY name")
    views = [row[0] for row in cursor.fetchall()]
    print(f"✅ Views created: {', '.join(views)}")

    return True


def print_summary(conn):
    """Print summary of warehouse structure"""
    print("\n" + "=" * 70)
    print("📊 WAREHOUSE SUMMARY")
    print("=" * 70)

    cursor = conn.cursor()

    # Count tables by category
    cursor.execute("""
        SELECT
            CASE
                WHEN name LIKE 'dim_%' THEN 'Dimension Tables'
                WHEN name LIKE 'fact_%' THEN 'Fact Tables'
                WHEN name LIKE 'map_%' THEN 'Mapping Tables'
                WHEN name LIKE 'attribution_%' THEN 'Attribution Tables'
                ELSE 'Other Tables'
            END as category,
            COUNT(*) as count
        FROM sqlite_master
        WHERE type='table' AND name NOT LIKE 'sqlite_%'
        GROUP BY category
        ORDER BY category
    """)

    print("\nTable Categories:")
    for row in cursor.fetchall():
        print(f"  {row[0]:<25} {row[1]:>3} tables")

    # Total records in key tables
    print("\nCurrent Record Counts:")
    for table in ['dim_customer', 'dim_platform', 'dim_date',
                  'fact_campaign_performance_daily', 'fact_shopify_orders']:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        print(f"  {table:<35} {count:>7} records")

    print("\n" + "=" * 70)
    print("\n📍 Next Steps:")
    print("   1. Run ETL scripts to populate dimension and fact tables")
    print("   2. Set up cross-platform campaign mapping")
    print("   3. Configure attribution engine")
    print("   4. Update API to query new warehouse")
    print(f"\n📂 Database location: {DB_FILE}")
    print("=" * 70)


def main():
    """Main initialization flow"""
    parser = argparse.ArgumentParser(description='Initialize Marketing Data Warehouse')
    parser.add_argument('--force', action='store_true',
                       help='Force recreation (deletes existing database)')
    args = parser.parse_args()

    print("=" * 70)
    print("MARKETING DATA WAREHOUSE INITIALIZATION")
    print("=" * 70)

    # Step 1: Create database
    if not create_database(force=args.force):
        if args.force:
            print("\n❌ Failed to create database")
            return
        else:
            print("\n💡 Run with --force to recreate the database")
            return

    # Step 2: Connect and create schema
    try:
        conn = sqlite3.connect(DB_FILE)
        print("✅ Connected to database")

        # Step 3: Execute schema
        if not execute_schema(conn):
            print("\n❌ Failed to create schema")
            return

        # Step 4: Populate date dimension
        populate_date_dimension(conn)

        # Step 5: Validate
        if not validate_schema(conn):
            print("\n⚠️  Schema validation issues detected")

        # Step 6: Print summary
        print_summary(conn)

        conn.close()
        print("\n✅ Warehouse initialization complete!")

    except Exception as e:
        print(f"\n❌ Error during initialization: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
