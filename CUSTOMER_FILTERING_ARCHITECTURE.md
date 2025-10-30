# Customer Filtering Architecture - Multi-Source Data Integration

## Overview
The MarketingIQ platform integrates data from multiple sources (Google Ads, GA4, Meta Ads) with unified customer filtering across all dashboards.

## Data Architecture

### 1. Warehouse Database (`marketing_warehouse.db`)
**Purpose**: Dimensional data warehouse for Google Ads historical data
**Location**: `D:\ADS_API\marketing_warehouse.db`
**Data Sources**:
- ✅ Google Ads campaigns, ad groups, keywords (LOADED - 19 campaigns, 19 ad groups, 542 keywords)
- ⏳ GA4 data (table structure ready, awaiting ETL)
- ⏳ Meta Ads data (table structure ready, awaiting ETL)

### 2. SQLAlchemy Models Database
**Purpose**: Real-time and operational data
**Data Sources**:
- GA4 properties, sessions, events
- Meta Ads accounts, campaigns, insights
- Shopify stores, orders, products

## Customer ID Mapping

### Customer Records in Warehouse
```
Internal ID | Customer Name    | Google Ads ID | GA4 Account ID
-----------|------------------|---------------|---------------
1          | Emcee Sons       | 5032737756   | 486113361     ← HAS BOTH!
2          | VANAVASI KALYANA | 7613138874   | NULL          ← Google Ads only
3          | Communn.io       | 6265362093   | NULL          ← Google Ads only
```

### ID Mapping Flow
```
Frontend (Customer Selector)
    ↓ sends: customer_id=5032737756 (Google Ads ID)

Backend (/warehouse/* endpoints)
    ↓ maps: 5032737756 → internal_customer_id=1

Warehouse DB Queries
    ↓ filters: WHERE customer_id = 1

Returns: Emcee Sons data
```

## API Endpoints with Customer Filtering

### Google Ads Endpoints (Warehouse)
All endpoints accept `customer_id` (Google Ads ID) and auto-map to internal ID:

- ✅ `/api/v1/warehouse/campaigns?customer_id=5032737756`
- ✅ `/api/v1/warehouse/ad-groups?customer_id=5032737756`
- ✅ `/api/v1/warehouse/keywords?customer_id=5032737756`
- ✅ `/api/v1/warehouse/google-ads/summary?customer_id=5032737756`
- ✅ `/api/v1/warehouse/metrics/summary?customer_id=5032737756`

### GA4 Endpoints (Warehouse)
- ✅ `/api/v1/warehouse/ga4/sessions?customer_id=5032737756`
  - Returns mock data for now (table structure ready)
  - Will return real data once GA4 ETL is implemented

### GA4 Endpoints (Real-time API)
These query the SQLAlchemy models database:
- `/api/v1/ga4/integration/status?customer_id=5032737756`
- `/api/v1/ga4/sessions?customer_id=5032737756`
- `/api/v1/ga4/events?customer_id=5032737756`

### Meta Ads Endpoints (Warehouse)
- ✅ `/api/v1/warehouse/meta/summary?customer_id=5032737756`
  - Returns mock data for now
  - Will return real data once Meta ETL is implemented

## Frontend Integration

### FilterContext (`src/context/FilterContext.tsx`)
Global state management for customer selection:
```typescript
const FilterContext = {
  customerId: 5032737756,        // Google Ads customer ID
  dateRange: 'LAST_30_DAYS',
  campaignType: 'ALL'
}
```

### useFilteredAPI Hook (`src/hooks/useFilteredAPI.ts`)
Automatically adds customer_id to all API requests:
```typescript
const { data, loading } = useCampaigns();
// Automatically calls: /warehouse/campaigns?customer_id=5032737756
```

### Dashboard Behavior

#### For Emcee Sons (customer_id=5032737756):
- ✅ **Data Dashboard**: Shows 15 campaigns, 14 ad groups, 434 keywords (Google Ads)
- ✅ **GA4 Dashboard**: Shows session metrics (mock data → will be real once ETL runs)
- ✅ **Insights Dashboard**: Analyzes Google Ads + GA4 combined data
- ✅ **Optimization Dashboard**: Budget/keyword recommendations for Google Ads campaigns
- ✅ **Forecasting Dashboard**: CTR/Spend projections based on Google Ads data
- ✅ **Alerts Dashboard**: Threshold monitoring for Google Ads metrics

#### For VANAVASI KALYANA (customer_id=7613138874):
- ✅ **Data Dashboard**: Shows 3 campaigns, 3 ad groups, 65 keywords (Google Ads only)
- ⚠️ **GA4 Dashboard**: No data (customer doesn't have GA4 integration)
- ✅ **Other Dashboards**: Work with Google Ads data only

#### For Communn.io (customer_id=6265362093):
- ✅ **Data Dashboard**: Shows 1 campaign, 2 ad groups, 43 keywords (Google Ads only)
- ⚠️ **GA4 Dashboard**: No data (customer doesn't have GA4 integration)
- ✅ **Other Dashboards**: Work with Google Ads data only

## Current Status

### ✅ Completed
1. Google Ads ETL pipeline (campaigns, ad groups, keywords)
2. Warehouse endpoints with customer ID mapping
3. Frontend customer filtering hooks
4. API customer filter propagation
5. Multi-customer support (3 customers configured)

### ⏳ Pending
1. GA4 ETL pipeline (warehouse has tables, needs data loading)
2. Meta Ads ETL pipeline (warehouse has tables, needs data loading)
3. Cross-platform unified metrics combining all sources

## Testing Customer Filtering

### Test Emcee Sons (Has Both Google Ads + GA4)
```bash
# Google Ads data
curl "http://localhost:8000/api/v1/warehouse/campaigns?customer_id=5032737756&limit=3"

# GA4 data (mock for now)
curl "http://localhost:8000/api/v1/warehouse/ga4/sessions?customer_id=5032737756"

# Unified metrics
curl "http://localhost:8000/api/v1/warehouse/metrics/summary?customer_id=5032737756"
```

### Test VANAVASI KALYANA (Google Ads Only)
```bash
curl "http://localhost:8000/api/v1/warehouse/campaigns?customer_id=7613138874&limit=3"
```

### Test Communn.io (Google Ads Only)
```bash
curl "http://localhost:8000/api/v1/warehouse/campaigns?customer_id=6265362093&limit=3"
```

## Next Steps

### To Enable GA4 Data for Emcee Sons:
1. Create GA4 ETL script (similar to Google Ads ETL)
2. Fetch GA4 data using Analytics Data API
3. Load into warehouse fact tables:
   - `fact_ga4_sessions`
   - `fact_ga4_events`
   - `fact_ga4_conversion_paths`
4. Dashboard will automatically display real GA4 data

### To Enable Meta Ads Data:
1. Create Meta Ads ETL script
2. Fetch from Meta Marketing API
3. Load into warehouse fact tables
4. Dashboard will automatically display Meta data
