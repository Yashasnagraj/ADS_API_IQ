# AI Features Implementation Guide
## Complete Build Instructions with Real Database Data

**Status**: Navigation Updated ✅ | Ready to Build Features

---

## 🎯 Overview

All 5 AI features will use **real data** from `marketing_warehouse.db`:
- 3 Customers (Emcee Sons, VANAVASI KALYANA, Communn.io)
- 19 Campaigns
- 84 Performance Records (campaigns_performance, keywords_performance)
- Keywords, Ad Groups, Search Terms

---

## ✅ COMPLETED: Navigation Structure

**File**: `marketingiq-platform/web/src/components/common/Layout.tsx`

**New AI Intelligence Section Added**:
```typescript
{
  title: 'AI Intelligence ⭐',
  items: [
    { text: 'AI Reports', path: '/ai/reports', icon: <DescriptionIcon />, badge: 'NEW' },
    { text: 'AI Copilot', path: '/ai/copilot', icon: <ChatIcon /> },
    { text: 'Creative Studio', path: '/ai/creative-studio', icon: <BrushIcon />, badge: 'NEW' },
    { text: 'Predictive Alerts', path: '/ai/predictive-alerts', icon: <PredictionsIcon />, badge: 'NEW' },
    { text: 'Campaign Builder', path: '/ai/campaign-builder', icon: <RocketLaunchIcon />, badge: 'NEW' },
  ],
}
```

---

## 🏗️ FEATURE 1: AI Reports Generator

### Route: `/ai/reports`

### Data Sources
```sql
-- Campaigns Performance
SELECT * FROM campaigns_performance
WHERE customer_id = <selected_customer>
AND date BETWEEN <start_date> AND <end_date>

-- Top Campaigns by ROAS
SELECT campaign_name, SUM(conversions_value) / SUM(cost_micros) * 1000000 as roas
FROM campaigns_performance
WHERE customer_id = <selected_customer>
GROUP BY campaign_id
ORDER BY roas DESC LIMIT 5

-- Budget Analysis
SELECT
  SUM(cost_micros) / 1000000 as total_spend,
  SUM(conversions_value) as total_revenue,
  SUM(conversions) as total_conversions
FROM campaigns_performance
WHERE customer_id = <selected_customer>
```

### Components to Build

**1. Report Type Selector** (`components/ai/reports/ReportTypeSelector.tsx`)
```typescript
const reportTypes = [
  {
    id: 'executive',
    title: 'Executive Summary',
    description: 'Quick 5-min overview',
    icon: <AssessmentIcon />,
  },
  {
    id: 'client',
    title: 'Client Report',
    description: 'Branded PDF for clients',
    icon: <PictureAsPdfIcon />,
  },
  {
    id: 'campaign',
    title: 'Campaign Postmortem',
    description: 'Deep dive analysis',
    icon: <AnalyticsIcon />,
  },
];
```

**2. Report Configurator** (`components/ai/reports/ReportConfigurator.tsx`)
```typescript
interface ReportConfig {
  reportName: string;
  customer_id: number;
  startDate: string;
  endDate: string;
  campaigns: 'all' | number[];
  includeSections: {
    executiveSummary: boolean;
    performanceTrends: boolean;
    aiInsights: boolean;
    topCampaigns: boolean;
    improvements: boolean;
    budgetAnalysis: boolean;
  };
  branding: {
    logo?: File;
    colorScheme: string;
  };
}
```

**3. Report Generator** (`components/ai/reports/ReportGenerator.tsx`)
```typescript
// Fetch real data
const generateReport = async (config: ReportConfig) => {
  const campaigns = await fetch(`/api/campaigns?customer_id=${config.customer_id}&start_date=${config.startDate}&end_date=${config.endDate}`);

  const reportData = {
    totalSpend: campaigns.reduce((sum, c) => sum + c.cost_micros / 1000000, 0),
    totalRevenue: campaigns.reduce((sum, c) => sum + c.conversions_value, 0),
    roas: totalRevenue / totalSpend,
    topCampaign: campaigns.sort((a, b) => b.conversions_value - a.conversions_value)[0],
    // ... more calculations
  };

  return generateMarkdown(reportData);
};
```

