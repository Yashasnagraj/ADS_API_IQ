#!/usr/bin/env python3
"""
Simplified Google Ads data extraction with compatible fields only.
"""

import sys
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# Use a client account ID (not manager account)
# Available client accounts:
# - 6265362093: Communn.io
# - 5032737756: Emcee Sons
# - 7613138874: VANAVASI KALYANA
CUSTOMER_ID = "6265362093"  # Communn.io

def extract_campaigns(client, customer_id):
    """Extract campaign data."""
    print("[INFO] Extracting campaigns...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.serving_status,
            campaign.advertising_channel_type,
            campaign.campaign_budget,
            campaign.bidding_strategy_type,
            campaign.start_date,
            campaign.end_date,
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.conversions,
            metrics.all_conversions,
            metrics.average_cpc,
            metrics.ctr,
            metrics.conversions_value,
            segments.date
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.impressions DESC
    """

    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        print("Campaign_ID,Campaign_Name,Status,Channel_Type,Clicks,Impressions,Cost,CTR,Conversions,Date")

        for batch in response:
            for row in batch.results:
                campaign = row.campaign
                metrics = row.metrics
                segments = row.segments

                cost = metrics.cost_micros / 1_000_000 if metrics.cost_micros else 0

                print(f"{campaign.id},{campaign.name},{campaign.status.name},"
                      f"{campaign.advertising_channel_type.name},{metrics.clicks},{metrics.impressions},"
                      f"{cost:.2f},{metrics.ctr:.4f},{metrics.conversions:.2f},{segments.date}")

    except GoogleAdsException as ex:
        print(f"[ERROR] Campaign query failed: {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in campaigns: {e}")

def extract_ad_groups(client, customer_id):
    """Extract ad group data."""
    print("[INFO] Extracting ad groups...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group.type,
            ad_group.cpc_bid_micros,
            ad_group.campaign,
            campaign.id,
            campaign.name,
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.conversions,
            metrics.average_cpc,
            metrics.ctr,
            segments.date,
            segments.device
        FROM ad_group
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.impressions DESC
    """

    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        print("AdGroup_ID,AdGroup_Name,Status,Campaign_Name,CPC_Bid,Clicks,Impressions,Cost,CTR,Conversions,Device,Date")

        for batch in response:
            for row in batch.results:
                ad_group = row.ad_group
                campaign = row.campaign
                metrics = row.metrics
                segments = row.segments

                cost = metrics.cost_micros / 1_000_000 if metrics.cost_micros else 0
                cpc_bid = ad_group.cpc_bid_micros / 1_000_000 if ad_group.cpc_bid_micros else 0
                device = segments.device.name if hasattr(segments, 'device') else 'UNKNOWN'

                print(f"{ad_group.id},{ad_group.name},{ad_group.status.name},{campaign.name},"
                      f"{cpc_bid:.2f},{metrics.clicks},{metrics.impressions},"
                      f"{cost:.2f},{metrics.ctr:.4f},{metrics.conversions:.2f},{device},{segments.date}")

    except GoogleAdsException as ex:
        print(f"[ERROR] Ad group query failed: {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in ad groups: {e}")

def extract_keywords(client, customer_id):
    """Extract keyword data."""
    print("[INFO] Extracting keywords...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.name,
            ad_group.name,
            ad_group_criterion.criterion_id,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.status,
            ad_group_criterion.quality_info.quality_score,
            ad_group_criterion.cpc_bid_micros,
            ad_group_criterion.position_estimates.first_page_cpc_micros,
            ad_group_criterion.position_estimates.top_of_page_cpc_micros,
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.conversions,
            metrics.average_cpc,
            metrics.ctr,
            segments.date
        FROM keyword_view
        WHERE segments.date DURING LAST_30_DAYS
            AND ad_group_criterion.status = 'ENABLED'
        ORDER BY metrics.impressions DESC
        LIMIT 500
    """

    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        print("Campaign,AdGroup,Keyword,Match_Type,Quality_Score,CPC_Bid,Clicks,Impressions,Cost,CTR,Conversions,Avg_CPC,Date")

        for batch in response:
            for row in batch.results:
                campaign = row.campaign
                ad_group = row.ad_group
                criterion = row.ad_group_criterion
                keyword = criterion.keyword
                metrics = row.metrics
                segments = row.segments
                quality_info = criterion.quality_info

                cost = metrics.cost_micros / 1_000_000 if metrics.cost_micros else 0
                avg_cpc = metrics.average_cpc / 1_000_000 if metrics.average_cpc else 0
                cpc_bid = criterion.cpc_bid_micros / 1_000_000 if criterion.cpc_bid_micros else 0
                quality_score = quality_info.quality_score if quality_info.quality_score else 0

                print(f"{campaign.name},{ad_group.name},{keyword.text},{keyword.match_type.name},"
                      f"{quality_score},{cpc_bid:.2f},{metrics.clicks},{metrics.impressions},"
                      f"{cost:.2f},{metrics.ctr:.4f},{metrics.conversions:.2f},{avg_cpc:.2f},{segments.date}")

    except GoogleAdsException as ex:
        print(f"[ERROR] Keyword query failed: {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in keywords: {e}")

def extract_search_terms(client, customer_id):
    """Extract search term data."""
    print("[INFO] Extracting search terms...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.name,
            ad_group.name,
            segments.keyword.info.text,
            segments.keyword.info.match_type,
            search_term_view.search_term,
            segments.search_term_match_type,
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.conversions,
            metrics.average_cpc,
            metrics.ctr,
            segments.date
        FROM search_term_view
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.impressions DESC
        LIMIT 500
    """

    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        print("Campaign,AdGroup,Keyword,Keyword_Match,Search_Term,Search_Match,Clicks,Impressions,Cost,CTR,Conversions,Avg_CPC,Date")

        for batch in response:
            for row in batch.results:
                campaign = row.campaign
                ad_group = row.ad_group
                search_term_view = row.search_term_view
                metrics = row.metrics
                segments = row.segments

                cost = metrics.cost_micros / 1_000_000 if metrics.cost_micros else 0
                avg_cpc = metrics.average_cpc / 1_000_000 if metrics.average_cpc else 0

                keyword_text = segments.keyword.info.text if hasattr(segments.keyword.info, 'text') else ''
                keyword_match = segments.keyword.info.match_type.name if hasattr(segments.keyword.info, 'match_type') else 'UNKNOWN'
                search_match_type = segments.search_term_match_type.name if hasattr(segments, 'search_term_match_type') else 'UNKNOWN'

                print(f"{campaign.name},{ad_group.name},{keyword_text},{keyword_match},"
                      f"{search_term_view.search_term},{search_match_type},{metrics.clicks},"
                      f"{metrics.impressions},{cost:.2f},{metrics.ctr:.4f},{metrics.conversions:.2f},{avg_cpc:.2f},{segments.date}")

    except GoogleAdsException as ex:
        print(f"[ERROR] Search term query failed: {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in search terms: {e}")

def extract_all_accounts(client):
    """Extract data for all client accounts under the manager."""

    customer_service = client.get_service("CustomerService")
    ga_service = client.get_service("GoogleAdsService")

    # Get all client accounts
    query = """
        SELECT
            customer_client.id,
            customer_client.descriptive_name,
            customer_client.manager
        FROM customer_client
        WHERE customer_client.level <= 1
            AND customer_client.status = 'ENABLED'
    """

    try:
        response = ga_service.search(customer_id="3341907700", query=query)

        client_accounts = []
        for row in response:
            if not row.customer_client.manager:  # Only client accounts
                client_accounts.append({
                    'id': str(row.customer_client.id),
                    'name': row.customer_client.descriptive_name
                })

        print(f"Found {len(client_accounts)} client accounts")
        print("=" * 80)

        for account in client_accounts:
            print(f"\n{'=' * 80}")
            print(f"Processing Account: {account['name']} (ID: {account['id']})")
            print(f"{'=' * 80}\n")

            extract_campaigns(client, account['id'])
            print()
            extract_ad_groups(client, account['id'])
            print()
            extract_keywords(client, account['id'])
            print()
            extract_search_terms(client, account['id'])
            print()

    except Exception as e:
        print(f"Error getting client accounts: {e}")

def main():
    """Main function to orchestrate all data extraction."""

    try:
        client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    except FileNotFoundError:
        print("[ERROR] google-ads.yaml not found.")
        print("Please ensure google-ads.yaml exists with your credentials.")
        sys.exit(1)
    except Exception as e:
        print(f"[ERROR] Failed to load configuration: {e}")
        sys.exit(1)

    print(f"Starting Google Ads data extraction")
    print("=" * 80)

    # Extract data for all client accounts
    extract_all_accounts(client)

    print("=" * 80)
    print("Done.")

if __name__ == "__main__":
    main()