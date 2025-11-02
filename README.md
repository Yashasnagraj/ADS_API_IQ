# Marketing IQ Platform

**Enterprise Multi-Platform Marketing Analytics with AI Intelligence**

---

## Vision

Marketing IQ is designed to solve the fragmentation problem in digital marketing analytics. Modern marketing teams run campaigns across multiple platforms - Google Ads, Meta Ads, Google Analytics, Shopify - but struggle to get a unified view of performance and actionable insights.

**Our Mission**: Consolidate all marketing data into one intelligent platform that not only shows what happened, but explains why it happened, predicts what will happen next, and recommends what to do about it.

### Why Marketing IQ?

**The Problem**:
- Marketing data scattered across 4+ platforms
- No single source of truth for performance
- Insights require manual analysis and technical expertise
- Optimization decisions based on gut feeling, not AI
- Incremental impact of campaigns difficult to measure

**Our Solution**:
- **Unified Data Warehouse** - All platforms in one star-schema database
- **AI-Powered Insights** - Natural language chatbot + automated analysis
- **Multi-Agent Intelligence** - Specialized AI agents for different tasks
- **Cross-Platform Attribution** - Understand true incremental impact
- **Predictive Forecasting** - Know what's coming before it happens
- **Automated Optimization** - AI recommends budget and bid changes

---

## What We Built

### 1. Multi-Platform Data Integration

**Platforms Integrated**:
- **Google Ads**: Campaigns, keywords, ad groups, search terms, quality scores
- **Meta Ads** (Facebook/Instagram): Campaigns, ad sets, ads, insights, demographics
- **Google Analytics 4**: Sessions, events, conversions, user paths, audiences
- **Shopify**: Orders, products, customers, cart events, revenue attribution

**Data Warehouse Architecture**:
- Star schema design optimized for analytics queries
- Daily automated ETL pipeline
- Multi-customer support (agency-ready)
- Historical data retention
- Real-time performance metrics

### 2. AI Multi-Agent System

Built on **Google ADK** (Agent Development Kit) with **Gemini 2.5 Flash**:

**Data Agent**:
- Fetches campaign performance across all platforms
- Retrieves keyword and ad group metrics
- Queries historical trends and patterns

**Insight Agent**:
- Analyzes performance trends automatically
- Detects anomalies in spend, clicks, conversions
- Identifies underperforming campaigns and keywords
- Provides diagnostic explanations (not just numbers)

**Optimization Agent**:
- Recommends budget reallocation across campaigns
- Suggests bid adjustments for keywords
- Prioritizes optimization opportunities by impact
- Calculates expected ROI of changes

**Forecasting Agent**:
- Predicts next 30-day performance
- Forecasts spend, clicks, conversions, revenue
- Models scenario outcomes ("what if" analysis)
- Identifies growth opportunities

**Alert Agent**:
- Monitors campaign performance thresholds
- Detects sudden drops in CTR, quality score, conversions
- Alerts on budget pacing issues
- Tracks competitive shifts

### 3. AI Chatbot Interface

**Natural Language Queries**:
- "Show me top performing campaigns this month"
- "Why did conversions drop last week?"
- "How should I optimize my budget?"
- "Predict next month's performance"

**Features**:
- Powered by Gemini 2.5 Flash for conversational responses
- Context-aware (knows current customer, date range, filters)
- Markdown-formatted answers with charts and tables
- Floating chat button on all dashboard pages
- Agent metadata showing which AI handled the request

### 4. Professional Web Dashboard

**Built with React + TypeScript + Material-UI**:

**Platform Dashboards**:
- **Unified Dashboard**: Cross-platform metrics, blended ROAS, best platform analysis
- **Google Ads Dashboard**: Campaign performance, keyword quality scores, search terms
- **Meta Ads Dashboard**: Ad set performance, demographic insights, creative analysis
- **GA4 Dashboard**: Session analytics, conversion paths, user behavior
- **Shopify Dashboard**: Revenue attribution, product performance, customer LTV

**Agent Dashboards**:
- **Data Agent Dashboard**: Campaign, keyword, ad group deep dives
- **Insights Dashboard**: Daily insights, anomaly detection, trend analysis
- **Optimization Dashboard**: Budget optimizer, keyword optimizer, ROI calculator
- **Forecasting Dashboard**: Spend forecast, CTR forecast, scenario simulator
- **Alerts Dashboard**: Threshold monitoring, performance alerts