### API Endpoint Needed
```python
# api/app/routes/ai_reports.py

@router.post("/api/ai/reports/generate")
async def generate_report(config: ReportConfig, db: Session = Depends(get_db)):
    # Query campaigns_performance
    campaigns = db.query(CampaignPerformance).filter(
        CampaignPerformance.customer_id == config.customer_id,
        CampaignPerformance.date >= config.start_date,
        CampaignPerformance.date <= config.end_date
    ).all()

    # Calculate metrics
    total_spend = sum(c.cost_micros / 1000000 for c in campaigns)
    total_revenue = sum(c.conversions_value for c in campaigns)
    roas = total_revenue / total_spend if total_spend > 0 else 0

    # Generate AI narrative using Gemini
    prompt = f"""
    Generate an executive summary for this marketing performance:
    - Total Spend: ₹{total_spend:,.2f}
    - Total Revenue: ₹{total_revenue:,.2f}
    - ROAS: {roas:.2f}x
    - Top Campaign: {campaigns[0].campaign_name}
    """

    narrative = await generate_with_gemini(prompt)

    return {
        "narrative": narrative,
        "metrics": {...},
        "charts": {...}
    }
```

---

## 🏗️ FEATURE 2: Creative Studio (Ad Copy Generator)

### Route: `/ai/creative-studio`

### Data Sources
```sql
-- Get existing ads for a campaign
SELECT DISTINCT
  a.headline1, a.headline2, a.headline3,
  a.description1, a.description2,
  k.keyword_text,
  cp.ctr, cp.conversions
FROM ads a
JOIN ad_groups ag ON a.ad_group_id = ag.ad_group_id
JOIN keywords k ON ag.ad_group_id = k.ad_group_id
JOIN campaigns_performance cp ON ag.campaign_id = cp.campaign_id
WHERE cp.customer_id = <selected_customer>
ORDER BY cp.ctr DESC LIMIT 10
```

### Components to Build

**1. Ad Copy Generator** (`components/ai/creative/AdCopyGenerator.tsx`)
```typescript
interface AdCopyInput {
  campaignGoal: 'sales' | 'awareness' | 'leads' | 'event';
  product: string;
  targetAudience: string;
  tone: 'professional' | 'casual' | 'urgent' | 'friendly';
  keyBenefits: string[];
  specialOffer?: string;
}

const generateAdCopy = async (input: AdCopyInput) => {
  // Get top-performing keywords for context
  const topKeywords = await fetch(`/api/keywords/top?customer_id=${customerId}`);

  // Generate with Gemini
  const prompt = `
  Generate 5 Google Ads variations for:
  Product: ${input.product}
  Audience: ${input.targetAudience}
  Goal: ${input.campaignGoal}
  Tone: ${input.tone}
  Benefits: ${input.keyBenefits.join(', ')}

  Top-performing keywords in account: ${topKeywords.map(k => k.text).join(', ')}

  Format:
  Headline 1 (max 30 chars)
  Description (max 90 chars)
  Score (1-10 for predicted CTR)
  `;

  return await callGemini(prompt);
};
```

**2. Copy Optimizer** (`components/ai/creative/CopyOptimizer.tsx`)
```typescript
const optimizeAdCopy = async (existingAd: Ad) => {
  // Analyze existing ad
  const issues = [];
  if (existingAd.headline1.length > 30) issues.push('Headline too long');
  if (!hasEmotionalWords(existingAd.description1)) issues.push('Missing emotional triggers');
  if (!hasCTA(existingAd.description1)) issues.push('No clear CTA');

  // Generate optimized versions
  const prompt = `
  Optimize this ad:
  Current: "${existingAd.headline1}" - "${existingAd.description1}"
  Issues: ${issues.join(', ')}

  Generate 3 improved versions with scores.
  `;

  return await callGemini(prompt);
};
```

### API Endpoint
```python
# api/app/routes/ai_creative.py

@router.post("/api/ai/creative/generate")
async def generate_ad_copy(input: AdCopyInput, db: Session = Depends(get_db)):
    # Get top keywords for context
    top_keywords = db.query(Keyword).join(CampaignKeyword).filter(
        CampaignKeyword.customer_id == input.customer_id
    ).order_by(CampaignKeyword.ctr.desc()).limit(10).all()

    keyword_context = ", ".join([k.keyword_text for k in top_keywords])

    # Generate with Gemini
    prompt = f"""
    Generate 5 Google Ads variations:
    Product: {input.product}
    Audience: {input.target_audience}
    Goal: {input.campaign_goal}
    Tone: {input.tone}
    Top keywords: {keyword_context}

    Each ad should have:
    - Headline 1 (max 30 chars)
    - Headline 2 (max 30 chars)
    - Description (max 90 chars)
    - Predicted CTR score (1-10)
    """

    variations = await generate_with_gemini(prompt)

    return {"variations": variations}
```

