import sqlite3

conn = sqlite3.connect('D:/ADS_API/marketing_warehouse.db')
cursor = conn.cursor()

cursor.execute('SELECT customer_id, customer_name, google_ads_customer_id FROM dim_customer')

print('Internal ID | Customer Name              | Google Ads ID')
print('-' * 65)
for row in cursor.fetchall():
    print(f'{row[0]:<11} | {row[1]:<26} | {row[2]}')

conn.close()
