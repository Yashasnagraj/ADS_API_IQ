# Meta (Facebook) Ads - Complete Setup Guide

**For Team Members**

This guide will help you set up Meta Ads integration for the MarketingIQ platform, including data extraction, warehouse ETL, and API access.

---

## What You'll Get

- Real-time access to Meta Ads campaigns, ad sets, and ads
- Daily performance metrics and insights
- Demographic and geographic breakdowns
- Integration with the marketing data warehouse
- REST API endpoints for all Meta Ads data

---

## Prerequisites

Before starting, make sure you have:

- Meta (Facebook) Business Manager access
- Admin access to a Meta Ad Account
- Python 3.11+ installed
- Access to the ADS_API project

---

## Quick Start (6 Steps)

### Step 1: Create Meta App

1. Go to [Meta for Developers](https://developers.facebook.com/apps)
2. Click **Create App**
3. Select **Business** as app type
4. Fill in details:
   - **App Name**: "MarketingIQ Meta Integration" (or your choice)
   - **App Contact Email**: Your email
   - **Business Account**: Select your business
5. Click **Create App**

### Step 2: Configure App Permissions

1. In your new app, go to **Add Products**
2. Add **Marketing API**
3. Go to **Settings** → **Basic**
4. Copy:
   - **App ID** → Save this
   - **App Secret** → Click "Show" and save this
5. Go to **Marketing API** → **Tools**
6. Add **Test Users** if testing

### Step 3: Setup Configuration File

Create `.env.meta` file in the project root:

```bash
# Copy the example template
cp .env.meta.example .env.meta
```

Edit `.env.meta` with your credentials:

```env
# Meta App Credentials
META_APP_ID=your_app_id_here
META_APP_SECRET=your_app_secret_here

# Access Token (we'll generate this in Step 4)
META_ACCESS_TOKEN=your_long_lived_access_token_here

# Ad Account ID (format: act_123456789)
META_AD_ACCOUNT_ID=act_123456789

# Internal Customer ID (usually 1 for single-customer setup)
CUSTOMER_ID=1

# API Version (optional, defaults to v19.0)
META_API_VERSION=v19.0
```

**Finding Your Ad Account ID:**
1. Go to [Facebook Ads Manager](https://adsmanager.facebook.com)
2. Look at the URL: `https://adsmanager.facebook.com/adsmanager/manage/campaigns?act=123456789`
3. Your Ad Account ID is: `act_123456789` (include the "act_" prefix)

Or:
1. Go to [Business Settings](https://business.facebook.com/settings/ad-accounts)
2. Click on your ad account
3. Copy the Account ID (add "act_" prefix)

### Step 4: Generate Access Token

Run the token generator script:

```bash
python generate_meta_token.py
```

This interactive script will:
1. Guide you to Meta Graph API Explorer
2. Help you generate a short-lived token
3. Exchange it for a long-lived token (60 days)
4. Test the token against your ad account
5. Automatically update `.env.meta` with the new token

**Detailed Steps:**

```
======================================================================
META ACCESS TOKEN GENERATOR
======================================================================

App ID: 1234567890
Ad Account: act_123456789

======================================================================
STEP 1: Get Short-Lived Token from Graph API Explorer
======================================================================

1. Go to: https://developers.facebook.com/tools/explorer/
2. Select your app: 1234567890
3. Add these permissions:
   ✓ ads_read
   ✓ ads_management
   ✓ read_insights
4. Click 'Generate Access Token'
5. Authorize the permissions
6. Copy the generated token

======================================================================

Paste your SHORT-LIVED token here:
> [paste your token]

🔄 Exchanging token for long-lived version...
✅ Got long-lived token!
   Expires in: 5184000 seconds (~60 days)

🧪 Testing token...
✅ Token works!
   Account: Your Ad Account Name
   Status: ACTIVE
   Currency: USD

✅ Updated .env.meta with new token

======================================================================
✅ SUCCESS! Token updated
======================================================================

You can now run:
   python warehouse_meta_ads_etl.py --days=30
======================================================================
```

**Pro Tip:** For production, use a **System User** token that never expires:
1. Go to [Business Settings](https://business.facebook.com/settings/system-users)
2. Create System User
3. Assign ad account access
4. Generate token with required permissions
5. Use this token in `.env.meta`

### Step 5: Install Python Dependencies

```bash
# Install Meta Ads SDK
pip install facebook-business
pip install python-dotenv
```

Or if you have a requirements.txt with all dependencies:
```bash
pip install -r requirements.txt
```

### Step 6: Run ETL Pipeline

Extract Meta Ads data and load into warehouse:

```bash
python warehouse_meta_ads_etl.py --days=30
```

This will:
- Connect to Meta Marketing API
- Fetch all campaigns with performance data
- Extract insights for the last 30 days
- Store everything in `marketing_warehouse.db`

**Expected Output:**

```
======================================================================
META ADS → WAREHOUSE ETL PIPELINE
======================================================================

Configuration:
   Customer ID: 1
   Meta Ad Account: act_123456789
   Days: 30

🔌 Connecting to warehouse...
   ✅ Connected

🔐 Initializing Meta API...
✅ Meta Marketing API initialized

📊 Fetching campaigns from Meta API...
   ✅ Fetched 15 campaigns

📊 Fetching campaign insights (last 30 days)...
   ✅ Fetched 450 daily insight records for 15 campaigns

💾 Loading data into warehouse...
   Loading campaigns...
   ✅ Loaded 15 campaigns
   Loading performance metrics...
   ✅ Loaded 450 performance records

======================================================================
✅ META ADS ETL COMPLETED
======================================================================

📊 Summary:
   Campaigns loaded:       15
   Performance records:    450
   Total records:          465

💾 Data stored in: marketing_warehouse.db
======================================================================
```

---

## Verify Setup

### 1. Check Database

```bash
# View campaign data
python show_warehouse_summary.py
```

Or query directly:
```bash
python -c "import sqlite3; conn = sqlite3.connect('marketing_warehouse.db'); print('Meta Campaigns:', conn.execute('SELECT COUNT(*) FROM dim_meta_campaign').fetchone()[0]); conn.close()"
```

### 2. Start API Server

```bash
cd api
python -m uvicorn app.main:app --reload --port 8000
```

### 3. Test API Endpoints

Open browser: `http://localhost:8000/docs`

Try these Meta Ads endpoints:

**Integration Status:**
```
GET /api/v1/meta/integration/status?customer_id=1
```

**Campaigns:**
```
GET /api/v1/meta/campaigns?customer_id=1
```

**Insights Summary:**
```
GET /api/v1/meta/insights/summary?customer_id=1&date_range=last_30d
```

**Age/Gender Demographics:**
```
GET /api/v1/meta/insights/age-gender?customer_id=1
```

---

## Warehouse Schema

The ETL creates these tables:

### 1. `dim_meta_campaign`
Campaign dimension table with metadata:
- `meta_campaign_id` (PK)
- `customer_id`
- `campaign_id` (Meta campaign ID)
- `name`
- `status`
- `effective_status`
- `objective`
- `daily_budget`
- `lifetime_budget`
- `bid_strategy`
- `buying_type`
- Timestamps: `created_time`, `updated_time`, `start_time`, `stop_time`

### 2. `fact_campaign_performance_daily`
Daily performance metrics:
- `fact_id` (PK)
- `customer_id`
- `platform_id` (FK to dim_platform: 'meta_ads')
- `date_id` (FK to dim_date)
- `meta_campaign_id` (FK to dim_meta_campaign)
- **Core Metrics:**
  - `impressions`
  - `clicks`
  - `spend_micros` (in micro-currency, e.g., $1.00 = 1,000,000)
  - `conversions`
  - `conversion_value_micros`
- **Calculated Metrics:**
  - `ctr` (Click-through rate %)
  - `cpc_micros` (Cost per click)
  - `cpm_micros` (Cost per 1000 impressions)
  - `cpa_micros` (Cost per acquisition)
  - `roas` (Return on ad spend)
- **Meta-Specific Metrics (JSON):**
  - `meta_ads_metrics` (reach, frequency, inline_link_clicks, etc.)

All monetary values stored in **micros** (multiply by 1,000,000):
- $10.50 → 10,500,000 micros
- Prevents floating-point precision issues

---

## Available API Endpoints

### Integration & Accounts

```http
GET  /api/v1/meta/integration/status?customer_id={id}
GET  /api/v1/meta/accounts?customer_id={id}
```

### Campaigns

```http
GET  /api/v1/meta/campaigns?customer_id={id}&status=ACTIVE&date_range=last_30d
GET  /api/v1/meta/campaigns/{campaign_id}?customer_id={id}
```

**Filters:**
- `status`: ACTIVE, PAUSED, DELETED, ARCHIVED
- `objective`: OUTCOME_SALES, OUTCOME_LEADS, OUTCOME_AWARENESS, etc.
- `date_range`: last_7d, last_30d, last_60d, last_90d

### Ad Sets

```http
GET  /api/v1/meta/adsets?customer_id={id}&campaign_id={campaign_id}
GET  /api/v1/meta/adsets/{adset_id}?customer_id={id}
```

### Ads

```http
GET  /api/v1/meta/ads?customer_id={id}&adset_id={adset_id}
GET  /api/v1/meta/ads/{ad_id}?customer_id={id}
```

### Insights & Performance

```http
GET  /api/v1/meta/insights?customer_id={id}&level=campaign&date_range=last_30d
GET  /api/v1/meta/insights/summary?customer_id={id}&date_range=last_30d
```

**Levels:** account, campaign, adset, ad

### Demographic Insights

```http
GET  /api/v1/meta/insights/age-gender?customer_id={id}
GET  /api/v1/meta/insights/country?customer_id={id}
GET  /api/v1/meta/insights/device?customer_id={id}
GET  /api/v1/meta/insights/platform?customer_id={id}
```

Returns performance broken down by:
- **Age/Gender:** 18-24, 25-34, 35-44, 45-54, 55-64, 65+ × male/female
- **Country:** Geographic performance
- **Device:** Mobile, desktop, tablet
- **Platform:** Facebook, Instagram, Messenger, Audience Network

### Cross-Platform Analysis

```http
GET  /api/v1/meta/cross-platform/comparison?customer_id={id}&days=30
GET  /api/v1/meta/cross-platform/unified-metrics?customer_id={id}&days=30
```

Compare Meta Ads vs Google Ads performance side-by-side.

### Creative Assets

```http
GET  /api/v1/meta/ad-creatives?customer_id={id}
GET  /api/v1/meta/images?customer_id={id}
GET  /api/v1/meta/videos?customer_id={id}
```

### Lead Generation

```http
GET  /api/v1/meta/leads?customer_id={id}
GET  /api/v1/meta/lead-forms/{form_id}/leads?customer_id={id}
```

### Custom Audiences & Conversions

```http
GET  /api/v1/meta/custom-audiences?customer_id={id}
GET  /api/v1/meta/custom-conversions?customer_id={id}
```

---

## Running ETL on Schedule

### Option 1: Windows Task Scheduler

1. Open **Task Scheduler**
2. Create Basic Task:
   - **Name:** Meta Ads Daily ETL
   - **Trigger:** Daily at 2:00 AM
   - **Action:** Start a program
   - **Program:** `python.exe`
   - **Arguments:** `warehouse_meta_ads_etl.py --days=7`
   - **Start in:** `D:\ADS_API`

### Option 2: Linux/Mac Cron

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 2 AM)
0 2 * * * cd /path/to/ADS_API && python warehouse_meta_ads_etl.py --days=7
```

### Option 3: Python Scheduler (Cross-platform)

Create `schedule_meta_etl.py`:

```python
import schedule
import time
import subprocess

def run_etl():
    print("Running Meta Ads ETL...")
    subprocess.run(["python", "warehouse_meta_ads_etl.py", "--days=7"])

# Run daily at 2:00 AM
schedule.every().day.at("02:00").do(run_etl)

print("Meta Ads ETL Scheduler started. Press Ctrl+C to stop.")
while True:
    schedule.run_pending()
    time.sleep(60)
```

Run:
```bash
pip install schedule
python schedule_meta_etl.py
```

---

## Multi-Customer Setup

For managing multiple customers (clients):

### 1. Create Customer Records

```python
# Add customers to warehouse
python -c "
import sqlite3
conn = sqlite3.connect('marketing_warehouse.db')

customers = [
    (1, 'Client A', 'act_111111111'),
    (2, 'Client B', 'act_222222222'),
    (3, 'Client C', 'act_333333333'),
]

for customer_id, name, meta_account in customers:
    conn.execute('''
        INSERT OR REPLACE INTO dim_customer (customer_id, customer_name, meta_business_id)
        VALUES (?, ?, ?)
    ''', (customer_id, name, meta_account))

conn.commit()
conn.close()
print('✅ Customers added')
"
```

### 2. Create Separate .env Files

```bash
.env.meta.client1
.env.meta.client2
.env.meta.client3
```

### 3. Run ETL for Each Client

```bash
# Client 1
python warehouse_meta_ads_etl.py --customer-id=1 --days=30

# Client 2
python warehouse_meta_ads_etl.py --customer-id=2 --days=30

# Client 3
python warehouse_meta_ads_etl.py --customer-id=3 --days=30
```

Or create a loop script:

```bash
#!/bin/bash
# run_all_meta_etl.sh

for customer_id in 1 2 3; do
    echo "Running ETL for Customer $customer_id..."
    python warehouse_meta_ads_etl.py --customer-id=$customer_id --days=7
done
```

---

## Troubleshooting

### Error: "Access token expired"

**Solution:**
```bash
# Regenerate token
python generate_meta_token.py

# The script will automatically update .env.meta
```

**Permanent Fix:**
Use a System User token instead (see Step 4 Pro Tip).

### Error: "Invalid OAuth access token"

**Causes:**
1. Token expired (short-lived tokens expire in 1-2 hours)
2. Wrong token copied
3. App permissions changed

**Solution:**
```bash
# Generate fresh long-lived token
python generate_meta_token.py

# Verify token in Graph API Explorer:
# https://developers.facebook.com/tools/debug/accesstoken/
```

### Error: "Ad account not found"

**Solution:**
1. Check Ad Account ID format: `act_123456789` (must include "act_" prefix)
2. Verify you have access:
   - Go to [Ads Manager](https://adsmanager.facebook.com)
   - Check if account appears in dropdown
3. Verify in Business Settings:
   - [Business Settings > Ad Accounts](https://business.facebook.com/settings/ad-accounts)
   - Check your role (must be Admin or Advertiser)

### Error: "Insufficient permissions"

**Solution:**
When generating token, ensure these permissions are added:
- `ads_read` - Required to read ads data
- `ads_management` - Required for full access
- `read_insights` - Required for performance metrics

Regenerate token with correct permissions:
```bash
python generate_meta_token.py
```

### Error: "API version mismatch"

**Solution:**
Update API version in `.env.meta`:
```env
META_API_VERSION=v19.0
```

Check latest version: [Meta API Versioning](https://developers.facebook.com/docs/graph-api/guides/versioning)

### Database Schema Errors

**Solution:**
```bash
# Reinitialize warehouse schema
python init_warehouse.py

# Then re-run ETL
python warehouse_meta_ads_etl.py --days=30
```

### No Data Showing in API

**Checklist:**
1. ✅ ETL completed successfully?
2. ✅ Data exists in database?
   ```bash
   python -c "import sqlite3; conn = sqlite3.connect('marketing_warehouse.db'); print(conn.execute('SELECT COUNT(*) FROM dim_meta_campaign').fetchone()[0])"
   ```
3. ✅ Using correct `customer_id` in API calls?
4. ✅ API server running?
5. ✅ Date range has data? (try `date_range=last_90d`)

---

## Token Types Explained

### Short-Lived User Token
- **Lifespan:** 1-2 hours
- **Use:** Testing, development
- **How to get:** Graph API Explorer
- **Limitations:** Expires quickly, requires frequent regeneration

### Long-Lived User Token
- **Lifespan:** 60 days
- **Use:** Production (with rotation)
- **How to get:** Exchange short-lived token via `generate_meta_token.py`
- **Limitations:** Still expires, needs rotation every 60 days

### System User Token (Recommended for Production)
- **Lifespan:** Never expires
- **Use:** Production, automated systems
- **How to get:**
  1. Go to [Business Settings > System Users](https://business.facebook.com/settings/system-users)
  2. Create System User
  3. Assign ad account access (Admin role)
  4. Generate token with required permissions
  5. Copy to `.env.meta`
- **Benefits:** No expiration, no rotation needed

---

## Required Permissions

When generating tokens, ensure these permissions:

| Permission | Purpose | Required? |
|------------|---------|-----------|
| `ads_read` | Read ads data (campaigns, ad sets, ads) | ✅ Yes |
| `ads_management` | Full access to manage ads | ✅ Yes |
| `read_insights` | Read performance metrics | ✅ Yes |
| `business_management` | Access business assets | Optional |
| `pages_read_engagement` | Read Page data | Optional |
| `instagram_basic` | Access Instagram insights | Optional |

---

## File Structure

```
ADS_API/
├── .env.meta                          # Your Meta credentials (DO NOT COMMIT)
├── .env.meta.example                  # Template
├── generate_meta_token.py             # Token generator
├── warehouse_meta_ads_etl.py          # Main ETL pipeline
├── warehouse_etl_helpers.py           # Shared warehouse utilities
├── warehouse_schema.sql               # Database schema
├── init_warehouse.py                  # Schema initialization
├── marketing_warehouse.db             # SQLite database (created by ETL)
├── show_warehouse_summary.py          # View warehouse data
├── META_ADS_SETUP_GUIDE.md           # This file
│
├── api/                               # REST API service
│   ├── app/
│   │   ├── routes/
│   │   │   └── meta.py               # Meta Ads API endpoints
│   │   ├── services/
│   │   │   └── meta_ads_service.py   # Meta API service layer
│   │   └── schemas/
│   │       └── meta.py               # Response schemas
│   └── main.py                       # FastAPI app
│
└── google-ads-multiagent/            # Multi-agent system
    └── adk/
        └── orchestration_agent/
            └── sub_agents/
                └── data_agent/
                    └── warehouse_client.py   # Warehouse queries
```

---

## Security Best Practices

1. **Never commit `.env.meta`** to git
   - Already in `.gitignore`
   - Contains sensitive credentials

2. **Use System User tokens in production**
   - Never expires
   - Can be easily revoked if compromised

3. **Rotate tokens periodically**
   - Even System User tokens should be rotated annually
   - Set calendar reminder

4. **Enable 2FA**
   - On your Facebook account
   - On Business Manager

5. **Use IP whitelisting** (if available)
   - In Meta App settings
   - Restrict to known IPs

6. **Monitor token usage**
   - Check [Business Settings > System Users](https://business.facebook.com/settings/system-users)
   - Review token activity logs

7. **Separate tokens per environment**
   - Development: `.env.meta.dev`
   - Production: `.env.meta.prod`

---

## Quick Reference Commands

```bash
# Generate access token
python generate_meta_token.py

# Run ETL (last 30 days)
python warehouse_meta_ads_etl.py --days=30

# Run ETL for specific customer
python warehouse_meta_ads_etl.py --customer-id=1 --days=30

# View warehouse data
python show_warehouse_summary.py

# Check database
sqlite3 marketing_warehouse.db "SELECT COUNT(*) FROM dim_meta_campaign;"

# Start API server
cd api && python -m uvicorn app.main:app --reload --port 8000

# Test API
curl "http://localhost:8000/api/v1/meta/campaigns?customer_id=1"

# Initialize warehouse schema
python init_warehouse.py
```

---

## Support Resources

### Official Documentation
- [Meta Marketing API](https://developers.facebook.com/docs/marketing-apis)
- [Meta Business SDK for Python](https://github.com/facebook/facebook-python-business-sdk)
- [Graph API Explorer](https://developers.facebook.com/tools/explorer/)
- [Access Token Debugger](https://developers.facebook.com/tools/debug/accesstoken/)

### Meta Business Resources
- [Business Manager](https://business.facebook.com)
- [Ads Manager](https://adsmanager.facebook.com)
- [Meta Developer Apps](https://developers.facebook.com/apps)

### Internal Documentation
- **Full Platform Setup:** `SETUP_GUIDE_FOR_BOSS.md`
- **Google Ads ETL:** `ETL_SETUP_GUIDE.md`
- **API Documentation:** `http://localhost:8000/docs` (when running)
- **Warehouse Status:** `WAREHOUSE_STATUS.md`

---

## Common Use Cases

### 1. Daily Performance Monitoring

```bash
# Run ETL every morning
python warehouse_meta_ads_etl.py --days=7

# View summary
python show_warehouse_summary.py

# Check API
curl "http://localhost:8000/api/v1/meta/insights/summary?customer_id=1&date_range=last_7d"
```

### 2. Campaign Performance Analysis

```python
# Query warehouse directly
import sqlite3
import pandas as pd

conn = sqlite3.connect('marketing_warehouse.db')

query = """
SELECT
    c.name AS campaign_name,
    SUM(f.impressions) AS total_impressions,
    SUM(f.clicks) AS total_clicks,
    SUM(f.spend_micros) / 1000000.0 AS total_spend,
    SUM(f.conversions) AS total_conversions,
    AVG(f.roas) AS avg_roas
FROM fact_campaign_performance_daily f
JOIN dim_meta_campaign c ON f.meta_campaign_id = c.meta_campaign_id
WHERE f.customer_id = 1
    AND f.date_id >= DATE('now', '-30 days')
GROUP BY c.name
ORDER BY total_spend DESC
"""

df = pd.read_sql_query(query, conn)
print(df)
```

### 3. Multi-Platform Comparison

```bash
# Compare Meta vs Google Ads
curl "http://localhost:8000/api/v1/meta/cross-platform/comparison?customer_id=1&days=30"
```

### 4. Demographic Analysis

```bash
# Get age/gender breakdown
curl "http://localhost:8000/api/v1/meta/insights/age-gender?customer_id=1&date_range=last_30d"

# Get country breakdown
curl "http://localhost:8000/api/v1/meta/insights/country?customer_id=1&date_range=last_30d"
```

---

## Setup Checklist

- [ ] Meta Business Manager access verified
- [ ] Meta app created
- [ ] App ID and App Secret saved
- [ ] Ad Account ID identified (with "act_" prefix)
- [ ] `.env.meta` file created and configured
- [ ] Python dependencies installed
- [ ] Access token generated (long-lived or System User)
- [ ] Token tested successfully
- [ ] ETL pipeline executed successfully
- [ ] Data verified in `marketing_warehouse.db`
- [ ] API server running
- [ ] API endpoints tested and returning data
- [ ] Scheduled task configured (optional)
- [ ] Backup/rotation plan for tokens (production)

---

## Next Steps

After setup:

1. **Integrate with Frontend:**
   - Update frontend to call Meta Ads API endpoints
   - Add Meta Ads dashboards
   - Implement customer filtering

2. **Setup Multi-Agent System:**
   - Configure Data Agent to query Meta data
   - Enable Insight Agent for Meta campaigns
   - Add Meta-specific optimization rules

3. **Schedule Regular Syncs:**
   - Daily ETL at 2 AM
   - Weekly full refresh
   - Monitor sync logs

4. **Monitor & Maintain:**
   - Check token expiration (if using user tokens)
   - Review API rate limits
   - Monitor data quality

---

**You're all set!** Meta Ads integration is now complete.

**Need help?** Check the troubleshooting section or official Meta documentation.

**Happy analyzing!** 📊