---

## 🏗️ FEATURE 3: AI Copilot (Full-Page Chat)

### Route: `/ai/copilot`

### Data Sources
```sql
-- Context-aware queries
-- Example: "Why is my CPC increasing?"
SELECT
  date,
  AVG(cpc) as avg_cpc,
  AVG(quality_score) as avg_quality
FROM keywords_performance
WHERE customer_id = <selected_customer>
AND date >= DATE('now', '-30 days')
GROUP BY date
ORDER BY date
```

### Components to Build

**1. Chat Interface** (`components/ai/copilot/ChatInterface.tsx`)
```typescript
interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  actions?: Action[];
  chart?: ChartData;
}

const ChatInterface = () => {
  const [messages, setMessages] = useState<Message[]>([]);
  const { filters } = useFilters();

  const sendMessage = async (text: string) => {
    // Send with context
    const response = await fetch('/api/ai/chat', {
      method: 'POST',
      body: JSON.stringify({
        message: text,
        context: {
          customer_id: filters.customerId,
          date_range: filters.dateRange,
          current_page: window.location.pathname,
        }
      })
    });

    const data = await response.json();
    setMessages([...messages, {
      role: 'user',
      content: text
    }, {
      role: 'assistant',
      content: data.response,
      actions: data.actions,
      chart: data.chart
    }]);
  };

  return (
    <Box sx={{ display: 'flex', height: '100vh' }}>
      <ContextSidebar />
      <Box sx={{ flex: 1 }}>
        <ChatHistory messages={messages} />
        <ChatInput onSend={sendMessage} />
      </Box>
    </Box>
  );
};
```

**2. Context Sidebar** (`components/ai/copilot/ContextSidebar.tsx`)
```typescript
const ContextSidebar = () => {
  const { filters } = useFilters();

  const quickActions = [
    { label: 'Generate report', action: () => navigate('/ai/reports') },
    { label: 'Pause campaign', action: () => pauseCampaign() },
    { label: 'Adjust budgets', action: () => navigate('/dashboard/optimization/budget') },
  ];

  const suggestedQueries = [
    "Show me my worst performing keywords",
    "Create a campaign for holiday sales",
    "Why is my ROAS dropping?",
    "Which campaigns have the best LTV customers?",
  ];

  return (
    <Box sx={{ width: 280, borderRight: 1, borderColor: 'divider' }}>
      <Box sx={{ p: 2 }}>
        <Typography variant="h6">Active Filters</Typography>
        <Chip label={`Customer: ${filters.customerName}`} />
        <Chip label={`Date: ${filters.dateRange}`} />
      </Box>

      <Divider />

      <List subheader={<ListSubheader>Quick Actions</ListSubheader>}>
        {quickActions.map(action => (
          <ListItemButton onClick={action.action}>
            <ListItemText primary={action.label} />
          </ListItemButton>
        ))}
      </List>

      <Divider />

      <List subheader={<ListSubheader>Suggested Queries</ListSubheader>}>
        {suggestedQueries.map(query => (
          <ListItemButton onClick={() => handleQuery(query)}>
            <ListItemText primary={query} />
          </ListItemButton>
        ))}
      </List>
    </Box>
  );
};
```

