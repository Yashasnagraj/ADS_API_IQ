# React Dashboards - Detailed Implementation Plan

**Project:** `D:\ADS_API\marketingiq-platform\web`

**Dashboard Structure (Standardized for All):**
1. **Header** - Title + description of what this dashboard shows
2. **Filters** - Customer selector, date range, campaign type, platform filters
3. **KPIs** - Key metrics (4-6 cards)
4. **AI Insights** - Descriptive, Diagnostic, Prescriptive analysis
5. **Visualizations** - Only necessary and meaningful charts

---

## 🎯 Dashboard List

### Core Dashboards:
1. **Unified Cross-Platform Dashboard** (`/dashboard/unified`) - NEW
2. **Google Ads Dashboard** (`/dashboard/google-ads`) - NEW
3. **Meta Ads Dashboard** (`/dashboard/meta-ads`) - NEW
4. **Google Analytics Dashboard** (`/dashboard/google-analytics`) - NEW
5. **E-Commerce Dashboard** (`/dashboard`) - EXISTING (enhance)

### Specialized Dashboards:
6. **Campaign Performance** (`/data/campaigns`)
7. **Keywords Analysis** (`/data/keywords`)
8. **Budget Optimizer** (`/optimization/budget`)
9. **Forecasting** (`/forecasting/overview`)
10. **Alerts & Anomalies** (`/alerts/dashboard`)

---

# 1. Unified Cross-Platform Dashboard

**Route:** `/dashboard/unified`
**Purpose:** Compare Google Ads, Meta Ads, and GA4 in one view. Help users decide where to invest budget.

## Structure:

### 1.1 Header
```tsx
<DashboardTemplate
  title="Unified Cross-Platform Analytics"
  subtitle="Compare Google Ads, Meta Ads, and Google Analytics performance side-by-side. AI-powered insights to optimize your marketing budget allocation."
  showAIBadge={true}
/>
```

**What it tells the user:**
> "This dashboard shows your complete marketing performance across all platforms. Use it to understand which platform gives the best ROI and where to invest more budget."

---

### 1.2 Filters
```tsx
<GlobalFilterBar
  filters={[
    { type: 'customer', label: 'Customer' },
    { type: 'dateRange', label: 'Date Range', default: 'LAST_30_DAYS' },
    { type: 'platform', label: 'Platform', options: ['ALL', 'Google Ads', 'Meta Ads', 'Organic'] }
  ]}
  onFilterChange={handleFilterChange}
/>
```

**Filter Options:**
- **Customer:** Dropdown of all customers
- **Date Range:** Last 7d, Last 30d, Last 90d, Custom
- **Platform:** All, Google Ads, Meta Ads, Organic (GA4)

---

### 1.3 KPIs (6 cards)

```tsx
<Grid container spacing={3}>
  {/* Row 1: Overall Metrics */}
  <Grid item xs={12} md={4}>
    <KPICard
      title="Total Marketing Spend"
      value="$12,450"
      change="+12%"
      trend="up"
      subtitle="Across all platforms"
      icon={<AttachMoney />}
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Blended ROAS"
      value="4.2x"
      change="+8%"
      trend="up"
      subtitle="Overall return on ad spend"
      icon={<TrendingUp />}
      highlight={true}
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Total Conversions"
      value="1,240"
      change="+24%"
      trend="up"
      subtitle="All platforms combined"
      icon={<ShoppingCart />}
    />
  </Grid>

  {/* Row 2: Platform Winners */}
  <Grid item xs={12} md={4}>
    <KPICard
      title="Best Platform (ROAS)"
      value="Google Ads"
      badge="5.2x ROAS"
      subtitle="Highest return on investment"
      icon={<Star />}
      color="success"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Best Platform (Conversions)"
      value="Google Ads"
      badge="64% of total"
      subtitle="Driving most conversions"
      icon={<Star />}
      color="success"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Cost Efficiency Leader"
      value="Organic (GA4)"
      badge="$0 CPC"
      subtitle="Free traffic with 4.2% CVR"
      icon={<Star />}
      color="info"
    />
  </Grid>
</Grid>
```

**KPI Insights:**
- Total Spend, ROAS, Conversions show overall performance
- Platform winners help user quickly see which platform is best
- Color coding: Green for winners, Blue for info

---

### 1.4 AI Insights (3 cards)

