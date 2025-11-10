# MarketingIQ AI Platform - Architecture Document

## Executive Summary

MarketingIQ is an enterprise-grade AI-powered marketing analytics and optimization platform that provides intelligent insights, automated decision-making, and multi-channel campaign management for digital advertising. The platform integrates with Google Ads, Meta Ads, Google Analytics 4, and Shopify to deliver a unified view of marketing performance with AI-driven recommendations.

---

## 1. System Overview

### 1.1 Platform Purpose
MarketingIQ serves as an intelligent marketing operations platform that:
- **Aggregates** marketing data from multiple sources (Google Ads, Meta Ads, GA4, Shopify)
- **Analyzes** campaign performance using AI/ML algorithms
- **Optimizes** budget allocation, keyword bidding, and campaign strategies
- **Forecasts** future performance trends and scenarios
- **Alerts** marketers to anomalies and opportunities in real-time
- **Automates** routine optimization tasks through AI agents

### 1.2 Core Value Propositions
1. **Multi-Customer Management**: CEO/teams can manage multiple client accounts from a single dashboard
2. **AI-Powered Intelligence**: 7 specialized AI models for anomaly detection, LTV prediction, attribution, and optimization
3. **Multi-Agent Architecture**: 5 specialized agents (Data, Insight, Optimization, Forecasting, Alert) working in orchestrated workflows
4. **Real-Time Decision Support**: Continuous monitoring and intelligent recommendations
5. **Cross-Platform Attribution**: Unified view across Google Ads, Meta Ads, GA4, and e-commerce platforms

---

## 2. Architecture Layers

### 2.1 High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    PRESENTATION LAYER (React)                    │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Data Agent   │  │ Insight      │  │ Optimization │          │
│  │ Dashboard    │  │ Agent        │  │ Agent        │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Forecasting  │  │ Alert Agent  │  │ Platform     │          │
│  │ Agent        │  │              │  │ Dashboards   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│              APPLICATION LAYER (FastAPI + Multi-Agent)           │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │         Root Orchestrator Agent (LangGraph)              │  │
│  │  Coordinates 5 specialized sub-agents via ADK framework  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                                                                  │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐               │
│  │ REST API   │  │ AI/ML      │  │ ETL        │               │
│  │ Routes     │  │ Services   │  │ Pipelines  │               │
│  └────────────┘  └────────────┘  └────────────┘               │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA LAYER (SQLite)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Google Ads   │  │ Meta Ads     │  │ GA4 Data     │          │
│  │ Warehouse    │  │ Data         │  │              │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│  ┌──────────────┐  ┌──────────────┐                            │
│  │ Shopify      │  │ ML Features  │                            │
│  │ E-commerce   │  │ Store        │                            │
│  └──────────────┘  └──────────────┘                            │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                  INTEGRATION LAYER (External APIs)               │
│  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌──────────┐ │
│  │ Google Ads │  │ Meta Ads   │  │ GA4 API    │  │ Shopify  │ │
│  │ API        │  │ Marketing  │  │            │  │ API      │ │
│  └────────────┘  └────────────┘  └────────────┘  └──────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Backend Architecture

### 3.1 Technology Stack
- **Framework**: FastAPI (Python 3.9+)
- **Database**: SQLite (with SQLAlchemy ORM)
- **AI Framework**: LangChain + LangGraph (Multi-Agent Orchestration)
- **ML Libraries**: scikit-learn, pandas, numpy
- **API Authentication**: OAuth 2.0 for external platforms
- **Logging**: Python logging + loguru

### 3.2 Backend Components

#### 3.2.1 REST API Layer (`api/app/`)

**Main Application** (`app/main.py`):
- FastAPI application entry point
- CORS middleware for cross-origin requests
- Exception handlers for HTTP errors and validation
- Health check endpoints
- API versioning (v1)

**API Routes** (`app/routes/`):
| Route | Purpose | Key Endpoints |
|-------|---------|---------------|
| `customers.py` | Customer/client management | GET/POST /api/v1/customers |
| `campaigns.py` | Campaign data access | GET /api/v1/campaigns?customer_id={id} |
| `ad_groups.py` | Ad group performance | GET /api/v1/adgroups?customer_id={id} |
| `keywords.py` | Keyword performance | GET /api/v1/keywords?customer_id={id} |
| `search_terms.py` | Search term analysis | GET /api/v1/search-terms |
| `ml_features.py` | ML feature store | GET /api/v1/ml-features |
| `metrics.py` | Aggregated metrics | GET /api/v1/metrics/summary |
| `ecommerce.py` | E-commerce insights | GET /api/v1/ecommerce/ltv |
| `shopify.py` | Shopify integration | GET /api/v1/shopify/orders |
| `ga4.py` | GA4 analytics | GET /api/v1/ga4/sessions |
| `meta.py` | Meta Ads data | GET /api/v1/meta/insights |
| `ai_intelligence.py` | AI insights & greetings | GET /api/v1/ai/greeting |
| `warehouse.py` | Warehouse queries | GET /api/v1/warehouse/performance |