### API Endpoint
```python
# api/app/routes/ai_copilot.py

@router.post("/api/ai/chat")
async def chat(request: ChatRequest, db: Session = Depends(get_db)):
    message = request.message
    customer_id = request.context.customer_id

    # Determine intent
    if "cpc" in message.lower() and "increasing" in message.lower():
        # Query data
        cpc_data = db.query(
            KeywordPerformance.date,
            func.avg(KeywordPerformance.cpc).label('avg_cpc')
        ).filter(
            KeywordPerformance.customer_id == customer_id
        ).group_by(KeywordPerformance.date).all()

        # Analyze
        cpc_trend = calculate_trend(cpc_data)

        # Generate response
        response = f"""
        Your CPC increased {cpc_trend.percent_change}% over the last {cpc_trend.days} days.

        Main reasons:
        1. Competitor bidding increased on {cpc_trend.competitive_keywords_count} keywords
        2. Quality Score dropped from {cpc_trend.prev_qs} to {cpc_trend.current_qs}
        3. {cpc_trend.new_keywords_count} new keywords added with higher CPCs

        Recommendation: Focus on improving Quality Score for your top 10 keywords.
        """

        return {
            "response": response,
            "chart": {
                "type": "line",
                "data": cpc_data
            },
            "actions": [
                {"label": "View Campaign Details", "path": "/dashboard/data/campaigns"},
                {"label": "Adjust Bids", "action": "adjust_bids"}
            ]
        }

    # Default: Use Gemini with data context
    prompt = f"""
    User question: {message}
    Customer: {customer_id}

    Available data context:
    - {len(campaigns)} active campaigns
    - Total spend: ₹{total_spend:,.2f}
    - Avg ROAS: {avg_roas:.2f}x

    Provide a helpful, data-driven answer.
    """

    return await generate_with_gemini(prompt)
```

---

## 🏗️ FEATURE 4: Predictive Alert System

### Route: `/ai/predictive-alerts`

### Data Sources
```sql
-- Budget burn rate
SELECT
  campaign_id,
  campaign_name,
  SUM(cost_micros) / 1000000 as daily_spend,
  budget_amount_micros / 1000000 as daily_budget
FROM campaigns_performance cp
JOIN campaigns c ON cp.campaign_id = c.campaign_id
WHERE cp.date = DATE('now')
AND cp.customer_id = <selected_customer>

-- Historical CTR patterns
SELECT
  strftime('%w', date) as day_of_week,
  AVG(ctr) as avg_ctr
FROM campaigns_performance
WHERE customer_id = <selected_customer>
GROUP BY day_of_week
```

### Components to Build

**1. Predictive Alert Card** (`components/ai/predictions/PredictiveAlertCard.tsx`)
```typescript
interface PredictiveAlert {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  title: string;
  campaign: string;
  forecast: string;
  impact: number; // Revenue at risk
  confidence: number; // 0-100
  recommendation: {
    action: string;
    details: string;
  };
  historicalAccuracy: number;
}

const PredictiveAlertCard = ({ alert }: { alert: PredictiveAlert }) => {
  return (
    <GradientCard variant={alert.severity === 'critical' ? 'error' : 'warning'}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 2 }}>
          <Typography variant="h6">
            {alert.severity === 'critical' ? '🔴' : '🟡'} {alert.title}
          </Typography>
          <ConfidenceScore score={alert.confidence} size="small" />
        </Box>

        <Typography variant="body2" sx={{ mb: 1 }}>
          <strong>Campaign:</strong> {alert.campaign}
        </Typography>

        <Typography variant="body2" sx={{ mb: 1 }}>
          <strong>Forecast:</strong> {alert.forecast}
        </Typography>

        <ImpactMeter
          value={alert.impact}
          label="Revenue at Risk"
          type="negative"
          size="small"
        />

        <Divider sx={{ my: 2 }} />

        <Typography variant="subtitle2" sx={{ mb: 1 }}>
          🤖 AI Recommendation:
        </Typography>
        <Typography variant="body2" sx={{ mb: 2 }}>
          {alert.recommendation.action}
        </Typography>

        <Box sx={{ display: 'flex', gap: 1 }}>
          <Button variant="contained" color="primary">
            Approve Auto-Action
          </Button>
          <Button variant="outlined">
            Modify & Approve
          </Button>
          <Button variant="text">
            Dismiss
          </Button>
        </Box>
      </CardContent>
    </GradientCard>
  );
};
```

**2. Prediction History** (`components/ai/predictions/PredictionHistory.tsx`)
```typescript
const PredictionHistory = () => {
  const [history, setHistory] = useState([]);

  useEffect(() => {
    fetch(`/api/ai/predictions/history?customer_id=${customerId}`)
      .then(res => res.json())
      .then(data => setHistory(data));
  }, []);

  return (
    <TableContainer>
      <Table>
        <TableHead>
          <TableRow>
            <TableCell>Date</TableCell>
            <TableCell>Prediction</TableCell>
            <TableCell>Confidence</TableCell>
            <TableCell>Actual Outcome</TableCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {history.map(item => (
            <TableRow key={item.id}>
              <TableCell>{item.date}</TableCell>
              <TableCell>{item.prediction}</TableCell>
              <TableCell>
                <ConfidenceScore score={item.confidence} variant="compact" />
              </TableCell>
              <TableCell>
                {item.correct ? '✅ Correct' : '❌ Did not occur'}
              </TableCell>
            </TableRow>
          ))}
        </TableBody>
      </Table>
    </TableContainer>
  );
};
```