```tsx
<Stack spacing={2} sx={{ mt: 3 }}>
  {/* Descriptive Analysis */}
  <InsightCard
    type="descriptive"
    icon={<Assessment />}
    title="What Happened"
    insight="Google Ads generated 64% of conversions with only 48% of total spend, achieving 5.2x ROAS. Meta Ads contributed 28% of conversions at 3.9x ROAS. Organic traffic (GA4) shows strong 4.2% conversion rate with zero acquisition cost."
    priority="info"
  />

  {/* Diagnostic Analysis */}
  <InsightCard
    type="diagnostic"
    icon={<Psychology />}
    title="Why It Happened"
    insight="Google Ads outperforms because of high-intent search keywords. Meta Ads CTR dropped 18% in the last week due to audience fatigue in the 25-34 age group. Organic traffic has high engagement (avg. 3.2 pages/session) indicating strong brand interest."
    priority="medium"
    details={[
      'Google Search Ads converting at 3.8% (vs. Meta 2.1%)',
      'Meta frequency reached 4.2 (creative refresh needed)',
      'Organic bounce rate: 32% (excellent)'
    ]}
  />

  {/* Prescriptive Analysis */}
  <InsightCard
    type="prescriptive"
    icon={<Lightbulb />}
    title="What You Should Do"
    insight="Shift 15% of Meta Ads budget to Google Ads for estimated 23% higher ROI. Refresh Meta ad creatives to combat fatigue. Invest in SEO to capitalize on strong organic performance."
    priority="high"
    actions={[
      { label: 'Apply Budget Shift', onClick: applyBudgetRecommendation, primary: true },
      { label: 'View Details', onClick: viewDetails }
    ]}
    expectedImpact="+$1,240 revenue increase"
    confidence="87%"
  />
</Stack>
```

**AI Insight Types:**
1. **Descriptive** (What) - Summary of performance
2. **Diagnostic** (Why) - Root cause analysis
3. **Prescriptive** (Do) - Actionable recommendations with buttons

---

### 1.5 Visualizations (4 charts)

```tsx
<Grid container spacing={3} sx={{ mt: 2 }}>
  {/* Chart 1: Platform Comparison Table */}
  <Grid item xs={12}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Platform Performance Comparison
      </Typography>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Metric</TableCell>
            <TableCell>Google Ads</TableCell>
            <TableCell>Meta Ads</TableCell>
            <TableCell>Organic (GA4)</TableCell>
            <TableCell>Winner</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          <TableRow>
            <TableCell>Spend</TableCell>
            <TableCell>$5,200</TableCell>
            <TableCell>$3,800</TableCell>
            <TableCell>$0</TableCell>
            <TableCell><Chip label="N/A" size="small" /></TableCell>
          </TableRow>
          <TableRow>
            <TableCell>ROAS</TableCell>
            <TableCell>5.2x</TableCell>
            <TableCell>3.9x</TableCell>
            <TableCell>N/A</TableCell>
            <TableCell><Chip label="Google Ads" color="success" size="small" /></TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Conversions</TableCell>
            <TableCell>420</TableCell>
            <TableCell>285</TableCell>
            <TableCell>180</TableCell>
            <TableCell><Chip label="Google Ads" color="success" size="small" /></TableCell>
          </TableRow>
          <TableRow>
            <TableCell>CPC</TableCell>
            <TableCell>$1.20</TableCell>
            <TableCell>$2.10</TableCell>
            <TableCell>$0.00</TableCell>
            <TableCell><Chip label="Organic" color="info" size="small" /></TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Conversion Rate</TableCell>
            <TableCell>3.8%</TableCell>
            <TableCell>2.1%</TableCell>
            <TableCell>4.2%</TableCell>
            <TableCell><Chip label="Organic" color="info" size="small" /></TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </Paper>
  </Grid>

  {/* Chart 2: Spend vs Revenue by Platform */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Spend vs Revenue by Platform
      </Typography>
      <BarChart
        data={[
          { platform: 'Google Ads', spend: 5200, revenue: 27040 },
          { platform: 'Meta Ads', spend: 3800, revenue: 14820 },
          { platform: 'Organic', spend: 0, revenue: 7560 }
        ]}
        xKey="platform"
        bars={[
          { dataKey: 'spend', fill: '#ef5350', name: 'Spend' },
          { dataKey: 'revenue', fill: '#66bb6a', name: 'Revenue' }
        ]}
        height={300}
      />
    </Paper>
  </Grid>

  {/* Chart 3: Daily Trend - All Platforms */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Daily Performance Trend (Last 30 Days)
      </Typography>
      <LineChart
        data={dailyTrendData}
        xKey="date"
        lines={[
          { dataKey: 'googleAdsRevenue', stroke: '#4285f4', name: 'Google Ads' },
          { dataKey: 'metaAdsRevenue', stroke: '#1877f2', name: 'Meta Ads' },
          { dataKey: 'organicRevenue', stroke: '#34a853', name: 'Organic' }
        ]}
        height={300}
      />
    </Paper>
  </Grid>

  {/* Chart 4: Budget Allocation Recommendation */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Current vs Recommended Budget Allocation
      </Typography>
      <PieChart
        data={[
          { name: 'Google Ads (Current)', value: 58, color: '#4285f4' },
          { name: 'Meta Ads (Current)', value: 42, color: '#1877f2' }
        ]}
        recommendedData={[
          { name: 'Google Ads (Recommended)', value: 65, color: '#34a853' },
          { name: 'Meta Ads (Recommended)', value: 35, color: '#fbbc04' }
        ]}
        height={300}
      />
      <Typography variant="caption" color="text.secondary" sx={{ mt: 2, display: 'block' }}>
        AI Recommendation: Shift 7% from Meta to Google Ads for 15% higher overall ROAS
      </Typography>
    </Paper>
  </Grid>

  {/* Chart 5: Conversion Funnel by Platform */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>
        Conversion Funnel Comparison
      </Typography>
      <FunnelChart
        platforms={['Google Ads', 'Meta Ads', 'Organic']}
        stages={[
          { name: 'Impressions', googleAds: 100000, metaAds: 85000, organic: 45000 },
          { name: 'Clicks', googleAds: 11000, metaAds: 7200, organic: 12000 },
          { name: 'Landing Page Views', googleAds: 9800, metaAds: 6100, organic: 10800 },
          { name: 'Add to Cart', googleAds: 2100, metaAds: 920, organic: 1890 },
          { name: 'Conversions', googleAds: 420, metaAds: 285, organic: 180 }
        ]}
        height={350}
      />
    </Paper>
  </Grid>
</Grid>
```

