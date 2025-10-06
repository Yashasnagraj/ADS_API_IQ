"""
Search term data collection tools for Data Agent
"""
from typing import Dict, List, Any, Optional
from langchain.tools import Tool
from loguru import logger
import pandas as pd
from datetime import datetime
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_client import DatabaseClient


class SearchTermTools:
    """Tools for fetching search term data from Google Ads API"""

    def __init__(self, google_ads_manager=None):
        """
        Initialize search term tools

        Args:
            google_ads_manager: GoogleAdsManager instance (optional)
        """
        self.gam = google_ads_manager
        self.db_client = DatabaseClient()

    def fetch_search_terms(
        self,
        customer_id: str = None,
        campaign_ids: Optional[List[str]] = None,
        date_range: str = "LAST_30_DAYS",
        min_impressions: int = 10
    ) -> Dict[str, Any]:
        """
        Fetch search terms report from API or Google Ads

        Args:
            customer_id: Google Ads customer ID (optional for API)
            campaign_ids: Optional list of campaign IDs to filter
            date_range: Date range for data
            min_impressions: Minimum impressions threshold

        Returns:
            Dictionary with search term data
        """
        try:
            # Try API first for faster response
            api_result = self.db_client.fetch_search_terms(min_impressions=min_impressions)

            if "error" not in api_result and api_result.get("search_terms"):
                logger.info(f"Fetched {len(api_result['search_terms'])} search terms from API")

                # Process API data to match expected format
                search_terms = api_result.get("search_terms", [])

                # Create DataFrame for analysis
                search_df = pd.DataFrame(search_terms)

                # Calculate aggregated terms
                aggregated_terms = []
                if not search_df.empty:
                    # Group by search term
                    term_agg = search_df.groupby('search_term').agg({
                        'impressions': 'sum',
                        'clicks': 'sum',
                        'cost': 'sum',
                        'conversions': 'sum'
                    }).reset_index()

                    # Calculate metrics
                    term_agg['ctr'] = (term_agg['clicks'] / term_agg['impressions'] * 100).fillna(0)
                    term_agg['avg_cpc'] = (term_agg['cost'] / term_agg['clicks']).fillna(0)
                    term_agg['conversion_rate'] = (term_agg['conversions'] / term_agg['clicks'] * 100).fillna(0)

                    aggregated_terms = term_agg.to_dict('records')

                return {
                    'search_terms': search_terms,
                    'aggregated_terms': aggregated_terms,
                    'summary': {
                        'total_unique_terms': search_df['search_term'].nunique() if not search_df.empty else 0,
                        'total_impressions': search_df['impressions'].sum() if not search_df.empty else 0,
                        'total_cost': search_df['cost'].sum() if not search_df.empty else 0,
                        'total_conversions': search_df['conversions'].sum() if not search_df.empty else 0
                    },
                    'customer_id': customer_id or 'API',
                    'date_range': date_range,
                    'fetched_at': datetime.now().isoformat(),
                    'source': 'API'
                }

            # Fall back to Google Ads Manager if available and API failed
            if self.gam and customer_id:
                # Build campaign filter
                campaign_filter = ""
                if campaign_ids:
                    ids_str = ", ".join([f"'{id}'" for id in campaign_ids])
                    campaign_filter = f"AND campaign.id IN ({ids_str})"

                query = f"""
                SELECT
                    search_term_view.search_term,
                    search_term_view.ad_group,
                    search_term_view.campaign,
                    search_term_view.status,
                    ad_group.id,
                    ad_group.name,
                    campaign.id,
                    campaign.name,
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
                WHERE segments.date DURING {date_range}
                    AND metrics.impressions > {min_impressions}
                    {campaign_filter}
                ORDER BY metrics.impressions DESC
                """

                # Execute query
                results = list(self.gam.execute_query(customer_id, query))

                # Process results
                search_terms = []

                for row in results:
                    search_term_view = row.get('search_term_view', {})
                    ad_group = row.get('ad_group', {})
                    campaign = row.get('campaign', {})
                    metrics = row.get('metrics', {})
                    segments = row.get('segments', {})

                    # Extract IDs from resource names
                    ad_group_resource = search_term_view.get('ad_group', '')
                    ad_group_id = ad_group_resource.split('/')[-1] if ad_group_resource else ad_group.get('id')

                    campaign_resource = search_term_view.get('campaign', '')
                    campaign_id = campaign_resource.split('/')[-1] if campaign_resource else campaign.get('id')

                    # Keyword info
                    keyword_info = segments.get('keyword', {}).get('info', {})

                    search_term_data = {
                    'date': segments.get('date'),
                    'search_term': search_term_view.get('search_term'),
                    'campaign_id': campaign_id,
                    'campaign_name': campaign.get('name'),
                    'ad_group_id': ad_group_id,
                    'ad_group_name': ad_group.get('name'),
                    'status': search_term_view.get('status'),
                    'triggering_keyword': keyword_info.get('text'),
                    'match_type': keyword_info.get('match_type'),
                    'impressions': metrics.get('impressions', 0),
                    'clicks': metrics.get('clicks', 0),
                    'cost': metrics.get('cost_micros', 0) / 1_000_000,
                    'conversions': metrics.get('conversions', 0),
                    'conversion_value': metrics.get('conversions_value', 0),
                    'ctr': metrics.get('ctr', 0),
                    'avg_cpc': metrics.get('average_cpc', 0) / 1_000_000 if metrics.get('average_cpc') else 0,
                    'conversion_rate': metrics.get('conversion_rate', 0)
                    }
                    search_terms.append(search_term_data)

                # Create DataFrame for analysis
                search_df = pd.DataFrame(search_terms)

                # Aggregate by search term
                aggregated_terms = []
                if not search_df.empty:
                    term_agg = search_df.groupby('search_term').agg({
                        'impressions': 'sum',
                        'clicks': 'sum',
                        'cost': 'sum',
                        'conversions': 'sum',
                        'conversion_value': 'sum',
                        'campaign_id': 'nunique',
                        'ad_group_id': 'nunique'
                    }).reset_index()

                    term_agg.columns = ['search_term', 'total_impressions', 'total_clicks',
                                       'total_cost', 'total_conversions', 'total_conversion_value',
                                       'campaign_count', 'ad_group_count']

                    # Calculate metrics
                    term_agg['ctr'] = (term_agg['total_clicks'] / term_agg['total_impressions'] * 100).fillna(0)
                    term_agg['avg_cpc'] = (term_agg['total_cost'] / term_agg['total_clicks']).fillna(0)
                    term_agg['conversion_rate'] = (term_agg['total_conversions'] / term_agg['total_clicks'] * 100).fillna(0)
                    term_agg['roas'] = (term_agg['total_conversion_value'] / term_agg['total_cost']).fillna(0)

                    aggregated_terms = term_agg.to_dict('records')

                logger.info(f"Fetched {len(search_df)} search term records for customer {customer_id}")

                return {
                    'search_terms': search_terms,
                    'aggregated_terms': aggregated_terms,
                    'summary': {
                        'total_unique_terms': search_df['search_term'].nunique() if not search_df.empty else 0,
                        'total_impressions': search_df['impressions'].sum() if not search_df.empty else 0,
                        'total_cost': search_df['cost'].sum() if not search_df.empty else 0,
                        'total_conversions': search_df['conversions'].sum() if not search_df.empty else 0
                    },
                    'customer_id': customer_id,
                    'date_range': date_range,
                    'fetched_at': datetime.now().isoformat()
                }

        except Exception as e:
            logger.error(f"Error fetching search terms: {str(e)}")
            return {
                'error': str(e),
                'search_terms': [],
                'aggregated_terms': [],
                'customer_id': customer_id
            }

    def identify_negative_keywords(
        self,
        customer_id: str,
        min_cost: float = 50.0,
        max_conversions: int = 0,
        min_impressions: int = 100
    ) -> Dict[str, Any]:
        """
        Identify search terms that should be added as negative keywords

        Args:
            customer_id: Google Ads customer ID
            min_cost: Minimum wasted spend threshold
            max_conversions: Maximum conversions (typically 0)
            min_impressions: Minimum impressions threshold

        Returns:
            Dictionary with negative keyword recommendations
        """
        try:
            # Fetch search terms
            search_data = self.fetch_search_terms(
                customer_id=customer_id,
                date_range="LAST_30_DAYS",
                min_impressions=min_impressions
            )

            if 'error' in search_data:
                return search_data

            # Create DataFrame
            df = pd.DataFrame(search_data.get('search_terms', []))

            if df.empty:
                return {
                    'negative_keywords': [],
                    'total_recommendations': 0,
                    'potential_savings': 0
                }

            # Aggregate by search term
            term_performance = df.groupby('search_term').agg({
                'impressions': 'sum',
                'clicks': 'sum',
                'cost': 'sum',
                'conversions': 'sum',
                'conversion_value': 'sum'
            }).reset_index()

            # Filter for negative keyword candidates
            negative_candidates = term_performance[
                (term_performance['cost'] >= min_cost) &
                (term_performance['conversions'] <= max_conversions) &
                (term_performance['impressions'] >= min_impressions)
            ]

            # Calculate metrics
            negative_candidates['ctr'] = (negative_candidates['clicks'] / negative_candidates['impressions'] * 100).fillna(0)
            negative_candidates['avg_cpc'] = (negative_candidates['cost'] / negative_candidates['clicks']).fillna(0)

            # Sort by wasted spend
            negative_candidates = negative_candidates.sort_values('cost', ascending=False)

            # Prepare recommendations
            recommendations = []
            for _, term in negative_candidates.iterrows():
                recommendations.append({
                    'search_term': term['search_term'],
                    'match_type': 'EXACT',  # Recommend exact match negatives
                    'wasted_spend': round(term['cost'], 2),
                    'impressions': int(term['impressions']),
                    'clicks': int(term['clicks']),
                    'ctr': round(term['ctr'], 2),
                    'avg_cpc': round(term['avg_cpc'], 2),
                    'reason': 'High spend with no conversions'
                })

            total_savings = negative_candidates['cost'].sum()

            logger.info(f"Identified {len(recommendations)} negative keyword candidates")

            return {
                'negative_keywords': recommendations,
                'total_recommendations': len(recommendations),
                'potential_savings': round(total_savings, 2),
                'analysis_period': 'LAST_30_DAYS',
                'criteria': {
                    'min_cost': min_cost,
                    'max_conversions': max_conversions,
                    'min_impressions': min_impressions
                },
                'customer_id': customer_id,
                'fetched_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error identifying negative keywords: {str(e)}")
            return {
                'error': str(e),
                'negative_keywords': [],
                'customer_id': customer_id
            }

    def get_tools(self) -> List[Tool]:
        """
        Get LangChain tools for search term data collection

        Returns:
            List of Tool objects
        """
        return [
            Tool(
                name="fetch_search_terms",
                func=self.fetch_search_terms,
                description="""Fetch search terms report from Google Ads API.
                Args: customer_id (str), campaign_ids (optional list), date_range (str), min_impressions (int)
                Returns: Dictionary with search terms, aggregated data, and performance metrics"""
            ),
            Tool(
                name="identify_negative_keywords",
                func=self.identify_negative_keywords,
                description="""Identify search terms that should be added as negative keywords.
                Args: customer_id (str), min_cost (float), max_conversions (int), min_impressions (int)
                Returns: Dictionary with negative keyword recommendations and potential savings"""
            )
        ]