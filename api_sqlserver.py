#!/usr/bin/env python3
"""
FastAPI REST API for Marketing Data Warehouse (SQL Server)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import pandas as pd
from loguru import logger
from db_connection import db

app = FastAPI(
    title="MarketingIQ API",
    description="REST API for Google Ads Data Warehouse",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response Models
class CampaignResponse(BaseModel):
    campaign_id: int
    campaign_name: str
    status: str
    campaign_type: str
    budget_amount: float
    bidding_strategy: str
    impressions: Optional[int] = 0
    clicks: Optional[int] = 0
    cost: Optional[float] = 0.0
    conversions: Optional[int] = 0
    ctr: Optional[float] = 0.0
    cpc: Optional[float] = 0.0
    roas: Optional[float] = 0.0

class AdGroupResponse(BaseModel):
    ad_group_id: int
    ad_group_name: str
    campaign_id: int
    campaign_name: Optional[str]
    status: str
    impressions: Optional[int] = 0
    clicks: Optional[int] = 0
    cost: Optional[float] = 0.0
    conversions: Optional[int] = 0
    ctr: Optional[float] = 0.0

class KeywordResponse(BaseModel):
    keyword_id: str
    keyword: str
    ad_group_id: int
    match_type: str
    status: str
    quality_score: Optional[int]
    impressions: Optional[int] = 0
    clicks: Optional[int] = 0
    cost: Optional[float] = 0.0
    ctr: Optional[float] = 0.0
    avg_position: Optional[float]

class PerformanceMetrics(BaseModel):
    date: str
    impressions: int
    clicks: int
    cost: float
    conversions: int
    conversion_value: float
    ctr: float
    cpc: float
    conversion_rate: float
    roas: float

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "message": "MarketingIQ API - SQL Server Edition",
        "version": "2.2.0",
        "endpoints": {
            "campaigns": [
                "/campaigns - List all campaigns with performance metrics",
                "/campaigns/{campaign_id} - Get specific campaign details",
                "/campaigns/{campaign_id}/performance - Time-series performance data",
                "/campaigns/{campaign_id}/ads - Get ads for a campaign",
                "/campaigns/top-performers - Top campaigns by metric (roas/conversions/ctr)"
            ],
            "ad_groups": [
                "/ad-groups - List ad groups with filtering",
                "/ad-groups/{ad_group_id} - Get specific ad group details",
                "/ad-groups/{ad_group_id}/ads - Get ads for an ad group"
            ],
            "ads": [
                "/ads - List all ads with creative content and performance",
                "/campaigns/{campaign_id}/ads - Ads within a specific campaign",
                "/ad-groups/{ad_group_id}/ads - Ads within a specific ad group"
            ],
            "keywords": [
                "/keywords - List keywords with quality scores",
                "/keywords/underperformers - Keywords wasting budget without conversions"
            ],
            "search_terms": [
                "/search-terms - Actual search queries triggering ads",
                "/search-terms/negative - Suggested negative keywords to reduce waste"
            ],
            "aggregated_metrics": [
                "/metrics/by-campaign - Metrics grouped by campaign",
                "/metrics/by-ad-group - Metrics grouped by ad group",
                "/metrics/by-keyword - Metrics grouped by keyword",
                "/metrics/by-day-of-week - Performance by day of week"
            ],
            "analytics": [
                "/metrics/summary - Overall performance summary",
                "/metrics/trends - Trending metrics over time",
                "/metrics/compare - Compare two time periods"
            ],
            "system": [
                "/health - Database connection health check",
                "/ - API documentation"
            ]
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        if db.test_connection():
            return {"status": "healthy", "database": "connected"}
        else:
            raise HTTPException(status_code=503, detail="Database connection failed")
    except Exception as e:
        raise HTTPException(status_code=503, detail=str(e))

@app.get("/campaigns", response_model=List[CampaignResponse])
async def get_campaigns(
    status: Optional[str] = None,
    limit: int = Query(100, le=1000)
):
    """Get all campaigns with optional filtering"""
    try:
        query = """
            SELECT TOP (@limit)
                c.CampaignID as campaign_id,
                c.CampaignName as campaign_name,
                c.CampaignStatus as status,
                c.CampaignType as campaign_type,
                c.BudgetAmount as budget_amount,
                c.BiddingStrategy as bidding_strategy,
                SUM(f.Impressions) as impressions,
                SUM(f.Clicks) as clicks,
                SUM(f.Cost) as cost,
                SUM(f.Conversions) as conversions,
                AVG(f.CTR) as ctr,
                AVG(f.CPC) as cpc,
                AVG(f.ROAS) as roas
            FROM dw.DimCampaign c
            LEFT JOIN dw.FactCampaignPerformance f ON c.CampaignKey = f.CampaignKey
            WHERE (@status IS NULL OR c.CampaignStatus = @status)
            GROUP BY c.CampaignID, c.CampaignName, c.CampaignStatus,
                     c.CampaignType, c.BudgetAmount, c.BiddingStrategy
            ORDER BY SUM(f.Cost) DESC
        """

        params = {"limit": limit, "status": status}
        results = db.execute_query(query, params)

        campaigns = []
        for row in results:
            campaigns.append({
                "campaign_id": row[0],
                "campaign_name": row[1],
                "status": row[2],
                "campaign_type": row[3],
                "budget_amount": row[4] or 0,
                "bidding_strategy": row[5],
                "impressions": row[6] or 0,
                "clicks": row[7] or 0,
                "cost": row[8] or 0,
                "conversions": row[9] or 0,
                "ctr": row[10] or 0,
                "cpc": row[11] or 0,
                "roas": row[12] or 0
            })

        return campaigns

    except Exception as e:
        logger.error(f"Error fetching campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns/{campaign_id}")
async def get_campaign(campaign_id: int):
    """Get specific campaign details"""
    try:
        query = """
            SELECT
                c.CampaignID,
                c.CampaignName,
                c.CampaignStatus,
                c.CampaignType,
                c.AdvertisingChannelType,
                c.StartDate,
                c.EndDate,
                c.BudgetAmount,
                c.BiddingStrategy,
                c.TargetCPA,
                c.TargetROAS,
                SUM(f.Impressions) as total_impressions,
                SUM(f.Clicks) as total_clicks,
                SUM(f.Cost) as total_cost,
                SUM(f.Conversions) as total_conversions,
                SUM(f.ConversionValue) as total_conversion_value
            FROM dw.DimCampaign c
            LEFT JOIN dw.FactCampaignPerformance f ON c.CampaignKey = f.CampaignKey
            WHERE c.CampaignID = @campaign_id
            GROUP BY c.CampaignID, c.CampaignName, c.CampaignStatus, c.CampaignType,
                     c.AdvertisingChannelType, c.StartDate, c.EndDate, c.BudgetAmount,
                     c.BiddingStrategy, c.TargetCPA, c.TargetROAS
        """

        results = db.execute_query(query, {"campaign_id": campaign_id})

        if not results:
            raise HTTPException(status_code=404, detail="Campaign not found")

        row = results[0]
        return {
            "campaign_id": row[0],
            "campaign_name": row[1],
            "status": row[2],
            "campaign_type": row[3],
            "advertising_channel_type": row[4],
            "start_date": row[5],
            "end_date": row[6],
            "budget_amount": row[7] or 0,
            "bidding_strategy": row[8],
            "target_cpa": row[9],
            "target_roas": row[10],
            "total_impressions": row[11] or 0,
            "total_clicks": row[12] or 0,
            "total_cost": row[13] or 0,
            "total_conversions": row[14] or 0,
            "total_conversion_value": row[15] or 0
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching campaign {campaign_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns/{campaign_id}/performance")
async def get_campaign_performance(
    campaign_id: int,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get campaign performance metrics over time"""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        query = """
            SELECT
                d.Date,
                f.Impressions,
                f.Clicks,
                f.Cost,
                f.Conversions,
                f.ConversionValue,
                f.CTR,
                f.CPC,
                f.ConversionRate,
                f.ROAS
            FROM dw.FactCampaignPerformance f
            JOIN dw.DimDate d ON f.DateKey = d.DateKey
            JOIN dw.DimCampaign c ON f.CampaignKey = c.CampaignKey
            WHERE c.CampaignID = @campaign_id
                AND d.Date BETWEEN @start_date AND @end_date
            ORDER BY d.Date
        """

        params = {
            "campaign_id": campaign_id,
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }

        results = db.execute_query(query, params)

        performance = []
        for row in results:
            performance.append({
                "date": row[0].strftime('%Y-%m-%d'),
                "impressions": row[1] or 0,
                "clicks": row[2] or 0,
                "cost": row[3] or 0,
                "conversions": row[4] or 0,
                "conversion_value": row[5] or 0,
                "ctr": row[6] or 0,
                "cpc": row[7] or 0,
                "conversion_rate": row[8] or 0,
                "roas": row[9] or 0
            })

        return performance

    except Exception as e:
        logger.error(f"Error fetching campaign performance: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ad-groups", response_model=List[AdGroupResponse])
