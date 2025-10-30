"""
Warehouse ETL Helper Functions

Shared utilities for all ETL scripts writing to marketing_warehouse.db
"""

import sqlite3
from pathlib import Path
from datetime import datetime, date
from typing import Dict, Optional, Any
import json

# Database path
WAREHOUSE_DB = Path(__file__).parent / "marketing_warehouse.db"


def get_warehouse_connection():
    """Get connection to warehouse database"""
    conn = sqlite3.connect(WAREHOUSE_DB)
    conn.row_factory = sqlite3.Row  # Enable column access by name
    return conn


def get_or_create_customer(conn, customer_id: int, customer_name: str,
                           google_ads_customer_id: str = None,
                           meta_business_id: str = None,
                           ga4_account_id: str = None,
                           shopify_domain: str = None,
                           currency: str = None) -> int:
    """
    Get or create customer record

    Returns: customer_id
    """
    cursor = conn.cursor()

    # Check if customer exists
    cursor.execute("SELECT customer_id FROM dim_customer WHERE customer_id = ?", (customer_id,))
    existing = cursor.fetchone()

    if existing:
        # Update platform IDs if provided
        updates = []
        params = []

        if google_ads_customer_id:
            updates.append("google_ads_customer_id = ?")
            params.append(google_ads_customer_id)
        if meta_business_id:
            updates.append("meta_business_id = ?")
            params.append(meta_business_id)
        if ga4_account_id:
            updates.append("ga4_account_id = ?")
            params.append(ga4_account_id)
        if shopify_domain:
            updates.append("shopify_domain = ?")
            params.append(shopify_domain)
        if currency:
            updates.append("currency = ?")
            params.append(currency)

        if updates:
            updates.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(customer_id)

            cursor.execute(f"""
                UPDATE dim_customer
                SET {', '.join(updates)}
                WHERE customer_id = ?
            """, params)
            conn.commit()

        return customer_id
    else:
        # Create new customer
        cursor.execute("""
            INSERT INTO dim_customer (
                customer_id, customer_name, google_ads_customer_id,
                meta_business_id, ga4_account_id, shopify_domain, currency
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (customer_id, customer_name, google_ads_customer_id,
              meta_business_id, ga4_account_id, shopify_domain, currency))
        conn.commit()
        return customer_id


def get_platform_id(conn, platform_name: str) -> int:
    """Get platform ID by name"""
    cursor = conn.cursor()
    cursor.execute("SELECT platform_id FROM dim_platform WHERE platform_name = ?", (platform_name,))
    row = cursor.fetchone()
    if row:
        return row[0]
    raise ValueError(f"Platform not found: {platform_name}")


def get_date_id(date_value: Any) -> str:
    """
    Convert date to date_id format (YYYYMMDD)

    Accepts: datetime, date, or string (YYYY-MM-DD)
    """
    if isinstance(date_value, datetime):
        return date_value.strftime("%Y%m%d")
    elif isinstance(date_value, date):
        return date_value.strftime("%Y%m%d")
    elif isinstance(date_value, str):
        # Parse YYYY-MM-DD format
        dt = datetime.strptime(date_value, "%Y-%m-%d")
        return dt.strftime("%Y%m%d")
    else:
        raise ValueError(f"Invalid date value: {date_value}")


def upsert_google_ads_campaign(conn, customer_id: int, campaign_data: Dict) -> int:
    """
    Insert or update Google Ads campaign dimension

    Returns: google_campaign_id (internal PK)
    """
    cursor = conn.cursor()

    # Check if campaign exists
    cursor.execute("""
        SELECT google_campaign_id FROM dim_google_ads_campaign
        WHERE customer_id = ? AND campaign_id = ?
    """, (customer_id, campaign_data['campaign_id']))

    existing = cursor.fetchone()

    if existing:
        # Update existing
        google_campaign_id = existing[0]
        cursor.execute("""
            UPDATE dim_google_ads_campaign SET
                campaign_name = ?,
                status = ?,
                serving_status = ?,
                channel_type = ?,
                bidding_strategy_type = ?,
                target_cpa_micros = ?,
                target_roas = ?,
                budget_amount_micros = ?,
                budget_period = ?,
                optimization_score = ?,
                start_date = ?,
                end_date = ?,
                updated_at = ?
            WHERE google_campaign_id = ?
        """, (
            campaign_data.get('campaign_name'),
            campaign_data.get('status'),
            campaign_data.get('serving_status'),
            campaign_data.get('channel_type'),
            campaign_data.get('bidding_strategy_type'),
            campaign_data.get('target_cpa_micros'),
            campaign_data.get('target_roas'),
            campaign_data.get('budget_amount_micros'),
            campaign_data.get('budget_period'),
            campaign_data.get('optimization_score'),
            campaign_data.get('start_date'),
            campaign_data.get('end_date'),
            datetime.now().isoformat(),
            google_campaign_id
        ))
    else:
        # Insert new
        cursor.execute("""
            INSERT INTO dim_google_ads_campaign (
                customer_id, campaign_id, campaign_name, status, serving_status,
                channel_type, bidding_strategy_type, target_cpa_micros, target_roas,
                budget_amount_micros, budget_period, optimization_score,
                start_date, end_date
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id,
            campaign_data['campaign_id'],
            campaign_data.get('campaign_name'),
            campaign_data.get('status'),
            campaign_data.get('serving_status'),
            campaign_data.get('channel_type'),
            campaign_data.get('bidding_strategy_type'),
            campaign_data.get('target_cpa_micros'),
            campaign_data.get('target_roas'),
            campaign_data.get('budget_amount_micros'),
            campaign_data.get('budget_period'),
            campaign_data.get('optimization_score'),
            campaign_data.get('start_date'),
            campaign_data.get('end_date')
        ))
        google_campaign_id = cursor.lastrowid

    conn.commit()
    return google_campaign_id


