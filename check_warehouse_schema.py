"""
Check warehouse database schema and sample data
"""
import sqlite3
import json
import sys
from pathlib import Path

# Connect to database
conn = sqlite3.connect('marketing_warehouse.db')
conn.row_factory = sqlite3.Row
cursor = conn.cursor()

# List all tables
print("=== Database Tables ===\n")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
tables = cursor.fetchall()
for table in tables:
    print(f"  - {table['name']}")

# Test WarehouseClient directly
print("\n=== Testing WarehouseClient.fetch_campaigns() ===\n")
sys.path.insert(0, str(Path(__file__).parent / "google-ads-multiagent" / "adk" / "orchestration_agent" / "sub_agents" / "data_agent"))

from warehouse_client import WarehouseClient

client = WarehouseClient()
result = client.fetch_campaigns(customer_id=1, limit=1)

if result.get("campaigns"):
    campaign = result["campaigns"][0]
    print("Sample campaign data structure:")
    print(json.dumps(campaign, indent=2, default=str))

    print("\n=== Checking for CTR and Cost ===")
    print(f"  CTR: {campaign.get('ctr', 'NOT FOUND')}")
    print(f"  Cost: {campaign.get('cost', 'NOT FOUND')}")
    print(f"  Clicks: {campaign.get('clicks', 'NOT FOUND')}")
    print(f"  Impressions: {campaign.get('impressions', 'NOT FOUND')}")
else:
    print("No campaigns returned")
    print(f"Result: {result}")

conn.close()
