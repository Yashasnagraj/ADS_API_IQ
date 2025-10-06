# Dashboard Enhancement Implementation Guide

## 🎯 Overview

This guide shows how to add **interactive KPIs** and **enhanced visualizations** to ALL MarketingIQ dashboards.

## ⚠️ CRITICAL: Data-Driven Approach

**NO HARDCODING!** All data MUST come from:
- ✅ API responses (`useFilteredAPI`, `useCampaigns`, `useKeywords`, etc.)
- ✅ Database warehouse tables
- ✅ Real-time metrics calculations
- ❌ NO mock data
- ❌ NO hardcoded values
- ❌ NO static arrays

### Example - WRONG (Hardcoded):
```tsx
// ❌ DON'T DO THIS
const kpiValue = 45; // Hardcoded
const trendValue = 12.5; // Hardcoded
```

### Example - CORRECT (Data-Driven):
```tsx
// ✅ DO THIS
const { data: metricsData } = useMetricsSummary();
const kpiValue = metricsData?.total_campaigns || 0; // From API
const trendValue = calculateTrend(metricsData?.historical) || 0; // Calculated
```

### ✅ Completed Reference Implementation
- **Anomaly Detection Dashboard** (`/src/agents/insight_agent/AnomalyDetection.tsx`) - Fully implemented with:
  - Interactive KPI cards that open detail drawers
  - Enhanced charts with axis labels
  - Professional color palette

---

## 📦 New Components Created

### 1. **InteractiveKPICard** (`/src/components/kpi/InteractiveKPICard.tsx`)
- Clickable KPI cards with hover effects
- Badge indicator showing it's interactive
- Supports drill-down functionality

### 2. **KPIDetailDrawer** (`/src/components/kpi/KPIDetailDrawer.tsx`)
- Reusable drawer for showing KPI details
- Supports list and table views
- Shows trend charts for metrics

### 3. **EnhancedChart** (`/src/components/charts/EnhancedChart.tsx`)
- Wrapper for Recharts with axis labels
- Automatic formatting (currency, percentage, number)
- Professional styling

### 4. **chartTheme.ts** (`/src/components/charts/chartTheme.ts`)
- Color palette and formatting utilities
- Gradient definitions
- Responsive configurations

---

## 🔧 Step-by-Step Implementation

### Step 1: Add Imports

```tsx
// Add these imports to your dashboard
import InteractiveKPICard from '../../components/kpi/InteractiveKPICard';
import KPIDetailDrawer, { KPIDetailItem } from '../../components/kpi/KPIDetailDrawer';
import { EnhancedChart } from '../../components/charts/EnhancedChart';
```

### Step 2: Add State for Drawer

```tsx
const [drawerOpen, setDrawerOpen] = useState(false);
const [drawerData, setDrawerData] = useState<KPIDetailItem[]>([]);
const [drawerTitle, setDrawerTitle] = useState('');
const [drawerSubtitle, setDrawerSubtitle] = useState('');
```

### Step 3: Create KPI Click Handler

```tsx
const handleKPIClick = (filterType?: string) => {
  // Filter your data based on the KPI clicked
  const filteredData = filterType
    ? data.filter(item => item.type === filterType)
    : data;

  // Map to KPIDetailItem format
  const drawerItems: KPIDetailItem[] = filteredData.map(item => ({
    id: item.id,
    name: item.name,
    value: item.value,
    status: item.status, // 'success' | 'warning' | 'error' | 'info'
    subtitle: item.subtitle,
    trend: item.trendPercentage,
  }));

  setDrawerData(drawerItems);
  setDrawerTitle('Your KPI Title');
  setDrawerSubtitle('Description of what this shows');
  setDrawerOpen(true);
};
```

### Step 4: Replace CompactKPICard with InteractiveKPICard

**Before:**
```tsx
<CompactKPICard
  title="Total Campaigns"
  value={campaigns.length}
  format="number"
  icon={<Campaign />}
  trend="up"
  trendValue={12}
  color="primary"
  index={0}
/>
```

