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
from .tools.ga4_tools import GA4Tools
from .db_client import DatabaseClient
from .api_client import APIClient
from .warehouse_client import WarehouseClient


class DataAgent:
    """
    Agent responsible for collecting data from MarketingIQ API and Google Ads
    """

    def __init__(self, google_ads_manager=None, use_warehouse=True):
        """
        Initialize Data Agent with all tools

        Args:
            google_ads_manager: Google Ads manager instance (optional)
            use_warehouse: Use new warehouse (default True)
        """
        self.gam = google_ads_manager
        self.name = "DataAgent"
        self.db_client = DatabaseClient()
        self.api_client = APIClient(base_url="http://localhost:8000")

        # Initialize warehouse client (new)
        self.use_warehouse = use_warehouse
        if use_warehouse:
            try:
                self.warehouse_client = WarehouseClient()
                logger.info("Data Agent initialized with warehouse client")
            except Exception as e:
                logger.warning(f"Could not initialize warehouse client: {e}. Falling back to old DB.")
                self.use_warehouse = False
                self.warehouse_client = None
        else:
            self.warehouse_client = None

        # Initialize tools
        self.search_term_tools = SearchTermTools(google_ads_manager)
        self.ml_feature_tools = MLFeatureTools(google_ads_manager)
        self.campaign_tools = CampaignTools(google_ads_manager) if google_ads_manager else None
        self.keyword_tools = KeywordTools(google_ads_manager) if google_ads_manager else None
        self.adgroup_tools = AdGroupTools(google_ads_manager) if google_ads_manager else None
        self.ga4_tools = GA4Tools(self.api_client)

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

    # ========================================================================
    # GA4 (Google Analytics 4) DATA METHODS
    # ========================================================================

    def get_ga4_session_behavior(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        campaign: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get GA4 session behavior data (bounce rate, engagement, pages/session)

        This enriches Google Ads campaigns with user behavior insights.

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            campaign: Filter by campaign name

        Returns:
            Session behavior data with bounce rates, engagement metrics
        """
        try:
            result = self.ga4_tools.fetch_ga4_sessions(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date,
                campaign=campaign
            )

            if "error" not in result:
                logger.info(f"Successfully fetched GA4 session data: {result.get('total_count', 0)} records")
            else:
                logger.error(f"GA4 session fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 session behavior: {str(e)}")
            return {"error": str(e), "sessions": []}

    def get_ga4_campaign_quality(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get campaign quality scores based on GA4 user behavior

        Quality scores (0-100) help identify which campaigns bring quality traffic,
        not just conversions.

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Campaign quality scores with recommendations
        """
        try:
            result = self.ga4_tools.fetch_ga4_campaign_quality_score(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date
            )

            if "error" not in result:
                logger.info(f"Successfully fetched GA4 quality scores for {result.get('total_count', 0)} campaigns")
            else:
                logger.error(f"GA4 quality score fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 campaign quality: {str(e)}")
            return {"error": str(e), "campaigns": []}

    def get_ga4_behavior_by_campaign(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get aggregated user behavior metrics grouped by campaign

        Shows bounce rate, engagement rate, session duration, and pages/session
        for each campaign.

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Behavior metrics by campaign
        """
        try:
            result = self.ga4_tools.fetch_ga4_behavior_by_campaign(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date
            )

            if "error" not in result:
                logger.info(f"Successfully fetched GA4 behavior data for campaigns")
            else:
                logger.error(f"GA4 behavior by campaign fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 behavior by campaign: {str(e)}")
            return {"error": str(e)}

    def get_ga4_conversion_paths(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_touchpoints: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get GA4 conversion paths for multi-touch attribution

        Shows the full customer journey from first touch to conversion.

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            min_touchpoints: Minimum touchpoints in path

        Returns:
            Conversion paths with all touchpoints
        """
        try:
            result = self.ga4_tools.fetch_ga4_conversion_paths(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date,
                min_touchpoints=min_touchpoints
            )

            if "error" not in result:
                logger.info(f"Successfully fetched {result.get('total_count', 0)} GA4 conversion paths")
            else:
                logger.error(f"GA4 conversion paths fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 conversion paths: {str(e)}")
            return {"error": str(e), "paths": []}

    def get_ga4_device_performance(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get device category performance breakdown (desktop/mobile/tablet)

        Useful for device bid adjustments in Google Ads.

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Device performance metrics
        """
        try:
            result = self.ga4_tools.fetch_ga4_device_performance(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date
            )

            if "error" not in result:
                logger.info(f"Successfully fetched GA4 device performance data")
            else:
                logger.error(f"GA4 device performance fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 device performance: {str(e)}")
            return {"error": str(e)}

    def get_ga4_audience_insights(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get GA4 audience insights (demographics, location, technology)

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Audience insights data
        """
        try:
            result = self.ga4_tools.fetch_ga4_audience_insights(
                customer_id=customer_id,
                start_date=start_date,
                end_date=end_date
            )

            if "error" not in result:
                logger.info(f"Successfully fetched {result.get('total_count', 0)} GA4 audience segments")
            else:
                logger.error(f"GA4 audience insights fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 audience insights: {str(e)}")
            return {"error": str(e), "segments": []}

    # ===== Warehouse Methods (New Multi-Platform) =====

    def fetch_campaigns_warehouse(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Fetch campaigns from warehouse (multi-platform)

        Args:
            customer_id: Filter by customer ID
            status: Campaign status filter
            limit: Maximum results

        Returns:
            Campaigns data from warehouse
        """
        if not self.use_warehouse or not self.warehouse_client:
            logger.warning("Warehouse not available, falling back to old DB")
            return self.db_client.fetch_campaigns(status=status, limit=limit)

        try:
            result = self.warehouse_client.fetch_campaigns(
                customer_id=customer_id,
                status=status,
                limit=limit
            )

            if "error" not in result:
                logger.info(f"Fetched {result.get('total', 0)} campaigns from warehouse")
            else:
                logger.error(f"Warehouse fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching campaigns from warehouse: {str(e)}")
            # Fallback to old DB
            return self.db_client.fetch_campaigns(status=status, limit=limit)

    def fetch_traffic_sources_warehouse(
        self,
        customer_id: Optional[int] = None,
        days: int = 30,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Fetch GA4 traffic sources from warehouse

        Args:
            customer_id: Filter by customer ID
            days: Number of days
            limit: Maximum results

        Returns:
            Traffic sources data
        """
        if not self.use_warehouse or not self.warehouse_client:
            logger.warning("Warehouse not available")
            return {'error': 'Warehouse not initialized', 'traffic_sources': []}

        try:
            result = self.warehouse_client.fetch_traffic_sources(
                customer_id=customer_id,
                days=days,
                limit=limit
            )

            if "error" not in result:
                logger.info(f"Fetched {result.get('total', 0)} traffic sources from warehouse")

            return result

        except Exception as e:
            logger.error(f"Error fetching traffic sources: {str(e)}")
            return {'error': str(e), 'traffic_sources': []}

    def fetch_metrics_summary_warehouse(
        self,
        customer_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Fetch overall metrics summary from warehouse (cross-platform)

        Args:
            customer_id: Filter by customer ID
            days: Number of days

        Returns:
            Metrics summary across all platforms
        """
        if not self.use_warehouse or not self.warehouse_client:
            logger.warning("Warehouse not available, falling back to old DB")
            return self.db_client.fetch_metrics_summary()

        try:
            result = self.warehouse_client.fetch_metrics_summary(
                customer_id=customer_id,
                days=days
            )

            if "error" not in result:
                logger.info("Fetched metrics summary from warehouse")

            return result

        except Exception as e:
            logger.error(f"Error fetching metrics summary: {str(e)}")
            # Fallback to old DB
            return self.db_client.fetch_metrics_summary()

    def get_warehouse_customers(self) -> List[Dict[str, Any]]:
        """
        Get list of all customers in warehouse

        Returns:
            List of customers with their configurations
        """
        if not self.use_warehouse or not self.warehouse_client:
            logger.warning("Warehouse not available")
            return []

        try:
            customers = self.warehouse_client.get_customers()
            logger.info(f"Found {len(customers)} customers in warehouse")
            return customers

        except Exception as e:
            logger.error(f"Error getting customers: {str(e)}")
            return []

    def clear_cache(self):
        """Clear all cached data"""
        self.db_client.clear_cache()
        self.ga4_tools.clear_cache()

        if self.use_warehouse and self.warehouse_client:
            self.warehouse_client.clear_cache()
            logger.info("Data cache cleared (old DB + warehouse + GA4)")
        else:
            logger.info("Data cache cleared (old DB + GA4)")