**Features**:
- Global filtering (customer, date range, campaign type)
- All dashboards react to filter changes instantly
- Responsive design (desktop, tablet, mobile)
- Dark theme with purple gradient accents
- Professional charts with Recharts library
- Real-time data updates

### 5. Advanced AI Intelligence

**PIE Model** (Probability of Incremental Effect):
- Calculates true incremental ROAS (not just reported ROAS)
- Identifies which conversions were truly caused by ads
- Detects "Generosity Flaw" in Meta/Google attribution
- Provides confidence scores for each campaign

**Anomaly Detection**:
- Statistical analysis of daily performance
- Detects outliers beyond normal variance
- Categorizes anomalies (spend spike, CTR drop, conversion anomaly)
- Explains probable causes

**Budget Optimization**:
- Linear programming for optimal budget allocation
- Considers ROAS, incrementality, and diminishing returns
- Recommends specific dollar amounts to shift
- Calculates expected impact of changes

**Performance Forecasting**:
- Time series analysis with trend decomposition
- Accounts for seasonality and day-of-week patterns
- Confidence intervals for predictions
- Scenario modeling capabilities

---

## Technology Stack

### Backend
- **FastAPI** - Modern Python web framework (async support)
- **SQLAlchemy** - ORM for database queries
- **Pydantic** - Data validation and serialization
- **Google Ads API** - Official Google Ads client library
- **Meta Marketing API** - Facebook/Instagram ads data
- **Google Analytics Data API** - GA4 reporting API
- **Shopify Admin API** - E-commerce data

### Frontend
- **React 19** - Latest React with concurrent features
- **TypeScript** - Type-safe development
- **Material-UI v5** - Professional component library
- **Recharts** - Composable charting library
- **Axios** - HTTP client with interceptors
- **React Router v7** - Client-side routing
- **Framer Motion** - Smooth animations
- **React Markdown** - Rich text formatting in chat

### AI & ML
- **Google ADK** - Multi-agent orchestration framework
- **Gemini 2.5 Flash** - Conversational AI and analysis
- **LangChain** - Agent prompting and chaining
- **NumPy/Pandas** - Data manipulation
- **SciPy** - Statistical analysis
- **scikit-learn** - ML models (forecasting, clustering)

### Database
- **SQLite** - Production data warehouse
- **Star Schema** - Analytics-optimized design
- Dimension tables: customers, campaigns, keywords, ad groups
- Fact tables: daily performance, insights, conversions

---

## Quick Start

### Prerequisites