**After:**
```tsx
<InteractiveKPICard
  title="Total Campaigns"
  value={campaigns.length}
  format="number"
  icon={<Campaign />}
  trend="up"
  trendValue={12}
  color="primary"
  onClick={() => handleKPIClick()}  // NEW: Add click handler
  drillDownAvailable={true}           // NEW: Show badge
  index={0}
/>
```

### Step 5: Add KPIDetailDrawer Component

```tsx
<KPIDetailDrawer
  open={drawerOpen}
  onClose={() => setDrawerOpen(false)}
  title={drawerTitle}
  subtitle={drawerSubtitle}
  data={drawerData}
  type="table"  // or "list"
  color="primary"
  showTopCount={10}
/>
```

### Step 6: Replace Chart with EnhancedChart

**Before:**
```tsx
<ResponsiveContainer width="100%" height={300}>
  <LineChart data={chartData}>
    <CartesianGrid strokeDasharray="3 3" />
    <XAxis dataKey="date" />
    <YAxis />
    <Tooltip />
    <Line dataKey="revenue" stroke="#8884d8" />
  </LineChart>
</ResponsiveContainer>
```

**After:**
```tsx
<EnhancedChart
  height={300}
  xAxis={{ label: 'Date', dataKey: 'date' }}
  yAxis={{ label: 'Revenue ($)', format: 'currency' }}
  showGrid={true}
  showTooltip={true}
  showLegend={true}
>
  <LineChart data={chartData}>
    <Line
      dataKey="revenue"
      stroke="#8884d8"
      name="Revenue"
      strokeWidth={2}
      type="monotone"
    />
  </LineChart>
</EnhancedChart>
```

---

## 📊 Dashboard-Specific Examples

### Data Agent Dashboards

#### CampaignsDashboard.tsx
```tsx
// KPI: Total Campaigns → Show campaign list
handleCampaignsClick() {
  const items = campaigns.map(c => ({
    id: c.campaign_id,
    name: c.campaign_name,
    value: `₹${c.cost}`,
    status: c.status === 'ENABLED' ? 'success' : 'warning',
    subtitle: `${c.clicks} clicks, ${c.impressions} impressions`,
    trend: c.ctr_change,
  }));
  openDrawer('All Campaigns', items);
}
```

#### KeywordsDashboard.tsx
```tsx
// KPI: Top Performers → Show best keywords
handleTopPerformersClick() {
  const items = keywords
    .sort((a, b) => b.ctr - a.ctr)
    .slice(0, 10)
    .map(k => ({
      id: k.keyword_id,
      name: k.keyword_text,
      value: `${k.ctr}%`,
      status: 'success',
      subtitle: `Quality Score: ${k.quality_score}`,
    }));
  openDrawer('Top Performing Keywords', items);
}
```

### Insight Agent Dashboards

#### CampaignInsights.tsx
```tsx
// KPI: Insights Count → Show insight breakdown
handleInsightsClick() {
  const items = insights.map(i => ({
    id: i.id,
    name: i.title,
    value: i.impact,
    status: i.type === 'opportunity' ? 'success' : 'warning',
    subtitle: i.description,
  }));
  openDrawer('Campaign Insights', items);
}
```

### Optimization Agent Dashboards

#### BudgetOptimizer.tsx
```tsx
// KPI: Potential Savings → Show campaigns to optimize
handleSavingsClick() {
  const items = budgetRecommendations.map(r => ({
    id: r.campaign_id,
    name: r.campaign_name,
    value: `₹${r.potential_savings}`,
    status: 'warning',
    subtitle: r.recommendation,
  }));
  openDrawer('Budget Optimization Opportunities', items);
}
```

### Forecasting Agent Dashboards

#### SpendForecast.tsx
```tsx
// KPI: Forecasted Spend → Show spend breakdown
handleForecastClick() {
  const items = forecast.breakdown.map(f => ({
    id: f.date,
    name: f.date,
    value: `₹${f.predicted_spend}`,
    status: f.within_budget ? 'success' : 'error',
    subtitle: `Confidence: ${f.confidence}%`,
  }));
  openDrawer('Spend Forecast Breakdown', items);
}
```

### Alert Agent Dashboards

