# ETL Pipeline Deployment Status Report
**Date**: 2025-10-10
**Status**: DEPLOYED - Configuration Issues Being Resolved

---

## ✅ Completed Tasks

###  1. Cloud Run Deployment
- **Service Name**: `ads-etl-pipeline`
- **URL**: https://ads-etl-pipeline-178867443107.us-central1.run.app
- **Region**: us-central1
- **Status**: RUNNING
- **Latest Revision**: ads-etl-pipeline-00011-gvt (active)
- **Resources**: 2 CPU, 2GB RAM
- **Timeout**: 30 minutes

### 2. OAuth Token Refresh
- ✅ Generated new refresh token successfully
- ✅ Updated Secret Manager with new token (version 6)
- ✅ Cloud Run service updated to use latest secret

---

## 🔧 Current Issues & Fixes

### Issue: Google Ads API Version Mismatch
**Problem**: The deployed code is using deprecated Google Ads API v15, which returns "GRPC target method can't be resolved" error.

**Root Cause**:
- google-ads==22.1.0 supports v17/v18
- The client defaults to v15 for backward compatibility
- Need to explicitly use CustomerService for listing accounts

**Solution Implemented**:
1. Updated `warehouse_etl.py` to use `CustomerService.list_accessible_customers()` instead of direct GAQL query
2. Added fallback logic for customers that can't be queried
3. Code changes ready for next deployment

---

## 📊 Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│              Cloud Run (ads-etl-pipeline)           │
│  ┌──────────────────────────────────────────────┐  │
│  │  1. Fetch from Google Ads API                │  │
│  │     - Campaigns (last 30 days)               │  │
│  │     - Ad Groups                              │  │
│  │     - Keywords                               │  │
│  │     - Search Terms                           │  │
│  │                                              │  │
│  │  2. Store in SQLite (google_ads_data.db)     │  │
│  │     - campaigns_performance                  │  │
│  │     - adgroups_performance                   │  │
│  │     - keywords_performance                   │  │
│  │     - search_terms                           │  │
│  │     - ml_features                            │  │
│  │                                              │  │
│  │  3. Expose via FastAPI                       │  │
│  │     GET / → Run ETL + return status          │  │
│  └──────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────┘
                      │
                      ▼
        ┌─────────────────────────────┐
        │    Secret Manager           │
        │  google-ads-yaml (v6)       │
        │  - refresh_token (UPDATED)  │
        │  - developer_token          │
        │  - client_id/secret         │
        └─────────────────────────────┘
```

---

## 🔜 Next Steps

### Immediate (Phase 1)
1. ⏳ Deploy fixed warehouse_etl.py with CustomerService changes
2. ⏳ Test ETL pipeline end-to-end
3. ⏳ Verify data is correctly fetched from Google Ads

### Automation (Phase 2)
4. ⬜ Set up Cloud Scheduler for daily automated runs
   - Schedule: Daily at 2am UTC
   - Target: ads-etl-pipeline Cloud Run service
   - Retry policy: 3 attempts with exponential backoff

5. ⬜ Configure BigQuery integration
   - Create dataset: `google_ads_warehouse`
   - Export SQLite data to BigQuery tables
   - Set up data retention policies

### Monitoring (Phase 3)
6. ⬜ Set up Cloud Monitoring alerts
   - ETL failure notifications
   - API quota usage alerts
   - Performance degradation warnings

7. ⬜ Create dashboard for ETL health
   - Last run timestamp
   - Records processed
   - Error rates
   - API call counts

---

## 📋 Database Schema

### campaigns_performance
```sql
- campaign_id (PK)
- customer_id ← FILTERING KEY
- campaign_name
- status, channel_type, bidding_strategy
- date
- metrics: impressions, clicks, cost, conversions, ctr, cpc, roas
```

### adgroups_performance
```sql
- ad_group_id (PK)
- campaign_id, customer_id ← FILTERING KEY
- ad_group_name, status, type
- date
- metrics: impressions, clicks, cost, conversions, ctr, cpc
```

### keywords_performance
```sql
- keyword_id (PK)
- ad_group_id, campaign_id, customer_id ← FILTERING KEY
- keyword_text, match_type, quality_score
- date
- metrics: impressions, clicks, cost, conversions, ctr, cpc
```

### search_terms
```sql
- search_term (PK)
- campaign_id, customer_id ← FILTERING KEY
- date
- metrics: impressions, clicks, cost, conversions, ctr, conversion_rate
```

---

## 🎯 Success Criteria

- [x] ETL deployed to Cloud Run
- [x] OAuth token refreshed and stored securely
- [ ] ETL successfully pulls data from Google Ads API
- [ ] All 5 tables populated with real data
- [ ] Data available for frontend dashboards
- [ ] Automated daily refresh working
- [ ] Multi-customer filtering functional

---

##  💡 Important Notes

1. **Customer Filtering**: Every table has `customer_id` for multi-client support
2. **Data Freshness**: ETL fetches last 30 days of data
3. **Error Handling**: Graceful fallbacks for API failures
4. **Token Security**: Refresh token stored in Secret Manager, never in code
5. **API Quota**: Monitor daily quota usage to avoid overages

---

## 🔗 Resources

- Cloud Run Service: https://ads-etl-pipeline-178867443107.us-central1.run.app
- Google Ads API Docs: https://developers.google.com/google-ads/api/docs
- Project: msrit-ads-etl
- Region: us-central1

---

**Last Updated**: 2025-10-10 13:35 UTC
**Status**: Awaiting final deployment with API version fix
