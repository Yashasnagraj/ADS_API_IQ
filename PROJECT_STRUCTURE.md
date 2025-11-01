# Marketing IQ Platform - Project Structure

**Professional Multi-Platform Marketing Analytics & AI Platform**

## Overview

Marketing IQ is an enterprise-grade analytics platform that integrates Google Ads, Meta Ads, GA4, and Shopify data with AI-powered insights, optimization recommendations, and forecasting capabilities.

## Core Components

### 1. Backend API (`/api`)
- **Technology**: FastAPI (Python)
- **Port**: 8000
- **Features**:
  - RESTful API for all platform data
  - Multi-customer support with filtering
  - AI Intelligence services (PIE model, insights, optimization, forecasting, alerts)
  - Integration with Google Ads API, Meta Ads API, GA4 API
  - Data warehouse queries via SQLAlchemy

**Start**: `cd api && uvicorn app.main:app --reload --port 8000`

### 2. Frontend Dashboard (`/marketingiq-platform/web`)
- **Technology**: React + TypeScript + Material-UI
- **Port**: 5173 (Vite dev server)
- **Features**:
  - Unified cross-platform dashboard
  - Google Ads, Meta Ads, GA4, Shopify dashboards
  - Agent-specific dashboards (Data, Insights, Optimization, Forecasting, Alerts)
  - AI chatbot with floating button
  - Global filtering (customer, date range, campaign type)
  - Responsive design with dark theme

**Start**: `cd marketingiq-platform/web && npm run dev`

### 3. AI Multi-Agent System (`/google-ads-multiagent/adk`)
- **Technology**: Google ADK + Gemini 2.5 Flash
- **Port**: 8003 (Chatbot API)
- **Agents**:
  - **Data Agent**: Fetches campaign, keyword, ad group performance
  - **Insight Agent**: Analyzes trends, detects anomalies
  - **Optimization Agent**: Recommends budget and bid optimizations
  - **Forecasting Agent**: Predicts future performance
  - **Alert Agent**: Monitors threshold breaches

**Start**: `cd google-ads-multiagent/adk && python chatbot_api.py`

### 4. Data Warehouse (`marketing_warehouse.db`)
- **Technology**: SQLite (Star schema)
- **Size**: ~1.2 MB
- **Tables**:
  - Dimension tables: `dim_customer`, `dim_google_ads_campaign`, `dim_keyword`, `dim_ad_group`
  - Fact tables: `fact_campaign_performance_daily`, `fact_keyword_performance`
  - Meta Ads: `meta_campaigns`, `meta_insights`
  - GA4: `ga4_sessions`, `ga4_events`
  - Shopify: `shopify_orders`, `shopify_products`

---

## Project Structure