def upsert_campaign_performance_fact(conn, customer_id: int, platform_name: str,
                                     date_value: str, google_campaign_id: int,
                                     metrics: Dict) -> None:
    """
    Insert or update daily campaign performance fact

    metrics should include: impressions, clicks, spend_micros, conversions, etc.
    """
    cursor = conn.cursor()

    platform_id = get_platform_id(conn, platform_name)
    date_id = get_date_id(date_value)

    # Calculate derived metrics
    impressions = metrics.get('impressions', 0)
    clicks = metrics.get('clicks', 0)
    spend_micros = metrics.get('spend_micros', 0)
    conversions = metrics.get('conversions', 0)
    conversion_value_micros = metrics.get('conversion_value_micros', 0)

    ctr = round((clicks / impressions * 100), 2) if impressions > 0 else 0
    cpc_micros = int(spend_micros / clicks) if clicks > 0 else 0
    cpm_micros = int(spend_micros / impressions * 1000) if impressions > 0 else 0
    cpa_micros = int(spend_micros / conversions) if conversions > 0 else 0
    roas = round((conversion_value_micros / spend_micros), 2) if spend_micros > 0 else 0

    # Google Ads specific metrics (JSON)
    google_ads_metrics = json.dumps({
        'quality_score': metrics.get('quality_score'),
        'search_impression_share': metrics.get('search_impression_share'),
        'search_top_impression_share': metrics.get('search_top_impression_share'),
        'search_rank_lost_impression_share': metrics.get('search_rank_lost_impression_share'),
        'average_cpc': metrics.get('average_cpc'),
        'cost_per_conversion': metrics.get('cost_per_conversion'),
        'interaction_rate': metrics.get('interaction_rate')
    })

    # Check if record exists
    cursor.execute("""
        SELECT fact_id FROM fact_campaign_performance_daily
        WHERE customer_id = ? AND platform_id = ? AND date_id = ? AND google_campaign_id = ?
    """, (customer_id, platform_id, date_id, google_campaign_id))

    existing = cursor.fetchone()

    if existing:
        # Update existing
        fact_id = existing[0]
        cursor.execute("""
            UPDATE fact_campaign_performance_daily SET
                impressions = ?,
                clicks = ?,
                spend_micros = ?,
                conversions = ?,
                conversion_value_micros = ?,
                ctr = ?,
                cpc_micros = ?,
                cpm_micros = ?,
                cpa_micros = ?,
                roas = ?,
                google_ads_metrics = ?,
                updated_at = ?
            WHERE fact_id = ?
        """, (
            impressions, clicks, spend_micros, conversions, conversion_value_micros,
            ctr, cpc_micros, cpm_micros, cpa_micros, roas,
            google_ads_metrics,
            datetime.now().isoformat(),
            fact_id
        ))
    else:
        # Insert new
        cursor.execute("""
            INSERT INTO fact_campaign_performance_daily (
                customer_id, platform_id, date_id, google_campaign_id,
                impressions, clicks, spend_micros, conversions, conversion_value_micros,
                ctr, cpc_micros, cpm_micros, cpa_micros, roas,
                google_ads_metrics
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id, platform_id, date_id, google_campaign_id,
            impressions, clicks, spend_micros, conversions, conversion_value_micros,
            ctr, cpc_micros, cpm_micros, cpa_micros, roas,
            google_ads_metrics
        ))

    conn.commit()


def upsert_ad_group(conn, customer_id: int, google_campaign_id: int, ad_group_data: Dict) -> int:
    """
    Insert or update ad group dimension

    Returns: ad_group_id (internal PK)
    """
    cursor = conn.cursor()

    # Check if ad group exists (using adgroup_id which stores Google's ID)
    cursor.execute("""
        SELECT ad_group_id FROM dim_ad_group
        WHERE customer_id = ? AND adgroup_id = ?
    """, (customer_id, ad_group_data['ad_group_id']))

    existing = cursor.fetchone()

    if existing:
        # Update existing
        internal_ad_group_id = existing[0]
        cursor.execute("""
            UPDATE dim_ad_group SET
                adgroup_name = ?,
                status = ?,
                cpc_bid_micros = ?,
                target_cpa_micros = ?,
                updated_at = ?
            WHERE ad_group_id = ?
        """, (
            ad_group_data.get('ad_group_name'),
            ad_group_data.get('status'),
            ad_group_data.get('cpc_bid_micros'),
            ad_group_data.get('target_cpa_micros'),
            datetime.now().isoformat(),
            internal_ad_group_id
        ))
    else:
        # Insert new
        cursor.execute("""
            INSERT INTO dim_ad_group (
                google_campaign_id, customer_id, adgroup_id, adgroup_name,
                status, cpc_bid_micros, target_cpa_micros
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            google_campaign_id,
            customer_id,
            ad_group_data['ad_group_id'],  # Google's ad group ID
            ad_group_data.get('ad_group_name'),
            ad_group_data.get('status'),
            ad_group_data.get('cpc_bid_micros'),
            ad_group_data.get('target_cpa_micros')
        ))
        internal_ad_group_id = cursor.lastrowid

    conn.commit()
    return internal_ad_group_id


