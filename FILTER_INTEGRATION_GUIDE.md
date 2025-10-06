# Customer Filter Integration Guide

## Implementation Summary

The customer filtering system has been implemented across all layers of the MarketingIQ platform:

### ✅ Completed Implementation

#### 1. Database Layer
- All warehouse tables already have `customer_id` fields:
  - `campaigns_performance`
  - `adgroups_performance`
  - `keywords_performance`
  - `search_terms`
  - `ml_features`

#### 2. Backend API (api/app/)
- **New Customer Endpoint**: `/api/v1/customers`
  - `GET /customers` - List all customers with campaign counts
  - `GET /customers/{id}/summary` - Get customer metrics summary

- **Updated Routes** (all now accept `customer_id` query parameter):
  - `GET /campaigns?customer_id={id}`
  - `GET /keywords?customer_id={id}`
  - `GET /search-terms?customer_id={id}`
  - `GET /metrics/summary?customer_id={id}`

#### 3. Multi-Agent System
- Updated `APIClient` in `google-ads-multiagent/adk/orchestration_agent/sub_agents/data_agent/api_client.py`
  - All methods now accept and forward `customer_id` parameter
  - Added `fetch_customers()` method
  - Cache keys updated to include customer_id

#### 4. Frontend Components

**New Components Created:**

1. **GlobalFilterBar** (`web/src/components/common/GlobalFilterBar.tsx`)
   - Customer selector dropdown
   - Date range selector
   - Campaign type filter
   - Collapsible/expandable design
   - Shows active filter count

2. **FilterContext** (`web/src/context/FilterContext.tsx`)
   - Global state management for filters
   - Persists to localStorage
   - Provides `useFilters()` hook

3. **useFilteredAPI Hook** (`web/src/hooks/useFilteredAPI.ts`)
   - Automatically includes filters in API calls
   - Helper hooks: `useCampaigns()`, `useKeywords()`, etc.

**Updated Components:**
- `web/src/index.tsx` - Wrapped app with FilterProvider
- `web/src/components/common/Layout.tsx` - Added GlobalFilterBar

---

## How to Use Filters in Dashboard Components

### Method 1: Using Context Hook

```typescript
import { useFilters } from '../../context/FilterContext';

const MyDashboard: React.FC = () => {
  const { filters } = useFilters();

  // filters.customerId - currently selected customer
  // filters.dateRange - selected date range
  // filters.campaignType - selected campaign type

  useEffect(() => {
    fetchData();
  }, [filters]); // Re-fetch when filters change

  return <div>Dashboard for Customer {filters.customerId}</div>;
};
```

### Method 2: Using useFilteredAPI Hook (Recommended)

```typescript
import { useCampaigns, useMetricsSummary } from '../../hooks/useFilteredAPI';

const CampaignsDashboard: React.FC = () => {
  // Automatically filtered by current customer
  const { data: campaigns, loading, error, refetch } = useCampaigns();
  const { data: metrics } = useMetricsSummary();

  if (loading) return <CircularProgress />;
  if (error) return <Typography>Error: {error.message}</Typography>;

  return (
    <div>
      <Typography>Campaigns: {campaigns?.total}</Typography>
      {campaigns?.campaigns.map(c => (
        <div key={c.campaign_id}>{c.campaign_name}</div>
      ))}
    </div>
  );
};
```

### Method 3: Custom API Calls with Filters

```typescript
import { useFilters } from '../../context/FilterContext';
import axios from 'axios';

const MyDashboard: React.FC = () => {
  const { filters } = useFilters();
  const [data, setData] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!filters.customerId) return;

      const response = await axios.get('http://localhost:8000/api/v1/campaigns', {
        params: {
          customer_id: filters.customerId,
          date_range: filters.dateRange,
          campaign_type: filters.campaignType
        }
      });

      setData(response.data);
    };

    fetchData();
  }, [filters.customerId, filters.dateRange, filters.campaignType]);

  return <div>{/* Render data */}</div>;
};
```

---

## Filter Flow Diagram

