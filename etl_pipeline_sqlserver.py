#!/usr/bin/env python3
"""
Google Ads ETL Pipeline for SQL Server
Extracts data from Google Ads API and loads into SQL Server dimensional model
"""

import os
import sys
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from loguru import logger
from dotenv import load_dotenv
from db_connection import db
import warnings

warnings.filterwarnings('ignore')
load_dotenv()

class GoogleAdsETLPipeline:
    def __init__(self):
        """Initialize ETL pipeline for SQL Server"""
        try:
            self.client = GoogleAdsClient.load_from_storage("google-ads.yaml")
            self.ga_service = self.client.get_service("GoogleAdsService")
            self.manager_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID", "3341907700")
            self.db = db

            logger.info("ETL Pipeline initialized for SQL Server")

            if not self.db.test_connection():
                logger.error("Failed to connect to SQL Server")
                sys.exit(1)

        except Exception as e:
            logger.error(f"Failed to initialize ETL pipeline: {e}")
            sys.exit(1)

    def get_accessible_customers(self):
        """Get list of accessible customer accounts"""
        query = """
            SELECT
                customer_client.id,
                customer_client.descriptive_name,
                customer_client.level,
                customer_client.manager,
                customer_client.status
            FROM customer_client
            WHERE customer_client.level <= 1
        """

        try:
            response = self.ga_service.search_stream(
                customer_id=self.manager_id,
                query=query
            )

            customers = []
            for batch in response:
                for row in batch.results:
                    if row.customer_client.status.name == "ENABLED":
                        customers.append({
                            'customer_id': str(row.customer_client.id),
                            'customer_name': row.customer_client.descriptive_name,
                            'is_manager': row.customer_client.manager
                        })

            logger.info(f"Found {len(customers)} accessible customer accounts")
            return customers
        except GoogleAdsException as ex:
            logger.error(f"Failed to get accessible customers: {ex}")
            return []

    def extract_campaigns(self, customer_id):
        """Extract campaign data"""
        query = """
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign.advertising_channel_sub_type,
                campaign.start_date,
                campaign.end_date,
                campaign.campaign_budget.amount_micros,
                campaign.bidding_strategy_type,
                campaign.target_cpa.target_cpa_micros,
                campaign.target_roas.target_roas,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                segments.date
            FROM campaign
            WHERE segments.date DURING LAST_30_DAYS
                AND campaign.status != 'REMOVED'
        """

        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id,
                query=query
            )

            campaigns_data = []
            performance_data = []

            for batch in response:
                for row in batch.results:
                    campaign = row.campaign
                    metrics = row.metrics
                    segment_date = row.segments.date

                    # Campaign dimension
                    campaign_dict = {
                        'CampaignID': campaign.id,
                        'CampaignName': campaign.name,
                        'CampaignStatus': campaign.status.name,
                        'CampaignType': campaign.advertising_channel_type.name,
                        'AdvertisingChannelType': campaign.advertising_channel_sub_type if campaign.advertising_channel_sub_type else None,
                        'StartDate': campaign.start_date if campaign.start_date else None,
                        'EndDate': campaign.end_date if campaign.end_date else None,
                        'BudgetAmount': campaign.campaign_budget.amount_micros / 1000000 if campaign.campaign_budget.amount_micros else 0,
                        'BiddingStrategy': campaign.bidding_strategy_type.name,
                        'TargetCPA': campaign.target_cpa.target_cpa_micros / 1000000 if campaign.target_cpa.target_cpa_micros else None,
                        'TargetROAS': campaign.target_roas.target_roas if campaign.target_roas.target_roas else None,
                        'IsActive': 1 if campaign.status.name == 'ENABLED' else 0
                    }
                    campaigns_data.append(campaign_dict)

                    # Performance fact
                    performance_dict = {
                        'Date': segment_date,
                        'CampaignID': campaign.id,
                        'Impressions': metrics.impressions,
                        'Clicks': metrics.clicks,
                        'Cost': metrics.cost_micros / 1000000,
                        'Conversions': metrics.conversions,
                        'ConversionValue': metrics.conversions_value
                    }
                    performance_data.append(performance_dict)

            return pd.DataFrame(campaigns_data), pd.DataFrame(performance_data)

        except GoogleAdsException as ex:
            logger.error(f"Failed to extract campaigns for customer {customer_id}: {ex}")
            return pd.DataFrame(), pd.DataFrame()

    def extract_ad_groups(self, customer_id):
        """Extract ad group data"""
        query = """
            SELECT
                ad_group.id,
                ad_group.name,
                ad_group.campaign,
                ad_group.status,
                ad_group.type,
                ad_group.cpc_bid_micros,
                ad_group.cpm_bid_micros,
                ad_group.target_cpa.target_cpa_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.average_cpc,
                segments.date
            FROM ad_group
            WHERE segments.date DURING LAST_30_DAYS
                AND ad_group.status != 'REMOVED'
        """

        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id,
                query=query
            )

            ad_groups_data = []
            performance_data = []

            for batch in response:
                for row in batch.results:
                    ad_group = row.ad_group
                    metrics = row.metrics
                    segment_date = row.segments.date

                    # Extract campaign ID from resource name
                    campaign_id = int(ad_group.campaign.split('/')[-1])

                    # Ad group dimension
                    ad_group_dict = {
                        'AdGroupID': ad_group.id,
                        'AdGroupName': ad_group.name,
                        'CampaignID': campaign_id,
                        'AdGroupStatus': ad_group.status.name,
                        'AdGroupType': ad_group.type.name,
                        'MaxCPC': ad_group.cpc_bid_micros / 1000000 if ad_group.cpc_bid_micros else None,
                        'MaxCPM': ad_group.cpm_bid_micros / 1000000 if ad_group.cpm_bid_micros else None,
                        'TargetCPA': ad_group.target_cpa.target_cpa_micros / 1000000 if ad_group.target_cpa.target_cpa_micros else None,
                        'IsActive': 1 if ad_group.status.name == 'ENABLED' else 0
                    }
                    ad_groups_data.append(ad_group_dict)

                    # Performance fact
                    performance_dict = {
                        'Date': segment_date,
                        'AdGroupID': ad_group.id,
                        'CampaignID': campaign_id,
                        'Impressions': metrics.impressions,
                        'Clicks': metrics.clicks,
                        'Cost': metrics.cost_micros / 1000000,
                        'Conversions': metrics.conversions,
                        'ConversionValue': metrics.conversions_value,
                        'AvgPosition': None  # Not available in newer API versions
                    }
                    performance_data.append(performance_dict)

            return pd.DataFrame(ad_groups_data), pd.DataFrame(performance_data)

        except GoogleAdsException as ex:
            logger.error(f"Failed to extract ad groups for customer {customer_id}: {ex}")
            return pd.DataFrame(), pd.DataFrame()

    def extract_keywords(self, customer_id):
        """Extract keyword data"""
        query = """
            SELECT
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.status,
                ad_group_criterion.quality_info.quality_score,
                ad_group_criterion.position_estimates.first_page_cpc_micros,
                ad_group_criterion.position_estimates.top_of_page_cpc_micros,
                ad_group_criterion.ad_group,
                ad_group_criterion.cpc_bid_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.average_position,
                segments.date
            FROM ad_group_criterion
            WHERE ad_group_criterion.type = 'KEYWORD'
                AND segments.date DURING LAST_30_DAYS
                AND ad_group_criterion.status != 'REMOVED'
        """

        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id,
                query=query
            )

            keywords_data = []
            performance_data = []

            for batch in response:
                for row in batch.results:
                    criterion = row.ad_group_criterion
                    metrics = row.metrics
                    segment_date = row.segments.date

                    # Extract ad group ID from resource name
                    ad_group_id = int(criterion.ad_group.split('/')[-1])

                    # Keyword dimension
                    keyword_dict = {
                        'KeywordID': str(criterion.criterion_id),
                        'Keyword': criterion.keyword.text,
                        'AdGroupID': ad_group_id,
                        'MatchType': criterion.keyword.match_type.name,
                        'Status': criterion.status.name,
                        'MaxCPC': criterion.cpc_bid_micros / 1000000 if criterion.cpc_bid_micros else None,
                        'QualityScore': criterion.quality_info.quality_score if criterion.quality_info.quality_score else None,
                        'FirstPageBid': criterion.position_estimates.first_page_cpc_micros / 1000000 if criterion.position_estimates.first_page_cpc_micros else None,
                        'TopOfPageBid': criterion.position_estimates.top_of_page_cpc_micros / 1000000 if criterion.position_estimates.top_of_page_cpc_micros else None,
                        'IsActive': 1 if criterion.status.name == 'ENABLED' else 0
                    }
                    keywords_data.append(keyword_dict)

                    # Performance fact
                    performance_dict = {
                        'Date': segment_date,
                        'KeywordID': str(criterion.criterion_id),
                        'AdGroupID': ad_group_id,
                        'Impressions': metrics.impressions,
                        'Clicks': metrics.clicks,
                        'Cost': metrics.cost_micros / 1000000,
                        'Conversions': metrics.conversions,
                        'ConversionValue': metrics.conversions_value,
                        'AvgPosition': metrics.average_position if metrics.average_position else None,
                        'QualityScore': criterion.quality_info.quality_score if criterion.quality_info.quality_score else None
                    }
                    performance_data.append(performance_dict)

            return pd.DataFrame(keywords_data), pd.DataFrame(performance_data)

        except GoogleAdsException as ex:
            logger.error(f"Failed to extract keywords for customer {customer_id}: {ex}")
            return pd.DataFrame(), pd.DataFrame()

    def extract_ads(self, customer_id):
        """Extract ad creative data"""
        query = """
            SELECT
                ad_group_ad.ad.id,
                ad_group_ad.ad.type,
                ad_group_ad.ad.expanded_text_ad.headline_part1,
                ad_group_ad.ad.expanded_text_ad.headline_part2,
                ad_group_ad.ad.expanded_text_ad.headline_part3,
                ad_group_ad.ad.expanded_text_ad.description,
                ad_group_ad.ad.expanded_text_ad.description2,
                ad_group_ad.ad.responsive_search_ad.headlines,
                ad_group_ad.ad.responsive_search_ad.descriptions,
                ad_group_ad.ad.final_urls,
                ad_group_ad.ad.display_url,
                ad_group_ad.ad_group,
                ad_group_ad.status,
                ad_group_ad.policy_summary.approval_status,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.all_conversions,
                segments.date
            FROM ad_group_ad
            WHERE segments.date DURING LAST_30_DAYS
                AND ad_group_ad.status != 'REMOVED'
        """

        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id,
                query=query
            )

            ads_data = []
            performance_data = []

            for batch in response:
                for row in batch.results:
                    ad = row.ad_group_ad.ad
                    ad_group_ad = row.ad_group_ad
                    metrics = row.metrics
                    segment_date = row.segments.date

                    # Extract ad group ID from resource name
                    ad_group_id = int(ad_group_ad.ad_group.split('/')[-1])

                    # Extract ad text based on ad type
                    headlines = []
                    descriptions = []

                    if ad.type.name == "EXPANDED_TEXT_AD":
                        if ad.expanded_text_ad.headline_part1:
                            headlines.append(ad.expanded_text_ad.headline_part1)
                        if ad.expanded_text_ad.headline_part2:
                            headlines.append(ad.expanded_text_ad.headline_part2)
                        if ad.expanded_text_ad.headline_part3:
                            headlines.append(ad.expanded_text_ad.headline_part3)
                        if ad.expanded_text_ad.description:
                            descriptions.append(ad.expanded_text_ad.description)
                        if ad.expanded_text_ad.description2:
                            descriptions.append(ad.expanded_text_ad.description2)
                    elif ad.type.name == "RESPONSIVE_SEARCH_AD":
                        headlines = [h.text for h in ad.responsive_search_ad.headlines]
                        descriptions = [d.text for d in ad.responsive_search_ad.descriptions]

                    # Ad dimension
                    ad_dict = {
                        'AdID': ad.id,
                        'AdType': ad.type.name,
                        'Headlines': ' | '.join(headlines),
                        'Descriptions': ' | '.join(descriptions),
                        'FinalURL': ad.final_urls[0] if ad.final_urls else None,
                        'DisplayURL': ad.display_url if ad.display_url else None,
                        'AdGroupID': ad_group_id,
                        'AdStatus': ad_group_ad.status.name,
                        'ApprovalStatus': ad_group_ad.policy_summary.approval_status.name if ad_group_ad.policy_summary else 'UNKNOWN',
                        'IsActive': 1 if ad_group_ad.status.name == 'ENABLED' else 0
                    }
                    ads_data.append(ad_dict)

                    # Performance fact
                    performance_dict = {
                        'Date': segment_date,
                        'AdID': ad.id,
                        'AdGroupID': ad_group_id,
                        'Impressions': metrics.impressions,
                        'Clicks': metrics.clicks,
                        'Cost': metrics.cost_micros / 1000000,
                        'Conversions': metrics.conversions,
                        'ConversionValue': metrics.conversions_value,
                        'AllConversions': metrics.all_conversions
                    }
                    performance_data.append(performance_dict)

            return pd.DataFrame(ads_data), pd.DataFrame(performance_data)

        except GoogleAdsException as ex:
            logger.error(f"Failed to extract ads for customer {customer_id}: {ex}")
            return pd.DataFrame(), pd.DataFrame()

    def extract_search_terms(self, customer_id):
        """Extract search terms report data"""
        query = """
            SELECT
                search_term_view.search_term,
                search_term_view.ad_group,
                search_term_view.campaign,
                search_term_view.status,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc,
                metrics.conversion_rate,
                segments.date,
                segments.keyword.info.text,
                segments.keyword.info.match_type
            FROM search_term_view
            WHERE segments.date DURING LAST_30_DAYS
                AND metrics.impressions > 0
        """

        try:
            response = self.ga_service.search_stream(
                customer_id=customer_id,
                query=query
            )

            search_terms_data = []

            for batch in response:
                for row in batch.results:
                    search_term = row.search_term_view
                    metrics = row.metrics
                    segment_date = row.segments.date
                    keyword_info = row.segments.keyword.info if hasattr(row.segments, 'keyword') else None

                    # Extract IDs from resource names
                    ad_group_id = int(search_term.ad_group.split('/')[-1]) if search_term.ad_group else None
                    campaign_id = int(search_term.campaign.split('/')[-1]) if search_term.campaign else None

                    search_term_dict = {
                        'Date': segment_date,
                        'SearchTerm': search_term.search_term,
                        'CampaignID': campaign_id,
                        'AdGroupID': ad_group_id,
                        'Status': search_term.status.name if search_term.status else 'UNKNOWN',
                        'TriggeringKeyword': keyword_info.text if keyword_info else None,
                        'MatchType': keyword_info.match_type.name if keyword_info else None,
                        'Impressions': metrics.impressions,
                        'Clicks': metrics.clicks,
                        'Cost': metrics.cost_micros / 1000000,
                        'Conversions': metrics.conversions,
                        'ConversionValue': metrics.conversions_value,
                        'CTR': metrics.ctr,
                        'AvgCPC': metrics.average_cpc,
                        'ConversionRate': metrics.conversion_rate
                    }
                    search_terms_data.append(search_term_dict)

            return pd.DataFrame(search_terms_data)

        except GoogleAdsException as ex:
            logger.error(f"Failed to extract search terms for customer {customer_id}: {ex}")
            return pd.DataFrame()

    def load_dimensions(self, campaigns_df, ad_groups_df, keywords_df, ads_df=None):
        """Load dimension tables into SQL Server"""
        try:
            # Load campaigns
            if not campaigns_df.empty:
                campaigns_df.drop_duplicates(subset=['CampaignID'], inplace=True)
                self.db.bulk_insert('DimCampaign', campaigns_df, schema='dw')
                logger.info(f"Loaded {len(campaigns_df)} campaigns")

            # Load ad groups
            if not ad_groups_df.empty:
                ad_groups_df.drop_duplicates(subset=['AdGroupID'], inplace=True)
                self.db.bulk_insert('DimAdGroup', ad_groups_df, schema='dw')
                logger.info(f"Loaded {len(ad_groups_df)} ad groups")

            # Load keywords
            if not keywords_df.empty:
                keywords_df.drop_duplicates(subset=['KeywordID'], inplace=True)
                self.db.bulk_insert('DimKeyword', keywords_df, schema='dw')
                logger.info(f"Loaded {len(keywords_df)} keywords")

            # Load ads
            if ads_df is not None and not ads_df.empty:
                ads_df.drop_duplicates(subset=['AdID'], inplace=True)
                self.db.bulk_insert('DimAd', ads_df, schema='dw')
                logger.info(f"Loaded {len(ads_df)} ads")

        except Exception as e:
            logger.error(f"Error loading dimensions: {e}")
            raise

    def load_facts(self, campaign_perf_df, ad_group_perf_df, keyword_perf_df, ad_perf_df=None, search_terms_df=None):
        """Load fact tables into SQL Server"""
        try:
            # Process dates for all dataframes
            all_dfs = [campaign_perf_df, ad_group_perf_df, keyword_perf_df]
            if ad_perf_df is not None:
                all_dfs.append(ad_perf_df)
            if search_terms_df is not None:
                all_dfs.append(search_terms_df)

            for df in all_dfs:
                if not df.empty and 'Date' in df.columns:
                    df['DateKey'] = pd.to_datetime(df['Date']).dt.strftime('%Y%m%d').astype(int)

            # Map IDs to dimension keys (simplified - in production you'd do proper lookups)
            if not campaign_perf_df.empty:
                campaign_perf_df['CampaignKey'] = campaign_perf_df['CampaignID']
                self.db.bulk_insert('FactCampaignPerformance', campaign_perf_df, schema='dw')
                logger.info(f"Loaded {len(campaign_perf_df)} campaign performance records")

            if not ad_group_perf_df.empty:
                ad_group_perf_df['AdGroupKey'] = ad_group_perf_df['AdGroupID']
                ad_group_perf_df['CampaignKey'] = ad_group_perf_df['CampaignID']
                self.db.bulk_insert('FactAdGroupPerformance', ad_group_perf_df, schema='dw')
                logger.info(f"Loaded {len(ad_group_perf_df)} ad group performance records")

            if not keyword_perf_df.empty:
                keyword_perf_df['KeywordKey'] = keyword_perf_df['KeywordID']
                keyword_perf_df['AdGroupKey'] = keyword_perf_df['AdGroupID']
                keyword_perf_df['CampaignKey'] = keyword_perf_df.get('CampaignID', 0)
                self.db.bulk_insert('FactKeywordPerformance', keyword_perf_df, schema='dw')
                logger.info(f"Loaded {len(keyword_perf_df)} keyword performance records")

            # Load ad performance
            if ad_perf_df is not None and not ad_perf_df.empty:
                ad_perf_df['AdKey'] = ad_perf_df['AdID']
                ad_perf_df['AdGroupKey'] = ad_perf_df['AdGroupID']
                self.db.bulk_insert('FactAdPerformance', ad_perf_df, schema='dw')
                logger.info(f"Loaded {len(ad_perf_df)} ad performance records")

            # Load search terms
            if search_terms_df is not None and not search_terms_df.empty:
                self.db.bulk_insert('FactSearchTermPerformance', search_terms_df, schema='dw')
                logger.info(f"Loaded {len(search_terms_df)} search term records")

        except Exception as e:
            logger.error(f"Error loading facts: {e}")
            raise

    def run_etl(self):
        """Run the complete ETL pipeline"""
        logger.info("Starting Google Ads ETL Pipeline for SQL Server")

        try:
            # Get accessible customers
            customers = self.get_accessible_customers()

            if not customers:
                logger.warning("No accessible customers found")
                return

            # Process each customer
            for customer in customers:
                if customer['is_manager']:
                    continue

                customer_id = customer['customer_id']
                customer_name = customer['customer_name']

                logger.info(f"Processing customer: {customer_name} ({customer_id})")

                # Extract data
                campaigns_df, campaign_perf_df = self.extract_campaigns(customer_id)
                ad_groups_df, ad_group_perf_df = self.extract_ad_groups(customer_id)
                keywords_df, keyword_perf_df = self.extract_keywords(customer_id)
                ads_df, ad_perf_df = self.extract_ads(customer_id)
                search_terms_df = self.extract_search_terms(customer_id)

                # Load dimensions
                self.load_dimensions(campaigns_df, ad_groups_df, keywords_df, ads_df)

                # Load facts
                self.load_facts(campaign_perf_df, ad_group_perf_df, keyword_perf_df, ad_perf_df, search_terms_df)

                logger.info(f"Completed processing for customer: {customer_name}")

            logger.info("ETL Pipeline completed successfully")

        except Exception as e:
            logger.error(f"ETL Pipeline failed: {e}")
            raise

if __name__ == "__main__":
    etl = GoogleAdsETLPipeline()
    etl.run_etl()