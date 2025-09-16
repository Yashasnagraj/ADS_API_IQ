#!/usr/bin/env python3
"""
Extract comprehensive Google Ads data using GAQL queries.
Connects to Google Ads API and extracts all available fields from multiple resources.
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
    """Extract all campaign data with comprehensive fields."""
    print("[INFO] Extracting campaigns...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            campaign.serving_status,
            campaign.ad_serving_optimization_status,
            campaign.advertising_channel_type,
            campaign.advertising_channel_sub_type,
            campaign.experiment_type,
            campaign.base_campaign,
            campaign.campaign_budget,
            campaign.bidding_strategy,
            campaign.bidding_strategy_type,
            campaign.start_date,
            campaign.end_date,
            campaign.final_url_suffix,
            campaign.frequency_caps,
            campaign.video_brand_safety_suitability,
            campaign.vanity_pharma.vanity_pharma_display_url_mode,
            campaign.vanity_pharma.vanity_pharma_text,
            campaign.selective_optimization.conversion_actions,
            campaign.optimization_goal_setting.optimization_goal_types,
            campaign.tracking_url_template,
            campaign.payment_mode,
            campaign.optimization_score,
            campaign.excluded_parent_asset_field_types,
            campaign.url_custom_parameters,
            campaign.real_time_bidding_setting.opt_in,
            campaign.network_settings.target_google_search,
            campaign.network_settings.target_search_network,
            campaign.network_settings.target_content_network,
            campaign.network_settings.target_partner_search_network,
            campaign.hotel_setting.hotel_center_id,
            campaign.dynamic_search_ads_setting.domain_name,
            campaign.dynamic_search_ads_setting.language_code,
            campaign.dynamic_search_ads_setting.use_supplied_urls_only,
            campaign.shopping_setting.merchant_id,
            campaign.shopping_setting.campaign_priority,
            campaign.shopping_setting.enable_local,
            campaign.target_spend.target_spend_micros,
            campaign.target_spend.cpc_bid_ceiling_micros,
            campaign.target_cpa.target_cpa_micros,
            campaign.target_roas.target_roas,
            campaign.target_roas.cpc_bid_ceiling_micros,
            campaign.target_roas.cpc_bid_floor_micros,
            campaign.target_impression_share.location,
            campaign.target_impression_share.location_fraction_micros,
            campaign.target_impression_share.cpc_bid_ceiling_micros,
            campaign.app_campaign_setting.app_id,
            campaign.app_campaign_setting.app_store,
            campaign.app_campaign_setting.bidding_strategy_goal_type,
            campaign.labels,
            campaign.excluded_parent_asset_field_types,
            campaign.geo_target_type_setting.positive_geo_target_type,
            campaign.geo_target_type_setting.negative_geo_target_type,
            campaign.local_campaign_setting.location_source_type,
            campaign.travel_campaign_settings.travel_account_id,
            campaign.accessible_bidding_strategy,
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.conversions,
            metrics.all_conversions,
            metrics.average_cpc,
            metrics.average_cpm,
            metrics.average_cpv,
            metrics.average_cpe,
            metrics.ctr,
            metrics.cost_per_conversion,
            metrics.cost_per_all_conversions,
            metrics.conversions_value,
            metrics.all_conversions_value,
            metrics.conversions_by_conversion_date,
            metrics.value_per_conversion,
            metrics.value_per_all_conversions,
            metrics.interaction_rate,
            metrics.interactions,
            metrics.interaction_event_types,
            metrics.average_cost,
            metrics.engagement_rate,
            metrics.engagements,
            metrics.active_view_cpm,
            metrics.active_view_ctr,
            metrics.active_view_impressions,
            metrics.active_view_measurability,
            metrics.active_view_measurable_cost_micros,
            metrics.active_view_measurable_impressions,
            metrics.active_view_viewability,
            metrics.absolute_top_impression_percentage,
            metrics.search_absolute_top_impression_share,
            metrics.search_budget_lost_absolute_top_impression_share,
            metrics.search_budget_lost_top_impression_share,
            metrics.search_exact_match_impression_share,
            metrics.search_impression_share,
            metrics.search_rank_lost_absolute_top_impression_share,
            metrics.search_rank_lost_impression_share,
            metrics.search_rank_lost_top_impression_share,
            metrics.search_top_impression_share,
            metrics.top_impression_percentage,
            metrics.video_view_rate,
            metrics.video_views,
            metrics.view_through_conversions,
            segments.date,
            segments.day_of_week,
            segments.month,
            segments.quarter,
            segments.year,
            segments.week
        FROM campaign
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.impressions DESC
    """

    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        print("Campaign_ID,Campaign_Name,Status,Serving_Status,Channel_Type,Budget,Bidding_Type,Clicks,Impressions,Cost,CTR,Conversions,Conv_Rate,Date")

        for batch in response:
            for row in batch.results:
                campaign = row.campaign
                metrics = row.metrics
                segments = row.segments

                cost = metrics.cost_micros / 1_000_000 if metrics.cost_micros else 0

                print(f"{campaign.id},{campaign.name},{campaign.status.name},{campaign.serving_status.name},"
                      f"{campaign.advertising_channel_type.name},{campaign.campaign_budget},"
                      f"{campaign.bidding_strategy_type.name},{metrics.clicks},{metrics.impressions},"
                      f"{cost:.2f},{metrics.ctr:.4f},{metrics.conversions:.2f},{(metrics.conversions/metrics.clicks if metrics.clicks > 0 else 0):.4f},"
                      f"{segments.date}")

    except GoogleAdsException as ex:
        print(f"[ERROR] Campaign query failed: {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in campaigns: {e}")

