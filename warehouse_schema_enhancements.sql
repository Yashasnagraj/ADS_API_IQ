-- ==============================================================================
-- Marketing Data Warehouse Schema Enhancements
-- ==============================================================================
--
-- Purpose: Add support for:
--   1. Historical data aggregation for week-over-week comparisons
--   2. Industry benchmarks (database-driven)
--   3. ML forecast data storage
--   4. Dynamic confidence score calculations
--
-- Date: 2025-01-12
-- ==============================================================================

-- ==============================================================================
-- HISTORICAL AGGREGATES TABLES
-- ==============================================================================

-- Pre-aggregated metrics for fast historical comparisons
CREATE TABLE IF NOT EXISTS metrics_historical_aggregates (
    aggregate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,

    -- Time period
    period_type TEXT NOT NULL,  -- 'daily', 'weekly', 'monthly', 'quarterly', 'yearly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,

    -- Metric identification
    metric_name TEXT NOT NULL,  -- 'spend', 'conversions', 'roas', 'ctr', 'cpc', 'sessions', 'bounce_rate'
    metric_category TEXT,  -- 'ads', 'analytics', 'ecommerce'

    -- Platform context (optional - NULL means aggregated across all platforms)
    platform_id INTEGER,
    campaign_id TEXT,  -- Can be campaign_unified_id, google_campaign_id, or meta_campaign_id

    -- Metric values
    metric_value REAL NOT NULL,
    metric_count INTEGER,  -- Number of data points used in aggregation
    metric_sum REAL,       -- Sum for calculating averages
    metric_min REAL,       -- Min value in period
    metric_max REAL,       -- Max value in period
    metric_stddev REAL,    -- Standard deviation for anomaly detection

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (platform_id) REFERENCES dim_platform(platform_id),

    -- Ensure unique combinations
    UNIQUE(customer_id, period_type, period_start, period_end, metric_name, platform_id, campaign_id)
);

CREATE INDEX idx_metrics_agg_customer_period ON metrics_historical_aggregates(customer_id, period_type, period_start);
CREATE INDEX idx_metrics_agg_metric_name ON metrics_historical_aggregates(metric_name);
CREATE INDEX idx_metrics_agg_platform ON metrics_historical_aggregates(platform_id);


-- Campaign-specific performance aggregates (for WoW comparisons)
CREATE TABLE IF NOT EXISTS campaign_performance_aggregates (
    aggregate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    campaign_id TEXT NOT NULL,  -- Platform-agnostic campaign identifier
    platform_id INTEGER NOT NULL,

    -- Time period
    period_type TEXT NOT NULL,  -- 'daily', 'weekly', 'monthly'
    period_start DATE NOT NULL,
    period_end DATE NOT NULL,
    week_number INTEGER,  -- ISO week number for WoW comparisons
    year INTEGER,

    -- Aggregated metrics
    total_impressions INTEGER DEFAULT 0,
    total_clicks INTEGER DEFAULT 0,
    total_spend_micros INTEGER DEFAULT 0,
    total_conversions REAL DEFAULT 0,
    total_conversion_value_micros INTEGER DEFAULT 0,

    -- Calculated metrics (averages)
    avg_ctr REAL,
    avg_cpc_micros INTEGER,
    avg_cpm_micros INTEGER,
    avg_cpa_micros INTEGER,
    avg_roas REAL,

    -- Statistical measures
    stddev_spend REAL,
    stddev_conversions REAL,
    stddev_roas REAL,

    -- Metadata
    data_points_count INTEGER,  -- Number of days in this aggregate
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (platform_id) REFERENCES dim_platform(platform_id),

    UNIQUE(customer_id, campaign_id, platform_id, period_type, period_start, period_end)
);

CREATE INDEX idx_campaign_agg_customer_period ON campaign_performance_aggregates(customer_id, period_type, period_start);
CREATE INDEX idx_campaign_agg_campaign ON campaign_performance_aggregates(campaign_id);
CREATE INDEX idx_campaign_agg_week ON campaign_performance_aggregates(customer_id, year, week_number);