**Why these charts:**
1. **Comparison Table** - Quick reference for all metrics
2. **Spend vs Revenue** - Visual ROI comparison
3. **Daily Trend** - Track performance over time
4. **Budget Allocation** - Show current vs recommended
5. **Conversion Funnel** - Identify where each platform loses users

---

### 1.6 Component File

**File:** `src/components/dashboard/UnifiedCrossPlatformDashboard.tsx`

```tsx
import React, { useState, useEffect } from 'react';
import DashboardTemplate from '../common/DashboardTemplate';
import GlobalFilterBar, { FilterState } from '../common/GlobalFilterBar';
import KPICard from '../common/KPICard';
import InsightCard from '../common/InsightCard';
import { Grid, Paper, Typography, Table, Stack } from '@mui/material';
import { fetchUnifiedMetrics, fetchPlatformComparison } from '../../services/analyticsService';

const UnifiedCrossPlatformDashboard: React.FC = () => {
  const [filters, setFilters] = useState<FilterState>({
    customerId: null,
    dateRange: 'LAST_30_DAYS',
    platform: 'ALL'
  });
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, [filters]);

  const loadData = async () => {
    setLoading(true);
    try {
      const metrics = await fetchUnifiedMetrics(filters);
      setData(metrics);
    } catch (error) {
      console.error('Failed to load unified metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <DashboardTemplate
      title="Unified Cross-Platform Analytics"
      subtitle="Compare Google Ads, Meta Ads, and Google Analytics performance side-by-side"
      showAIBadge={true}
    >
      {/* Filters */}
      <GlobalFilterBar
        onFilterChange={setFilters}
        initialFilters={filters}
      />

      {/* KPIs */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* KPI cards here */}
      </Grid>

      {/* AI Insights */}
      <Stack spacing={2} sx={{ mt: 3 }}>
        {/* InsightCard components */}
      </Stack>

      {/* Visualizations */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {/* Charts here */}
      </Grid>
    </DashboardTemplate>
  );
};

export default UnifiedCrossPlatformDashboard;
```

---

# 2. Google Ads Dashboard

**Route:** `/dashboard/google-ads`
**Purpose:** Deep dive into Google Ads performance only. No Meta or GA4 data.

## Structure:

### 2.1 Header
```tsx
<DashboardTemplate
  title="Google Ads Performance"
  subtitle="Comprehensive view of your Google Ads campaigns, keywords, and search terms. Optimize your search and shopping campaigns with AI-powered insights."
  showAIBadge={true}
/>
```

---

### 2.2 Filters
```tsx
<GlobalFilterBar
  filters={[
    { type: 'customer', label: 'Customer' },
    { type: 'dateRange', label: 'Date Range' },
    { type: 'campaignType', label: 'Campaign Type', options: ['ALL', 'SEARCH', 'SHOPPING', 'DISPLAY', 'VIDEO'] },
    { type: 'campaign', label: 'Campaign', multiSelect: true }
  ]}
  onFilterChange={handleFilterChange}
/>
```

---

### 2.3 KPIs (6 cards)