def extract_ad_groups(client, customer_id):
    """Extract all ad group data with comprehensive fields."""
    print("[INFO] Extracting ad groups...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group.type,
            ad_group.ad_rotation_mode,
            ad_group.base_ad_group,
            ad_group.tracking_url_template,
            ad_group.url_custom_parameters,
            ad_group.campaign,
            ad_group.cpc_bid_micros,
            ad_group.cpm_bid_micros,
            ad_group.cpv_bid_micros,
            ad_group.target_cpa_micros,
            ad_group.target_cpm_micros,
            ad_group.target_roas,
            ad_group.percent_cpc_bid_micros,
            ad_group.display_custom_bid_dimension,
            ad_group.final_url_suffix,
            ad_group.audience_setting.use_audience_grouped,
            ad_group.effective_target_cpa_micros,
            ad_group.effective_target_cpa_source,
            ad_group.effective_target_roas,
            ad_group.effective_target_roas_source,
            ad_group.labels,
            ad_group.excluded_parent_asset_field_types,
            campaign.id,
            campaign.name,
            campaign.status,
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.conversions,
            metrics.all_conversions,
            metrics.average_cpc,
            metrics.average_cpm,
            metrics.average_cpv,
            metrics.average_cpe,
            metrics.ctr,
            metrics.cost_per_conversion,
            metrics.cost_per_all_conversions,
            metrics.conversions_value,
            metrics.all_conversions_value,
            metrics.value_per_conversion,
            metrics.value_per_all_conversions,
            metrics.interaction_rate,
            metrics.interactions,
            metrics.engagement_rate,
            metrics.engagements,
            metrics.bounce_rate,
            metrics.absolute_top_impression_percentage,
            metrics.active_view_cpm,
            metrics.active_view_ctr,
            metrics.active_view_impressions,
            metrics.active_view_measurability,
            metrics.active_view_measurable_cost_micros,
            metrics.active_view_measurable_impressions,
            metrics.active_view_viewability,
            metrics.search_absolute_top_impression_share,
            metrics.search_budget_lost_absolute_top_impression_share,
            metrics.search_budget_lost_top_impression_share,
            metrics.search_exact_match_impression_share,
            metrics.search_impression_share,
            metrics.search_rank_lost_absolute_top_impression_share,
            metrics.search_rank_lost_impression_share,
            metrics.search_rank_lost_top_impression_share,
            metrics.search_top_impression_share,
            metrics.top_impression_percentage,
            metrics.video_view_rate,
            metrics.video_views,
            metrics.view_through_conversions,
            segments.date,
            segments.day_of_week,
            segments.device,
            segments.ad_network_type,
            segments.click_type,
            segments.conversion_action,
            segments.conversion_action_category,
            segments.conversion_action_name,
            segments.conversion_lag_bucket,
            segments.conversion_or_adjustment_lag_bucket,
            segments.external_conversion_source
        FROM ad_group
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.impressions DESC
    """

    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        print("AdGroup_ID,AdGroup_Name,Status,Type,Campaign_ID,Campaign_Name,CPC_Bid,Clicks,Impressions,Cost,CTR,Conversions,Conv_Rate,Device,Network,Date")

        for batch in response:
            for row in batch.results:
                ad_group = row.ad_group
                campaign = row.campaign
                metrics = row.metrics
                segments = row.segments

                cost = metrics.cost_micros / 1_000_000 if metrics.cost_micros else 0
                cpc_bid = ad_group.cpc_bid_micros / 1_000_000 if ad_group.cpc_bid_micros else 0

                device = segments.device.name if hasattr(segments, 'device') else 'UNKNOWN'
                network = segments.ad_network_type.name if hasattr(segments, 'ad_network_type') else 'UNKNOWN'

                print(f"{ad_group.id},{ad_group.name},{ad_group.status.name},{ad_group.type.name},"
                      f"{campaign.id},{campaign.name},{cpc_bid:.2f},{metrics.clicks},{metrics.impressions},"
                      f"{cost:.2f},{metrics.ctr:.4f},{metrics.conversions:.2f},{(metrics.conversions/metrics.clicks if metrics.clicks > 0 else 0):.4f},"
                      f"{device},{network},{segments.date}")

    except GoogleAdsException as ex:
        print(f"[ERROR] Ad group query failed: {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in ad groups: {e}")

def extract_keywords(client, customer_id):
    """Extract all keyword data with comprehensive fields."""
    print("[INFO] Extracting keywords...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            ad_group.id,
            ad_group.name,
            ad_group.status,
            ad_group_criterion.criterion_id,
            ad_group_criterion.status,
            ad_group_criterion.quality_info.quality_score,
            ad_group_criterion.quality_info.creative_quality_score,
            ad_group_criterion.quality_info.post_click_quality_score,
            ad_group_criterion.quality_info.search_predicted_ctr,
            ad_group_criterion.position_estimates.first_page_cpc_micros,
            ad_group_criterion.position_estimates.first_position_cpc_micros,
            ad_group_criterion.position_estimates.top_of_page_cpc_micros,
            ad_group_criterion.position_estimates.estimated_add_clicks_at_first_position_cpc,
            ad_group_criterion.position_estimates.estimated_add_cost_at_first_position_cpc,
            ad_group_criterion.effective_cpc_bid_micros,
            ad_group_criterion.effective_cpc_bid_source,
            ad_group_criterion.effective_cpm_bid_micros,
            ad_group_criterion.effective_cpm_bid_source,
            ad_group_criterion.effective_cpv_bid_micros,
            ad_group_criterion.effective_cpv_bid_source,
            ad_group_criterion.effective_percent_cpc_bid_micros,
            ad_group_criterion.effective_percent_cpc_bid_source,
            ad_group_criterion.final_mobile_urls,
            ad_group_criterion.final_url_suffix,
            ad_group_criterion.final_urls,
            ad_group_criterion.keyword.text,
            ad_group_criterion.keyword.match_type,
            ad_group_criterion.negative,
            ad_group_criterion.bid_modifier,
            ad_group_criterion.cpc_bid_micros,
            ad_group_criterion.cpm_bid_micros,
            ad_group_criterion.cpv_bid_micros,
            ad_group_criterion.percent_cpc_bid_micros,
            ad_group_criterion.tracking_url_template,
            ad_group_criterion.url_custom_parameters,
            ad_group_criterion.labels,
            ad_group_criterion.approval_status,
            ad_group_criterion.disapproval_reasons,
            ad_group_criterion.system_serving_status,
            ad_group_criterion.display_name,
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.conversions,
            metrics.all_conversions,
            metrics.average_cpc,
            metrics.average_cpm,
            metrics.average_cpv,
            metrics.average_cpe,
            metrics.ctr,
            metrics.cost_per_conversion,
            metrics.cost_per_all_conversions,
            metrics.conversions_value,
            metrics.all_conversions_value,
            metrics.conversions_by_conversion_date,
            metrics.value_per_conversion,
            metrics.value_per_all_conversions,
            metrics.value_per_conversions_by_conversion_date,
            metrics.all_conversions_from_interactions_rate,
            metrics.all_conversions_from_interactions_value_per_interaction,
            metrics.interaction_rate,
            metrics.interactions,
            metrics.interaction_event_types,
            metrics.engagement_rate,
            metrics.engagements,
            metrics.historical_creative_quality_score,
            metrics.historical_landing_page_quality_score,
            metrics.historical_quality_score,
            metrics.historical_search_predicted_ctr,
            metrics.absolute_top_impression_percentage,
            metrics.active_view_cpm,
            metrics.active_view_ctr,
            metrics.active_view_impressions,
            metrics.active_view_measurability,
            metrics.active_view_measurable_cost_micros,
            metrics.active_view_measurable_impressions,
            metrics.active_view_viewability,
            metrics.search_absolute_top_impression_share,
            metrics.search_budget_lost_absolute_top_impression_share,
            metrics.search_budget_lost_top_impression_share,
            metrics.search_exact_match_impression_share,
            metrics.search_impression_share,
            metrics.search_rank_lost_absolute_top_impression_share,
            metrics.search_rank_lost_impression_share,
            metrics.search_rank_lost_top_impression_share,
            metrics.search_top_impression_share,
            metrics.top_impression_percentage,
            metrics.view_through_conversions,
            segments.date,
            segments.day_of_week,
            segments.device,
            segments.ad_network_type,
            segments.click_type,
            segments.conversion_action,
            segments.conversion_action_category,
            segments.conversion_action_name,
            segments.external_conversion_source,
            segments.keyword.ad_group_criterion,
            segments.keyword.info.text,
            segments.keyword.info.match_type,
            segments.month,
            segments.quarter,
            segments.slot,
            segments.week,
            segments.year
        FROM keyword_view
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.impressions DESC
        LIMIT 1000
    """

    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        print("Campaign_Name,AdGroup_Name,Keyword,Match_Type,Status,Quality_Score,CPC_Bid,Clicks,Impressions,Cost,CTR,Conversions,Conv_Rate,Avg_CPC,First_Page_CPC,Top_Page_CPC,Device,Network,Date")

        for batch in response:
            for row in batch.results:
                campaign = row.campaign
                ad_group = row.ad_group
                criterion = row.ad_group_criterion
                keyword = criterion.keyword
                metrics = row.metrics
                segments = row.segments
                quality_info = criterion.quality_info
                position_estimates = criterion.position_estimates

                cost = metrics.cost_micros / 1_000_000 if metrics.cost_micros else 0
                avg_cpc = metrics.average_cpc / 1_000_000 if metrics.average_cpc else 0
                cpc_bid = criterion.cpc_bid_micros / 1_000_000 if criterion.cpc_bid_micros else 0
                first_page_cpc = position_estimates.first_page_cpc_micros / 1_000_000 if position_estimates.first_page_cpc_micros else 0
                top_page_cpc = position_estimates.top_of_page_cpc_micros / 1_000_000 if position_estimates.top_of_page_cpc_micros else 0
                quality_score = quality_info.quality_score if quality_info.quality_score else 0

                device = segments.device.name if hasattr(segments, 'device') else 'UNKNOWN'
                network = segments.ad_network_type.name if hasattr(segments, 'ad_network_type') else 'UNKNOWN'

                print(f"{campaign.name},{ad_group.name},{keyword.text},{keyword.match_type.name},"
                      f"{criterion.status.name},{quality_score},{cpc_bid:.2f},{metrics.clicks},"
                      f"{metrics.impressions},{cost:.2f},{metrics.ctr:.4f},{metrics.conversions:.2f},"
                      f"{(metrics.conversions/metrics.clicks if metrics.clicks > 0 else 0):.4f},{avg_cpc:.2f},{first_page_cpc:.2f},{top_page_cpc:.2f},"
                      f"{device},{network},{segments.date}")

    except GoogleAdsException as ex:
        print(f"[ERROR] Keyword query failed: {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in keywords: {e}")

def extract_search_terms(client, customer_id):
    """Extract all search term data with comprehensive fields."""
    print("[INFO] Extracting search terms...")

    ga_service = client.get_service("GoogleAdsService")

    query = """
        SELECT
            campaign.id,
            campaign.name,
            campaign.status,
            ad_group.id,
            ad_group.name,
            ad_group.status,
            segments.search_term_match_type,
            segments.keyword.ad_group_criterion,
            segments.keyword.info.text,
            segments.keyword.info.match_type,
            search_term_view.search_term,
            search_term_view.status,
            search_term_view.ad_group,
            metrics.clicks,
            metrics.impressions,
            metrics.cost_micros,
            metrics.conversions,
            metrics.all_conversions,
            metrics.average_cpc,
            metrics.average_cpm,
            metrics.average_cpv,
            metrics.average_cpe,
            metrics.ctr,
            metrics.cost_per_conversion,
            metrics.cost_per_all_conversions,
            metrics.conversions_value,
            metrics.all_conversions_value,
            metrics.conversions_by_conversion_date,
            metrics.value_per_conversion,
            metrics.value_per_all_conversions,
            metrics.value_per_conversions_by_conversion_date,
            metrics.all_conversions_from_interactions_rate,
            metrics.all_conversions_from_interactions_value_per_interaction,
            metrics.interaction_rate,
            metrics.interactions,
            metrics.interaction_event_types,
            metrics.engagement_rate,
            metrics.engagements,
            metrics.absolute_top_impression_percentage,
            metrics.cross_device_conversions,
            metrics.active_view_cpm,
            metrics.active_view_ctr,
            metrics.active_view_impressions,
            metrics.active_view_measurability,
            metrics.active_view_measurable_cost_micros,
            metrics.active_view_measurable_impressions,
            metrics.active_view_viewability,
            metrics.search_absolute_top_impression_share,
            metrics.search_budget_lost_absolute_top_impression_share,
            metrics.search_budget_lost_top_impression_share,
            metrics.search_exact_match_impression_share,
            metrics.search_impression_share,
            metrics.search_rank_lost_absolute_top_impression_share,
            metrics.search_rank_lost_impression_share,
            metrics.search_rank_lost_top_impression_share,
            metrics.search_top_impression_share,
            metrics.top_impression_percentage,
            metrics.video_view_rate,
            metrics.video_views,
            metrics.view_through_conversions,
            segments.date,
            segments.day_of_week,
            segments.device,
            segments.ad_network_type,
            segments.click_type,
            segments.conversion_action,
            segments.conversion_action_category,
            segments.conversion_action_name,
            segments.conversion_lag_bucket,
            segments.conversion_or_adjustment_lag_bucket,
            segments.external_conversion_source,
            segments.month,
            segments.quarter,
            segments.slot,
            segments.week,
            segments.year
        FROM search_term_view
        WHERE segments.date DURING LAST_30_DAYS
        ORDER BY metrics.impressions DESC
        LIMIT 1000
    """

    try:
        response = ga_service.search_stream(customer_id=customer_id, query=query)

        print("Campaign_Name,AdGroup_Name,Keyword,Keyword_Match_Type,Search_Term,Search_Term_Match_Type,Clicks,Impressions,Cost,CTR,Conversions,Conv_Rate,Avg_CPC,Device,Network,Date")

        for batch in response:
            for row in batch.results:
                campaign = row.campaign
                ad_group = row.ad_group
                search_term_view = row.search_term_view
                metrics = row.metrics
                segments = row.segments

                cost = metrics.cost_micros / 1_000_000 if metrics.cost_micros else 0
                avg_cpc = metrics.average_cpc / 1_000_000 if metrics.average_cpc else 0

                device = segments.device.name if hasattr(segments, 'device') else 'UNKNOWN'
                network = segments.ad_network_type.name if hasattr(segments, 'ad_network_type') else 'UNKNOWN'
                search_match_type = segments.search_term_match_type.name if hasattr(segments, 'search_term_match_type') else 'UNKNOWN'
                keyword_text = segments.keyword.info.text if hasattr(segments.keyword.info, 'text') else ''
                keyword_match = segments.keyword.info.match_type.name if hasattr(segments.keyword.info, 'match_type') else 'UNKNOWN'

                print(f"{campaign.name},{ad_group.name},{keyword_text},{keyword_match},"
                      f"{search_term_view.search_term},{search_match_type},{metrics.clicks},"
                      f"{metrics.impressions},{cost:.2f},{metrics.ctr:.4f},{metrics.conversions:.2f},"
                      f"{(metrics.conversions/metrics.clicks if metrics.clicks > 0 else 0):.4f},{avg_cpc:.2f},{device},{network},{segments.date}")

    except GoogleAdsException as ex:
        print(f"[ERROR] Search term query failed: {ex.error.code().name}")
        for error in ex.failure.errors:
            print(f"  Error: {error.message}")
    except Exception as e:
        print(f"[ERROR] Unexpected error in search terms: {e}")

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

    print(f"Starting Google Ads data extraction for Customer ID: {CUSTOMER_ID}")
    print("=" * 80)

    extract_campaigns(client, CUSTOMER_ID)
    print()

    extract_ad_groups(client, CUSTOMER_ID)
    print()

    extract_keywords(client, CUSTOMER_ID)
    print()

    extract_search_terms(client, CUSTOMER_ID)
    print()

    print("=" * 80)
    print("Done.")

if __name__ == "__main__":
    main()