def upsert_keyword(conn, customer_id: int, internal_ad_group_id: int, google_campaign_id: int, keyword_data: Dict) -> int:
    """
    Insert or update keyword dimension

    Returns: keyword_id (internal PK)
    """
    cursor = conn.cursor()

    # Check if keyword exists (use keyword_text + match_type + ad_group_id as unique key)
    cursor.execute("""
        SELECT keyword_id FROM dim_keyword
        WHERE customer_id = ? AND ad_group_id = ? AND keyword_text = ? AND match_type = ?
    """, (customer_id, internal_ad_group_id, keyword_data['keyword_text'], keyword_data.get('match_type')))

    existing = cursor.fetchone()

    if existing:
        # Update existing
        internal_keyword_id = existing[0]
        cursor.execute("""
            UPDATE dim_keyword SET
                status = ?,
                quality_score = ?,
                cpc_bid_micros = ?,
                updated_at = ?
            WHERE keyword_id = ?
        """, (
            keyword_data.get('status'),
            keyword_data.get('quality_score'),
            keyword_data.get('cpc_bid_micros'),
            datetime.now().isoformat(),
            internal_keyword_id
        ))
    else:
        # Insert new
        cursor.execute("""
            INSERT INTO dim_keyword (
                ad_group_id, google_campaign_id, customer_id, keyword_text,
                match_type, status, quality_score, cpc_bid_micros
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            internal_ad_group_id,
            google_campaign_id,
            customer_id,
            keyword_data.get('keyword_text'),
            keyword_data.get('match_type'),
            keyword_data.get('status'),
            keyword_data.get('quality_score'),
            keyword_data.get('cpc_bid_micros')
        ))
        internal_keyword_id = cursor.lastrowid

    conn.commit()
    return internal_keyword_id


def upsert_keyword_performance_fact(conn, customer_id: int, google_campaign_id: int,
                                     internal_ad_group_id: int, internal_keyword_id: int,
                                     date_value: str, metrics: Dict) -> None:
    """
    Insert or update daily keyword performance fact

    metrics should include: impressions, clicks, cost_micros, conversions, etc.
    """
    cursor = conn.cursor()

    date_id = get_date_id(date_value)

    # Calculate derived metrics
    impressions = metrics.get('impressions', 0)
    clicks = metrics.get('clicks', 0)
    cost_micros = metrics.get('cost_micros', 0)
    conversions = metrics.get('conversions', 0)
    conversion_value_micros = metrics.get('conversion_value_micros', 0)

    ctr = round((clicks / impressions * 100), 2) if impressions > 0 else 0
    cpc_micros = int(cost_micros / clicks) if clicks > 0 else 0

    # Check if record exists
    cursor.execute("""
        SELECT fact_id FROM fact_keyword_performance_daily
        WHERE customer_id = ? AND date_id = ? AND keyword_id = ?
    """, (customer_id, date_id, internal_keyword_id))

    existing = cursor.fetchone()

    if existing:
        # Update existing
        fact_id = existing[0]
        cursor.execute("""
            UPDATE fact_keyword_performance_daily SET
                impressions = ?,
                clicks = ?,
                cost_micros = ?,
                conversions = ?,
                conversion_value_micros = ?,
                quality_score = ?,
                ctr = ?,
                cpc_micros = ?
            WHERE fact_id = ?
        """, (
            impressions, clicks, cost_micros, conversions, conversion_value_micros,
            metrics.get('quality_score'),
            ctr, cpc_micros,
            fact_id
        ))
    else:
        # Insert new
        cursor.execute("""
            INSERT INTO fact_keyword_performance_daily (
                customer_id, date_id, google_campaign_id, ad_group_id, keyword_id,
                impressions, clicks, cost_micros, conversions, conversion_value_micros,
                quality_score, ctr, cpc_micros
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            customer_id, date_id, google_campaign_id, internal_ad_group_id, internal_keyword_id,
            impressions, clicks, cost_micros, conversions, conversion_value_micros,
            metrics.get('quality_score'),
            ctr, cpc_micros
        ))

    conn.commit()