### API Endpoint
```python
# api/app/routes/ai_predictions.py

@router.get("/api/ai/predictions")
async def get_predictions(customer_id: int, db: Session = Depends(get_db)):
    predictions = []

    # 1. Budget Depletion Prediction
    campaigns = db.query(Campaign).filter(Campaign.customer_id == customer_id).all()

    for campaign in campaigns:
        today_spend = db.query(func.sum(CampaignPerformance.cost_micros)).filter(
            CampaignPerformance.campaign_id == campaign.campaign_id,
            CampaignPerformance.date == date.today()
        ).scalar() or 0

        daily_budget = campaign.budget_amount_micros
        hours_left_in_day = 24 - datetime.now().hour
        projected_spend = today_spend * (24 / (24 - hours_left_in_day))

        if projected_spend > daily_budget * 0.9:
            hours_until_depletion = (daily_budget - today_spend) / (today_spend / (24 - hours_left_in_day))

            predictions.append({
                "id": f"budget_{campaign.campaign_id}",
                "severity": "critical",
                "title": "Budget Depletion Predicted",
                "campaign": campaign.campaign_name,
                "forecast": f"Will run out of budget in {hours_until_depletion:.1f} hours",
                "impact": calculate_lost_revenue(campaign, hours_until_depletion),
                "confidence": 94,
                "recommendation": {
                    "action": f"Increase daily budget from ₹{daily_budget/1000000:,.0f} to ₹{projected_spend/1000000:,.0f}",
                    "details": "Based on current pacing and conversion rate"
                },
                "historical_accuracy": 87
            })

    # 2. CTR Drop Prediction (day-of-week patterns)
    tomorrow_dow = (datetime.now().weekday() + 1) % 7
    historical_ctr = db.query(func.avg(CampaignPerformance.ctr)).filter(
        CampaignPerformance.customer_id == customer_id,
        extract('dow', CampaignPerformance.date) == tomorrow_dow
    ).scalar()

    current_avg_ctr = db.query(func.avg(CampaignPerformance.ctr)).filter(
        CampaignPerformance.customer_id == customer_id,
        CampaignPerformance.date >= date.today() - timedelta(days=7)
    ).scalar()

    if historical_ctr < current_avg_ctr * 0.85:
        predictions.append({
            "severity": "warning",
            "title": "CTR Drop Predicted",
            "forecast": f"CTR likely to drop {((1 - historical_ctr/current_avg_ctr) * 100):.0f}% tomorrow",
            # ... more details
        })

    return {"predictions": predictions}
```

---

## 🏗️ FEATURE 5: AI Campaign Builder

### Route: `/ai/campaign-builder`

### Data Sources
```sql
-- Get keyword ideas from existing campaigns
SELECT DISTINCT keyword_text, AVG(ctr) as avg_ctr, AVG(quality_score) as avg_qs
FROM keywords k
JOIN keywords_performance kp ON k.keyword_id = kp.keyword_id
WHERE k.customer_id = <selected_customer>
AND kp.impressions > 100
GROUP BY keyword_text
ORDER BY avg_ctr DESC
LIMIT 100

-- Get top-performing ad copy
SELECT headline1, description1, AVG(ctr) as avg_ctr
FROM ads a
JOIN ad_performance ap ON a.ad_id = ap.ad_id
WHERE a.customer_id = <selected_customer>
GROUP BY headline1, description1
ORDER BY avg_ctr DESC
LIMIT 20
```

### Components to Build

