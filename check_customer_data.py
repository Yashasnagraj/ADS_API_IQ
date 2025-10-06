import sqlite3

conn = sqlite3.connect('google_ads_data.db')
cursor = conn.cursor()

cursor.execute('''
    SELECT customer_id, COUNT(*), SUM(clicks), SUM(cost_micros)/1000000
    FROM campaign_keywords
    GROUP BY customer_id
''')

print('Customer Data Summary:')
for row in cursor.fetchall():
    print(f'  Customer {row[0]}: {row[1]} records, {row[2]} clicks, Rs {row[3]:.2f} cost')

# Check all customers
cursor.execute('SELECT DISTINCT customer_id FROM campaigns')
print('\nAll customers in campaigns table:')
for row in cursor.fetchall():
    print(f'  Customer ID: {row[0]}')

conn.close()
