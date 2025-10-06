"""
ML feature extraction tools for Data Agent
"""
from typing import Dict, List, Any, Optional
from langchain.tools import Tool
from loguru import logger
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db_client import DatabaseClient


class MLFeatureTools:
    """Tools for extracting ML features from Google Ads data"""

    def __init__(self, google_ads_manager=None):
        """
        Initialize ML feature tools

        Args:
            google_ads_manager: GoogleAdsManager instance (optional)
        """
        self.gam = google_ads_manager
        self.db_client = DatabaseClient()

    def extract_ml_features(
        self,
        customer_id: str = None,
        entity_type: str = "campaign",
        date_range: str = "LAST_30_DAYS"
    ) -> Dict[str, Any]:
        """
        Extract ML features from API or Google Ads

        Args:
            customer_id: Google Ads customer ID (optional for API)
            entity_type: Type of entity (campaign, ad_group, keyword)
            date_range: Date range for data

        Returns:
            Dictionary with ML features
        """
        try:
            # Try API first
            api_result = self.db_client.fetch_ml_features(entity_type=entity_type)

            if "error" not in api_result and api_result.get("features"):
                logger.info(f"Fetched ML features from API for entity type: {entity_type}")
                return api_result

            # Fall back to Google Ads Manager if available
            if self.gam and customer_id:
                if entity_type == "campaign":
                    features = self._extract_campaign_features(customer_id, date_range)
                elif entity_type == "ad_group":
                    features = self._extract_ad_group_features(customer_id, date_range)
                elif entity_type == "keyword":
                    features = self._extract_keyword_features(customer_id, date_range)
                else:
                    raise ValueError(f"Unsupported entity type: {entity_type}")

                return features

            # If neither API nor Google Ads Manager worked
            return {
                'error': 'No data source available',
                'features': [],
                'customer_id': customer_id or 'API'
            }

        except Exception as e:
            logger.error(f"Error extracting ML features: {str(e)}")
            return {
                'error': str(e),
                'features': [],
                'customer_id': customer_id or 'API'
            }

    def _extract_campaign_features(
        self,
        customer_id: str,
        date_range: str
    ) -> Dict[str, Any]:
        """
        Extract campaign-level ML features

        Args:
            customer_id: Google Ads customer ID
            date_range: Date range for data

        Returns:
            Dictionary with campaign features
        """
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.advertising_channel_type,
                campaign.bidding_strategy_type,
                campaign.campaign_budget.amount_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.search_impression_share,
                metrics.search_rank_lost_impression_share,
                metrics.search_budget_lost_impression_share,
                metrics.content_impression_share,
                metrics.interaction_rate,
                metrics.engagement_rate,
                segments.date,
                segments.day_of_week,
                segments.hour,
                segments.device
            FROM campaign
            WHERE segments.date DURING {date_range}
                AND campaign.status = 'ENABLED'
        """

        # Execute query
        results = list(self.gam.execute_query(customer_id, query))

        # Process results into DataFrame
        data = []
        for row in results:
            campaign = row.get('campaign', {})
            metrics = row.get('metrics', {})
            segments = row.get('segments', {})

            data.append({
                'campaign_id': campaign.get('id'),
                'campaign_name': campaign.get('name'),
                'channel_type': campaign.get('advertising_channel_type'),
                'bidding_strategy': campaign.get('bidding_strategy_type'),
                'budget': campaign.get('campaign_budget', {}).get('amount_micros', 0) / 1_000_000,
                'impressions': metrics.get('impressions', 0),
                'clicks': metrics.get('clicks', 0),
                'cost': metrics.get('cost_micros', 0) / 1_000_000,
                'conversions': metrics.get('conversions', 0),
                'conversion_value': metrics.get('conversions_value', 0),
                'search_impression_share': metrics.get('search_impression_share', 0),
                'search_rank_lost_is': metrics.get('search_rank_lost_impression_share', 0),
                'search_budget_lost_is': metrics.get('search_budget_lost_impression_share', 0),
                'content_impression_share': metrics.get('content_impression_share', 0),
                'interaction_rate': metrics.get('interaction_rate', 0),
                'engagement_rate': metrics.get('engagement_rate', 0),
                'date': segments.get('date'),
                'day_of_week': segments.get('day_of_week'),
                'hour': segments.get('hour'),
                'device': segments.get('device')
            })

        df = pd.DataFrame(data)

        if df.empty:
            return {
                'features': [],
                'feature_names': [],
                'customer_id': customer_id
            }

        # Engineer features
        features_df = self._engineer_campaign_features(df)

        return {
            'features': features_df.to_dict('records'),
            'feature_names': list(features_df.columns),
            'shape': features_df.shape,
            'entity_type': 'campaign',
            'customer_id': customer_id,
            'date_range': date_range,
            'fetched_at': datetime.now().isoformat()
        }

    def _engineer_campaign_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features for campaigns

        Args:
            df: Raw campaign data

        Returns:
            DataFrame with engineered features
        """
        # Group by campaign to aggregate
        campaign_features = df.groupby('campaign_id').agg({
            'impressions': ['sum', 'mean', 'std'],
            'clicks': ['sum', 'mean', 'std'],
            'cost': ['sum', 'mean', 'std'],
            'conversions': ['sum', 'mean', 'std'],
            'conversion_value': ['sum', 'mean'],
            'budget': 'first'
        })

        # Flatten column names
        campaign_features.columns = ['_'.join(col).strip() for col in campaign_features.columns]

        # Calculate derived features
        campaign_features['ctr'] = (
            campaign_features['clicks_sum'] / campaign_features['impressions_sum']
        ).fillna(0)

        campaign_features['conversion_rate'] = (
            campaign_features['conversions_sum'] / campaign_features['clicks_sum']
        ).fillna(0)

        campaign_features['avg_cpc'] = (
            campaign_features['cost_sum'] / campaign_features['clicks_sum']
        ).fillna(0)

        campaign_features['roas'] = (
            campaign_features['conversion_value_sum'] / campaign_features['cost_sum']
        ).fillna(0)

        campaign_features['cost_per_conversion'] = (
            campaign_features['cost_sum'] / campaign_features['conversions_sum']
        ).fillna(0)

        campaign_features['budget_utilization'] = (
            campaign_features['cost_mean'] / campaign_features['budget_first']
        ).fillna(0)

        # Add time-based features
        if 'day_of_week' in df.columns:
            dow_performance = df.groupby(['campaign_id', 'day_of_week'])['clicks'].sum().unstack(fill_value=0)
            dow_features = dow_performance.add_prefix('dow_clicks_')
            campaign_features = campaign_features.join(dow_features)

        # Add device-based features
        if 'device' in df.columns:
            device_performance = df.groupby(['campaign_id', 'device'])['conversions'].sum().unstack(fill_value=0)
            device_features = device_performance.add_prefix('device_conversions_')
            campaign_features = campaign_features.join(device_features)

        # Calculate trend features (if enough data)
        if len(df['date'].unique()) > 7:
            for campaign_id in campaign_features.index:
                campaign_data = df[df['campaign_id'] == campaign_id].sort_values('date')
                if len(campaign_data) > 1:
                    # Calculate linear trend
                    x = np.arange(len(campaign_data))
                    y = campaign_data['clicks'].values
                    if len(x) > 1 and np.std(y) > 0:
                        trend = np.polyfit(x, y, 1)[0]
                        campaign_features.loc[campaign_id, 'clicks_trend'] = trend

        # Fill NaN values
        campaign_features = campaign_features.fillna(0)

        # Reset index
        campaign_features = campaign_features.reset_index()

        return campaign_features

    def _extract_keyword_features(
        self,
        customer_id: str,
        date_range: str
    ) -> Dict[str, Any]:
        """
        Extract keyword-level ML features

        Args:
            customer_id: Google Ads customer ID
            date_range: Date range for data

        Returns:
            Dictionary with keyword features
        """
        query = f"""
            SELECT
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.quality_info.quality_score,
                ad_group_criterion.position_estimates.first_page_cpc_micros,
                ad_group_criterion.position_estimates.top_of_page_cpc_micros,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.historical_quality_score,
                metrics.historical_landing_page_quality_score,
                metrics.historical_creative_quality_score,
                segments.date,
                segments.device
            FROM ad_group_criterion
            WHERE ad_group_criterion.type = 'KEYWORD'
                AND segments.date DURING {date_range}
                AND ad_group_criterion.status = 'ENABLED'
        """

        # Execute query
        results = list(self.gam.execute_query(customer_id, query))

        # Process results
        data = []
        for row in results:
            criterion = row.get('ad_group_criterion', {})
            metrics = row.get('metrics', {})
            segments = row.get('segments', {})

            keyword_length = len(criterion.get('keyword', {}).get('text', '').split())

            data.append({
                'keyword_id': str(criterion.get('criterion_id')),
                'keyword_text': criterion.get('keyword', {}).get('text'),
                'match_type': criterion.get('keyword', {}).get('match_type'),
                'quality_score': criterion.get('quality_info', {}).get('quality_score', 0),
                'first_page_bid': criterion.get('position_estimates', {}).get('first_page_cpc_micros', 0) / 1_000_000,
                'top_page_bid': criterion.get('position_estimates', {}).get('top_of_page_cpc_micros', 0) / 1_000_000,
                'keyword_length': keyword_length,
                'impressions': metrics.get('impressions', 0),
                'clicks': metrics.get('clicks', 0),
                'cost': metrics.get('cost_micros', 0) / 1_000_000,
                'conversions': metrics.get('conversions', 0),
                'conversion_value': metrics.get('conversions_value', 0),
                'hist_quality_score': metrics.get('historical_quality_score', 0),
                'hist_landing_page_qs': metrics.get('historical_landing_page_quality_score', 0),
                'hist_creative_qs': metrics.get('historical_creative_quality_score', 0),
                'date': segments.get('date'),
                'device': segments.get('device')
            })

        df = pd.DataFrame(data)

        if df.empty:
            return {
                'features': [],
                'feature_names': [],
                'customer_id': customer_id
            }

        # Engineer keyword features
        features_df = self._engineer_keyword_features(df)

        return {
            'features': features_df.to_dict('records'),
            'feature_names': list(features_df.columns),
            'shape': features_df.shape,
            'entity_type': 'keyword',
            'customer_id': customer_id,
            'date_range': date_range,
            'fetched_at': datetime.now().isoformat()
        }

    def _engineer_keyword_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Engineer features for keywords

        Args:
            df: Raw keyword data

        Returns:
            DataFrame with engineered features
        """
        # Group by keyword
        keyword_features = df.groupby('keyword_id').agg({
            'keyword_text': 'first',
            'match_type': 'first',
            'quality_score': 'mean',
            'keyword_length': 'first',
            'first_page_bid': 'mean',
            'top_page_bid': 'mean',
            'impressions': 'sum',
            'clicks': 'sum',
            'cost': 'sum',
            'conversions': 'sum',
            'conversion_value': 'sum'
        })

        # Calculate derived features
        keyword_features['ctr'] = (
            keyword_features['clicks'] / keyword_features['impressions']
        ).fillna(0)

        keyword_features['conversion_rate'] = (
            keyword_features['conversions'] / keyword_features['clicks']
        ).fillna(0)

        keyword_features['avg_cpc'] = (
            keyword_features['cost'] / keyword_features['clicks']
        ).fillna(0)

        keyword_features['roas'] = (
            keyword_features['conversion_value'] / keyword_features['cost']
        ).fillna(0)

        # Add match type encoding
        match_type_mapping = {
            'EXACT': 3,
            'PHRASE': 2,
            'BROAD': 1,
            'UNKNOWN': 0
        }
        keyword_features['match_type_encoded'] = keyword_features['match_type'].map(
            match_type_mapping
        ).fillna(0)

        # Quality score features
        keyword_features['quality_score_normalized'] = keyword_features['quality_score'] / 10.0
        keyword_features['quality_score_category'] = pd.cut(
            keyword_features['quality_score'],
            bins=[0, 3, 6, 8, 10],
            labels=['low', 'medium', 'high', 'excellent']
        )

        # Bid efficiency features
        keyword_features['bid_to_first_page_ratio'] = (
            keyword_features['avg_cpc'] / keyword_features['first_page_bid']
        ).fillna(0)

        keyword_features['bid_to_top_page_ratio'] = (
            keyword_features['avg_cpc'] / keyword_features['top_page_bid']
        ).fillna(0)

        # Reset index
        keyword_features = keyword_features.reset_index()

        return keyword_features

    def get_tools(self) -> List[Tool]:
        """
        Get LangChain tools for ML feature extraction

        Returns:
            List of Tool objects
        """
        return [
            Tool(
                name="extract_ml_features",
                func=self.extract_ml_features,
                description="""Extract ML features from Google Ads data.
                Args: customer_id (str), entity_type (str: campaign/ad_group/keyword), date_range (str)
                Returns: Dictionary with engineered features ready for ML models"""
            )
        ]