```tsx
<Grid container spacing={3}>
  <Grid item xs={12} md={4}>
    <KPICard
      title="Total Spend"
      value="$5,200"
      change="+8%"
      trend="up"
      subtitle="Last 30 days"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="ROAS"
      value="5.2x"
      change="+12%"
      trend="up"
      subtitle="Return on ad spend"
      highlight={true}
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Conversions"
      value="420"
      change="+24%"
      trend="up"
      subtitle="Total conversions"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Avg. CPC"
      value="$1.20"
      change="-5%"
      trend="down"
      trendPositive={true}
      subtitle="Cost per click"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="CTR"
      value="3.8%"
      change="+0.4%"
      trend="up"
      subtitle="Click-through rate"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Quality Score"
      value="7.2/10"
      change="+0.3"
      trend="up"
      subtitle="Avg. across all keywords"
    />
  </Grid>
</Grid>
```

---

### 2.4 AI Insights

```tsx
<Stack spacing={2} sx={{ mt: 3 }}>
  <InsightCard
    type="descriptive"
    title="Campaign Performance Summary"
    insight="Your Search campaigns generated 78% of conversions at 5.8x ROAS. Shopping campaigns contributed 18% at 4.1x ROAS. Display underperformed with 1.2x ROAS."
  />

  <InsightCard
    type="diagnostic"
    title="Top Performer Analysis"
    insight="'Brand Keywords' campaign has 12.4x ROAS due to high purchase intent. 'Competitor Terms' campaign struggling with 2.1x ROAS because of high CPCs ($4.20 avg) and low quality scores (4.2 avg)."
    details={[
      'Brand keywords: 8.5% CVR, $0.85 CPC',
      'Competitor terms: 1.8% CVR, $4.20 CPC, QS: 4.2',
      'Generic keywords: 3.2% CVR, $1.80 CPC, QS: 6.8'
    ]}
  />

  <InsightCard
    type="prescriptive"
    title="Optimization Recommendations"
    insight="Increase brand campaign budget by 25% (expected +$2,100 revenue). Pause 12 underperforming keywords with QS < 3. Add 8 negative keywords to reduce wasted spend by $450/month."
    priority="high"
    actions={[
      { label: 'Apply All Recommendations', primary: true },
      { label: 'View Keyword Details', onClick: viewKeywords }
    ]}
    expectedImpact="+$1,850 monthly profit"
    confidence="91%"
  />
</Stack>
```

---

### 2.5 Visualizations (5 charts)

```tsx
<Grid container spacing={3} sx={{ mt: 2 }}>
  {/* Chart 1: Campaign Performance Table */}
  <Grid item xs={12}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>Top Campaigns</Typography>
      <Table>
        {/* Campaign Name | Spend | ROAS | Conversions | CPC | Status */}
      </Table>
    </Paper>
  </Grid>

  {/* Chart 2: Spend & Revenue Trend (30 days) */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>Daily Spend & Revenue</Typography>
      <AreaChart data={dailyData} />
    </Paper>
  </Grid>

  {/* Chart 3: Campaign Type Performance */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>Performance by Campaign Type</Typography>
      <BarChart data={campaignTypeData} />
    </Paper>
  </Grid>

  {/* Chart 4: Top 10 Keywords */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>Top Performing Keywords</Typography>
      <Table size="small">
        {/* Keyword | Conversions | ROAS | QS */}
      </Table>
    </Paper>
  </Grid>

  {/* Chart 5: Quality Score Distribution */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6" gutterBottom>Quality Score Distribution</Typography>
      <PieChart data={qualityScoreData} />
    </Paper>
  </Grid>
</Grid>
```

**Why these charts:**
- **Campaign Table**: Quick overview of all campaigns
- **Spend/Revenue Trend**: Track daily performance
- **Campaign Type**: Compare Search vs Shopping vs Display
- **Top Keywords**: Identify winners
- **Quality Score**: Health indicator for account

---

# 3. Meta Ads Dashboard

**Route:** `/dashboard/meta-ads`
**Purpose:** Deep dive into Meta (Facebook/Instagram) Ads. No Google or GA4 data.

## Structure:

### 3.1 Header
```tsx
<DashboardTemplate
  title="Meta Ads Performance"
  subtitle="Analyze your Facebook and Instagram advertising performance. Demographic insights, creative analysis, and audience optimization powered by AI."
  showAIBadge={true}
/>
```

---