**All API routes accept `customer_id` as query parameter for multi-customer filtering.**

#### 3.2.2 Database Layer (`app/db/`)

**Database Models** (`app/db/models.py`):

**Google Ads Models**:
- `Customer`: Customer/client accounts (customer_id, name, currency, timezone)
- `Campaign`: Campaign configuration (customer_id, campaign_id, name, status, budget, bidding_strategy)
- `AdGroup`: Ad group settings (ad_group_id, campaign_id, customer_id, bids)
- `Keyword`: Keyword data (keyword_id, customer_id, keyword_text, match_type, quality_score)
- `SearchTerm`: Search query performance (customer_id, search_term, clicks, impressions, conversions)
- `CampaignKeyword`: Performance metrics by campaign+keyword (customer_id, date, clicks, cost, conversions)
- `MLFeature`: Engineered features for ML models (customer_id, campaign metrics, keyword metrics)

**Shopify E-commerce Models**:
- `ShopifyStore`: Store credentials (store_id, customer_id, access_token)
- `ShopifyOrder`: Order data with attribution (order_id, customer_id, gclid, utm_params, total_price)
- `ShopifyProduct`: Product catalog (product_id, title, price, inventory)
- `ShopifyCustomer`: Customer LTV data (customer_id, total_spent, orders_count, first_order_gclid)
- `ShopifyCartEvent`: Cart abandonment tracking (event_id, customer_id, gclid, products_json)

**Meta Ads Models**:
- `MetaAdAccount`: Meta account connection (account_id, customer_id, access_token)
- `MetaCampaign`: Meta campaign data (campaign_id, customer_id, objective, budget)
- `MetaAdSet`: Ad set configuration (adset_id, targeting, optimization_goal)
- `MetaAd`: Creative/ad details (ad_id, creative_title, creative_body, call_to_action)
- `MetaInsights`: Performance metrics (customer_id, date, impressions, clicks, spend, conversions, ROAS)

**GA4 Models**:
- `GA4Property`: GA4 property connection (property_id, customer_id, credentials_path)
- `GA4Session`: Session aggregated data (customer_id, date, utm_params, sessions, users, conversions)
- `GA4Event`: Event tracking (event_name, customer_id, event_count, ecommerce_revenue)
- `GA4ConversionPath`: Multi-touch attribution paths (customer_id, touchpoints_json, conversion_value)
- `GA4Audience`: Audience insights (segment_name, demographics, device_category, conversion_rate)

**Key Design Principles**:
- Every table has `customer_id` for multi-customer filtering
- Timestamps for data freshness tracking
- Foreign key relationships for data integrity
- Indexed columns for fast queries (customer_id, date, campaign_id)

#### 3.2.3 AI/ML Services (`app/services/ai/`)

**AI Service Portfolio**:

1. **Anomaly Detector** (`anomaly_detector.py`, `anomaly_detector_warehouse.py`):
   - **Purpose**: Detect unusual patterns in campaign performance
   - **Algorithm**: Isolation Forest (unsupervised learning)
   - **Features**: Cost, CTR, conversion rate, impressions
   - **Output**: Anomaly scores + flagged campaigns
   - **Use Case**: Alert on sudden spend spikes, CTR drops, conversion anomalies

2. **LTV Predictor** (`ltv_predictor.py`, `ltv_predictor_warehouse.py`):
   - **Purpose**: Predict customer lifetime value
   - **Algorithm**: Random Forest Regression
   - **Features**: Order history, AOV, purchase frequency, first_order_gclid
   - **Output**: Predicted LTV (30/60/90 day)
   - **Use Case**: Optimize CAC vs. LTV, identify high-value segments

3. **PIE Model** (`pie_model.py`, `pie_model_warehouse.py`):
   - **Purpose**: Prioritize optimization opportunities
   - **Framework**: Potential, Importance, Ease scoring
   - **Metrics**: Budget potential, performance impact, implementation complexity
   - **Output**: Ranked list of optimization opportunities
   - **Use Case**: Decide which campaigns/keywords to optimize first

4. **Attribution Analyzer** (`attribution_analyzer.py`):
   - **Purpose**: Multi-touch attribution modeling
   - **Models**: First-touch, last-touch, linear, time-decay, position-based
   - **Data Sources**: GA4 conversion paths, Shopify orders, Google Ads clicks
   - **Output**: Attribution credit by channel/campaign
   - **Use Case**: Understand true channel contribution, optimize budget allocation