async def get_ad_groups(
    campaign_id: Optional[int] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=1000)
):
    """Get ad groups with optional filtering"""
    try:
        query = """
            SELECT TOP (@limit)
                a.AdGroupID as ad_group_id,
                a.AdGroupName as ad_group_name,
                a.CampaignID as campaign_id,
                c.CampaignName as campaign_name,
                a.AdGroupStatus as status,
                SUM(f.Impressions) as impressions,
                SUM(f.Clicks) as clicks,
                SUM(f.Cost) as cost,
                SUM(f.Conversions) as conversions,
                AVG(f.CTR) as ctr
            FROM dw.DimAdGroup a
            LEFT JOIN dw.DimCampaign c ON a.CampaignID = c.CampaignID
            LEFT JOIN dw.FactAdGroupPerformance f ON a.AdGroupKey = f.AdGroupKey
            WHERE (@campaign_id IS NULL OR a.CampaignID = @campaign_id)
                AND (@status IS NULL OR a.AdGroupStatus = @status)
            GROUP BY a.AdGroupID, a.AdGroupName, a.CampaignID, c.CampaignName, a.AdGroupStatus
            ORDER BY SUM(f.Cost) DESC
        """

        params = {"limit": limit, "campaign_id": campaign_id, "status": status}
        results = db.execute_query(query, params)

        ad_groups = []
        for row in results:
            ad_groups.append({
                "ad_group_id": row[0],
                "ad_group_name": row[1],
                "campaign_id": row[2],
                "campaign_name": row[3],
                "status": row[4],
                "impressions": row[5] or 0,
                "clicks": row[6] or 0,
                "cost": row[7] or 0,
                "conversions": row[8] or 0,
                "ctr": row[9] or 0
            })

        return ad_groups

    except Exception as e:
        logger.error(f"Error fetching ad groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/keywords", response_model=List[KeywordResponse])
