"""
Google Analytics 4 (GA4) data collection tools for Data Agent

Provides user behavior insights to enrich Google Ads campaign analysis
"""
from typing import Dict, List, Any, Optional
from loguru import logger
import pandas as pd
from datetime import datetime, timedelta


class GA4Tools:
    """Tools for fetching GA4 user behavior data via REST API"""

    def __init__(self, api_client):
        """
        Initialize GA4 tools

        Args:
            api_client: APIClient instance for REST API calls
        """
        self.api_client = api_client

    def fetch_ga4_sessions(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        source: Optional[str] = None,
        campaign: Optional[str] = None,
        device: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Fetch GA4 session behavior data

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            source: Filter by traffic source
            campaign: Filter by campaign name
            device: Filter by device category (desktop, mobile, tablet)
            limit: Maximum number of results

        Returns:
            Dictionary with session data including bounce rate, engagement, pages/session
        """
        try:
            params = {"customer_id": customer_id, "limit": limit}

            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if source:
                params["source"] = source
            if campaign:
                params["campaign"] = campaign
            if device:
                params["device"] = device

            # Check cache
            cache_key = f"ga4_sessions_{customer_id}_{start_date}_{end_date}_{source}_{campaign}"
            cached = self.api_client._get_cached(cache_key)
            if cached:
                return cached

            # Fetch from API
            result = self.api_client._make_request(
                "GET",
                "/api/v1/ga4/sessions",
                params=params
            )

            if "error" not in result:
                self.api_client._set_cache(cache_key, result)
                logger.info(f"Fetched {result.get('total_count', 0)} GA4 session records")
            else:
                logger.error(f"GA4 sessions fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 sessions: {str(e)}")
            return {"error": str(e), "status": "failed"}

    def fetch_ga4_behavior_by_campaign(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch aggregated user behavior metrics grouped by campaign

        This is CRITICAL for understanding campaign quality beyond just conversions.

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dictionary with campaigns and their behavior metrics:
            - Bounce rate (% of single-page sessions)
            - Engagement rate (% of engaged sessions)
            - Avg session duration (seconds)
            - Pages per session
            - Conversions
        """
        try:
            params = {"customer_id": customer_id}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            cache_key = f"ga4_behavior_campaign_{customer_id}_{start_date}_{end_date}"
            cached = self.api_client._get_cached(cache_key)
            if cached:
                return cached

            result = self.api_client._make_request(
                "GET",
                "/api/v1/ga4/sessions/by-campaign",
                params=params
            )

            if "error" not in result:
                self.api_client._set_cache(cache_key, result)
                logger.info(f"Fetched GA4 behavior data for {len(result)} campaigns")
            else:
                logger.error(f"GA4 campaign behavior fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 campaign behavior: {str(e)}")
            return {"error": str(e), "status": "failed"}

    def fetch_ga4_campaign_quality_score(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get campaign quality scores based on GA4 user behavior

        Quality score (0-100) calculated from:
        - Bounce rate (40% weight - lower is better)
        - Engagement rate (30% weight - higher is better)
        - Pages per session (30% weight - higher is better)

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dictionary with campaigns and quality scores + recommendations
        """
        try:
            params = {"customer_id": customer_id}
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            cache_key = f"ga4_quality_{customer_id}_{start_date}_{end_date}"
            cached = self.api_client._get_cached(cache_key)
            if cached:
                return cached

            # Fetch campaign enrichment endpoint (combines Ads + GA4 data)
            result = self.api_client._make_request(
                "GET",
                "/api/v1/ga4/campaign-enrichment",
                params=params
            )

            if "error" not in result:
                self.api_client._set_cache(cache_key, result)
                logger.info(f"Fetched quality scores for {result.get('total_count', 0)} campaigns")
            else:
                logger.error(f"GA4 quality score fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 quality scores: {str(e)}")
            return {"error": str(e), "status": "failed"}

    def fetch_ga4_events(
        self,
        customer_id: int = 1,
        event_name: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Fetch GA4 event tracking data

        Common events: page_view, purchase, add_to_cart, begin_checkout, sign_up

        Args:
            customer_id: Customer ID
            event_name: Filter by specific event (e.g., "purchase", "add_to_cart")
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            limit: Maximum number of results

        Returns:
            Dictionary with event data including counts and values
        """
        try:
            params = {"customer_id": customer_id, "limit": limit}

            if event_name:
                params["event_name"] = event_name
            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            cache_key = f"ga4_events_{customer_id}_{event_name}_{start_date}_{end_date}"
            cached = self.api_client._get_cached(cache_key)
            if cached:
                return cached

            result = self.api_client._make_request(
                "GET",
                "/api/v1/ga4/events",
                params=params
            )

            if "error" not in result:
                self.api_client._set_cache(cache_key, result)
                logger.info(f"Fetched {result.get('total_count', 0)} GA4 event records")
            else:
                logger.error(f"GA4 events fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 events: {str(e)}")
            return {"error": str(e), "status": "failed"}

    def fetch_ga4_conversion_paths(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        min_touchpoints: Optional[int] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Fetch GA4 conversion paths for multi-touch attribution analysis

        Shows the full customer journey from first touch to conversion.
        Critical for understanding which campaigns contribute to conversions.

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            min_touchpoints: Minimum number of touchpoints in path
            limit: Maximum number of results

        Returns:
            Dictionary with conversion paths showing:
            - All touchpoints in customer journey
            - First-touch and last-touch sources
            - Days to conversion
            - Conversion value
        """
        try:
            params = {"customer_id": customer_id, "limit": limit}

            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if min_touchpoints:
                params["min_touchpoints"] = min_touchpoints

            cache_key = f"ga4_paths_{customer_id}_{start_date}_{end_date}_{min_touchpoints}"
            cached = self.api_client._get_cached(cache_key)
            if cached:
                return cached

            result = self.api_client._make_request(
                "GET",
                "/api/v1/ga4/conversion-paths",
                params=params
            )

            if "error" not in result:
                self.api_client._set_cache(cache_key, result)
                logger.info(f"Fetched {result.get('total_count', 0)} GA4 conversion paths")
            else:
                logger.error(f"GA4 conversion paths fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 conversion paths: {str(e)}")
            return {"error": str(e), "status": "failed"}

    def fetch_ga4_audience_insights(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        segment_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Fetch GA4 audience insights (demographics, device, location)

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            segment_type: Filter by segment type (demographic, behavior, technology)

        Returns:
            Dictionary with audience segments including:
            - Country breakdown
            - Device category (desktop, mobile, tablet)
            - Operating system and browser
            - Engagement metrics by segment
        """
        try:
            params = {"customer_id": customer_id}

            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date
            if segment_type:
                params["segment_type"] = segment_type

            cache_key = f"ga4_audience_{customer_id}_{start_date}_{end_date}_{segment_type}"
            cached = self.api_client._get_cached(cache_key)
            if cached:
                return cached

            result = self.api_client._make_request(
                "GET",
                "/api/v1/ga4/audience-insights",
                params=params
            )

            if "error" not in result:
                self.api_client._set_cache(cache_key, result)
                logger.info(f"Fetched {result.get('total_count', 0)} GA4 audience segments")
            else:
                logger.error(f"GA4 audience insights fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 audience insights: {str(e)}")
            return {"error": str(e), "status": "failed"}

    def fetch_ga4_device_performance(
        self,
        customer_id: int = 1,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get device category performance breakdown

        Useful for device bid adjustments in Google Ads.

        Args:
            customer_id: Customer ID
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)

        Returns:
            Dictionary with desktop/mobile/tablet performance metrics
        """
        try:
            params = {"customer_id": customer_id}

            if start_date:
                params["start_date"] = start_date
            if end_date:
                params["end_date"] = end_date

            cache_key = f"ga4_devices_{customer_id}_{start_date}_{end_date}"
            cached = self.api_client._get_cached(cache_key)
            if cached:
                return cached

            result = self.api_client._make_request(
                "GET",
                "/api/v1/ga4/audience-insights/devices",
                params=params
            )

            if "error" not in result:
                self.api_client._set_cache(cache_key, result)
                logger.info(f"Fetched device performance data")
            else:
                logger.error(f"GA4 device performance fetch failed: {result.get('error')}")

            return result

        except Exception as e:
            logger.error(f"Error fetching GA4 device performance: {str(e)}")
            return {"error": str(e), "status": "failed"}

    def clear_cache(self):
        """Clear all GA4 data cache"""
        logger.info("Clearing GA4 data cache")
        self.api_client._cache.clear()
        self.api_client._cache_timestamps.clear()