5. **Decision Engine** (`decision_engine.py`):
   - **Purpose**: Automated campaign decision-making
   - **Rules Engine**: Bid adjustment rules, budget reallocation, pause/enable logic
   - **Input**: Real-time performance metrics, thresholds, business rules
   - **Output**: Actionable recommendations (increase bid, pause keyword, reallocate budget)
   - **Use Case**: Automate routine optimization tasks

6. **Greeting Generator** (`greeting_generator.py`):
   - **Purpose**: Personalized AI-generated greetings and summaries
   - **Technology**: Template-based + ML insights
   - **Input**: User context, time of day, recent campaign performance
   - **Output**: Contextual greetings with key insights
   - **Use Case**: Dashboard welcome messages, email summaries

#### 3.2.4 Core Services

**Google Ads Service** (`app/services/google_ads_service.py`):
- Google Ads API client wrapper
- GAQL (Google Ads Query Language) builder
- Campaign, ad group, keyword CRUD operations
- Performance report fetching

**Meta Ads Service** (`app/services/meta_ads_service.py`):
- Facebook Marketing API integration
- Campaign, ad set, ad management
- Insights API for performance metrics
- Audience targeting management

**GAQL Builder** (`app/services/gaql_builder.py`):
- Dynamic query construction for Google Ads API
- Filter builder (customer_id, date_range, status)
- Metrics selection (impressions, clicks, cost, conversions)
- Pagination support

**E-commerce Insights** (`app/services/ecommerce_insights.py`):
- Cross-platform e-commerce analytics
- ROAS calculation across platforms
- Product performance analysis
- Customer segmentation

### 3.3 Multi-Agent System (`google-ads-multiagent/adk/`)

#### 3.3.1 Agent Architecture

**Orchestration Pattern**: LangGraph State Machine

**Root Orchestrator** (`orchestration_agent/`):
- **Technology**: LangGraph + LangChain
- **Purpose**: Route user queries to appropriate sub-agents
- **State Management**: Shared state across agent workflow
- **Task Scheduling**: Parallel and sequential agent execution
- **Result Aggregation**: Combine outputs from multiple agents

**Sub-Agents**:

1. **Data Agent** (`sub_agents/data_agent/`):
   - **Role**: Fetch and retrieve marketing data
   - **Tools**:
     - `campaign_tools.py`: Fetch campaign metrics from Google Ads API
     - `adgroup_tools.py`: Retrieve ad group performance
     - `keyword_tools.py`: Get keyword-level data
     - `search_term_tools.py`: Analyze search query performance
     - `ml_feature_tools.py`: Access ML feature store
     - `ga4_tools.py`: Query GA4 analytics
   - **Data Sources**: API database via `api_client.py`, Google Ads API via `db_client.py`
   - **Output**: Structured DataFrames with campaign/keyword/search term data

2. **Insight Agent** (`sub_agents/insight_agent/`):
   - **Role**: Generate actionable insights from data
   - **Tools**:
     - `anomaly_detector.py`: Detect performance anomalies
     - `performance_analyzer.py`: Analyze trends and patterns
     - `roi_calculator.py`: Calculate ROAS, CAC, LTV metrics
     - `trend_analyzer.py`: Identify upward/downward trends
     - `competitor_analysis.py`: Benchmark against industry
   - **AI Models**: Uses AI services (anomaly detector, attribution analyzer)
   - **Output**: Insight cards with severity, recommendations, impact scores

3. **Optimization Agent** (`sub_agents/optimization_agent/`):
   - **Role**: Generate optimization recommendations
   - **Capabilities**:
     - Budget optimization (reallocate across campaigns)
     - Keyword bid optimization (increase/decrease bids)
     - Negative keyword suggestions
     - Ad scheduling recommendations
     - Audience targeting refinement
   - **Algorithm**: PIE model (Potential-Importance-Ease)
   - **Output**: Ranked optimization opportunities with expected impact

4. **Forecasting Agent** (`sub_agents/forecasting_agent/`):
   - **Role**: Predict future performance
   - **Tools**:
     - `performance_forecaster.py`: Time-series forecasting (ARIMA, Prophet)
     - `scenario_planner.py`: What-if scenario simulation
   - **Metrics**: Forecast spend, CTR, conversions, ROAS
   - **Time Horizons**: 7-day, 30-day, 90-day
   - **Output**: Forecast charts with confidence intervals

5. **Alert Agent** (implicit in system):
   - **Role**: Monitor thresholds and trigger alerts
   - **Monitors**:
     - Spend exceeding budget
     - CTR dropping below threshold
     - Conversion rate anomalies
     - Quality score degradation
   - **Alert Channels**: Dashboard notifications, email (future)
   - **Output**: Alert cards with severity (critical, warning, info)

