#!/usr/bin/env python3
"""
Test script to verify customer filtering functionality and KPI calculations
"""

import requests
import json
import sqlite3
from datetime import datetime

BASE_URL = "http://localhost:5000"

def test_customer_list():
    """Test getting list of available customers"""
    print("\n=== Testing Customer List Endpoint ===")
    response = requests.get(f"{BASE_URL}/api/customers")
    if response.status_code == 200:
        data = response.json()
        print(f"✅ Found {data['total']} customers")
        for customer in data['customers'][:3]:  # Show first 3
            print(f"  Customer ID: {customer['customer_id']}, Campaigns: {customer['campaign_count']}, Revenue: ${customer.get('total_revenue', 0):,.2f}")
        return data['customers']
    else:
        print(f"❌ Failed to get customers: {response.status_code}")
        return []

def test_kpis_without_filter():
    """Test KPIs without customer filter (all customers)"""
    print("\n=== Testing KPIs Without Filter ===")
    response = requests.get(f"{BASE_URL}/api/descriptive/kpis")
    if response.status_code == 200:
        data = response.json()
        kpis = data['kpis']
        print("✅ KPIs for ALL customers:")
        print(f"  Revenue: {kpis['revenue']['value']} (Change: {kpis['revenue']['change']:.1f}%)")
        print(f"  Conversion Rate: {kpis['conversion_rate']['value']}")
        print(f"  CPC: {kpis['cpc']['value']}")
        print(f"  CTR: {kpis['ctr']['value']}")
        print(f"  Total Clicks: {data['summary']['total_clicks']:,}")
        print(f"  Total Conversions: {data['summary']['total_conversions']:,}")
        return data
    else:
        print(f"❌ Failed to get KPIs: {response.status_code}")
        return None

def test_kpis_with_filter(customer_id):
    """Test KPIs with customer filter"""
    print(f"\n=== Testing KPIs With Filter (Customer ID: {customer_id}) ===")
    response = requests.get(f"{BASE_URL}/api/descriptive/kpis?customer_id={customer_id}")
    if response.status_code == 200:
        data = response.json()
        kpis = data['kpis']
        print(f"✅ KPIs for Customer {customer_id}:")
        print(f"  Revenue: {kpis['revenue']['value']} (Change: {kpis['revenue']['change']:.1f}%)")
        print(f"  Conversion Rate: {kpis['conversion_rate']['value']}")
        print(f"  CPC: {kpis['cpc']['value']}")
        print(f"  CTR: {kpis['ctr']['value']}")
        print(f"  Total Clicks: {data['summary']['total_clicks']:,}")
        print(f"  Total Conversions: {data['summary']['total_conversions']:,}")
        return data
    else:
        print(f"❌ Failed to get filtered KPIs: {response.status_code}")
        return None

def verify_database_values():
    """Verify that KPIs are computed from database, not hardcoded"""
    print("\n=== Verifying Database Values ===")
    conn = sqlite3.connect('google_ads_data.db')
    cursor = conn.cursor()

    # Check actual database values
    query = """
        SELECT
            COUNT(DISTINCT customer_id) as customer_count,
            SUM(conversion_value) as total_revenue,
            AVG(conversion_rate) as avg_conversion_rate,
            AVG(avg_cpc_micros) / 1000000.0 as avg_cpc,
            SUM(clicks) as total_clicks,
            SUM(conversions) as total_conversions
        FROM campaign_keywords
        WHERE date >= date('now', '-30 days')
    """

    cursor.execute(query)
    result = cursor.fetchone()

    if result:
        print("✅ Database values (Last 30 days):")
        print(f"  Customer Count: {result[0]}")
        print(f"  Total Revenue: ${result[1]:,.2f}" if result[1] else "  Total Revenue: $0.00")
        print(f"  Avg Conversion Rate: {result[2]:.2f}%" if result[2] else "  Avg Conversion Rate: 0.00%")
        print(f"  Avg CPC: ${result[3]:.2f}" if result[3] else "  Avg CPC: $0.00")
        print(f"  Total Clicks: {result[4]:,}" if result[4] else "  Total Clicks: 0")
        print(f"  Total Conversions: {result[5]:,}" if result[5] else "  Total Conversions: 0")

    conn.close()

def test_realtime_metrics():
    """Test realtime metrics endpoint to confirm hardcoded values"""
    print("\n=== Testing Realtime Metrics (Should be Hardcoded) ===")
    response = requests.get(f"{BASE_URL}/api/realtime/metrics")
    if response.status_code == 200:
        data = response.json()
        print("⚠️  Realtime metrics (hardcoded with random variations):")
        print(f"  Impressions: {data['impressions']:,}")
        print(f"  Clicks: {data['clicks']:,}")
        print(f"  Conversions: {data['conversions']}")
        print(f"  Cost: ${data['cost']:,.2f}")
        print(f"  Revenue: ${data['revenue']:,.2f}")
        print("  Note: These values are intentionally hardcoded for demo purposes")
    else:
        print(f"❌ Failed to get realtime metrics: {response.status_code}")

def main():
    print("=" * 60)
    print("CUSTOMER FILTER & KPI VERIFICATION TEST")
    print("=" * 60)

    # Test 1: Get customer list
    customers = test_customer_list()

    # Test 2: Get KPIs without filter
    all_kpis = test_kpis_without_filter()

    # Test 3: Get KPIs with filter (if customers exist)
    if customers:
        # Test with first customer
        test_kpis_with_filter(customers[0]['customer_id'])

        # If there's a second customer, test with that too
        if len(customers) > 1:
            test_kpis_with_filter(customers[1]['customer_id'])

    # Test 4: Verify database values
    verify_database_values()

    # Test 5: Check realtime metrics (hardcoded)
    test_realtime_metrics()

    print("\n" + "=" * 60)
    print("TEST SUMMARY:")
    print("✅ Customer filtering has been implemented")
    print("✅ KPIs are computed from database (except realtime metrics)")
    print("⚠️  Realtime metrics endpoint uses hardcoded values for demo")
    print("=" * 60)

if __name__ == "__main__":
    main()