### 3.2 Filters
```tsx
<GlobalFilterBar
  filters={[
    { type: 'customer', label: 'Customer' },
    { type: 'dateRange', label: 'Date Range' },
    { type: 'platform', label: 'Platform', options: ['ALL', 'Facebook', 'Instagram', 'Messenger', 'Audience Network'] },
    { type: 'objective', label: 'Objective', options: ['ALL', 'CONVERSIONS', 'TRAFFIC', 'AWARENESS', 'LEADS'] },
    { type: 'campaign', label: 'Campaign', multiSelect: true }
  ]}
  onFilterChange={handleFilterChange}
/>
```

---

### 3.3 KPIs (6 cards)

```tsx
<Grid container spacing={3}>
  <Grid item xs={12} md={4}>
    <KPICard
      title="Total Spend"
      value="$3,800"
      change="+12%"
      subtitle="Last 30 days"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="ROAS"
      value="3.9x"
      change="+5%"
      highlight={true}
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Conversions"
      value="285"
      change="+18%"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Avg. CPC"
      value="$2.10"
      change="-8%"
      trendPositive={true}
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="CTR"
      value="2.1%"
      change="-18%"
      trend="down"
      subtitle="Potential ad fatigue"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Frequency"
      value="4.2"
      change="+1.1"
      trend="up"
      subtitle="Creative refresh needed"
      color="warning"
    />
  </Grid>
</Grid>
```

---

### 3.4 AI Insights

```tsx
<Stack spacing={2} sx={{ mt: 3 }}>
  <InsightCard
    type="descriptive"
    title="Platform & Audience Summary"
    insight="Instagram ads generated 62% of conversions, outperforming Facebook (34%). Your best-performing audience is 25-34 females with 4.8% conversion rate. Desktop placements underperform mobile by 45%."
  />

  <InsightCard
    type="diagnostic"
    title="Creative Fatigue Detected"
    insight="CTR dropped 18% in last 7 days due to ad fatigue. Your current creative set has been shown 4.2 times per user on average (frequency). Users aged 25-34 saw ads 5.8 times, causing diminishing returns."
    details={[
      'Frequency 25-34: 5.8 (critical)',
      'Frequency 35-44: 3.2 (healthy)',
      'CTR decline: -18% week-over-week',
      'Best performing creative: Video A (3.2% CTR)'
    ]}
    priority="high"
  />

  <InsightCard
    type="prescriptive"
    title="Refresh & Optimize"
    insight="Refresh ad creatives for 25-34 audience segment. Shift 20% budget from Facebook to Instagram. Reduce desktop spend by 30% and reallocate to mobile."
    actions={[
      { label: 'Pause Fatigued Ads', primary: true },
      { label: 'Create Creative Brief', onClick: createBrief }
    ]}
    expectedImpact="+35% CTR improvement, +$890 revenue"
    confidence="84%"
  />
</Stack>
```

---

### 3.5 Visualizations (6 charts)

```tsx
<Grid container spacing={3} sx={{ mt: 2 }}>
  {/* Chart 1: Campaign Performance Table */}
  <Grid item xs={12}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">Top Meta Campaigns</Typography>
      <Table>
        {/* Campaign | Objective | Spend | ROAS | Conversions | Frequency */}
      </Table>
    </Paper>
  </Grid>

  {/* Chart 2: Platform Breakdown (Facebook vs Instagram) */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">Performance by Platform</Typography>
      <BarChart
        data={[
          { platform: 'Instagram', conversions: 177, roas: 4.8 },
          { platform: 'Facebook', conversions: 97, roas: 2.9 },
          { platform: 'Messenger', conversions: 8, roas: 1.2 },
          { platform: 'Audience Network', conversions: 3, roas: 0.8 }
        ]}
      />
    </Paper>
  </Grid>

  {/* Chart 3: Age & Gender Demographics */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">Top Performing Demographics</Typography>
      <Table size="small">
        <TableBody>
          <TableRow>
            <TableCell>25-34 Female</TableCell>
            <TableCell>4.8% CVR</TableCell>
            <TableCell>5.2x ROAS</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>35-44 Female</TableCell>
            <TableCell>3.2% CVR</TableCell>
            <TableCell>4.1x ROAS</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>25-34 Male</TableCell>
            <TableCell>2.1% CVR</TableCell>
            <TableCell>3.2x ROAS</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </Paper>
  </Grid>

  {/* Chart 4: Daily Trend with Frequency */}
  <Grid item xs={12}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">Daily Performance & Ad Frequency</Typography>
      <ComboChart
        data={dailyData}
        lines={[
          { dataKey: 'conversions', stroke: '#1877f2' }
        ]}
        bars={[
          { dataKey: 'frequency', fill: '#fbbc04' }
        ]}
      />
    </Paper>
  </Grid>

  {/* Chart 5: Device Performance */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">Device Breakdown</Typography>
      <PieChart
        data={[
          { name: 'Mobile', value: 78, roas: 4.5 },
          { name: 'Desktop', value: 19, roas: 2.1 },
          { name: 'Tablet', value: 3, roas: 1.8 }
        ]}
      />
    </Paper>
  </Grid>

  {/* Chart 6: Top Countries */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">Geographic Performance</Typography>
      <Table size="small">
        <TableBody>
          <TableRow>
            <TableCell>United States</TableCell>
            <TableCell>68%</TableCell>
            <TableCell>4.2x ROAS</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>Canada</TableCell>
            <TableCell>18%</TableCell>
            <TableCell>3.8x ROAS</TableCell>
          </TableRow>
          <TableRow>
            <TableCell>United Kingdom</TableCell>
            <TableCell>9%</TableCell>
            <TableCell>3.2x ROAS</TableCell>
          </TableRow>
        </TableBody>
      </Table>
    </Paper>
  </Grid>
</Grid>
```

