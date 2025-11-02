"""
Check what data is actually in the warehouse for a sample campaign
"""
import sqlite3
import json

# Connect to database
conn = sqlite3.connect('marketing_warehouse.db')
conn.row_factory = sqlite3.Row  # This enables column access by name
cursor = conn.cursor()

# Get a sample campaign's data
print("=== Sample Campaign Data ===\n")
cursor.execute("""
    SELECT c.campaign_id, c.campaign_name, c.status,
           p.*
    FROM dim_campaign c
    LEFT JOIN fact_campaign_performance_daily p ON c.campaign_id = p.campaign_id
    WHERE c.customer_id = 1
    LIMIT 1
""")

row = cursor.fetchone()
if row:
    print("Available columns:")
    for key in row.keys():
        print(f"  {key}: {row[key]}")
else:
    print("No data found")

# Check what the warehouse_client fetch_campaigns returns
print("\n=== Testing WarehouseClient ===\n")
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "google-ads-multiagent" / "adk" / "orchestration_agent" / "sub_agents" / "data_agent"))

from warehouse_client import WarehouseClient

client = WarehouseClient()
result = client.fetch_campaigns(customer_id=1, limit=1)

if result.get("campaigns"):
    print("First campaign returned by fetch_campaigns:")
    print(json.dumps(result["campaigns"][0], indent=2))
else:
    print("No campaigns returned")

conn.close()
