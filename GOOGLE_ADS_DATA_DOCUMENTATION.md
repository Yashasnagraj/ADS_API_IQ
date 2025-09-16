# Google Ads Data Documentation 📊

## Overview
This document describes the complete Google Ads data extraction pipeline and available datasets for multi-agent ML system training.

---

## 🏢 Account Structure

### Manager Account
- **ID**: 3341907700
- **Name**: Leadzsite AI
- **Type**: Manager Account (MCC)

### Client Accounts

| Account ID | Account Name | Status | Currency | Active Campaigns |
|------------|--------------|--------|----------|------------------|
| 6265362093 | Communn.io | ENABLED | INR | 1 (Whatsappapicommunn) |
| 5032737756 | Emcee Sons | ENABLED | INR | 15 campaigns |
| 7613138874 | VANAVASI KALYANA | ENABLED | USD | 3 campaigns |

---

## 📁 Database Structure

### Database File: `google_ads_data.db`

### Tables Overview

| Table Name | Records | Description |
|------------|---------|-------------|
| `campaigns` | 19 | Campaign configuration and settings |
| `ad_groups` | 19 | Ad group configuration within campaigns |
| `keywords` | 542 | Keyword data with quality scores and bids |
| `search_terms` | 199 | Actual search queries triggering ads |
| `campaign_keywords` | 28 | Performance metrics linking campaigns to keywords |
| `ml_features` | 511 | Denormalized features for ML training |

---

## 📊 Available Data Fields

### 1. **Campaigns Table** (19 records)

```sql
campaign_id                 INTEGER (Primary Key)
customer_id                 INTEGER
campaign_name              TEXT
status                     TEXT (ENABLED, PAUSED, REMOVED)
serving_status             TEXT
channel_type               TEXT (SEARCH, DISPLAY, SHOPPING, VIDEO, etc.)
channel_subtype            TEXT
bidding_strategy_type      TEXT (TARGET_SPEND, MANUAL_CPC, TARGET_CPA, etc.)
budget_id                  TEXT
budget_amount_micros       INTEGER
start_date                 TEXT
end_date                   TEXT
optimization_score         REAL
target_cpa_micros         INTEGER
target_roas               REAL
network_target_search     BOOLEAN
network_target_content    BOOLEAN
network_target_partner    BOOLEAN
geo_target_type_positive  TEXT
geo_target_type_negative  TEXT
```

#### Sample Campaign Data
- **Whatsappapicommunn** (Communn.io): TARGET_SPEND bidding, SEARCH channel
- **New Year Diaries 2021** (Emcee Sons): Various product campaigns
- **Tax Benifit @24** (VANAVASI KALYANA): Non-profit campaigns

---

### 2. **Ad Groups Table** (19 records)

```sql
ad_group_id          INTEGER (Primary Key)
campaign_id          INTEGER (Foreign Key)
customer_id          INTEGER
ad_group_name        TEXT
status               TEXT (ENABLED, PAUSED)
type                 TEXT
cpc_bid_micros       INTEGER
cpm_bid_micros       INTEGER
target_cpa_micros    INTEGER
target_roas          REAL
ad_rotation_mode     TEXT
```

---

### 3. **Keywords Table** (542 records)

```sql
keyword_id                      TEXT (Primary Key: customer_id_adgroup_id_criterion_id)
ad_group_id                     INTEGER (Foreign Key)
campaign_id                     INTEGER (Foreign Key)
customer_id                     INTEGER
keyword_text                    TEXT
match_type                      TEXT (EXACT, PHRASE, BROAD)
status                          TEXT (ENABLED, PAUSED, REMOVED)
quality_score                   INTEGER (1-10)
creative_quality_score          TEXT (BELOW_AVERAGE, AVERAGE, ABOVE_AVERAGE)
landing_page_quality_score      TEXT
search_predicted_ctr            TEXT
cpc_bid_micros                  INTEGER
first_page_cpc_micros          INTEGER
first_position_cpc_micros      INTEGER
top_of_page_cpc_micros         INTEGER
approval_status                 TEXT
system_serving_status          TEXT
is_negative                     BOOLEAN
bid_modifier                    REAL
```

