"""
Test WarehouseClient customer lookup
"""
import sys
from pathlib import Path

# Add paths
sys.path.insert(0, str(Path(__file__).parent / "google-ads-multiagent" / "adk" / "orchestration_agent" / "sub_agents" / "data_agent"))

from warehouse_client import WarehouseClient

# Initialize client
print("Initializing WarehouseClient...")
client = WarehouseClient()

# Get customers
print("\nFetching customers...")
customers = client.get_customers()

print(f"\nFound {len(customers)} customers:")
for c in customers:
    print(f"  - ID: {c['customer_id']}, Name: {c['customer_name']}")

# Test lookup function
def get_customer_info(customer_id: str):
    """Get customer name from ID"""
    customers = client.get_customers()
    for c in customers:
        if str(c['customer_id']) == str(customer_id):
            return {
                'customer_id': c['customer_id'],
                'customer_name': c['customer_name']
            }
    return None

# Test lookups
print("\nTesting customer lookups:")
for customer_id in ["1", "2", "3"]:
    info = get_customer_info(customer_id)
    if info:
        print(f"  Customer {customer_id}: {info['customer_name']}")
    else:
        print(f"  Customer {customer_id}: NOT FOUND")

# Test fetch_campaigns
print("\nTesting fetch_campaigns with customer_id:")
result = client.fetch_campaigns(customer_id=1)
if "error" in result:
    print(f"  Error: {result['error']}")
else:
    campaigns = result.get("campaigns", [])
    print(f"  Found {len(campaigns)} campaigns for customer 1")
    if campaigns:
        print(f"  First campaign: {campaigns[0].get('name', 'Unknown')}")