#### 3.3.2 Agent Communication Flow

```
User Query: "Optimize my campaigns for next week"
     │
     ▼
┌────────────────────────────────────┐
│   Root Orchestrator Agent          │
│   (Parses intent, routes to agents)│
└────────────────────────────────────┘
     │
     ├──────────► Data Agent: Fetch campaign performance (last 30 days)
     │            Returns: DataFrame with cost, CTR, conversions
     │
     ├──────────► Insight Agent: Analyze performance, detect anomalies
     │            Returns: "Campaign X has 30% CTR drop, Campaign Y anomaly"
     │
     ├──────────► Forecasting Agent: Predict next 7 days
     │            Returns: "Expected spend $5000, conversions 150"
     │
     ├──────────► Optimization Agent: Generate recommendations
     │            Returns: "Reallocate $500 from Campaign X to Y, increase bid on Keyword Z"
     │
     ▼
┌────────────────────────────────────┐
│   Result Aggregator                │
│   Combines all agent outputs       │
└────────────────────────────────────┘
     │
     ▼
User receives: Unified optimization plan with data + insights + forecast + actions
```

---

## 4. Frontend Architecture

### 4.1 Technology Stack
- **Framework**: React 19.1 + TypeScript
- **UI Library**: Material-UI (MUI) 5.18
- **State Management**: Redux Toolkit + RTK Query
- **Routing**: React Router DOM 7.9
- **Charts**: Recharts 3.3
- **Animations**: Framer Motion 12.23
- **Build Tool**: Vite 7.1

### 4.2 Frontend Structure

**Project Layout**:
```
marketingiq-platform/web/src/
├── components/
│   ├── common/               # Shared components
│   │   ├── GlobalFilterBar.tsx       # Customer selector, date picker, filters
│   │   ├── KPICard.tsx               # Metric display cards
│   │   ├── InsightCard.tsx           # AI insight display
│   │   ├── DashboardTemplate.tsx     # Reusable dashboard layout
│   │   └── Layout.tsx                # Main app layout
│   │
│   ├── dashboards/
│   │   ├── agents/           # Agent-specific dashboards
│   │   │   ├── data_agent/
│   │   │   │   ├── CampaignsDashboard.tsx
│   │   │   │   ├── AdGroupsDashboard.tsx
│   │   │   │   └── KeywordsDashboard.tsx
│   │   │   │
│   │   │   ├── insight_agent/
│   │   │   │   ├── InsightsSummary.tsx
│   │   │   │   ├── CampaignInsights.tsx
│   │   │   │   └── AnomalyDetection.tsx
│   │   │   │
│   │   │   ├── optimization_agent/
│   │   │   │   ├── BudgetOptimizer.tsx
│   │   │   │   ├── KeywordOptimizer.tsx
│   │   │   │   └── CampaignSimulator.tsx
│   │   │   │
│   │   │   ├── forecasting_agent/
│   │   │   │   ├── SpendForecast.tsx
│   │   │   │   ├── CTRForecast.tsx
│   │   │   │   └── ScenarioSimulator.tsx
│   │   │   │
│   │   │   └── alert_agent/
│   │   │       ├── AlertsDashboard.tsx
│   │   │       └── ThresholdsMonitor.tsx
│   │   │
│   │   └── platform/         # Platform dashboards
│   │       ├── UnifiedDashboard.tsx      # All-in-one view
│   │       ├── GoogleAdsDashboard.tsx
│   │       ├── MetaAdsDashboard.tsx
│   │       ├── GA4Dashboard.tsx
│   │       └── EcommerceDashboard.tsx
│   │
│   ├── charts/               # Chart components
│   │   └── EnhancedChart.tsx
│   │
│   ├── chat/                 # Chatbot UI
│   │   └── FloatingChatButton.tsx
│   │
│   └── landing/              # Landing page
│       └── LandingPage.tsx
│
├── context/
│   └── FilterContext.tsx     # Global filter state (customer, date range)
│
├── App.tsx                   # Main app component
└── main.tsx                  # Entry point
```

### 4.3 Dashboard Features

#### 4.3.1 Global Filter Bar (`GlobalFilterBar.tsx`)
**Purpose**: Central filtering for all dashboards

**Filters**:
1. **Customer Selector**:
   - Dropdown with all customer accounts
   - Displays: customer_name (customer_id)
   - Default: First customer in database
   - onChange: Triggers dashboard refresh

2. **Date Range Picker**:
   - Presets: Last 7 days, 30 days, 90 days, custom
   - Format: YYYY-MM-DD