-- ==============================================================================
-- INDUSTRY BENCHMARKS TABLE
-- ==============================================================================

-- Database-driven industry benchmarks (replaces hardcoded values)
CREATE TABLE IF NOT EXISTS industry_benchmarks (
    benchmark_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Industry categorization
    industry_vertical TEXT NOT NULL,  -- 'ecommerce', 'saas', 'b2b', 'local', 'general'
    industry_sub_vertical TEXT,  -- More specific: 'fashion', 'electronics', 'services', etc.

    -- Platform context
    platform TEXT NOT NULL,  -- 'google_ads', 'meta_ads', 'ga4', 'shopify', 'unified'

    -- Metric identification
    metric_name TEXT NOT NULL,  -- 'ctr', 'cpc', 'roas', 'conversion_rate', 'bounce_rate', 'aov'
    metric_category TEXT,  -- 'performance', 'cost', 'conversion', 'engagement'

    -- Benchmark values
    benchmark_value REAL NOT NULL,
    benchmark_unit TEXT,  -- '%', 'currency', 'ratio', 'seconds'

    -- Benchmark ranges (for scoring)
    excellent_threshold REAL,  -- Top 10%
    good_threshold REAL,       -- Top 25%
    average_threshold REAL,    -- Median
    poor_threshold REAL,       -- Bottom 25%

    -- Data source and confidence
    data_source TEXT,  -- 'google', 'meta', 'industry_report', 'internal_data', 'manual'
    sample_size INTEGER,  -- Number of accounts/campaigns used to calculate benchmark
    confidence_score INTEGER DEFAULT 80,  -- 0-100

    -- Geographic context (optional)
    country_code TEXT DEFAULT 'ALL',  -- 'US', 'IN', 'ALL'
    currency TEXT DEFAULT 'USD',

    -- Validity period
    valid_from DATE NOT NULL,
    valid_until DATE,  -- NULL means still valid

    -- Metadata
    created_by TEXT DEFAULT 'system',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT,

    UNIQUE(industry_vertical, platform, metric_name, country_code, valid_from)
);

CREATE INDEX idx_benchmarks_industry ON industry_benchmarks(industry_vertical, platform);
CREATE INDEX idx_benchmarks_metric ON industry_benchmarks(metric_name);
CREATE INDEX idx_benchmarks_valid ON industry_benchmarks(valid_from, valid_until);


-- Seed initial benchmarks from current hardcoded values
INSERT OR IGNORE INTO industry_benchmarks
    (industry_vertical, platform, metric_name, metric_category, benchmark_value, benchmark_unit,
     excellent_threshold, good_threshold, average_threshold, poor_threshold,
     data_source, valid_from, country_code, currency)