**Required Software**:
- Python 3.10+ ([Download](https://www.python.org/downloads/))
- Node.js 18+ ([Download](https://nodejs.org/))
- Git ([Download](https://git-scm.com/))

**Required API Credentials**:
- Google Ads API access (developer token, OAuth2 credentials)
- Meta Ads API access (app ID, app secret, access token)
- Google Analytics 4 API (service account credentials)
- Gemini API key ([Get here](https://makersuite.google.com/app/apikey))

---

## Setup Instructions

### 1. Clone Repository

```bash
git clone <your-repository-url>
cd ADS_API
```

### 2. Set Up Backend API

```bash
# Navigate to API directory
cd api

# Install Python dependencies
pip install -r requirements.txt

# Create environment file
cp ../.env.example ../.env

# Edit .env with your credentials
# GOOGLE_ADS_DEVELOPER_TOKEN=xxx
# GOOGLE_ADS_CLIENT_ID=xxx
# GOOGLE_ADS_CLIENT_SECRET=xxx
# GOOGLE_ADS_REFRESH_TOKEN=xxx
# GOOGLE_ADS_LOGIN_CUSTOMER_ID=xxx

# Also create .env.meta and .env.ga4 files
cp ../.env.meta.example ../.env.meta
cp ../.env.ga4.example ../.env.ga4

# Initialize database
cd ..
python init_warehouse.py

# Run ETL to populate data (first time only)
python warehouse_etl.py

# Start backend server
cd api
uvicorn app.main:app --reload --port 8000
```

**Backend API will be running on**: http://localhost:8000
**API Documentation**: http://localhost:8000/docs

### 3. Set Up Google ADK Chatbot

```bash
# Navigate to ADK directory
cd google-ads-multiagent/adk

# Create .env file for Gemini
echo "GOOGLE_API_KEY=your_gemini_api_key_here" > .env

# Install ADK dependencies (if not already installed)
pip install google-generativeai python-dotenv

# Start chatbot API
python chatbot_api.py
```

**Chatbot API will be running on**: http://localhost:8003
**Health Check**: http://localhost:8003/health

### 4. Set Up Web Dashboard

```bash
# Navigate to frontend directory
cd marketingiq-platform/web

# Install Node.js dependencies
npm install

# Start development server
npm run dev
```

**Frontend will be running on**: http://localhost:5173

### 5. One-Command Start (After Initial Setup)

Once you've completed the setup above, you can start all servers with:

```bash
# Windows
START_ALL_SERVERS.bat

# Linux/Mac
./start_all.sh
```

This automatically starts:
1. Backend API (port 8000)
2. Chatbot API (port 8003)
3. Frontend (port 5173)

---

## Using the Platform

### Access the Dashboard

1. Open browser: http://localhost:5173
2. You'll see the landing page with feature overview
3. Click "Get Started" to access dashboards

### Navigate Dashboards

**Main Navigation** (left sidebar):
- **Home** - Landing page
- **Unified Dashboard** - Cross-platform analytics
- **Platform Dashboards** - Google Ads, Meta Ads, GA4, Shopify
- **Agent Dashboards** - Data, Insights, Optimization, Forecasting, Alerts

### Use Global Filters

**Top filter bar** (appears on all dashboards):
- **Customer** - Select which client/account to view
- **Date Range** - Choose time period (Last 7/30/90 days, custom range)
- **Campaign Type** - Filter by campaign objective (Search, Ecommerce, B2B, All)

All dashboards update instantly when you change filters.

### Chat with AI Assistant

1. Look for purple **chat button** in bottom-right corner
2. Click to open chat window
3. Ask questions in natural language:

**Example Questions**:
- "Show me top performing campaigns"
- "Which keywords have low quality scores?"
- "How should I optimize my budget?"
- "Predict next month's performance"
- "Are there any anomalies in my campaigns?"

4. AI responds with:
   - Formatted text with **bold**, *italic*, lists
   - Data tables and metrics
   - Insights and recommendations
   - Agent attribution (shows which AI handled it)

### View AI Intelligence

Each dashboard has an **AI Intelligence** section showing:

**Descriptive** - What happened?
- Daily performance summary
- Key metric changes
- Top campaigns/keywords

**Diagnostic** - Why did it happen?
- Trend analysis
- Anomaly detection
- Contributing factors

**Predictive** - What will happen?
- Performance forecasts
- Trend projections
- Risk indicators

**Prescriptive** - What should we do?
- Optimization recommendations
- Budget reallocation suggestions
- Bid adjustment proposals

---

## API Endpoints

### Warehouse Endpoints
```
GET /api/v1/warehouse/metrics
    - Cross-platform summary metrics
    - Params: customer_id, date_range

GET /api/v1/warehouse/google-ads-performance
    - Google Ads campaign performance
    - Params: customer_id, date_range, campaign_type

GET /api/v1/warehouse/meta-ads-performance
    - Meta Ads insights
    - Params: customer_id, date_range

GET /api/v1/warehouse/ga4-metrics
    - Google Analytics 4 data
    - Params: customer_id, date_range
```

### AI Intelligence Endpoints
```
GET /api/v1/ai/daily-insights
    - Daily AI-generated insights
    - Returns: descriptive, diagnostic, predictive, prescriptive

GET /api/v1/ai/incrementality
    - PIE model results (incremental ROAS)
    - Returns: campaign-level incrementality scores

GET /api/v1/ai/anomalies
    - Anomaly detection results
    - Returns: detected anomalies with explanations

GET /api/v1/ai/budget-optimization
    - Budget allocation recommendations
    - Returns: suggested budget changes

GET /api/v1/ai/spend-forecast
    - Performance forecasting
    - Returns: 30-day predictions with confidence intervals
```

### Campaign & Keyword Endpoints
```
GET /api/v1/campaigns
    - List all campaigns
    - Params: customer_id, campaign_type

GET /api/v1/campaigns/{campaign_id}/performance
    - Single campaign details
    - Params: date_range

GET /api/v1/keywords/performance
    - Keyword performance data
    - Params: customer_id

GET /api/v1/adgroups
    - Ad group data
    - Params: customer_id, campaign_id
```

### Chatbot Endpoints
```
POST /api/chat
    - Send message to AI chatbot
    - Body: { message, customer_id, date_range, campaign_type }
    - Returns: { response, metadata, timestamp, agent_used }

GET /health
    - Chatbot health check
    - Returns: { status, adk_agents, gemini_enabled }

GET /api/agents
    - List available agents
    - Returns: { agents: [{ name, type, status }] }
```

**Full Interactive Docs**: http://localhost:8000/docs

---

## Architecture

### Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                     EXTERNAL DATA SOURCES                       │
├─────────────────────────────────────────────────────────────────┤
│  Google Ads API  │  Meta Ads API  │  GA4 API  │  Shopify API   │
└────────┬─────────┴────────┬────────┴───────┬──┴────────┬────────┘
         │                  │                │           │
         ↓                  ↓                ↓           ↓
┌─────────────────────────────────────────────────────────────────┐
│                        ETL PIPELINE                             │
├─────────────────────────────────────────────────────────────────┤
│  warehouse_google_ads_etl.py  │  warehouse_meta_ads_etl.py     │
│  warehouse_ga4_etl.py          │  shopify_etl.py               │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                   DATA WAREHOUSE (SQLite)                       │
├─────────────────────────────────────────────────────────────────┤
│  marketing_warehouse.db                                         │
│  ┌──────────────────────┐  ┌──────────────────────┐           │
│  │  Dimension Tables    │  │  Fact Tables         │           │
│  │  - dim_customer      │  │  - fact_campaign_*   │           │
│  │  - dim_campaign      │  │  - fact_keyword_*    │           │
│  │  - dim_keyword       │  │  - meta_insights     │           │
│  │  - dim_ad_group      │  │  - ga4_sessions      │           │
│  └──────────────────────┘  └──────────────────────┘           │
└─────────────────────────┬───────────────────────────────────────┘
                          │
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND API (FastAPI)                        │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌──────────────────┐  ┌────────────────┐│
│  │ Warehouse Routes│  │  AI Services     │  │ Campaign Routes││
│  │  - Metrics      │  │  - PIE Model     │  │  - List        ││
│  │  - Performance  │  │  - Insights      │  │  - Details     ││
│  │  - Cross-platform│  │  - Forecasting  │  │  - Keywords    ││
│  └─────────────────┘  └──────────────────┘  └────────────────┘│
└─────────────┬──────────────────────────┬────────────────────────┘
              │                          │
              ↓                          ↓
┌──────────────────────────┐  ┌──────────────────────────────────┐
│   FRONTEND (React)       │  │  AI CHATBOT (Google ADK)         │
├──────────────────────────┤  ├──────────────────────────────────┤
│  ┌───────────────────┐   │  │  ┌────────────────────────────┐  │
│  │ Dashboards        │   │  │  │ Root Agent (Orchestrator)  │  │
│  │  - Unified        │   │  │  └──────────┬─────────────────┘  │
│  │  - Google Ads     │   │  │             │                    │
│  │  - Meta Ads       │   │  │    ┌────────┴────────┐          │
│  │  - GA4            │   │  │    │   Sub-Agents    │          │
│  │  - Agents         │   │  │    │  - Data Agent   │          │
│  └───────────────────┘   │  │    │  - Insight Agent│          │
│  ┌───────────────────┐   │  │    │  - Optimization │          │
│  │ Chatbot UI        │───┼──┼───→│  - Forecasting  │          │
│  │  - Floating Button│   │  │    │  - Alert Agent  │          │
│  │  - Chat Window    │   │  │    └─────────────────┘          │
│  └───────────────────┘   │  │  Powered by Gemini 2.5 Flash    │
└──────────────────────────┘  └──────────────────────────────────┘
```

### Component Communication

```
Frontend (React)
    ↓ HTTP (Axios)
Backend API (FastAPI) :8000
    ↓ SQL (SQLAlchemy)
Data Warehouse (SQLite)

Frontend (React)
    ↓ HTTP (Axios)
Chatbot API (FastAPI) :8003
    ↓ Gemini SDK
Google Gemini 2.5 Flash
    ↓ Warehouse Client
Data Warehouse (SQLite)
```

---

## File Structure

```
ADS_API/
├── api/                          # Backend API
│   ├── app/
│   │   ├── routes/               # API endpoints
│   │   │   ├── campaigns.py
│   │   │   ├── keywords.py
│   │   │   └── warehouse.py
│   │   ├── services/             # Business logic
│   │   │   ├── ai/               # AI Intelligence
│   │   │   │   ├── daily_insights_warehouse.py
│   │   │   │   ├── pie_model_warehouse.py
│   │   │   │   ├── anomaly_detection_warehouse.py
│   │   │   │   ├── budget_optimizer_warehouse.py
│   │   │   │   └── spend_forecast_warehouse.py
│   │   │   ├── google_ads_service.py
│   │   │   ├── meta_ads_service.py
│   │   │   └── ga4_service.py
│   │   ├── models/               # SQLAlchemy models
│   │   └── main.py               # FastAPI app
│   └── requirements.txt
│
├── marketingiq-platform/web/     # Frontend
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/
│   │   │   │   └── FloatingChatButton.tsx
│   │   │   ├── dashboard/        # Platform dashboards
│   │   │   │   ├── UnifiedDashboard.tsx
│   │   │   │   ├── GoogleAdsDashboard.tsx
│   │   │   │   └── MetaAdsDashboard.tsx
│   │   │   ├── dashboards/agents/ # Agent dashboards
│   │   │   │   ├── data_agent/
│   │   │   │   ├── insight_agent/
│   │   │   │   ├── optimization_agent/
│   │   │   │   └── forecasting_agent/
│   │   │   ├── common/
│   │   │   │   ├── Layout.tsx
│   │   │   │   └── GlobalFilterBar.tsx
│   │   │   └── landing/
│   │   │       └── LandingPage.tsx
│   │   ├── services/             # API clients
│   │   │   ├── api.ts
│   │   │   ├── unifiedService.ts
│   │   │   └── metaAdsService.ts
│   │   ├── context/
│   │   │   └── FilterContext.tsx # Global filters
│   │   └── types/
│   │       └── index.ts
│   └── package.json
│
├── google-ads-multiagent/adk/    # AI Multi-Agent System
│   ├── chatbot_api.py            # Chatbot FastAPI server
│   ├── orchestration_agent/
│   │   ├── agent.py              # Root agent
│   │   └── sub_agents/
│   │       ├── data_agent/
│   │       │   ├── agent.py
│   │       │   ├── tools.py
│   │       │   └── warehouse_client.py
│   │       ├── insight_agent/
│   │       ├── optimization_agent/
│   │       └── forecasting_agent/
│   └── .env                      # Gemini API key
│
├── ETL Scripts
│   ├── warehouse_etl.py          # Main ETL orchestrator
│   ├── warehouse_google_ads_etl.py
│   ├── warehouse_meta_ads_etl.py
│   ├── warehouse_ga4_etl.py
│   ├── shopify_etl.py
│   ├── warehouse_etl_helpers.py
│   └── init_warehouse.py
│
├── Configuration
│   ├── .env                      # Google Ads credentials
│   ├── .env.meta                 # Meta Ads credentials
│   ├── .env.ga4                  # GA4 credentials
│   ├── google-ads.yaml           # Google Ads API config
│   ├── requirements.txt
│   └── warehouse_schema.sql
│
├── Startup Scripts
│   ├── START_ALL_SERVERS.bat    # Windows: Start all servers
│   ├── START_BACKEND.bat         # Windows: Backend only
│   ├── start_all.sh              # Linux/Mac: Start all
│   └── stop_all.sh               # Stop all servers
│
├── Data & Logs
│   ├── marketing_warehouse.db    # Production database
│   ├── credentials/              # API credentials
│   ├── secrets/                  # OAuth tokens
│   └── logs/                     # Application logs
│
└── Documentation
    ├── README.md                 # This file
    ├── CHATBOT_SETUP.md          # Chatbot setup guide
    ├── CLAUDE.md                 # Development notes
    └── PROJECT_STRUCTURE.md      # Detailed structure
```

---

## Data Refresh Schedule

### Manual ETL
```bash
# Full refresh (all platforms)
python warehouse_etl.py

# Individual platforms
python warehouse_google_ads_etl.py
python warehouse_meta_ads_etl.py
python warehouse_ga4_etl.py
python shopify_etl.py
```

### Automated (Production)
- **Cloud Function**: Runs daily at 2 AM UTC
- **Deployment**: `./deploy-etl.sh`
- **Monitoring**: Check `logs/etl.log`

---

## Troubleshooting

### Backend API won't start
```bash
# Check Python version
python --version  # Should be 3.10+

# Reinstall dependencies
cd api
pip install -r requirements.txt --force-reinstall

# Check database exists
ls -l ../marketing_warehouse.db

# Initialize if missing
cd ..
python init_warehouse.py
```

### Frontend won't start
```bash
# Check Node version
node --version  # Should be 18+

# Clear cache and reinstall
cd marketingiq-platform/web
rm -rf node_modules package-lock.json
npm install

# Start dev server
npm run dev
```

### Chatbot not responding
```bash
# Check Gemini API key
cd google-ads-multiagent/adk
cat .env  # Should have GOOGLE_API_KEY=xxx

# Test chatbot health
curl http://localhost:8003/health

# Check chatbot logs in terminal
# Should see "Gemini API configured for friendly responses"
```

### No data in dashboards
```bash
# Verify warehouse has data
python -c "import sqlite3; conn = sqlite3.connect('marketing_warehouse.db'); print('Campaigns:', conn.execute('SELECT COUNT(*) FROM dim_google_ads_campaign').fetchone()[0])"

# Run ETL if empty
python warehouse_etl.py

# Check customer filter
# Make sure you've selected a customer with data (e.g., "Emcee Sons")
```

### CORS errors
```bash
# Make sure backend is running
curl http://localhost:8000/health

# Restart backend
cd api
uvicorn app.main:app --reload --port 8000
```

---

## Deployment

### Development
```bash
# All services on localhost
START_ALL_SERVERS.bat  # or ./start_all.sh
```

### Production (Google Cloud)
```bash
# Deploy ETL pipeline
./deploy-etl.sh

# Deploy backend API
gcloud builds submit --config cloudbuild.yaml

# Frontend can be deployed to:
# - Vercel
# - Netlify
# - Google Cloud Run
```

---

## Security & Credentials

### Never Commit
- `.env` files (all variants)
- `credentials/` folder
- `secrets/` folder
- `*.db` files (except schema)

### Git-Ignored
All sensitive files are already in `.gitignore`:
- `.env*`
- `credentials/`
- `secrets/`
- `marketing_warehouse.db`
- `google_ads_data.db`
- OAuth tokens

---

## Performance

### Database Size
- Typical warehouse: ~1-2 MB per customer per month
- 1 year of data for 5 customers: ~60-120 MB
- SQLite handles up to 140 TB (we're using <1 GB)

### Query Speed
- Simple metrics: <50ms
- Complex aggregations: <200ms
- AI analysis: 1-3 seconds
- Chatbot responses: 2-5 seconds (includes Gemini processing)

### Scalability
- Current: Handles 10+ customers, 1000+ campaigns
- Bottleneck: SQLite write concurrency
- Solution (if needed): Migrate to PostgreSQL

---

## Future Roadmap

### Planned Features
- [ ] Real-time data streaming (vs daily batch)
- [ ] Custom alert rules builder
- [ ] Automated campaign creation from AI recommendations
- [ ] A/B test analysis and recommendations
- [ ] Competitive intelligence integration
- [ ] Multi-user accounts with role-based access
- [ ] PDF report generation
- [ ] Email digest of daily insights
- [ ] Slack/Teams bot integration
- [ ] Mobile app (React Native)

### Platform Expansions
- [ ] LinkedIn Ads integration
- [ ] TikTok Ads integration
- [ ] Twitter Ads integration
- [ ] Amazon Advertising integration

---

## Contributing

This is a proprietary platform. For questions or feature requests, contact the development team.

---

## License

Proprietary - All rights reserved.

---

## Support

For technical support or questions:
- Check documentation: `PROJECT_STRUCTURE.md`, `CHATBOT_SETUP.md`
- API docs: http://localhost:8000/docs
- Chatbot health: http://localhost:8003/health

---

**Built with professional standards for enterprise marketing analytics.**

*Last updated: November 2025*
