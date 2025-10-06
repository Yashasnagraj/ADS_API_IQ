"""
Populate realistic sample Google Ads performance data
Based on actual campaigns in the database
"""
import sqlite3
from datetime import datetime, timedelta
import random

conn = sqlite3.connect('google_ads_data.db')
cursor = conn.cursor()

# Get actual campaigns and keywords for ALL customers
cursor.execute('SELECT campaign_id, customer_id FROM campaigns')
campaigns = cursor.fetchall()

cursor.execute('SELECT keyword_id, campaign_id, customer_id FROM keywords')
keywords = cursor.fetchall()

print(f"Found {len(campaigns)} campaigns and {len(keywords)} keywords")

# Clear existing campaign_keywords data
cursor.execute('DELETE FROM campaign_keywords')
print("Cleared existing campaign_keywords data")

# Generate realistic performance data for last 30 days
records_created = 0
for days_ago in range(30):
    date = (datetime.now() - timedelta(days=days_ago)).strftime('%Y-%m-%d')

    # Create data for each keyword (use more keywords to cover all customers)
    for keyword_id, campaign_id, customer_id in keywords[:100]:  # Use 100 keywords to cover all customers
        # Generate realistic metrics
        impressions = random.randint(50, 500)
        clicks = int(impressions * random.uniform(0.01, 0.08))  # 1-8% CTR
        cost_micros = clicks * random.randint(5_000_000, 50_000_000)  # ₹5-₹50 per click
        conversions = clicks * random.uniform(0.01, 0.15)  # 1-15% conversion rate
        conversion_value = conversions * random.uniform(500, 5000)  # ₹500-₹5000 per conversion

        ctr = (clicks / impressions * 100) if impressions > 0 else 0
        conversion_rate = (conversions / clicks * 100) if clicks > 0 else 0
        avg_cpc_micros = (cost_micros / clicks) if clicks > 0 else 0

        cursor.execute('''
            INSERT INTO campaign_keywords (
                campaign_id, keyword_id, customer_id, date,
                clicks, impressions, cost_micros, conversions, conversion_value,
                ctr, conversion_rate, avg_cpc_micros,
                absolute_top_impression_percentage, top_impression_percentage,
                search_impression_share, search_rank_lost_impression_share
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            campaign_id, keyword_id, customer_id, date,
            clicks, impressions, cost_micros, conversions, conversion_value,
            ctr, conversion_rate, avg_cpc_micros,
            random.uniform(10, 40),  # Absolute top %
            random.uniform(40, 80),  # Top %
            random.uniform(50, 95),  # Impression share
            random.uniform(5, 50)    # Lost impression share
        ))
        records_created += 1

conn.commit()
print(f"\n[SUCCESS] Created {records_created} performance records across 30 days")

# Verify the data
cursor.execute('''
    SELECT
        SUM(clicks),
        SUM(impressions),
        SUM(cost_micros) / 1000000.0 as total_cost,
        SUM(conversions),
        SUM(conversion_value)
    FROM campaign_keywords
''')
row = cursor.fetchone()
print(f"\nTotal Metrics:")
print(f"  Clicks: {row[0]:,}")
print(f"  Impressions: {row[1]:,}")
print(f"  Cost: Rs {row[2]:,.2f}")
print(f"  Conversions: {row[3]:,.2f}")
print(f"  Revenue: Rs {row[4]:,.2f}")

conn.close()
print("\n[SUCCESS] Sample data populated successfully!")
