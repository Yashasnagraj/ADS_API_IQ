#!/usr/bin/env python3
"""
Query Google Ads API for keyword performance data.
Fetches keywords and campaign information for the last 30 days.
"""

import sys
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

# EDIT THIS: Your Google Ads customer ID (without hyphens)
CUSTOMER_ID = "3341907700"  # Your actual customer ID

def main():
    """Query and display keyword performance data from Google Ads."""
    
    # Initialize the Google Ads client using config file
    try:
        client = GoogleAdsClient.load_from_storage("google-ads.yaml")
    except FileNotFoundError:
        print("Error: google-ads.yaml not found.")
        print("Please copy google-ads.yaml.template to google-ads.yaml and fill in your credentials.")
        sys.exit(1)
    except Exception as e:
        print(f"Error loading configuration: {e}")
        sys.exit(1)
    
    # Get the GoogleAdsService
    ga_service = client.get_service("GoogleAdsService")
    
    # Calculate date range (last 30 days)
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    # GAQL query to fetch keyword data
    query = f"""
        SELECT
            campaign.id,
            campaign.name,
            ad_group.id,
            ad_group.name,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.average_cpc,
            metrics.ctr,
            metrics.conversions,
            metrics.conversion_rate
        FROM keyword_view
        WHERE segments.date BETWEEN '{start_date.strftime('%Y-%m-%d')}' 
            AND '{end_date.strftime('%Y-%m-%d')}'
            AND campaign.status = 'ENABLED'
            AND ad_group.status = 'ENABLED'
            AND ad_group_criterion.status = 'ENABLED'
        ORDER BY metrics.impressions DESC
        LIMIT 100
    """
    
    try:
        # Execute the query
        print(f"Fetching keyword data for customer ID: {CUSTOMER_ID}")
        print(f"Date range: {start_date} to {end_date}")
        print("-" * 120)
        
        # Make the request
        response = ga_service.search_stream(customer_id=CUSTOMER_ID, query=query)
        
        # Print CSV header
        print("Campaign,Ad Group,Keyword,Match Type,Clicks,Impressions,Cost,Avg CPC,CTR,Conversions,Conv Rate")
        print("-" * 120)
        
        row_count = 0
        total_cost = 0
        total_clicks = 0
        total_impressions = 0
        total_conversions = 0
        
        # Process and display results
        for batch in response:
            for row in batch.results:
                campaign = row.campaign
                ad_group = row.ad_group
                keyword = row.ad_group_criterion.keyword
                metrics = row.metrics
                
                # Convert cost from micros to actual currency
                cost = metrics.cost_micros / 1_000_000
                total_cost += cost
                total_clicks += metrics.clicks
                total_impressions += metrics.impressions
                total_conversions += metrics.conversions
                
                # Format and print the row
                print(f'"{campaign.name}","{ad_group.name}","{keyword.text}",{keyword.match_type.name},'
                      f'{metrics.clicks},{metrics.impressions},{cost:.2f},{metrics.average_cpc/1_000_000:.2f},'
                      f'{metrics.ctr:.2%},{metrics.conversions:.2f},{metrics.conversion_rate:.2%}')
                
                row_count += 1
        
        # Print summary
        print("-" * 120)
        print(f"\nSummary:")
        print(f"Total Keywords: {row_count}")
        print(f"Total Clicks: {total_clicks:,}")
        print(f"Total Impressions: {total_impressions:,}")
        print(f"Total Cost: ${total_cost:,.2f}")
        print(f"Total Conversions: {total_conversions:.2f}")
        if total_impressions > 0:
            print(f"Overall CTR: {(total_clicks/total_impressions):.2%}")
        if total_clicks > 0:
            print(f"Overall CPC: ${(total_cost/total_clicks):.2f}")
            print(f"Overall Conv Rate: {(total_conversions/total_clicks):.2%}")
        
    except GoogleAdsException as ex:
        print(f"Request failed with status {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f'\tError: "{error.message}"')
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    print(f"\t\tOn field: {field_path_element.field_name}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()