#### Top Keywords by Volume
1. **whatsapp api** - 205 impressions, QS: 5
2. **wati** - 86 impressions, QS: 3
3. **whatsapp business api** - 84 impressions, QS: 7
4. **whatsapp broadcast** - 74 impressions, QS: 5
5. **sending broadcast on whatsapp** - 54 impressions

---

### 4. **Search Terms Table** (199 records)

```sql
search_term_id           INTEGER (Auto-increment Primary Key)
keyword_id               TEXT (Foreign Key)
ad_group_id             INTEGER (Foreign Key)
campaign_id             INTEGER (Foreign Key)
customer_id             INTEGER
search_term             TEXT (Actual search query)
keyword_text            TEXT (Triggering keyword)
match_type              TEXT
search_term_match_type  TEXT (EXACT, NEAR_EXACT, etc.)
date                    TEXT
clicks                  INTEGER
impressions             INTEGER
cost_micros            INTEGER
conversions            REAL
conversion_value       REAL
ctr                    REAL
avg_cpc_micros        INTEGER
```

#### Sample Search Terms
- "whatsapp api" → triggered by keyword "whatsapp api" (EXACT)
- "whatsapp business api" → triggered by "whatsapp api" (NEAR_EXACT)
- "whatsapp cloud api" → triggered by "whatsapp api" (NEAR_EXACT)
- "wati" → triggered by "wati" (EXACT)

---

### 5. **Campaign Keywords Performance** (28 records)

```sql
id                                    INTEGER (Auto-increment)
campaign_id                          INTEGER (Foreign Key)
keyword_id                           TEXT (Foreign Key)
customer_id                          INTEGER
date                                 TEXT
clicks                               INTEGER
impressions                          INTEGER
cost_micros                         INTEGER
conversions                         REAL
conversion_value                    REAL
ctr                                 REAL
conversion_rate                     REAL
avg_cpc_micros                      INTEGER
avg_position                        REAL
absolute_top_impression_percentage  REAL
top_impression_percentage           REAL
search_impression_share             REAL
search_rank_lost_impression_share  REAL
```

---

### 6. **ML Features Table** (511 records) 🎯

**Denormalized table optimized for ML training**

```sql
id                    INTEGER (Auto-increment)
customer_id          INTEGER
campaign_id          INTEGER
campaign_name        TEXT
channel_type         TEXT
bidding_strategy     TEXT
budget_amount        REAL (in currency units)
keyword_id           TEXT
keyword_text         TEXT
match_type           TEXT
quality_score        INTEGER
avg_cpc             REAL (in currency units)
ctr                 REAL (click-through rate)
conversion_rate     REAL
conversions         REAL
cost                REAL (in currency units)
impressions         INTEGER
clicks              INTEGER
competition_index   REAL (0-100, derived from quality score)
search_volume_trend REAL (0-100, placeholder for trends)
```

#### ML Features Statistics
- **Total Features**: 511 records
- **Active Keywords**: Keywords with ENABLED status
- **Metrics Coverage**: 28 keywords with performance data
- **Quality Score Distribution**: Ranges from 2 to 7

---

## 📈 Performance Metrics Summary

### Campaign Performance (Last 30 Days)

| Campaign | Clicks | Impressions | Cost (INR) | Conversions | CTR | Conv Rate |
|----------|--------|-------------|------------|-------------|-----|-----------|
| Whatsappapicommunn | 72 | 621 | 5,114 | 6 | 11.6% | 8.3% |

### Top Performing Keywords

| Keyword | Clicks | Impressions | Cost | CTR | Conversions |
|---------|--------|-------------|------|-----|-------------|
| whatsapp api | 31 | 205 | ₹2,171 | 15.1% | 5 |
| whatsapp business api | 10 | 84 | ₹726 | 11.9% | 0 |
| wati | 3 | 86 | ₹226 | 3.5% | 0 |

---

## 🔍 Database Views

### v_campaign_performance
Aggregated campaign-level metrics with keyword counts and performance summary.

### v_keyword_performance
Detailed keyword performance with campaign context and quality metrics.

---

## 📂 Exported Files

