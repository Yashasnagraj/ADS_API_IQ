"""
Campaign data collection tools for Data Agent
"""
from typing import Dict, List, Any, Optional
from langchain.tools import Tool
from loguru import logger
import pandas as pd
from datetime import datetime, timedelta


class CampaignTools:
    """Tools for fetching campaign data from Google Ads API"""

    def __init__(self, google_ads_manager):
        """
        Initialize campaign tools

        Args:
            google_ads_manager: GoogleAdsManager instance
        """
        self.gam = google_ads_manager

    def fetch_campaign_data(
        self,
        customer_id: str,
        date_range: str = "LAST_30_DAYS",
        include_paused: bool = False
    ) -> Dict[str, Any]:
        """
        Fetch campaign data from Google Ads

        Args:
            customer_id: Google Ads customer ID
            date_range: Date range for data
            include_paused: Include paused campaigns

        Returns:
            Dictionary with campaign data
        """
        try:
            # Build query
            status_filter = "" if include_paused else "AND campaign.status = 'ENABLED'"

            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.status,
                    campaign.advertising_channel_type,
                    campaign.advertising_channel_sub_type,
                    campaign.bidding_strategy_type,
                    campaign.campaign_budget.amount_micros,
                    campaign.target_cpa.target_cpa_micros,
                    campaign.target_roas.target_roas,
                    campaign.start_date,
                    campaign.end_date,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.conversion_rate,
                    metrics.cost_per_conversion,
                    segments.date
                FROM campaign
                WHERE segments.date DURING {date_range}
                    {status_filter}
                ORDER BY metrics.cost_micros DESC
            """

            # Execute query
            results = list(self.gam.execute_query(customer_id, query))

            # Process results
            campaigns = []
            performance_data = []

            for row in results:
                campaign = row.get('campaign', {})
                metrics = row.get('metrics', {})
                segments = row.get('segments', {})

                # Campaign dimension data
                campaign_info = {
                    'campaign_id': campaign.get('id'),
                    'campaign_name': campaign.get('name'),
                    'status': campaign.get('status'),
                    'channel_type': campaign.get('advertising_channel_type'),
                    'channel_subtype': campaign.get('advertising_channel_sub_type'),
                    'bidding_strategy': campaign.get('bidding_strategy_type'),
                    'budget': campaign.get('campaign_budget', {}).get('amount_micros', 0) / 1_000_000,
                    'target_cpa': campaign.get('target_cpa', {}).get('target_cpa_micros', 0) / 1_000_000 if campaign.get('target_cpa') else None,
                    'target_roas': campaign.get('target_roas', {}).get('target_roas') if campaign.get('target_roas') else None,
                    'start_date': campaign.get('start_date'),
                    'end_date': campaign.get('end_date')
                }
                campaigns.append(campaign_info)

                # Performance data
                perf_data = {
                    'date': segments.get('date'),
                    'campaign_id': campaign.get('id'),
                    'impressions': metrics.get('impressions', 0),
                    'clicks': metrics.get('clicks', 0),
                    'cost': metrics.get('cost_micros', 0) / 1_000_000,
                    'conversions': metrics.get('conversions', 0),
                    'conversion_value': metrics.get('conversions_value', 0),
                    'ctr': metrics.get('ctr', 0),
                    'avg_cpc': metrics.get('average_cpc', 0) / 1_000_000 if metrics.get('average_cpc') else 0,
                    'conversion_rate': metrics.get('conversion_rate', 0),
                    'cost_per_conversion': metrics.get('cost_per_conversion', 0) / 1_000_000 if metrics.get('cost_per_conversion') else 0
                }
                performance_data.append(perf_data)

            # Create DataFrames
            campaigns_df = pd.DataFrame(campaigns).drop_duplicates(subset=['campaign_id'])
            performance_df = pd.DataFrame(performance_data)

            # Calculate aggregated metrics
            if not performance_df.empty:
                aggregated = performance_df.groupby('campaign_id').agg({
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

                # Merge with campaign info
                campaigns_df = campaigns_df.merge(aggregated, on='campaign_id', how='left')

            logger.info(f"Fetched {len(campaigns_df)} campaigns for customer {customer_id}")

            return {
                'campaigns': campaigns_df.to_dict('records'),
                'performance_data': performance_df.to_dict('records'),
                'summary': {
                    'total_campaigns': len(campaigns_df),
                    'active_campaigns': len(campaigns_df[campaigns_df['status'] == 'ENABLED']),
                    'total_cost': performance_df['cost'].sum() if not performance_df.empty else 0,
                    'total_conversions': performance_df['conversions'].sum() if not performance_df.empty else 0,
                    'total_conversion_value': performance_df['conversion_value'].sum() if not performance_df.empty else 0
                },
                'customer_id': customer_id,
                'date_range': date_range,
                'fetched_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching campaign data: {str(e)}")
            return {
                'error': str(e),
                'campaigns': [],
                'performance_data': [],
                'customer_id': customer_id
            }

    def fetch_campaign_budget_data(
        self,
        customer_id: str,
        campaign_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Fetch campaign budget utilization data

        Args:
            customer_id: Google Ads customer ID
            campaign_ids: Optional list of campaign IDs to filter

        Returns:
            Dictionary with budget data
        """
        try:
            # Build campaign filter
            campaign_filter = ""
            if campaign_ids:
                ids_str = ", ".join(campaign_ids)
                campaign_filter = f"AND campaign.id IN ({ids_str})"

            query = f"""
                SELECT
                    campaign.id,
                    campaign.name,
                    campaign.campaign_budget.amount_micros,
                    campaign.campaign_budget.delivery_method,
                    campaign.campaign_budget.period,
                    metrics.cost_micros,
                    segments.date
                FROM campaign
                WHERE segments.date DURING LAST_7_DAYS
                    AND campaign.status = 'ENABLED'
                    {campaign_filter}
            """

            # Execute query
            results = list(self.gam.execute_query(customer_id, query))

            # Process budget data
            budget_data = {}
            for row in results:
                campaign = row.get('campaign', {})
                metrics = row.get('metrics', {})
                segments = row.get('segments', {})

                campaign_id = str(campaign.get('id'))

                if campaign_id not in budget_data:
                    budget_data[campaign_id] = {
                        'campaign_id': campaign_id,
                        'campaign_name': campaign.get('name'),
                        'daily_budget': campaign.get('campaign_budget', {}).get('amount_micros', 0) / 1_000_000,
                        'delivery_method': campaign.get('campaign_budget', {}).get('delivery_method', 'STANDARD'),
                        'period': campaign.get('campaign_budget', {}).get('period', 'DAILY'),
                        'daily_spend': []
                    }

                budget_data[campaign_id]['daily_spend'].append({
                    'date': segments.get('date'),
                    'cost': metrics.get('cost_micros', 0) / 1_000_000
                })

            # Calculate budget utilization
            for campaign_id, data in budget_data.items():
                daily_spend_df = pd.DataFrame(data['daily_spend'])
                if not daily_spend_df.empty:
                    data['avg_daily_spend'] = daily_spend_df['cost'].mean()
                    data['max_daily_spend'] = daily_spend_df['cost'].max()
                    data['min_daily_spend'] = daily_spend_df['cost'].min()
                    data['budget_utilization_pct'] = (data['avg_daily_spend'] / data['daily_budget'] * 100) if data['daily_budget'] > 0 else 0
                    data['days_over_budget'] = len(daily_spend_df[daily_spend_df['cost'] > data['daily_budget']])

            return {
                'budget_data': list(budget_data.values()),
                'customer_id': customer_id,
                'fetched_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching campaign budget data: {str(e)}")
            return {
                'error': str(e),
                'budget_data': [],
                'customer_id': customer_id
            }

    def get_tools(self) -> List[Tool]:
        """
        Get LangChain tools for campaign data collection

        Returns:
            List of Tool objects
        """
        return [
            Tool(
                name="fetch_campaign_data",
                func=self.fetch_campaign_data,
                description="""Fetch campaign data from Google Ads API.
                Args: customer_id (str), date_range (str: LAST_7_DAYS/LAST_30_DAYS/LAST_90_DAYS), include_paused (bool)
                Returns: Dictionary with campaigns list, performance data, and summary statistics"""
            ),
            Tool(
                name="fetch_campaign_budget_data",
                func=self.fetch_campaign_budget_data,
                description="""Fetch campaign budget utilization data.
                Args: customer_id (str), campaign_ids (optional list of campaign IDs)
                Returns: Dictionary with budget utilization metrics for each campaign"""
            )
        ]