VALUES
    -- Google Ads benchmarks
    ('general', 'google_ads', 'ctr', 'performance', 3.17, '%', 5.0, 4.0, 3.17, 2.0, 'google', '2024-01-01', 'ALL', 'USD'),
    ('general', 'google_ads', 'cpc', 'cost', 2.69, 'currency', 1.5, 2.0, 2.69, 4.0, 'google', '2024-01-01', 'ALL', 'USD'),
    ('general', 'google_ads', 'roas', 'performance', 2.0, 'ratio', 5.0, 3.5, 2.0, 1.0, 'google', '2024-01-01', 'ALL', 'USD'),
    ('general', 'google_ads', 'conversion_rate', 'conversion', 3.75, '%', 7.0, 5.0, 3.75, 2.0, 'google', '2024-01-01', 'ALL', 'USD'),

    -- GA4 benchmarks
    ('general', 'ga4', 'conversion_rate', 'conversion', 2.35, '%', 5.0, 3.5, 2.35, 1.0, 'google', '2024-01-01', 'ALL', 'USD'),
    ('general', 'ga4', 'bounce_rate', 'engagement', 45.0, '%', 25.0, 35.0, 45.0, 60.0, 'google', '2024-01-01', 'ALL', 'USD'),
    ('general', 'ga4', 'avg_session_duration', 'engagement', 120.0, 'seconds', 180.0, 150.0, 120.0, 60.0, 'google', '2024-01-01', 'ALL', 'USD'),
    ('general', 'ga4', 'pages_per_session', 'engagement', 2.5, 'ratio', 4.0, 3.0, 2.5, 1.5, 'google', '2024-01-01', 'ALL', 'USD'),

    -- Unified cross-platform benchmarks
    ('general', 'unified', 'blended_roas', 'performance', 2.5, 'ratio', 5.0, 3.5, 2.5, 1.5, 'internal_data', '2024-01-01', 'ALL', 'USD'),

    -- E-commerce specific benchmarks
    ('ecommerce', 'google_ads', 'roas', 'performance', 4.0, 'ratio', 8.0, 6.0, 4.0, 2.0, 'industry_report', '2024-01-01', 'ALL', 'USD'),
    ('ecommerce', 'shopify', 'aov', 'conversion', 3500.0, 'currency', 5000.0, 4000.0, 3500.0, 2000.0, 'industry_report', '2024-01-01', 'IN', 'INR'),
    ('ecommerce', 'shopify', 'conversion_rate', 'conversion', 2.5, '%', 5.0, 3.5, 2.5, 1.0, 'industry_report', '2024-01-01', 'ALL', 'USD'),
    ('ecommerce', 'shopify', 'repeat_purchase_rate', 'conversion', 30.0, '%', 50.0, 40.0, 30.0, 15.0, 'industry_report', '2024-01-01', 'ALL', 'USD');


-- ==============================================================================
-- FORECAST DATA TABLES
-- ==============================================================================

-- ML-based forecast predictions storage
CREATE TABLE IF NOT EXISTS ml_forecasts (
    forecast_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,

    -- Forecast target
    forecast_type TEXT NOT NULL,  -- 'spend', 'conversions', 'revenue', 'ctr', 'roas'
    forecast_level TEXT NOT NULL,  -- 'account', 'campaign', 'adgroup', 'keyword'

    -- Entity identification
    campaign_id TEXT,
    adgroup_id TEXT,
    keyword_id TEXT,
    platform_id INTEGER,

    -- Forecast period
    forecast_date DATE NOT NULL,
    forecast_horizon_days INTEGER,  -- How many days ahead this forecast is for

    -- Predicted values
    predicted_value REAL NOT NULL,
    predicted_lower_bound REAL,  -- 95% confidence interval lower
    predicted_upper_bound REAL,  -- 95% confidence interval upper

    -- Confidence metrics
    confidence_score REAL,  -- 0-100 (based on model performance)
    prediction_variance REAL,

    -- Model information
    model_type TEXT,  -- 'prophet', 'arima', 'sarima', 'linear_regression', 'lstm'
    model_version TEXT,
    model_accuracy_metrics TEXT,  -- JSON: {mape, rmse, mae, r2_score}

    -- Training data context
    training_data_points INTEGER,  -- Number of historical data points used
    training_period_start DATE,
    training_period_end DATE,
    training_data_quality_score REAL,  -- 0-100

    -- Seasonality and trends
    seasonal_component REAL,  -- Seasonal effect on this prediction
    trend_component REAL,     -- Trend effect on this prediction

    -- Metadata
    forecast_generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    forecast_updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Actual value (populated after forecast date passes - for model evaluation)
    actual_value REAL,
    actual_recorded_at TIMESTAMP,
    forecast_error REAL,  -- actual_value - predicted_value
    forecast_error_pct REAL,  -- (actual_value - predicted_value) / actual_value * 100

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (platform_id) REFERENCES dim_platform(platform_id),

    UNIQUE(customer_id, forecast_type, forecast_level, forecast_date, campaign_id, adgroup_id, keyword_id)
);