async def get_keywords(
    ad_group_id: Optional[int] = None,
    match_type: Optional[str] = None,
    min_quality_score: Optional[int] = None,
    limit: int = Query(100, le=1000)
):
    """Get keywords with optional filtering"""
    try:
        query = """
            SELECT TOP (@limit)
                k.KeywordID as keyword_id,
                k.Keyword as keyword,
                k.AdGroupID as ad_group_id,
                k.MatchType as match_type,
                k.Status as status,
                k.QualityScore as quality_score,
                SUM(f.Impressions) as impressions,
                SUM(f.Clicks) as clicks,
                SUM(f.Cost) as cost,
                AVG(f.CTR) as ctr,
                AVG(f.AvgPosition) as avg_position
            FROM dw.DimKeyword k
            LEFT JOIN dw.FactKeywordPerformance f ON k.KeywordKey = f.KeywordKey
            WHERE (@ad_group_id IS NULL OR k.AdGroupID = @ad_group_id)
                AND (@match_type IS NULL OR k.MatchType = @match_type)
                AND (@min_quality_score IS NULL OR k.QualityScore >= @min_quality_score)
            GROUP BY k.KeywordID, k.Keyword, k.AdGroupID, k.MatchType, k.Status, k.QualityScore
            ORDER BY SUM(f.Impressions) DESC
        """

        params = {
            "limit": limit,
            "ad_group_id": ad_group_id,
            "match_type": match_type,
            "min_quality_score": min_quality_score
        }
        results = db.execute_query(query, params)

        keywords = []
        for row in results:
            keywords.append({
                "keyword_id": row[0],
                "keyword": row[1],
                "ad_group_id": row[2],
                "match_type": row[3],
                "status": row[4],
                "quality_score": row[5],
                "impressions": row[6] or 0,
                "clicks": row[7] or 0,
                "cost": row[8] or 0,
                "ctr": row[9] or 0,
                "avg_position": row[10]
            })

        return keywords

    except Exception as e:
        logger.error(f"Error fetching keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/summary")
async def get_metrics_summary(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get overall performance metrics summary"""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        query = """
            SELECT
                SUM(f.Impressions) as total_impressions,
                SUM(f.Clicks) as total_clicks,
                SUM(f.Cost) as total_cost,
                SUM(f.Conversions) as total_conversions,
                SUM(f.ConversionValue) as total_conversion_value,
                AVG(f.CTR) as avg_ctr,
                AVG(f.CPC) as avg_cpc,
                AVG(f.ConversionRate) as avg_conversion_rate,
                AVG(f.ROAS) as avg_roas,
                COUNT(DISTINCT f.CampaignKey) as active_campaigns
            FROM dw.FactCampaignPerformance f
            JOIN dw.DimDate d ON f.DateKey = d.DateKey
            WHERE d.Date BETWEEN @start_date AND @end_date
        """

        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }

        results = db.execute_query(query, params)

        if results:
            row = results[0]
            return {
                "period": {
                    "start_date": start_date.strftime('%Y-%m-%d'),
                    "end_date": end_date.strftime('%Y-%m-%d')
                },
                "metrics": {
                    "total_impressions": row[0] or 0,
                    "total_clicks": row[1] or 0,
                    "total_cost": row[2] or 0,
                    "total_conversions": row[3] or 0,
                    "total_conversion_value": row[4] or 0,
                    "avg_ctr": row[5] or 0,
                    "avg_cpc": row[6] or 0,
                    "avg_conversion_rate": row[7] or 0,
                    "avg_roas": row[8] or 0,
                    "active_campaigns": row[9] or 0
                }
            }

        return {"metrics": {}}

    except Exception as e:
        logger.error(f"Error fetching metrics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/trends")
async def get_metrics_trends(
    metric: str = Query("impressions", regex="^(impressions|clicks|cost|conversions|ctr|cpc|roas)$"),
    granularity: str = Query("daily", regex="^(daily|weekly|monthly)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get trending metrics over time"""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        # Determine grouping based on granularity
        if granularity == "weekly":
            date_group = "DATEPART(YEAR, d.Date), DATEPART(WEEK, d.Date)"
            date_select = "CONCAT(YEAR(MIN(d.Date)), '-W', DATEPART(WEEK, MIN(d.Date)))"
        elif granularity == "monthly":
            date_group = "YEAR(d.Date), MONTH(d.Date)"
            date_select = "FORMAT(MIN(d.Date), 'yyyy-MM')"
        else:
            date_group = "d.Date"
            date_select = "d.Date"

        # Map metric to SQL aggregation
        metric_map = {
            "impressions": "SUM(f.Impressions)",
            "clicks": "SUM(f.Clicks)",
            "cost": "SUM(f.Cost)",
            "conversions": "SUM(f.Conversions)",
            "ctr": "AVG(f.CTR)",
            "cpc": "AVG(f.CPC)",
            "roas": "AVG(f.ROAS)"
        }

        query = f"""
            SELECT
                {date_select} as period,
                {metric_map[metric]} as value
            FROM dw.FactCampaignPerformance f
            JOIN dw.DimDate d ON f.DateKey = d.DateKey
            WHERE d.Date BETWEEN @start_date AND @end_date
            GROUP BY {date_group}
            ORDER BY MIN(d.Date)
        """

        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }

        results = db.execute_query(query, params)

        trends = []
        for row in results:
            trends.append({
                "period": str(row[0]),
                "value": row[1] or 0
            })

        return {
            "metric": metric,
            "granularity": granularity,
            "data": trends
        }

    except Exception as e:
        logger.error(f"Error fetching metrics trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/by-campaign")
