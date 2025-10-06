"""
Ad Group data collection tools for Data Agent
"""
from typing import Dict, List, Any, Optional
from langchain.tools import Tool
from loguru import logger
import pandas as pd
from datetime import datetime


class AdGroupTools:
    """Tools for fetching ad group data from Google Ads API"""

    def __init__(self, google_ads_manager):
        """
        Initialize ad group tools

        Args:
            google_ads_manager: GoogleAdsManager instance
        """
        self.gam = google_ads_manager

    def fetch_adgroup_data(
        self,
        customer_id: str,
        campaign_ids: Optional[List[str]] = None,
        date_range: str = "LAST_30_DAYS"
    ) -> Dict[str, Any]:
        """
        Fetch ad group data from Google Ads

        Args:
            customer_id: Google Ads customer ID
            campaign_ids: Optional list of campaign IDs to filter
            date_range: Date range for data

        Returns:
            Dictionary with ad group data
        """
        try:
            # Build campaign filter
            campaign_filter = ""
            if campaign_ids:
                ids_str = ", ".join([f"'{id}'" for id in campaign_ids])
                campaign_filter = f"AND campaign.id IN ({ids_str})"

            query = f"""
                SELECT
                    ad_group.id,
                    ad_group.name,
                    ad_group.campaign,
                    ad_group.status,
                    ad_group.type,
                    ad_group.cpc_bid_micros,
                    ad_group.cpm_bid_micros,
                    ad_group.target_cpa.target_cpa_micros,
                    ad_group.target_roas.target_roas,
                    ad_group.percent_cpc_bid_micros,
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.average_cpc,
                    metrics.average_cpm,
                    metrics.ctr,
                    metrics.conversion_rate,
                    segments.date
                FROM ad_group
                WHERE segments.date DURING {date_range}
                    AND ad_group.status != 'REMOVED'
                    {campaign_filter}
                ORDER BY metrics.cost_micros DESC
            """

            # Execute query
            results = list(self.gam.execute_query(customer_id, query))

            # Process results
            ad_groups = []
            performance_data = []

            for row in results:
                ad_group = row.get('ad_group', {})
                campaign = row.get('campaign', {})
                metrics = row.get('metrics', {})
                segments = row.get('segments', {})

                # Extract campaign ID from resource name
                campaign_resource = ad_group.get('campaign', '')
                campaign_id = campaign_resource.split('/')[-1] if campaign_resource else campaign.get('id')

                # Ad group dimension data
                ad_group_info = {
                    'ad_group_id': ad_group.get('id'),
                    'ad_group_name': ad_group.get('name'),
                    'campaign_id': campaign_id,
                    'campaign_name': campaign.get('name'),
                    'status': ad_group.get('status'),
                    'type': ad_group.get('type'),
                    'max_cpc': ad_group.get('cpc_bid_micros', 0) / 1_000_000 if ad_group.get('cpc_bid_micros') else None,
                    'max_cpm': ad_group.get('cpm_bid_micros', 0) / 1_000_000 if ad_group.get('cpm_bid_micros') else None,
                    'target_cpa': ad_group.get('target_cpa', {}).get('target_cpa_micros', 0) / 1_000_000 if ad_group.get('target_cpa') else None,
                    'target_roas': ad_group.get('target_roas', {}).get('target_roas') if ad_group.get('target_roas') else None,
                    'percent_cpc_bid': ad_group.get('percent_cpc_bid_micros', 0) / 1_000_000 if ad_group.get('percent_cpc_bid_micros') else None
                }
                ad_groups.append(ad_group_info)

                # Performance data
                perf_data = {
                    'date': segments.get('date'),
                    'ad_group_id': ad_group.get('id'),
                    'campaign_id': campaign_id,
                    'impressions': metrics.get('impressions', 0),
                    'clicks': metrics.get('clicks', 0),
                    'cost': metrics.get('cost_micros', 0) / 1_000_000,
                    'conversions': metrics.get('conversions', 0),
                    'conversion_value': metrics.get('conversions_value', 0),
                    'avg_cpc': metrics.get('average_cpc', 0) / 1_000_000 if metrics.get('average_cpc') else 0,
                    'avg_cpm': metrics.get('average_cpm', 0) / 1_000_000 if metrics.get('average_cpm') else 0,
                    'ctr': metrics.get('ctr', 0),
                    'conversion_rate': metrics.get('conversion_rate', 0)
                }
                performance_data.append(perf_data)

            # Create DataFrames
            ad_groups_df = pd.DataFrame(ad_groups).drop_duplicates(subset=['ad_group_id'])
            performance_df = pd.DataFrame(performance_data)

            # Calculate aggregated metrics
            if not performance_df.empty:
                aggregated = performance_df.groupby('ad_group_id').agg({
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'cost': 'sum',
                    'conversions': 'sum',
                    'conversion_value': 'sum'
                }).reset_index()

                # Calculate derived metrics
                aggregated['ctr'] = (aggregated['clicks'] / aggregated['impressions'] * 100).fillna(0)
                aggregated['conversion_rate'] = (aggregated['conversions'] / aggregated['clicks'] * 100).fillna(0)
                aggregated['avg_cpc'] = (aggregated['cost'] / aggregated['clicks']).fillna(0)
                aggregated['roas'] = (aggregated['conversion_value'] / aggregated['cost']).fillna(0)

                # Merge with ad group info
                ad_groups_df = ad_groups_df.merge(aggregated, on='ad_group_id', how='left')

            logger.info(f"Fetched {len(ad_groups_df)} ad groups for customer {customer_id}")

            return {
                'ad_groups': ad_groups_df.to_dict('records'),
                'performance_data': performance_df.to_dict('records'),
                'summary': {
                    'total_ad_groups': len(ad_groups_df),
                    'active_ad_groups': len(ad_groups_df[ad_groups_df['status'] == 'ENABLED']),
                    'total_cost': performance_df['cost'].sum() if not performance_df.empty else 0,
                    'total_conversions': performance_df['conversions'].sum() if not performance_df.empty else 0
                },
                'customer_id': customer_id,
                'date_range': date_range,
                'fetched_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching ad group data: {str(e)}")
            return {
                'error': str(e),
                'ad_groups': [],
                'performance_data': [],
                'customer_id': customer_id
            }

    def fetch_adgroup_demographics(
        self,
        customer_id: str,
        ad_group_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Fetch ad group demographic performance data

        Args:
            customer_id: Google Ads customer ID
            ad_group_ids: Optional list of ad group IDs to filter

        Returns:
            Dictionary with demographic data
        """
        try:
            # Build ad group filter
            ad_group_filter = ""
            if ad_group_ids:
                ids_str = ", ".join([f"'{id}'" for id in ad_group_ids])
                ad_group_filter = f"AND ad_group.id IN ({ids_str})"

            query = f"""
                SELECT
                    ad_group.id,
                    ad_group.name,
                    segments.demographic.age_range,
                    segments.demographic.gender,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.ctr,
                    metrics.conversion_rate
                FROM ad_group
                WHERE segments.date DURING LAST_30_DAYS
                    AND ad_group.status = 'ENABLED'
                    {ad_group_filter}
            """

            # Execute query
            results = list(self.gam.execute_query(customer_id, query))

            # Process demographic data
            demographic_data = []

            for row in results:
                ad_group = row.get('ad_group', {})
                segments = row.get('segments', {})
                metrics = row.get('metrics', {})

                demographic = segments.get('demographic', {})

                demographic_data.append({
                    'ad_group_id': ad_group.get('id'),
                    'ad_group_name': ad_group.get('name'),
                    'age_range': demographic.get('age_range', 'UNKNOWN'),
                    'gender': demographic.get('gender', 'UNKNOWN'),
                    'impressions': metrics.get('impressions', 0),
                    'clicks': metrics.get('clicks', 0),
                    'cost': metrics.get('cost_micros', 0) / 1_000_000,
                    'conversions': metrics.get('conversions', 0),
                    'conversion_value': metrics.get('conversions_value', 0),
                    'ctr': metrics.get('ctr', 0),
                    'conversion_rate': metrics.get('conversion_rate', 0)
                })

            # Create DataFrame for analysis
            demo_df = pd.DataFrame(demographic_data)

            # Aggregate by demographics
            age_performance = {}
            gender_performance = {}

            if not demo_df.empty:
                # Age range performance
                age_groups = demo_df.groupby('age_range').agg({
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'cost': 'sum',
                    'conversions': 'sum',
                    'conversion_value': 'sum'
                }).reset_index()
                age_performance = age_groups.to_dict('records')

                # Gender performance
                gender_groups = demo_df.groupby('gender').agg({
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'cost': 'sum',
                    'conversions': 'sum',
                    'conversion_value': 'sum'
                }).reset_index()
                gender_performance = gender_groups.to_dict('records')

            return {
                'demographic_data': demographic_data,
                'age_performance': age_performance,
                'gender_performance': gender_performance,
                'customer_id': customer_id,
                'fetched_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching ad group demographic data: {str(e)}")
            return {
                'error': str(e),
                'demographic_data': [],
                'customer_id': customer_id
            }

    def get_tools(self) -> List[Tool]:
        """
        Get LangChain tools for ad group data collection

        Returns:
            List of Tool objects
        """
        return [
            Tool(
                name="fetch_adgroup_data",
                func=self.fetch_adgroup_data,
                description="""Fetch ad group data from Google Ads API.
                Args: customer_id (str), campaign_ids (optional list), date_range (str)
                Returns: Dictionary with ad groups list, performance data, and summary"""
            ),
            Tool(
                name="fetch_adgroup_demographics",
                func=self.fetch_adgroup_demographics,
                description="""Fetch ad group demographic performance data.
                Args: customer_id (str), ad_group_ids (optional list)
                Returns: Dictionary with demographic performance breakdown"""
            )
        ]