3. **Campaign Type Filter**:
   - Options: All, Search, Ecommerce, B2B, Display
   - Multi-select

**State Management**: React Context (FilterContext) shared across all dashboards

**Data Flow**:
```
User selects customer → FilterContext updates → All dashboards re-fetch with customer_id
```

#### 4.3.2 Data Agent Dashboards

**Campaigns Dashboard** (`CampaignsDashboard.tsx`):
- Table: campaign_name, status, budget, spend, CTR, conversions, ROAS
- Filters: customer_id, date_range, campaign_type
- Actions: View details, Edit settings
- Charts: Spend over time, CTR trend

**Ad Groups Dashboard** (`AdGroupsDashboard.tsx`):
- Table: ad_group_name, campaign, bids, impressions, clicks, cost
- Grouping by campaign
- Sortable columns

**Keywords Dashboard** (`KeywordsDashboard.tsx`):
- Table: keyword_text, match_type, quality_score, avg_cpc, conversions
- Search functionality
- Quality score distribution chart

#### 4.3.3 Insight Agent Dashboards

**Insights Summary** (`InsightsSummary.tsx`):
- Top 5 insights by priority
- Insight cards with:
  - Title, description
  - Severity (critical/warning/info)
  - Recommended action
  - Expected impact
- Source: `/api/v1/ai/insights?customer_id={id}`

**Anomaly Detection** (`AnomalyDetection.tsx`):
- Real-time anomaly alerts
- Scatter plot: Cost vs. CTR with anomalies highlighted
- Anomaly details: Campaign, metric, deviation %, timeframe
- Source: AI anomaly detector service

**Campaign Insights** (`CampaignInsights.tsx`):
- Performance breakdown by campaign
- Top performers vs. underperformers
- Trend analysis (7-day, 30-day)

#### 4.3.4 Optimization Agent Dashboards

**Budget Optimizer** (`BudgetOptimizer.tsx`):
- Current budget allocation (pie chart)
- Recommended reallocation (side-by-side comparison)
- Expected impact: +X% conversions, -Y% CPA
- Interactive: Drag-and-drop budget adjustment
- Apply button → Calls backend decision engine

**Keyword Optimizer** (`KeywordOptimizer.tsx`):
- Keyword opportunities table:
  - Keywords to increase bid (high CTR, low position)
  - Keywords to decrease bid (low CTR, high cost)
  - Negative keyword suggestions (high cost, 0 conversions)
- Bid adjustment simulator

**Campaign Simulator** (`CampaignSimulator.tsx`):
- What-if scenarios:
  - "What if I increase budget by 20%?"
  - "What if I pause Campaign X?"
  - "What if I shift spend to mobile?"
- Forecast impact: spend, conversions, ROAS

#### 4.3.5 Forecasting Agent Dashboards

**Spend Forecast** (`SpendForecast.tsx`):
- Line chart: Historical spend + 30-day forecast
- Confidence intervals (80%, 95%)
- Budget pacing: "On track to spend $X by month end"

**CTR Forecast** (`CTRForecast.tsx`):
- Predicted CTR trend by campaign
- Seasonal patterns
- Recommendations to improve CTR

**Scenario Simulator** (`ScenarioSimulator.tsx`):
- Multi-scenario comparison
- Variables: Budget, bids, targeting
- Output: Forecasted conversions, ROAS, CPA

#### 4.3.6 Alert Agent Dashboards

**Alerts Dashboard** (`AlertsDashboard.tsx`):
- Alert list (sorted by severity, timestamp)
- Alert types:
  - Spend alert: "Campaign X spent 90% of daily budget by 2 PM"
  - Performance alert: "Keyword Y CTR dropped 40% vs. last week"
  - Quality score alert: "10 keywords quality score < 5"
- Actions: Acknowledge, Snooze, View details

**Thresholds Monitor** (`ThresholdsMonitor.tsx`):
- Configure alert thresholds per customer
- Metrics: Spend, CTR, conversion rate, quality score
- Conditions: >, <, % change
- Notification channels: Dashboard, email, Slack (future)

### 4.4 State Management

**Redux Toolkit Store**:
- `customersSlice`: List of customers, selected customer
- `campaignsSlice`: Campaign data cache
- `filtersSlice`: Global filters (date range, campaign type)
- `alertsSlice`: Active alerts

**RTK Query APIs**:
- `campaignsApi`: GET /api/v1/campaigns
- `insightsApi`: GET /api/v1/ai/insights
- `forecastApi`: GET /api/v1/forecast/spend
- Auto-caching, auto-refetching on filter change

---

## 5. Data Flow Architecture

### 5.1 ETL Pipeline

