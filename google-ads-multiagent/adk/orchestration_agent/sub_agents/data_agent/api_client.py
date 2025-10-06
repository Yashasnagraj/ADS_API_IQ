"""
API Client for MarketingIQ REST API integration
"""
import requests
from typing import Dict, Any, Optional, List
from functools import lru_cache
import time
from loguru import logger
from datetime import datetime, timedelta


class APIClient:
    """Client for interacting with MarketingIQ REST API"""

    def __init__(self, base_url: str = "http://localhost:8000", cache_ttl: int = 300):
        """
        Initialize API client with caching

        Args:
            base_url: Base URL of the API
            cache_ttl: Cache time-to-live in seconds (default 5 minutes)
        """
        self.base_url = base_url.rstrip('/')
        self.cache_ttl = cache_ttl
        self._cache = {}
        self._cache_timestamps = {}
        self.session = requests.Session()

    def _is_cache_valid(self, key: str) -> bool:
        """Check if cached data is still valid"""
        if key not in self._cache_timestamps:
            return False
        return (datetime.now() - self._cache_timestamps[key]).total_seconds() < self.cache_ttl

    def _get_cached(self, key: str) -> Optional[Any]:
        """Get cached data if valid"""
        if self._is_cache_valid(key):
            logger.debug(f"Cache hit for {key}")
            return self._cache.get(key)
        return None

    def _set_cache(self, key: str, value: Any):
        """Set cache with timestamp"""
        self._cache[key] = value
        self._cache_timestamps[key] = datetime.now()

    def _make_request(self, method: str, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Make HTTP request with error handling

        Args:
            method: HTTP method
            endpoint: API endpoint
            params: Query parameters

        Returns:
            Response data
        """
        url = f"{self.base_url}{endpoint}"

        try:
            response = self.session.request(method, url, params=params, timeout=30)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {str(e)}")
            return {"error": str(e), "status": "failed"}

    def fetch_search_terms(self, min_impressions: int = 10, limit: int = 100) -> Dict[str, Any]:
        """
        Fetch search terms from API with caching

        Args:
            min_impressions: Minimum impressions threshold
            limit: Maximum number of results

        Returns:
            Search terms data
        """
        cache_key = f"search_terms_{min_impressions}_{limit}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        result = self._make_request(
            "GET",
            "/api/searchterms",
            params={"min_impressions": min_impressions, "limit": limit}
        )

        if "error" not in result:
            self._set_cache(cache_key, result)

        return result

    def fetch_ml_features(self, entity_type: str = "campaign") -> Dict[str, Any]:
        """
        Fetch ML features from API

        Args:
            entity_type: Type of entity (campaign/keyword)

        Returns:
            ML features data
        """
        cache_key = f"ml_features_{entity_type}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        result = self._make_request("GET", "/api/ml/features", params={"entity_type": entity_type})

        if "error" not in result:
            self._set_cache(cache_key, result)

        return result

    def fetch_campaigns(self, customer_id: Optional[int] = None, status: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """
        Fetch campaigns from API

        Args:
            customer_id: Filter by customer ID
            status: Campaign status filter
            limit: Maximum number of results

        Returns:
            Campaigns data
        """
        cache_key = f"campaigns_{customer_id}_{status}_{limit}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        params = {"limit": limit}
        if customer_id:
            params["customer_id"] = customer_id
        if status:
            params["status"] = status

        result = self._make_request("GET", "/api/campaigns", params=params)

        if "error" not in result:
            self._set_cache(cache_key, result)

        return result

    def fetch_campaign_performance(self, campaign_id: str) -> Dict[str, Any]:
        """
        Fetch campaign performance data

        Args:
            campaign_id: Campaign ID

        Returns:
            Performance data
        """
        cache_key = f"campaign_perf_{campaign_id}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        result = self._make_request("GET", f"/api/campaigns/{campaign_id}/performance")

        if "error" not in result:
            self._set_cache(cache_key, result)

        return result

    def fetch_keywords(self, customer_id: Optional[int] = None, min_quality_score: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch keywords from API

        Args:
            customer_id: Filter by customer ID
            min_quality_score: Minimum quality score filter

        Returns:
            Keywords data
        """
        cache_key = f"keywords_{customer_id}_{min_quality_score}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        params = {}
        if customer_id:
            params["customer_id"] = customer_id
        if min_quality_score:
            params["min_quality_score"] = min_quality_score

        result = self._make_request("GET", "/api/keywords", params=params)

        if "error" not in result:
            self._set_cache(cache_key, result)

        return result

    def fetch_metrics_summary(self, customer_id: Optional[int] = None) -> Dict[str, Any]:
        """
        Fetch overall metrics summary

        Args:
            customer_id: Filter by customer ID

        Returns:
            Metrics summary
        """
        cache_key = f"metrics_summary_{customer_id}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        params = {}
        if customer_id:
            params["customer_id"] = customer_id

        result = self._make_request("GET", "/api/metrics/summary", params=params)

        if "error" not in result:
            self._set_cache(cache_key, result)

        return result

    def fetch_customers(self) -> Dict[str, Any]:
        """
        Fetch list of all customers

        Returns:
            Customers data
        """
        cache_key = "customers"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        result = self._make_request("GET", "/api/customers")

        if "error" not in result:
            self._set_cache(cache_key, result)

        return result

    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("API cache cleared")