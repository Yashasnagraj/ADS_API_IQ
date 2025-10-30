# MarketingIQ Google Ads Data Platform

Complete platform for Google Ads data extraction, analysis, and AI-powered insights. This repository contains:
- **ETL Pipeline** - Extracts Google Ads data into a data warehouse
- **Data API** - REST API to access the data
- **Multi-Agent System** - AI agents for insights and optimization
- **Web Dashboard** - React frontend for visualization and chat

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Overview](#quick-overview)
3. [Complete Setup Guide](#complete-setup-guide)
4. [Running the Platform](#running-the-platform)
5. [Architecture](#architecture)
6. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before starting, ensure you have:

### Required Software
- **Python 3.8+** ([Download](https://www.python.org/downloads/))
- **Node.js 18+** ([Download](https://nodejs.org/))
- **Git** ([Download](https://git-scm.com/))

### Required Accounts & Credentials
- **Google Ads Account** with API access
- **Google Ads API Developer Token** (apply at [Google Ads API Center](https://ads.google.com/aw/apicenter))
- **Google Cloud Project** with Ads API enabled
- **OAuth 2.0 Credentials** (Client ID & Secret)
- **Gemini API Key** (for AI features, get from [Google AI Studio](https://makersuite.google.com/app/apikey))

### Verify Installation
```bash
python --version  # Should be 3.8+
node --version    # Should be 18+
npm --version     # Should be 9+
git --version
```

---

## Quick Overview

This platform has 4 main components that work together:

```
┌─────────────────────────────────────────────────────────────┐
│                    YOUR LAPTOP SETUP                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. ETL Pipeline (warehouse_etl.py)                         │
│     ↓ Extracts data from Google Ads                        │
│     ↓ Stores in google_ads_data.db                         │
│                                                             │
│  2. Data API (api/)                                         │
│     ↓ Reads from google_ads_data.db                        │
│     ↓ Serves data via REST API (port 8000)                 │
│                                                             │
│  3. Multi-Agent System (google-ads-multiagent/)            │
│     ↓ AI Agents using Gemini                               │
│     ↓ Connects to Data API and database                    │
│     ↓ Serves chat API (port 8001)                          │
│                                                             │
│  4. Web Dashboard (marketingiq-platform/web/)              │
│     ↓ React frontend                                        │
│     ↓ Connects to Data API & Agent API                     │
│     ↓ Runs on port 3001                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Complete Setup Guide

Follow these steps **in order** to set up everything on your laptop.

### STEP 1: Clone the Repository

```bash
git clone <your-repo-url>
cd ADS_API
```

---

### STEP 2: Set Up ETL Pipeline (Data Warehouse)

This extracts Google Ads data and stores it in a local database.

#### 2.1 Install Python Dependencies
```bash
pip install -r requirements.txt
```

#### 2.2 Configure Google Ads Credentials

**Option A: If you already have credentials**
```bash
# Copy the template
cp google-ads.yaml.template google-ads.yaml

# Edit google-ads.yaml and add:
# - developer_token
# - client_id
# - client_secret
# - refresh_token
# - login_customer_id (your Manager Account ID)
```

**Option B: If you need to generate credentials**

1. Create Google Cloud Project:
   - Go to [Google Cloud Console](https://console.cloud.google.com)
   - Create new project: "MarketingIQ-API"
   - Enable Google Ads API

2. Create OAuth 2.0 Credentials:
   - Go to APIs & Services → Credentials
   - Create Credentials → OAuth 2.0 Client ID
   - Application type: **Desktop app**
   - Copy Client ID and Client Secret

3. Generate Refresh Token:
```bash
python generate_refresh_token.py
```
   - Browser will open
   - Sign in with your Google Ads account
   - Copy the refresh token displayed
   - Add to `google-ads.yaml`

#### 2.3 Run ETL Pipeline
```bash
python warehouse_etl.py
```

**What happens:**
- Connects to Google Ads API
- Extracts last 30 days of data
- Creates `google_ads_data.db` SQLite database
- Populates 5 tables: campaigns, ad groups, keywords, search terms, ML features

**Expected output:**
```
======================================================================
STARTING WAREHOUSE ETL PIPELINE
======================================================================
Processing customer: Your Business (1234567890)
----------------------------------------------------------------------
Extracting campaigns performance...
Loaded 25 records into campaigns_performance
Extracting ad groups performance...
Loaded 150 records into adgroups_performance
...
ETL PIPELINE COMPLETED SUCCESSFULLY
```

**Verify:**
```bash
# Check database was created
ls -lh google_ads_data.db

# Query the database
python -c "import sqlite3; conn = sqlite3.connect('google_ads_data.db'); print('Campaigns:', conn.execute('SELECT COUNT(*) FROM campaigns_performance').fetchone()[0])"
```

---

### STEP 3: Set Up Data API

This API reads from the database and serves data to the frontend.

```bash
# Navigate to API folder
cd api

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file (if not exists)
echo "DATABASE_URL=sqlite:///../google_ads_data.db" > .env
echo "CORS_ORIGINS=[\"http://localhost:3001\",\"http://localhost:3000\"]" >> .env

# Start the API server
uvicorn app.main:app --reload --port 8000
```

**Verify API is running:**
- Open browser: http://localhost:8000/health
- Should see: `{"status":"healthy"}`
- API docs: http://localhost:8000/docs

**Keep this terminal open** - API needs to keep running.

---

### STEP 4: Set Up Multi-Agent System (Chatbot/AI Agents)

This provides AI-powered insights using Google's Gemini.

**Open a NEW terminal** (keep API running in previous terminal).

```bash
cd google-ads-multiagent

# Create virtual environment
python -m venv venv

# Activate it
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

**Edit `google-ads-multiagent/.env`:**
```env
# Google Ads API (same credentials as root folder)
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_manager_id

# Gemini API Key (get from https://makersuite.google.com/app/apikey)
GEMINI_API_KEY=your_gemini_api_key

# Database path (points to root google_ads_data.db)
DATABASE_PATH=../google_ads_data.db

# LangSmith (optional - for debugging agents)
LANGCHAIN_TRACING_V2=false
LANGCHAIN_ENDPOINT=https://api.smith.langchain.com
LANGCHAIN_API_KEY=your_langsmith_key
LANGCHAIN_PROJECT=google-ads-agents
```

**Start the Agent API:**
```bash
python agent_api.py
```

**Verify agents are running:**
- Open browser: http://localhost:8001/health
- Should see: `{"status":"healthy","agents":5}`

**Keep this terminal open** - Agent API needs to keep running.

---

### STEP 5: Set Up Web Dashboard (Frontend)

This is the React web interface that connects everything together.

**Open a NEW terminal** (keep both APIs running).

```bash
cd marketingiq-platform/web

# Install Node.js dependencies
npm install --legacy-peer-deps

# Create .env file
echo "REACT_APP_API_URL=http://localhost:8000/api/v1" > .env
echo "REACT_APP_AGENT_API_URL=http://localhost:8001" >> .env

# Start development server
npm start
```

**What happens:**
- Webpack compiles React app
- Opens browser at http://localhost:3001
- Dashboard connects to both APIs

**Verify dashboard is working:**
- You should see the MarketingIQ dashboard
- Check browser console (F12) - no errors
- Click on different sections - data should load

**Keep this terminal open** - Frontend needs to keep running.

---

## Running the Platform

After initial setup, here's how to start everything:

### Daily Startup (4 terminals)

**Terminal 1 - Data API:**
```bash
cd api
source venv/bin/activate  # or venv\Scripts\activate on Windows
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 - Agent API:**
```bash
cd google-ads-multiagent
source venv/bin/activate  # or venv\Scripts\activate on Windows
python agent_api.py
```

**Terminal 3 - Frontend:**
```bash
cd marketingiq-platform/web
npm start
```

**Terminal 4 - Run ETL (optional - to refresh data):**
```bash
python warehouse_etl.py
```

### Quick Start Script (Windows)

Create `START_ALL.bat`:
```bat
@echo off
start cmd /k "cd api && venv\Scripts\activate && uvicorn app.main:app --reload --port 8000"
start cmd /k "cd google-ads-multiagent && venv\Scripts\activate && python agent_api.py"
start cmd /k "cd marketingiq-platform\web && npm start"
echo All services starting...
timeout /t 10
start http://localhost:3001
```

Run: `START_ALL.bat`

### Quick Start Script (Mac/Linux)

Create `start_all.sh`:
```bash
#!/bin/bash

# Start Data API
cd api && source venv/bin/activate && uvicorn app.main:app --reload --port 8000 &

# Start Agent API
cd ../google-ads-multiagent && source venv/bin/activate && python agent_api.py &

# Start Frontend
cd ../marketingiq-platform/web && npm start &

# Open browser
sleep 10
open http://localhost:3001  # macOS
# xdg-open http://localhost:3001  # Linux

wait
```

Make executable: `chmod +x start_all.sh`
Run: `./start_all.sh`

---

## Architecture

### System Components

```
┌──────────────────────────────────────────────────────────────┐
│                         FRONTEND                             │
│              marketingiq-platform/web/                       │
│                  (React + TypeScript)                        │
│                   Port: 3001                                 │
└───────────────────┬──────────────────────┬──────────────────┘
                    │                      │
            ┌───────▼─────────┐   ┌────────▼─────────┐
            │   DATA API      │   │  AGENT API       │
            │   api/          │   │  google-ads-     │
            │   (FastAPI)     │   │  multiagent/     │
            │   Port: 8000    │   │  (FastAPI)       │
            └────────┬────────┘   └────────┬─────────┘
                     │                     │
                     │    ┌────────────────┘
                     │    │
                ┌────▼────▼─────┐      ┌──────────────┐
                │  google_ads_  │      │  Google Ads  │
                │  data.db      │◄─────┤  API         │
                │  (SQLite)     │      └──────────────┘
                └───────────────┘             ▲
                                              │
                                    ┌─────────┴─────────┐
                                    │  warehouse_etl.py │
                                    │  (ETL Pipeline)   │
                                    └───────────────────┘
```

### Data Flow

1. **ETL Pipeline** (`warehouse_etl.py`)
   - Runs on-demand or scheduled
   - Connects to Google Ads API
   - Extracts data → Transforms → Loads into `google_ads_data.db`

2. **Data API** (`api/`)
   - FastAPI service on port 8000
   - Reads from `google_ads_data.db`
   - Serves REST endpoints for campaigns, keywords, metrics
   - Used by frontend for dashboards

3. **Agent API** (`google-ads-multiagent/`)
   - FastAPI service on port 8001
   - Connects to both database and Google Ads API
   - Runs 5 AI agents: Data, Insight, Optimization, Forecasting, Alert
   - Uses Google Gemini for natural language processing
   - Serves chat interface

4. **Frontend** (`marketingiq-platform/web/`)
   - React application on port 3001
   - Connects to both APIs
   - Provides dashboards, data explorer, and chat interface

### Port Reference

| Component | Port | URL |
|-----------|------|-----|
| Frontend Dashboard | 3001 | http://localhost:3001 |
| Data API | 8000 | http://localhost:8000 |
| Agent API (Chat) | 8001 | http://localhost:8001 |

---

## Database Schema

The ETL creates 5 tables with `customer_id` for multi-customer filtering:

### 1. campaigns_performance
Campaign-level metrics and configuration.
- **Fields:** campaign_id, customer_id, campaign_name, status, channel_type, bidding_strategy, budget_amount, date, impressions, clicks, cost, conversions, ctr, cpc, roas, etc.

### 2. adgroups_performance
Ad group structure and metrics.
- **Fields:** ad_group_id, campaign_id, customer_id, ad_group_name, status, ad_group_type, date, impressions, clicks, cost, conversions, ctr, cpc, etc.

### 3. keywords_performance
Keyword-level targeting and performance.
- **Fields:** keyword_id, ad_group_id, campaign_id, customer_id, keyword_text, match_type, status, quality_score, max_cpc, date, impressions, clicks, cost, conversions, etc.

### 4. search_terms
Actual user search queries.
- **Fields:** search_term, keyword_id, campaign_id, customer_id, match_type, date, impressions, clicks, cost, conversions, ctr, conversion_rate, etc.

### 5. ml_features
Pre-processed features for machine learning.
- **Fields:** customer_id, campaign_id, keyword_id, keyword_text, match_type, quality_score, avg_cpc, ctr, conversion_rate, cost, impressions, clicks, competition_index, search_volume_trend, etc.

---

## Multi-Agent System

The platform includes 5 AI agents powered by Google Gemini:

### 1. Data Agent
**Purpose:** Query and retrieve Google Ads data
**Capabilities:**
- Fetch campaigns, ad groups, keywords
- Get performance metrics
- Filter by date, status, customer

### 2. Insight Agent
**Purpose:** Analyze performance and detect anomalies
**Capabilities:**
- Identify underperforming campaigns
- Detect CTR drops, cost spikes
- Compare metrics against benchmarks

### 3. Optimization Agent
**Purpose:** Provide actionable recommendations
**Capabilities:**
- Budget reallocation suggestions
- Keyword bid adjustments
- Campaign structure improvements

### 4. Forecasting Agent
**Purpose:** Predict future performance
**Capabilities:**
- 7-day spend forecasts
- CTR predictions
- Conversion projections

### 5. Alert Agent
**Purpose:** Monitor and alert on critical issues
**Capabilities:**
- Budget overspend alerts
- Quality score drops
- Conversion rate anomalies

### Using the Agents

**Via Web Chat:**
```
User: "Show me my top 5 campaigns by spend"
Data Agent: [Returns campaign list with spend metrics]

User: "Why is my CTR dropping?"
Insight Agent: [Analyzes trends and identifies causes]

User: "How should I optimize my budget?"
Optimization Agent: [Provides recommendations]
```

**Via API:**
```bash
curl -X POST http://localhost:8001/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Show me campaigns with CTR below 2%"}'
```

---

## API Endpoints

### Data API (Port 8000)

**Health Check:**
```
GET /health
```

**Campaigns:**
```
GET /api/v1/campaigns?customer_id=123
GET /api/v1/campaigns/{id}
GET /api/v1/campaigns/{id}/performance
```

**Keywords:**
```
GET /api/v1/keywords?customer_id=123
GET /api/v1/keywords/performance?campaign_id=456
GET /api/v1/keywords/top?limit=10
```

**Metrics:**
```
GET /api/v1/metrics/summary?customer_id=123
GET /api/v1/metrics/timeseries?days=30
```

**Search Terms:**
```
GET /api/v1/search-terms?campaign_id=456
GET /api/v1/search-terms/top
```

**ML Features:**
```
GET /api/v1/ml-features?customer_id=123
```

**Full documentation:** http://localhost:8000/docs

### Agent API (Port 8001)

**Chat with AI Agents:**
```
POST /chat
Body: {"message": "your question", "customer_id": "123"}
```

**Get Agent Status:**
```
GET /agents
```

**Query Specific Agent:**
```
POST /agents/{agent_name}/query
Body: {"query": "your question"}
```

**Full documentation:** http://localhost:8001/docs

---

## Troubleshooting

### Problem: "Module not found" errors

**Solution:**
```bash
# For Python:
pip install -r requirements.txt

# For Node.js:
cd marketingiq-platform/web
npm install --legacy-peer-deps
```

### Problem: API returns empty data

**Check:**
1. ETL ran successfully: `python warehouse_etl.py`
2. Database exists: `ls -lh google_ads_data.db`
3. Database has data:
```bash
python -c "import sqlite3; conn = sqlite3.connect('google_ads_data.db'); print('Campaigns:', conn.execute('SELECT COUNT(*) FROM campaigns_performance').fetchone()[0])"
```

### Problem: "Authentication failed" when running ETL

**Solutions:**
- Verify `google-ads.yaml` has correct credentials
- Check developer token is approved (not in "test" mode)
- Regenerate refresh token: `python generate_refresh_token.py`
- Ensure `login_customer_id` is your Manager Account ID

### Problem: "Database is locked"

**Solution:**
```bash
# Close all connections
# Kill any running Python processes
# Delete and recreate database
rm google_ads_data.db
python warehouse_etl.py
```

### Problem: Frontend shows CORS errors

**Check:**
1. Data API is running on port 8000
2. Agent API is running on port 8001
3. Check `api/.env` has correct CORS origins:
```env
CORS_ORIGINS=["http://localhost:3001","http://localhost:3000"]
```

### Problem: "process is not defined" in frontend

**Solution:**
```bash
# Clear cache and rebuild
cd marketingiq-platform/web
rm -rf node_modules dist
npm install --legacy-peer-deps
npm start
```

### Problem: Gemini API errors

**Check:**
1. `GEMINI_API_KEY` is set in `google-ads-multiagent/.env`
2. API key is valid: https://makersuite.google.com/app/apikey
3. Gemini API is enabled in your Google Cloud project

### Problem: Port already in use

**Find and kill process:**
```bash
# Windows:
netstat -ano | findstr :8000
taskkill /PID <process_id> /F

# Mac/Linux:
lsof -ti:8000 | xargs kill -9
```

### Problem: ETL extracts no data

**Check:**
1. Google Ads account has campaigns
2. Campaigns have data in last 30 days
3. Manager account has access to client accounts
4. API credentials have correct permissions

---

## Project Structure

```
ADS_API/
│
├── warehouse_etl.py              # ETL pipeline (main script)
├── generate_refresh_token.py     # OAuth token generator
├── requirements.txt              # ETL Python dependencies
├── google-ads.yaml.template      # Config template
├── google-ads.yaml               # Your credentials (DO NOT COMMIT)
├── google_ads_data.db            # SQLite database (created by ETL)
│
├── README.md                     # This file
├── ETL_SETUP_GUIDE.md            # Simple ETL-only setup
├── ETL_STATUS_REPORT.md          # Cloud deployment status
├── SETUP_GUIDE_FOR_BOSS.md       # Alternative setup guide
├── CLAUDE.md                     # AI assistant instructions
│
├── api/                          # DATA API (FastAPI)
│   ├── app/
│   │   ├── main.py               # FastAPI app
│   │   ├── routes/               # API endpoints
│   │   ├── schemas/              # Pydantic models
│   │   └── db/                   # Database models
│   ├── requirements.txt          # API dependencies
│   └── .env                      # API config
│
├── google-ads-multiagent/        # AGENT API (Multi-Agent System)
│   ├── agent_api.py              # Agent FastAPI server
│   ├── main.py                   # Agent orchestration
│   ├── adk/                      # Agent Development Kit
│   ├── src/                      # Agent implementations
│   │   └── agents/               # 5 AI agents
│   ├── requirements.txt          # Agent dependencies
│   └── .env                      # Agent config (Gemini API key)
│
└── marketingiq-platform/         # FRONTEND
    ├── web/                      # React Dashboard
    │   ├── src/
    │   │   ├── components/       # React components
    │   │   ├── pages/            # Dashboard pages
    │   │   ├── hooks/            # Custom React hooks
    │   │   └── config/           # API configuration
    │   ├── package.json          # Node dependencies
    │   ├── webpack.config.js     # Build config
    │   └── .env                  # Frontend config
    │
    └── server/                   # Additional backend
        └── api.py                # Supplementary API
```

---

## Environment Variables Reference

### Root `.env` (for ETL)
```env
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_manager_id
```

### `api/.env` (Data API)
```env
DATABASE_URL=sqlite:///../google_ads_data.db
CORS_ORIGINS=["http://localhost:3001","http://localhost:3000"]
DEBUG=true
LOG_LEVEL=INFO
```

### `google-ads-multiagent/.env` (Agent API)
```env
GOOGLE_ADS_DEVELOPER_TOKEN=your_token
GOOGLE_ADS_CLIENT_ID=your_client_id
GOOGLE_ADS_CLIENT_SECRET=your_secret
GOOGLE_ADS_REFRESH_TOKEN=your_refresh_token
GOOGLE_ADS_LOGIN_CUSTOMER_ID=your_manager_id

GEMINI_API_KEY=your_gemini_api_key
DATABASE_PATH=../google_ads_data.db

LANGCHAIN_TRACING_V2=false
LANGCHAIN_API_KEY=optional
LANGCHAIN_PROJECT=google-ads-agents
```

### `marketingiq-platform/web/.env` (Frontend)
```env
REACT_APP_API_URL=http://localhost:8000/api/v1
REACT_APP_AGENT_API_URL=http://localhost:8001
NODE_ENV=development
```

---

## Getting Help

### Documentation Files
- **ETL_SETUP_GUIDE.md** - ETL pipeline only setup
- **SETUP_GUIDE_FOR_BOSS.md** - Alternative setup guide
- **ETL_STATUS_REPORT.md** - Cloud deployment status
- **marketingiq-platform/web/README.md** - Frontend docs
- **google-ads-multiagent/README.md** - Agent system docs

### API Documentation
- Data API docs: http://localhost:8000/docs
- Agent API docs: http://localhost:8001/docs

### External Resources
- [Google Ads API Docs](https://developers.google.com/google-ads/api)
- [FastAPI Docs](https://fastapi.tiangolo.com)
- [React Docs](https://react.dev)
- [LangChain Docs](https://docs.langchain.com)

---

## Quick Command Reference

### ETL Commands
```bash
# Run ETL pipeline
python warehouse_etl.py

# Generate OAuth token
python generate_refresh_token.py

# Query database
python -c "import sqlite3; conn = sqlite3.connect('google_ads_data.db'); print(conn.execute('SELECT * FROM campaigns_performance LIMIT 5').fetchall())"
```

### API Commands
```bash
# Start Data API
cd api && uvicorn app.main:app --reload --port 8000

# Start Agent API
cd google-ads-multiagent && python agent_api.py

# Test API
curl http://localhost:8000/health
curl http://localhost:8001/health
```

### Frontend Commands
```bash
# Install dependencies
cd marketingiq-platform/web && npm install --legacy-peer-deps

# Start dev server
npm start

# Build for production
npm run build

# Clear cache
rm -rf node_modules dist && npm install --legacy-peer-deps
```

---

## Security Notes

- **Never commit** `google-ads.yaml` or `.env` files
- Keep API keys secure and rotate regularly
- Use environment variables for credentials
- Enable HTTPS in production
- Implement rate limiting for public APIs
- Review Google Ads API usage limits

---

## Data Statistics (Example)

After running ETL, you should have:
- **19** Active Campaigns
- **542** Keywords tracked
- **199** Search terms analyzed
- **511** ML features generated
- **$5,114** Total spend tracked
- **6** Conversions recorded

*(Your numbers will vary based on your Google Ads account)*

---

## Contributing

This is a proprietary project. For internal development:
1. Create feature branch
2. Make changes
3. Test thoroughly
4. Submit for review

---

## Support & Contacts

- **Technical Issues**: Check Troubleshooting section
- **ETL Questions**: See ETL_SETUP_GUIDE.md
- **API Issues**: Check API documentation at `/docs` endpoints
- **Frontend Issues**: See marketingiq-platform/web/README.md

---

**Built with:**
- Python 3.11 | FastAPI | SQLAlchemy | Pandas
- React 18 | TypeScript | Material-UI | Recharts
- LangChain | LangGraph | Google Gemini
- Google Ads API | SQLite

**Last Updated:** October 2024

---

**Ready to start?** Follow the [Complete Setup Guide](#complete-setup-guide) above step by step!