#### AlertsDashboard.tsx
```tsx
// KPI: Active Alerts → Show all alerts
handleAlertsClick(severity?: string) {
  const filtered = severity
    ? alerts.filter(a => a.severity === severity)
    : alerts;

  const items = filtered.map(a => ({
    id: a.alert_id,
    name: a.title,
    value: a.metric_value,
    status: a.severity === 'critical' ? 'error' : 'warning',
    subtitle: a.description,
  }));
  openDrawer(`${severity || 'All'} Alerts`, items);
}
```

---

## 🎨 Chart Enhancement Patterns

### Line Chart (Trend)
```tsx
<EnhancedChart
  height={300}
  xAxis={{ label: 'Date', dataKey: 'date' }}
  yAxis={{ label: 'CTR (%)', format: 'percentage' }}
>
  <LineChart data={trendData}>
    <Line dataKey="ctr" stroke="#10b981" strokeWidth={3} type="monotone" />
  </LineChart>
</EnhancedChart>
```

### Bar Chart (Comparison)
```tsx
<EnhancedChart
  height={300}
  xAxis={{ label: 'Campaign', dataKey: 'name' }}
  yAxis={{ label: 'Revenue ($)', format: 'currency' }}
>
  <BarChart data={campaignData}>
    <Bar dataKey="revenue" fill="#6366f1" radius={[4, 4, 0, 0]} />
  </BarChart>
</EnhancedChart>
```

### Area Chart (Volume)
```tsx
<EnhancedChart
  height={300}
  xAxis={{ label: 'Time', dataKey: 'time' }}
  yAxis={{ label: 'Impressions', format: 'compact' }}
>
  <AreaChart data={volumeData}>
    <Area
      dataKey="impressions"
      fill="url(#gradient)"
      stroke="#3b82f6"
      type="monotone"
    />
  </AreaChart>
</EnhancedChart>
```

### Pie Chart (Distribution)
```tsx
<ResponsiveContainer width="100%" height={300}>
  <PieChart>
    <Pie
      data={distributionData}
      dataKey="value"
      nameKey="name"
      cx="50%"
      cy="50%"
      outerRadius={100}
      label={(entry) => `${entry.name}: ${entry.value}%`}
    >
      {distributionData.map((entry, index) => (
        <Cell key={`cell-${index}`} fill={chartColors[index]} />
      ))}
    </Pie>
    <RechartsTooltip formatter={(value) => `${value}%`} />
  </PieChart>
</ResponsiveContainer>
```

---

## ✅ Implementation Checklist

Use this checklist for each dashboard:

### KPI Cards
- [ ] Replace `CompactKPICard` with `InteractiveKPICard`
- [ ] Add `onClick` handler for clickable KPIs
- [ ] Add `drillDownAvailable={true}` prop
- [ ] Create KPI click handler function
- [ ] Map data to `KPIDetailItem[]` format

### Drawer
- [ ] Add drawer state (open, data, title, subtitle)
- [ ] Add `KPIDetailDrawer` component
- [ ] Configure drawer type ('list' or 'table')
- [ ] Add trend data if available

### Charts
- [ ] Wrap charts with `EnhancedChart`
- [ ] Add `xAxis` label with appropriate format
- [ ] Add `yAxis` label with appropriate format
- [ ] Set `showGrid={true}`
- [ ] Set `showTooltip={true}`
- [ ] Add `showLegend={true}` for multi-series
- [ ] Add `name` prop to data series for legend

### Styling
- [ ] Use colors from `chartTheme.ts`
- [ ] Add smooth line types (`type="monotone"`)
- [ ] Increase stroke width for better visibility
- [ ] Add gradient fills for area charts
- [ ] Use radius for bar charts

---

## 🚀 Quick Copy-Paste Templates