async def get_metrics_by_campaign(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(20, le=100)
):
    """Get aggregated metrics grouped by campaign"""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        query = """
            SELECT TOP (@limit)
                c.CampaignID,
                c.CampaignName,
                c.CampaignStatus,
                c.BudgetAmount,
                SUM(f.Impressions) as total_impressions,
                SUM(f.Clicks) as total_clicks,
                SUM(f.Cost) as total_cost,
                SUM(f.Conversions) as total_conversions,
                SUM(f.ConversionValue) as total_conversion_value,
                CASE WHEN SUM(f.Impressions) > 0
                     THEN CAST(SUM(f.Clicks) AS FLOAT) / SUM(f.Impressions) * 100
                     ELSE 0 END as ctr,
                CASE WHEN SUM(f.Clicks) > 0
                     THEN SUM(f.Cost) / SUM(f.Clicks)
                     ELSE 0 END as avg_cpc,
                CASE WHEN SUM(f.Clicks) > 0
                     THEN CAST(SUM(f.Conversions) AS FLOAT) / SUM(f.Clicks) * 100
                     ELSE 0 END as conversion_rate,
                CASE WHEN SUM(f.Cost) > 0
                     THEN SUM(f.ConversionValue) / SUM(f.Cost)
                     ELSE 0 END as roas
            FROM dw.DimCampaign c
            JOIN dw.FactCampaignPerformance f ON c.CampaignKey = f.CampaignKey
            JOIN dw.DimDate d ON f.DateKey = d.DateKey
            WHERE d.Date BETWEEN @start_date AND @end_date
            GROUP BY c.CampaignID, c.CampaignName, c.CampaignStatus, c.BudgetAmount
            ORDER BY SUM(f.Cost) DESC
        """

        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "limit": limit
        }

        results = db.execute_query(query, params)

        campaigns = []
        for row in results:
            campaigns.append({
                "campaign_id": row[0],
                "campaign_name": row[1],
                "status": row[2],
                "budget": row[3] or 0,
                "impressions": row[4] or 0,
                "clicks": row[5] or 0,
                "cost": row[6] or 0,
                "conversions": row[7] or 0,
                "conversion_value": row[8] or 0,
                "ctr": round(row[9], 2),
                "avg_cpc": round(row[10], 2) if row[10] else 0,
                "conversion_rate": round(row[11], 2),
                "roas": round(row[12], 2) if row[12] else 0
            })

        return {
            "period": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d')
            },
            "campaigns": campaigns,
            "total_campaigns": len(campaigns)
        }

    except Exception as e:
        logger.error(f"Error fetching metrics by campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/by-ad-group")
async def get_metrics_by_ad_group(
    campaign_id: Optional[int] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(50, le=200)
):
    """Get aggregated metrics grouped by ad group"""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        query = """
            SELECT TOP (@limit)
                a.AdGroupID,
                a.AdGroupName,
                c.CampaignID,
                c.CampaignName,
                a.AdGroupStatus,
                SUM(f.Impressions) as total_impressions,
                SUM(f.Clicks) as total_clicks,
                SUM(f.Cost) as total_cost,
                SUM(f.Conversions) as total_conversions,
                CASE WHEN SUM(f.Impressions) > 0
                     THEN CAST(SUM(f.Clicks) AS FLOAT) / SUM(f.Impressions) * 100
                     ELSE 0 END as ctr,
                CASE WHEN SUM(f.Clicks) > 0
                     THEN SUM(f.Cost) / SUM(f.Clicks)
                     ELSE 0 END as avg_cpc
            FROM dw.DimAdGroup a
            JOIN dw.DimCampaign c ON a.CampaignID = c.CampaignID
            JOIN dw.FactAdGroupPerformance f ON a.AdGroupKey = f.AdGroupKey
            JOIN dw.DimDate d ON f.DateKey = d.DateKey
            WHERE d.Date BETWEEN @start_date AND @end_date
                AND (@campaign_id IS NULL OR c.CampaignID = @campaign_id)
            GROUP BY a.AdGroupID, a.AdGroupName, c.CampaignID, c.CampaignName, a.AdGroupStatus
            ORDER BY SUM(f.Cost) DESC
        """

        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "campaign_id": campaign_id,
            "limit": limit
        }

        results = db.execute_query(query, params)

        ad_groups = []
        for row in results:
            ad_groups.append({
                "ad_group_id": row[0],
                "ad_group_name": row[1],
                "campaign_id": row[2],
                "campaign_name": row[3],
                "status": row[4],
                "impressions": row[5] or 0,
                "clicks": row[6] or 0,
                "cost": row[7] or 0,
                "conversions": row[8] or 0,
                "ctr": round(row[9], 2),
                "avg_cpc": round(row[10], 2) if row[10] else 0
            })

        return {
            "period": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d')
            },
            "ad_groups": ad_groups,
            "total_ad_groups": len(ad_groups)
        }

    except Exception as e:
        logger.error(f"Error fetching metrics by ad group: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/by-keyword")
async def get_metrics_by_keyword(
    ad_group_id: Optional[int] = None,
    min_impressions: int = Query(0, ge=0),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(100, le=500)
):
    """Get aggregated metrics grouped by keyword"""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        query = """
            SELECT TOP (@limit)
                k.KeywordID,
                k.Keyword,
                k.MatchType,
                k.QualityScore,
                a.AdGroupID,
                a.AdGroupName,
                SUM(f.Impressions) as total_impressions,
                SUM(f.Clicks) as total_clicks,
                SUM(f.Cost) as total_cost,
                SUM(f.Conversions) as total_conversions,
                CASE WHEN SUM(f.Impressions) > 0
                     THEN CAST(SUM(f.Clicks) AS FLOAT) / SUM(f.Impressions) * 100
                     ELSE 0 END as ctr,
                CASE WHEN SUM(f.Clicks) > 0
                     THEN SUM(f.Cost) / SUM(f.Clicks)
                     ELSE 0 END as avg_cpc,
                AVG(f.AvgPosition) as avg_position
            FROM dw.DimKeyword k
            JOIN dw.DimAdGroup a ON k.AdGroupID = a.AdGroupID
            JOIN dw.FactKeywordPerformance f ON k.KeywordKey = f.KeywordKey
            JOIN dw.DimDate d ON f.DateKey = d.DateKey
            WHERE d.Date BETWEEN @start_date AND @end_date
                AND (@ad_group_id IS NULL OR a.AdGroupID = @ad_group_id)
            GROUP BY k.KeywordID, k.Keyword, k.MatchType, k.QualityScore,
                     a.AdGroupID, a.AdGroupName
            HAVING SUM(f.Impressions) >= @min_impressions
            ORDER BY SUM(f.Cost) DESC
        """

        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "ad_group_id": ad_group_id,
            "min_impressions": min_impressions,
            "limit": limit
        }

        results = db.execute_query(query, params)

        keywords = []
        for row in results:
            keywords.append({
                "keyword_id": row[0],
                "keyword": row[1],
                "match_type": row[2],
                "quality_score": row[3],
                "ad_group_id": row[4],
                "ad_group_name": row[5],
                "impressions": row[6] or 0,
                "clicks": row[7] or 0,
                "cost": row[8] or 0,
                "conversions": row[9] or 0,
                "ctr": round(row[10], 2),
                "avg_cpc": round(row[11], 2) if row[11] else 0,
                "avg_position": round(row[12], 1) if row[12] else None
            })

        return {
            "period": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d')
            },
            "keywords": keywords,
            "total_keywords": len(keywords)
        }

    except Exception as e:
        logger.error(f"Error fetching metrics by keyword: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/by-day-of-week")
