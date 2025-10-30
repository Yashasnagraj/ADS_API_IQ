import sqlite3

conn = sqlite3.connect(r'D:\ADS_API\marketing_warehouse.db')
cursor = conn.cursor()

# Check campaigns
cursor.execute('SELECT COUNT(*) FROM meta_campaigns WHERE customer_id = 1')
count = cursor.fetchone()[0]
print(f'Campaigns in DB: {count}')

# Sample campaigns
cursor.execute('SELECT campaign_id, name, status, daily_budget, lifetime_budget FROM meta_campaigns LIMIT 5')
campaigns = cursor.fetchall()
print('\nSample campaigns:')
for c in campaigns:
    budget = c[3] if c[3] else (c[4] if c[4] else 'N/A')
    print(f'  {c[1][:50]} - Status: {c[2]}, Budget: {budget}')

conn.close()
