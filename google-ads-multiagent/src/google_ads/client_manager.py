"""
Google Ads Client Manager
Handles Google Ads API connections and query execution
"""
import os
from typing import List, Dict, Any, Optional, Iterator
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from loguru import logger
import yaml
from pathlib import Path
from functools import lru_cache
import asyncio
from datetime import datetime, timedelta


class GoogleAdsManager:
    """Manages Google Ads API client and operations"""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize Google Ads Manager

        Args:
            config_path: Path to Google Ads configuration file
        """
        if not config_path:
            config_path = os.path.join(
                Path(__file__).parent.parent.parent,
                "config",
                "google_ads_config.yaml"
            )

        try:
            # Load configuration
            with open(config_path, 'r') as f:
                self.config = yaml.safe_load(f)

            # Override with environment variables if present
            self._override_with_env()

            # Initialize client
            self.client = GoogleAdsClient.load_from_dict(self.config)
            self.ga_service = None
            self._initialize_service()

            logger.info("Google Ads Manager initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Google Ads Manager: {str(e)}")
            raise

    def _override_with_env(self):
        """Override config with environment variables"""
        env_mappings = {
            'developer_token': 'GOOGLE_ADS_DEVELOPER_TOKEN',
            'client_id': 'GOOGLE_ADS_CLIENT_ID',
            'client_secret': 'GOOGLE_ADS_CLIENT_SECRET',
            'refresh_token': 'GOOGLE_ADS_REFRESH_TOKEN',
            'login_customer_id': 'GOOGLE_ADS_LOGIN_CUSTOMER_ID'
        }

        for config_key, env_key in env_mappings.items():
            env_value = os.getenv(env_key)
            if env_value:
                self.config[config_key] = env_value

    def _initialize_service(self):
        """Initialize Google Ads service"""
        self.ga_service = self.get_service("GoogleAdsService")

    def get_service(self, service_name: str, version: str = "v18"):
        """
        Get Google Ads service

        Args:
            service_name: Name of the service
            version: API version

        Returns:
            Service instance
        """
        return self.client.get_service(service_name, version=version)

    def execute_query(
        self,
        customer_id: str,
        query: str,
        page_size: int = 1000
    ) -> Iterator[Dict]:
        """
        Execute GAQL query

        Args:
            customer_id: Customer ID
            query: GAQL query string
            page_size: Results per page

        Returns:
            Iterator of result dictionaries
        """
        try:
            # Remove hyphens from customer ID
            customer_id = customer_id.replace("-", "")

            # Execute search stream
            stream = self.ga_service.search_stream(
                customer_id=customer_id,
                query=query
            )

            # Process results
            for batch in stream:
                for row in batch.results:
                    yield self._row_to_dict(row)

        except GoogleAdsException as ex:
            logger.error(f"Google Ads API error: {ex}")
            self._handle_google_ads_error(ex)
            raise

    async def execute_query_async(
        self,
        customer_id: str,
        query: str
    ) -> List[Dict]:
        """
        Execute GAQL query asynchronously

        Args:
            customer_id: Customer ID
            query: GAQL query string

        Returns:
            List of result dictionaries
        """
        loop = asyncio.get_event_loop()
        results = await loop.run_in_executor(
            None,
            lambda: list(self.execute_query(customer_id, query))
        )
        return results

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """
        Convert protobuf row to dictionary

        Args:
            row: Protobuf row object

        Returns:
            Dictionary representation
        """
        result = {}

        # Process each field in the row
        for field in row._pb.DESCRIPTOR.fields:
            if row._pb.HasField(field.name):
                value = getattr(row, field.name)
                result[field.name] = self._convert_value(value)

        return result

    def _convert_value(self, value) -> Any:
        """
        Convert protobuf value to Python type

        Args:
            value: Protobuf value

        Returns:
            Python value
        """
        if hasattr(value, '_pb'):
            # Nested message
            return self._message_to_dict(value._pb)
        elif hasattr(value, '__iter__') and not isinstance(value, (str, bytes)):
            # Repeated field
            return [self._convert_value(v) for v in value]
        else:
            return value

    def _message_to_dict(self, message) -> Dict:
        """
        Convert protobuf message to dictionary

        Args:
            message: Protobuf message

        Returns:
            Dictionary representation
        """
        result = {}
        for field, value in message.ListFields():
            if field.label == field.LABEL_REPEATED:
                result[field.name] = [
                    self._convert_value(v) for v in value
                ]
            else:
                result[field.name] = self._convert_value(value)
        return result

    def _handle_google_ads_error(self, exception: GoogleAdsException):
        """
        Handle Google Ads API errors

        Args:
            exception: GoogleAdsException
        """
        for error in exception.failure.errors:
            logger.error(f"Error code: {error.error_code}")
            logger.error(f"Error message: {error.message}")
            if error.location:
                for field_path_element in error.location.field_path_elements:
                    logger.error(f"Field: {field_path_element.field_name}")

    @lru_cache(maxsize=100)
    def get_accessible_customers(self) -> List[Dict[str, str]]:
        """
        Get list of accessible customer accounts

        Returns:
            List of customer dictionaries
        """
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

        customers = []
        try:
            for row in self.execute_query(
                self.config.get('login_customer_id', ''),
                query
            ):
                if row.get('customer_client', {}).get('status') == 'ENABLED':
                    customers.append({
                        'customer_id': str(row['customer_client']['id']),
                        'customer_name': row['customer_client']['descriptive_name'],
                        'is_manager': row['customer_client'].get('manager', False),
                        'level': row['customer_client'].get('level', 0)
                    })

            logger.info(f"Found {len(customers)} accessible customers")
            return customers

        except Exception as e:
            logger.error(f"Failed to get accessible customers: {str(e)}")
            return []

    def build_date_range_query(
        self,
        days_back: int = 30
    ) -> str:
        """
        Build date range condition for GAQL

        Args:
            days_back: Number of days to look back

        Returns:
            Date range query string
        """
        if days_back == 30:
            return "segments.date DURING LAST_30_DAYS"
        elif days_back == 7:
            return "segments.date DURING LAST_7_DAYS"
        elif days_back == 14:
            return "segments.date DURING LAST_14_DAYS"
        else:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=days_back)).strftime("%Y-%m-%d")
            return f"segments.date BETWEEN '{start_date}' AND '{end_date}'"

    def validate_customer_id(self, customer_id: str) -> bool:
        """
        Validate customer ID format

        Args:
            customer_id: Customer ID to validate

        Returns:
            True if valid
        """
        # Remove hyphens
        clean_id = customer_id.replace("-", "")

        # Check if it's numeric and 10 digits
        return clean_id.isdigit() and len(clean_id) == 10

    def get_account_hierarchy(self) -> Dict:
        """
        Get complete account hierarchy

        Returns:
            Dictionary with account hierarchy
        """
        query = """
            SELECT
                customer_client.id,
                customer_client.descriptive_name,
                customer_client.level,
                customer_client.manager,
                customer_client.status,
                customer_client.currency_code,
                customer_client.time_zone
            FROM customer_client
        """

        hierarchy = {
            'manager_accounts': [],
            'client_accounts': [],
            'total_accounts': 0
        }

        try:
            for row in self.execute_query(
                self.config.get('login_customer_id', ''),
                query
            ):
                account_info = {
                    'id': str(row['customer_client']['id']),
                    'name': row['customer_client']['descriptive_name'],
                    'level': row['customer_client'].get('level', 0),
                    'status': row['customer_client'].get('status', 'UNKNOWN'),
                    'currency': row['customer_client'].get('currency_code', 'USD'),
                    'timezone': row['customer_client'].get('time_zone', 'UTC')
                }

                if row['customer_client'].get('manager', False):
                    hierarchy['manager_accounts'].append(account_info)
                else:
                    hierarchy['client_accounts'].append(account_info)

            hierarchy['total_accounts'] = (
                len(hierarchy['manager_accounts']) +
                len(hierarchy['client_accounts'])
            )

            return hierarchy

        except Exception as e:
            logger.error(f"Failed to get account hierarchy: {str(e)}")
            return hierarchy

    def test_connection(self) -> bool:
        """
        Test Google Ads API connection

        Returns:
            True if connection successful
        """
        try:
            # Try to get customer info
            customer_service = self.get_service("CustomerService")
            customer_id = self.config.get('login_customer_id', '')

            # Remove hyphens
            customer_id = customer_id.replace("-", "")

            # Get customer info
            customer = customer_service.get_customer(
                resource_name=f"customers/{customer_id}"
            )

            logger.info(f"Connected to Google Ads API - Customer: {customer.descriptive_name}")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Google Ads API: {str(e)}")
            return False


class QueryBuilder:
    """Helper class for building GAQL queries"""

    @staticmethod
    def campaign_performance(
        date_range: str = "LAST_30_DAYS",
        metrics: Optional[List[str]] = None,
        segments: Optional[List[str]] = None
    ) -> str:
        """
        Build campaign performance query

        Args:
            date_range: Date range for the query
            metrics: List of metrics to include
            segments: List of segments to include

        Returns:
            GAQL query string
        """
        # Default metrics
        if not metrics:
            metrics = [
                "metrics.impressions",
                "metrics.clicks",
                "metrics.cost_micros",
                "metrics.conversions",
                "metrics.conversions_value"
            ]

        # Default segments
        if not segments:
            segments = ["segments.date"]

        # Build SELECT clause
        select_fields = [
            "campaign.id",
            "campaign.name",
            "campaign.status",
            "campaign.advertising_channel_type",
            "campaign.bidding_strategy_type",
            "campaign.campaign_budget.amount_micros"
        ] + metrics + segments

        # Build query
        query = f"""
            SELECT
                {', '.join(select_fields)}
            FROM campaign
            WHERE segments.date DURING {date_range}
                AND campaign.status != 'REMOVED'
        """

        return query.strip()

    @staticmethod
    def keyword_performance(
        date_range: str = "LAST_30_DAYS",
        min_impressions: int = 0
    ) -> str:
        """
        Build keyword performance query

        Args:
            date_range: Date range for the query
            min_impressions: Minimum impressions filter

        Returns:
            GAQL query string
        """
        query = f"""
            SELECT
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.status,
                ad_group_criterion.quality_info.quality_score,
                ad_group_criterion.ad_group,
                metrics.impressions,
                metrics.clicks,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                segments.date
            FROM ad_group_criterion
            WHERE ad_group_criterion.type = 'KEYWORD'
                AND segments.date DURING {date_range}
                AND ad_group_criterion.status != 'REMOVED'
                AND metrics.impressions > {min_impressions}
        """

        return query.strip()

    @staticmethod
    def search_term_report(
        date_range: str = "LAST_30_DAYS",
        min_impressions: int = 10
    ) -> str:
        """
        Build search term report query

        Args:
            date_range: Date range for the query
            min_impressions: Minimum impressions filter

        Returns:
            GAQL query string
        """
        query = f"""
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
            WHERE segments.date DURING {date_range}
                AND metrics.impressions > {min_impressions}
        """

        return query.strip()