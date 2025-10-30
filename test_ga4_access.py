"""
Test GA4 Data API Access

Tests if we can access GA4 data with common property IDs.
If you know your GA4 property ID, you can test it directly.

Find your Property ID:
1. Go to GA4 Admin
2. Click Property Settings
3. Look for "Property ID" (9-digit number)

Usage:
    python test_ga4_access.py --property_id=123456789
"""

import sys
import os
import argparse
from pathlib import Path
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import (
    DateRange,
    Dimension,
    Metric,
    RunReportRequest,
)
from google.oauth2 import service_account

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')


def test_property_access(property_id):
    """Test access to a specific GA4 property"""

    print("=" * 70)
    print("TESTING GA4 PROPERTY ACCESS")
    print("=" * 70)

    credentials_path = Path(__file__).parent / 'credentials' / 'ga4-service-account.json'

    if not credentials_path.exists():
        print(f"\n❌ Credentials not found at: {credentials_path}")
        return False

    print(f"\n🔐 Loading credentials...")

    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )

        client = BetaAnalyticsDataClient(credentials=credentials)

        print(f"   Service Account: {credentials.service_account_email}")
        print(f"\n📊 Testing Property ID: {property_id}")

        # Try a simple query
        request = RunReportRequest(
            property=f"properties/{property_id}",
            date_ranges=[DateRange(start_date="7daysAgo", end_date="today")],
            dimensions=[Dimension(name="date")],
            metrics=[Metric(name="sessions")],
        )

        print(f"   Running test query (last 7 days)...")

        response = client.run_report(request)

        # Count rows
        row_count = len(response.rows)

        print(f"\n✅ SUCCESS! Property is accessible")
        print(f"   Returned {row_count} days of data")

        if row_count > 0:
            print(f"\n   Sample data:")
            for i, row in enumerate(response.rows[:3]):
                date = row.dimension_values[0].value
                sessions = row.metric_values[0].value
                print(f"      {date}: {sessions} sessions")

        print(f"\n✅ This property ID works!")
        print(f"   You can now run:")
        print(f"      python warehouse_ga4_etl.py --property_id={property_id} --days=30")

        return True

    except Exception as e:
        print(f"\n❌ ERROR: {e}")

        if "403" in str(e):
            print("\n   This means:")
            print("   • Service account doesn't have access to this property")
            print("   • You need to add the service account as a Viewer")
            print(f"\n   📝 To grant access:")
            print(f"      1. Open GA4 Admin → Property Access Management")
            print(f"      2. Click 'Add users'")
            print(f"      3. Add: {credentials.service_account_email}")
            print(f"      4. Grant 'Viewer' role")
        elif "404" in str(e):
            print("\n   Property ID not found. Double-check:")
            print("   • GA4 Admin → Property Settings → Property ID")
        else:
            print(f"\n   Unexpected error. Details:")
            import traceback
            traceback.print_exc()

        return False


def main():
    parser = argparse.ArgumentParser(description='Test GA4 Property Access')
    parser.add_argument('--property_id', type=str, help='GA4 Property ID to test')
    args = parser.parse_args()

    if not args.property_id:
        print("=" * 70)
        print("GA4 PROPERTY ID REQUIRED")
        print("=" * 70)
        print("\n📝 To find your GA4 Property ID:")
        print("   1. Open Google Analytics 4")
        print("   2. Click Admin (gear icon)")
        print("   3. Click 'Property Settings'")
        print("   4. Look for 'Property ID' (9-digit number)")
        print("\n   Then run:")
        print("      python test_ga4_access.py --property_id=YOUR_PROPERTY_ID")
        print("\n=" * 70)
        return

    test_property_access(args.property_id)


if __name__ == "__main__":
    main()
