"""
Find Google Ads Accounts with Campaigns

Lists all accessible accounts and checks which ones have campaigns.
"""

import sys
import os
from pathlib import Path
from google.ads.googleads.client import GoogleAdsClient

# Fix Windows console encoding
if sys.platform == 'win32':
    os.system('chcp 65001 >nul 2>&1')
    sys.stdout.reconfigure(encoding='utf-8')

def find_accounts():
    """Find all accessible Google Ads accounts"""

    print("=" * 70)
    print("FINDING GOOGLE ADS ACCOUNTS")
    print("=" * 70)

    # Initialize client
    yaml_path = Path(__file__).parent / 'google-ads.yaml'
    client = GoogleAdsClient.load_from_storage(str(yaml_path))

    # Get accessible customers
    print("\n🔍 Searching for accessible accounts...\n")

    customer_service = client.get_service("CustomerService")

    try:
        accessible_customers = customer_service.list_accessible_customers()
        resource_names = accessible_customers.resource_names

        print(f"✅ Found {len(resource_names)} accessible accounts:\n")

        accounts_with_campaigns = []

        for resource_name in resource_names:
            # Extract customer ID from resource name
            customer_id = resource_name.split('/')[-1]

            print(f"📊 Checking account: {customer_id}")

            # Get account details
            try:
                ga_service = client.get_service("GoogleAdsService")

                # Get account info
                query = f"""
                    SELECT
                        customer.id,
                        customer.descriptive_name,
                        customer.currency_code,
                        customer.manager
                    FROM customer
                    WHERE customer.id = {customer_id}
                """

                response = ga_service.search(customer_id=customer_id, query=query)

                for row in response:
                    cust = row.customer
                    is_manager = cust.manager
                    name = cust.descriptive_name if cust.descriptive_name else "(No name)"
                    currency = cust.currency_code if cust.currency_code else "N/A"

                    print(f"   Name: {name}")
                    print(f"   Currency: {currency}")
                    print(f"   Type: {'Manager Account (MCC)' if is_manager else 'Client Account'}")

                    # Check for campaigns (only for non-manager accounts)
                    if not is_manager:
                        campaign_query = """
                            SELECT campaign.id, campaign.name
                            FROM campaign
                            WHERE campaign.status != 'REMOVED'
                            LIMIT 5
                        """

                        try:
                            campaign_response = ga_service.search(customer_id=customer_id, query=campaign_query)
                            campaigns = list(campaign_response)

                            if campaigns:
                                print(f"   ✅ HAS CAMPAIGNS: {len(campaigns)} found")
                                print("   Sample campaigns:")
                                for i, campaign_row in enumerate(campaigns[:3], 1):
                                    print(f"      {i}. {campaign_row.campaign.name}")

                                accounts_with_campaigns.append({
                                    'customer_id': customer_id,
                                    'name': name,
                                    'currency': currency,
                                    'campaign_count': len(campaigns)
                                })
                            else:
                                print("   ⚠️  No campaigns")
                        except Exception as e:
                            print(f"   ❌ Error checking campaigns: {e}")

                    print()

            except Exception as e:
                print(f"   ❌ Error accessing account: {e}\n")

        # Summary
        print("=" * 70)
        print("📊 SUMMARY")
        print("=" * 70)
        print(f"\nTotal accounts found: {len(resource_names)}")
        print(f"Accounts with campaigns: {len(accounts_with_campaigns)}\n")

        if accounts_with_campaigns:
            print("✅ ACCOUNTS YOU CAN USE FOR ETL:\n")
            for acc in accounts_with_campaigns:
                print(f"   Customer ID: {acc['customer_id']}")
                print(f"   Name: {acc['name']}")
                print(f"   Currency: {acc['currency']}")
                print(f"   Campaigns: {acc['campaign_count']}+")
                print()
                print(f"   📝 To use this account, update your .env:")
                print(f"      GOOGLE_ADS_CUSTOMER_ID={acc['customer_id']}")
                print()
                print(f"   📝 Then run:")
                print(f"      python warehouse_google_ads_etl.py --days=30")
                print()
                print("-" * 70)
                print()
        else:
            print("⚠️  No accounts with campaigns found.")
            print("\nOptions:")
            print("   1. Create campaigns in Google Ads UI")
            print("   2. Check if you have access to other accounts")
            print("   3. Use sample data to test warehouse features")

        print("=" * 70)

    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    find_accounts()