### CSV Files in `extracted_data/` directory:
- `campaigns.csv` - All campaign data
- `ad_groups.csv` - All ad group data
- `keywords.csv` - All keyword data
- `search_terms.csv` - All search term data
- `campaign_keywords.csv` - Performance metrics
- `ml_features.csv` - ML training features

---

## 🚀 Usage Examples

### Query the Database

```python
import sqlite3
import pandas as pd

# Connect to database
conn = sqlite3.connect('google_ads_data.db')

# Get ML features for training
df_ml = pd.read_sql_query("SELECT * FROM ml_features WHERE impressions > 0", conn)

# Get campaign hierarchy
df_hierarchy = pd.read_sql_query("""
    SELECT c.campaign_name, ag.ad_group_name, k.keyword_text, k.quality_score
    FROM campaigns c
    JOIN ad_groups ag ON c.campaign_id = ag.campaign_id
    JOIN keywords k ON ag.ad_group_id = k.ad_group_id
    WHERE c.status = 'ENABLED'
""", conn)

# Get search term insights
df_search = pd.read_sql_query("""
    SELECT search_term, COUNT(*) as frequency,
           SUM(clicks) as total_clicks,
           SUM(conversions) as total_conversions
    FROM search_terms
    GROUP BY search_term
    ORDER BY total_clicks DESC
""", conn)

conn.close()
```

### Access via SQLite CLI

```bash
sqlite3 google_ads_data.db

# Show all tables
.tables

# Show schema
.schema ml_features

# Query data
SELECT * FROM ml_features LIMIT 10;
```

---

## 🎯 ML Training Features

### Campaign-Level Features
- `channel_type`: Type of advertising channel (SEARCH, DISPLAY, etc.)
- `bidding_strategy`: Bidding strategy type
- `budget_amount`: Campaign budget in currency units

### Keyword-Level Features
- `keyword_text`: The actual keyword text
- `match_type`: EXACT, PHRASE, or BROAD
- `quality_score`: Google's quality score (1-10)

### Performance Metrics
- `avg_cpc`: Average cost per click
- `ctr`: Click-through rate
- `conversion_rate`: Conversion rate
- `conversions`: Total conversions
- `cost`: Total cost
- `impressions`: Total impressions
- `clicks`: Total clicks

### Competitive Metrics
- `competition_index`: Derived from quality score (0-100)
- `search_volume_trend`: Placeholder for search trends (0-100)

---

## 📝 Notes

1. **Data Freshness**: Data covers the last 30 days of activity
2. **Active Accounts**: Only Communn.io has recent campaign activity
3. **Quality Scores**: Available for 5 keywords, ranging from 2-7
4. **Currency**: Mixed (INR for Indian accounts, USD for VANAVASI KALYANA)
5. **Performance Data**: 28 keyword-campaign combinations have performance metrics

---

## 🔧 Scripts Available

1. **`extract_google_ads.py`** - Original comprehensive extraction script
2. **`extract_google_ads_simple.py`** - Simplified extraction with compatible fields
3. **`google_ads_etl_pipeline.py`** - Complete ETL pipeline with database creation
4. **`fix_campaigns_ml.py`** - Fixes campaign data and populates ML features
5. **`query_database.py`** - Query and display database contents
6. **`list_accounts.py`** - List all accessible Google Ads accounts
7. **`get_refresh_token.py`** - Obtain refresh token for authentication

---

## 📊 Data Quality Indicators

✅ **Complete Data**
- All 3 client accounts extracted
- 542 keywords with configuration data
- 199 search terms with performance metrics

⚠️ **Partial Data**
- Quality scores available for only 5 keywords
- Campaign budgets using default values in some cases
- Search volume trends using placeholder values

❌ **Missing Data**
- Historical trends beyond 30 days
- Competitor analysis data
- Ad creative performance

---

## 🎯 Ready for ML Training

The `ml_features` table is optimized for training with:
- **511 feature records** combining campaign and keyword data
- **Hierarchical structure** preserved (Campaign → AdGroup → Keyword)
- **Performance metrics** included for supervised learning
- **Competition indicators** for market analysis
- **Denormalized format** for easy model consumption

---

*Last Updated: 2025-09-15*
*Database Version: 1.0*
*API Version: Google Ads API v21*