**Why these charts:**
- **Campaign Table**: Overview of all campaigns
- **Platform Breakdown**: Facebook vs Instagram performance
- **Demographics**: Age/gender insights
- **Daily Trend**: Track frequency impact
- **Device**: Mobile vs desktop optimization
- **Geographic**: Country performance

---

# 4. Google Analytics (GA4) Dashboard

**Route:** `/dashboard/google-analytics`
**Purpose:** Analyze website traffic, user behavior, and organic performance. No paid ads data.

## Structure:

### 4.1 Header
```tsx
<DashboardTemplate
  title="Google Analytics (GA4) - Website Performance"
  subtitle="Understand your website traffic, user behavior, conversion funnels, and organic performance. Identify opportunities to improve user experience and conversion rates."
  showAIBadge={true}
/>
```

---

### 4.2 Filters
```tsx
<GlobalFilterBar
  filters={[
    { type: 'customer', label: 'Customer' },
    { type: 'dateRange', label: 'Date Range' },
    { type: 'source', label: 'Traffic Source', options: ['ALL', 'Organic', 'Direct', 'Referral', 'Social'] },
    { type: 'device', label: 'Device', options: ['ALL', 'Desktop', 'Mobile', 'Tablet'] }
  ]}
  onFilterChange={handleFilterChange}
/>
```

---

### 4.3 KPIs (6 cards)

```tsx
<Grid container spacing={3}>
  <Grid item xs={12} md={4}>
    <KPICard
      title="Total Sessions"
      value="45,200"
      change="+15%"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Conversion Rate"
      value="4.2%"
      change="+0.3%"
      highlight={true}
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Conversions"
      value="1,898"
      change="+18%"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Bounce Rate"
      value="32%"
      change="-4%"
      trend="down"
      trendPositive={true}
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Avg. Session Duration"
      value="2:45"
      change="+12s"
      trend="up"
    />
  </Grid>

  <Grid item xs={12} md={4}>
    <KPICard
      title="Pages per Session"
      value="3.2"
      change="+0.4"
    />
  </Grid>
</Grid>
```

---

### 4.4 AI Insights

```tsx
<Stack spacing={2} sx={{ mt: 3 }}>
  <InsightCard
    type="descriptive"
    title="Traffic & Engagement Overview"
    insight="Organic search drives 58% of traffic with excellent 4.2% conversion rate. Direct traffic shows highest engagement (4.1 pages/session). Mobile traffic is 72% of total, converting at 3.8%."
  />

  <InsightCard
    type="diagnostic"
    title="Conversion Funnel Analysis"
    insight="Your checkout page has 42% drop-off rate, likely due to 8.5s load time (3x slower than homepage). Users who view product comparison page convert 2.8x higher than those who don't."
    details={[
      'Checkout abandonment: 42%',
      'Checkout page load time: 8.5s (critical)',
      'Product comparison viewers: 2.8x CVR',
      'Mobile checkout: 48% abandonment vs 36% desktop'
    ]}
    priority="high"
  />

  <InsightCard
    type="prescriptive"
    title="Optimize User Journey"
    insight="Optimize checkout page load time (target <3s) to reduce abandonment. Promote product comparison feature on category pages. Improve mobile checkout UX (currently 48% abandonment)."
    actions={[
      { label: 'View Technical Recommendations', primary: true },
      { label: 'Analyze Checkout Flow', onClick: analyzeCheckout }
    ]}
    expectedImpact="+18% conversion rate, +$4,200/month revenue"
    confidence="79%"
  />
</Stack>
```

---

### 4.5 Visualizations (6 charts)

