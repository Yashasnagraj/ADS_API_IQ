"""
Test unified dashboard data
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# Test Meta insights
print("=" * 70)
print("META ADS INSIGHTS")
print("=" * 70)
response = requests.get(f"{BASE_URL}/warehouse/meta/insights/summary", params={
    "customer_id": 1,
    "date_range": "last_30d"
})
meta_data = response.json()
print(json.dumps(meta_data, indent=2))

print("\n" + "=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Meta Ads Spend: Rs {meta_data.get('spend', 0):,.2f}")
print(f"Meta Ads Conversions: {meta_data.get('conversions', 0)}")
print(f"Meta Ads ROAS: {meta_data.get('roas', 0):.2f}x")
print(f"Meta Ads CPC: Rs {meta_data.get('cpc', 0):.2f}")
print(f"Meta Ads CTR: {meta_data.get('ctr', 0):.2f}%")
print(f"\nDate Range: {meta_data.get('date_start')} to {meta_data.get('date_stop')}")
print(f"Impressions: {meta_data.get('impressions', 0):,}")
print(f"Clicks: {meta_data.get('clicks', 0):,}")