**1. Campaign Wizard** (`components/ai/campaign-builder/CampaignWizard.tsx`)
```typescript
const steps = [
  'Campaign Goal',
  'Product Details',
  'AI Generation',
  'Review & Edit',
  'Launch Options'
];

const CampaignWizard = () => {
  const [activeStep, setActiveStep] = useState(0);
  const [config, setConfig] = useState<CampaignConfig>({});

  const handleNext = async () => {
    if (activeStep === 2) {
      // Generate campaign structure
      const structure = await generateCampaignStructure(config);
      setConfig({ ...config, structure });
    }
    setActiveStep(activeStep + 1);
  };

  return (
    <Box>
      <Stepper activeStep={activeStep}>
        {steps.map(label => (
          <Step key={label}>
            <StepLabel>{label}</StepLabel>
          </Step>
        ))}
      </Stepper>

      {activeStep === 0 && <CampaignGoalStep />}
      {activeStep === 1 && <ProductDetailsStep />}
      {activeStep === 2 && <AIGenerationStep />}
      {activeStep === 3 && <ReviewEditStep structure={config.structure} />}
      {activeStep === 4 && <LaunchOptionsStep />}

      <Box sx={{ display: 'flex', justifyContent: 'space-between', mt: 3 }}>
        <Button disabled={activeStep === 0} onClick={() => setActiveStep(activeStep - 1)}>
          Back
        </Button>
        <Button variant="contained" onClick={handleNext}>
          {activeStep === steps.length - 1 ? 'Launch Campaign' : 'Continue'}
        </Button>
      </Box>
    </Box>
  );
};
```

**2. Campaign Structure Tree** (`components/ai/campaign-builder/CampaignStructureTree.tsx`)
```typescript
interface CampaignStructure {
  campaignName: string;
  budget: number;
  adGroups: AdGroup[];
  negativeKeywords: string[];
  biddingStrategy: string;
}

interface AdGroup {
  name: string;
  budget: number;
  keywords: Keyword[];
  ads: Ad[];
}

const CampaignStructureTree = ({ structure, onEdit }: Props) => {
  return (
    <Card>
      <CardContent>
        <Typography variant="h6">
          📊 CAMPAIGN STRUCTURE (AI-Generated)
        </Typography>

        <Box sx={{ mt: 2 }}>
          <Typography variant="body1" fontWeight={600}>
            {structure.campaignName}
          </Typography>

          {structure.adGroups.map((adGroup, index) => (
            <Accordion key={index}>
              <AccordionSummary expandIcon={<ExpandMoreIcon />}>
                <Typography>
                  Ad Group {index + 1}: {adGroup.name} (Budget: ₹{adGroup.budget:,.0f})
                </Typography>
              </AccordionSummary>
              <AccordionDetails>
                <Typography variant="subtitle2">Keywords ({adGroup.keywords.length}):</Typography>
                <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1, mb: 2 }}>
                  {adGroup.keywords.map((kw, i) => (
                    <Chip
                      key={i}
                      label={`${kw.text} [${kw.matchType}] - CPC ₹${kw.estimatedCpc}`}
                      size="small"
                      onDelete={() => onEdit('removeKeyword', { adGroupIndex: index, keywordIndex: i })}
                    />
                  ))}
                </Box>

                <Typography variant="subtitle2">Ads ({adGroup.ads.length} variations):</Typography>
                {adGroup.ads.map((ad, i) => (
                  <Card key={i} variant="outlined" sx={{ p: 1, mb: 1 }}>
                    <Typography variant="body2" fontWeight={600}>{ad.headline1}</Typography>
                    <Typography variant="caption">{ad.description1}</Typography>
                  </Card>
                ))}
              </AccordionDetails>
            </Accordion>
          ))}

          <Divider sx={{ my: 2 }} />

          <Typography variant="subtitle2">Negative Keywords:</Typography>
          <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 1 }}>
            {structure.negativeKeywords.map((kw, i) => (
              <Chip key={i} label={kw} size="small" color="error" />
            ))}
          </Box>

          <Typography variant="subtitle2" sx={{ mt: 2 }}>
            Bid Strategy: {structure.biddingStrategy}
          </Typography>
        </Box>
      </CardContent>
    </Card>
  );
};
```

