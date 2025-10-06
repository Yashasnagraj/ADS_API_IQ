#!/usr/bin/env python3
"""
FastAPI REST API for Marketing Data Warehouse (SQLite)
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime, date, timedelta
import pandas as pd
import sqlite3
import json
from loguru import logger

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

# Database connection
def get_db():
    conn = sqlite3.connect('google_ads_data.db')
    conn.row_factory = sqlite3.Row
    return conn

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

@app.get("/")
def root():
    return {"message": "MarketingIQ API v2.0", "status": "active"}

@app.get("/health")
def health_check():
    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        conn.close()
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}

@app.get("/campaigns")
def get_campaigns():
    try:
        conn = get_db()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        query = """
        SELECT * FROM campaigns
        ORDER BY campaign_name
        """

        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        return results
    except Exception as e:
        logger.error(f"Error fetching campaigns: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/ad-groups")
def get_ad_groups(campaign_id: Optional[int] = None):
    try:
        conn = get_db()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        if campaign_id:
            query = "SELECT * FROM ad_groups WHERE campaign_id = ? ORDER BY ad_group_name"
            cursor.execute(query, (campaign_id,))
        else:
            query = "SELECT * FROM ad_groups ORDER BY ad_group_name"
            cursor.execute(query)

        results = cursor.fetchall()
        conn.close()

        return results
    except Exception as e:
        logger.error(f"Error fetching ad groups: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/keywords")
def get_keywords(campaign_id: Optional[int] = None):
    try:
        conn = get_db()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        if campaign_id:
            query = """
            SELECT k.*
            FROM keywords k
            JOIN campaign_keywords ck ON k.keyword_id = ck.keyword_id
            WHERE ck.campaign_id = ?
            ORDER BY k.keyword_text
            """
            cursor.execute(query, (campaign_id,))
        else:
            query = "SELECT * FROM keywords ORDER BY keyword_text"
            cursor.execute(query)

        results = cursor.fetchall()
        conn.close()

        return results
    except Exception as e:
        logger.error(f"Error fetching keywords: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/search-terms")
def get_search_terms(
    date_start: Optional[str] = None,
    date_end: Optional[str] = None
):
    try:
        conn = get_db()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        query = "SELECT * FROM search_terms ORDER BY impressions DESC LIMIT 100"
        cursor.execute(query)

        results = cursor.fetchall()
        conn.close()

        return results
    except Exception as e:
        logger.error(f"Error fetching search terms: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/summary")
def get_metrics_summary():
    try:
        conn = get_db()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        # Get campaign metrics from search_terms table which has performance data
        query = """
        SELECT
            COUNT(DISTINCT st.campaign_id) as total_campaigns,
            COUNT(DISTINCT CASE WHEN c.status = 'ENABLED' THEN c.campaign_id END) as active_campaigns,
            SUM(st.impressions) as total_impressions,
            SUM(st.clicks) as total_clicks,
            SUM(st.cost_micros / 1000000.0) as total_cost,
            SUM(st.conversions) as total_conversions,
            AVG(st.ctr) as avg_ctr,
            AVG(st.avg_cpc_micros / 1000000.0) as avg_cpc,
            AVG(CASE WHEN st.impressions > 0 THEN st.conversions * 100.0 / st.impressions ELSE 0 END) as avg_conversion_rate
        FROM search_terms st
        LEFT JOIN campaigns c ON st.campaign_id = c.campaign_id
        """

        cursor.execute(query)
        metrics = cursor.fetchone()

        # Get additional counts
        cursor.execute("SELECT COUNT(*) as total_keywords FROM keywords")
        keywords = cursor.fetchone()

        cursor.execute("SELECT COUNT(*) as total_ad_groups FROM ad_groups")
        ad_groups = cursor.fetchone()

        conn.close()

        result = {
            **metrics,
            'total_keywords': keywords['total_keywords'],
            'total_ad_groups': ad_groups['total_ad_groups']
        }

        # Convert None values to 0
        for key in result:
            if result[key] is None:
                result[key] = 0

        return result
    except Exception as e:
        logger.error(f"Error fetching metrics summary: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/trends")
def get_metrics_trends():
    try:
        conn = get_db()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        # Generate sample trend data for demonstration
        trends = []
        base_date = datetime.now() - timedelta(days=30)

        for i in range(30):
            current_date = base_date + timedelta(days=i)
            trends.append({
                'date': current_date.strftime('%Y-%m-%d'),
                'impressions': 10000 + (i * 500),
                'clicks': 500 + (i * 25),
                'cost': 85000 + (i * 4250),  # INR values (roughly 85 INR per USD)
                'conversions': 50 + (i * 2),
                'ctr': 5.0 + (i * 0.1),
                'cpc': 170.0 + (i * 4.25),  # INR values for CPC
                'currency': 'INR'
            })

        conn.close()

        return trends
    except Exception as e:
        logger.error(f"Error fetching metrics trends: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/metrics/by-campaign")
def get_metrics_by_campaign():
    try:
        conn = get_db()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        query = """
        SELECT
            c.campaign_id,
            c.campaign_name,
            c.status,
            SUM(st.impressions) as impressions,
            SUM(st.clicks) as clicks,
            SUM(st.cost_micros / 1000000.0) as cost,
            SUM(st.conversions) as conversions,
            AVG(st.ctr) as ctr,
            AVG(st.avg_cpc_micros / 1000000.0) as cpc,
            AVG(CASE WHEN st.impressions > 0 THEN st.conversions * 100.0 / st.impressions ELSE 0 END) as conversion_rate
        FROM campaigns c
        LEFT JOIN search_terms st ON c.campaign_id = st.campaign_id
        GROUP BY c.campaign_id, c.campaign_name, c.status
        HAVING SUM(st.impressions) > 0
        ORDER BY cost DESC
        LIMIT 10
        """

        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        return results
    except Exception as e:
        logger.error(f"Error fetching metrics by campaign: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/campaigns/top-performers")
def get_top_performers(metric: str = Query("roas", description="Metric to sort by: roas, conversions, or ctr")):
    """Get top performing campaigns by specified metric"""
    try:
        conn = get_db()
        conn.row_factory = dict_factory
        cursor = conn.cursor()

        # Calculate ROAS (assuming we have conversion_value)
        # For now, we'll use conversions as a proxy
        order_by_clause = {
            "roas": "CASE WHEN SUM(st.cost_micros) > 0 THEN SUM(st.conversions) * 100.0 / SUM(st.cost_micros / 1000000.0) ELSE 0 END DESC",
            "conversions": "SUM(st.conversions) DESC",
            "ctr": "AVG(st.ctr) DESC"
        }.get(metric.lower(), "SUM(st.conversions) DESC")

        query = f"""
        SELECT
            c.campaign_id,
            c.campaign_name,
            c.status,
            SUM(st.impressions) as impressions,
            SUM(st.clicks) as clicks,
            SUM(st.cost_micros / 1000000.0) as cost,
            SUM(st.conversions) as conversions,
            AVG(st.ctr) as ctr,
            AVG(st.avg_cpc_micros / 1000000.0) as cpc,
            CASE WHEN SUM(st.cost_micros) > 0 THEN SUM(st.conversions) * 100.0 / SUM(st.cost_micros / 1000000.0) ELSE 0 END as roas,
            AVG(CASE WHEN st.impressions > 0 THEN st.conversions * 100.0 / st.impressions ELSE 0 END) as conversion_rate
        FROM campaigns c
        LEFT JOIN search_terms st ON c.campaign_id = st.campaign_id
        GROUP BY c.campaign_id, c.campaign_name, c.status
        HAVING SUM(st.impressions) > 0
        ORDER BY {order_by_clause}
        LIMIT 10
        """

        cursor.execute(query)
        results = cursor.fetchall()
        conn.close()

        return results
    except Exception as e:
        logger.error(f"Error fetching top performers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8004)