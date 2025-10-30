"""
Setup multi-customer database
Adds 2 new customers for testing multi-customer filtering
"""
import sqlite3
from datetime import datetime

# Connect to warehouse database
conn = sqlite3.connect(r'D:\ADS_API\marketing_warehouse.db')
cursor = conn.cursor()

# Customer 1 already exists (Emcee Sons - 1074645992720544)
# Let's add 2 more customers

customers_to_add = [
    {
        'customer_id': 2,
        'customer_name': 'TechMart Retail',
        'descriptive_name': 'TechMart Retail - E-commerce',
        'google_ads_customer_id': '2000000001',  # Example Google Ads ID
        'industry_vertical': 'Retail',
        'timezone': 'Asia/Kolkata',
        'currency': 'INR',
        'is_active': 1
    },
    {
        'customer_id': 3,
        'customer_name': 'ProServices Solutions',
        'descriptive_name': 'ProServices - B2B Services',
        'google_ads_customer_id': '3000000001',  # Example Google Ads ID
        'industry_vertical': 'Professional Services',
        'timezone': 'Asia/Kolkata',
        'currency': 'INR',
        'is_active': 1
    }
]

print("Adding customers to database...")
print("=" * 70)

for customer in customers_to_add:
    try:
        cursor.execute("""
            INSERT OR IGNORE INTO dim_customer (
                customer_id,
                customer_name,
                descriptive_name,
                google_ads_customer_id,
                industry_vertical,
                timezone,
                currency,
                is_active
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer['customer_id'],
            customer['customer_name'],
            customer['descriptive_name'],
            customer['google_ads_customer_id'],
            customer['industry_vertical'],
            customer['timezone'],
            customer['currency'],
            customer['is_active']
        ))

        if cursor.rowcount > 0:
            print(f"+ Added customer: {customer['customer_name']} (ID: {customer['customer_id']})")
        else:
            print(f"* Customer {customer['customer_name']} already exists")
    except Exception as e:
        print(f"X Error adding customer {customer['customer_name']}: {e}")

conn.commit()

# Verify customers
print("\n" + "=" * 70)
print("Current customers in database:")
print("=" * 70)

cursor.execute("""
    SELECT customer_id, customer_name, google_ads_customer_id, industry_vertical
    FROM dim_customer
    ORDER BY customer_id ASC
""")

for row in cursor.fetchall():
    print(f"ID: {row[0]} | Name: {row[1]} | Google Ads: {row[2]} | Industry: {row[3]}")

# Check what data exists for each customer
print("\n" + "=" * 70)
print("Data availability per customer:")
print("=" * 70)

for customer_id in [1, 2, 3]:
    print(f"\nCustomer ID {customer_id}:")

    # Check Meta campaigns
    cursor.execute("SELECT COUNT(*) FROM meta_campaigns WHERE customer_id = ?", (customer_id,))
    meta_count = cursor.fetchone()[0]
    print(f"  Meta Campaigns: {meta_count}")

    # Check Meta insights
    cursor.execute("SELECT COUNT(*) FROM meta_insights WHERE customer_id = ?", (customer_id,))
    meta_insights = cursor.fetchone()[0]
    print(f"  Meta Insights: {meta_insights}")

    # Check Google Ads campaigns
    cursor.execute("SELECT COUNT(*) FROM campaigns WHERE customer_id = ?", (customer_id,))
    google_campaigns = cursor.fetchone()[0]
    print(f"  Google Ads Campaigns: {google_campaigns}")

    # Check GA4 sessions
    cursor.execute("SELECT COUNT(*) FROM ga4_sessions WHERE customer_id = ?", (customer_id,))
    ga4_sessions = cursor.fetchone()[0]
    print(f"  GA4 Sessions: {ga4_sessions}")

conn.close()

print("\n" + "=" * 70)
print("✓ Customer setup complete!")
print("=" * 70)
print("\nNext steps:")
print("1. For Customer 2 & 3: Run Google Ads ETL to populate their data")
print("2. Update frontend customer dropdown to show all 3 customers")
print("3. Test customer filtering across all dashboards")