async def get_metrics_by_day_of_week(
    start_date: Optional[date] = None,
    end_date: Optional[date] = None
):
    """Get performance metrics grouped by day of week"""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        query = """
            SELECT
                DATENAME(WEEKDAY, d.Date) as day_name,
                DATEPART(WEEKDAY, d.Date) as day_number,
                COUNT(DISTINCT d.Date) as days_count,
                SUM(f.Impressions) as total_impressions,
                SUM(f.Clicks) as total_clicks,
                SUM(f.Cost) as total_cost,
                SUM(f.Conversions) as total_conversions,
                AVG(f.CTR) as avg_ctr,
                AVG(f.CPC) as avg_cpc,
                AVG(f.ConversionRate) as avg_conversion_rate
            FROM dw.FactCampaignPerformance f
            JOIN dw.DimDate d ON f.DateKey = d.DateKey
            WHERE d.Date BETWEEN @start_date AND @end_date
            GROUP BY DATENAME(WEEKDAY, d.Date), DATEPART(WEEKDAY, d.Date)
            ORDER BY DATEPART(WEEKDAY, d.Date)
        """

        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d')
        }

        results = db.execute_query(query, params)

        weekday_metrics = []
        for row in results:
            weekday_metrics.append({
                "day_of_week": row[0],
                "day_number": row[1],
                "days_analyzed": row[2],
                "total_impressions": row[3] or 0,
                "total_clicks": row[4] or 0,
                "total_cost": row[5] or 0,
                "total_conversions": row[6] or 0,
                "avg_ctr": round(row[7], 2) if row[7] else 0,
                "avg_cpc": round(row[8], 2) if row[8] else 0,
                "avg_conversion_rate": round(row[9], 2) if row[9] else 0,
                "avg_daily_cost": round(row[5] / row[2], 2) if row[2] > 0 else 0
            })

        return {
            "period": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d')
            },
            "weekday_performance": weekday_metrics
        }

    except Exception as e:
        logger.error(f"Error fetching metrics by day of week: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/compare")
async def compare_metrics(
    period1_start: date = Query(..., description="Start date for period 1"),
    period1_end: date = Query(..., description="End date for period 1"),
    period2_start: date = Query(..., description="Start date for period 2"),
    period2_end: date = Query(..., description="End date for period 2")
):
    """Compare metrics between two time periods"""
    try:
        query = """
            SELECT
                @period_label as period,
                SUM(f.Impressions) as impressions,
                SUM(f.Clicks) as clicks,
                SUM(f.Cost) as cost,
                SUM(f.Conversions) as conversions,
                SUM(f.ConversionValue) as conversion_value,
                AVG(f.CTR) as avg_ctr,
                AVG(f.CPC) as avg_cpc,
                AVG(f.ConversionRate) as avg_conversion_rate,
                AVG(f.ROAS) as avg_roas,
                COUNT(DISTINCT f.CampaignKey) as active_campaigns
            FROM dw.FactCampaignPerformance f
            JOIN dw.DimDate d ON f.DateKey = d.DateKey
            WHERE d.Date BETWEEN @start_date AND @end_date
        """

        # Get period 1 metrics
        params1 = {
            "period_label": "period1",
            "start_date": period1_start.strftime('%Y-%m-%d'),
            "end_date": period1_end.strftime('%Y-%m-%d')
        }
        results1 = db.execute_query(query, params1)

        # Get period 2 metrics
        params2 = {
            "period_label": "period2",
            "start_date": period2_start.strftime('%Y-%m-%d'),
            "end_date": period2_end.strftime('%Y-%m-%d')
        }
        results2 = db.execute_query(query, params2)

        if results1 and results2:
            row1 = results1[0]
            row2 = results2[0]

            def calculate_change(new_val, old_val):
                if old_val and old_val != 0:
                    return round(((new_val - old_val) / old_val) * 100, 2)
                return None

            period1_metrics = {
                "impressions": row1[1] or 0,
                "clicks": row1[2] or 0,
                "cost": row1[3] or 0,
                "conversions": row1[4] or 0,
                "conversion_value": row1[5] or 0,
                "avg_ctr": round(row1[6], 2) if row1[6] else 0,
                "avg_cpc": round(row1[7], 2) if row1[7] else 0,
                "avg_conversion_rate": round(row1[8], 2) if row1[8] else 0,
                "avg_roas": round(row1[9], 2) if row1[9] else 0,
                "active_campaigns": row1[10] or 0
            }

            period2_metrics = {
                "impressions": row2[1] or 0,
                "clicks": row2[2] or 0,
                "cost": row2[3] or 0,
                "conversions": row2[4] or 0,
                "conversion_value": row2[5] or 0,
                "avg_ctr": round(row2[6], 2) if row2[6] else 0,
                "avg_cpc": round(row2[7], 2) if row2[7] else 0,
                "avg_conversion_rate": round(row2[8], 2) if row2[8] else 0,
                "avg_roas": round(row2[9], 2) if row2[9] else 0,
                "active_campaigns": row2[10] or 0
            }

            changes = {
                "impressions_change": calculate_change(period2_metrics["impressions"], period1_metrics["impressions"]),
                "clicks_change": calculate_change(period2_metrics["clicks"], period1_metrics["clicks"]),
                "cost_change": calculate_change(period2_metrics["cost"], period1_metrics["cost"]),
                "conversions_change": calculate_change(period2_metrics["conversions"], period1_metrics["conversions"]),
                "conversion_value_change": calculate_change(period2_metrics["conversion_value"], period1_metrics["conversion_value"]),
                "ctr_change": calculate_change(period2_metrics["avg_ctr"], period1_metrics["avg_ctr"]),
                "cpc_change": calculate_change(period2_metrics["avg_cpc"], period1_metrics["avg_cpc"]),
                "conversion_rate_change": calculate_change(period2_metrics["avg_conversion_rate"], period1_metrics["avg_conversion_rate"]),
                "roas_change": calculate_change(period2_metrics["avg_roas"], period1_metrics["avg_roas"])
            }

            return {
                "period1": {
                    "date_range": f"{period1_start} to {period1_end}",
                    "metrics": period1_metrics
                },
                "period2": {
                    "date_range": f"{period2_start} to {period2_end}",
                    "metrics": period2_metrics
                },
                "changes": changes
            }

        return {"error": "No data available for comparison"}

    except Exception as e:
        logger.error(f"Error comparing metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns/top-performers")
