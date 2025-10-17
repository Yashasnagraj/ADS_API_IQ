# Google Ads ETL Pipeline - Setup Guide

Simple guide to set up and run the Google Ads data extraction pipeline.

---

## What This Does

Extracts Google Ads data (campaigns, ad groups, keywords, search terms) from your Google Ads account and stores it in a SQLite database for analysis.

---

## Prerequisites

- **Python 3.8+** installed
- **Google Ads API credentials** (developer token, client ID, client secret, refresh token)
- **Google Ads Manager Account** access

---

## Quick Setup (5 Steps)

### Step 1: Install Python Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Configure Google Ads Credentials

Copy the template:
```bash
cp google-ads.yaml.template google-ads.yaml
```

Edit `google-ads.yaml` with your credentials:
```yaml
developer_token: YOUR_DEVELOPER_TOKEN
client_id: YOUR_CLIENT_ID.apps.googleusercontent.com
client_secret: YOUR_CLIENT_SECRET
refresh_token: YOUR_REFRESH_TOKEN
login_customer_id: YOUR_MANAGER_ACCOUNT_ID
```

### Step 3: Generate Refresh Token (First Time Only)

If you don't have a refresh token yet:

```bash
python generate_refresh_token.py
```

This will:
- Open browser for Google login
- Ask for Google Ads API permissions
- Display your refresh token
- Copy the refresh token to `google-ads.yaml`

### Step 4: Run the ETL Pipeline

```bash
python warehouse_etl.py
```

This will:
- Connect to Google Ads API
- Fetch all accessible customer accounts
- Extract last 30 days of data
- Store in `google_ads_data.db`

**Expected output:**
```
======================================================================
STARTING WAREHOUSE ETL PIPELINE
======================================================================

Processing customer: Your Business (1234567890)
----------------------------------------------------------------------
Extracting campaigns performance...
Extracting ad groups performance...
Extracting keywords performance...
Extracting search terms...
Loaded X records into campaigns_performance
Loaded X records into adgroups_performance
Loaded X records into keywords_performance
Loaded X records into search_terms

Generating ML features...
Generated X ML features

======================================================================
ETL PIPELINE COMPLETED SUCCESSFULLY
======================================================================
```

### Step 5: Verify Data

Check the database:
```bash
python -c "import sqlite3; conn = sqlite3.connect('google_ads_data.db'); print('Campaigns:', conn.execute('SELECT COUNT(*) FROM campaigns_performance').fetchone()[0]); conn.close()"
```

---

## Database Schema

The ETL creates 5 tables:

1. **campaigns_performance** - Campaign metrics and config
   - Fields: campaign_id, customer_id, campaign_name, status, channel_type, impressions, clicks, cost, conversions, etc.

2. **adgroups_performance** - Ad group metrics
   - Fields: ad_group_id, campaign_id, customer_id, ad_group_name, impressions, clicks, cost, etc.

3. **keywords_performance** - Keyword-level data
   - Fields: keyword_id, ad_group_id, keyword_text, match_type, quality_score, impressions, clicks, cost, etc.

4. **search_terms** - User search queries
   - Fields: search_term, keyword_id, campaign_id, impressions, clicks, cost, conversions, etc.

5. **ml_features** - Pre-processed features for ML
   - Denormalized table combining campaign + keyword data for machine learning

All tables include `customer_id` for multi-customer filtering.

---

## File Structure

```
ADS_API/
├── warehouse_etl.py              # Main ETL pipeline
├── requirements.txt              # Python dependencies
├── google-ads.yaml.template      # Config template
├── google-ads.yaml              # Your credentials (DO NOT COMMIT)
├── generate_refresh_token.py     # OAuth token generator
├── google_ads_data.db           # SQLite database (created by ETL)
├── README.md                    # Project overview
├── ETL_STATUS_REPORT.md         # Current deployment status
├── SETUP_GUIDE_FOR_BOSS.md      # Full platform setup (frontend + backend)
└── api/                         # REST API service (optional)
```

---

## Deployment to Google Cloud Run

For production deployment, see: **ETL_STATUS_REPORT.md**

Quick deploy:
```bash
./deploy-etl.sh
```

This uses `cloudbuild.yaml` to deploy the ETL as a Cloud Run service.

---

## Troubleshooting

### Error: "Authentication failed"

**Solution:**
- Verify credentials in `google-ads.yaml`
- Check developer token is approved
- Regenerate refresh token if expired: `python generate_refresh_token.py`

### Error: "No accessible customers found"

**Solution:**
- Verify `login_customer_id` is your Manager Account ID
- Check you have access to client accounts
- Ensure accounts are not suspended

### Error: "API version mismatch"

**Solution:**
- The pipeline uses Google Ads API v16
- If error persists, check `ETL_STATUS_REPORT.md` for latest version info

### Database locked

**Solution:**
- Close any open database connections
- Delete `google_ads_data.db` and run ETL again

---

## Running ETL on Schedule

### Option 1: Cloud Scheduler (Production)

Deploy to Cloud Run, then:
```bash
gcloud scheduler jobs create http etl-daily \
  --schedule="0 2 * * *" \
  --uri="https://your-etl-service.run.app" \
  --http-method=POST
```

### Option 2: Local Cron (Development)

Linux/Mac:
```bash
# Add to crontab
0 2 * * * cd /path/to/ADS_API && python warehouse_etl.py
```

Windows Task Scheduler:
- Create task
- Trigger: Daily at 2:00 AM
- Action: Start program `python.exe`
- Arguments: `warehouse_etl.py`
- Start in: `D:\ADS_API`

---

## API Service (Optional)

To expose the data via REST API:

```bash
cd api
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

API will be available at: `http://localhost:8000`

Documentation: `http://localhost:8000/docs`

---

## Support

- **ETL Issues**: Check `ETL_STATUS_REPORT.md`
- **Full Platform Setup**: See `SETUP_GUIDE_FOR_BOSS.md`
- **Google Ads API Docs**: https://developers.google.com/google-ads/api

---

## Quick Reference

```bash
# Install dependencies
pip install -r requirements.txt

# Generate OAuth token
python generate_refresh_token.py

# Run ETL
python warehouse_etl.py

# Query database
python -c "import sqlite3; conn = sqlite3.connect('google_ads_data.db'); print(conn.execute('SELECT * FROM campaigns_performance LIMIT 5').fetchall())"

# Deploy to Cloud Run
./deploy-etl.sh
```

---

**That's it!** Your ETL pipeline should now be running and populating the database with Google Ads data.