### Complete Interactive KPI Section
```tsx
// State
const [drawerOpen, setDrawerOpen] = useState(false);
const [drawerData, setDrawerData] = useState<KPIDetailItem[]>([]);
const [drawerTitle, setDrawerTitle] = useState('');

// Handler
const handleKPIClick = (items: any[], title: string) => {
  const drawerItems: KPIDetailItem[] = items.map(item => ({
    id: item.id,
    name: item.name,
    value: item.value,
    status: item.status,
    subtitle: item.subtitle,
    trend: item.trend,
  }));
  setDrawerData(drawerItems);
  setDrawerTitle(title);
  setDrawerOpen(true);
};

// JSX
<Grid container spacing={3}>
  <Grid item xs={12} sm={6} md={3}>
    <InteractiveKPICard
      title="Your Metric"
      value={metricValue}
      format="number"
      icon={<YourIcon />}
      trend="up"
      trendValue={12}
      color="primary"
      onClick={() => handleKPIClick(yourData, 'Metric Details')}
      drillDownAvailable={true}
    />
  </Grid>
</Grid>

<KPIDetailDrawer
  open={drawerOpen}
  onClose={() => setDrawerOpen(false)}
  title={drawerTitle}
  data={drawerData}
  type="table"
  color="primary"
/>
```

### Complete Enhanced Chart
```tsx
<EnhancedChart
  height={300}
  xAxis={{ label: 'X-Axis Label', dataKey: 'xKey', format: 'number' }}
  yAxis={{ label: 'Y-Axis Label (units)', format: 'currency' }}
  showGrid={true}
  showTooltip={true}
  showLegend={true}
>
  <LineChart data={yourData}>
    <Line
      dataKey="metric1"
      stroke="#6366f1"
      strokeWidth={3}
      type="monotone"
      name="Metric 1"
    />
    <Line
      dataKey="metric2"
      stroke="#10b981"
      strokeWidth={3}
      type="monotone"
      name="Metric 2"
    />
  </LineChart>
</EnhancedChart>
```

---

## 📋 Dashboards to Update

### ✅ Completed
1. Anomaly Detection (`/agents/insight_agent/AnomalyDetection.tsx`)

### 🔄 To Update
2. Campaigns Dashboard (`/agents/data_agent/CampaignsDashboard.tsx`)
3. Keywords Dashboard (`/agents/data_agent/KeywordsDashboard.tsx`)
4. Ad Groups Dashboard (`/agents/data_agent/AdGroupsDashboard.tsx`)
5. Search Terms Dashboard (`/agents/data_agent/SearchTermsDashboard.tsx`)
6. Campaign Insights (`/agents/insight_agent/CampaignInsights.tsx`)
7. Keyword Insights (`/agents/insight_agent/KeywordInsights.tsx`)
8. Insights Summary (`/agents/insight_agent/InsightsSummary.tsx`)
9. Budget Optimizer (`/agents/optimization_agent/BudgetOptimizer.tsx`)
10. Keyword Optimizer (`/agents/optimization_agent/KeywordOptimizer.tsx`)
11. Campaign Simulator (`/agents/optimization_agent/CampaignSimulator.tsx`)
12. Spend Forecast (`/agents/forecasting_agent/SpendForecast.tsx`)
13. CTR Forecast (`/agents/forecasting_agent/CTRForecast.tsx`)
14. Scenario Simulator (`/agents/forecasting_agent/ScenarioSimulator.tsx`)
15. Alerts Dashboard (`/agents/alert_agent/AlertsDashboard.tsx`)
16. Thresholds Monitor (`/agents/alert_agent/ThresholdsMonitor.tsx`)

---

## 🎯 Success Criteria

### User Experience
- ✅ All KPIs are clickable and show hover effects
- ✅ Clicking KPI opens drawer with relevant details
- ✅ Drawer shows top items with "show more" if needed
- ✅ Charts have clear X and Y axis labels
- ✅ Chart tooltips show formatted values with units
- ✅ Professional color palette throughout

### Technical Quality
- ✅ Consistent use of InteractiveKPICard
- ✅ Consistent use of EnhancedChart
- ✅ Proper TypeScript typing
- ✅ Reusable, maintainable code
- ✅ Performance optimized (React.memo where needed)

---

## 📞 Support

For questions or issues:
1. Check reference implementation: `AnomalyDetection.tsx`
2. Review component docs in component files
3. Check `chartTheme.ts` for available formatters and colors