```
D:\ADS_API\
│
├── api/                              # Backend API
│   ├── app/
│   │   ├── routes/                   # API endpoints
│   │   ├── services/                 # Business logic
│   │   │   ├── ai/                   # AI Intelligence services
│   │   │   ├── google_ads_service.py
│   │   │   ├── meta_ads_service.py
│   │   │   └── ga4_service.py
│   │   ├── models/                   # SQLAlchemy models
│   │   └── main.py                   # FastAPI app entry
│   └── requirements.txt
│
├── marketingiq-platform/             # Frontend
│   └── web/
│       ├── src/
│       │   ├── components/
│       │   │   ├── chat/             # AI Chatbot
│       │   │   ├── dashboard/        # Platform dashboards
│       │   │   ├── dashboards/       # Agent dashboards
│       │   │   ├── common/           # Shared components
│       │   │   └── landing/          # Landing page
│       │   ├── services/             # API client services
│       │   ├── context/              # React context (filters)
│       │   └── types/                # TypeScript types
│       └── package.json
│
├── google-ads-multiagent/            # AI Multi-Agent System
│   └── adk/
│       ├── chatbot_api.py            # Chatbot FastAPI server
│       ├── orchestration_agent/      # ADK agents
│       │   ├── agent.py              # Root agent
│       │   └── sub_agents/           # Specialized agents
│       │       ├── data_agent/
│       │       ├── insight_agent/
│       │       ├── optimization_agent/
│       │       └── forecasting_agent/
│       └── .env                      # Gemini API key
│
├── ETL Scripts                       # Data Pipeline
│   ├── warehouse_etl.py              # Main ETL orchestrator
│   ├── warehouse_google_ads_etl.py   # Google Ads data ingestion
│   ├── warehouse_meta_ads_etl.py     # Meta Ads data ingestion
│   ├── warehouse_ga4_etl.py          # GA4 data ingestion
│   ├── warehouse_etl_helpers.py      # ETL utilities
│   ├── ga4_etl.py                    # GA4 standalone ETL
│   ├── meta_ads_etl.py               # Meta Ads standalone ETL
│   ├── shopify_etl.py                # Shopify data ingestion
│   └── init_warehouse.py             # Warehouse initialization
│
├── Setup Scripts                     # Environment Setup
│   ├── setup_ga4.py                  # GA4 authentication setup
│   ├── setup_meta_ads.py             # Meta Ads authentication
│   └── setup_shopify.py              # Shopify configuration
│
├── Startup Scripts                   # Server Management
│   ├── START_ALL_SERVERS.bat         # Start backend + chatbot + frontend (Windows)
│   ├── START_BACKEND.bat             # Start backend only
│   ├── START_ALL.bat                 # Start all services (legacy)
│   ├── start_all.sh                  # Start all (Linux/Mac)
│   └── stop_all.sh                   # Stop all services
│
├── Configuration Files
│   ├── .env                          # Google Ads API credentials
│   ├── .env.meta                     # Meta Ads API credentials
│   ├── .env.ga4                      # GA4 API credentials
│   ├── .env.example                  # Example environment file
│   ├── google-ads.yaml               # Google Ads API config
│   ├── requirements.txt              # Python dependencies
│   └── warehouse_schema.sql          # Database schema
│
├── Deployment
│   ├── cloudbuild.yaml               # Google Cloud Build config
│   ├── deploy-etl.sh                 # ETL deployment script
│   ├── .dockerignore                 # Docker ignore rules
│   └── .gcloudignore                 # Google Cloud ignore rules
│
├── Credentials & Secrets
│   ├── credentials/                  # API credentials (Google, Meta, GA4)
│   └── secrets/                      # OAuth tokens and secrets
│
├── Data & Logs
│   ├── marketing_warehouse.db        # Main production database
│   └── logs/                         # Application logs
│
└── Documentation
    ├── README.md                     # Main project documentation
    ├── CHATBOT_SETUP.md              # AI Chatbot setup guide
    ├── CLAUDE.md                     # Development instructions
    └── PROJECT_STRUCTURE.md          # This file

```

---

## Quick Start

### One-Command Start (Recommended)
```bash
# Windows
START_ALL_SERVERS.bat

# Linux/Mac
./start_all.sh
```

This starts:
1. Backend API → http://localhost:8000
2. Chatbot API → http://localhost:8003
3. Frontend → http://localhost:5173

### Manual Start
```bash
# Terminal 1 - Backend API
cd api
uvicorn app.main:app --reload --port 8000

# Terminal 2 - Chatbot API
cd google-ads-multiagent/adk
python chatbot_api.py

# Terminal 3 - Frontend
cd marketingiq-platform/web
npm run dev
```

---

## Key Features

### Multi-Platform Analytics
- **Google Ads**: Campaigns, keywords, ad groups, search terms
- **Meta Ads**: Campaigns, ad sets, ads, insights
- **GA4**: Sessions, events, conversions, user behavior
- **Shopify**: Orders, products, customers, cart events

### AI Intelligence
- **PIE Model**: Incremental ROAS calculation
- **Anomaly Detection**: Identifies performance issues
- **Budget Optimization**: AI-powered budget allocation
- **Forecasting**: Predictive performance modeling
- **Alert System**: Threshold-based monitoring

### AI Chatbot
- Natural language queries
- Context-aware responses (customer, date range)
- Markdown-formatted answers
- Powered by Gemini 2.5 Flash
- Analytics icon and professional UI

### Global Filtering
- Customer selection
- Date range picker
- Campaign type filter (Search/Ecommerce/B2B)
- All dashboards react to filter changes

---

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - ORM for database queries
- **Pydantic** - Data validation
- **Google Ads API** - Campaign data
- **Meta Marketing API** - Facebook/Instagram ads
- **Google Analytics Data API** - GA4 data
- **Shopify API** - E-commerce data

### Frontend
- **React 19** - UI framework
- **TypeScript** - Type safety
- **Material-UI v5** - Component library
- **Recharts** - Data visualization
- **Axios** - HTTP client
- **React Router** - Navigation
- **Framer Motion** - Animations

### AI & ML
- **Google ADK** - Multi-agent orchestration
- **Gemini 2.5 Flash** - AI responses
- **LangChain** - Agent framework
- **SKLearn** - Machine learning models

### Database
- **SQLite** - Data warehouse
- **Star Schema** - Analytics-optimized design

---

## API Endpoints

### Warehouse Endpoints
- `GET /api/v1/warehouse/metrics` - Cross-platform metrics
- `GET /api/v1/warehouse/google-ads-performance` - Google Ads data
- `GET /api/v1/warehouse/meta-ads-performance` - Meta Ads data
- `GET /api/v1/warehouse/ga4-metrics` - GA4 analytics

