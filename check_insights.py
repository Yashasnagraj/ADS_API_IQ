import sqlite3

conn = sqlite3.connect(r'D:\ADS_API\marketing_warehouse.db')
cursor = conn.cursor()

# Get total insights
cursor.execute('SELECT COUNT(*) FROM meta_insights WHERE customer_id = 1')
total = cursor.fetchone()[0]
print(f'Total Insights Records: {total}\n')

# Get summary stats
cursor.execute('''
    SELECT
        MIN(date_start) as earliest_date,
        MAX(date_start) as latest_date,
        SUM(impressions) as total_impressions,
        SUM(clicks) as total_clicks,
        SUM(spend) as total_spend,
        SUM(conversions) as total_conversions,
        SUM(purchase_value) as total_revenue
    FROM meta_insights
    WHERE customer_id = 1
''')

row = cursor.fetchone()
print('Historical Performance Summary:')
print(f'  Date Range: {row[0]} to {row[1]}')
print(f'  Total Impressions: {int(row[2]):,}')
print(f'  Total Clicks: {int(row[3]):,}')
print(f'  Total Spend: Rs {row[4]:,.2f}')
print(f'  Total Conversions: {row[5]:.1f}')
print(f'  Total Revenue: Rs {row[6]:,.2f}')

if row[4] > 0:
    roas = row[6] / row[4]
    ctr = (row[3] / row[2]) * 100 if row[2] > 0 else 0
    cpc = row[4] / row[3] if row[3] > 0 else 0
    print(f'\n  ROAS: {roas:.2f}x')
    print(f'  CTR: {ctr:.2f}%')
    print(f'  CPC: Rs {cpc:.2f}')

# Show sample records
print('\n\nSample Insight Records:')
cursor.execute('''
    SELECT date_start, campaign_id, impressions, clicks, spend, conversions
    FROM meta_insights
    WHERE customer_id = 1
    ORDER BY date_start DESC
    LIMIT 5
''')

for r in cursor.fetchall():
    print(f'  {r[0]} | Campaign: {r[1][:15]}... | Impr: {r[2]:,} | Clicks: {r[3]} | Spend: Rs{r[4]:.2f}')

conn.close()
