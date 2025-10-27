"""
Google Ads Real-time Service
Uses Google Ads API with GAQL (Google Ads Query Language) for live data querying
"""
from typing import List, Dict, Any, Optional
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException
from app.core.config import settings
import os
from pathlib import Path
from dotenv import load_dotenv
from loguru import logger

# Load .env file explicitly
env_path = Path(__file__).parent.parent.parent.parent / '.env'
if env_path.exists():
    load_dotenv(env_path)
    logger.info(f"✅ Loaded .env from: {env_path}")
else:
    logger.warning(f"⚠️  .env file not found at: {env_path}")


class GoogleAdsService:
    """Service for real-time Google Ads API queries using GAQL"""

    def __init__(self):
        """Initialize Google Ads client from environment credentials"""
        # Load credentials from environment
        developer_token = os.getenv("GOOGLE_ADS_DEVELOPER_TOKEN")
        client_id = os.getenv("GOOGLE_ADS_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_ADS_CLIENT_SECRET")
        refresh_token = os.getenv("GOOGLE_ADS_REFRESH_TOKEN")
        login_customer_id = os.getenv("GOOGLE_ADS_LOGIN_CUSTOMER_ID")

        # Validate all required credentials are present
        missing_creds = []
        if not developer_token:
            missing_creds.append("GOOGLE_ADS_DEVELOPER_TOKEN")
        if not client_id:
            missing_creds.append("GOOGLE_ADS_CLIENT_ID")
        if not client_secret:
            missing_creds.append("GOOGLE_ADS_CLIENT_SECRET")
        if not refresh_token:
            missing_creds.append("GOOGLE_ADS_REFRESH_TOKEN")

        if missing_creds:
            error_msg = f"Missing required environment variables: {', '.join(missing_creds)}"
            logger.error(f"❌ {error_msg}")
            raise ValueError(error_msg)

        # Build credentials dictionary for Google Ads client
        self.credentials = {
            "developer_token": developer_token,
            "client_id": client_id,
            "client_secret": client_secret,
            "refresh_token": refresh_token,
            "token_uri": "https://oauth2.googleapis.com/token",
            "use_proto_plus": True
        }

        # Add login customer ID if provided (optional for MCC accounts)
        if login_customer_id:
            self.credentials["login_customer_id"] = login_customer_id

        # Initialize client
        try:
            logger.info("🔧 Initializing Google Ads API client...")
            logger.debug(f"Using client_id: {client_id[:20]}...")
            logger.debug(f"Using developer_token: {developer_token[:10]}...")

            self.client = GoogleAdsClient.load_from_dict(self.credentials)
            logger.info("✅ Google Ads API client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Google Ads client: {e}")
            logger.error(f"Credentials keys present: {list(self.credentials.keys())}")
            raise

    def execute_query(
        self,
        customer_id: str,
        query: str
    ) -> List[Dict[str, Any]]:
        """
        Execute a GAQL query and return results as list of dictionaries

        Args:
            customer_id: Google Ads customer ID (without hyphens)
            query: GAQL query string

        Returns:
            List of dictionaries containing query results
        """
        try:
            # Remove hyphens from customer ID if present
            customer_id = str(customer_id).replace("-", "")

            # Get GoogleAds service
            ga_service = self.client.get_service("GoogleAdsService")

            # Execute query
            logger.info(f"🔍 Executing GAQL query for customer {customer_id}")
            logger.debug(f"Query: {query}")

            stream = ga_service.search_stream(
                customer_id=customer_id,
                query=query
            )

            # Process results
            results = []
            for batch in stream:
                for row in batch.results:
                    # Convert protobuf row to dictionary
                    row_dict = self._row_to_dict(row)
                    results.append(row_dict)

            logger.info(f"✅ Query returned {len(results)} rows")
            return results

        except GoogleAdsException as ex:
            logger.error(f"❌ Google Ads API error: {ex.error.code().name}")
            for error in ex.failure.errors:
                logger.error(f"  - {error.message}")
            raise
        except Exception as e:
            logger.error(f"❌ Error executing query: {e}")
            raise

    def _row_to_dict(self, row) -> Dict[str, Any]:
        """
        Convert protobuf row to dictionary
        Handles proto-plus messages and nested fields
        """
        import json
        from google.protobuf.json_format import MessageToDict

        # Convert proto message to dict using protobuf's built-in converter
        try:
            # For proto-plus messages, convert to dict directly
            result = MessageToDict(row._pb, preserving_proto_field_name=True)
            return result
        except Exception as e:
            logger.warning(f"Could not convert message to dict: {e}")
            # Fallback: manual extraction
            result = {}
            if hasattr(row, '_pb'):
                # Proto-plus message
                for field, value in row._pb.ListFields():
                    field_name = field.name
                    result[field_name] = self._convert_value(value)
            return result

    def _convert_value(self, value):
        """Convert protobuf value to Python native type"""
        from google.protobuf.message import Message

        if isinstance(value, Message):
            return self._message_to_dict(value)
        elif isinstance(value, (list, tuple)):
            return [self._convert_value(item) for item in value]
        else:
            return value

    def _message_to_dict(self, message) -> Dict[str, Any]:
        """Convert nested protobuf message to dictionary"""
        from google.protobuf.json_format import MessageToDict

        try:
            result = MessageToDict(message, preserving_proto_field_name=True)

            # Convert micros fields to standard currency
            converted_result = {}
            for key, value in result.items():
                converted_result[key] = value
                if key.endswith("_micros") and isinstance(value, (int, float)):
                    base_name = key.replace("_micros", "")
                    converted_result[base_name] = value / 1_000_000 if value else 0

            return converted_result
        except Exception as e:
            logger.warning(f"Could not convert nested message: {e}")
            return {}

    def list_accessible_customers(self) -> List[Dict[str, Any]]:
        """
        List all accessible Google Ads customer accounts

        Returns:
            List of customer dictionaries with id and resource_name
        """
        try:
            customer_service = self.client.get_service("CustomerService")
            accessible_customers = customer_service.list_accessible_customers()

            customers = []
            for customer_resource in accessible_customers.resource_names:
                # Extract customer ID from resource name
                # Format: customers/1234567890
                customer_id = customer_resource.split("/")[1]
                customers.append({
                    "customer_id": customer_id,
                    "resource_name": customer_resource
                })

            logger.info(f"✅ Found {len(customers)} accessible customers")
            return customers

        except Exception as e:
            logger.error(f"❌ Error listing customers: {e}")
            raise

    def list_client_accounts(self, manager_customer_id: str) -> List[Dict[str, Any]]:
        """
        List all client accounts under a manager account (MCC)

        Args:
            manager_customer_id: Manager account customer ID

        Returns:
            List of client account dictionaries
        """
        try:
            query = """
                SELECT
                    customer_client.client_customer,
                    customer_client.level,
                    customer_client.manager,
                    customer_client.descriptive_name,
                    customer_client.currency_code,
                    customer_client.time_zone,
                    customer_client.id,
                    customer_client.status
                FROM customer_client
                WHERE customer_client.status = 'ENABLED'
                  AND customer_client.level = 1
            """

            results = self.execute_query(manager_customer_id, query)

            client_accounts = []
            for row in results:
                customer_client = row.get("customer_client", {})
                # Extract client customer ID from resource name
                client_customer_resource = customer_client.get("client_customer", "")
                if client_customer_resource:
                    client_id = client_customer_resource.split("/")[1] if "/" in client_customer_resource else None
                    if client_id:
                        client_accounts.append({
                            "customer_id": client_id,
                            "descriptive_name": customer_client.get("descriptive_name", f"Client {client_id}"),
                            "currency_code": customer_client.get("currency_code", ""),
                            "time_zone": customer_client.get("time_zone", ""),
                            "is_manager": customer_client.get("manager", False),
                            "status": customer_client.get("status", "")
                        })

            logger.info(f"✅ Found {len(client_accounts)} client accounts under manager {manager_customer_id}")
            return client_accounts

        except Exception as e:
            logger.error(f"❌ Error listing client accounts: {e}")
            raise

    def get_customer_info(self, customer_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific customer

        Args:
            customer_id: Google Ads customer ID

        Returns:
            Dictionary with customer details
        """
        query = """
            SELECT
                customer.id,
                customer.descriptive_name,
                customer.currency_code,
                customer.time_zone,
                customer.status,
                customer.manager
            FROM customer
            WHERE customer.id = {customer_id}
        """.replace("{customer_id}", str(customer_id))

        results = self.execute_query(customer_id, query)
        return results[0] if results else {}

    def get_campaigns(
        self,
        customer_id: str,
        status: Optional[str] = None,
        date_range: str = "LAST_30_DAYS"
    ) -> List[Dict[str, Any]]:
        """
        Get campaigns with performance metrics

        Args:
            customer_id: Google Ads customer ID
            status: Filter by status (ENABLED, PAUSED, REMOVED)
            date_range: Date range for metrics (LAST_7_DAYS, LAST_30_DAYS, etc.)

        Returns:
            List of campaign dictionaries
        """
        query = f"""
            SELECT
                campaign.id,
                campaign.name,
                campaign.status,
                campaign.advertising_channel_type,
                campaign.bidding_strategy_type,
                campaign_budget.amount_micros,
                campaign.optimization_score,
                campaign.start_date,
                campaign.end_date,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc
            FROM campaign
            WHERE segments.date DURING {date_range}
        """

        if status:
            query += f" AND campaign.status = '{status}'"

        return self.execute_query(customer_id, query)

    def get_keywords(
        self,
        customer_id: str,
        campaign_id: Optional[int] = None,
        date_range: str = "LAST_30_DAYS",
        min_quality_score: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Get keywords with performance metrics and quality scores

        Args:
            customer_id: Google Ads customer ID
            campaign_id: Filter by campaign ID
            date_range: Date range for metrics
            min_quality_score: Minimum quality score filter

        Returns:
            List of keyword dictionaries
        """
        query = f"""
            SELECT
                ad_group_criterion.criterion_id,
                ad_group_criterion.keyword.text,
                ad_group_criterion.keyword.match_type,
                ad_group_criterion.status,
                ad_group_criterion.quality_info.quality_score,
                ad_group_criterion.quality_info.creative_quality_score,
                ad_group_criterion.quality_info.post_click_quality_score,
                ad_group_criterion.quality_info.search_predicted_ctr,
                ad_group_criterion.cpc_bid_micros,
                ad_group_criterion.final_urls,
                ad_group.id,
                ad_group.name,
                campaign.id,
                campaign.name,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc
            FROM keyword_view
            WHERE segments.date DURING {date_range}
              AND ad_group_criterion.status != 'REMOVED'
        """

        if campaign_id:
            query += f" AND campaign.id = {campaign_id}"

        if min_quality_score:
            query += f" AND ad_group_criterion.quality_info.quality_score >= {min_quality_score}"

        return self.execute_query(customer_id, query)

    def get_search_terms(
        self,
        customer_id: str,
        campaign_id: Optional[int] = None,
        date_range: str = "LAST_30_DAYS"
    ) -> List[Dict[str, Any]]:
        """
        Get search terms (actual user queries) with performance

        Args:
            customer_id: Google Ads customer ID
            campaign_id: Filter by campaign ID
            date_range: Date range for metrics

        Returns:
            List of search term dictionaries
        """
        query = f"""
            SELECT
                search_term_view.search_term,
                search_term_view.status,
                segments.keyword.info.text,
                segments.keyword.info.match_type,
                search_term_view.search_term_match_type,
                ad_group.id,
                ad_group.name,
                campaign.id,
                campaign.name,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions,
                metrics.conversions_value,
                metrics.ctr,
                metrics.average_cpc
            FROM search_term_view
            WHERE segments.date DURING {date_range}
        """

        if campaign_id:
            query += f" AND campaign.id = {campaign_id}"

        return self.execute_query(customer_id, query)

    def get_ad_groups(
        self,
        customer_id: str,
        campaign_id: Optional[int] = None,
        date_range: str = "LAST_30_DAYS"
    ) -> List[Dict[str, Any]]:
        """
        Get ad groups with performance metrics

        Args:
            customer_id: Google Ads customer ID
            campaign_id: Filter by campaign ID
            date_range: Date range for metrics

        Returns:
            List of ad group dictionaries
        """
        query = f"""
            SELECT
                ad_group.id,
                ad_group.name,
                ad_group.status,
                ad_group.type,
                ad_group.cpc_bid_micros,
                campaign.id,
                campaign.name,
                metrics.clicks,
                metrics.impressions,
                metrics.cost_micros,
                metrics.conversions,
                metrics.ctr,
                metrics.average_cpc
            FROM ad_group
            WHERE segments.date DURING {date_range}
              AND ad_group.status != 'REMOVED'
        """

        if campaign_id:
            query += f" AND campaign.id = {campaign_id}"

        return self.execute_query(customer_id, query)


def get_google_ads_service() -> GoogleAdsService:
    """
    Create a new GoogleAdsService instance with fresh credentials
    Note: Removed singleton pattern to ensure credentials are always reloaded
    """
    # Reload .env file to get latest credentials
    env_path = Path(__file__).parent.parent.parent.parent / '.env'
    if env_path.exists():
        load_dotenv(env_path, override=True)  # override=True to reload values
    return GoogleAdsService()
