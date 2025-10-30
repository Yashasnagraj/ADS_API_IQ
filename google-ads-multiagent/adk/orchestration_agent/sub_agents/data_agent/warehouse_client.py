"""
Warehouse Client for Marketing Data Warehouse
Connects to SQLite warehouse with dimensional star schema
Supports multi-customer and multi-platform queries
"""
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import sqlite3
import pandas as pd
from loguru import logger

# Warehouse database path
WAREHOUSE_DB = project_root / "marketing_warehouse.db"


class WarehouseClient:
    """Client for interacting with Marketing Data Warehouse (SQLite)"""

    def __init__(self, db_path: Optional[str] = None):
        """
        Initialize warehouse client

        Args:
            db_path: Path to warehouse database (defaults to marketing_warehouse.db)
        """
        self.db_path = db_path or WAREHOUSE_DB
        self._cache = {}
        self._cache_timestamps = {}
        self.cache_ttl = 300  # 5 minutes cache

        logger.info(f"Warehouse client initialized: {self.db_path}")

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        return conn

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

    def fetch_campaigns(
        self,
        customer_id: Optional[int] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Fetch campaigns from warehouse

        Args:
            customer_id: Filter by customer ID
            status: Campaign status filter (ENABLED, PAUSED, etc.)
            limit: Maximum number of results

        Returns:
            Campaigns data with performance metrics
        """
        cache_key = f"campaigns_{customer_id}_{status}_{limit}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            # Query campaigns with aggregated performance
            query = """
                SELECT
                    c.campaign_id as id,
                    c.campaign_name as name,
                    c.status,
                    c.channel_type as type,
                    c.budget_amount_micros / 1000000.0 as budget,
                    c.bidding_strategy_type as bidding_strategy,
                    COALESCE(SUM(f.impressions), 0) as impressions,
                    COALESCE(SUM(f.clicks), 0) as clicks,
                    COALESCE(SUM(f.spend_micros), 0) / 1000000.0 as cost,
                    COALESCE(SUM(f.conversions), 0) as conversions,
                    COALESCE(SUM(f.conversion_value_micros), 0) / 1000000.0 as conversion_value,
                    COALESCE(AVG(f.ctr), 0) as ctr,
                    COALESCE(AVG(f.cpc_micros), 0) / 1000000.0 as cpc,
                    CASE
                        WHEN SUM(f.clicks) > 0
                        THEN (SUM(f.conversions) * 100.0 / SUM(f.clicks))
                        ELSE 0
                    END as conversion_rate,
                    CASE
                        WHEN SUM(f.conversions) > 0
                        THEN (SUM(f.spend_micros) / 1000000.0 / SUM(f.conversions))
                        ELSE 0
                    END as cpa,
                    COALESCE(AVG(f.roas), 0) as roas,
                    cust.customer_name,
                    cust.currency
                FROM dim_google_ads_campaign c
                JOIN dim_customer cust ON c.customer_id = cust.customer_id
                LEFT JOIN fact_campaign_performance_daily f
                    ON c.google_campaign_id = f.google_campaign_id
                WHERE 1=1
            """

            params = []

            if customer_id:
                query += " AND c.customer_id = ?"
                params.append(customer_id)

            if status:
                query += " AND c.status = ?"
                params.append(status)

            query += """
                GROUP BY c.campaign_id, c.campaign_name, c.status, c.channel_type,
                         c.budget_amount_micros, c.bidding_strategy_type,
                         cust.customer_name, cust.currency
                ORDER BY COALESCE(SUM(f.spend_micros), 0) DESC
                LIMIT ?
            """
            params.append(limit)

            cursor.execute(query, params)

            campaigns = []
            for row in cursor.fetchall():
                campaigns.append({
                    'id': row['id'],
                    'name': row['name'],
                    'status': row['status'],
                    'type': row['type'],
                    'budget': float(row['budget']) if row['budget'] is not None else 0.0,
                    'bidding_strategy': row['bidding_strategy'],
                    'impressions': int(row['impressions']) if row['impressions'] is not None else 0,
                    'clicks': int(row['clicks']) if row['clicks'] is not None else 0,
                    'cost': float(row['cost']) if row['cost'] is not None else 0.0,
                    'conversions': float(row['conversions']) if row['conversions'] is not None else 0.0,
                    'conversion_value': float(row['conversion_value']) if row['conversion_value'] is not None else 0.0,
                    'ctr': float(row['ctr']) if row['ctr'] is not None else 0.0,
                    'cpc': float(row['cpc']) if row['cpc'] is not None else 0.0,
                    'conversion_rate': float(row['conversion_rate']) if row['conversion_rate'] is not None else 0.0,
                    'cpa': float(row['cpa']) if row['cpa'] is not None else 0.0,
                    'roas': float(row['roas']) if row['roas'] is not None else 0.0,
                    'customer_name': row['customer_name'],
                    'currency': row['currency'],
                    'max_cpc': float(row['cpc'] * 1.2) if row['cpc'] else 2.0
                })

            result = {
                'campaigns': campaigns,
                'total': len(campaigns),
                'status': 'success'
            }

            self._set_cache(cache_key, result)
            logger.info(f"Fetched {len(campaigns)} campaigns from warehouse")

            conn.close()
            return result

        except Exception as e:
            logger.error(f"Error fetching campaigns from warehouse: {str(e)}")
            return {'error': str(e), 'campaigns': [], 'total': 0}

    def fetch_campaign_performance(
        self,
        campaign_id: str,
        days: int = 30,
        customer_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Fetch campaign performance time-series data

        Args:
            campaign_id: Campaign ID
            days: Number of days to fetch
            customer_id: Filter by customer

        Returns:
            Performance data
        """
        cache_key = f"campaign_perf_{campaign_id}_{days}_{customer_id}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                SELECT
                    d.full_date as date,
                    f.impressions,
                    f.clicks,
                    f.spend_micros / 1000000.0 as cost,
                    f.conversions,
                    f.conversion_value_micros / 1000000.0 as conversion_value,
                    f.ctr,
                    f.cpc_micros / 1000000.0 as cpc,
                    f.roas
                FROM fact_campaign_performance_daily f
                JOIN dim_google_ads_campaign c ON f.google_campaign_id = c.google_campaign_id
                JOIN dim_date d ON f.date_id = d.date_id
                WHERE c.campaign_id = ?
                    AND d.full_date >= date('now', '-' || ? || ' days')
            """

            params = [campaign_id, days]

            if customer_id:
                query += " AND c.customer_id = ?"
                params.append(customer_id)

            query += " ORDER BY d.full_date DESC"

            cursor.execute(query, params)

            performance_data = []
            for row in cursor.fetchall():
                performance_data.append({
                    'date': row['date'],
                    'impressions': int(row['impressions']) if row['impressions'] else 0,
                    'clicks': int(row['clicks']) if row['clicks'] else 0,
                    'cost': float(row['cost']) if row['cost'] else 0,
                    'conversions': float(row['conversions']) if row['conversions'] else 0,
                    'conversion_value': float(row['conversion_value']) if row['conversion_value'] else 0,
                    'ctr': float(row['ctr']) if row['ctr'] else 0,
                    'cpc': float(row['cpc']) if row['cpc'] else 0,
                    'roas': float(row['roas']) if row['roas'] else 0
                })

            result = {
                'performance': performance_data,
                'campaign_id': campaign_id,
                'period': f'{days} days',
                'data_points': len(performance_data)
            }

            self._set_cache(cache_key, result)
            logger.info(f"Fetched {len(performance_data)} performance records for campaign {campaign_id}")

            conn.close()
            return result

        except Exception as e:
            logger.error(f"Error fetching campaign performance: {str(e)}")
            return {'error': str(e), 'performance': []}

    def fetch_traffic_sources(
        self,
        customer_id: Optional[int] = None,
        days: int = 30,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Fetch GA4 traffic sources with performance

        Args:
            customer_id: Filter by customer
            days: Number of days
            limit: Maximum results

        Returns:
            Traffic sources data
        """
        cache_key = f"traffic_sources_{customer_id}_{days}_{limit}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                SELECT
                    s.source,
                    s.medium,
                    s.utm_campaign,
                    COALESCE(SUM(f.impressions), 0) as sessions,
                    COALESCE(SUM(f.clicks), 0) as page_views,
                    COALESCE(SUM(f.conversions), 0) as conversions,
                    COALESCE(SUM(f.conversion_value_micros), 0) / 1000000.0 as revenue,
                    cust.customer_name
                FROM dim_ga4_source_medium s
                JOIN dim_customer cust ON s.customer_id = cust.customer_id
                LEFT JOIN fact_campaign_performance_daily f
                    ON s.source_medium_id = f.ga4_source_medium_id
                LEFT JOIN dim_date d ON f.date_id = d.date_id
                WHERE d.full_date >= date('now', '-' || ? || ' days')
            """

            params = [days]

            if customer_id:
                query += " AND s.customer_id = ?"
                params.append(customer_id)

            query += """
                GROUP BY s.source, s.medium, s.utm_campaign, cust.customer_name
                ORDER BY COALESCE(SUM(f.impressions), 0) DESC
                LIMIT ?
            """
            params.append(limit)

            cursor.execute(query, params)

            sources = []
            for row in cursor.fetchall():
                sources.append({
                    'source': row['source'],
                    'medium': row['medium'],
                    'campaign': row['utm_campaign'],
                    'sessions': int(row['sessions']),
                    'page_views': int(row['page_views']),
                    'conversions': float(row['conversions']),
                    'revenue': float(row['revenue']),
                    'customer_name': row['customer_name']
                })

            result = {
                'traffic_sources': sources,
                'total': len(sources),
                'status': 'success'
            }

            self._set_cache(cache_key, result)
            logger.info(f"Fetched {len(sources)} traffic sources from warehouse")

            conn.close()
            return result

        except Exception as e:
            logger.error(f"Error fetching traffic sources: {str(e)}")
            return {'error': str(e), 'traffic_sources': [], 'total': 0}

    def fetch_metrics_summary(
        self,
        customer_id: Optional[int] = None,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Fetch overall metrics summary across all platforms

        Args:
            customer_id: Filter by customer
            days: Number of days

        Returns:
            Metrics summary
        """
        cache_key = f"metrics_summary_{customer_id}_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            query = """
                SELECT
                    COUNT(DISTINCT c.campaign_id) as total_campaigns,
                    COUNT(DISTINCT s.source_medium_id) as total_traffic_sources,
                    COALESCE(SUM(f.impressions), 0) as total_impressions,
                    COALESCE(SUM(f.clicks), 0) as total_clicks,
                    COALESCE(SUM(f.spend_micros), 0) / 1000000.0 as total_cost,
                    COALESCE(SUM(f.conversions), 0) as total_conversions,
                    COALESCE(SUM(f.conversion_value_micros), 0) / 1000000.0 as total_conversion_value,
                    COALESCE(AVG(f.ctr), 0) as avg_ctr,
                    COALESCE(AVG(f.cpc_micros), 0) / 1000000.0 as avg_cpc,
                    CASE
                        WHEN SUM(f.clicks) > 0
                        THEN (SUM(f.conversions) * 100.0 / SUM(f.clicks))
                        ELSE 0
                    END as avg_conversion_rate,
                    COALESCE(AVG(f.roas), 0) as avg_roas
                FROM fact_campaign_performance_daily f
                JOIN dim_date d ON f.date_id = d.date_id
                LEFT JOIN dim_google_ads_campaign c ON f.google_campaign_id = c.google_campaign_id
                LEFT JOIN dim_ga4_source_medium s ON f.ga4_source_medium_id = s.source_medium_id
                WHERE d.full_date >= date('now', '-' || ? || ' days')
            """

            params = [days]

            if customer_id:
                query += " AND f.customer_id = ?"
                params.append(customer_id)

            cursor.execute(query, params)
            row = cursor.fetchone()

            if row:
                summary = {
                    'total_campaigns': int(row['total_campaigns']),
                    'total_traffic_sources': int(row['total_traffic_sources']),
                    'total_impressions': int(row['total_impressions']),
                    'total_clicks': int(row['total_clicks']),
                    'total_cost': float(row['total_cost']),
                    'total_conversions': float(row['total_conversions']),
                    'total_conversion_value': float(row['total_conversion_value']),
                    'avg_ctr': float(row['avg_ctr']),
                    'avg_cpc': float(row['avg_cpc']),
                    'avg_conversion_rate': float(row['avg_conversion_rate']),
                    'avg_roas': float(row['avg_roas']),
                    'period': f'Last {days} days'
                }
            else:
                summary = {}

            result = {
                'summary': summary,
                'status': 'success',
                'generated_at': datetime.now().isoformat()
            }

            self._set_cache(cache_key, result)
            logger.info("Fetched metrics summary from warehouse")

            conn.close()
            return result

        except Exception as e:
            logger.error(f"Error fetching metrics summary: {str(e)}")
            return {'error': str(e), 'summary': {}}

    def get_customers(self) -> List[Dict[str, Any]]:
        """
        Get list of all customers in warehouse

        Returns:
            List of customers
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()

            cursor.execute("""
                SELECT
                    customer_id,
                    customer_name,
                    google_ads_customer_id,
                    meta_business_id,
                    ga4_account_id,
                    currency,
                    is_active
                FROM dim_customer
                WHERE is_active = 1
                ORDER BY customer_name
            """)

            customers = []
            for row in cursor.fetchall():
                customers.append({
                    'customer_id': row['customer_id'],
                    'customer_name': row['customer_name'],
                    'google_ads_customer_id': row['google_ads_customer_id'],
                    'meta_business_id': row['meta_business_id'],
                    'ga4_account_id': row['ga4_account_id'],
                    'currency': row['currency'],
                    'is_active': bool(row['is_active'])
                })

            conn.close()
            logger.info(f"Found {len(customers)} active customers in warehouse")
            return customers

        except Exception as e:
            logger.error(f"Error getting customers: {str(e)}")
            return []

    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Warehouse cache cleared")
