"""
Find GA4 Properties

Lists all GA4 properties accessible by the service account.
"""

import sys
import os
from pathlib import Path
from google.analytics.admin import AnalyticsAdminServiceClient
from google.oauth2 import service_account

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')


def find_ga4_properties():
    """Find all accessible GA4 properties"""

    print("=" * 70)
    print("FINDING GA4 PROPERTIES")
    print("=" * 70)

    # Load credentials
    credentials_path = Path(__file__).parent / 'credentials' / 'ga4-service-account.json'

    if not credentials_path.exists():
        print(f"\n❌ Credentials not found at: {credentials_path}")
        return

    print(f"\n🔐 Loading credentials from: {credentials_path.name}")

    try:
        credentials = service_account.Credentials.from_service_account_file(
            str(credentials_path),
            scopes=['https://www.googleapis.com/auth/analytics.readonly']
        )

        client = AnalyticsAdminServiceClient(credentials=credentials)

        print("\n🔍 Searching for GA4 properties...\n")

        # List all accounts
        print("📊 Attempting to list accounts...")

        try:
            accounts = client.list_accounts()
            account_list = list(accounts)

            if not account_list:
                print("\n⚠️  No GA4 accounts found.")
                print("\nPossible reasons:")
                print("   1. Service account needs to be added to GA4 property")
                print("   2. No GA4 properties exist in this Google Cloud project")
                print("\n📝 To grant access:")
                print("   1. Go to GA4 Admin → Property Access Management")
                print("   2. Add this email as a Viewer:")
                print(f"      {credentials.service_account_email}")
                return

            print(f"✅ Found {len(account_list)} account(s)\n")
            print("-" * 70)

            properties_found = []

            for account in account_list:
                print(f"\n📁 Account: {account.display_name}")
                print(f"   Resource Name: {account.name}")

                # List properties in this account
                try:
                    properties = client.list_properties(parent=account.name)

                    for prop in properties:
                        property_id = prop.name.split('/')[-1]

                        print(f"\n   📊 Property: {prop.display_name}")
                        print(f"      Property ID: {property_id}")
                        print(f"      Currency: {prop.currency_code if prop.currency_code else 'N/A'}")
                        print(f"      Time Zone: {prop.time_zone if prop.time_zone else 'N/A'}")
                        print(f"      Industry: {prop.industry_category.name if prop.industry_category else 'N/A'}")

                        properties_found.append({
                            'id': property_id,
                            'name': prop.display_name,
                            'account': account.display_name
                        })

                except Exception as e:
                    print(f"   ⚠️  Could not list properties: {e}")

            # Summary
            print("\n" + "=" * 70)
            print("📊 SUMMARY")
            print("=" * 70)

            if properties_found:
                print(f"\n✅ Found {len(properties_found)} GA4 properties:\n")

                for prop in properties_found:
                    print(f"   Property ID: {prop['id']}")
                    print(f"   Name: {prop['name']}")
                    print(f"   Account: {prop['account']}")
                    print()
                    print(f"   📝 To fetch data from this property:")
                    print(f"      python warehouse_ga4_etl.py --property_id={prop['id']} --days=30")
                    print()
                    print("-" * 70)
                    print()
            else:
                print("\n⚠️  No properties accessible by this service account")
                print("\n📝 Grant access by:")
                print("   1. Open GA4 Admin → Property Access Management")
                print("   2. Click 'Add users'")
                print(f"   3. Add email: {credentials.service_account_email}")
                print("   4. Grant 'Viewer' role")

            print("=" * 70)

        except Exception as e:
            print(f"\n❌ Error listing accounts: {e}")
            print("\nThis usually means:")
            print("   • Service account has no access to any GA4 properties")
            print("   • You need to grant access in GA4 Admin")
            print(f"\n   Service account email: {credentials.service_account_email}")

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    find_ga4_properties()
