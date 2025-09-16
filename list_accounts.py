#!/usr/bin/env python3
"""
List all accessible Google Ads accounts.
"""

import sys
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

MANAGER_ID = "3341907700"

def main():
    """List all accessible Google Ads accounts."""

    try:
        client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    except FileNotFoundError:
        print("[ERROR] google-ads.yaml not found.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to load configuration: {e}")
        sys.exit(1)

    ga_service = client.get_service("GoogleAdsService")
    customer_service = client.get_service("CustomerService")

    print("Fetching accessible accounts...")
    print("=" * 60)

    try:
        # Get list of accessible customers
        accessible_customers = customer_service.list_accessible_customers()

        print(f"Found {len(accessible_customers.resource_names)} accessible account(s):")
        print()

        for resource_name in accessible_customers.resource_names:
            customer_id = resource_name.split('/')[-1]

            # Get account details
            query = f"""
                SELECT
                    customer.id,
                    customer.descriptive_name,
                    customer.currency_code,
                    customer.time_zone,
                    customer.manager,
                    customer.test_account
                FROM customer
                WHERE customer.id = {customer_id}
            """

            try:
                response = ga_service.search(customer_id=customer_id, query=query)

                for row in response:
                    customer = row.customer
                    account_type = "Manager" if customer.manager else "Client"
                    test_status = " (TEST)" if customer.test_account else ""

                    print(f"ID: {customer.id}")
                    print(f"Name: {customer.descriptive_name}")
                    print(f"Type: {account_type}{test_status}")
                    print(f"Currency: {customer.currency_code}")
                    print(f"Time Zone: {customer.time_zone}")
                    print("-" * 40)

            except Exception as e:
                print(f"Error fetching details for {customer_id}: {e}")
                print("-" * 40)

        # If we have a manager account, get its client accounts
        if MANAGER_ID:
            print(f"\nFetching client accounts under manager {MANAGER_ID}...")
            print("=" * 60)

            query = """
                SELECT
                    customer_client.id,
                    customer_client.descriptive_name,
                    customer_client.currency_code,
                    customer_client.time_zone,
                    customer_client.manager,
                    customer_client.level,
                    customer_client.status
                FROM customer_client
                WHERE customer_client.level <= 1
            """

            try:
                response = ga_service.search(customer_id=MANAGER_ID, query=query)

                client_count = 0
                for row in response:
                    client = row.customer_client
                    if not client.manager:  # Only show client accounts, not sub-managers
                        client_count += 1
                        print(f"Client ID: {client.id}")
                        print(f"Name: {client.descriptive_name}")
                        print(f"Status: {client.status.name}")
                        print(f"Currency: {client.currency_code}")
                        print(f"Time Zone: {client.time_zone}")
                        print("-" * 40)

                if client_count == 0:
                    print("No client accounts found under this manager.")
                else:
                    print(f"\nTotal client accounts: {client_count}")

            except Exception as e:
                print(f"Error fetching client accounts: {e}")

    except GoogleAdsException as ex:
        print(f"Request failed with status {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f'  Error: "{error.message}"')
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()