### AI Endpoints
- `GET /api/v1/ai/daily-insights` - Daily AI insights
- `GET /api/v1/ai/incrementality` - PIE model results
- `GET /api/v1/ai/anomalies` - Anomaly detection
- `GET /api/v1/ai/budget-optimization` - Budget recommendations
- `GET /api/v1/ai/spend-forecast` - Performance forecasts

### Campaigns & Keywords
- `GET /api/v1/campaigns` - Campaign list
- `GET /api/v1/campaigns/{id}/performance` - Campaign details
- `GET /api/v1/keywords/performance` - Keyword metrics
- `GET /api/v1/adgroups` - Ad group data

### Chatbot
- `POST /api/chat` - Send message to AI chatbot
- `GET /health` - Chatbot health check
- `GET /api/agents` - List available agents

**Full API Docs**: http://localhost:8000/docs

---

## Environment Variables

### Required
```bash
# Google Ads API (.env)
GOOGLE_ADS_DEVELOPER_TOKEN=xxx
GOOGLE_ADS_CLIENT_ID=xxx
GOOGLE_ADS_CLIENT_SECRET=xxx
GOOGLE_ADS_REFRESH_TOKEN=xxx
GOOGLE_ADS_LOGIN_CUSTOMER_ID=xxx

# Meta Ads API (.env.meta)
META_ACCESS_TOKEN=xxx
META_APP_ID=xxx
META_APP_SECRET=xxx
META_AD_ACCOUNT_ID=xxx

# GA4 API (.env.ga4)
GA4_PROPERTY_ID=xxx
GA4_CREDENTIALS_PATH=credentials/ga4-credentials.json

# Gemini AI (google-ads-multiagent/adk/.env)
GOOGLE_API_KEY=xxx
```

---

## Data Flow

```
External APIs                  ETL Pipeline              Warehouse              Backend API           Frontend
─────────────────             ───────────────           ─────────────          ────────────          ──────────
Google Ads API      ──────>   warehouse_google_ads_etl  ──────>   dim_google_ads_campaign   ──────>   /api/v1/warehouse   ──────>   Dashboard
Meta Marketing API  ──────>   warehouse_meta_ads_etl    ──────>   meta_insights             ──────>   /api/v1/warehouse   ──────>   Components
GA4 Data API        ──────>   warehouse_ga4_etl         ──────>   ga4_sessions              ──────>   /api/v1/warehouse   ──────>   Charts
Shopify API         ──────>   shopify_etl               ──────>   shopify_orders            ──────>   /api/v1/shopify     ──────>   Reports

                                                                   marketing_warehouse.db
                                                                   (Star Schema)

                                                                   ↓

                                                                   AI Services
                                                                   - PIE Model
                                                                   - Insights
                                                                   - Forecasting

                                                                   ↓

                                                                   ADK Chatbot
                                                                   (Multi-Agent)
```

---

## Deployment

### Development
```bash
# Clone repository
git clone <repository-url>
cd ADS_API

# Install backend dependencies
cd api
pip install -r requirements.txt

# Install frontend dependencies
cd ../marketingiq-platform/web
npm install

# Configure environment
cp .env.example .env
# Edit .env with your credentials

# Initialize warehouse
python init_warehouse.py

# Start all servers
START_ALL_SERVERS.bat
```

### Production (Google Cloud)
```bash
# Deploy ETL pipeline
./deploy-etl.sh

# Build and deploy
gcloud builds submit --config cloudbuild.yaml
```

---

## Security Notes

### Credentials Management
- All API credentials stored in `/credentials` and `/secrets`
- These folders are **git-ignored** for security
- Use `.env` files for environment-specific configuration
- Never commit credentials to version control

### API Keys
- Google Ads API key in `.env`
- Meta Ads access token in `.env.meta`
- GA4 service account in `credentials/ga4-credentials.json`
- Gemini API key in `google-ads-multiagent/adk/.env`

---

## Maintenance

### Database Backup
```bash
# Manual backup
cp marketing_warehouse.db marketing_warehouse_backup_$(date +%Y%m%d).db
```

### ETL Refresh
```bash
# Full warehouse refresh
python warehouse_etl.py

# Individual platform refresh
python warehouse_google_ads_etl.py
python warehouse_meta_ads_etl.py
python warehouse_ga4_etl.py
```

### Logs
- Backend logs: `logs/api.log`
- ETL logs: `logs/etl.log`
- Chatbot logs: Console output

---

## Support & Contact

For technical questions or issues, refer to:
- **README.md** - General project information
- **CHATBOT_SETUP.md** - AI chatbot configuration
- **API Documentation** - http://localhost:8000/docs

---

**Built with Professional Standards for Enterprise Marketing Analytics**