```
┌─────────────────────────────────────┐
│  GlobalFilterBar (Top of Layout)   │
│  - Customer Selector                │
│  - Date Range Picker                │
│  - Campaign Type Filter             │
└─────────────┬───────────────────────┘
              │
              │ Updates FilterContext
              ▼
┌─────────────────────────────────────┐
│       FilterContext (Global)        │
│  filters: {                         │
│    customerId: 123456789            │
│    dateRange: "LAST_30_DAYS"        │
│    campaignType: "SEARCH"           │
│  }                                  │
└─────────────┬───────────────────────┘
              │
              │ useFilters() hook
              ▼
┌─────────────────────────────────────┐
│    Dashboard Components             │
│  - UnifiedDashboard                 │
│  - CampaignsDashboard               │
│  - KeywordsDashboard                │
│  - All other dashboards             │
└─────────────┬───────────────────────┘
              │
              │ useFilteredAPI()
              ▼
┌─────────────────────────────────────┐
│     Backend API Requests            │
│  GET /campaigns?customer_id=123456  │
│  GET /keywords?customer_id=123456   │
│  GET /metrics/summary?customer_id.. │
└─────────────┬───────────────────────┘
              │
              │ SQL Queries
              ▼
┌─────────────────────────────────────┐
│         SQLite Database             │
│  WHERE customer_id = 123456789      │
└─────────────────────────────────────┘
```

---

## Next Steps - Dashboard Updates Needed

To complete the integration, update each dashboard component to use the filter context:

### Priority 1: Core Dashboards
- [x] UnifiedDashboard - Update to use useFilteredAPI
- [ ] CampaignsDashboard - Replace hardcoded API calls
- [ ] KeywordsDashboard - Add customer filtering
- [ ] SearchTermsDashboard - Add customer filtering

### Priority 2: Insight Dashboards
- [ ] CampaignInsights - Filter insights by customer
- [ ] AnomalyDetection - Show only customer anomalies
- [ ] InsightsSummary - Customer-specific summary

### Priority 3: Optimization Dashboards
- [ ] BudgetOptimizer - Optimize for selected customer
- [ ] KeywordOptimizer - Customer keyword optimization
- [ ] CampaignSimulator - Simulate for customer campaigns

### Priority 4: Forecasting Dashboards
- [ ] CTRForecast - Forecast customer CTR
- [ ] SpendForecast - Customer spend forecast
- [ ] ScenarioSimulator - Customer-specific scenarios

### Priority 5: Alert Dashboards
- [ ] AlertsDashboard - Customer-scoped alerts
- [ ] ThresholdsMonitor - Customer threshold monitoring

---

## Testing the Implementation

### 1. Start Backend API
```bash
cd api
uvicorn app.main:app --reload --port 8000
```

### 2. Verify Customer Endpoint
```bash
curl http://localhost:8000/api/v1/customers
```

Should return:
```json
{
  "customers": [
    {
      "customer_id": 3341907700,
      "customer_name": "Customer 3341907700",
      "campaigns_count": 4
    }
  ],
  "total": 1
}
```

### 3. Test Filtered Campaign Query
```bash
curl "http://localhost:8000/api/v1/campaigns?customer_id=3341907700"
```

### 4. Start React App
```bash
cd marketingiq-platform/web
npm start
```

### 5. Verify UI
- Check that filter bar appears at top of all pages
- Select a customer from dropdown
- Verify dashboards update to show only that customer's data
- Change date range and verify updates
- Check browser localStorage for persisted filters

---

## Architecture Benefits

✅ **Scalability**: Easily handles multiple customers/clients
✅ **CEO/Team View**: Each user sees only their customer's data
✅ **Google Ads Parity**: Matches expectation from Google Ads UI
✅ **Performance**: Queries filtered at database level
✅ **Multi-tenant Ready**: Foundation for multi-tenant SaaS
✅ **Agent Support**: All AI agents respect customer filtering
✅ **Persistent State**: Filters saved across page refreshes
✅ **Clean Separation**: Filter logic centralized, not scattered

---

## File Reference

### Backend
- `api/app/routes/customers.py` - New customer endpoints
- `api/app/routes/campaigns.py` - Updated campaign routes
- `api/app/routes/keywords.py` - Updated keyword routes
- `api/app/routes/search_terms.py` - Updated search term routes
- `api/app/main.py` - Added customers router

### Frontend
- `web/src/components/common/GlobalFilterBar.tsx` - Filter UI component
- `web/src/context/FilterContext.tsx` - Global filter state
- `web/src/hooks/useFilteredAPI.ts` - API hook with auto-filtering
- `web/src/components/common/Layout.tsx` - Integrated filter bar
- `web/src/index.tsx` - Added FilterProvider

### Multi-Agent
- `google-ads-multiagent/adk/.../api_client.py` - Updated API client

---

## Summary

The customer filtering system is **fully implemented** at the backend and agent layers, with the frontend infrastructure in place. The GlobalFilterBar is now visible on all pages and will automatically filter data as you select different customers.

The main remaining work is updating individual dashboard components to use the `useFilteredAPI` hooks or `useFilters` context, which can be done incrementally without breaking existing functionality.