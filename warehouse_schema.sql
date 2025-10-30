-- ==============================================================================
-- Multi-Platform Marketing Data Warehouse Schema
-- ==============================================================================
--
-- Purpose: Unified dimensional data warehouse for Google Ads, Meta Ads, GA4, and Shopify
-- Architecture: Star Schema with dimension tables, fact tables, and mapping tables
-- Database: SQLite (marketing_warehouse.db)
--
-- Key Features:
-- - Cross-platform campaign mapping
-- - Multi-touch attribution
-- - Real-time data from live APIs
-- - Optimized for analytical queries
--
-- Created: 2025-10-28
-- ==============================================================================

-- ==============================================================================
-- CORE DIMENSION TABLES
-- ==============================================================================

-- Customer dimension (master)
CREATE TABLE dim_customer (
    customer_id INTEGER PRIMARY KEY,
    customer_name TEXT NOT NULL,
    descriptive_name TEXT,

    -- Platform-specific IDs
    google_ads_customer_id TEXT,  -- e.g., "1234567890"
    meta_business_id TEXT,         -- e.g., "act_1595713968470185"
    ga4_account_id TEXT,           -- e.g., "123456789"
    shopify_domain TEXT,           -- e.g., "mystore.myshopify.com"

    -- Business info
    industry_vertical TEXT,        -- e.g., "ecommerce", "saas", "b2b", "local"
    timezone TEXT DEFAULT 'UTC',   -- Customer's primary timezone
    currency TEXT DEFAULT 'USD',   -- Base currency for reporting

    -- Status
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_customer_google_ads ON dim_customer(google_ads_customer_id);
CREATE INDEX idx_customer_meta ON dim_customer(meta_business_id);
CREATE INDEX idx_customer_ga4 ON dim_customer(ga4_account_id);


-- Platform dimension
CREATE TABLE dim_platform (
    platform_id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform_name TEXT NOT NULL UNIQUE,  -- google_ads, meta_ads, ga4, shopify
    platform_category TEXT,               -- ads, analytics, ecommerce
    api_version TEXT,
    last_sync_at TIMESTAMP,
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Pre-populate platforms
INSERT INTO dim_platform (platform_name, platform_category) VALUES
('google_ads', 'ads'),
('meta_ads', 'ads'),
('ga4', 'analytics'),
('shopify', 'ecommerce');


-- Date dimension for time-series analysis
CREATE TABLE dim_date (
    date_id TEXT PRIMARY KEY,  -- YYYYMMDD format (e.g., "20250128")
    full_date DATE NOT NULL UNIQUE,
    year INTEGER NOT NULL,
    quarter INTEGER NOT NULL,
    month INTEGER NOT NULL,
    week INTEGER NOT NULL,
    day_of_month INTEGER NOT NULL,
    day_of_week INTEGER NOT NULL,  -- 0=Sunday, 6=Saturday
    month_name TEXT NOT NULL,
    day_name TEXT NOT NULL,

    -- Flags
    is_weekend BOOLEAN DEFAULT 0,
    is_holiday BOOLEAN DEFAULT 0,

    -- Fiscal periods (can customize)
    fiscal_year INTEGER,
    fiscal_quarter INTEGER,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_date_full ON dim_date(full_date);
CREATE INDEX idx_date_year_month ON dim_date(year, month);


-- Unified campaign dimension (cross-platform master)
CREATE TABLE dim_campaign_unified (
    campaign_unified_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,

    -- Campaign info
    campaign_name TEXT NOT NULL,           -- Normalized name
    campaign_objective TEXT,               -- traffic, conversions, awareness, sales, leads
    campaign_type TEXT,                    -- search, display, social, shopping, video

    -- Dates
    start_date DATE,
    end_date DATE,

    -- Platform mappings (JSON)
    platform_mappings TEXT,  -- JSON: {"google_ads": "campaign_id_123", "meta_ads": "campaign_id_456"}

    -- Status
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
);

CREATE INDEX idx_campaign_unified_customer ON dim_campaign_unified(customer_id);
CREATE INDEX idx_campaign_unified_name ON dim_campaign_unified(campaign_name);


-- ==============================================================================
-- PLATFORM-SPECIFIC DIMENSION TABLES
-- ==============================================================================

-- Google Ads Campaign Dimension
CREATE TABLE dim_google_ads_campaign (
    google_campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_unified_id INTEGER,
    customer_id INTEGER NOT NULL,

    -- Google Ads specific
    campaign_id TEXT NOT NULL,  -- Google's campaign ID
    campaign_name TEXT NOT NULL,
    status TEXT,                -- ENABLED, PAUSED, REMOVED
    serving_status TEXT,        -- SERVING, SUSPENDED, ENDED
    channel_type TEXT,          -- SEARCH, DISPLAY, SHOPPING, VIDEO, MULTI_CHANNEL

    -- Bidding
    bidding_strategy_type TEXT,
    target_cpa_micros INTEGER,
    target_roas REAL,
    budget_amount_micros INTEGER,
    budget_period TEXT,         -- DAILY, CUSTOM

    -- Performance metrics
    optimization_score REAL,    -- 0-1 (Google's optimization score)

    -- Settings (JSON for flexibility)
    network_settings TEXT,      -- JSON: {search_network, display_network, etc.}
    ad_rotation_mode TEXT,

    -- Dates
    start_date DATE,
    end_date DATE,

    -- Metadata
    is_deleted BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (campaign_unified_id) REFERENCES dim_campaign_unified(campaign_unified_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
);

CREATE INDEX idx_google_campaign_customer ON dim_google_ads_campaign(customer_id);
CREATE INDEX idx_google_campaign_id ON dim_google_ads_campaign(campaign_id);
CREATE INDEX idx_google_campaign_unified ON dim_google_ads_campaign(campaign_unified_id);


-- Meta Ads Campaign Dimension
CREATE TABLE dim_meta_campaign (
    meta_campaign_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_unified_id INTEGER,
    customer_id INTEGER NOT NULL,
    account_id TEXT NOT NULL,

    -- Meta specific
    campaign_id TEXT NOT NULL,  -- Meta's campaign ID
    name TEXT NOT NULL,
    status TEXT,                -- ACTIVE, PAUSED, DELETED, ARCHIVED
    effective_status TEXT,      -- ACTIVE, PAUSED, DELETED, PENDING_REVIEW, etc.
    objective TEXT,             -- OUTCOME_SALES, OUTCOME_LEADS, OUTCOME_AWARENESS, etc.

    -- Budget
    daily_budget REAL,
    lifetime_budget REAL,
    budget_remaining REAL,
    budget_type TEXT,           -- daily, lifetime

    -- Bidding
    bid_strategy TEXT,          -- LOWEST_COST_WITHOUT_CAP, etc.
    buying_type TEXT,           -- AUCTION, RESERVED

    -- Settings
    special_ad_categories TEXT,  -- JSON array

    -- Dates
    created_time TIMESTAMP,
    updated_time TIMESTAMP,
    start_time TIMESTAMP,
    stop_time TIMESTAMP,

    -- Metadata
    is_deleted BOOLEAN DEFAULT 0,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (campaign_unified_id) REFERENCES dim_campaign_unified(campaign_unified_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
);

CREATE INDEX idx_meta_campaign_customer ON dim_meta_campaign(customer_id);
CREATE INDEX idx_meta_campaign_id ON dim_meta_campaign(campaign_id);
CREATE INDEX idx_meta_campaign_account ON dim_meta_campaign(account_id);
CREATE INDEX idx_meta_campaign_unified ON dim_meta_campaign(campaign_unified_id);


-- GA4 Source/Medium Dimension
CREATE TABLE dim_ga4_source_medium (
    source_medium_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    property_id TEXT NOT NULL,

    -- GA4 traffic source
    utm_source TEXT,            -- From UTM parameters
    utm_medium TEXT,
    utm_campaign TEXT,
    utm_term TEXT,
    utm_content TEXT,

    -- GA4 fallback attribution
    source TEXT,                -- ga:source dimension
    medium TEXT,                -- ga:medium dimension

    -- Cross-platform linking
    linked_campaign_unified_id INTEGER,
    traffic_type TEXT,          -- paid, organic, direct, referral, social, email

    -- Metadata
    first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (linked_campaign_unified_id) REFERENCES dim_campaign_unified(campaign_unified_id)
);

CREATE INDEX idx_ga4_customer ON dim_ga4_source_medium(customer_id);
CREATE INDEX idx_ga4_property ON dim_ga4_source_medium(property_id);
CREATE INDEX idx_ga4_utm_campaign ON dim_ga4_source_medium(utm_campaign);
CREATE INDEX idx_ga4_linked_campaign ON dim_ga4_source_medium(linked_campaign_unified_id);


-- Google Ads Ad Group Dimension
CREATE TABLE dim_ad_group (
    ad_group_id INTEGER PRIMARY KEY AUTOINCREMENT,
    google_campaign_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,

    -- Google Ads specific
    adgroup_id TEXT NOT NULL,  -- Google's ad group ID
    adgroup_name TEXT NOT NULL,
    status TEXT,

    -- Bidding
    cpc_bid_micros INTEGER,
    target_cpa_micros INTEGER,

    -- Dates
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (google_campaign_id) REFERENCES dim_google_ads_campaign(google_campaign_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
);

CREATE INDEX idx_adgroup_campaign ON dim_ad_group(google_campaign_id);
CREATE INDEX idx_adgroup_customer ON dim_ad_group(customer_id);


-- Google Ads Keyword Dimension
CREATE TABLE dim_keyword (
    keyword_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ad_group_id INTEGER NOT NULL,
    google_campaign_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,

    -- Keyword details
    keyword_text TEXT NOT NULL,
    match_type TEXT,  -- EXACT, PHRASE, BROAD
    status TEXT,

    -- Quality
    quality_score INTEGER,  -- 1-10

    -- Bidding
    cpc_bid_micros INTEGER,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (ad_group_id) REFERENCES dim_ad_group(ad_group_id),
    FOREIGN KEY (google_campaign_id) REFERENCES dim_google_ads_campaign(google_campaign_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id)
);

CREATE INDEX idx_keyword_adgroup ON dim_keyword(ad_group_id);
CREATE INDEX idx_keyword_customer ON dim_keyword(customer_id);


-- ==============================================================================
-- FACT TABLES (Star Schema)
-- ==============================================================================

-- Daily Campaign Performance Fact Table
CREATE TABLE fact_campaign_performance_daily (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Dimension keys
    customer_id INTEGER NOT NULL,
    platform_id INTEGER NOT NULL,
    date_id TEXT NOT NULL,
    campaign_unified_id INTEGER,

    -- Platform-specific campaign keys (nullable)
    google_campaign_id INTEGER,
    meta_campaign_id INTEGER,
    ga4_source_medium_id INTEGER,

    -- Core standardized metrics
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    spend_micros INTEGER DEFAULT 0,  -- In micros (1/1,000,000 of currency unit)
    conversions REAL DEFAULT 0,
    conversion_value_micros INTEGER DEFAULT 0,

    -- Calculated metrics
    ctr REAL,         -- Click-through rate %
    cpc_micros INTEGER,  -- Cost per click
    cpm_micros INTEGER,  -- Cost per 1000 impressions
    cpa_micros INTEGER,  -- Cost per acquisition
    roas REAL,        -- Return on ad spend

    -- Platform-specific metrics (JSON for flexibility)
    google_ads_metrics TEXT,  -- JSON: {quality_score, search_impression_share, top_impression_share, etc.}
    meta_ads_metrics TEXT,    -- JSON: {reach, frequency, engagement, inline_link_clicks, etc.}
    ga4_metrics TEXT,         -- JSON: {sessions, bounce_rate, avg_session_duration, pages_per_session, etc.}

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (platform_id) REFERENCES dim_platform(platform_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (campaign_unified_id) REFERENCES dim_campaign_unified(campaign_unified_id),
    FOREIGN KEY (google_campaign_id) REFERENCES dim_google_ads_campaign(google_campaign_id),
    FOREIGN KEY (meta_campaign_id) REFERENCES dim_meta_campaign(meta_campaign_id),
    FOREIGN KEY (ga4_source_medium_id) REFERENCES dim_ga4_source_medium(source_medium_id),

    -- Ensure unique daily records per campaign per platform
    UNIQUE(customer_id, platform_id, date_id, campaign_unified_id, google_campaign_id, meta_campaign_id, ga4_source_medium_id)
);

CREATE INDEX idx_fact_campaign_customer_date ON fact_campaign_performance_daily(customer_id, date_id);
CREATE INDEX idx_fact_campaign_platform ON fact_campaign_performance_daily(platform_id);
CREATE INDEX idx_fact_campaign_unified ON fact_campaign_performance_daily(campaign_unified_id);


-- Daily Keyword Performance Fact Table
CREATE TABLE fact_keyword_performance_daily (
    fact_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Dimension keys
    customer_id INTEGER NOT NULL,
    date_id TEXT NOT NULL,
    google_campaign_id INTEGER NOT NULL,
    ad_group_id INTEGER NOT NULL,
    keyword_id INTEGER NOT NULL,

    -- Metrics
    impressions INTEGER DEFAULT 0,
    clicks INTEGER DEFAULT 0,
    cost_micros INTEGER DEFAULT 0,
    conversions REAL DEFAULT 0,
    conversion_value_micros INTEGER DEFAULT 0,

    -- Keyword-specific metrics
    quality_score INTEGER,
    avg_position REAL,
    search_impression_share REAL,  -- % of eligible impressions received

    -- Calculated
    ctr REAL,
    cpc_micros INTEGER,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (google_campaign_id) REFERENCES dim_google_ads_campaign(google_campaign_id),
    FOREIGN KEY (ad_group_id) REFERENCES dim_ad_group(ad_group_id),
    FOREIGN KEY (keyword_id) REFERENCES dim_keyword(keyword_id),

    UNIQUE(customer_id, date_id, keyword_id)
);

CREATE INDEX idx_fact_keyword_customer_date ON fact_keyword_performance_daily(customer_id, date_id);
CREATE INDEX idx_fact_keyword_campaign ON fact_keyword_performance_daily(google_campaign_id);


-- Shopify Orders Fact Table (with attribution)
CREATE TABLE fact_shopify_orders (
    order_id TEXT PRIMARY KEY,
    customer_id INTEGER NOT NULL,
    store_id TEXT NOT NULL,
    date_id TEXT NOT NULL,

    -- Attribution (cross-platform)
    campaign_unified_id INTEGER,
    google_campaign_id INTEGER,
    meta_campaign_id INTEGER,
    ga4_source_medium_id INTEGER,

    -- Order details
    total_price_micros INTEGER NOT NULL,
    subtotal_micros INTEGER,
    tax_micros INTEGER,
    discount_micros INTEGER,
    shipping_micros INTEGER,

    -- Order status
    financial_status TEXT,      -- paid, pending, refunded, etc.
    fulfillment_status TEXT,    -- fulfilled, partial, unfulfilled

    -- Order items
    line_items_count INTEGER,
    product_categories TEXT,    -- JSON array

    -- Attribution fields
    gclid TEXT,                 -- Google Click ID
    fbclid TEXT,                -- Facebook Click ID
    ga4_client_id TEXT,         -- GA4 Client ID

    -- UTM parameters
    utm_source TEXT,
    utm_medium TEXT,
    utm_campaign TEXT,
    utm_term TEXT,
    utm_content TEXT,

    -- Attribution analysis
    attribution_model TEXT DEFAULT 'last_click',  -- last_click, first_click, linear, time_decay
    attribution_confidence INTEGER,  -- 0-100 (100 = exact match via GCLID, lower for UTM matching)

    -- Shopify metadata
    shopify_customer_id TEXT,
    email TEXT,
    phone TEXT,

    -- Timestamps
    order_created_at TIMESTAMP,
    order_updated_at TIMESTAMP,
    synced_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (campaign_unified_id) REFERENCES dim_campaign_unified(campaign_unified_id),
    FOREIGN KEY (google_campaign_id) REFERENCES dim_google_ads_campaign(google_campaign_id),
    FOREIGN KEY (meta_campaign_id) REFERENCES dim_meta_campaign(meta_campaign_id),
    FOREIGN KEY (ga4_source_medium_id) REFERENCES dim_ga4_source_medium(source_medium_id)
);

CREATE INDEX idx_shopify_customer ON fact_shopify_orders(customer_id);
CREATE INDEX idx_shopify_date ON fact_shopify_orders(date_id);
CREATE INDEX idx_shopify_gclid ON fact_shopify_orders(gclid);
CREATE INDEX idx_shopify_fbclid ON fact_shopify_orders(fbclid);
CREATE INDEX idx_shopify_campaign_unified ON fact_shopify_orders(campaign_unified_id);


-- ==============================================================================
-- MAPPING TABLES (Cross-Platform)
-- ==============================================================================

-- Campaign Cross-Platform Mapping
CREATE TABLE map_campaign_cross_platform (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    campaign_unified_id INTEGER NOT NULL,
    customer_id INTEGER NOT NULL,

    -- Platform-specific campaign IDs
    google_ads_campaign_id INTEGER,
    meta_campaign_id INTEGER,
    ga4_utm_campaign TEXT,
    shopify_utm_campaign TEXT,

    -- Mapping metadata
    mapping_method TEXT,  -- manual, auto_name_match, auto_utm_match, ml_predicted
    mapping_confidence INTEGER DEFAULT 0,  -- 0-100

    -- Audit
    created_by TEXT,  -- user_id or 'system'
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified_at TIMESTAMP,
    is_verified BOOLEAN DEFAULT 0,

    FOREIGN KEY (campaign_unified_id) REFERENCES dim_campaign_unified(campaign_unified_id),
    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (google_ads_campaign_id) REFERENCES dim_google_ads_campaign(google_campaign_id),
    FOREIGN KEY (meta_campaign_id) REFERENCES dim_meta_campaign(meta_campaign_id),

    UNIQUE(campaign_unified_id, google_ads_campaign_id, meta_campaign_id, ga4_utm_campaign)
);

CREATE INDEX idx_map_campaign_customer ON map_campaign_cross_platform(customer_id);
CREATE INDEX idx_map_campaign_unified ON map_campaign_cross_platform(campaign_unified_id);


-- Account Platform Mapping
CREATE TABLE map_account_platform (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    platform_id INTEGER NOT NULL,

    -- Platform-specific account ID
    platform_account_id TEXT NOT NULL,  -- e.g., "act_123" for Meta, "1234567890" for Google Ads
    account_name TEXT,

    -- Status
    is_active BOOLEAN DEFAULT 1,
    is_primary BOOLEAN DEFAULT 0,  -- Primary account for this customer on this platform

    -- Credentials status
    credentials_valid BOOLEAN DEFAULT 1,
    credentials_valid_until TIMESTAMP,
    last_sync_at TIMESTAMP,
    last_sync_status TEXT,  -- success, failed, partial

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (platform_id) REFERENCES dim_platform(platform_id),

    UNIQUE(customer_id, platform_id, platform_account_id)
);

CREATE INDEX idx_map_account_customer ON map_account_platform(customer_id);
CREATE INDEX idx_map_account_platform ON map_account_platform(platform_id);


-- Customer Identifier Mapping (Master)
CREATE TABLE map_customer_identifiers (
    mapping_id INTEGER PRIMARY KEY AUTOINCREMENT,
    internal_customer_id INTEGER NOT NULL,

    -- Platform identification
    platform TEXT NOT NULL,  -- google_ads, meta_ads, ga4, shopify
    external_id TEXT NOT NULL,
    external_name TEXT,

    -- Validation
    mapping_verified BOOLEAN DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    last_verified_at TIMESTAMP,

    FOREIGN KEY (internal_customer_id) REFERENCES dim_customer(customer_id),

    UNIQUE(internal_customer_id, platform, external_id)
);

CREATE INDEX idx_map_customer_internal ON map_customer_identifiers(internal_customer_id);
CREATE INDEX idx_map_customer_external ON map_customer_identifiers(external_id);


-- ==============================================================================
-- ATTRIBUTION TABLES
-- ==============================================================================

-- Multi-Touch Attribution Touchpoints
CREATE TABLE attribution_touchpoints (
    touchpoint_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    conversion_id TEXT NOT NULL,  -- FK to fact_shopify_orders.order_id or other conversion table

    -- Journey sequence
    touchpoint_sequence INTEGER NOT NULL,  -- 1, 2, 3, ... (order in customer journey)

    -- Timing
    date_id TEXT NOT NULL,
    touchpoint_timestamp TIMESTAMP NOT NULL,

    -- Platform & campaign
    platform_id INTEGER NOT NULL,
    campaign_unified_id INTEGER,
    google_campaign_id INTEGER,
    meta_campaign_id INTEGER,
    ga4_source_medium_id INTEGER,

    -- Traffic source details
    source TEXT,
    medium TEXT,
    campaign TEXT,
    term TEXT,
    content TEXT,

    -- User context
    device_category TEXT,       -- mobile, desktop, tablet
    landing_page_url TEXT,
    referrer_url TEXT,

    -- Attribution value (calculated per model)
    attributed_value_micros INTEGER,  -- Portion of conversion value attributed to this touchpoint
    attribution_model TEXT,            -- first_touch, last_touch, linear, time_decay, position_based

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (conversion_id) REFERENCES fact_shopify_orders(order_id),
    FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    FOREIGN KEY (platform_id) REFERENCES dim_platform(platform_id),
    FOREIGN KEY (campaign_unified_id) REFERENCES dim_campaign_unified(campaign_unified_id),

    UNIQUE(conversion_id, touchpoint_sequence)
);

CREATE INDEX idx_touchpoint_conversion ON attribution_touchpoints(conversion_id);
CREATE INDEX idx_touchpoint_customer ON attribution_touchpoints(customer_id);
CREATE INDEX idx_touchpoint_campaign ON attribution_touchpoints(campaign_unified_id);


-- ==============================================================================
-- SYNC STATUS TRACKING
-- ==============================================================================

-- ETL Sync Status
CREATE TABLE etl_sync_log (
    sync_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    platform_id INTEGER NOT NULL,

    -- Sync details
    sync_started_at TIMESTAMP NOT NULL,
    sync_completed_at TIMESTAMP,
    sync_status TEXT NOT NULL,  -- running, success, failed, partial

    -- Records processed
    records_fetched INTEGER DEFAULT 0,
    records_inserted INTEGER DEFAULT 0,
    records_updated INTEGER DEFAULT 0,
    records_failed INTEGER DEFAULT 0,

    -- Error tracking
    error_message TEXT,
    error_details TEXT,  -- JSON with detailed error info

    -- Sync type
    sync_type TEXT DEFAULT 'incremental',  -- full, incremental

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (platform_id) REFERENCES dim_platform(platform_id)
);

CREATE INDEX idx_sync_log_customer ON etl_sync_log(customer_id);
CREATE INDEX idx_sync_log_platform ON etl_sync_log(platform_id);
CREATE INDEX idx_sync_log_status ON etl_sync_log(sync_status);


-- ==============================================================================
-- VIEWS FOR COMMON QUERIES
-- ==============================================================================

-- Unified campaign performance across all platforms
CREATE VIEW view_unified_campaign_performance AS
SELECT
    f.customer_id,
    f.date_id,
    d.full_date,
    cu.campaign_unified_id,
    cu.campaign_name,
    p.platform_name,

    -- Metrics
    f.impressions,
    f.clicks,
    f.spend_micros / 1000000.0 AS spend,
    f.conversions,
    f.conversion_value_micros / 1000000.0 AS conversion_value,
    f.ctr,
    f.cpc_micros / 1000000.0 AS cpc,
    f.roas

FROM fact_campaign_performance_daily f
JOIN dim_date d ON f.date_id = d.date_id
JOIN dim_customer c ON f.customer_id = c.customer_id
JOIN dim_platform p ON f.platform_id = p.platform_id
LEFT JOIN dim_campaign_unified cu ON f.campaign_unified_id = cu.campaign_unified_id;


-- Attribution coverage report
CREATE VIEW view_attribution_coverage AS
SELECT
    customer_id,
    COUNT(*) as total_orders,
    SUM(CASE WHEN campaign_unified_id IS NOT NULL THEN 1 ELSE 0 END) as attributed_orders,
    ROUND(100.0 * SUM(CASE WHEN campaign_unified_id IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as attribution_coverage_pct,
    SUM(CASE WHEN gclid IS NOT NULL THEN 1 ELSE 0 END) as orders_with_gclid,
    SUM(CASE WHEN fbclid IS NOT NULL THEN 1 ELSE 0 END) as orders_with_fbclid,
    SUM(CASE WHEN utm_campaign IS NOT NULL THEN 1 ELSE 0 END) as orders_with_utm
FROM fact_shopify_orders
GROUP BY customer_id;


-- ==============================================================================
-- END OF SCHEMA
-- ==============================================================================
