# MarketingIQ Platform - Complete API Inventory

**Total Endpoints:** 65+
**Platforms:** 5 (Google Ads, GA4, Shopify, Meta Ads, E-commerce Analytics)
**Base URL:** `http://localhost:8000/api/v1`

---

## Table of Contents
1. [Google Ads Endpoints](#google-ads-endpoints)
2. [GA4 Endpoints](#ga4-endpoints)
3. [Shopify Endpoints](#shopify-endpoints)
4. [Meta Ads Endpoints](#meta-ads-endpoints)
5. [E-commerce Analytics Endpoints](#ecommerce-analytics-endpoints)
6. [Common Query Parameters](#common-query-parameters)
7. [Response Format Standards](#response-format-standards)

---

## Google Ads Endpoints

### Customers

#### `GET /customers`
**Purpose:** List all Google Ads customers with campaign counts

**Query Parameters:**
- None required

**Response:**
```json
{
  "customers": [
    {
      "customer_id": 5032737756,
      "customer_name": "Emcee Sons",
      "campaigns_count": 15
    }
  ],
  "total": 1
}
```

**Use Cases:**
- Customer selector dropdown
- Multi-customer dashboard switcher

---

#### `GET /customers/{customer_id}/summary`
**Purpose:** Get performance summary for a customer

**Response:**
```json
{
  "customer_id": 5032737756,
  "total_campaigns": 15,
  "total_spend": 218980.38,
  "total_clicks": 8086,
  "total_conversions": 647,
  "avg_cpc": 27.08,
  "ctr": 4.3
}
```

**Use Cases:**
- Executive dashboard KPI cards
- Customer overview page

---

### Campaigns

#### `GET /campaigns`
**Purpose:** List campaigns with performance metrics

**Query Parameters:**
- `customer_id` (required): Customer ID
- `status`: Filter by status (ENABLED, PAUSED, REMOVED)
- `channel_type`: Filter by type (SEARCH, SHOPPING, DISPLAY, etc.)
- `limit`: Max results (default: 100)
- `offset`: Pagination offset

**Response:**
```json
{
  "total": 15,
  "limit": 100,
  "offset": 0,
  "has_more": false,
  "campaigns": [
    {
      "campaign_id": 8199907592,
      "customer_id": 5032737756,
      "campaign_name": "New Year Diaries 2021",
      "status": "PAUSED",
      "channel_type": "SMART",
      "budget_amount_micros": 50000000,
      "quality_score": 1.6,
      "total_clicks": 150,
      "total_cost": 5000.00,
      "conversions": 10
    }
  ]
}
```

**Use Cases:**
- Campaign list view
- Campaign performance comparison
- Budget allocation dashboard

---

#### `GET /campaigns/{campaign_id}`
**Purpose:** Get detailed campaign information

**Query Parameters:**
- `customer_id` (required)

**Response:**
```json
{
  "campaign_id": 8199907592,
  "campaign_name": "New Year Diaries 2021",
  "status": "PAUSED",
  "bidding_strategy_type": "TARGET_SPEND",
  "budget_amount_micros": 50000000,
  "daily_budget": 500.00,
  "network_target_search": true,
  "start_date": "2019-11-22",
  "end_date": "2037-12-30",
  "performance": {
    "clicks": 150,
    "impressions": 5000,
    "cost": 5000.00,
    "conversions": 10,
    "ctr": 3.0,
    "avg_cpc": 33.33
  }
}
```

**Use Cases:**
- Campaign detail page
- Campaign editing form
- Performance drill-down

---

#### `GET /campaigns/{campaign_id}/adgroups`
**Purpose:** Get ad groups within a campaign

**Use Cases:**
- Campaign hierarchy view
- Campaign breakdown analysis

---

### Ad Groups

#### `GET /ad-groups`
**Purpose:** List ad groups with performance

**Query Parameters:**
- `customer_id` (required)
- `campaign_id`: Filter by campaign
- `status`: Filter by status
- `limit`, `offset`: Pagination

**Response:**
```json
{
  "total": 25,
  "ad_groups": [
    {
      "ad_group_id": 123456,
      "campaign_id": 8199907592,
      "ad_group_name": "Diaries - Broad",
      "status": "ENABLED",
      "cpc_bid_micros": 5000000,
      "cpc_bid": 5.00,
      "clicks": 50,
      "impressions": 1200,
      "cost": 250.00
    }
  ]
}
```

**Use Cases:**
- Ad group management
- Performance by ad group
- Bid optimization

---

#### `GET /ad-groups/{ad_group_id}`
**Purpose:** Ad group details

#### `GET /ad-groups/{ad_group_id}/keywords`
**Purpose:** Keywords in ad group

---

### Keywords

#### `GET /keywords`
**Purpose:** List keywords with quality scores and performance

**Query Parameters:**
- `customer_id` (required)
- `campaign_id`: Filter by campaign
- `ad_group_id`: Filter by ad group
- `match_type`: EXACT, PHRASE, BROAD
- `min_quality_score`: Minimum quality score
- `sort_by`: clicks, cost, conversions, ctr
- `limit`, `offset`

**Response:**
```json
{
  "total": 150,
  "keywords": [
    {
      "keyword_id": "abc123",
      "keyword_text": "custom diaries",
      "match_type": "EXACT",
      "quality_score": 8,
      "cpc_bid": 10.00,
      "clicks": 100,
      "impressions": 2000,
      "cost": 1000.00,
      "conversions": 5,
      "ctr": 5.0,
      "avg_cpc": 10.00,
      "conversion_rate": 5.0
    }
  ]
}
```

**Use Cases:**
- Keyword research
- Quality score optimization
- Bid management
- Negative keyword identification

---

#### `GET /keywords/{keyword_id}`
**Purpose:** Detailed keyword performance

#### `GET /keywords/{keyword_id}/search-terms`
**Purpose:** Search terms that triggered this keyword

---

### Search Terms

#### `GET /search-terms`
**Purpose:** Actual user search queries and their performance

**Query Parameters:**
- `customer_id` (required)
- `campaign_id`, `ad_group_id`, `keyword_id`: Filters
- `min_clicks`: Minimum clicks threshold
- `limit`, `offset`

**Response:**
```json
{
  "total": 500,
  "search_terms": [
    {
      "search_term": "buy custom diary online",
      "keyword_text": "custom diaries",
      "match_type": "PHRASE",
      "clicks": 25,
      "impressions": 300,
      "cost": 250.00,
      "conversions": 2,
      "ctr": 8.33,
      "conversion_rate": 8.0
    }
  ]
}
```

**Use Cases:**
- Search query analysis
- Negative keyword discovery
- New keyword ideas
- Match type optimization

---

### ML Features

#### `GET /ml-features`
**Purpose:** Machine learning feature data for predictive analytics

**Use Cases:**
- ML model training
- Performance prediction
- Budget optimization algorithms

---

### Metrics

#### `GET /metrics/summary`
**Purpose:** Aggregated performance summary

**Query Parameters:**
- `customer_id` (required)
- `date_start`, `date_end`: Date range
- `campaign_ids`: Comma-separated campaign IDs

**Response:**
```json
{
  "total_spend": 218980.38,
  "total_clicks": 8086,
  "total_impressions": 187825,
  "total_conversions": 647,
  "avg_cpc": 27.08,
  "avg_ctr": 4.3,
  "avg_conversion_rate": 8.0,
  "total_revenue": 150000.00,
  "roas": 0.68
}
```

**Use Cases:**
- Executive dashboard
- Performance summary cards
- KPI monitoring

---

#### `GET /metrics/timeseries`
**Purpose:** Daily time-series performance data

**Query Parameters:**
- `customer_id` (required)
- `date_start`, `date_end`
- `granularity`: day, week, month
- `metrics`: clicks,cost,conversions (comma-separated)

**Response:**
```json
{
  "data": [
    {
      "date": "2025-01-01",
      "clicks": 150,
      "cost": 4000.00,
      "conversions": 12,
      "impressions": 3500
    },
    {
      "date": "2025-01-02",
      "clicks": 160,
      "cost": 4200.00,
      "conversions": 15,
      "impressions": 3600
    }
  ]
}
```

**Use Cases:**
- Performance charts
- Trend analysis
- Forecasting

---

## GA4 Endpoints

### Integration

#### `GET /ga4/integration/status`
**Purpose:** Check GA4 connection status

**Query Parameters:**
- `customer_id` (required)

**Response:**
```json
{
  "customer_id": 5032737756,
  "is_connected": true,
  "properties_count": 1,
  "total_sessions": 17858,
  "total_events": 45000,
  "total_conversions": 500,
  "attribution_coverage": 85.5,
  "last_sync_at": "2025-01-15T10:30:00"
}
```

**Use Cases:**
- Integration health check
- Data freshness monitoring

---

#### `GET /ga4/properties`
**Purpose:** List connected GA4 properties

**Response:**
```json
[
  {
    "property_id": "123456789",
    "property_name": "Emcee Sons Website",
    "website_url": "https://emceesons.com",
    "currency_code": "INR",
    "time_zone": "Asia/Kolkata",
    "is_active": true,
    "last_sync_at": "2025-01-15T10:30:00"
  }
]
```

---

### Sessions & Behavior

#### `GET /ga4/sessions`
**Purpose:** Session metrics by date, source, campaign

**Query Parameters:**
- `customer_id` (required)
- `date_start`, `date_end`
- `source`: Traffic source filter
- `medium`: Traffic medium filter
- `campaign`: Campaign name filter
- `device_category`: desktop, mobile, tablet
- `limit`, `offset`

**Response:**
```json
{
  "sessions": [
    {
      "date": "2025-01-15",
      "source": "google",
      "medium": "cpc",
      "campaign": "New Year Diaries 2021",
      "device_category": "mobile",
      "sessions": 150,
      "users": 120,
      "new_users": 80,
      "engaged_sessions": 120,
      "bounce_rate": 35.5,
      "engagement_rate": 80.0,
      "avg_session_duration": 180.5,
      "pages_per_session": 3.2,
      "page_views": 480,
      "conversions": 10,
      "conversion_value": 5000.00
    }
  ],
  "total_count": 500
}
```

**Use Cases:**
- Traffic analysis
- Source/medium performance
- Device performance
- Campaign behavior metrics

---

#### `GET /ga4/sessions/by-source`
**Purpose:** Aggregated metrics by traffic source

**Response:**
```json
[
  {
    "source": "google",
    "sessions": 5000,
    "users": 4000,
    "bounce_rate": 40.0,
    "avg_session_duration": 150.0,
    "pages_per_session": 2.8,
    "conversions": 100,
    "conversion_rate": 2.0
  }
]
```

**Use Cases:**
- Traffic source comparison
- Channel performance analysis

---

#### `GET /ga4/sessions/by-campaign`
**Purpose:** Behavior metrics grouped by campaign

**Response:**
```json
[
  {
    "campaign": "New Year Diaries 2021",
    "source": "google",
    "sessions": 2000,
    "users": 1500,
    "bounce_rate": 35.0,
    "conversions": 50,
    "conversion_rate": 2.5
  }
]
```

**Use Cases:**
- Campaign performance analysis
- Traffic quality by campaign

---

### Events

#### `GET /ga4/events`
**Purpose:** Event tracking data

**Query Parameters:**
- `customer_id` (required)
- `event_name`: Filter by event (page_view, purchase, add_to_cart)
- `date_start`, `date_end`
- `limit`, `offset`

**Response:**
```json
{
  "events": [
    {
      "event_name": "purchase",
      "date": "2025-01-15",
      "event_count": 50,
      "event_value": 25000.00,
      "ecommerce_revenue": 25000.00,
      "ecommerce_quantity": 75,
      "users": 45
    }
  ],
  "total_count": 100
}
```

**Use Cases:**
- Event tracking analysis
- Conversion funnel
- E-commerce events

---

#### `GET /ga4/events/top`
**Purpose:** Top performing events

**Use Cases:**
- Most triggered events
- Event priority analysis

---

### Attribution

#### `GET /ga4/conversion-paths`
**Purpose:** Multi-touch attribution - customer journey to conversion

**Query Parameters:**
- `customer_id` (required)
- `date_start`, `date_end`
- `min_touchpoints`: Minimum touchpoints filter

**Response:**
```json
{
  "paths": [
    {
      "conversion_event": "purchase",
      "conversion_date": "2025-01-15",
      "conversion_value": 500.00,
      "touchpoints_count": 3,
      "days_to_conversion": 5,
      "first_touch_source": "google",
      "first_touch_campaign": "Brand Campaign",
      "last_touch_source": "direct",
      "touchpoints": [
        {
          "source": "google",
          "medium": "cpc",
          "campaign": "Brand Campaign",
          "timestamp": "2025-01-10",
          "order": 1
        },
        {
          "source": "facebook",
          "medium": "social",
          "timestamp": "2025-01-12",
          "order": 2
        },
        {
          "source": "direct",
          "timestamp": "2025-01-15",
          "order": 3
        }
      ]
    }
  ],
  "total_count": 200
}
```

**Use Cases:**
- Multi-touch attribution
- Customer journey mapping
- Channel assist analysis

---

#### `GET /ga4/attribution`
**Purpose:** Compare attribution models (first-touch, last-touch, linear, etc.)

**Response:**
```json
[
  {
    "channel": "Google Ads",
    "first_touch_conversions": 100,
    "last_touch_conversions": 150,
    "linear_conversions": 125,
    "time_decay_conversions": 135
  }
]
```

**Use Cases:**
- Attribution model comparison
- Channel value analysis

---

### Audience Insights

#### `GET /ga4/audience-insights`
**Purpose:** Demographics, interests, technology data

**Query Parameters:**
- `customer_id` (required)
- `date_start`, `date_end`

**Response:**
```json
{
  "total_users": 10000,
  "new_users": 3000,
  "avg_engagement_rate": 75.0,
  "avg_session_duration": 180.0,
  "demographics": {
    "age_ranges": {
      "18-24": 1500,
      "25-34": 4000,
      "35-44": 3000,
      "45+": 1500
    },
    "genders": {
      "male": 6000,
      "female": 4000
    }
  },
  "technology": {
    "devices": {
      "mobile": 6000,
      "desktop": 3500,
      "tablet": 500
    },
    "browsers": {
      "Chrome": 7000,
      "Safari": 2000,
      "Firefox": 1000
    }
  }
}
```

**Use Cases:**
- Audience analysis
- Targeting optimization
- UX optimization

---

#### `GET /ga4/audience-insights/devices`
**Purpose:** Device category breakdown

#### `GET /ga4/audience-insights/countries`
**Purpose:** Geographic breakdown

---

### Enrichment (GA4 + Google Ads Combined)

#### `GET /ga4/campaign-enrichment`
**Purpose:** Link Google Ads campaigns with GA4 behavior metrics

**Query Parameters:**
- `customer_id` (required)
- `campaign_id`: Google Ads campaign ID
- `date_start`, `date_end`

**Response:**
```json
{
  "campaigns": [
    {
      "campaign_id": 8199907592,
      "campaign_name": "New Year Diaries 2021",
      "google_ads_metrics": {
        "clicks": 150,
        "cost": 5000.00,
        "impressions": 5000,
        "avg_cpc": 33.33
      },
      "ga4_behavior": {
        "sessions": 120,
        "bounce_rate": 35.0,
        "pages_per_session": 3.2,
        "avg_session_duration": 180.0,
        "conversions": 10
      },
      "combined_metrics": {
        "click_to_session_rate": 80.0,
        "cost_per_session": 41.67,
        "session_to_conversion_rate": 8.33
      }
    }
  ]
}
```

**Use Cases:**
- Campaign effectiveness analysis
- Landing page quality assessment
- True ROI calculation (ad spend vs actual website behavior)

---

#### `GET /ga4/keyword-enrichment`
**Purpose:** Link keywords with GA4 behavior

**Use Cases:**
- Keyword quality beyond Google Ads metrics
- Landing page optimization by keyword

---

#### `GET /ga4/adgroup-enrichment`
**Purpose:** Link ad groups with GA4 behavior

---

#### `GET /ga4/user-behavior`
**Purpose:** User behavior patterns by campaign

---

## Shopify Endpoints

### Integration

#### `GET /shopify/stores`
**Purpose:** List connected Shopify stores

**Response:**
```json
{
  "stores": [
    {
      "store_id": "mystore.myshopify.com",
      "customer_id": 5032737756,
      "shop_name": "Emcee Sons Shop",
      "currency": "INR",
      "is_active": true,
      "last_sync_at": "2025-01-15T10:30:00"
    }
  ],
  "total_count": 1
}
```

---

#### `GET /shopify/stores/{store_id}`
**Purpose:** Store details

---

#### `GET /shopify/integration/status`
**Purpose:** Shopify connection status

**Response:**
```json
{
  "customer_id": 5032737756,
  "is_connected": true,
  "stores_count": 1,
  "total_orders": 500,
  "total_revenue": 250000.00,
  "total_products": 50,
  "attributed_orders": 200,
  "attribution_coverage": 40.0
}
```

---

### Orders

#### `GET /shopify/orders`
**Purpose:** Order list with Google Ads attribution

**Query Parameters:**
- `customer_id` (required)
- `date_start`, `date_end`
- `financial_status`: paid, pending, refunded
- `has_gclid`: Filter orders with Google Click ID
- `utm_source`, `utm_campaign`: Attribution filters
- `limit`, `offset`

**Response:**
```json
{
  "orders": [
    {
      "order_id": "12345",
      "order_number": "#1001",
      "order_name": "#1001",
      "email": "customer@example.com",
      "total_price": 500.00,
      "currency": "INR",
      "financial_status": "paid",
      "fulfillment_status": "fulfilled",
      "gclid": "abc123xyz",
      "utm_source": "google",
      "utm_campaign": "New Year Diaries 2021",
      "created_at": "2025-01-15T10:00:00",
      "line_items_count": 3
    }
  ],
  "total_count": 500
}
```

**Use Cases:**
- Order management
- Revenue attribution
- Customer purchase history

---

#### `GET /shopify/orders/{order_id}`
**Purpose:** Detailed order information

---

### Products

#### `GET /shopify/products`
**Purpose:** Product catalog

**Query Parameters:**
- `customer_id` (required)
- `status`: active, archived, draft
- `product_type`: Filter by type
- `limit`, `offset`

**Response:**
```json
{
  "products": [
    {
      "product_id": "prod123",
      "title": "Custom Leather Diary",
      "product_type": "Stationery",
      "vendor": "Emcee Sons",
      "price": 500.00,
      "compare_at_price": 700.00,
      "inventory_quantity": 50,
      "status": "active"
    }
  ],
  "total_count": 50
}
```

---

#### `GET /shopify/products/{product_id}`
**Purpose:** Product details

---

#### `GET /shopify/products/performance/ranking`
**Purpose:** Top products by revenue

**Response:**
```json
[
  {
    "product_id": "prod123",
    "product_title": "Custom Leather Diary",
    "total_revenue": 50000.00,
    "units_sold": 100,
    "avg_order_value": 500.00,
    "conversion_rate": 5.0
  }
]
```

**Use Cases:**
- Best sellers analysis
- Inventory optimization
- Product performance tracking

---

### Customers

#### `GET /shopify/customers`
**Purpose:** Customer list

**Query Parameters:**
- `customer_id` (required)
- `accepts_marketing`: Filter marketing opt-in
- `min_total_spent`: LTV filter
- `limit`, `offset`

**Response:**
```json
{
  "customers": [
    {
      "shopify_customer_id": "cust123",
      "email": "customer@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "total_spent": 5000.00,
      "orders_count": 10,
      "average_order_value": 500.00,
      "accepts_marketing": true,
      "first_order_gclid": "abc123",
      "first_order_utm_campaign": "Brand Campaign"
    }
  ],
  "total_count": 1000
}
```

---

#### `GET /shopify/customers/ltv`
**Purpose:** Customer lifetime value analysis

**Response:**
```json
[
  {
    "email": "customer@example.com",
    "total_spent": 5000.00,
    "orders_count": 10,
    "avg_order_value": 500.00,
    "ltv_segment": "High Value",
    "first_purchase_date": "2024-01-15",
    "last_purchase_date": "2025-01-15",
    "customer_age_days": 365
  }
]
```

**Use Cases:**
- Customer segmentation
- Retention analysis
- VIP customer identification

---

### Attribution

#### `GET /shopify/attribution/revenue`
**Purpose:** Revenue attribution to Google Ads campaigns

**Query Parameters:**
- `customer_id` (required)
- `date_start`, `date_end`
- `attribution_model`: last_click, first_click

**Response:**
```json
[
  {
    "campaign_id": 8199907592,
    "campaign_name": "New Year Diaries 2021",
    "attributed_orders": 50,
    "attributed_revenue": 25000.00,
    "ad_spend": 5000.00,
    "roas": 5.0,
    "cost_per_order": 100.00
  }
]
```

**Use Cases:**
- ROAS calculation
- Campaign profitability analysis
- Budget allocation optimization

---

### Cart Analytics

#### `GET /shopify/cart-events`
**Purpose:** Cart activity tracking

**Query Parameters:**
- `customer_id` (required)
- `event_type`: cart_created, checkout_abandoned
- `has_gclid`: Attribution filter
- `date_start`, `date_end`

**Response:**
```json
{
  "events": [
    {
      "event_type": "checkout_abandoned",
      "customer_email": "customer@example.com",
      "total_price": 500.00,
      "line_items_count": 2,
      "gclid": "abc123",
      "utm_campaign": "New Year Sale",
      "event_at": "2025-01-15T10:00:00",
      "abandoned_checkout_url": "https://checkout.shopify.com/..."
    }
  ],
  "total_count": 100
}
```

---

#### `GET /shopify/cart-abandonment/metrics`
**Purpose:** Cart abandonment rates and recovery opportunities

**Response:**
```json
{
  "total_carts": 500,
  "abandoned_carts": 200,
  "abandonment_rate": 40.0,
  "total_abandoned_value": 100000.00,
  "recoverable_value": 80000.00,
  "avg_abandoned_cart_value": 500.00
}
```

**Use Cases:**
- Abandonment analysis
- Recovery campaign planning
- Checkout optimization

---

## Meta Ads Endpoints

### Integration

#### `GET /meta/integration/status`
**Purpose:** Meta Ads connection status

**Query Parameters:**
- `customer_id` (required)

**Response:**
```json
{
  "customer_id": 5032737756,
  "is_connected": true,
  "accounts_count": 1,
  "active_accounts": 1,
  "total_campaigns": 5,
  "total_adsets": 15,
  "total_ads": 30,
  "total_spend": 50000.00,
  "total_clicks": 10000,
  "total_conversions": 200,
  "last_sync_at": "2025-01-15T10:30:00"
}
```

---

#### `GET /meta/accounts`
**Purpose:** List Meta ad accounts

**Response:**
```json
{
  "accounts": [
    {
      "account_id": "act_1595713968470185",
      "customer_id": 5032737756,
      "account_name": "Emcee Sons",
      "currency": "INR",
      "timezone_name": "Asia/Kolkata",
      "account_status": "ACTIVE",
      "is_active": true
    }
  ],
  "total_count": 1
}
```

---

### Campaigns

#### `GET /meta/campaigns`
**Purpose:** List Meta Ads campaigns

**Query Parameters:**
- `customer_id` (required)
- `status`: ACTIVE, PAUSED, DELETED
- `objective`: OUTCOME_SALES, OUTCOME_TRAFFIC, etc.
- `limit`, `offset`

**Response:**
```json
{
  "campaigns": [
    {
      "campaign_id": "123456",
      "campaign_name": "January Sale 2025",
      "status": "ACTIVE",
      "objective": "OUTCOME_SALES",
      "daily_budget": 1000.00,
      "lifetime_budget": null,
      "budget_remaining": 5000.00,
      "bid_strategy": "LOWEST_COST_WITHOUT_CAP",
      "created_time": "2025-01-01T00:00:00",
      "start_time": "2025-01-01T00:00:00"
    }
  ],
  "total_count": 5
}
```

**Use Cases:**
- Campaign management
- Budget monitoring
- Performance tracking

---

#### `GET /meta/campaigns/{campaign_id}`
**Purpose:** Campaign details

---

### Ad Sets

#### `GET /meta/adsets`
**Purpose:** List ad sets with targeting

**Query Parameters:**
- `customer_id` (required)
- `campaign_id`: Filter by campaign
- `status`: Filter by status

**Response:**
```json
{
  "adsets": [
    {
      "adset_id": "789",
      "campaign_id": "123456",
      "name": "Age 25-34 Mumbai",
      "status": "ACTIVE",
      "daily_budget": 500.00,
      "bid_amount": 10.00,
      "optimization_goal": "LINK_CLICKS",
      "targeting": "{\"age_min\": 25, \"age_max\": 34, \"geo_locations\": [\"Mumbai\"]}"
    }
  ],
  "total_count": 15
}
```

**Use Cases:**
- Targeting analysis
- Bid management
- Audience optimization

---

#### `GET /meta/adsets/{adset_id}`
**Purpose:** Ad set details

---

### Ads (Creatives)

#### `GET /meta/ads`
**Purpose:** List ads with creative details

**Query Parameters:**
- `customer_id` (required)
- `campaign_id`, `adset_id`: Filters
- `status`: Filter by status

**Response:**
```json
{
  "ads": [
    {
      "ad_id": "101112",
      "adset_id": "789",
      "campaign_id": "123456",
      "name": "Diary Image Ad 1",
      "status": "ACTIVE",
      "creative_id": "creative123",
      "creative_title": "Get Custom Diaries",
      "creative_body": "Personalized diaries for 2025",
      "creative_image_url": "https://...",
      "call_to_action_type": "SHOP_NOW"
    }
  ],
  "total_count": 30
}
```

**Use Cases:**
- Creative performance analysis
- A/B testing creatives
- Ad management

---

#### `GET /meta/ads/{ad_id}`
**Purpose:** Ad details

---

### Performance

#### `GET /meta/insights`
**Purpose:** Daily performance metrics

**Query Parameters:**
- `customer_id` (required)
- `entity_type`: campaign, adset, ad
- `campaign_id`: Filter by campaign
- `date_start`, `date_end`
- `limit`, `offset`

**Response:**
```json
{
  "insights": [
    {
      "entity_type": "campaign",
      "entity_id": "123456",
      "campaign_id": "123456",
      "date_start": "2025-01-15",
      "date_stop": "2025-01-15",
      "impressions": 10000,
      "clicks": 500,
      "spend": 5000.00,
      "reach": 8000,
      "frequency": 1.25,
      "conversions": 25,
      "purchase_value": 12500.00,
      "ctr": 5.0,
      "cpc": 10.00,
      "cpm": 500.00,
      "roas": 2.5
    }
  ],
  "total_count": 100
}
```

**Use Cases:**
- Performance tracking
- Trend analysis
- ROI calculation

---

#### `GET /meta/insights/summary`
**Purpose:** Aggregated performance summary

**Query Parameters:**
- `customer_id` (required)
- `date_start`, `date_end`

**Response:**
```json
{
  "customer_id": 5032737756,
  "date_start": "2025-01-01",
  "date_stop": "2025-01-15",
  "total_impressions": 150000,
  "total_clicks": 7500,
  "total_spend": 75000.00,
  "total_reach": 100000,
  "avg_frequency": 1.5,
  "total_conversions": 375,
  "total_purchase_value": 187500.00,
  "avg_ctr": 5.0,
  "avg_cpc": 10.00,
  "avg_cpm": 500.00,
  "overall_roas": 2.5
}
```

**Use Cases:**
- Executive dashboard
- Performance summary cards

---

### Cross-Platform (KEY FEATURE)

#### `GET /meta/cross-platform/comparison`
**Purpose:** Compare Google Ads vs Meta Ads performance

**Query Parameters:**
- `customer_id` (required)
- `days`: Number of days to analyze (default: 30)

**Response:**
```json
{
  "customer_id": 5032737756,
  "date_range": "Last 30 days",
  "google_ads": {
    "total_spend": 218980.38,
    "total_clicks": 8086,
    "total_impressions": 187825,
    "total_conversions": 647,
    "avg_cpc": 27.08,
    "ctr": 4.3,
    "roas": 0.68,
    "conversion_rate": 8.0
  },
  "meta_ads": {
    "total_spend": 75000.00,
    "total_clicks": 7500,
    "total_impressions": 150000,
    "total_conversions": 375,
    "avg_cpc": 10.00,
    "ctr": 5.0,
    "roas": 2.5,
    "conversion_rate": 5.0
  },
  "meta_vs_google_spend_ratio": 0.34,
  "meta_vs_google_cpc_diff": -17.08,
  "meta_vs_google_roas_diff": 1.82,
  "recommendation": "Meta Ads is outperforming Google Ads with 17.08 lower CPC and 1.82 higher ROAS. Consider increasing Meta budget by 15-20%."
}
```

**Use Cases:**
- Platform comparison
- Budget reallocation decisions
- Performance benchmarking

---

#### `GET /meta/cross-platform/unified-metrics`
**Purpose:** Combined metrics across all platforms

**Query Parameters:**
- `customer_id` (required)
- `days`: Number of days

**Response:**
```json
{
  "customer_id": 5032737756,
  "date_range": "Last 30 days",
  "total_spend": 293980.38,
  "total_clicks": 15586,
  "total_impressions": 337825,
  "total_conversions": 1022,
  "total_revenue": 250000.00,
  "google_ads_spend": 218980.38,
  "meta_ads_spend": 75000.00,
  "ga4_sessions": 17858,
  "shopify_orders": 500,
  "overall_roas": 0.85,
  "blended_cpc": 18.86,
  "blended_conversion_rate": 6.56
}
```

**Use Cases:**
- Unified executive dashboard
- Total marketing ROI
- Multi-channel attribution

---

## E-commerce Analytics Endpoints

### Overview

#### `GET /ecommerce/overview`
**Purpose:** E-commerce performance summary

**Query Parameters:**
- `customer_id` (required)
- `date_start`, `date_end`

**Response:**
```json
{
  "total_revenue": 250000.00,
  "total_orders": 500,
  "avg_order_value": 500.00,
  "total_products_sold": 750,
  "total_customers": 350,
  "new_customers": 200,
  "returning_customers": 150,
  "customer_retention_rate": 42.86
}
```

**Use Cases:**
- E-commerce dashboard
- KPI monitoring

---

#### `GET /ecommerce/kpis`
**Purpose:** Key e-commerce KPIs

**Response:**
```json
{
  "revenue_growth": 15.5,
  "order_growth": 12.3,
  "customer_growth": 20.0,
  "repeat_purchase_rate": 30.0,
  "cart_abandonment_rate": 40.0,
  "avg_customer_lifetime_value": 1500.00
}
```

---

### Funnel

#### `GET /ecommerce/funnel`
**Purpose:** Conversion funnel analysis

**Response:**
```json
{
  "stages": [
    {
      "stage": "Sessions",
      "count": 10000,
      "conversion_rate": 100.0
    },
    {
      "stage": "Product Views",
      "count": 5000,
      "conversion_rate": 50.0
    },
    {
      "stage": "Add to Cart",
      "count": 2000,
      "conversion_rate": 20.0
    },
    {
      "stage": "Checkout",
      "count": 1000,
      "conversion_rate": 10.0
    },
    {
      "stage": "Purchase",
      "count": 500,
      "conversion_rate": 5.0
    }
  ],
  "overall_conversion_rate": 5.0
}
```

**Use Cases:**
- Funnel optimization
- Drop-off analysis
- Conversion rate optimization

---

### Performance

#### `GET /ecommerce/channels`
**Purpose:** Channel attribution

**Response:**
```json
[
  {
    "channel": "Google Ads",
    "orders": 200,
    "revenue": 100000.00,
    "avg_order_value": 500.00,
    "cost": 20000.00,
    "roas": 5.0
  },
  {
    "channel": "Meta Ads",
    "orders": 150,
    "revenue": 75000.00,
    "avg_order_value": 500.00,
    "cost": 15000.00,
    "roas": 5.0
  },
  {
    "channel": "Organic",
    "orders": 100,
    "revenue": 50000.00,
    "avg_order_value": 500.00,
    "cost": 0.00,
    "roas": null
  }
]
```

**Use Cases:**
- Channel performance comparison
- Marketing budget allocation

---

#### `GET /ecommerce/products`
**Purpose:** Product performance analysis

**Response:**
```json
[
  {
    "product_id": "prod123",
    "product_name": "Custom Leather Diary",
    "units_sold": 100,
    "revenue": 50000.00,
    "avg_price": 500.00,
    "conversion_rate": 5.0,
    "stock_level": 50
  }
]
```

---

### Insights

#### `GET /ecommerce/segments`
**Purpose:** Customer segmentation (RFM analysis)

**Response:**
```json
{
  "segments": [
    {
      "segment": "Champions",
      "customer_count": 50,
      "total_revenue": 75000.00,
      "avg_ltv": 1500.00,
      "recency_score": 5,
      "frequency_score": 5,
      "monetary_score": 5
    },
    {
      "segment": "At Risk",
      "customer_count": 30,
      "total_revenue": 15000.00,
      "avg_ltv": 500.00,
      "recency_score": 2,
      "frequency_score": 4,
      "monetary_score": 4
    }
  ]
}
```

**Use Cases:**
- Customer retention campaigns
- Personalized marketing
- Loyalty programs

---

#### `GET /ecommerce/forecast`
**Purpose:** Revenue forecasting

**Response:**
```json
{
  "forecast": [
    {
      "date": "2025-02-01",
      "predicted_revenue": 9000.00,
      "confidence_interval_lower": 8000.00,
      "confidence_interval_upper": 10000.00
    }
  ],
  "forecast_accuracy": 85.5,
  "trend": "increasing"
}
```

**Use Cases:**
- Budget planning
- Inventory planning
- Sales targets

---

#### `GET /ecommerce/anomalies`
**Purpose:** Anomaly detection

**Response:**
```json
{
  "anomalies": [
    {
      "date": "2025-01-15",
      "metric": "revenue",
      "actual_value": 15000.00,
      "expected_value": 8000.00,
      "deviation_percent": 87.5,
      "severity": "high",
      "description": "Revenue is 87.5% higher than expected"
    }
  ]
}
```

**Use Cases:**
- Alert system
- Performance monitoring
- Issue detection

---

## Common Query Parameters

### Standard Parameters (Most Endpoints)
- `customer_id` (required): Filter by customer
- `limit` (default: 100): Max results per page
- `offset` (default: 0): Pagination offset

### Date Parameters
- `date_start`: Start date (YYYY-MM-DD)
- `date_end`: End date (YYYY-MM-DD)
- `date_range`: Preset ranges (LAST_7_DAYS, LAST_30_DAYS, THIS_MONTH, etc.)

### Filtering Parameters
- `status`: Entity status filter
- `campaign_id`, `ad_group_id`, `keyword_id`: Hierarchy filters
- `sort_by`: Sort field
- `order`: asc or desc

---

## Response Format Standards

### Success Response
```json
{
  "data": [...],
  "total": 100,
  "limit": 50,
  "offset": 0,
  "has_more": true
}
```

### Error Response
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "customer_id is required",
    "details": {}
  }
}
```

### Pagination
All list endpoints support:
- `limit`: Max items (1-1000)
- `offset`: Skip items
- `has_more`: Boolean indicating more results

---

## Data Freshness

| Platform | Sync Frequency | Last Sync Field |
|----------|---------------|-----------------|
| Google Ads | On-demand (ETL) | N/A |
| GA4 | On-demand (ETL) | `last_sync_at` in property |
| Shopify | On-demand (ETL) | `last_sync_at` in store |
| Meta Ads | On-demand (ETL) | `last_sync_at` in account |

**To refresh data:** Run respective ETL script:
- Google Ads: `python warehouse_etl.py`
- GA4: `python ga4_etl.py`
- Shopify: `python shopify_etl.py`
- Meta Ads: `python meta_ads_etl.py`

---

## API Documentation

**Interactive Swagger UI:** `http://localhost:8000/docs`
**ReDoc:** `http://localhost:8000/redoc`
**OpenAPI JSON:** `http://localhost:8000/openapi.json`

---

**Last Updated:** 2025-01-25
**API Version:** v1
**Total Endpoints:** 65+
