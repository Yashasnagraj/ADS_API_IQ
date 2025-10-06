"""
Data Collection Agent for Google Ads Multi-Agent System
"""
from typing import Dict, Any, Optional, List
from loguru import logger
from .tools.search_term_tools import SearchTermTools
from .tools.ml_feature_tools import MLFeatureTools
from .tools.campaign_tools import CampaignTools
from .tools.keyword_tools import KeywordTools
from .tools.adgroup_tools import AdGroupTools
from .db_client import DatabaseClient


class DataAgent:
    """
    Agent responsible for collecting data from MarketingIQ API and Google Ads
    """

    def __init__(self, google_ads_manager=None):
        """
        Initialize Data Agent with all tools

        Args:
            google_ads_manager: Google Ads manager instance (optional)
        """
        self.gam = google_ads_manager
        self.name = "DataAgent"
        self.db_client = DatabaseClient()

        # Initialize tools
        self.search_term_tools = SearchTermTools(google_ads_manager)
        self.ml_feature_tools = MLFeatureTools(google_ads_manager)
        self.campaign_tools = CampaignTools(google_ads_manager) if google_ads_manager else None
        self.keyword_tools = KeywordTools(google_ads_manager) if google_ads_manager else None
        self.adgroup_tools = AdGroupTools(google_ads_manager) if google_ads_manager else None

        # Validation rules
        self.validation_rules = {
            'min_impressions': 10,
            'min_clicks': 1,
            'max_cpc': 100,
            'min_quality_score': 1,
            'max_quality_score': 10
        }

    def validate_data(self, data: Dict[str, Any], data_type: str) -> Dict[str, Any]:
        """
        Validate collected data based on type

        Args:
            data: Data to validate
            data_type: Type of data (campaign, keyword, search_term, etc.)

        Returns:
            Validation result with any issues found
        """
        issues = []

        if data_type == 'campaign':
            if 'campaigns' in data:
                for campaign in data['campaigns']:
                    if campaign.get('impressions', 0) < self.validation_rules['min_impressions']:
                        issues.append(f"Campaign {campaign.get('name')} has low impressions")
                    if campaign.get('cpc', 0) > self.validation_rules['max_cpc']:
                        issues.append(f"Campaign {campaign.get('name')} has high CPC")

        elif data_type == 'keyword':
            if 'keywords' in data:
                for keyword in data['keywords']:
                    qs = keyword.get('quality_score', 0)
                    if qs < self.validation_rules['min_quality_score'] or qs > self.validation_rules['max_quality_score']:
                        issues.append(f"Keyword {keyword.get('text')} has invalid quality score: {qs}")

        elif data_type == 'search_term':
            if 'search_terms' in data:
                for term in data['search_terms']:
                    if term.get('clicks', 0) < self.validation_rules['min_clicks'] and term.get('cost', 0) > 0:
                        issues.append(f"Search term '{term.get('search_term')}' has cost but no clicks")

        return {
            'valid': len(issues) == 0,
            'issues': issues,
            'data_type': data_type,
            'records_validated': len(data.get(data_type + 's', []))
        }

    def fetch_search_terms(
        self,
        customer_id: str = None,
        min_impressions: int = 10,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch search terms with validation

        Args:
            customer_id: Customer ID (optional for API)
            min_impressions: Minimum impressions filter
            use_cache: Whether to use cached data

        Returns:
            Search terms data with validation
        """
        try:
            if not use_cache:
                self.db_client.clear_cache()

            result = self.search_term_tools.fetch_search_terms(
                customer_id=customer_id,
                min_impressions=min_impressions
            )

            # Validate data
            validation = self.validate_data(result, 'search_term')
            result['validation'] = validation

            return result

        except Exception as e:
            logger.error(f"Error fetching search terms: {str(e)}")
            return {
                'error': str(e),
                'search_terms': [],
                'validation': {'valid': False, 'issues': [str(e)]}
            }

    def fetch_ml_features(
        self,
        customer_id: str = None,
        entity_type: str = "campaign",
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Fetch ML features with validation

        Args:
            customer_id: Customer ID (optional for API)
            entity_type: Entity type (campaign/keyword)
            use_cache: Whether to use cached data

        Returns:
            ML features data
        """
        try:
            if not use_cache:
                self.db_client.clear_cache()

            result = self.ml_feature_tools.extract_ml_features(
                customer_id=customer_id,
                entity_type=entity_type
            )

            return result

        except Exception as e:
            logger.error(f"Error fetching ML features: {str(e)}")
            return {
                'error': str(e),
                'features': []
            }

    def get_campaign_performance(
        self,
        customer_id: str = None,
        campaign_ids: Optional[List[str]] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get campaign performance data from API or Google Ads

        Args:
            customer_id: Customer ID (optional for API)
            campaign_ids: Specific campaign IDs to fetch
            use_cache: Whether to use cached data

        Returns:
            Campaign performance data
        """
        try:
            if not use_cache:
                self.db_client.clear_cache()

            # Try API first
            result = self.db_client.fetch_campaigns()

            if "error" not in result:
                # Filter by campaign IDs if specified
                if campaign_ids and 'campaigns' in result:
                    result['campaigns'] = [
                        c for c in result['campaigns']
                        if str(c.get('id')) in campaign_ids
                    ]

                # Validate data
                validation = self.validate_data(result, 'campaign')
                result['validation'] = validation

                return result

            # Fall back to Google Ads Manager if available
            if self.campaign_tools and customer_id:
                return self.campaign_tools.fetch_campaign_performance(
                    customer_id=customer_id,
                    campaign_ids=campaign_ids
                )

            return {
                'error': 'No data source available',
                'campaigns': []
            }

        except Exception as e:
            logger.error(f"Error fetching campaign performance: {str(e)}")
            return {
                'error': str(e),
                'campaigns': []
            }

    def get_keyword_performance(
        self,
        customer_id: str = None,
        min_quality_score: Optional[int] = None,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Get keyword performance data

        Args:
            customer_id: Customer ID (optional for API)
            min_quality_score: Minimum quality score filter
            use_cache: Whether to use cached data

        Returns:
            Keyword performance data
        """
        try:
            if not use_cache:
                self.db_client.clear_cache()

            # Try API first
            result = self.db_client.fetch_keywords(min_quality_score=min_quality_score)

            if "error" not in result:
                # Validate data
                validation = self.validate_data(result, 'keyword')
                result['validation'] = validation

                return result

            # Fall back to Google Ads Manager if available
            if self.keyword_tools and customer_id:
                return self.keyword_tools.fetch_keyword_performance(
                    customer_id=customer_id,
                    min_quality_score=min_quality_score
                )

            return {
                'error': 'No data source available',
                'keywords': []
            }

        except Exception as e:
            logger.error(f"Error fetching keyword performance: {str(e)}")
            return {
                'error': str(e),
                'keywords': []
            }

    def get_metrics_summary(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Get overall metrics summary from API

        Args:
            use_cache: Whether to use cached data

        Returns:
            Metrics summary
        """
        try:
            if not use_cache:
                self.db_client.clear_cache()

            result = self.db_client.fetch_metrics_summary()

            if "error" not in result:
                logger.info("Successfully fetched metrics summary")
                return result

            return {
                'error': result.get('error'),
                'summary': {}
            }

        except Exception as e:
            logger.error(f"Error fetching metrics summary: {str(e)}")
            return {
                'error': str(e),
                'summary': {}
            }

    def clear_cache(self):
        """Clear all cached data"""
        self.db_client.clear_cache()
        logger.info("Data cache cleared")