**3. Performance Projection** (`components/ai/campaign-builder/PerformanceProjection.tsx`)
```typescript
const PerformanceProjection = ({ structure }: Props) => {
  const [projection, setProjection] = useState(null);

  useEffect(() => {
    // Calculate projections based on historical data
    const calculateProjection = async () => {
      // Fetch historical performance for similar keywords
      const historicalData = await fetch(`/api/ai/campaign-builder/project`, {
        method: 'POST',
        body: JSON.stringify({ structure })
      });

      setProjection(await historicalData.json());
    };

    calculateProjection();
  }, [structure]);

  if (!projection) return <AILoadingState message="Calculating projections..." />;

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">✨ AI INSIGHTS</Typography>

        <Grid container spacing={2} sx={{ mt: 1 }}>
          <Grid item xs={6} md={3}>
            <ImpactMeter
              value={projection.estimatedImpressions}
              label="Estimated Impressions"
              type="neutral"
              format="number"
            />
          </Grid>
          <Grid item xs={6} md={3}>
            <ImpactMeter
              value={projection.projectedCpc}
              label="Projected CPC"
              type="neutral"
              format="currency"
            />
          </Grid>
          <Grid item xs={6} md={3}>
            <ImpactMeter
              value={projection.expectedConversions}
              label="Expected Conversions"
              type="positive"
              format="number"
            />
          </Grid>
          <Grid item xs={6} md={3}>
            <ImpactMeter
              value={projection.predictedRoas}
              label="Predicted ROAS"
              type="positive"
              format="number"
            />
          </Grid>
        </Grid>
      </CardContent>
    </Card>
  );
};
```

### API Endpoint
```python
# api/app/routes/ai_campaign_builder.py

@router.post("/api/ai/campaign-builder/generate")
async def generate_campaign_structure(config: CampaignConfig, db: Session = Depends(get_db)):
    # Get keyword ideas from historical data
    similar_keywords = db.query(
        Keyword.keyword_text,
        func.avg(KeywordPerformance.ctr).label('avg_ctr'),
        func.avg(KeywordPerformance.cpc).label('avg_cpc'),
        func.avg(Keyword.quality_score).label('avg_qs')
    ).join(KeywordPerformance).filter(
        Keyword.customer_id == config.customer_id
    ).group_by(Keyword.keyword_text).order_by(desc('avg_ctr')).limit(100).all()

    # Get top ad copy patterns
    top_ads = db.query(
        Ad.headline1, Ad.description1,
        func.avg(AdPerformance.ctr).label('avg_ctr')
    ).join(AdPerformance).filter(
        Ad.customer_id == config.customer_id
    ).group_by(Ad.headline1, Ad.description1).order_by(desc('avg_ctr')).limit(20).all()

    # Use Gemini to generate campaign structure
    prompt = f"""
    Generate a Google Ads campaign structure:

    Product: {config.product}
    Budget: ₹{config.budget}
    Target Audience: {config.target_audience}

    Historical context:
    - Top performing keywords: {[k.keyword_text for k in similar_keywords[:10]]}
    - Best ad headlines: {[a.headline1 for a in top_ads[:5]]}

    Create:
    - 3 ad groups with themes
    - 20-30 keywords per ad group with match types
    - 3 ad variations per ad group
    - Negative keyword list
    - Budget allocation
    """

    structure = await generate_with_gemini(prompt)

    return {"structure": structure}

@router.post("/api/ai/campaign-builder/project")
async def project_performance(structure: CampaignStructure, db: Session = Depends(get_db)):
    # Calculate projections based on historical data
    all_keywords = [kw for ag in structure.ad_groups for kw in ag.keywords]

    # Get historical performance for similar keywords
    historical_perf = db.query(
        func.avg(KeywordPerformance.impressions).label('avg_impressions'),
        func.avg(KeywordPerformance.cpc).label('avg_cpc'),
        func.avg(KeywordPerformance.conversions).label('avg_conversions')
    ).filter(
        KeywordPerformance.keyword_text.in_([kw.text for kw in all_keywords])
    ).first()

    estimated_impressions = historical_perf.avg_impressions * len(all_keywords)
    projected_cpc = historical_perf.avg_cpc
    expected_conversions = historical_perf.avg_conversions * len(all_keywords)
    predicted_roas = (expected_conversions * avg_conversion_value) / (estimated_impressions * projected_cpc)

    return {
        "estimated_impressions": int(estimated_impressions),
        "projected_cpc": round(projected_cpc, 2),
        "expected_conversions": f"{int(expected_conversions)}-{int(expected_conversions * 1.3)}",
        "predicted_roas": f"{predicted_roas:.1f}-{predicted_roas * 1.2:.1f}x"
    }
```

---

## 📋 Implementation Checklist