```tsx
<Grid container spacing={3} sx={{ mt: 2 }}>
  {/* Chart 1: Traffic Sources Table */}
  <Grid item xs={12}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">Traffic Sources</Typography>
      <Table>
        {/* Source | Sessions | Conversions | CVR | Bounce Rate */}
      </Table>
    </Paper>
  </Grid>

  {/* Chart 2: Daily Sessions Trend */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">Daily Sessions (30 Days)</Typography>
      <LineChart data={dailySessions} />
    </Paper>
  </Grid>

  {/* Chart 3: Conversion Funnel */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">Conversion Funnel</Typography>
      <FunnelChart
        stages={[
          { name: 'Landing Page', users: 45200, dropOff: 0 },
          { name: 'Product Page', users: 18800, dropOff: 58% },
          { name: 'Add to Cart', users: 4512, dropOff: 76% },
          { name: 'Checkout', users: 3260, dropOff: 28% },
          { name: 'Purchase', users: 1898, dropOff: 42% }
        ]}
      />
    </Paper>
  </Grid>

  {/* Chart 4: Top Pages */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">Top Landing Pages</Typography>
      <Table size="small">
        {/* Page | Sessions | CVR | Bounce Rate */}
      </Table>
    </Paper>
  </Grid>

  {/* Chart 5: Device Performance */}
  <Grid item xs={12} md={6}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">Device Breakdown</Typography>
      <BarChart
        data={[
          { device: 'Mobile', sessions: 32544, cvr: 3.8 },
          { device: 'Desktop', sessions: 11296, cvr: 5.1 },
          { device: 'Tablet', sessions: 1360, cvr: 2.9 }
        ]}
      />
    </Paper>
  </Grid>

  {/* Chart 6: User Behavior Flow */}
  <Grid item xs={12}>
    <Paper sx={{ p: 3 }}>
      <Typography variant="h6">User Behavior Flow</Typography>
      <SankeyChart
        data={{
          nodes: [
            { name: 'Homepage' },
            { name: 'Category Page' },
            { name: 'Product Page' },
            { name: 'Cart' },
            { name: 'Checkout' },
            { name: 'Exit' }
          ],
          links: [
            { source: 0, target: 1, value: 15000 },
            { source: 0, target: 2, value: 8000 },
            { source: 1, target: 2, value: 12000 },
            // ... more flow data
          ]
        }}
      />
    </Paper>
  </Grid>
</Grid>
```

---

# 5. E-Commerce Dashboard (Enhanced)

**Route:** `/dashboard`
**Purpose:** E-commerce metrics across all platforms. Revenue, orders, products.

## Structure:

### 5.1 Header
```tsx
<DashboardTemplate
  title="E-Commerce Performance Dashboard"
  subtitle="Revenue, orders, and product performance across all marketing channels. Track your e-commerce KPIs and identify top-selling products."
  showAIBadge={true}
/>
```

---

### 5.2 Filters
```tsx
<GlobalFilterBar
  filters={[
    { type: 'customer', label: 'Customer' },
    { type: 'dateRange', label: 'Date Range' },
    { type: 'channel', label: 'Channel', options: ['ALL', 'Google Ads', 'Meta Ads', 'Organic', 'Direct'] },
    { type: 'product', label: 'Product Category', options: ['ALL', 'Electronics', 'Clothing', 'Home'] }
  ]}
/>
```

---

### 5.3 KPIs (6 cards)

```tsx
<Grid container spacing={3}>
  <Grid item xs={12} md={4}>
    <KPICard title="Total Revenue" value="$49,400" change="+18%" />
  </Grid>
  <Grid item xs={12} md={4}>
    <KPICard title="Total Orders" value="1,898" change="+15%" highlight={true} />
  </Grid>
  <Grid item xs={12} md={4}>
    <KPICard title="Avg. Order Value" value="$26.03" change="+3%" />
  </Grid>
  <Grid item xs={12} md={4}>
    <KPICard title="Cart Abandonment" value="42%" change="-5%" trend="down" trendPositive={true} />
  </Grid>
  <Grid item xs={12} md={4}>
    <KPICard title="Customer LTV" value="$142" change="+8%" />
  </Grid>
  <Grid item xs={12} md={4}>
    <KPICard title="Repeat Purchase Rate" value="28%" change="+4%" />
  </Grid>
</Grid>
```

---

### 5.4 AI Insights

```tsx
<Stack spacing={2}>
  <InsightCard
    type="descriptive"
    insight="Google Ads drove 52% of e-commerce revenue ($25,688) with $26.05 AOV. Electronics category is top seller (48% of revenue). Mobile checkout improving: 38% abandonment vs 42% last month."
  />

  <InsightCard
    type="diagnostic"
    insight="Repeat purchase rate dropped from 32% to 28% because email automation stopped working for 12 days. Cart abandonment spikes on mobile at checkout payment step (48%)."
    priority="medium"
  />

  <InsightCard
    type="prescriptive"
    insight="Fix email automation to recover repeat purchases. Implement mobile-optimized payment options (Apple Pay, Google Pay) to reduce abandonment. Cross-sell electronics with accessories (+$3,200 potential revenue)."
    actions={[{ label: 'Setup Cross-Sell Rules', primary: true }]}
    expectedImpact="+$4,800/month revenue"
  />
</Stack>
```