async def get_top_performing_campaigns(
    metric: str = Query("roas", regex="^(roas|conversions|ctr|conversion_rate)$"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(10, le=50)
):
    """Get top performing campaigns by specified metric"""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        order_by_map = {
            "roas": "CASE WHEN SUM(f.Cost) > 0 THEN SUM(f.ConversionValue) / SUM(f.Cost) ELSE 0 END",
            "conversions": "SUM(f.Conversions)",
            "ctr": "CASE WHEN SUM(f.Impressions) > 0 THEN CAST(SUM(f.Clicks) AS FLOAT) / SUM(f.Impressions) * 100 ELSE 0 END",
            "conversion_rate": "CASE WHEN SUM(f.Clicks) > 0 THEN CAST(SUM(f.Conversions) AS FLOAT) / SUM(f.Clicks) * 100 ELSE 0 END"
        }

        query = f"""
            SELECT TOP (@limit)
                c.CampaignID,
                c.CampaignName,
                c.CampaignStatus,
                SUM(f.Impressions) as impressions,
                SUM(f.Clicks) as clicks,
                SUM(f.Cost) as cost,
                SUM(f.Conversions) as conversions,
                SUM(f.ConversionValue) as conversion_value,
                CASE WHEN SUM(f.Impressions) > 0
                     THEN CAST(SUM(f.Clicks) AS FLOAT) / SUM(f.Impressions) * 100
                     ELSE 0 END as ctr,
                CASE WHEN SUM(f.Clicks) > 0
                     THEN CAST(SUM(f.Conversions) AS FLOAT) / SUM(f.Clicks) * 100
                     ELSE 0 END as conversion_rate,
                CASE WHEN SUM(f.Cost) > 0
                     THEN SUM(f.ConversionValue) / SUM(f.Cost)
                     ELSE 0 END as roas
            FROM dw.DimCampaign c
            JOIN dw.FactCampaignPerformance f ON c.CampaignKey = f.CampaignKey
            JOIN dw.DimDate d ON f.DateKey = d.DateKey
            WHERE d.Date BETWEEN @start_date AND @end_date
                AND c.CampaignStatus = 'ENABLED'
                AND f.Impressions > 100  -- Minimum threshold for relevance
            GROUP BY c.CampaignID, c.CampaignName, c.CampaignStatus
            ORDER BY {order_by_map[metric]} DESC
        """

        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "limit": limit
        }

        results = db.execute_query(query, params)

        campaigns = []
        for row in results:
            campaigns.append({
                "campaign_id": row[0],
                "campaign_name": row[1],
                "status": row[2],
                "impressions": row[3] or 0,
                "clicks": row[4] or 0,
                "cost": row[5] or 0,
                "conversions": row[6] or 0,
                "conversion_value": row[7] or 0,
                "ctr": round(row[8], 2),
                "conversion_rate": round(row[9], 2),
                "roas": round(row[10], 2) if row[10] else 0,
                f"ranked_by": metric
            })

        return {
            "period": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d')
            },
            "metric": metric,
            "top_performers": campaigns
        }

    except Exception as e:
        logger.error(f"Error fetching top performing campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ads", response_model=List[Dict[str, Any]])
