import sqlite3

conn = sqlite3.connect('D:/ADS_API/marketing_warehouse.db')
cursor = conn.cursor()

print("=== dim_customer schema ===")
cursor.execute('PRAGMA table_info(dim_customer)')
for row in cursor.fetchall():
    print(f'{row[1]}: {row[2]}')

print("\n=== dim_customer data ===")
cursor.execute('SELECT * FROM dim_customer')
columns = [desc[0] for desc in cursor.description]
print(' | '.join(columns))
print('-' * 80)
for row in cursor.fetchall():
    print(' | '.join(str(x) if x is not None else 'NULL' for x in row))

print("\n=== Check for GA4 tables ===")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%ga4%'")
ga4_tables = cursor.fetchall()
if ga4_tables:
    for table in ga4_tables:
        cursor.execute(f'SELECT COUNT(*) FROM {table[0]}')
        count = cursor.fetchone()[0]
        print(f'{table[0]}: {count} records')
else:
    print('No GA4 tables found')

conn.close()