---

### 5.5 Visualizations (5 charts)

```tsx
<Grid container spacing={3}>
  {/* Revenue by Channel */}
  <Grid item xs={12} md={6}>
    <Paper><BarChart title="Revenue by Channel" /></Paper>
  </Grid>

  {/* Daily Revenue Trend */}
  <Grid item xs={12} md={6}>
    <Paper><LineChart title="Daily Revenue (30 Days)" /></Paper>
  </Grid>

  {/* Top Products Table */}
  <Grid item xs={12}>
    <Paper><ProductTable /></Paper>
  </Grid>

  {/* Purchase Funnel */}
  <Grid item xs={12} md={6}>
    <Paper><FunnelChart /></Paper>
  </Grid>

  {/* Customer Segments */}
  <Grid item xs={12} md={6}>
    <Paper><PieChart title="Customer Segments" /></Paper>
  </Grid>
</Grid>
```

---

# Summary: File Structure

```
src/
├── components/
│   ├── dashboard/
│   │   ├── UnifiedCrossPlatformDashboard.tsx      (NEW)
│   │   ├── GoogleAdsDashboard.tsx                 (NEW)
│   │   ├── MetaAdsDashboard.tsx                   (NEW)
│   │   ├── GoogleAnalyticsDashboard.tsx           (NEW)
│   │   ├── EcommerceDashboard.tsx                 (ENHANCE EXISTING)
│   │   ├── CampaignsDashboard.tsx                 (ENHANCE)
│   │   ├── KeywordsDashboard.tsx                  (ENHANCE)
│   │   ├── BudgetOptimizerDashboard.tsx           (ENHANCE)
│   │   ├── ForecastingDashboard.tsx               (ENHANCE)
│   │   └── AlertsDashboard.tsx                    (ENHANCE)
│   │
│   ├── common/
│   │   ├── DashboardTemplate.tsx                  (EXISTING)
│   │   ├── GlobalFilterBar.tsx                    (ENHANCE)
│   │   ├── KPICard.tsx                            (EXISTING)
│   │   ├── InsightCard.tsx                        (EXISTING)
│   │   └── AIInsightSection.tsx                   (NEW)
│   │
│   └── charts/
│       ├── ComparisonTable.tsx                    (NEW)
│       ├── PlatformBarChart.tsx                   (NEW)
│       ├── BudgetAllocationChart.tsx              (NEW)
│       └── FunnelChart.tsx                        (EXISTING)
│
├── services/
│   ├── analyticsService.ts                        (ENHANCE)
│   ├── googleAdsService.ts                        (NEW)
│   ├── metaAdsService.ts                          (NEW)
│   └── ga4Service.ts                              (NEW)
│
└── App.tsx                                         (UPDATE ROUTES)
```

---

# Implementation Priority

## Phase 1: Core Dashboards (Week 1-2)
1. ✅ Unified Cross-Platform Dashboard
2. ✅ Google Ads Dashboard
3. ✅ Meta Ads Dashboard

## Phase 2: Analytics & Insights (Week 3)
4. ✅ Google Analytics Dashboard
5. ✅ Enhance E-Commerce Dashboard
6. ✅ AI Insight components

## Phase 3: Specialized Dashboards (Week 4-5)
7. ✅ Budget Optimizer
8. ✅ Forecasting
9. ✅ Alerts & Anomalies

---

# Shared Components to Build

### 1. Enhanced GlobalFilterBar
```tsx
// Add platform filter, multi-select campaigns
<GlobalFilterBar
  filters={[
    { type: 'customer' },
    { type: 'dateRange' },
    { type: 'platform' },
    { type: 'campaignType' },
    { type: 'campaign', multiSelect: true }
  ]}
/>
```

### 2. AI Insight Section
```tsx
<AIInsightSection
  descriptive="What happened"
  diagnostic="Why it happened"
  prescriptive="What to do"
  actions={[...]}
/>
```

### 3. Platform Comparison Table
```tsx
<PlatformComparisonTable
  platforms={['Google Ads', 'Meta Ads', 'Organic']}
  metrics={['spend', 'roas', 'conversions', 'cpc', 'cvr']}
  highlightWinner={true}
/>
```

---

**Ready to start building?** 🚀

Let me know which dashboard you want to build first!
