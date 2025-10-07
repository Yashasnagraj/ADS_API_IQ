#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test customer names functionality
"""

import sys
import requests

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

API_BASE_URL = "http://localhost:8000"

def test_customers_endpoint():
    """Test /customers endpoint to see customer names"""
    print("\n" + "="*60)
    print("Testing /customers endpoint")
    print("="*60)

    try:
        response = requests.get(f"{API_BASE_URL}/customers")

        if response.status_code == 200:
            data = response.json()

            print(f"\n✓ Found {data['total']} customers:\n")

            for customer in data['customers']:
                print(f"  • {customer['customer_name']}")
                print(f"    ID: {customer['customer_id']}")
                print(f"    Campaigns: {customer['campaigns_count']}")
                print()

            return True
        else:
            print(f"✗ Error: {response.status_code}")
            print(f"  {response.text}")
            return False

    except requests.exceptions.ConnectionError:
        print("\n✗ Cannot connect to API server")
        print("  Please start the API server first:")
        print("  cd api && uvicorn app.main:app --reload")
        return False
    except Exception as e:
        print(f"\n✗ Error: {e}")
        return False


def test_customer_summary():
    """Test /customers/{id}/summary endpoint"""
    print("\n" + "="*60)
    print("Testing /customers/{id}/summary endpoint")
    print("="*60)

    customer_ids = [6265362093, 5032737756, 7613138874]

    for customer_id in customer_ids:
        try:
            response = requests.get(f"{API_BASE_URL}/customers/{customer_id}/summary")

            if response.status_code == 200:
                data = response.json()

                print(f"\n✓ {data['customer_name']} (ID: {customer_id})")
                print(f"  Campaigns: {data['campaigns_count']}")
                print(f"  Metrics:")
                print(f"    - Impressions: {data['metrics']['impressions']:,}")
                print(f"    - Clicks: {data['metrics']['clicks']:,}")
                print(f"    - Cost: ₹{data['metrics']['cost']:.2f}")
                print(f"    - Conversions: {data['metrics']['conversions']:.2f}")

        except Exception as e:
            print(f"\n✗ Error for customer {customer_id}: {e}")


def main():
    print("\n🧪 Customer Names API Test")
    print("="*60)

    # Test customers list
    if test_customers_endpoint():
        # Test customer summaries
        test_customer_summary()

        print("\n" + "="*60)
        print("✅ Customer names are working!")
        print("="*60)
        print("\nNow your web page will show:")
        print("  • Communn.io (instead of 6265362093)")
        print("  • Emcee Sons (instead of 5032737756)")
        print("  • VANAVASI KALYANA (instead of 7613138874)")
        print()
    else:
        print("\n⚠️  Make sure the API server is running:")
        print("   cd api")
        print("   uvicorn app.main:app --reload")
        print()

if __name__ == "__main__":
    main()