### Phase 1: Routes & Basic Structure ✅
- [x] Update navigation in Layout.tsx
- [ ] Add routes to App.tsx
- [ ] Create base page components for each feature

### Phase 2: API Endpoints
- [ ] Create `/api/ai/reports/generate`
- [ ] Create `/api/ai/creative/generate`
- [ ] Create `/api/ai/chat`
- [ ] Create `/api/ai/predictions`
- [ ] Create `/api/ai/campaign-builder/generate`

### Phase 3: UI Components
- [ ] AI Reports: ReportTypeSelector, ReportConfigurator, ReportPreview
- [ ] Creative Studio: AdCopyGenerator, CopyOptimizer, CopyScoreCard
- [ ] AI Copilot: ChatInterface, ContextSidebar, ChatMessage
- [ ] Predictive Alerts: PredictiveAlertCard, PredictionHistory
- [ ] Campaign Builder: CampaignWizard, CampaignStructureTree, PerformanceProjection

### Phase 4: Data Integration
- [ ] Connect all features to marketing_warehouse.db
- [ ] Implement Gemini AI integration for text generation
- [ ] Add error handling & loading states
- [ ] Implement toast notifications for user actions

### Phase 5: Testing & Polish
- [ ] Test with real customer data (Emcee Sons)
- [ ] Verify all calculations are accurate
- [ ] Add skeleton loaders
- [ ] Implement empty states
- [ ] Mobile responsiveness testing

---

## 🚀 Quick Start Implementation

### Step 1: Install Dependencies
```bash
cd marketingiq-platform/web
npm install notistack
```

### Step 2: Add Routes to App.tsx
```typescript
// Add imports
import AIReportsPage from './components/dashboards/ai/AIReportsPage';
import CreativeStudioPage from './components/dashboards/ai/CreativeStudioPage';
import AICopilotPage from './components/dashboards/ai/AICopilotPage';
import PredictiveAlertsPage from './components/dashboards/ai/PredictiveAlertsPage';
import CampaignBuilderPage from './components/dashboards/ai/CampaignBuilderPage';

// Add routes
<Route path="ai/*" element={
  <Layout>
    <Routes>
      <Route path="reports" element={<AIReportsPage />} />
      <Route path="creative-studio" element={<CreativeStudioPage />} />
      <Route path="copilot" element={<AICopilotPage />} />
      <Route path="predictive-alerts" element={<PredictiveAlertsPage />} />
      <Route path="campaign-builder" element={<CampaignBuilderPage />} />
    </Routes>
  </Layout>
} />
```

### Step 3: Create Backend Routes
```python
# api/app/main.py

from app.routes import ai_reports, ai_creative, ai_copilot, ai_predictions, ai_campaign_builder

app.include_router(ai_reports.router, prefix="/api/ai", tags=["AI Features"])
app.include_router(ai_creative.router, prefix="/api/ai", tags=["AI Features"])
app.include_router(ai_copilot.router, prefix="/api/ai", tags=["AI Features"])
app.include_router(ai_predictions.router, prefix="/api/ai", tags=["AI Features"])
app.include_router(ai_campaign_builder.router, prefix="/api/ai", tags=["AI Features"])
```

---

## 📊 Database Schema Reference

```sql
-- Customers
customers (customer_id, customer_name, descriptive_name)

-- Campaigns
campaigns (campaign_id, customer_id, campaign_name, status, budget_amount_micros)
campaigns_performance (campaign_id, customer_id, date, impressions, clicks, cost_micros, conversions, conversions_value, ctr)

-- Keywords
keywords (keyword_id, campaign_id, customer_id, keyword_text, match_type, quality_score)
keywords_performance (keyword_id, date, impressions, clicks, cpc, ctr, conversions)

-- Ad Groups
ad_groups (ad_group_id, campaign_id, customer_id, ad_group_name)

-- ML Features
ml_features (customer_id, campaign_id, feature_name, feature_value, date)
```

---

## 🎯 Success Metrics

Each feature should track:
- **Usage**: % of users who use the feature weekly
- **Time Saved**: Avg hours saved per use
- **Accuracy**: AI prediction/recommendation accuracy
- **Adoption**: Week-over-week growth in usage
- **Value**: Revenue impact (for predictions/optimizations)

---

**Status**: Implementation Guide Complete 📚
**Next**: Build features one by one following this guide

