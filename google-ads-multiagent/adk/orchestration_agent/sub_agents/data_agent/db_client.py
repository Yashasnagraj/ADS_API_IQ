"""
Database Client for MarketingIQ SQL Server integration
Directly queries the database instead of using REST API
"""
import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))))

from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta
import pandas as pd
from loguru import logger
from db_connection import DatabaseConnection


class DatabaseClient:
    """Client for interacting with MarketingIQ SQL Server Database"""

    def __init__(self):
        """Initialize database client"""
        self.db = DatabaseConnection()
        self._cache = {}
        self._cache_timestamps = {}
        self.cache_ttl = 300  # 5 minutes cache

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

    def fetch_campaigns(self, status: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """
        Fetch campaigns from database

        Args:
            status: Campaign status filter
            limit: Maximum number of results

        Returns:
            Campaigns data
        """
        cache_key = f"campaigns_{status}_{limit}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            query = """
                SELECT TOP (@limit)
                    c.CampaignID as id,
                    c.CampaignName as name,
                    c.Status as status,
                    c.CampaignType as type,
                    c.BudgetAmount as budget,
                    c.BiddingStrategy as bidding_strategy,
                    SUM(cp.Impressions) as impressions,
                    SUM(cp.Clicks) as clicks,
                    SUM(cp.Cost) as cost,
                    SUM(cp.Conversions) as conversions,
                    SUM(cp.ConversionValue) as conversion_value,
                    AVG(cp.CTR) as ctr,
                    AVG(cp.CPC) as cpc,
                    AVG(cp.ConversionRate) as conversion_rate,
                    AVG(cp.CostPerConversion) as cpa,
                    AVG(cp.ROAS) as roas
                FROM dw.DimCampaign c
                LEFT JOIN dw.FactCampaignPerformance cp ON c.CampaignKey = cp.CampaignKey
                WHERE (@status IS NULL OR c.Status = @status)
                GROUP BY c.CampaignID, c.CampaignName, c.Status, c.CampaignType,
                         c.BudgetAmount, c.BiddingStrategy
                ORDER BY SUM(cp.Cost) DESC
            """

            params = {'limit': limit, 'status': status}
            rows = self.db.execute_query(query, params)

            campaigns = []
            for row in rows:
                campaigns.append({
                    'id': row[0],
                    'name': row[1],
                    'status': row[2],
                    'type': row[3],
                    'budget': float(row[4]) if row[4] else 0,
                    'bidding_strategy': row[5],
                    'impressions': int(row[6]) if row[6] else 0,
                    'clicks': int(row[7]) if row[7] else 0,
                    'cost': float(row[8]) if row[8] else 0,
                    'conversions': int(row[9]) if row[9] else 0,
                    'conversion_value': float(row[10]) if row[10] else 0,
                    'ctr': float(row[11]) if row[11] else 0,
                    'cpc': float(row[12]) if row[12] else 0,
                    'conversion_rate': float(row[13]) if row[13] else 0,
                    'cpa': float(row[14]) if row[14] else 0,
                    'roas': float(row[15]) if row[15] else 0,
                    'max_cpc': float(row[12] * 1.2) if row[12] else 2.0  # Estimate max CPC
                })

            result = {
                'campaigns': campaigns,
                'total': len(campaigns),
                'status': 'success'
            }

            self._set_cache(cache_key, result)
            logger.info(f"Fetched {len(campaigns)} campaigns from database")
            return result

        except Exception as e:
            logger.error(f"Error fetching campaigns from database: {str(e)}")
            return {'error': str(e), 'campaigns': []}

    def fetch_campaign_performance(self, campaign_id: str, days: int = 30) -> Dict[str, Any]:
        """
        Fetch campaign performance time-series data

        Args:
            campaign_id: Campaign ID
            days: Number of days to fetch

        Returns:
            Performance data
        """
        cache_key = f"campaign_perf_{campaign_id}_{days}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            query = """
                SELECT
                    d.Date,
                    cp.Impressions,
                    cp.Clicks,
                    cp.Cost,
                    cp.Conversions,
                    cp.ConversionValue,
                    cp.CTR,
                    cp.CPC,
                    cp.ROAS
                FROM dw.FactCampaignPerformance cp
                JOIN dw.DimCampaign c ON cp.CampaignKey = c.CampaignKey
                JOIN dw.DimDate d ON cp.DateKey = d.DateKey
                WHERE c.CampaignID = @campaign_id
                    AND d.Date >= DATEADD(day, -@days, GETDATE())
                ORDER BY d.Date DESC
            """

            params = {'campaign_id': campaign_id, 'days': days}
            rows = self.db.execute_query(query, params)

            performance_data = []
            for row in rows:
                performance_data.append({
                    'date': row[0].strftime('%Y-%m-%d') if row[0] else None,
                    'impressions': int(row[1]) if row[1] else 0,
                    'clicks': int(row[2]) if row[2] else 0,
                    'cost': float(row[3]) if row[3] else 0,
                    'conversions': int(row[4]) if row[4] else 0,
                    'conversion_value': float(row[5]) if row[5] else 0,
                    'ctr': float(row[6]) if row[6] else 0,
                    'cpc': float(row[7]) if row[7] else 0,
                    'roas': float(row[8]) if row[8] else 0
                })

            result = {
                'performance': performance_data,
                'campaign_id': campaign_id,
                'period': f'{days} days'
            }

            self._set_cache(cache_key, result)
            return result

        except Exception as e:
            logger.error(f"Error fetching campaign performance: {str(e)}")
            return {'error': str(e), 'performance': []}

    def fetch_keywords(self, min_quality_score: Optional[int] = None, limit: int = 100) -> Dict[str, Any]:
        """
        Fetch keywords from database

        Args:
            min_quality_score: Minimum quality score filter
            limit: Maximum number of results

        Returns:
            Keywords data
        """
        cache_key = f"keywords_{min_quality_score}_{limit}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            query = """
                SELECT TOP (@limit)
                    k.KeywordID as id,
                    k.KeywordText as text,
                    k.MatchType as match_type,
                    k.Status as status,
                    k.MaxCPC as max_cpc,
                    AVG(kp.QualityScore) as quality_score,
                    SUM(kp.Impressions) as impressions,
                    SUM(kp.Clicks) as clicks,
                    SUM(kp.Cost) as cost,
                    SUM(kp.Conversions) as conversions,
                    SUM(kp.ConversionValue) as conversion_value,
                    AVG(kp.CTR) as ctr,
                    AVG(kp.CPC) as cpc,
                    AVG(kp.AvgPosition) as avg_position
                FROM dw.DimKeyword k
                LEFT JOIN dw.FactKeywordPerformance kp ON k.KeywordKey = kp.KeywordKey
                WHERE (@min_qs IS NULL OR kp.QualityScore >= @min_qs)
                GROUP BY k.KeywordID, k.KeywordText, k.MatchType, k.Status, k.MaxCPC
                HAVING SUM(kp.Impressions) > 0
                ORDER BY SUM(kp.Cost) DESC
            """

            params = {'limit': limit, 'min_qs': min_quality_score}
            rows = self.db.execute_query(query, params)

            keywords = []
            for row in rows:
                keywords.append({
                    'id': row[0],
                    'text': row[1],
                    'match_type': row[2],
                    'status': row[3],
                    'max_cpc': float(row[4]) if row[4] else 2.0,
                    'quality_score': int(row[5]) if row[5] else 5,
                    'impressions': int(row[6]) if row[6] else 0,
                    'clicks': int(row[7]) if row[7] else 0,
                    'cost': float(row[8]) if row[8] else 0,
                    'conversions': int(row[9]) if row[9] else 0,
                    'conversion_value': float(row[10]) if row[10] else 0,
                    'ctr': float(row[11]) if row[11] else 0,
                    'cpc': float(row[12]) if row[12] else 0,
                    'avg_position': float(row[13]) if row[13] else 0,
                    'conversion_rate': (int(row[9]) / int(row[7]) * 100) if row[7] and row[7] > 0 else 0
                })

            result = {
                'keywords': keywords,
                'total': len(keywords),
                'status': 'success'
            }

            self._set_cache(cache_key, result)
            logger.info(f"Fetched {len(keywords)} keywords from database")
            return result

        except Exception as e:
            logger.error(f"Error fetching keywords from database: {str(e)}")
            return {'error': str(e), 'keywords': []}

    def fetch_search_terms(self, min_impressions: int = 10, limit: int = 100) -> Dict[str, Any]:
        """
        Fetch search terms from database

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

        try:
            # Query search term data (using keyword performance as proxy)
            query = """
                SELECT TOP (@limit)
                    k.KeywordText as search_term,
                    c.CampaignName as campaign_name,
                    ag.AdGroupName as ad_group_name,
                    k.MatchType as match_type,
                    SUM(kp.Impressions) as impressions,
                    SUM(kp.Clicks) as clicks,
                    SUM(kp.Cost) as cost,
                    SUM(kp.Conversions) as conversions,
                    AVG(kp.CTR) * 100 as ctr,
                    AVG(kp.CPC) as avg_cpc
                FROM dw.FactKeywordPerformance kp
                JOIN dw.DimKeyword k ON kp.KeywordKey = k.KeywordKey
                JOIN dw.DimAdGroup ag ON kp.AdGroupKey = ag.AdGroupKey
                JOIN dw.DimCampaign c ON kp.CampaignKey = c.CampaignKey
                WHERE kp.Impressions >= @min_impressions
                GROUP BY k.KeywordText, c.CampaignName, ag.AdGroupName, k.MatchType
                ORDER BY SUM(kp.Cost) DESC
            """

            params = {'limit': limit, 'min_impressions': min_impressions}
            rows = self.db.execute_query(query, params)

            search_terms = []
            for row in rows:
                search_terms.append({
                    'search_term': row[0],
                    'campaign_name': row[1],
                    'ad_group_name': row[2],
                    'match_type': row[3],
                    'impressions': int(row[4]) if row[4] else 0,
                    'clicks': int(row[5]) if row[5] else 0,
                    'cost': float(row[6]) if row[6] else 0,
                    'conversions': int(row[7]) if row[7] else 0,
                    'ctr': float(row[8]) if row[8] else 0,
                    'avg_cpc': float(row[9]) if row[9] else 0
                })

            result = {
                'search_terms': search_terms,
                'total': len(search_terms),
                'status': 'success'
            }

            self._set_cache(cache_key, result)
            logger.info(f"Fetched {len(search_terms)} search terms from database")
            return result

        except Exception as e:
            logger.error(f"Error fetching search terms from database: {str(e)}")
            return {'error': str(e), 'search_terms': []}

    def fetch_ml_features(self, entity_type: str = "campaign") -> Dict[str, Any]:
        """
        Fetch ML features from database

        Args:
            entity_type: Type of entity (campaign/keyword)

        Returns:
            ML features data
        """
        cache_key = f"ml_features_{entity_type}"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            if entity_type == "campaign":
                query = """
                    SELECT
                        c.CampaignID as campaign_id,
                        c.CampaignName as campaign_name,
                        SUM(cp.Impressions) as impressions_sum,
                        SUM(cp.Clicks) as clicks_sum,
                        SUM(cp.Cost) as cost_sum,
                        SUM(cp.Conversions) as conversions_sum,
                        SUM(cp.ConversionValue) as conversion_value_sum,
                        AVG(cp.CTR) * 100 as ctr,
                        AVG(cp.CPC) as cpc,
                        AVG(cp.ROAS) as roas,
                        AVG(cp.ConversionRate) * 100 as conversion_rate,
                        COUNT(DISTINCT cp.DateKey) as days_active,
                        STDEV(cp.Cost) as cost_std,
                        STDEV(cp.Clicks) as clicks_std
                    FROM dw.DimCampaign c
                    LEFT JOIN dw.FactCampaignPerformance cp ON c.CampaignKey = cp.CampaignKey
                    GROUP BY c.CampaignID, c.CampaignName
                    HAVING SUM(cp.Impressions) > 1000
                """
                rows = self.db.execute_query(query)

            elif entity_type == "keyword":
                query = """
                    SELECT
                        k.KeywordID as keyword_id,
                        k.KeywordText as keyword_text,
                        k.MatchType as match_type,
                        AVG(kp.QualityScore) as quality_score,
                        SUM(kp.Impressions) as impressions_sum,
                        SUM(kp.Clicks) as clicks_sum,
                        SUM(kp.Cost) as cost_sum,
                        SUM(kp.Conversions) as conversions_sum,
                        AVG(kp.CTR) * 100 as ctr,
                        AVG(kp.CPC) as cpc,
                        AVG(kp.AvgPosition) as avg_position,
                        LEN(k.KeywordText) - LEN(REPLACE(k.KeywordText, ' ', '')) + 1 as keyword_length
                    FROM dw.DimKeyword k
                    LEFT JOIN dw.FactKeywordPerformance kp ON k.KeywordKey = kp.KeywordKey
                    GROUP BY k.KeywordID, k.KeywordText, k.MatchType
                    HAVING SUM(kp.Impressions) > 100
                """
                rows = self.db.execute_query(query)
            else:
                return {'error': f'Unsupported entity type: {entity_type}', 'features': []}

            features = []
            for row in rows:
                if entity_type == "campaign":
                    features.append({
                        'campaign_id': row[0],
                        'campaign_name': row[1],
                        'impressions_sum': float(row[2]) if row[2] else 0,
                        'clicks_sum': float(row[3]) if row[3] else 0,
                        'cost_sum': float(row[4]) if row[4] else 0,
                        'conversions_sum': float(row[5]) if row[5] else 0,
                        'conversion_value_sum': float(row[6]) if row[6] else 0,
                        'ctr': float(row[7]) if row[7] else 0,
                        'cpc': float(row[8]) if row[8] else 0,
                        'roas': float(row[9]) if row[9] else 0,
                        'conversion_rate': float(row[10]) if row[10] else 0,
                        'days_active': int(row[11]) if row[11] else 0,
                        'cost_std': float(row[12]) if row[12] else 0,
                        'clicks_std': float(row[13]) if row[13] else 0
                    })
                else:  # keyword
                    features.append({
                        'keyword_id': row[0],
                        'keyword_text': row[1],
                        'match_type': row[2],
                        'quality_score': float(row[3]) if row[3] else 5,
                        'impressions_sum': float(row[4]) if row[4] else 0,
                        'clicks_sum': float(row[5]) if row[5] else 0,
                        'cost_sum': float(row[6]) if row[6] else 0,
                        'conversions_sum': float(row[7]) if row[7] else 0,
                        'ctr': float(row[8]) if row[8] else 0,
                        'cpc': float(row[9]) if row[9] else 0,
                        'avg_position': float(row[10]) if row[10] else 0,
                        'keyword_length': int(row[11]) if row[11] else 1
                    })

            result = {
                'features': features,
                'entity_type': entity_type,
                'total': len(features),
                'status': 'success'
            }

            self._set_cache(cache_key, result)
            logger.info(f"Fetched {len(features)} ML features for {entity_type}")
            return result

        except Exception as e:
            logger.error(f"Error fetching ML features from database: {str(e)}")
            return {'error': str(e), 'features': []}

    def fetch_metrics_summary(self) -> Dict[str, Any]:
        """
        Fetch overall metrics summary

        Returns:
            Metrics summary
        """
        cache_key = "metrics_summary"
        cached = self._get_cached(cache_key)
        if cached:
            return cached

        try:
            query = """
                SELECT
                    COUNT(DISTINCT c.CampaignID) as total_campaigns,
                    COUNT(DISTINCT ag.AdGroupID) as total_ad_groups,
                    COUNT(DISTINCT k.KeywordID) as total_keywords,
                    SUM(cp.Impressions) as total_impressions,
                    SUM(cp.Clicks) as total_clicks,
                    SUM(cp.Cost) as total_cost,
                    SUM(cp.Conversions) as total_conversions,
                    SUM(cp.ConversionValue) as total_conversion_value,
                    AVG(cp.CTR) * 100 as avg_ctr,
                    AVG(cp.CPC) as avg_cpc,
                    AVG(cp.ConversionRate) * 100 as avg_conversion_rate,
                    AVG(cp.ROAS) as avg_roas
                FROM dw.FactCampaignPerformance cp
                JOIN dw.DimCampaign c ON cp.CampaignKey = c.CampaignKey
                JOIN dw.DimDate d ON cp.DateKey = d.DateKey
                LEFT JOIN dw.FactAdGroupPerformance agp ON agp.CampaignKey = c.CampaignKey
                LEFT JOIN dw.DimAdGroup ag ON agp.AdGroupKey = ag.AdGroupKey
                LEFT JOIN dw.FactKeywordPerformance kp ON kp.CampaignKey = c.CampaignKey
                LEFT JOIN dw.DimKeyword k ON kp.KeywordKey = k.KeywordKey
                WHERE d.Date >= DATEADD(day, -30, GETDATE())
            """

            rows = self.db.execute_query(query)

            if rows and len(rows) > 0:
                row = rows[0]
                summary = {
                    'total_campaigns': int(row[0]) if row[0] else 0,
                    'total_ad_groups': int(row[1]) if row[1] else 0,
                    'total_keywords': int(row[2]) if row[2] else 0,
                    'total_impressions': int(row[3]) if row[3] else 0,
                    'total_clicks': int(row[4]) if row[4] else 0,
                    'total_cost': float(row[5]) if row[5] else 0,
                    'total_conversions': int(row[6]) if row[6] else 0,
                    'total_conversion_value': float(row[7]) if row[7] else 0,
                    'avg_ctr': float(row[8]) if row[8] else 0,
                    'avg_cpc': float(row[9]) if row[9] else 0,
                    'avg_conversion_rate': float(row[10]) if row[10] else 0,
                    'avg_roas': float(row[11]) if row[11] else 0,
                    'period': 'Last 30 days'
                }
            else:
                summary = {}

            result = {
                'summary': summary,
                'status': 'success',
                'generated_at': datetime.now().isoformat()
            }

            self._set_cache(cache_key, result)
            logger.info("Fetched metrics summary from database")
            return result

        except Exception as e:
            logger.error(f"Error fetching metrics summary: {str(e)}")
            return {'error': str(e), 'summary': {}}

    def clear_cache(self):
        """Clear all cached data"""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Database cache cleared")