**ETL Scripts**:
1. `warehouse_etl.py`: Google Ads → SQLite warehouse
2. `shopify_etl.py`: Shopify → SQLite
3. `ga4_etl.py`: GA4 → SQLite
4. `meta_ads_etl.py`: Meta Ads → SQLite

**ETL Flow (Example: Google Ads)**:
```
┌─────────────────────────────────────────────────────────────┐
│ 1. EXTRACT: Google Ads API                                  │
│    - Authenticate with google-ads.yaml                      │
│    - Query campaigns, ad groups, keywords (GAQL)            │
│    - Fetch performance metrics (last 30 days)               │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 2. TRANSFORM: Data processing                               │
│    - Convert micros to currency (cost_micros / 1,000,000)  │
│    - Calculate derived metrics (CTR = clicks/impressions)   │
│    - Enrich with customer_id                                │
│    - Handle nulls, duplicates                               │
└─────────────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│ 3. LOAD: SQLite warehouse                                   │
│    - Insert into campaigns, ad_groups, keywords tables      │
│    - Upsert logic (update if exists)                        │
│    - Update last_sync_at timestamp                          │
└─────────────────────────────────────────────────────────────┘
```

**Scheduling**: Cron jobs (every 1 hour for real-time dashboards)

### 5.2 API Request Flow

**Example: User views Campaigns Dashboard**

```
1. User selects Customer "Acme Corp" (customer_id=123) in GlobalFilterBar
   │
   ▼
2. FilterContext updates: { customer_id: 123, date_range: "LAST_30_DAYS" }
   │
   ▼
3. CampaignsDashboard detects filter change, triggers API call:
   GET /api/v1/campaigns?customer_id=123&date_range=LAST_30_DAYS
   │
   ▼
4. FastAPI routes/campaigns.py receives request
   │
   ▼
5. Queries database:
   SELECT * FROM campaigns WHERE customer_id = 123
   JOIN campaign_keywords FOR metrics
   │
   ▼
6. Returns JSON:
   [
     { campaign_id: 1, campaign_name: "Summer Sale", spend: 1500, conversions: 45, ... },
     { campaign_id: 2, campaign_name: "Brand Awareness", spend: 800, conversions: 20, ... }
   ]
   │
   ▼
7. React component receives data, renders table + charts
```

### 5.3 AI Insight Generation Flow

**Example: Anomaly Detection**

```
1. Scheduled job (every 30 min) triggers anomaly detection
   │
   ▼
2. app/services/ai/anomaly_detector.py:
   - Fetch last 7 days of campaign metrics (all customers)
   - Extract features: [cost, ctr, conversion_rate, impressions]
   │
   ▼
3. Isolation Forest model:
   - Fit on features
   - Predict anomaly scores (threshold: -0.5)
   - Flag campaigns with score < -0.5
   │
   ▼
4. Generate insights:
   [
     {
       customer_id: 123,
       campaign_id: 1,
       campaign_name: "Summer Sale",
       anomaly_type: "cost_spike",
       severity: "critical",
       message: "Cost increased 45% vs. last week",
       recommendation: "Review keyword bids, check for click fraud"
     }
   ]
   │
   ▼
5. Store insights in cache (Redis in production, in-memory for now)
   │
   ▼
6. Frontend fetches: GET /api/v1/ai/insights?customer_id=123
   │
   ▼
7. Display in InsightsSummary dashboard
```

---

## 6. Multi-Customer Architecture

### 6.1 Customer Isolation Strategy

**Database Level**:
- Every table includes `customer_id` column
- All queries filtered by `customer_id` (passed as query param)
- No shared data across customers (strict isolation)

**API Level**:
- All endpoints require `customer_id` query parameter
- Example: `/api/v1/campaigns?customer_id=123`
- Backend validates customer_id exists before returning data

**Frontend Level**:
- `GlobalFilterBar` customer selector is the source of truth
- `FilterContext` propagates customer_id to all dashboards
- Every API call includes selected customer_id

**Security**:
- Future: Add authentication middleware to verify user has access to customer_id
- OAuth scopes per customer
- Audit logging for customer data access

### 6.2 Multi-Customer Workflow

**CEO/Team Workflow**:
```
1. CEO logs in → Sees list of all customers (10 clients)
2. Selects "Acme Corp" from dropdown
3. All dashboards update:
   - Data Agent: Shows Acme's campaigns, keywords
   - Insight Agent: Shows Acme-specific anomalies, insights
   - Optimization Agent: Budget recommendations for Acme only
   - Forecasting Agent: Acme's spend forecast
   - Alert Agent: Acme's active alerts
4. CEO switches to "Beta Inc" → Entire dashboard reloads with Beta's data
```

---

