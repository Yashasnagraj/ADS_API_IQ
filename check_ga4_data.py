import sqlite3

conn = sqlite3.connect('D:/ADS_API/marketing_warehouse.db')
cursor = conn.cursor()

# Check customer GA4 configuration
print("=== CUSTOMER GA4 CONFIGURATION ===")
cursor.execute('SELECT customer_id, customer_name, google_ads_customer_id, ga4_property_id, ga4_account_id FROM dim_customer')
print('Customer ID | Name                       | Google Ads ID  | GA4 Property | GA4 Account')
print('-' * 100)
for row in cursor.fetchall():
    print(f'{row[0]:<11} | {row[1]:<26} | {row[2]:<14} | {row[3] or "None":<12} | {row[4] or "None"}')

# Check if there's any GA4 data in fact tables
print("\n=== GA4 DATA IN WAREHOUSE ===")

cursor.execute('SELECT COUNT(*) FROM fact_ga4_sessions')
ga4_sessions = cursor.fetchone()[0]
print(f'GA4 Sessions Records: {ga4_sessions}')

if ga4_sessions > 0:
    cursor.execute('SELECT customer_id, COUNT(*) FROM fact_ga4_sessions GROUP BY customer_id')
    print('\nGA4 Sessions by Customer:')
    for row in cursor.fetchall():
        print(f'  Customer {row[0]}: {row[1]} records')

# Check GA4 events
try:
    cursor.execute('SELECT COUNT(*) FROM fact_ga4_events')
    ga4_events = cursor.fetchone()[0]
    print(f'\nGA4 Events Records: {ga4_events}')
except:
    print('\nfact_ga4_events table not found')

conn.close()