async def get_ads(
    ad_group_id: Optional[int] = None,
    campaign_id: Optional[int] = None,
    ad_type: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=500)
):
    """Get ads with performance metrics"""
    try:
        query = """
            SELECT TOP (@limit)
                a.AdID,
                a.AdType,
                a.Headlines,
                a.Descriptions,
                a.FinalURL,
                a.DisplayURL,
                a.AdGroupID,
                ag.AdGroupName,
                c.CampaignID,
                c.CampaignName,
                a.AdStatus,
                a.ApprovalStatus,
                SUM(f.Impressions) as impressions,
                SUM(f.Clicks) as clicks,
                SUM(f.Cost) as cost,
                SUM(f.Conversions) as conversions,
                SUM(f.ConversionValue) as conversion_value,
                CASE WHEN SUM(f.Impressions) > 0
                     THEN CAST(SUM(f.Clicks) AS FLOAT) / SUM(f.Impressions) * 100
                     ELSE 0 END as ctr,
                CASE WHEN SUM(f.Clicks) > 0
                     THEN SUM(f.Cost) / SUM(f.Clicks)
                     ELSE 0 END as avg_cpc
            FROM dw.DimAd a
            LEFT JOIN dw.DimAdGroup ag ON a.AdGroupID = ag.AdGroupID
            LEFT JOIN dw.DimCampaign c ON ag.CampaignID = c.CampaignID
            LEFT JOIN dw.FactAdPerformance f ON a.AdID = f.AdID
            WHERE (@ad_group_id IS NULL OR a.AdGroupID = @ad_group_id)
                AND (@campaign_id IS NULL OR c.CampaignID = @campaign_id)
                AND (@ad_type IS NULL OR a.AdType = @ad_type)
                AND (@status IS NULL OR a.AdStatus = @status)
            GROUP BY a.AdID, a.AdType, a.Headlines, a.Descriptions, a.FinalURL,
                     a.DisplayURL, a.AdGroupID, ag.AdGroupName, c.CampaignID,
                     c.CampaignName, a.AdStatus, a.ApprovalStatus
            ORDER BY SUM(f.Impressions) DESC
        """

        params = {
            "limit": limit,
            "ad_group_id": ad_group_id,
            "campaign_id": campaign_id,
            "ad_type": ad_type,
            "status": status
        }

        results = db.execute_query(query, params)

        ads = []
        for row in results:
            ads.append({
                "ad_id": row[0],
                "ad_type": row[1],
                "headlines": row[2].split(' | ') if row[2] else [],
                "descriptions": row[3].split(' | ') if row[3] else [],
                "final_url": row[4],
                "display_url": row[5],
                "ad_group_id": row[6],
                "ad_group_name": row[7],
                "campaign_id": row[8],
                "campaign_name": row[9],
                "status": row[10],
                "approval_status": row[11],
                "impressions": row[12] or 0,
                "clicks": row[13] or 0,
                "cost": row[14] or 0,
                "conversions": row[15] or 0,
                "conversion_value": row[16] or 0,
                "ctr": round(row[17], 2),
                "avg_cpc": round(row[18], 2) if row[18] else 0
            })

        return ads

    except Exception as e:
        logger.error(f"Error fetching ads: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns/{campaign_id}/ads")
async def get_campaign_ads(campaign_id: int, limit: int = Query(50, le=200)):
    """Get all ads for a specific campaign"""
    return await get_ads(campaign_id=campaign_id, limit=limit)

@app.get("/ad-groups/{ad_group_id}/ads")
async def get_ad_group_ads(ad_group_id: int, limit: int = Query(50, le=200)):
    """Get all ads for a specific ad group"""
    return await get_ads(ad_group_id=ad_group_id, limit=limit)

@app.get("/search-terms")
async def get_search_terms(
    min_impressions: int = Query(10, ge=0),
    min_cost: float = Query(0, ge=0),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(200, le=1000)
):
    """Get search terms report with performance metrics"""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        query = """
            SELECT TOP (@limit)
                st.SearchTerm,
                st.CampaignID,
                c.CampaignName,
                st.AdGroupID,
                ag.AdGroupName,
                st.TriggeringKeyword,
                st.MatchType,
                SUM(st.Impressions) as impressions,
                SUM(st.Clicks) as clicks,
                SUM(st.Cost) as cost,
                SUM(st.Conversions) as conversions,
                SUM(st.ConversionValue) as conversion_value,
                AVG(st.CTR) as ctr,
                AVG(st.AvgCPC) as avg_cpc,
                AVG(st.ConversionRate) as conversion_rate
            FROM dw.FactSearchTermPerformance st
            LEFT JOIN dw.DimCampaign c ON st.CampaignID = c.CampaignID
            LEFT JOIN dw.DimAdGroup ag ON st.AdGroupID = ag.AdGroupID
            JOIN dw.DimDate d ON st.DateKey = d.DateKey
            WHERE d.Date BETWEEN @start_date AND @end_date
            GROUP BY st.SearchTerm, st.CampaignID, c.CampaignName,
                     st.AdGroupID, ag.AdGroupName, st.TriggeringKeyword, st.MatchType
            HAVING SUM(st.Impressions) >= @min_impressions
                AND SUM(st.Cost) >= @min_cost
            ORDER BY SUM(st.Impressions) DESC
        """

        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "min_impressions": min_impressions,
            "min_cost": min_cost,
            "limit": limit
        }

        results = db.execute_query(query, params)

        search_terms = []
        for row in results:
            search_terms.append({
                "search_term": row[0],
                "campaign_id": row[1],
                "campaign_name": row[2],
                "ad_group_id": row[3],
                "ad_group_name": row[4],
                "triggering_keyword": row[5],
                "match_type": row[6],
                "impressions": row[7] or 0,
                "clicks": row[8] or 0,
                "cost": row[9] or 0,
                "conversions": row[10] or 0,
                "conversion_value": row[11] or 0,
                "ctr": round(row[12], 2) if row[12] else 0,
                "avg_cpc": round(row[13], 2) if row[13] else 0,
                "conversion_rate": round(row[14], 2) if row[14] else 0
            })

        return {
            "period": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d')
            },
            "search_terms": search_terms,
            "total_terms": len(search_terms)
        }

    except Exception as e:
        logger.error(f"Error fetching search terms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search-terms/negative")
