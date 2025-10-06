import sqlite3

conn = sqlite3.connect('google_ads_data.db')
cursor = conn.cursor()

# Check campaigns
cursor.execute('SELECT COUNT(*) FROM campaigns')
print(f'Total campaigns: {cursor.fetchone()[0]}')

# Check keywords
cursor.execute('SELECT COUNT(*) FROM keywords')
print(f'Total keywords: {cursor.fetchone()[0]}')

# Check campaign_keywords
cursor.execute('SELECT COUNT(*) FROM campaign_keywords')
print(f'Total campaign_keywords: {cursor.fetchone()[0]}')

# Sample campaigns
cursor.execute('SELECT campaign_id, campaign_name, status, customer_id FROM campaigns LIMIT 5')
print('\nSample campaigns:')
for row in cursor.fetchall():
    print(f'  ID: {row[0]}, Name: {row[1]}, Status: {row[2]}, Customer: {row[3]}')

# Check if data needs to be refreshed from ETL
print('\n--- Checking if ETL needs to run ---')
cursor.execute('SELECT * FROM campaign_keywords LIMIT 1')
row = cursor.fetchone()
if row:
    print(f'Sample campaign_keywords record: {row}')

conn.close()
