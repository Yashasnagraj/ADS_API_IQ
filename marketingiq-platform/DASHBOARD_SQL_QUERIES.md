# 📊 Marketing Warehouse SQL Queries for Agent Dashboards

**Database:** `marketing_warehouse.db`
**Note:** All monetary values stored in micros (÷ 1,000,000 for actual value)
**Date Format:** YYYYMMDD (e.g., '20250101')

---

## 🗂️ Table of Contents

1. [Data Agent Queries](#data-agent-queries)
2. [Insight Agent Queries](#insight-agent-queries)
3. [Optimization Agent Queries](#optimization-agent-queries)
4. [Forecasting Agent Queries](#forecasting-agent-queries)
5. [Alert Agent Queries](#alert-agent-queries)

---

# DATA AGENT QUERIES

## 1. Campaigns Dashboard

### Get All Campaigns with Performance Metrics

```sql
-- Fetch campaigns with aggregated performance for date range
SELECT
    gc.google_campaign_id,
    gc.campaign_id,
    gc.campaign_name,
    gc.status,
    gc.campaign_type,
    gc.bidding_strategy_type,
    gc.budget_amount_micros / 1000000.0 AS budget,

    -- Aggregated performance metrics
    SUM(fp.impressions) AS impressions,
    SUM(fp.clicks) AS clicks,
    SUM(fp.spend_micros) / 1000000.0 AS cost,
    SUM(fp.conversions) AS conversions,
    SUM(fp.conversion_value_micros) / 1000000.0 AS conversion_value,

    -- Calculated metrics
    CASE
        WHEN SUM(fp.impressions) > 0
        THEN (SUM(fp.clicks) * 100.0 / SUM(fp.impressions))
        ELSE 0
    END AS ctr,

    CASE
        WHEN SUM(fp.clicks) > 0
        THEN (SUM(fp.spend_micros) / 1000000.0 / SUM(fp.clicks))
        ELSE 0
    END AS cpc,

    CASE
        WHEN SUM(fp.conversions) > 0
        THEN (SUM(fp.spend_micros) / 1000000.0 / SUM(fp.conversions))
        ELSE 0
    END AS cpa,

    CASE
        WHEN SUM(fp.clicks) > 0
        THEN (SUM(fp.conversions) * 100.0 / SUM(fp.clicks))
        ELSE 0
    END AS conversion_rate,

    CASE
        WHEN SUM(fp.spend_micros) > 0
        THEN (SUM(fp.conversion_value_micros) * 1.0 / SUM(fp.spend_micros))
        ELSE 0
    END AS roas,

    -- Budget utilization
    CASE
        WHEN gc.budget_amount_micros > 0
        THEN (SUM(fp.spend_micros) * 100.0 / gc.budget_amount_micros)
        ELSE 0
    END AS budget_used_percent

FROM dim_google_ads_campaign gc
LEFT JOIN fact_campaign_performance_daily fp
    ON gc.google_campaign_id = fp.google_campaign_id
    AND fp.date_id BETWEEN :start_date AND :end_date

WHERE gc.customer_id = :customer_id
    AND (:include_paused = 1 OR gc.status = 'ENABLED')
    AND (:campaign_type = 'ALL' OR gc.channel_type = :campaign_type)

GROUP BY gc.google_campaign_id

ORDER BY cost DESC;
```

### Get Campaign Performance Over Time (for charts)

```sql
-- Daily performance trend
SELECT
    fp.date_id,
    DATE(
        SUBSTR(fp.date_id, 1, 4) || '-' ||
        SUBSTR(fp.date_id, 5, 2) || '-' ||
        SUBSTR(fp.date_id, 7, 2)
    ) AS date,
    SUM(fp.impressions) AS impressions,
    SUM(fp.clicks) AS clicks,
    SUM(fp.spend_micros) / 1000000.0 AS cost,
    SUM(fp.conversions) AS conversions,

    CASE
        WHEN SUM(fp.impressions) > 0
        THEN (SUM(fp.clicks) * 100.0 / SUM(fp.impressions))
        ELSE 0
    END AS ctr,

    CASE
        WHEN SUM(fp.clicks) > 0
        THEN (SUM(fp.spend_micros) / 1000000.0 / SUM(fp.clicks))
        ELSE 0
    END AS cpc

FROM fact_campaign_performance_daily fp
WHERE fp.customer_id = :customer_id
    AND fp.date_id BETWEEN :start_date AND :end_date
GROUP BY fp.date_id
ORDER BY fp.date_id ASC;
```

### Get Top/Bottom Performers

```sql
-- Top 5 campaigns by conversions
SELECT
    gc.campaign_name,
    SUM(fp.conversions) AS conversions,
    SUM(fp.spend_micros) / 1000000.0 AS cost,
    CASE
        WHEN SUM(fp.spend_micros) > 0
        THEN (SUM(fp.conversions) * 1000000.0 / SUM(fp.spend_micros))
        ELSE 0
    END AS efficiency_score
FROM dim_google_ads_campaign gc
JOIN fact_campaign_performance_daily fp
    ON gc.google_campaign_id = fp.google_campaign_id
WHERE gc.customer_id = :customer_id
    AND fp.date_id BETWEEN :start_date AND :end_date
    AND gc.status = 'ENABLED'
GROUP BY gc.google_campaign_id
ORDER BY conversions DESC
LIMIT 5;
```

---

## 2. Ad Groups Dashboard

```sql
-- Fetch ad groups with performance
SELECT
    ag.ad_group_id,
    ag.adgroup_id,
    ag.adgroup_name,
    ag.status,
    gc.campaign_name,
    ag.cpc_bid_micros / 1000000.0 AS cpc_bid,

    -- Aggregated metrics from keyword performance
    SUM(kp.impressions) AS impressions,
    SUM(kp.clicks) AS clicks,
    SUM(kp.cost_micros) / 1000000.0 AS cost,
    SUM(kp.conversions) AS conversions,

    -- Calculated metrics
    CASE
        WHEN SUM(kp.impressions) > 0
        THEN (SUM(kp.clicks) * 100.0 / SUM(kp.impressions))
        ELSE 0
    END AS ctr,

    CASE
        WHEN SUM(kp.clicks) > 0
        THEN (SUM(kp.cost_micros) / 1000000.0 / SUM(kp.clicks))
        ELSE 0
    END AS cpc,

    AVG(kp.quality_score) AS avg_quality_score

FROM dim_ad_group ag
JOIN dim_google_ads_campaign gc
    ON ag.google_campaign_id = gc.google_campaign_id
LEFT JOIN fact_keyword_performance_daily kp
    ON ag.ad_group_id = kp.ad_group_id
    AND kp.date_id BETWEEN :start_date AND :end_date

WHERE ag.customer_id = :customer_id
    AND (:campaign_ids IS NULL OR gc.google_campaign_id IN (:campaign_ids))

GROUP BY ag.ad_group_id

ORDER BY cost DESC;
```

---

## 3. Keywords Dashboard

```sql
-- Fetch keywords with performance and quality scores
SELECT
    k.keyword_id,
    k.keyword_text,
    k.match_type,
    k.status,
    k.quality_score,
    k.cpc_bid_micros / 1000000.0 AS cpc_bid,

    ag.adgroup_name,
    gc.campaign_name,

    -- Aggregated performance
    SUM(kp.impressions) AS impressions,
    SUM(kp.clicks) AS clicks,
    SUM(kp.cost_micros) / 1000000.0 AS cost,
    SUM(kp.conversions) AS conversions,
    AVG(kp.avg_position) AS avg_position,
    AVG(kp.search_impression_share) AS search_impression_share,

    -- Calculated metrics
    CASE
        WHEN SUM(kp.impressions) > 0
        THEN (SUM(kp.clicks) * 100.0 / SUM(kp.impressions))
        ELSE 0
    END AS ctr,

    CASE
        WHEN SUM(kp.clicks) > 0
        THEN (SUM(kp.cost_micros) / 1000000.0 / SUM(kp.clicks))
        ELSE 0
    END AS cpc,

    CASE
        WHEN SUM(kp.clicks) > 0
        THEN (SUM(kp.conversions) * 100.0 / SUM(kp.clicks))
        ELSE 0
    END AS conversion_rate,

    CASE
        WHEN SUM(kp.conversions) > 0
        THEN (SUM(kp.cost_micros) / 1000000.0 / SUM(kp.conversions))
        ELSE 0
    END AS cpa

FROM dim_keyword k
JOIN dim_ad_group ag ON k.ad_group_id = ag.ad_group_id
JOIN dim_google_ads_campaign gc ON k.google_campaign_id = gc.google_campaign_id
LEFT JOIN fact_keyword_performance_daily kp
    ON k.keyword_id = kp.keyword_id
    AND kp.date_id BETWEEN :start_date AND :end_date

WHERE k.customer_id = :customer_id
    AND (:min_impressions = 0 OR kp.impressions >= :min_impressions)
    AND (:adgroup_ids IS NULL OR k.ad_group_id IN (:adgroup_ids))

GROUP BY k.keyword_id

ORDER BY cost DESC;
```

### Keywords by Quality Score Distribution

```sql
-- Quality score distribution
SELECT
    k.quality_score,
    COUNT(*) AS keyword_count,
    SUM(kp.impressions) AS total_impressions,
    SUM(kp.cost_micros) / 1000000.0 AS total_cost,
    AVG(kp.ctr) AS avg_ctr

FROM dim_keyword k
LEFT JOIN fact_keyword_performance_daily kp
    ON k.keyword_id = kp.keyword_id
    AND kp.date_id BETWEEN :start_date AND :end_date

WHERE k.customer_id = :customer_id
    AND k.quality_score IS NOT NULL

GROUP BY k.quality_score
ORDER BY k.quality_score DESC;
```

---

## 4. Search Terms Dashboard

### Note: Search terms not in current schema
### Would need: `fact_search_terms_daily` table
### Placeholder query structure:

```sql
-- If search terms table exists
SELECT
    st.search_term,
    st.keyword_text,
    st.match_type,
    SUM(st.impressions) AS impressions,
    SUM(st.clicks) AS clicks,
    SUM(st.cost_micros) / 1000000.0 AS cost,
    SUM(st.conversions) AS conversions,

    CASE
        WHEN SUM(st.impressions) > 0
        THEN (SUM(st.clicks) * 100.0 / SUM(st.impressions))
        ELSE 0
    END AS ctr,

    CASE
        WHEN SUM(st.clicks) > 0
        THEN (SUM(st.cost_micros) / 1000000.0 / SUM(st.clicks))
        ELSE 0
    END AS cpc

FROM fact_search_terms_daily st
WHERE st.customer_id = :customer_id
    AND st.date_id BETWEEN :start_date AND :end_date
GROUP BY st.search_term
ORDER BY impressions DESC;
```

---

## 5. ML Features Dashboard

### Feature Engineering for Campaigns

```sql
-- ML features for campaigns
SELECT
    gc.google_campaign_id AS entity_id,
    gc.campaign_name AS entity_name,
    'campaign' AS entity_type,

    -- Time-based features
    CAST(JULIANDAY('now') - JULIANDAY(gc.start_date) AS INTEGER) AS days_active,

    -- Performance features (last 30 days)
    SUM(fp.impressions) AS impressions_30d,
    SUM(fp.clicks) AS clicks_30d,
    SUM(fp.spend_micros) / 1000000.0 AS spend_30d,
    SUM(fp.conversions) AS conversions_30d,

    -- Trend features (7d vs 30d)
    (SELECT SUM(clicks) FROM fact_campaign_performance_daily
     WHERE google_campaign_id = gc.google_campaign_id
     AND date_id >= :last_7d_start) * 1.0 / NULLIF(SUM(fp.clicks), 0) AS click_trend_7d_vs_30d,

    -- Volatility (coefficient of variation)
    (STDEV(fp.spend_micros) * 100.0 / AVG(NULLIF(fp.spend_micros, 0))) AS spend_cv,

    -- Quality indicators
    AVG(fp.ctr) AS avg_ctr,
    AVG(fp.roas) AS avg_roas,

    -- Budget features
    CASE
        WHEN gc.budget_amount_micros > 0
        THEN (SUM(fp.spend_micros) * 100.0 / gc.budget_amount_micros)
        ELSE 0
    END AS budget_utilization

FROM dim_google_ads_campaign gc
LEFT JOIN fact_campaign_performance_daily fp
    ON gc.google_campaign_id = fp.google_campaign_id
    AND fp.date_id >= :last_30d_start

WHERE gc.customer_id = :customer_id

GROUP BY gc.google_campaign_id;
```

### Feature Engineering for Keywords

```sql
-- ML features for keywords
SELECT
    k.keyword_id AS entity_id,
    k.keyword_text AS entity_name,
    'keyword' AS entity_type,

    -- Keyword attributes
    k.match_type,
    k.quality_score,
    LENGTH(k.keyword_text) AS keyword_length,
    (LENGTH(k.keyword_text) - LENGTH(REPLACE(k.keyword_text, ' ', '')) + 1) AS word_count,

    -- Performance features
    SUM(kp.impressions) AS impressions_30d,
    SUM(kp.clicks) AS clicks_30d,
    SUM(kp.cost_micros) / 1000000.0 AS cost_30d,
    SUM(kp.conversions) AS conversions_30d,

    AVG(kp.avg_position) AS avg_position,
    AVG(kp.search_impression_share) AS impression_share,
    AVG(kp.ctr) AS avg_ctr,
    AVG(kp.cpc_micros) / 1000000.0 AS avg_cpc,

    -- Trend indicators
    (SELECT AVG(ctr) FROM fact_keyword_performance_daily
     WHERE keyword_id = k.keyword_id
     AND date_id >= :last_7d_start) - AVG(kp.ctr) AS ctr_change_7d

FROM dim_keyword k
LEFT JOIN fact_keyword_performance_daily kp
    ON k.keyword_id = kp.keyword_id
    AND kp.date_id >= :last_30d_start

WHERE k.customer_id = :customer_id

GROUP BY k.keyword_id;
```

---

# INSIGHT AGENT QUERIES

## 1. Campaign Performance Analysis

### Overall Campaign Metrics

```sql
-- Campaign performance summary
SELECT
    COUNT(DISTINCT gc.google_campaign_id) AS total_campaigns,
    COUNT(DISTINCT CASE WHEN gc.status = 'ENABLED' THEN gc.google_campaign_id END) AS active_campaigns,
    COUNT(DISTINCT CASE WHEN gc.status = 'PAUSED' THEN gc.google_campaign_id END) AS paused_campaigns,

    SUM(fp.impressions) AS total_impressions,
    SUM(fp.clicks) AS total_clicks,
    SUM(fp.spend_micros) / 1000000.0 AS total_cost,
    SUM(fp.conversions) AS total_conversions,
    SUM(fp.conversion_value_micros) / 1000000.0 AS total_conversion_value,

    AVG(fp.ctr) AS avg_ctr,
    AVG(fp.cpc_micros) / 1000000.0 AS avg_cpc,

    CASE
        WHEN SUM(fp.spend_micros) > 0
        THEN (SUM(fp.conversion_value_micros) * 1.0 / SUM(fp.spend_micros))
        ELSE 0
    END AS overall_roas

FROM dim_google_ads_campaign gc
LEFT JOIN fact_campaign_performance_daily fp
    ON gc.google_campaign_id = fp.google_campaign_id
    AND fp.date_id BETWEEN :start_date AND :end_date

WHERE gc.customer_id = :customer_id;
```

### Top Performers Identification

```sql
-- Top 10 performing campaigns (by ROAS)
SELECT
    gc.campaign_name,
    SUM(fp.spend_micros) / 1000000.0 AS cost,
    SUM(fp.conversions) AS conversions,
    SUM(fp.conversion_value_micros) / 1000000.0 AS conversion_value,
    CASE
        WHEN SUM(fp.spend_micros) > 0
        THEN (SUM(fp.conversion_value_micros) * 1.0 / SUM(fp.spend_micros))
        ELSE 0
    END AS roas,
    'top_performer' AS category

FROM dim_google_ads_campaign gc
JOIN fact_campaign_performance_daily fp
    ON gc.google_campaign_id = fp.google_campaign_id

WHERE gc.customer_id = :customer_id
    AND fp.date_id BETWEEN :start_date AND :end_date
    AND gc.status = 'ENABLED'
    AND fp.conversions > 0

GROUP BY gc.google_campaign_id
ORDER BY roas DESC
LIMIT 10;
```

### Underperformers Identification

```sql
-- Bottom 10 campaigns (high spend, low ROAS)
SELECT
    gc.campaign_name,
    SUM(fp.spend_micros) / 1000000.0 AS cost,
    SUM(fp.conversions) AS conversions,
    AVG(fp.ctr) AS ctr,
    CASE
        WHEN SUM(fp.spend_micros) > 0
        THEN (SUM(fp.conversion_value_micros) * 1.0 / SUM(fp.spend_micros))
        ELSE 0
    END AS roas,
    'underperformer' AS category,
    CASE
        WHEN AVG(fp.ctr) < 2.0 THEN 'Low CTR'
        WHEN SUM(fp.conversions) = 0 THEN 'No Conversions'
        WHEN roas < 2.0 THEN 'Poor ROAS'
        ELSE 'High Spend'
    END AS issue_type

FROM dim_google_ads_campaign gc
JOIN fact_campaign_performance_daily fp
    ON gc.google_campaign_id = fp.google_campaign_id

WHERE gc.customer_id = :customer_id
    AND fp.date_id BETWEEN :start_date AND :end_date
    AND gc.status = 'ENABLED'
    AND fp.spend_micros > 1000000 -- At least $1 spent

GROUP BY gc.google_campaign_id
HAVING roas < 2.0 OR SUM(fp.conversions) = 0
ORDER BY cost DESC
LIMIT 10;
```

---

## 2. Keyword Performance Analysis

### High-Value Keywords

```sql
-- High-performing keywords
SELECT
    k.keyword_text,
    k.match_type,
    k.quality_score,
    ag.adgroup_name,
    gc.campaign_name,

    SUM(kp.impressions) AS impressions,
    SUM(kp.clicks) AS clicks,
    SUM(kp.cost_micros) / 1000000.0 AS cost,
    SUM(kp.conversions) AS conversions,
    AVG(kp.ctr) AS ctr,

    CASE
        WHEN SUM(kp.clicks) > 0
        THEN (SUM(kp.cost_micros) / 1000000.0 / SUM(kp.clicks))
        ELSE 0
    END AS cpc,

    'high_value' AS category

FROM dim_keyword k
JOIN dim_ad_group ag ON k.ad_group_id = ag.ad_group_id
JOIN dim_google_ads_campaign gc ON k.google_campaign_id = gc.google_campaign_id
JOIN fact_keyword_performance_daily kp
    ON k.keyword_id = kp.keyword_id

WHERE k.customer_id = :customer_id
    AND kp.date_id BETWEEN :start_date AND :end_date
    AND k.status = 'ENABLED'
    AND k.quality_score >= 7
    AND kp.conversions > 0

GROUP BY k.keyword_id
ORDER BY conversions DESC, ctr DESC
LIMIT 20;
```

### Low Quality Keywords (Candidates for Pause/Negative)

```sql
-- Low-quality keywords wasting budget
SELECT
    k.keyword_text,
    k.match_type,
    k.quality_score,

    SUM(kp.impressions) AS impressions,
    SUM(kp.clicks) AS clicks,
    SUM(kp.cost_micros) / 1000000.0 AS cost,
    SUM(kp.conversions) AS conversions,
    AVG(kp.ctr) AS ctr,
    AVG(kp.avg_position) AS avg_position,

    'low_quality' AS category,
    CASE
        WHEN k.quality_score < 5 THEN 'Poor Quality Score'
        WHEN AVG(kp.ctr) < 1.0 THEN 'Very Low CTR'
        WHEN SUM(kp.conversions) = 0 AND cost > 10 THEN 'No Conversions'
        ELSE 'High Cost, Low Performance'
    END AS issue

FROM dim_keyword k
JOIN fact_keyword_performance_daily kp
    ON k.keyword_id = kp.keyword_id

WHERE k.customer_id = :customer_id
    AND kp.date_id BETWEEN :start_date AND :end_date
    AND k.status = 'ENABLED'
    AND (
        k.quality_score < 5
        OR (kp.cost_micros > 10000000 AND kp.conversions = 0)
    )

GROUP BY k.keyword_id
ORDER BY cost DESC
LIMIT 20;
```

---

## 3. Anomaly Detection

### Statistical Anomaly Detection (Z-Score Method)

```sql
-- Detect campaigns with anomalous performance
WITH campaign_stats AS (
    SELECT
        gc.google_campaign_id,
        gc.campaign_name,
        fp.date_id,
        fp.impressions,
        fp.clicks,
        fp.spend_micros / 1000000.0 AS cost,
        fp.conversions,
        fp.ctr
    FROM dim_google_ads_campaign gc
    JOIN fact_campaign_performance_daily fp
        ON gc.google_campaign_id = fp.google_campaign_id
    WHERE gc.customer_id = :customer_id
        AND fp.date_id BETWEEN :start_date AND :end_date
        AND gc.status = 'ENABLED'
),
aggregated_stats AS (
    SELECT
        google_campaign_id,
        campaign_name,
        AVG(cost) AS avg_cost,
        STDEV(cost) AS stddev_cost,
        AVG(ctr) AS avg_ctr,
        STDEV(ctr) AS stddev_ctr,
        AVG(conversions) AS avg_conversions,
        STDEV(conversions) AS stddev_conversions
    FROM campaign_stats
    GROUP BY google_campaign_id
)
SELECT
    cs.campaign_name,
    cs.date_id,
    cs.cost AS actual_cost,
    ast.avg_cost AS expected_cost,
    (cs.cost - ast.avg_cost) / NULLIF(ast.stddev_cost, 0) AS cost_z_score,

    cs.ctr AS actual_ctr,
    ast.avg_ctr AS expected_ctr,
    (cs.ctr - ast.avg_ctr) / NULLIF(ast.stddev_ctr, 0) AS ctr_z_score,

    CASE
        WHEN ABS((cs.cost - ast.avg_cost) / NULLIF(ast.stddev_cost, 0)) > 2 THEN 'High'
        WHEN ABS((cs.cost - ast.avg_cost) / NULLIF(ast.stddev_cost, 0)) > 1.5 THEN 'Medium'
        ELSE 'Low'
    END AS severity,

    CASE
        WHEN (cs.cost - ast.avg_cost) / NULLIF(ast.stddev_cost, 0) > 2 THEN 'Cost Spike'
        WHEN (cs.cost - ast.avg_cost) / NULLIF(ast.stddev_cost, 0) < -2 THEN 'Cost Drop'
        WHEN (cs.ctr - ast.avg_ctr) / NULLIF(ast.stddev_ctr, 0) < -2 THEN 'CTR Drop'
        WHEN (cs.conversions - ast.avg_conversions) / NULLIF(ast.stddev_conversions, 0) < -2 THEN 'Conversion Drop'
        ELSE 'Normal'
    END AS anomaly_type

FROM campaign_stats cs
JOIN aggregated_stats ast ON cs.google_campaign_id = ast.google_campaign_id

WHERE ABS((cs.cost - ast.avg_cost) / NULLIF(ast.stddev_cost, 0)) > :sensitivity
   OR ABS((cs.ctr - ast.avg_ctr) / NULLIF(ast.stddev_ctr, 0)) > :sensitivity

ORDER BY ABS(cost_z_score) DESC
LIMIT 50;
```

### Day-over-Day Change Detection

```sql
-- Detect significant day-over-day changes
WITH daily_metrics AS (
    SELECT
        gc.campaign_name,
        fp.date_id,
        fp.spend_micros / 1000000.0 AS cost,
        fp.ctr,
        fp.conversions,
        LAG(fp.spend_micros / 1000000.0) OVER (
            PARTITION BY gc.google_campaign_id ORDER BY fp.date_id
        ) AS prev_cost,
        LAG(fp.ctr) OVER (
            PARTITION BY gc.google_campaign_id ORDER BY fp.date_id
        ) AS prev_ctr,
        LAG(fp.conversions) OVER (
            PARTITION BY gc.google_campaign_id ORDER BY fp.date_id
        ) AS prev_conversions
    FROM dim_google_ads_campaign gc
    JOIN fact_campaign_performance_daily fp
        ON gc.google_campaign_id = fp.google_campaign_id
    WHERE gc.customer_id = :customer_id
        AND fp.date_id BETWEEN :start_date AND :end_date
)
SELECT
    campaign_name,
    date_id,
    cost,
    prev_cost,
    ((cost - prev_cost) * 100.0 / NULLIF(prev_cost, 0)) AS cost_change_pct,

    ctr,
    prev_ctr,
    ((ctr - prev_ctr) * 100.0 / NULLIF(prev_ctr, 0)) AS ctr_change_pct,

    conversions,
    prev_conversions,
    (conversions - prev_conversions) AS conversion_change,

    CASE
        WHEN ABS((cost - prev_cost) * 100.0 / NULLIF(prev_cost, 0)) > 50 THEN 'Cost Anomaly'
        WHEN ABS((ctr - prev_ctr) * 100.0 / NULLIF(prev_ctr, 0)) > 30 THEN 'CTR Anomaly'
        WHEN ABS(conversions - prev_conversions) > 5 THEN 'Conversion Anomaly'
        ELSE 'Normal'
    END AS anomaly_type

FROM daily_metrics

WHERE prev_cost IS NOT NULL
    AND (
        ABS((cost - prev_cost) * 100.0 / NULLIF(prev_cost, 0)) > 50
        OR ABS((ctr - prev_ctr) * 100.0 / NULLIF(prev_ctr, 0)) > 30
        OR ABS(conversions - prev_conversions) > 5
    )

ORDER BY date_id DESC, ABS(cost_change_pct) DESC;
```

---

## 4. Performance Trends Analysis

```sql
-- 7-day vs 30-day trend comparison
WITH metrics_7d AS (
    SELECT
        customer_id,
        AVG(spend_micros) / 1000000.0 AS avg_cost_7d,
        AVG(ctr) AS avg_ctr_7d,
        AVG(conversions) AS avg_conversions_7d
    FROM fact_campaign_performance_daily
    WHERE customer_id = :customer_id
        AND date_id >= :last_7d_start
),
metrics_30d AS (
    SELECT
        customer_id,
        AVG(spend_micros) / 1000000.0 AS avg_cost_30d,
        AVG(ctr) AS avg_ctr_30d,
        AVG(conversions) AS avg_conversions_30d
    FROM fact_campaign_performance_daily
    WHERE customer_id = :customer_id
        AND date_id >= :last_30d_start
)
SELECT
    m7.avg_cost_7d,
    m30.avg_cost_30d,
    ((m7.avg_cost_7d - m30.avg_cost_30d) * 100.0 / NULLIF(m30.avg_cost_30d, 0)) AS cost_trend_pct,

    m7.avg_ctr_7d,
    m30.avg_ctr_30d,
    ((m7.avg_ctr_7d - m30.avg_ctr_30d) * 100.0 / NULLIF(m30.avg_ctr_30d, 0)) AS ctr_trend_pct,

    m7.avg_conversions_7d,
    m30.avg_conversions_30d,
    ((m7.avg_conversions_7d - m30.avg_conversions_30d) * 100.0 / NULLIF(m30.avg_conversions_30d, 0)) AS conversion_trend_pct,

    CASE
        WHEN ((m7.avg_cost_7d - m30.avg_cost_30d) / NULLIF(m30.avg_cost_30d, 0)) > 0.1 THEN 'Increasing Spend'
        WHEN ((m7.avg_cost_7d - m30.avg_cost_30d) / NULLIF(m30.avg_cost_30d, 0)) < -0.1 THEN 'Decreasing Spend'
        ELSE 'Stable Spend'
    END AS spend_trend,

    CASE
        WHEN ((m7.avg_ctr_7d - m30.avg_ctr_30d) / NULLIF(m30.avg_ctr_30d, 0)) > 0.1 THEN 'Improving CTR'
        WHEN ((m7.avg_ctr_7d - m30.avg_ctr_30d) / NULLIF(m30.avg_ctr_30d, 0)) < -0.1 THEN 'Declining CTR'
        ELSE 'Stable CTR'
    END AS ctr_trend

FROM metrics_7d m7
CROSS JOIN metrics_30d m30;
```

---

## 5. ROI Analysis

```sql
-- Profitability analysis by campaign
SELECT
    gc.campaign_name,
    gc.campaign_type,

    SUM(fp.spend_micros) / 1000000.0 AS total_cost,
    SUM(fp.conversions) AS total_conversions,
    SUM(fp.conversion_value_micros) / 1000000.0 AS total_revenue,

    (SUM(fp.conversion_value_micros) - SUM(fp.spend_micros)) / 1000000.0 AS profit,

    CASE
        WHEN SUM(fp.spend_micros) > 0
        THEN ((SUM(fp.conversion_value_micros) - SUM(fp.spend_micros)) * 100.0 / SUM(fp.spend_micros))
        ELSE 0
    END AS roi_percentage,

    CASE
        WHEN SUM(fp.spend_micros) > 0
        THEN (SUM(fp.conversion_value_micros) * 1.0 / SUM(fp.spend_micros))
        ELSE 0
    END AS roas,

    CASE
        WHEN (SUM(fp.conversion_value_micros) - SUM(fp.spend_micros)) > 0 THEN 'Profitable'
        WHEN (SUM(fp.conversion_value_micros) - SUM(fp.spend_micros)) < 0 THEN 'Unprofitable'
        ELSE 'Break Even'
    END AS profitability_status

FROM dim_google_ads_campaign gc
JOIN fact_campaign_performance_daily fp
    ON gc.google_campaign_id = fp.google_campaign_id

WHERE gc.customer_id = :customer_id
    AND fp.date_id BETWEEN :start_date AND :end_date
    AND gc.status = 'ENABLED'

GROUP BY gc.google_campaign_id

ORDER BY profit DESC;
```

---

# OPTIMIZATION AGENT QUERIES

## 1. Budget Optimization

### Budget Reallocation Recommendations

```sql
-- Identify campaigns for budget reallocation
WITH campaign_efficiency AS (
    SELECT
        gc.google_campaign_id,
        gc.campaign_name,
        gc.budget_amount_micros / 1000000.0 AS current_budget,

        SUM(fp.spend_micros) / 1000000.0 AS actual_spend,
        SUM(fp.conversions) AS conversions,
        SUM(fp.conversion_value_micros) / 1000000.0 AS revenue,

        CASE
            WHEN SUM(fp.spend_micros) > 0
            THEN (SUM(fp.conversions) * 1000000.0 / SUM(fp.spend_micros))
            ELSE 0
        END AS efficiency_score,

        CASE
            WHEN SUM(fp.spend_micros) > 0
            THEN (SUM(fp.conversion_value_micros) * 1.0 / SUM(fp.spend_micros))
            ELSE 0
        END AS roas,

        CASE
            WHEN gc.budget_amount_micros > 0
            THEN (SUM(fp.spend_micros) * 100.0 / gc.budget_amount_micros)
            ELSE 0
        END AS budget_utilization_pct

    FROM dim_google_ads_campaign gc
    JOIN fact_campaign_performance_daily fp
        ON gc.google_campaign_id = fp.google_campaign_id
    WHERE gc.customer_id = :customer_id
        AND fp.date_id BETWEEN :start_date AND :end_date
        AND gc.status = 'ENABLED'
    GROUP BY gc.google_campaign_id
),
avg_efficiency AS (
    SELECT AVG(efficiency_score) AS avg_efficiency
    FROM campaign_efficiency
)
SELECT
    ce.campaign_name,
    ce.current_budget,
    ce.actual_spend,
    ce.conversions,
    ce.efficiency_score,
    ce.roas,
    ce.budget_utilization_pct,

    -- Recommendation logic
    CASE
        WHEN ce.efficiency_score > ae.avg_efficiency * 1.5 AND ce.budget_utilization_pct > 80
            THEN 'Increase'
        WHEN ce.efficiency_score < ae.avg_efficiency * 0.5 AND ce.conversions > 0
            THEN 'Decrease'
        WHEN ce.roas < 2.0 AND ce.actual_spend > 50
            THEN 'Pause'
        ELSE 'Maintain'
    END AS recommendation,

    -- Suggested budget change (max ±30%)
    CASE
        WHEN ce.efficiency_score > ae.avg_efficiency * 1.5 AND ce.budget_utilization_pct > 80
            THEN ce.current_budget * 1.25
        WHEN ce.efficiency_score < ae.avg_efficiency * 0.5 AND ce.conversions > 0
            THEN ce.current_budget * 0.80
        WHEN ce.roas < 2.0 AND ce.actual_spend > 50
            THEN 0
        ELSE ce.current_budget
    END AS suggested_budget,

    CASE
        WHEN ce.efficiency_score > ae.avg_efficiency * 1.5 THEN 'High'
        WHEN ce.efficiency_score > ae.avg_efficiency * 1.2 THEN 'Medium'
        ELSE 'Low'
    END AS priority,

    -- Estimated impact
    CASE
        WHEN ce.efficiency_score > ae.avg_efficiency * 1.5 AND ce.budget_utilization_pct > 80
            THEN ce.conversions * 0.20
        WHEN ce.efficiency_score < ae.avg_efficiency * 0.5
            THEN ce.conversions * -0.10
        ELSE 0
    END AS estimated_conversion_impact

FROM campaign_efficiency ce
CROSS JOIN avg_efficiency ae

WHERE ce.recommendation != 'Maintain'

ORDER BY priority DESC, estimated_conversion_impact DESC;
```

---

## 2. Keyword Bid Optimization

```sql
-- Bid adjustment recommendations for keywords
WITH keyword_performance AS (
    SELECT
        k.keyword_id,
        k.keyword_text,
        k.match_type,
        k.quality_score,
        k.cpc_bid_micros / 1000000.0 AS current_bid,

        SUM(kp.impressions) AS impressions,
        SUM(kp.clicks) AS clicks,
        SUM(kp.cost_micros) / 1000000.0 AS cost,
        SUM(kp.conversions) AS conversions,
        AVG(kp.avg_position) AS avg_position,

        CASE
            WHEN SUM(kp.clicks) > 0
            THEN (SUM(kp.cost_micros) / 1000000.0 / SUM(kp.clicks))
            ELSE 0
        END AS actual_cpc,

        CASE
            WHEN SUM(kp.impressions) > 0
            THEN (SUM(kp.clicks) * 100.0 / SUM(kp.impressions))
            ELSE 0
        END AS ctr,

        CASE
            WHEN SUM(kp.clicks) > 0
            THEN (SUM(kp.conversions) * 100.0 / SUM(kp.clicks))
            ELSE 0
        END AS conversion_rate

    FROM dim_keyword k
    JOIN fact_keyword_performance_daily kp
        ON k.keyword_id = kp.keyword_id
    WHERE k.customer_id = :customer_id
        AND kp.date_id BETWEEN :start_date AND :end_date
        AND k.status = 'ENABLED'
        AND kp.impressions > :min_impressions
    GROUP BY k.keyword_id
)
SELECT
    keyword_text,
    match_type,
    quality_score,
    current_bid,
    actual_cpc,
    conversions,
    ctr,
    avg_position,

    -- Recommendation logic
    CASE
        -- Increase bid: Good performance, poor position
        WHEN conversions > 0 AND avg_position > 3 AND ctr > 3.0
            THEN 'Increase'

        -- Decrease bid: Poor CTR, high position
        WHEN ctr < 1.0 AND avg_position < 2.0
            THEN 'Decrease'

        -- Pause: No conversions, high cost
        WHEN conversions = 0 AND cost > 20
            THEN 'Pause'

        ELSE 'Maintain'
    END AS bid_recommendation,

    -- Suggested bid (max ±20% change)
    CASE
        WHEN conversions > 0 AND avg_position > 3 AND ctr > 3.0
            THEN current_bid * 1.15
        WHEN ctr < 1.0 AND avg_position < 2.0
            THEN current_bid * 0.85
        ELSE current_bid
    END AS suggested_bid,

    -- Bid modifier recommendation
    CASE
        WHEN quality_score >= 8 AND conversions > 5 THEN '+20%'
        WHEN quality_score >= 7 AND conversions > 2 THEN '+10%'
        WHEN quality_score <= 4 THEN '-20%'
        WHEN quality_score <= 5 THEN '-10%'
        ELSE '0%'
    END AS bid_modifier,

    CASE
        WHEN conversions > 5 AND ctr > 5.0 THEN 'High'
        WHEN conversions > 2 AND ctr > 3.0 THEN 'Medium'
        ELSE 'Low'
    END AS optimization_priority,

    -- Reason for recommendation
    CASE
        WHEN conversions > 0 AND avg_position > 3 AND ctr > 3.0
            THEN 'Good performance but low visibility - increase bid for better position'
        WHEN ctr < 1.0 AND avg_position < 2.0
            THEN 'High position but poor CTR - decrease bid to reduce waste'
        WHEN conversions = 0 AND cost > 20
            THEN 'No conversions despite significant spend - consider pausing'
        ELSE 'Performance is acceptable'
    END AS reason

FROM keyword_performance

WHERE bid_recommendation != 'Maintain'

ORDER BY optimization_priority DESC, conversions DESC;
```

---

## 3. Negative Keyword Suggestions

```sql
-- Identify candidate negative keywords
-- Based on keywords with spend but no conversions
SELECT
    k.keyword_text,
    k.match_type,
    k.quality_score,
    ag.adgroup_name,
    gc.campaign_name,

    SUM(kp.impressions) AS impressions,
    SUM(kp.clicks) AS clicks,
    SUM(kp.cost_micros) / 1000000.0 AS cost,
    SUM(kp.conversions) AS conversions,

    CASE
        WHEN SUM(kp.impressions) > 0
        THEN (SUM(kp.clicks) * 100.0 / SUM(kp.impressions))
        ELSE 0
    END AS ctr,

    'Negative Keyword Candidate' AS suggestion_type,

    CASE
        WHEN SUM(kp.conversions) = 0 AND SUM(kp.cost_micros) > 50000000
            THEN 'High Cost, Zero Conversions'
        WHEN k.quality_score < 3
            THEN 'Very Low Quality Score'
        WHEN ctr < 0.5
            THEN 'Extremely Low CTR'
        ELSE 'Poor Performance'
    END AS reason,

    CASE
        WHEN SUM(kp.cost_micros) > 100000000 THEN 'High'
        WHEN SUM(kp.cost_micros) > 50000000 THEN 'Medium'
        ELSE 'Low'
    END AS priority

FROM dim_keyword k
JOIN dim_ad_group ag ON k.ad_group_id = ag.ad_group_id
JOIN dim_google_ads_campaign gc ON k.google_campaign_id = gc.google_campaign_id
JOIN fact_keyword_performance_daily kp
    ON k.keyword_id = kp.keyword_id

WHERE k.customer_id = :customer_id
    AND kp.date_id BETWEEN :start_date AND :end_date
    AND k.status = 'ENABLED'
    AND (
        (kp.conversions = 0 AND kp.cost_micros > 20000000) -- $20+ spent, no conversions
        OR k.quality_score < 4
        OR (kp.clicks > 50 AND kp.conversions = 0)
    )

GROUP BY k.keyword_id

ORDER BY cost DESC
LIMIT 50;
```

---

## 4. Campaign Simulator (What-If Analysis)

```sql
-- Simulate budget increase/decrease impact
-- Based on historical efficiency
WITH campaign_metrics AS (
    SELECT
        gc.google_campaign_id,
        gc.campaign_name,
        gc.budget_amount_micros / 1000000.0 AS current_budget,

        AVG(fp.spend_micros) / 1000000.0 AS avg_daily_spend,
        AVG(fp.conversions) AS avg_daily_conversions,
        AVG(fp.ctr) AS avg_ctr,

        -- Calculate efficiency (conversions per $1)
        CASE
            WHEN SUM(fp.spend_micros) > 0
            THEN (SUM(fp.conversions) / (SUM(fp.spend_micros) / 1000000.0))
            ELSE 0
        END AS conversion_efficiency

    FROM dim_google_ads_campaign gc
    JOIN fact_campaign_performance_daily fp
        ON gc.google_campaign_id = fp.google_campaign_id
    WHERE gc.customer_id = :customer_id
        AND fp.date_id BETWEEN :start_date AND :end_date
        AND gc.status = 'ENABLED'
    GROUP BY gc.google_campaign_id
)
SELECT
    campaign_name,
    current_budget,
    avg_daily_spend,
    avg_daily_conversions,
    conversion_efficiency,

    -- Scenario: +25% budget
    current_budget * 1.25 AS budget_scenario_increase_25,
    (avg_daily_spend * 1.25) AS projected_spend_increase_25,
    (avg_daily_conversions * 1.20) AS projected_conversions_increase_25, -- Diminishing returns

    -- Scenario: -25% budget
    current_budget * 0.75 AS budget_scenario_decrease_25,
    (avg_daily_spend * 0.75) AS projected_spend_decrease_25,
    (avg_daily_conversions * 0.80) AS projected_conversions_decrease_25,

    -- Impact assessment
    (avg_daily_conversions * 1.20) - avg_daily_conversions AS estimated_gain_increase,
    avg_daily_conversions - (avg_daily_conversions * 0.80) AS estimated_loss_decrease,

    CASE
        WHEN conversion_efficiency > 0.1 THEN 'High confidence in scaling'
        WHEN conversion_efficiency > 0.05 THEN 'Medium confidence'
        ELSE 'Low confidence, risky to scale'
    END AS scaling_confidence

FROM campaign_metrics

WHERE avg_daily_spend > 10 -- At least $10/day

ORDER BY conversion_efficiency DESC;
```

---

# FORECASTING AGENT QUERIES

## 1. CTR Forecast (Simple Trend-Based)

```sql
-- Linear trend forecast for CTR
WITH daily_ctr AS (
    SELECT
        fp.date_id,
        DATE(
            SUBSTR(fp.date_id, 1, 4) || '-' ||
            SUBSTR(fp.date_id, 5, 2) || '-' ||
            SUBSTR(fp.date_id, 7, 2)
        ) AS date,
        JULIANDAY(DATE(
            SUBSTR(fp.date_id, 1, 4) || '-' ||
            SUBSTR(fp.date_id, 5, 2) || '-' ||
            SUBSTR(fp.date_id, 7, 2)
        )) AS day_number,
        AVG(fp.ctr) AS avg_ctr
    FROM fact_campaign_performance_daily fp
    WHERE fp.customer_id = :customer_id
        AND fp.date_id BETWEEN :start_date AND :end_date
    GROUP BY fp.date_id
),
trend_calculation AS (
    SELECT
        AVG(day_number) AS avg_day,
        AVG(avg_ctr) AS avg_ctr,
        -- Calculate slope (m) for y = mx + b
        (COUNT(*) * SUM(day_number * avg_ctr) - SUM(day_number) * SUM(avg_ctr)) /
        (COUNT(*) * SUM(day_number * day_number) - SUM(day_number) * SUM(day_number)) AS slope
    FROM daily_ctr
)
SELECT
    DATE('now', '+' || (ROW_NUMBER() OVER ()) || ' days') AS forecast_date,
    JULIANDAY(DATE('now', '+' || (ROW_NUMBER() OVER ()) || ' days')) AS forecast_day,

    -- Linear forecast: y = mx + b
    (tc.slope * JULIANDAY(DATE('now', '+' || (ROW_NUMBER() OVER ()) || ' days')) +
     (tc.avg_ctr - tc.slope * tc.avg_day)) AS forecasted_ctr,

    -- Confidence bounds (±20%)
    (tc.slope * JULIANDAY(DATE('now', '+' || (ROW_NUMBER() OVER ()) || ' days')) +
     (tc.avg_ctr - tc.slope * tc.avg_day)) * 0.8 AS lower_bound,

    (tc.slope * JULIANDAY(DATE('now', '+' || (ROW_NUMBER() OVER ()) || ' days')) +
     (tc.avg_ctr - tc.slope * tc.avg_day)) * 1.2 AS upper_bound,

    'Linear Trend' AS forecast_method,
    'Medium' AS confidence_level

FROM trend_calculation tc
CROSS JOIN (
    SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL
    SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7
    UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL
    SELECT 11 UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14
    UNION ALL SELECT 15 UNION ALL SELECT 16 UNION ALL SELECT 17 UNION ALL
    SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20 UNION ALL SELECT 21
    UNION ALL SELECT 22 UNION ALL SELECT 23 UNION ALL SELECT 24 UNION ALL
    SELECT 25 UNION ALL SELECT 26 UNION ALL SELECT 27 UNION ALL SELECT 28
    UNION ALL SELECT 29 UNION ALL SELECT 30
)

LIMIT :forecast_days;
```

---

## 2. Spend Forecast

```sql
-- Spend forecast with moving average
WITH daily_spend AS (
    SELECT
        fp.date_id,
        DATE(
            SUBSTR(fp.date_id, 1, 4) || '-' ||
            SUBSTR(fp.date_id, 5, 2) || '-' ||
            SUBSTR(fp.date_id, 7, 2)
        ) AS date,
        SUM(fp.spend_micros) / 1000000.0 AS daily_spend
    FROM fact_campaign_performance_daily fp
    WHERE fp.customer_id = :customer_id
        AND fp.date_id BETWEEN :start_date AND :end_date
    GROUP BY fp.date_id
),
moving_avg AS (
    SELECT
        date,
        daily_spend,
        AVG(daily_spend) OVER (
            ORDER BY date
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS ma_7day,
        AVG(daily_spend) OVER (
            ORDER BY date
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS ma_30day
    FROM daily_spend
),
forecast_base AS (
    SELECT
        AVG(ma_7day) AS avg_recent_spend,
        STDEV(daily_spend) AS spend_volatility,
        AVG(ma_30day) AS avg_historical_spend
    FROM moving_avg
    WHERE date >= DATE('now', '-7 days')
)
SELECT
    DATE('now', '+' || (ROW_NUMBER() OVER ()) || ' days') AS forecast_date,

    -- Forecast: blend of recent and historical averages
    (fb.avg_recent_spend * 0.7 + fb.avg_historical_spend * 0.3) AS forecasted_spend,

    -- Confidence intervals
    (fb.avg_recent_spend * 0.7 + fb.avg_historical_spend * 0.3) - (fb.spend_volatility * 1.96) AS lower_bound_95,
    (fb.avg_recent_spend * 0.7 + fb.avg_historical_spend * 0.3) + (fb.spend_volatility * 1.96) AS upper_bound_95,

    (fb.avg_recent_spend * 0.7 + fb.avg_historical_spend * 0.3) - (fb.spend_volatility * 1.44) AS lower_bound_85,
    (fb.avg_recent_spend * 0.7 + fb.avg_historical_spend * 0.3) + (fb.spend_volatility * 1.44) AS upper_bound_85,

    'Moving Average' AS forecast_method,

    CASE
        WHEN fb.spend_volatility < (fb.avg_recent_spend * 0.15) THEN 'High'
        WHEN fb.spend_volatility < (fb.avg_recent_spend * 0.30) THEN 'Medium'
        ELSE 'Low'
    END AS confidence_level

FROM forecast_base fb
CROSS JOIN (
    SELECT 1 AS n UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL
    SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7
    UNION ALL SELECT 8 UNION ALL SELECT 9 UNION ALL SELECT 10 UNION ALL
    SELECT 11 UNION ALL SELECT 12 UNION ALL SELECT 13 UNION ALL SELECT 14
    UNION ALL SELECT 15 UNION ALL SELECT 16 UNION ALL SELECT 17 UNION ALL
    SELECT 18 UNION ALL SELECT 19 UNION ALL SELECT 20 UNION ALL SELECT 21
    UNION ALL SELECT 22 UNION ALL SELECT 23 UNION ALL SELECT 24 UNION ALL
    SELECT 25 UNION ALL SELECT 26 UNION ALL SELECT 27 UNION ALL SELECT 28
    UNION ALL SELECT 29 UNION ALL SELECT 30
)

LIMIT :forecast_days;
```

---

## 3. Scenario Planning

```sql
-- Budget scenario impact modeling
WITH current_performance AS (
    SELECT
        gc.google_campaign_id,
        gc.campaign_name,
        gc.budget_amount_micros / 1000000.0 AS current_budget,

        AVG(fp.spend_micros) / 1000000.0 AS avg_daily_spend,
        AVG(fp.conversions) AS avg_daily_conversions,
        AVG(fp.conversion_value_micros) / 1000000.0 AS avg_daily_revenue,

        -- Calculate conversion rate and efficiency
        CASE
            WHEN SUM(fp.spend_micros) > 0
            THEN (SUM(fp.conversions) / (SUM(fp.spend_micros) / 1000000.0))
            ELSE 0
        END AS conversion_per_dollar,

        CASE
            WHEN SUM(fp.spend_micros) > 0
            THEN (SUM(fp.conversion_value_micros) * 1.0 / SUM(fp.spend_micros))
            ELSE 0
        END AS roas

    FROM dim_google_ads_campaign gc
    JOIN fact_campaign_performance_daily fp
        ON gc.google_campaign_id = fp.google_campaign_id
    WHERE gc.customer_id = :customer_id
        AND fp.date_id >= DATE('now', '-30 days')
        AND gc.status = 'ENABLED'
    GROUP BY gc.google_campaign_id
)
SELECT
    campaign_name,
    current_budget,
    avg_daily_spend,
    avg_daily_conversions,
    avg_daily_revenue,
    roas,

    -- Scenario 1: Conservative (-20% budget)
    current_budget * 0.8 AS scenario_conservative_budget,
    avg_daily_spend * 0.8 AS scenario_conservative_spend,
    avg_daily_conversions * 0.85 AS scenario_conservative_conversions, -- Less impact on conversions
    avg_daily_revenue * 0.85 AS scenario_conservative_revenue,

    -- Scenario 2: Moderate (+20% budget)
    current_budget * 1.2 AS scenario_moderate_budget,
    avg_daily_spend * 1.2 AS scenario_moderate_spend,
    avg_daily_conversions * 1.15 AS scenario_moderate_conversions, -- Diminishing returns
    avg_daily_revenue * 1.15 AS scenario_moderate_revenue,

    -- Scenario 3: Aggressive (+50% budget)
    current_budget * 1.5 AS scenario_aggressive_budget,
    avg_daily_spend * 1.5 AS scenario_aggressive_spend,
    avg_daily_conversions * 1.30 AS scenario_aggressive_conversions, -- More diminishing returns
    avg_daily_revenue * 1.30 AS scenario_aggressive_revenue,

    -- Impact projections (30-day)
    ((avg_daily_conversions * 1.15) - avg_daily_conversions) * 30 AS projected_gain_moderate,
    ((avg_daily_revenue * 1.15) - avg_daily_revenue) * 30 AS projected_revenue_gain_moderate,

    -- ROI for each scenario
    CASE
        WHEN (current_budget * 1.2 - current_budget) > 0
        THEN (((avg_daily_revenue * 1.15) - avg_daily_revenue) * 30) /
             ((current_budget * 1.2 - current_budget) * 30) * 100
        ELSE 0
    END AS moderate_scenario_roi_pct,

    CASE
        WHEN roas > 4.0 THEN 'Excellent - Safe to scale'
        WHEN roas > 2.5 THEN 'Good - Can scale moderately'
        WHEN roas > 1.5 THEN 'Fair - Scale cautiously'
        ELSE 'Poor - Do not scale'
    END AS scaling_recommendation

FROM current_performance

WHERE avg_daily_spend > 5 -- At least $5/day

ORDER BY roas DESC;
```

---

# ALERT AGENT QUERIES

## 1. Real-Time Alert Monitoring

```sql
-- Threshold breach detection
WITH latest_performance AS (
    SELECT
        gc.google_campaign_id,
        gc.campaign_name,
        gc.status,
        gc.budget_amount_micros / 1000000.0 AS budget,

        fp.date_id,
        fp.spend_micros / 1000000.0 AS daily_spend,
        fp.ctr,
        fp.conversions,
        fp.cpc_micros / 1000000.0 AS cpc,

        -- Calculate budget usage
        CASE
            WHEN gc.budget_amount_micros > 0
            THEN (fp.spend_micros * 100.0 / gc.budget_amount_micros)
            ELSE 0
        END AS budget_used_pct,

        -- Get previous day metrics
        LAG(fp.spend_micros / 1000000.0) OVER (
            PARTITION BY gc.google_campaign_id ORDER BY fp.date_id
        ) AS prev_daily_spend,

        LAG(fp.ctr) OVER (
            PARTITION BY gc.google_campaign_id ORDER BY fp.date_id
        ) AS prev_ctr,

        LAG(fp.conversions) OVER (
            PARTITION BY gc.google_campaign_id ORDER BY fp.date_id
        ) AS prev_conversions

    FROM dim_google_ads_campaign gc
    JOIN fact_campaign_performance_daily fp
        ON gc.google_campaign_id = fp.google_campaign_id
    WHERE gc.customer_id = :customer_id
        AND fp.date_id >= DATE('now', '-2 days')
        AND gc.status = 'ENABLED'
)
SELECT
    campaign_name,
    date_id,
    daily_spend,
    budget_used_pct,
    ctr,
    cpc,
    conversions,

    -- Alert type
    CASE
        WHEN budget_used_pct >= 90 THEN 'Budget Warning'
        WHEN ctr < 1.5 THEN 'Low CTR'
        WHEN cpc > 5.0 THEN 'High CPC'
        WHEN conversions = 0 AND daily_spend > 20 THEN 'No Conversions'
        WHEN (daily_spend - prev_daily_spend) / NULLIF(prev_daily_spend, 0) > 0.5 THEN 'Spend Spike'
        WHEN (prev_ctr - ctr) / NULLIF(prev_ctr, 0) > 0.3 THEN 'CTR Drop'
        ELSE 'OK'
    END AS alert_type,

    -- Severity
    CASE
        WHEN budget_used_pct >= 95 OR ctr < 1.0 OR cpc > 10.0 THEN 'High'
        WHEN budget_used_pct >= 80 OR ctr < 1.5 OR cpc > 5.0 THEN 'Medium'
        ELSE 'Low'
    END AS severity,

    -- Alert message
    CASE
        WHEN budget_used_pct >= 90
            THEN 'Campaign has used ' || ROUND(budget_used_pct, 1) || '% of daily budget'
        WHEN ctr < 1.5
            THEN 'CTR (' || ROUND(ctr, 2) || '%) is below threshold of 1.5%'
        WHEN cpc > 5.0
            THEN 'CPC ($' || ROUND(cpc, 2) || ') is above threshold of $5.00'
        WHEN conversions = 0 AND daily_spend > 20
            THEN 'No conversions despite spending $' || ROUND(daily_spend, 2)
        WHEN (daily_spend - prev_daily_spend) / NULLIF(prev_daily_spend, 0) > 0.5
            THEN 'Spend increased by ' || ROUND(((daily_spend - prev_daily_spend) / NULLIF(prev_daily_spend, 0) * 100), 1) || '%'
        WHEN (prev_ctr - ctr) / NULLIF(prev_ctr, 0) > 0.3
            THEN 'CTR dropped by ' || ROUND(((prev_ctr - ctr) / NULLIF(prev_ctr, 0) * 100), 1) || '%'
        ELSE 'No issues detected'
    END AS alert_message,

    CURRENT_TIMESTAMP AS alert_timestamp

FROM latest_performance

WHERE date_id = (SELECT MAX(date_id) FROM fact_campaign_performance_daily)
    AND alert_type != 'OK'

ORDER BY
    CASE severity
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        ELSE 3
    END,
    daily_spend DESC;
```

---

## 2. Threshold Configuration

```sql
-- Alert thresholds by customer (would need separate threshold table)
-- This is a placeholder structure

/*
CREATE TABLE alert_thresholds (
    threshold_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_id INTEGER NOT NULL,
    metric_name TEXT NOT NULL,
    threshold_value REAL NOT NULL,
    comparison_operator TEXT NOT NULL, -- '<', '>', '<=', '>=', '='
    severity TEXT NOT NULL, -- 'Low', 'Medium', 'High'
    is_active BOOLEAN DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
*/

-- Get active alert thresholds
SELECT
    threshold_id,
    customer_id,
    metric_name,
    threshold_value,
    comparison_operator,
    severity,
    is_active
FROM alert_thresholds
WHERE customer_id = :customer_id
    AND is_active = 1
ORDER BY severity DESC, metric_name;
```

---

## PARAMETER REFERENCE

### Common Parameters Used in Queries:

- **:customer_id** - Customer ID (INTEGER) - Required for all queries
- **:start_date** - Start date in YYYYMMDD format (TEXT) - e.g., '20250101'
- **:end_date** - End date in YYYYMMDD format (TEXT) - e.g., '20250131'
- **:campaign_type** - Campaign type filter (TEXT) - 'ALL', 'SEARCH', 'DISPLAY', 'SHOPPING', 'VIDEO'
- **:include_paused** - Include paused campaigns (INTEGER) - 0 or 1
- **:campaign_ids** - Comma-separated campaign IDs (TEXT) - e.g., '1,2,3'
- **:adgroup_ids** - Comma-separated ad group IDs (TEXT)
- **:min_impressions** - Minimum impressions threshold (INTEGER)
- **:sensitivity** - Anomaly detection sensitivity (REAL) - typically 1.5, 2.0, 2.5
- **:forecast_days** - Number of days to forecast (INTEGER) - typically 7, 14, 30
- **:last_7d_start** - Start date for last 7 days (YYYYMMDD)
- **:last_30d_start** - Start date for last 30 days (YYYYMMDD)
- **:last_90d_start** - Start date for last 90 days (YYYYMMDD)

### Example Parameter Values:
```
customer_id: 1
start_date: '20250901'
end_date: '20250930'
campaign_type: 'ALL'
include_paused: 0
min_impressions: 100
sensitivity: 2.0
forecast_days: 30
```

---

## NOTES

1. **Micros Conversion:** All monetary values are stored as micros (1/1,000,000). Divide by 1,000,000 for actual values.
2. **Date Format:** date_id is stored as TEXT in YYYYMMDD format. Use string functions or DATE() for manipulation.
3. **NULL Handling:** Use NULLIF() to avoid division by zero in calculated fields.
4. **Performance:** Add indexes on customer_id, date_id, and foreign keys for better query performance.
5. **Search Terms:** Currently not in schema - would require additional table.
6. **Alert Thresholds:** Would require separate configuration table (provided structure above).

---

This SQL query library provides comprehensive data access for all agent dashboards with proper customer filtering and optimized performance calculations.
