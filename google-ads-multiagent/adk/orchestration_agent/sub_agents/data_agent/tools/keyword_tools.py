"""
Keyword data collection tools for Data Agent
"""
from typing import Dict, List, Any, Optional
from langchain.tools import Tool
from loguru import logger
import pandas as pd
from datetime import datetime


class KeywordTools:
    """Tools for fetching keyword data from Google Ads API"""

    def __init__(self, google_ads_manager):
        """
        Initialize keyword tools

        Args:
            google_ads_manager: GoogleAdsManager instance
        """
        self.gam = google_ads_manager

    def fetch_keyword_data(
        self,
        customer_id: str,
        ad_group_ids: Optional[List[str]] = None,
        date_range: str = "LAST_30_DAYS",
        min_impressions: int = 0
    ) -> Dict[str, Any]:
        """
        Fetch keyword data from Google Ads

        Args:
            customer_id: Google Ads customer ID
            ad_group_ids: Optional list of ad group IDs to filter
            date_range: Date range for data
            min_impressions: Minimum impressions threshold

        Returns:
            Dictionary with keyword data
        """
        try:
            # Build ad group filter
            ad_group_filter = ""
            if ad_group_ids:
                ids_str = ", ".join([f"'{id}'" for id in ad_group_ids])
                ad_group_filter = f"AND ad_group.id IN ({ids_str})"

            query = f"""
                SELECT
                    ad_group_criterion.criterion_id,
                    ad_group_criterion.keyword.text,
                    ad_group_criterion.keyword.match_type,
                    ad_group_criterion.status,
                    ad_group_criterion.quality_info.quality_score,
                    ad_group_criterion.quality_info.creative_quality_score,
                    ad_group_criterion.quality_info.landing_page_quality_score,
                    ad_group_criterion.quality_info.search_predicted_ctr,
                    ad_group_criterion.position_estimates.first_page_cpc_micros,
                    ad_group_criterion.position_estimates.top_of_page_cpc_micros,
                    ad_group_criterion.position_estimates.first_position_cpc_micros,
                    ad_group_criterion.ad_group,
                    ad_group_criterion.cpc_bid_micros,
                    ad_group.id,
                    ad_group.name,
                    campaign.id,
                    campaign.name,
                    metrics.impressions,
                    metrics.clicks,
                    metrics.cost_micros,
                    metrics.conversions,
                    metrics.conversions_value,
                    metrics.average_position,
                    metrics.ctr,
                    metrics.average_cpc,
                    metrics.conversion_rate,
                    metrics.cost_per_conversion,
                    segments.date
                FROM ad_group_criterion
                WHERE ad_group_criterion.type = 'KEYWORD'
                    AND segments.date DURING {date_range}
                    AND ad_group_criterion.status != 'REMOVED'
                    AND metrics.impressions > {min_impressions}
                    {ad_group_filter}
                ORDER BY metrics.impressions DESC
            """

            # Execute query
            results = list(self.gam.execute_query(customer_id, query))

            # Process results
            keywords = []
            performance_data = []

            for row in results:
                criterion = row.get('ad_group_criterion', {})
                ad_group = row.get('ad_group', {})
                campaign = row.get('campaign', {})
                metrics = row.get('metrics', {})
                segments = row.get('segments', {})

                # Extract ad group ID from resource name
                ad_group_resource = criterion.get('ad_group', '')
                ad_group_id = ad_group_resource.split('/')[-1] if ad_group_resource else ad_group.get('id')

                # Quality info
                quality_info = criterion.get('quality_info', {})
                position_estimates = criterion.get('position_estimates', {})

                # Keyword dimension data
                keyword_info = {
                    'keyword_id': str(criterion.get('criterion_id')),
                    'keyword_text': criterion.get('keyword', {}).get('text'),
                    'match_type': criterion.get('keyword', {}).get('match_type'),
                    'status': criterion.get('status'),
                    'ad_group_id': ad_group_id,
                    'ad_group_name': ad_group.get('name'),
                    'campaign_id': campaign.get('id'),
                    'campaign_name': campaign.get('name'),
                    'max_cpc': criterion.get('cpc_bid_micros', 0) / 1_000_000 if criterion.get('cpc_bid_micros') else None,
                    'quality_score': quality_info.get('quality_score'),
                    'creative_quality_score': quality_info.get('creative_quality_score'),
                    'landing_page_quality_score': quality_info.get('landing_page_quality_score'),
                    'expected_ctr': quality_info.get('search_predicted_ctr'),
                    'first_page_bid': position_estimates.get('first_page_cpc_micros', 0) / 1_000_000 if position_estimates.get('first_page_cpc_micros') else None,
                    'top_of_page_bid': position_estimates.get('top_of_page_cpc_micros', 0) / 1_000_000 if position_estimates.get('top_of_page_cpc_micros') else None,
                    'first_position_bid': position_estimates.get('first_position_cpc_micros', 0) / 1_000_000 if position_estimates.get('first_position_cpc_micros') else None
                }
                keywords.append(keyword_info)

                # Performance data
                perf_data = {
                    'date': segments.get('date'),
                    'keyword_id': str(criterion.get('criterion_id')),
                    'ad_group_id': ad_group_id,
                    'impressions': metrics.get('impressions', 0),
                    'clicks': metrics.get('clicks', 0),
                    'cost': metrics.get('cost_micros', 0) / 1_000_000,
                    'conversions': metrics.get('conversions', 0),
                    'conversion_value': metrics.get('conversions_value', 0),
                    'avg_position': metrics.get('average_position'),
                    'ctr': metrics.get('ctr', 0),
                    'avg_cpc': metrics.get('average_cpc', 0) / 1_000_000 if metrics.get('average_cpc') else 0,
                    'conversion_rate': metrics.get('conversion_rate', 0),
                    'cost_per_conversion': metrics.get('cost_per_conversion', 0) / 1_000_000 if metrics.get('cost_per_conversion') else 0
                }
                performance_data.append(perf_data)

            # Create DataFrames
            keywords_df = pd.DataFrame(keywords).drop_duplicates(subset=['keyword_id'])
            performance_df = pd.DataFrame(performance_data)

            # Calculate aggregated metrics
            if not performance_df.empty:
                aggregated = performance_df.groupby('keyword_id').agg({
                    'impressions': 'sum',
                    'clicks': 'sum',
                    'cost': 'sum',
                    'conversions': 'sum',
                    'conversion_value': 'sum',
                    'avg_position': 'mean'
                }).reset_index()

                # Calculate derived metrics
                aggregated['ctr'] = (aggregated['clicks'] / aggregated['impressions'] * 100).fillna(0)
                aggregated['conversion_rate'] = (aggregated['conversions'] / aggregated['clicks'] * 100).fillna(0)
                aggregated['avg_cpc'] = (aggregated['cost'] / aggregated['clicks']).fillna(0)
                aggregated['roas'] = (aggregated['conversion_value'] / aggregated['cost']).fillna(0)

                # Merge with keyword info
                keywords_df = keywords_df.merge(aggregated, on='keyword_id', how='left')

            logger.info(f"Fetched {len(keywords_df)} keywords for customer {customer_id}")

            return {
                'keywords': keywords_df.to_dict('records'),
                'performance_data': performance_df.to_dict('records'),
                'summary': {
                    'total_keywords': len(keywords_df),
                    'active_keywords': len(keywords_df[keywords_df['status'] == 'ENABLED']),
                    'avg_quality_score': keywords_df['quality_score'].mean() if 'quality_score' in keywords_df else None,
                    'total_cost': performance_df['cost'].sum() if not performance_df.empty else 0,
                    'total_conversions': performance_df['conversions'].sum() if not performance_df.empty else 0
                },
                'customer_id': customer_id,
                'date_range': date_range,
                'fetched_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching keyword data: {str(e)}")
            return {
                'error': str(e),
                'keywords': [],
                'performance_data': [],
                'customer_id': customer_id
            }

    def fetch_keyword_ideas(
        self,
        customer_id: str,
        keyword_texts: List[str],
        language_id: str = "1000",  # English
        location_ids: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Fetch keyword ideas from Google Ads Keyword Planner

        Args:
            customer_id: Google Ads customer ID
            keyword_texts: List of seed keywords
            language_id: Language ID (default: English)
            location_ids: Optional list of location IDs

        Returns:
            Dictionary with keyword ideas
        """
        try:
            # Get keyword planning service
            keyword_plan_idea_service = self.gam.get_service("KeywordPlanIdeaService")

            # Set up request parameters
            request = self.gam.client.get_type("GenerateKeywordIdeasRequest")
            request.customer_id = customer_id
            request.language = f"languageConstants/{language_id}"

            # Add location targeting if specified
            if location_ids:
                for location_id in location_ids:
                    request.geo_target_constants.append(f"geoTargetConstants/{location_id}")

            # Add seed keywords
            request.keyword_plan_network = "GOOGLE_SEARCH"
            request.keyword_seed.keywords.extend(keyword_texts)

            # Execute request
            keyword_ideas = keyword_plan_idea_service.generate_keyword_ideas(request=request)

            # Process results
            ideas = []
            for idea in keyword_ideas:
                keyword_idea = {
                    'keyword_text': idea.text,
                    'avg_monthly_searches': idea.keyword_idea_metrics.avg_monthly_searches,
                    'competition': idea.keyword_idea_metrics.competition.name,
                    'competition_index': idea.keyword_idea_metrics.competition_index,
                    'low_top_of_page_bid': idea.keyword_idea_metrics.low_top_of_page_bid_micros / 1_000_000 if idea.keyword_idea_metrics.low_top_of_page_bid_micros else None,
                    'high_top_of_page_bid': idea.keyword_idea_metrics.high_top_of_page_bid_micros / 1_000_000 if idea.keyword_idea_metrics.high_top_of_page_bid_micros else None
                }
                ideas.append(keyword_idea)

            # Sort by search volume
            ideas_df = pd.DataFrame(ideas)
            if not ideas_df.empty:
                ideas_df = ideas_df.sort_values('avg_monthly_searches', ascending=False)

            return {
                'keyword_ideas': ideas_df.to_dict('records') if not ideas_df.empty else [],
                'total_ideas': len(ideas),
                'seed_keywords': keyword_texts,
                'customer_id': customer_id,
                'fetched_at': datetime.now().isoformat()
            }

        except Exception as e:
            logger.error(f"Error fetching keyword ideas: {str(e)}")
            return {
                'error': str(e),
                'keyword_ideas': [],
                'customer_id': customer_id
            }

    def get_tools(self) -> List[Tool]:
        """
        Get LangChain tools for keyword data collection

        Returns:
            List of Tool objects
        """
        return [
            Tool(
                name="fetch_keyword_data",
                func=self.fetch_keyword_data,
                description="""Fetch keyword data from Google Ads API.
                Args: customer_id (str), ad_group_ids (optional list), date_range (str), min_impressions (int)
                Returns: Dictionary with keywords list, performance data, quality scores, and summary"""
            ),
            Tool(
                name="fetch_keyword_ideas",
                func=self.fetch_keyword_ideas,
                description="""Fetch keyword ideas from Google Ads Keyword Planner.
                Args: customer_id (str), keyword_texts (list of seed keywords), language_id (str), location_ids (optional list)
                Returns: Dictionary with keyword suggestions and search volume data"""
            )
        ]