def log_etl_sync(conn, customer_id: int, platform_name: str,
                sync_status: str, records_fetched: int = 0,
                records_inserted: int = 0, records_updated: int = 0,
                error_message: str = None) -> int:
    """
    Log ETL sync run

    Returns: sync_id
    """
    cursor = conn.cursor()
    platform_id = get_platform_id(conn, platform_name)

    cursor.execute("""
        INSERT INTO etl_sync_log (
            customer_id, platform_id, sync_started_at, sync_completed_at,
            sync_status, records_fetched, records_inserted, records_updated,
            error_message
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        customer_id, platform_id,
        datetime.now().isoformat(),
        datetime.now().isoformat() if sync_status != 'running' else None,
        sync_status,
        records_fetched, records_inserted, records_updated,
        error_message
    ))

    sync_id = cursor.lastrowid
    conn.commit()
    return sync_id


def update_etl_sync(conn, sync_id: int, sync_status: str,
                   records_inserted: int = 0, records_updated: int = 0,
                   error_message: str = None) -> None:
    """Update ETL sync log"""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE etl_sync_log SET
            sync_completed_at = ?,
            sync_status = ?,
            records_inserted = records_inserted + ?,
            records_updated = records_updated + ?,
            error_message = ?
        WHERE sync_id = ?
    """, (
        datetime.now().isoformat(),
        sync_status,
        records_inserted,
        records_updated,
        error_message,
        sync_id
    ))
    conn.commit()


def update_platform_last_sync(conn, platform_name: str) -> None:
    """Update platform last sync timestamp"""
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE dim_platform
        SET last_sync_at = ?
        WHERE platform_name = ?
    """, (datetime.now().isoformat(), platform_name))
    conn.commit()