## 7. Deployment Architecture

### 7.1 Development Environment
- **Backend**: `uvicorn api.app.main:app --reload` (port 8000)
- **Frontend**: `npm run dev` (Vite dev server, port 5173)
- **Database**: SQLite file (`marketing_warehouse.db`)

### 7.2 Production Environment (Planned)

**Infrastructure**:
```
┌─────────────────────────────────────────────────────────────┐
│                    LOAD BALANCER (Nginx)                     │
└─────────────────────────────────────────────────────────────┘
                         │
        ┌────────────────┴────────────────┐
        │                                 │
        ▼                                 ▼
┌──────────────────┐            ┌──────────────────┐
│  Frontend        │            │  Backend API     │
│  (React Static)  │            │  (FastAPI)       │
│  S3 + CloudFront │            │  EC2/Fargate     │
└──────────────────┘            └──────────────────┘
                                         │
                ┌────────────────────────┴────────────────────┐
                │                                             │
                ▼                                             ▼
┌──────────────────────────────┐            ┌──────────────────────┐
│  Database (PostgreSQL RDS)   │            │  Redis Cache         │
│  - Multi-customer data       │            │  - AI insights cache │
│  - Auto-scaling              │            │  - Session store     │
└──────────────────────────────┘            └──────────────────────┘
                │
                ▼
┌──────────────────────────────┐
│  Background Workers          │
│  - ETL jobs (Airflow)        │
│  - AI model training         │
│  - Alert monitoring          │
└──────────────────────────────┘
```

**Deployment Steps**:
1. Build frontend: `npm run build` → Static files to S3
2. Build backend: Docker image → Push to ECR → Deploy to ECS
3. Database migration: Alembic migrations to RDS
4. ETL scheduling: Airflow DAGs for hourly sync
5. Monitoring: CloudWatch + Sentry for error tracking

---

## 8. Security & Compliance

### 8.1 Data Security
- **Encryption at Rest**: Database encryption (RDS encryption)
- **Encryption in Transit**: HTTPS/TLS for all API calls
- **API Key Management**: Environment variables, AWS Secrets Manager
- **OAuth Tokens**: Encrypted storage, token refresh logic

### 8.2 Access Control
- **Multi-Tenancy**: Customer-level data isolation
- **Role-Based Access**: Admin, Manager, Viewer roles (future)
- **API Authentication**: JWT tokens (future)
- **Audit Logging**: Track all data access by user + customer

### 8.3 Compliance
- **GDPR**: Right to erasure (customer deletion API)
- **CCPA**: Data export API
- **PCI DSS**: No credit card storage (Shopify/Stripe handles payments)

---

## 9. Performance Optimization

### 9.1 Backend Optimizations
- **Database Indexing**: customer_id, date, campaign_id indexed
- **Query Optimization**: SQLAlchemy eager loading, joins
- **Caching**: Redis for AI insights, frequently accessed campaigns
- **Pagination**: Limit 100 records per API call, offset-based pagination
- **Background Jobs**: Celery for heavy tasks (AI model training, large ETL)

### 9.2 Frontend Optimizations
- **Code Splitting**: Lazy load dashboards (React.lazy)
- **Memoization**: useMemo, useCallback for expensive computations
- **Virtual Scrolling**: Large tables (react-window)
- **API Caching**: RTK Query automatic caching (5 min TTL)
- **Chart Optimization**: Recharts with dataKey optimization

### 9.3 Scalability
- **Horizontal Scaling**: Multiple FastAPI instances behind load balancer
- **Database Read Replicas**: Separate read/write databases
- **CDN**: CloudFront for static assets
- **Auto-Scaling**: ECS auto-scaling based on CPU/memory

---

## 10. Future Enhancements

### 10.1 Planned Features
1. **Real-Time Collaboration**: WebSocket for multi-user dashboard updates
2. **Custom Reports**: Drag-and-drop report builder
3. **White-Label Solution**: Rebrandable UI for agencies
4. **Mobile App**: React Native app for on-the-go monitoring
5. **Advanced AI**:
   - GPT-powered campaign copywriting
   - Image generation for ads (DALL-E integration)
   - Automated bid management (reinforcement learning)
6. **Integrations**:
   - Slack notifications
   - Zapier automation
   - BigQuery export
   - Salesforce CRM sync

### 10.2 Technical Debt
- Migrate SQLite → PostgreSQL for production
- Add comprehensive test coverage (pytest, Jest)
- Implement proper error boundaries in React
- Add API rate limiting
- GraphQL API for flexible queries

---

## 11. Appendix

### 11.1 Technology Glossary