async def get_negative_keyword_suggestions(
    min_cost: float = Query(50, description="Minimum wasted spend"),
    max_conversions: int = Query(0, description="Maximum conversions"),
    min_impressions: int = Query(100, description="Minimum impressions"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(100, le=500)
):
    """Get search terms that should be added as negative keywords"""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        query = """
            SELECT TOP (@limit)
                st.SearchTerm,
                COUNT(DISTINCT st.CampaignID) as campaign_count,
                COUNT(DISTINCT st.AdGroupID) as ad_group_count,
                SUM(st.Impressions) as total_impressions,
                SUM(st.Clicks) as total_clicks,
                SUM(st.Cost) as total_cost,
                SUM(st.Conversions) as total_conversions,
                AVG(st.CTR) as avg_ctr,
                AVG(st.AvgCPC) as avg_cpc,
                CASE WHEN SUM(st.Clicks) > 0
                     THEN CAST(SUM(st.Conversions) AS FLOAT) / SUM(st.Clicks) * 100
                     ELSE 0 END as conversion_rate
            FROM dw.FactSearchTermPerformance st
            JOIN dw.DimDate d ON st.DateKey = d.DateKey
            WHERE d.Date BETWEEN @start_date AND @end_date
                AND st.SearchTerm NOT IN (
                    SELECT DISTINCT Keyword FROM dw.DimKeyword
                )
            GROUP BY st.SearchTerm
            HAVING SUM(st.Cost) >= @min_cost
                AND SUM(st.Conversions) <= @max_conversions
                AND SUM(st.Impressions) >= @min_impressions
            ORDER BY SUM(st.Cost) DESC
        """

        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "min_cost": min_cost,
            "max_conversions": max_conversions,
            "min_impressions": min_impressions,
            "limit": limit
        }

        results = db.execute_query(query, params)

        negative_suggestions = []
        for row in results:
            negative_suggestions.append({
                "search_term": row[0],
                "appears_in_campaigns": row[1],
                "appears_in_ad_groups": row[2],
                "impressions": row[3] or 0,
                "clicks": row[4] or 0,
                "wasted_spend": row[5] or 0,
                "conversions": row[6] or 0,
                "ctr": round(row[7], 2) if row[7] else 0,
                "avg_cpc": round(row[8], 2) if row[8] else 0,
                "conversion_rate": round(row[9], 2),
                "recommendation": "Add as negative keyword"
            })

        total_wasted = sum(s["wasted_spend"] for s in negative_suggestions)

        return {
            "period": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d')
            },
            "criteria": {
                "min_cost": min_cost,
                "max_conversions": max_conversions,
                "min_impressions": min_impressions
            },
            "negative_keyword_suggestions": negative_suggestions,
            "total_suggestions": len(negative_suggestions),
            "potential_savings": round(total_wasted, 2)
        }

    except Exception as e:
        logger.error(f"Error fetching negative keyword suggestions: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/keywords/underperformers")
async def get_underperforming_keywords(
    min_cost: float = Query(100, description="Minimum cost spent"),
    max_conversions: int = Query(1, description="Maximum conversions"),
    min_impressions: int = Query(1000, description="Minimum impressions"),
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    limit: int = Query(50, le=200)
):
    """Get underperforming keywords that are spending money without results"""
    try:
        if not start_date:
            start_date = date.today() - timedelta(days=30)
        if not end_date:
            end_date = date.today()

        query = """
            SELECT TOP (@limit)
                k.KeywordID,
                k.Keyword,
                k.MatchType,
                k.QualityScore,
                a.AdGroupName,
                c.CampaignName,
                SUM(f.Impressions) as total_impressions,
                SUM(f.Clicks) as total_clicks,
                SUM(f.Cost) as total_cost,
                SUM(f.Conversions) as total_conversions,
                CASE WHEN SUM(f.Impressions) > 0
                     THEN CAST(SUM(f.Clicks) AS FLOAT) / SUM(f.Impressions) * 100
                     ELSE 0 END as ctr,
                CASE WHEN SUM(f.Clicks) > 0
                     THEN SUM(f.Cost) / SUM(f.Clicks)
                     ELSE 0 END as avg_cpc,
                AVG(f.AvgPosition) as avg_position
            FROM dw.DimKeyword k
            JOIN dw.DimAdGroup a ON k.AdGroupID = a.AdGroupID
            JOIN dw.DimCampaign c ON a.CampaignID = c.CampaignID
            JOIN dw.FactKeywordPerformance f ON k.KeywordKey = f.KeywordKey
            JOIN dw.DimDate d ON f.DateKey = d.DateKey
            WHERE d.Date BETWEEN @start_date AND @end_date
                AND k.Status = 'ENABLED'
            GROUP BY k.KeywordID, k.Keyword, k.MatchType, k.QualityScore,
                     a.AdGroupName, c.CampaignName
            HAVING SUM(f.Cost) >= @min_cost
                AND SUM(f.Conversions) <= @max_conversions
                AND SUM(f.Impressions) >= @min_impressions
            ORDER BY SUM(f.Cost) DESC
        """

        params = {
            "start_date": start_date.strftime('%Y-%m-%d'),
            "end_date": end_date.strftime('%Y-%m-%d'),
            "min_cost": min_cost,
            "max_conversions": max_conversions,
            "min_impressions": min_impressions,
            "limit": limit
        }

        results = db.execute_query(query, params)

        keywords = []
        for row in results:
            keywords.append({
                "keyword_id": row[0],
                "keyword": row[1],
                "match_type": row[2],
                "quality_score": row[3],
                "ad_group_name": row[4],
                "campaign_name": row[5],
                "impressions": row[6] or 0,
                "clicks": row[7] or 0,
                "cost": row[8] or 0,
                "conversions": row[9] or 0,
                "ctr": round(row[10], 2),
                "avg_cpc": round(row[11], 2) if row[11] else 0,
                "avg_position": round(row[12], 1) if row[12] else None,
                "wasted_spend": row[8] or 0  # Since conversions are low/zero
            })

        total_wasted = sum(k["wasted_spend"] for k in keywords)

        return {
            "period": {
                "start_date": start_date.strftime('%Y-%m-%d'),
                "end_date": end_date.strftime('%Y-%m-%d')
            },
            "criteria": {
                "min_cost": min_cost,
                "max_conversions": max_conversions,
                "min_impressions": min_impressions
            },
            "underperformers": keywords,
            "total_keywords": len(keywords),
            "total_wasted_spend": round(total_wasted, 2)
        }

    except Exception as e:
        logger.error(f"Error fetching underperforming keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8003)