CREATE INDEX idx_forecasts_customer_date ON ml_forecasts(customer_id, forecast_date);
CREATE INDEX idx_forecasts_campaign ON ml_forecasts(campaign_id, forecast_date);
CREATE INDEX idx_forecasts_type ON ml_forecasts(forecast_type, forecast_level);
CREATE INDEX idx_forecasts_generated ON ml_forecasts(forecast_generated_at);


-- Forecast model performance tracking
CREATE TABLE IF NOT EXISTS forecast_model_performance (
    performance_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Model identification
    model_type TEXT NOT NULL,
    model_version TEXT NOT NULL,
    forecast_type TEXT NOT NULL,  -- 'spend', 'conversions', etc.

    -- Evaluation period
    evaluation_period_start DATE NOT NULL,
    evaluation_period_end DATE NOT NULL,

    -- Performance metrics
    mape REAL,  -- Mean Absolute Percentage Error
    rmse REAL,  -- Root Mean Squared Error
    mae REAL,   -- Mean Absolute Error
    r2_score REAL,  -- R-squared score

    -- Prediction counts
    total_predictions INTEGER,
    successful_predictions INTEGER,
    failed_predictions INTEGER,

    -- Confidence calibration
    avg_confidence_score REAL,
    confidence_vs_accuracy_correlation REAL,

    -- Metadata
    evaluated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_model_perf_type ON forecast_model_performance(model_type, forecast_type);
CREATE INDEX idx_model_perf_date ON forecast_model_performance(evaluation_period_start);


-- ==============================================================================
-- CUSTOMER-SPECIFIC BASELINES (for anomaly detection)
-- ==============================================================================

-- Customer-specific performance baselines (replaces generic thresholds)
CREATE TABLE IF NOT EXISTS customer_performance_baselines (
    baseline_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,

    -- Metric identification
    metric_name TEXT NOT NULL,
    metric_category TEXT,

    -- Platform/campaign context
    platform_id INTEGER,
    campaign_id TEXT,

    -- Baseline values (calculated from historical data)
    baseline_value REAL NOT NULL,
    baseline_mean REAL,
    baseline_median REAL,
    baseline_stddev REAL,
    baseline_min REAL,
    baseline_max REAL,

    -- Anomaly detection thresholds
    upper_control_limit REAL,  -- baseline_mean + (2 * stddev)
    lower_control_limit REAL,  -- baseline_mean - (2 * stddev)

    -- Calculation period
    calculation_period_start DATE NOT NULL,
    calculation_period_end DATE NOT NULL,
    data_points_count INTEGER,

    -- Validity
    is_active BOOLEAN DEFAULT 1,
    recalculate_after DATE,  -- When to recalculate baseline

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (customer_id) REFERENCES dim_customer(customer_id),
    FOREIGN KEY (platform_id) REFERENCES dim_platform(platform_id),

    UNIQUE(customer_id, metric_name, platform_id, campaign_id, calculation_period_start)
);

CREATE INDEX idx_baselines_customer ON customer_performance_baselines(customer_id, metric_name);
CREATE INDEX idx_baselines_active ON customer_performance_baselines(is_active, recalculate_after);


-- ==============================================================================
-- CONFIDENCE SCORE FACTORS TABLE
-- ==============================================================================

-- Factors that affect confidence score calculations
CREATE TABLE IF NOT EXISTS confidence_score_factors (
    factor_id INTEGER PRIMARY KEY AUTOINCREMENT,

    -- Factor identification
    factor_name TEXT NOT NULL UNIQUE,  -- 'data_completeness', 'sample_size', 'data_freshness', 'variance_stability'
    factor_category TEXT,  -- 'data_quality', 'statistical', 'temporal'

    -- Weight in overall confidence calculation
    factor_weight REAL DEFAULT 1.0,  -- Multiplier (0.0-1.0)

    -- Scoring function
    scoring_method TEXT,  -- 'linear', 'exponential', 'logarithmic', 'threshold'
    min_threshold REAL,  -- Minimum value for scoring
    max_threshold REAL,  -- Maximum value for scoring

    -- Configuration
    is_active BOOLEAN DEFAULT 1,
    description TEXT,

    -- Metadata
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Seed confidence score factors
INSERT OR IGNORE INTO confidence_score_factors
    (factor_name, factor_category, factor_weight, scoring_method, min_threshold, max_threshold, description)
VALUES
    ('data_completeness', 'data_quality', 1.0, 'linear', 0.0, 100.0, 'Percentage of expected data points present'),
    ('sample_size', 'statistical', 0.9, 'logarithmic', 10.0, 1000.0, 'Number of data points used in calculation'),
    ('data_freshness', 'temporal', 0.7, 'exponential', 0.0, 30.0, 'Days since last data update'),
    ('variance_stability', 'statistical', 0.8, 'linear', 0.0, 1.0, 'Coefficient of variation (lower is better)'),
    ('historical_depth', 'temporal', 0.6, 'logarithmic', 7.0, 365.0, 'Days of historical data available'),
    ('prediction_accuracy', 'statistical', 1.0, 'linear', 0.0, 100.0, 'Historical forecast accuracy percentage');


-- ==============================================================================
-- VIEWS FOR QUICK ACCESS
-- ==============================================================================

-- View: Week-over-Week comparison helper
CREATE VIEW IF NOT EXISTS view_wow_comparison AS
SELECT
    current.customer_id,
    current.campaign_id,
    current.metric_name,
    current.year,
    current.week_number,
    current.metric_value as current_value,
    previous.metric_value as previous_value,
    ROUND(((current.metric_value - previous.metric_value) / NULLIF(previous.metric_value, 0)) * 100, 2) as change_percentage,
    CASE
        WHEN current.metric_value > previous.metric_value THEN 'increase'
        WHEN current.metric_value < previous.metric_value THEN 'decrease'
        ELSE 'no_change'
    END as change_direction
FROM metrics_historical_aggregates current
LEFT JOIN metrics_historical_aggregates previous
    ON current.customer_id = previous.customer_id
    AND current.metric_name = previous.metric_name
    AND current.campaign_id = previous.campaign_id
    AND current.period_type = 'weekly'
    AND previous.period_type = 'weekly'
    AND previous.week_number = (current.week_number - 1)
    AND previous.year = current.year
WHERE current.period_type = 'weekly';


-- View: Active benchmarks lookup
CREATE VIEW IF NOT EXISTS view_active_benchmarks AS
SELECT
    industry_vertical,
    platform,
    metric_name,
    benchmark_value,
    benchmark_unit,
    excellent_threshold,
    good_threshold,
    average_threshold,
    poor_threshold,
    confidence_score,
    country_code,
    currency
FROM industry_benchmarks
WHERE (valid_until IS NULL OR valid_until >= DATE('now'))
    AND valid_from <= DATE('now');


-- View: Latest forecasts with confidence
CREATE VIEW IF NOT EXISTS view_latest_forecasts AS
SELECT
    customer_id,
    campaign_id,
    forecast_type,
    forecast_date,
    predicted_value,
    predicted_lower_bound,
    predicted_upper_bound,
    confidence_score,
    model_type,
    training_data_points,
    training_data_quality_score,
    forecast_generated_at
FROM ml_forecasts
WHERE forecast_date >= DATE('now')
    AND forecast_generated_at = (
        SELECT MAX(forecast_generated_at)
        FROM ml_forecasts f2
        WHERE f2.customer_id = ml_forecasts.customer_id
            AND f2.campaign_id = ml_forecasts.campaign_id
            AND f2.forecast_type = ml_forecasts.forecast_type
            AND f2.forecast_date = ml_forecasts.forecast_date
    );


-- ==============================================================================
-- END OF ENHANCEMENTS
-- ==============================================================================
