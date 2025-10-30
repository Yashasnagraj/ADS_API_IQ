"""
Find Client Accounts Under MCC

Searches for the three customer accounts mentioned:
- emcee sons
- vanavasi kalyana
- (third customer)

Lists all client accounts under the MCC and identifies which have campaigns.
"""

import sys
import os
from pathlib import Path
from google.ads.googleads.client import GoogleAdsClient

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

def find_client_accounts():
    """Find all client accounts under the MCC"""

    print("=" * 70)
    print("FINDING CLIENT ACCOUNTS UNDER MCC")
    print("=" * 70)

    # Initialize client
    yaml_path = Path(__file__).parent / 'google-ads.yaml'
    client = GoogleAdsClient.load_from_storage(str(yaml_path))

    # Get the MCC account ID
    mcc_id = "3341907700"

    print(f"\n🔍 Searching for client accounts under MCC: {mcc_id}\n")

    ga_service = client.get_service("GoogleAdsService")

    # Query to get all client accounts under the MCC
    query = """
        SELECT
            customer_client.id,
            customer_client.descriptive_name,
            customer_client.currency_code,
            customer_client.manager,
            customer_client.status
        FROM customer_client
        WHERE customer_client.status = 'ENABLED'
    """

    try:
        response = ga_service.search(customer_id=mcc_id, query=query)

        client_accounts = []

        print("📋 Client Accounts Found:\n")
        print("-" * 70)

        for row in response:
            client = row.customer_client

            # Skip manager accounts
            if client.manager:
                continue

            account_info = {
                'id': str(client.id),
                'name': client.descriptive_name if client.descriptive_name else "(No name)",
                'currency': client.currency_code if client.currency_code else "N/A"
            }

            client_accounts.append(account_info)

            print(f"\n📊 Customer ID: {account_info['id']}")
            print(f"   Name: {account_info['name']}")
            print(f"   Currency: {account_info['currency']}")

            # Check if this matches our target customers
            name_lower = account_info['name'].lower()
            if any(keyword in name_lower for keyword in ['emcee', 'vanavasi', 'kalyana']):
                print(f"   ⭐ TARGET CUSTOMER MATCH!")

            # Check for campaigns
            campaign_query = """
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status
                FROM campaign
                WHERE campaign.status != 'REMOVED'
                LIMIT 10
            """

            try:
                campaign_response = ga_service.search(
                    customer_id=account_info['id'],
                    query=campaign_query
                )
                campaigns = list(campaign_response)

                if campaigns:
                    print(f"   ✅ HAS {len(campaigns)}+ CAMPAIGNS")
                    print(f"   Sample campaigns:")
                    for i, camp_row in enumerate(campaigns[:5], 1):
                        status = camp_row.campaign.status.name
                        print(f"      {i}. {camp_row.campaign.name} ({status})")
                else:
                    print(f"   ⚠️  No campaigns found")

            except Exception as e:
                print(f"   ❌ Error checking campaigns: {e}")

            print("-" * 70)

        # Summary
        print("\n" + "=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"\nTotal client accounts: {len(client_accounts)}\n")

        # Highlight target customers
        print("🎯 TARGET CUSTOMERS TO USE FOR ETL:\n")

        target_found = False
        for acc in client_accounts:
            name_lower = acc['name'].lower()
            if any(keyword in name_lower for keyword in ['emcee', 'vanavasi', 'kalyana']):
                target_found = True
                print(f"   ✅ {acc['name']}")
                print(f"      Customer ID: {acc['id']}")
                print(f"      Currency: {acc['currency']}")
                print(f"\n      📝 To fetch data from this account:")
                print(f"         python warehouse_google_ads_etl.py --customer_id={acc['id']} --days=30")
                print()

        if not target_found:
            print("   ⚠️  No accounts matching 'emcee', 'vanavasi', or 'kalyana' found")
            print("\n   All available accounts:")
            for acc in client_accounts:
                print(f"      • {acc['name']} (ID: {acc['id']})")

        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_client_accounts()
