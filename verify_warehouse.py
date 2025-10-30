import sqlite3

conn = sqlite3.connect('D:/ADS_API/marketing_warehouse.db')
cursor = conn.cursor()

# Check keyword performance records
cursor.execute('SELECT COUNT(*) FROM fact_keyword_performance_daily')
print(f'Keyword performance records: {cursor.fetchone()[0]}')

# Check ENABLED campaigns with keywords
cursor.execute('''
    SELECT c.campaign_name, c.status, COUNT(k.keyword_id) as keyword_count
    FROM dim_google_ads_campaign c
    LEFT JOIN dim_keyword k ON c.customer_id = k.customer_id
        AND c.google_campaign_id = k.google_campaign_id
    WHERE c.status = 'ENABLED'
    GROUP BY c.campaign_name, c.status
    ORDER BY keyword_count DESC
''')
print('\nENABLED campaigns with keywords:')
for row in cursor.fetchall():
    print(f'  {row[0]}: {row[2]} keywords')

# Summary of all data loaded
print('\n=== WAREHOUSE DATA SUMMARY ===')
cursor.execute('SELECT COUNT(*) FROM dim_customer')
print(f'Customers: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM dim_google_ads_campaign')
print(f'Campaigns: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM dim_ad_group')
print(f'Ad Groups: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM dim_keyword')
print(f'Keywords: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM fact_campaign_performance_daily')
print(f'Campaign Performance Records: {cursor.fetchone()[0]}')

cursor.execute('SELECT COUNT(*) FROM fact_keyword_performance_daily')
print(f'Keyword Performance Records: {cursor.fetchone()[0]}')

conn.close()