| Term | Definition |
|------|------------|
| **ADK** | Agent Development Kit - Framework for building multi-agent systems |
| **LangGraph** | LangChain's state machine framework for agent orchestration |
| **GAQL** | Google Ads Query Language - SQL-like language for querying Google Ads API |
| **RTK Query** | Redux Toolkit Query - Data fetching and caching library |
| **PIE Model** | Potential-Importance-Ease prioritization framework |
| **LTV** | Lifetime Value - Total revenue a customer generates over their lifetime |
| **ROAS** | Return on Ad Spend - Revenue / Ad Spend |
| **CTR** | Click-Through Rate - Clicks / Impressions |
| **CPA** | Cost Per Acquisition - Cost / Conversions |
| **Quality Score** | Google Ads metric (1-10) for keyword relevance |

### 11.2 API Endpoint Reference

**Customer Management**:
- `GET /api/v1/customers` - List all customers
- `POST /api/v1/customers` - Create customer
- `GET /api/v1/customers/{customer_id}` - Get customer details

**Campaign Data**:
- `GET /api/v1/campaigns?customer_id={id}` - List campaigns
- `GET /api/v1/campaigns/{campaign_id}?customer_id={id}` - Campaign details
- `GET /api/v1/adgroups?customer_id={id}&campaign_id={id}` - Ad groups
- `GET /api/v1/keywords?customer_id={id}` - Keywords performance

**AI Intelligence**:
- `GET /api/v1/ai/greeting?customer_id={id}` - Personalized greeting
- `GET /api/v1/ai/insights?customer_id={id}` - AI-generated insights
- `GET /api/v1/ai/anomalies?customer_id={id}` - Anomaly detections

**Optimization**:
- `GET /api/v1/optimization/budget?customer_id={id}` - Budget recommendations
- `GET /api/v1/optimization/keywords?customer_id={id}` - Keyword bid suggestions
- `POST /api/v1/optimization/apply` - Apply optimization (future)

**Forecasting**:
- `GET /api/v1/forecast/spend?customer_id={id}` - Spend forecast
- `GET /api/v1/forecast/ctr?customer_id={id}` - CTR forecast
- `POST /api/v1/forecast/scenario` - Scenario simulation

**Alerts**:
- `GET /api/v1/alerts?customer_id={id}` - Active alerts
- `POST /api/v1/alerts/thresholds?customer_id={id}` - Configure thresholds

### 11.3 Database Schema Diagram

**Core Tables Relationships**:
```
customers (customer_id PK)
    │
    ├── campaigns (campaign_id PK, customer_id FK)
    │       │
    │       ├── ad_groups (ad_group_id PK, campaign_id FK, customer_id FK)
    │       │       │
    │       │       └── keywords (keyword_id PK, ad_group_id FK, campaign_id FK, customer_id FK)
    │       │               │
    │       │               └── search_terms (search_term_id PK, keyword_id FK, customer_id FK)
    │       │
    │       └── campaign_keywords (id PK, campaign_id FK, keyword_id FK, customer_id FK)
    │
    ├── ml_features (id PK, customer_id FK)
    │
    ├── shopify_stores (store_id PK, customer_id FK)
    │       │
    │       ├── shopify_orders (order_id PK, store_id FK, customer_id FK)
    │       ├── shopify_products (product_id PK, store_id FK, customer_id FK)
    │       ├── shopify_customers (shopify_customer_id PK, store_id FK, customer_id FK)
    │       └── shopify_cart_events (event_id PK, store_id FK, customer_id FK)
    │
    ├── meta_ad_accounts (account_id PK, customer_id FK)
    │       │
    │       └── meta_campaigns (campaign_id PK, account_id FK, customer_id FK)
    │               │
    │               ├── meta_adsets (adset_id PK, campaign_id FK, customer_id FK)
    │               │       │
    │               │       └── meta_ads (ad_id PK, adset_id FK, campaign_id FK, customer_id FK)
    │               │
    │               └── meta_insights (insight_id PK, campaign_id FK, customer_id FK)
    │
    └── ga4_properties (property_id PK, customer_id FK)
            │
            ├── ga4_sessions (session_id PK, property_id FK, customer_id FK)
            ├── ga4_events (event_id PK, property_id FK, customer_id FK)
            ├── ga4_conversion_paths (path_id PK, property_id FK, customer_id FK)
            └── ga4_audiences (audience_id PK, property_id FK, customer_id FK)
```

---

## 12. Contact & Support

**Documentation**: https://docs.marketingiq.ai (future)
**API Reference**: https://api.marketingiq.ai/docs
**GitHub**: https://github.com/marketingiq/platform (private)
**Support Email**: support@marketingiq.ai

---

**Document Version**: 1.0
**Last Updated**: 2025-11-08
**Author**: MarketingIQ Engineering Team
