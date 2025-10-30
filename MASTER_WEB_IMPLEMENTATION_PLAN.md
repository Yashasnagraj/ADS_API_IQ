# 🚀 Master Web Implementation Plan - MarketingIQ Platform

**Complete plan for Landing Page + All Dashboards**

**Use this document as the single source of truth when Meta Ads data is ready.**

---

## 📋 Table of Contents

1. [Landing Page - Scroll Story Experience](#landing-page)
2. [Unified Cross-Platform Dashboard](#unified-dashboard)
3. [Google Ads Dashboard](#google-ads-dashboard)
4. [Meta Ads Dashboard](#meta-ads-dashboard)
5. [Google Analytics Dashboard](#ga4-dashboard)
6. [E-Commerce Dashboard](#ecommerce-dashboard)
7. [Specialized Dashboards](#specialized-dashboards)
8. [Technical Implementation](#technical-implementation)

---

# 🎬 Landing Page - Scroll Story Experience

**Route:** `/` or `/landing`
**Experience:** Single flowing story with smooth scroll-reveal animations

## User Requirement:
> "I want the landing page to feel like a single, flowing story — when the user scrolls down, each section should reveal or fold in smoothly instead of just appearing instantly. Think of how modern SaaS or portfolio sites reveal content section by section with fade, slide, or scale animations tied to scroll."

---

## Design Philosophy

### Light Theme
- **Primary Background:** #FFFFFF (Pure White)
- **Secondary Background:** #F8F9FA (Light Gray)
- **Accent Color:** #1E88E5 (Soft Blue)
- **Text:** #2C3E50 (Dark Gray)
- **Minimal colors and icons**
- **Clean, professional aesthetic**

### Scroll Animation Principles
- **Smooth reveal on scroll** - No instant appearance
- **Tied to scroll position** - Animations trigger at specific scroll thresholds
- **Staggered animations** - Elements within sections animate sequentially
- **Subtle and professional** - Not distracting or "too much"
- **Performance optimized** - Smooth 60fps animations

---

## Landing Page Structure

### Section 1: Hero (Full Viewport)

**Animation:** Fade in on page load (no scroll needed)

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  [Background: Blurred analytics dashboard screenshot]       │
│  [Subtle parallax effect on scroll]                         │
│                                                              │
│         Marketing Intelligence Platform                     │
│         ─────────────────────────────────                   │
│    ↑ Fade in + Slide up from bottom (0.8s delay)           │
│                                                              │
│    One Dashboard. Three Platforms. Infinite Insights.       │
│    ↑ Fade in + Slide up (1.2s delay)                       │
│                                                              │
│    Real-time analytics across Google Ads, Meta Ads,         │
│    and Google Analytics — powered by AI.                     │
│    ↑ Fade in (1.6s delay)                                   │
│                                                              │
│    [Get Started]  [View Demo]                               │
│    ↑ Fade in + Scale from 0.9 to 1.0 (2.0s delay)          │
│                                                              │
│                                  [💬 AI Assistant]          │
│                                  ↑ Float in from right      │
└──────────────────────────────────────────────────────────────┘
```

**Scroll Behavior:**
- Background photo has **subtle parallax** (moves slower than scroll)
- When user scrolls down 10%, hero content fades out slightly (60% opacity)

**Technical:**
```tsx
<motion.section
  initial={{ opacity: 0 }}
  animate={{ opacity: 1 }}
  transition={{ duration: 0.6 }}
  style={{
    backgroundImage: 'url(...)',
    backgroundAttachment: 'fixed', // Parallax effect
  }}
>
  <motion.h1
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 0.8, duration: 0.6 }}
  >
    Marketing Intelligence Platform
  </motion.h1>

  <motion.p
    initial={{ opacity: 0, y: 30 }}
    animate={{ opacity: 1, y: 0 }}
    transition={{ delay: 1.2, duration: 0.6 }}
  >
    One Dashboard. Three Platforms. Infinite Insights.
  </motion.p>

  <motion.div
    initial={{ opacity: 0, scale: 0.9 }}
    animate={{ opacity: 1, scale: 1 }}
    transition={{ delay: 2.0, duration: 0.5 }}
  >
    <Button>Get Started</Button>
    <Button>View Demo</Button>
  </motion.div>
</motion.section>
```

---

### Section 2: Platform Integration

**Animation:** Fade in + Slide up when 20% of section is in viewport

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│              Unified Cross-Platform Analytics                │
│              ↑ Fade in + Slide up                           │
│                                                              │
│  ┌────────────┐    ┌────────────┐    ┌────────────┐        │
│  │            │    │            │    │            │        │
│  │ Google Ads │ ←──│  Unified   │──→ │  Meta Ads  │        │
│  │            │    │ Dashboard  │    │            │        │
│  └────────────┘    └────────────┘    └────────────┘        │
│  ↑ Stagger: 0.2s   ↑ Stagger: 0.4s  ↑ Stagger: 0.6s       │
│                           │                                 │
│                           ↓                                 │
│                    ┌────────────┐                           │
│                    │  Google    │                           │
│                    │ Analytics  │                           │
│                    └────────────┘                           │
│                    ↑ Stagger: 0.8s                          │
│                                                              │
│        All your marketing data in one place.                │
│        ↑ Fade in (1.0s after diagram starts)                │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Scroll Trigger:** When section reaches 20% viewport
**Animation Type:** Fade + Slide up (translateY: 30px → 0px)
**Stagger:** Each box appears 0.2s after the previous

**Technical:**
```tsx
<motion.section
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.2 }}
  transition={{ duration: 0.6 }}
>
  <motion.h2
    initial={{ opacity: 0, y: 20 }}
    whileInView={{ opacity: 1, y: 0 }}
    viewport={{ once: true }}
    transition={{ delay: 0.2, duration: 0.5 }}
  >
    Unified Cross-Platform Analytics
  </motion.h2>

  <motion.div className="platform-boxes">
    {['Google Ads', 'Unified Dashboard', 'Meta Ads', 'Google Analytics'].map((platform, i) => (
      <motion.div
        key={platform}
        initial={{ opacity: 0, scale: 0.8 }}
        whileInView={{ opacity: 1, scale: 1 }}
        viewport={{ once: true }}
        transition={{ delay: i * 0.2, duration: 0.5 }}
      >
        {platform}
      </motion.div>
    ))}
  </motion.div>
</motion.section>
```

---

### Section 3: Real-Time Metrics Overview

**Animation:** Cards scale in from 0.9 to 1.0 with stagger

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                  Today's Performance                         │
│                  ↑ Fade in                                   │
│                                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ Total Spend  │ │ Total ROAS   │ │ Conversions  │        │
│  │              │ │              │ │              │        │
│  │   $2,450     │ │    4.2x      │ │     156      │        │
│  │   ↑ 12%     │ │    ↑ 8%     │ │    ↑ 24%    │        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│  ↑ Scale 0.9→1   ↑ Scale 0.9→1   ↑ Scale 0.9→1            │
│    Delay 0.2s      Delay 0.4s      Delay 0.6s              │
│                                                              │
│  ┌──────────────┐ ┌──────────────┐ ┌──────────────┐        │
│  │ Google Ads   │ │  Meta Ads    │ │   Organic    │        │
│  │ ROAS: 5.1x   │ │ ROAS: 3.8x   │ │ Traffic: 2.4k│        │
│  └──────────────┘ └──────────────┘ └──────────────┘        │
│  ↑ Delay 0.8s    ↑ Delay 1.0s    ↑ Delay 1.2s              │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Scroll Trigger:** When section is 30% in viewport
**Animation:** Scale from 0.9 to 1.0 + Fade in
**Stagger:** 0.2s between each card

**Technical:**
```tsx
<motion.section
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, amount: 0.3 }}
  variants={{
    visible: {
      transition: {
        staggerChildren: 0.2
      }
    }
  }}
>
  <motion.h2
    variants={{
      hidden: { opacity: 0, y: 20 },
      visible: { opacity: 1, y: 0 }
    }}
  >
    Today's Performance
  </motion.h2>

  <motion.div className="metrics-grid">
    {metrics.map((metric, i) => (
      <motion.div
        key={i}
        variants={{
          hidden: { opacity: 0, scale: 0.9 },
          visible: { opacity: 1, scale: 1 }
        }}
      >
        <MetricCard {...metric} />
      </motion.div>
    ))}
  </motion.div>
</motion.section>
```

---

### Section 4: AI Insights

**Animation:** Slide in from left (descriptive), center (diagnostic), right (prescriptive)

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                    AI-Powered Insights                       │
│                    ↑ Fade in                                 │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 💡 Prescriptive Analysis                               │ │
│  │ ← Slide in from LEFT                                   │ │
│  │ "Shift 15% of budget from Meta to Google Ads           │ │
│  │  for 23% higher ROI this week."                        │ │
│  │                                                         │ │
│  │ [Apply Recommendation]                                 │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 🔍 Diagnostic Analysis                                 │ │
│  │ ↑ Slide in from BOTTOM                                 │ │
│  │ "Meta Ads CTR dropped 18% because..."                  │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 📊 Descriptive Analysis                                │ │
│  │ → Slide in from RIGHT                                  │ │
│  │ "Google Ads generated 64% of conversions..."           │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Scroll Trigger:** When section is 25% in viewport
**Animation:** Each card slides from different direction
**Stagger:** 0.3s between cards

**Technical:**
```tsx
const insightVariants = {
  hiddenLeft: { opacity: 0, x: -100 },
  hiddenCenter: { opacity: 0, y: 50 },
  hiddenRight: { opacity: 0, x: 100 },
  visible: { opacity: 1, x: 0, y: 0 }
};

<motion.section
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, amount: 0.25 }}
>
  <motion.div
    variants={insightVariants}
    initial="hiddenLeft"
    whileInView="visible"
    transition={{ delay: 0.2, duration: 0.6 }}
  >
    <InsightCard type="prescriptive" />
  </motion.div>

  <motion.div
    variants={insightVariants}
    initial="hiddenCenter"
    whileInView="visible"
    transition={{ delay: 0.5, duration: 0.6 }}
  >
    <InsightCard type="diagnostic" />
  </motion.div>

  <motion.div
    variants={insightVariants}
    initial="hiddenRight"
    whileInView="visible"
    transition={{ delay: 0.8, duration: 0.6 }}
  >
    <InsightCard type="descriptive" />
  </motion.div>
</motion.section>
```

---

### Section 5: Platform Comparison

**Animation:** Table rows appear one by one from top to bottom

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│            Where to Invest Your Marketing Budget?           │
│            ↑ Fade in + Slide up                             │
│                                                              │
│  Platform Performance (Last 30 Days)                        │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ Header Row                                             │ │
│  │ ↑ Fade in (0.2s)                                       │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ Google Ads Row                                         │ │
│  │ ↑ Slide in from left (0.4s)                            │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ Meta Ads Row                                           │ │
│  │ ↑ Slide in from left (0.6s)                            │ │
│  ├────────────────────────────────────────────────────────┤ │
│  │ Organic Row                                            │ │
│  │ ↑ Slide in from left (0.8s)                            │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  💡 AI Recommendation:                                      │
│  "Google Ads shows 33% better ROI..."                       │
│  ↑ Fade in + Pulse (1.2s delay)                             │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Technical:**
```tsx
<motion.section
  initial={{ opacity: 0, y: 30 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true, amount: 0.2 }}
>
  <Table>
    <TableHead>
      <motion.tr
        initial={{ opacity: 0 }}
        whileInView={{ opacity: 1 }}
        transition={{ delay: 0.2 }}
      >
        <TableCell>Metric</TableCell>
        <TableCell>Google Ads</TableCell>
        <TableCell>Meta Ads</TableCell>
        <TableCell>Organic</TableCell>
      </motion.tr>
    </TableHead>
    <TableBody>
      {rows.map((row, i) => (
        <motion.tr
          key={i}
          initial={{ opacity: 0, x: -50 }}
          whileInView={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.4 + (i * 0.2) }}
        >
          {row}
        </motion.tr>
      ))}
    </TableBody>
  </Table>

  <motion.div
    initial={{ opacity: 0, scale: 0.95 }}
    whileInView={{ opacity: 1, scale: 1 }}
    transition={{ delay: 1.2, duration: 0.5 }}
    animate={{ scale: [1, 1.02, 1] }}
    transition={{ repeat: Infinity, duration: 2 }}
  >
    💡 AI Recommendation: "Google Ads shows 33% better ROI..."
  </motion.div>
</motion.section>
```

---

### Section 6: Features Grid

**Animation:** Cards fade in and scale from bottom in a grid pattern

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│                   Platform Capabilities                      │
│                   ↑ Fade in                                  │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │  Real-Time   │  │ AI Insights  │  │ Multi-Agent  │      │
│  │  Monitoring  │  │   Powered    │  │   System     │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ↑ Delay 0.2s     ↑ Delay 0.4s     ↑ Delay 0.6s            │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Forecasting  │  │ Anomaly      │  │ Budget       │      │
│  │              │  │ Detection    │  │ Optimizer    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
│  ↑ Delay 0.8s     ↑ Delay 1.0s     ↑ Delay 1.2s            │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Technical:**
```tsx
<motion.section
  initial="hidden"
  whileInView="visible"
  viewport={{ once: true, amount: 0.2 }}
  variants={{
    visible: {
      transition: {
        staggerChildren: 0.2
      }
    }
  }}
>
  <motion.h2
    variants={{
      hidden: { opacity: 0, y: 20 },
      visible: { opacity: 1, y: 0 }
    }}
  >
    Platform Capabilities
  </motion.h2>

  <motion.div className="features-grid">
    {features.map((feature, i) => (
      <motion.div
        key={i}
        variants={{
          hidden: { opacity: 0, y: 30, scale: 0.95 },
          visible: { opacity: 1, y: 0, scale: 1 }
        }}
        whileHover={{ scale: 1.05, transition: { duration: 0.2 } }}
      >
        <FeatureCard {...feature} />
      </motion.div>
    ))}
  </motion.div>
</motion.section>
```

---

### Section 7: CTA Footer

**Animation:** Fade in + Scale with final "Get Started" button pulse

```
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│    Ready to optimize your marketing?                         │
│    ↑ Fade in + Slide up                                     │
│                                                              │
│    [Get Started Now]                                         │
│    ↑ Scale + Continuous pulse animation                     │
│                                                              │
└──────────────────────────────────────────────────────────────┘
```

**Technical:**
```tsx
<motion.section
  initial={{ opacity: 0, y: 50 }}
  whileInView={{ opacity: 1, y: 0 }}
  viewport={{ once: true }}
  transition={{ duration: 0.6 }}
>
  <motion.h2
    initial={{ opacity: 0 }}
    whileInView={{ opacity: 1 }}
    transition={{ delay: 0.3 }}
  >
    Ready to optimize your marketing?
  </motion.h2>

  <motion.div
    initial={{ opacity: 0, scale: 0.8 }}
    whileInView={{ opacity: 1, scale: 1 }}
    transition={{ delay: 0.6, duration: 0.5 }}
  >
    <motion.button
      animate={{
        scale: [1, 1.05, 1],
      }}
      transition={{
        repeat: Infinity,
        duration: 2,
        ease: "easeInOut"
      }}
      whileHover={{ scale: 1.1 }}
      whileTap={{ scale: 0.95 }}
    >
      Get Started Now
    </motion.button>
  </motion.div>
</motion.section>
```

---

## Floating Chatbot

**Animation:** Slide in from bottom-right after 2 seconds on page

```tsx
<motion.div
  className="floating-chatbot"
  initial={{ opacity: 0, x: 100, y: 100 }}
  animate={{ opacity: 1, x: 0, y: 0 }}
  transition={{ delay: 2, duration: 0.6, type: "spring" }}
  style={{
    position: 'fixed',
    bottom: 24,
    right: 24,
    zIndex: 1000
  }}
>
  <motion.button
    animate={{
      y: [0, -10, 0]
    }}
    transition={{
      repeat: Infinity,
      duration: 2,
      ease: "easeInOut"
    }}
  >
    💬 AI Assistant
  </motion.button>
</motion.div>
```

---

## Landing Page Technical Stack

### Libraries to Use:
```json
{
  "framer-motion": "^10.x",  // For scroll animations
  "react-intersection-observer": "^9.x",  // Scroll detection
  "react-scroll": "^1.x"  // Smooth scrolling
}
```

### Component Structure:
```
src/components/landing/
├── PremiumLandingPage.tsx          (Main component)
├── sections/
│   ├── HeroSection.tsx             (Section 1)
│   ├── PlatformIntegrationSection.tsx  (Section 2)
│   ├── MetricsPreviewSection.tsx   (Section 3)
│   ├── AIInsightsSection.tsx       (Section 4)
│   ├── ComparisonSection.tsx       (Section 5)
│   ├── FeaturesSection.tsx         (Section 6)
│   └── CTASection.tsx              (Section 7)
├── FloatingChatbot.tsx             (Floating button)
└── animations/
    ├── variants.ts                 (Animation variants)
    └── scrollConfig.ts             (Scroll thresholds)
```

---

# 📊 Dashboards Implementation

## Standard Dashboard Structure

**Every dashboard follows this exact pattern:**

```tsx
<DashboardTemplate title="..." subtitle="...">
  {/* 1. HEADER - Built into DashboardTemplate */}

  {/* 2. FILTERS */}
  <GlobalFilterBar
    onFilterChange={setFilters}
    initialFilters={filters}
  />

  {/* 3. KPIs (6 cards) */}
  <Grid container spacing={3} sx={{ mt: 2 }}>
    {kpis.map(kpi => (
      <Grid item xs={12} md={4}>
        <KPICard {...kpi} />
      </Grid>
    ))}
  </Grid>

  {/* 4. AI INSIGHTS (3 cards) */}
  <Stack spacing={2} sx={{ mt: 3 }}>
    <InsightCard type="descriptive" {...descriptive} />
    <InsightCard type="diagnostic" {...diagnostic} />
    <InsightCard type="prescriptive" {...prescriptive} />
  </Stack>

  {/* 5. VISUALIZATIONS (4-6 charts) */}
  <Grid container spacing={3} sx={{ mt: 2 }}>
    {/* Only meaningful charts */}
  </Grid>
</DashboardTemplate>
```

---

# 1. Unified Cross-Platform Dashboard

**Route:** `/dashboard/unified`

## Header
```tsx
title: "Unified Cross-Platform Analytics"
subtitle: "Compare Google Ads, Meta Ads, and Google Analytics performance side-by-side. AI-powered insights to optimize your marketing budget allocation."
```

## Filters
```tsx
- Customer selector
- Date range (Last 7d, 30d, 90d, Custom)
- Platform filter (ALL, Google Ads, Meta Ads, Organic)
```

## KPIs (6 cards)
```
Row 1:
- Total Marketing Spend: $12,450 (+12%)
- Blended ROAS: 4.2x (+8%) [HIGHLIGHTED]
- Total Conversions: 1,240 (+24%)

Row 2:
- Best Platform (ROAS): Google Ads - 5.2x ROAS
- Best Platform (Conversions): Google Ads - 64% of total
- Cost Efficiency Leader: Organic - $0 CPC
```

## AI Insights
```tsx
Descriptive: "Google Ads generated 64% of conversions with only 48% of total spend, achieving 5.2x ROAS. Meta Ads contributed 28% of conversions at 3.9x ROAS."

Diagnostic: "Google Ads outperforms because of high-intent search keywords. Meta Ads CTR dropped 18% in last week due to audience fatigue in 25-34 age group."

Prescriptive: "Shift 15% of Meta Ads budget to Google Ads for estimated 23% higher ROI."
- Action: [Apply Budget Shift] button
- Expected Impact: +$1,240 revenue
- Confidence: 87%
```

## Visualizations (5 charts)

### 1. Platform Comparison Table
| Metric | Google Ads | Meta Ads | Organic | Winner |
|--------|-----------|----------|---------|--------|
| Spend | $5,200 | $3,800 | $0 | N/A |
| ROAS | 5.2x | 3.9x | N/A | Google Ads ⭐ |
| Conversions | 420 | 285 | 180 | Google Ads ⭐ |
| CPC | $1.20 | $2.10 | $0.00 | Organic ⭐ |
| CVR | 3.8% | 2.1% | 4.2% | Organic ⭐ |

### 2. Spend vs Revenue by Platform (Bar Chart)
- Google Ads: Spend $5,200, Revenue $27,040
- Meta Ads: Spend $3,800, Revenue $14,820
- Organic: Spend $0, Revenue $7,560

### 3. Daily Performance Trend (Line Chart - 30 days)
- 3 lines: Google Ads, Meta Ads, Organic revenue
- Shows performance over time

### 4. Budget Allocation - Current vs Recommended (Pie Charts)
- Current: Google 58%, Meta 42%
- Recommended: Google 65%, Meta 35%
- AI note: "Shift 7% for 15% higher ROAS"

### 5. Conversion Funnel by Platform (Funnel Chart)
- Stages: Impressions → Clicks → Landing → Cart → Purchase
- Compare drop-off rates across platforms

---

# 2. Google Ads Dashboard

**Route:** `/dashboard/google-ads`

## Header
```tsx
title: "Google Ads Performance"
subtitle: "Comprehensive view of your Google Ads campaigns, keywords, and search terms. Optimize your search and shopping campaigns with AI-powered insights."
```

## Filters
```tsx
- Customer selector
- Date range
- Campaign type (ALL, SEARCH, SHOPPING, DISPLAY, VIDEO)
- Campaign (multi-select)
```

## KPIs (6 cards)
```
- Total Spend: $5,200 (+8%)
- ROAS: 5.2x (+12%) [HIGHLIGHTED]
- Conversions: 420 (+24%)
- Avg. CPC: $1.20 (-5%) [Green trend - lower is better]
- CTR: 3.8% (+0.4%)
- Quality Score: 7.2/10 (+0.3)
```

## AI Insights
```tsx
Descriptive: "Search campaigns generated 78% of conversions at 5.8x ROAS. Shopping campaigns contributed 18% at 4.1x ROAS."

Diagnostic: "'Brand Keywords' campaign has 12.4x ROAS due to high purchase intent. 'Competitor Terms' struggling with 2.1x ROAS because of high CPCs ($4.20) and low quality scores (4.2)."

Prescriptive: "Increase brand campaign budget by 25% (expected +$2,100 revenue). Pause 12 underperforming keywords with QS < 3. Add 8 negative keywords to reduce wasted spend by $450/month."
- Action: [Apply All Recommendations]
- Expected Impact: +$1,850 monthly profit
- Confidence: 91%
```

## Visualizations (5 charts)

### 1. Top Campaigns Table
Columns: Campaign Name, Spend, ROAS, Conversions, CPC, Status

### 2. Daily Spend & Revenue Trend (Area Chart - 30 days)
Shows spend and revenue over time

### 3. Performance by Campaign Type (Bar Chart)
Compare: Search, Shopping, Display, Video

### 4. Top 10 Keywords Table
Columns: Keyword, Conversions, ROAS, Quality Score

### 5. Quality Score Distribution (Pie Chart)
Show distribution: 1-3 (Poor), 4-6 (Average), 7-10 (Good)

---

# 3. Meta Ads Dashboard

**Route:** `/dashboard/meta-ads`

## Header
```tsx
title: "Meta Ads Performance"
subtitle: "Analyze your Facebook and Instagram advertising performance. Demographic insights, creative analysis, and audience optimization powered by AI."
```

## Filters
```tsx
- Customer selector
- Date range
- Platform (ALL, Facebook, Instagram, Messenger, Audience Network)
- Objective (ALL, CONVERSIONS, TRAFFIC, AWARENESS, LEADS)
- Campaign (multi-select)
```

## KPIs (6 cards)
```
- Total Spend: $3,800 (+12%)
- ROAS: 3.9x (+5%) [HIGHLIGHTED]
- Conversions: 285 (+18%)
- Avg. CPC: $2.10 (-8%) [Green - lower is better]
- CTR: 2.1% (-18%) [Red - potential ad fatigue]
- Frequency: 4.2 (+1.1) [Warning - creative refresh needed]
```

## AI Insights
```tsx
Descriptive: "Instagram ads generated 62% of conversions, outperforming Facebook (34%). Your best-performing audience is 25-34 females with 4.8% conversion rate."

Diagnostic: "CTR dropped 18% in last 7 days due to ad fatigue. Current creative set shown 4.2 times per user on average. Users aged 25-34 saw ads 5.8 times, causing diminishing returns."
- Details: Frequency 25-34: 5.8 (critical), CTR decline: -18% WoW

Prescriptive: "Refresh ad creatives for 25-34 audience segment. Shift 20% budget from Facebook to Instagram. Reduce desktop spend by 30% and reallocate to mobile."
- Actions: [Pause Fatigued Ads] [Create Creative Brief]
- Expected Impact: +35% CTR, +$890 revenue
- Confidence: 84%
```

## Visualizations (6 charts)

### 1. Top Meta Campaigns Table
Columns: Campaign, Objective, Spend, ROAS, Conversions, Frequency

### 2. Performance by Platform (Bar Chart)
- Instagram: 177 conversions, 4.8x ROAS
- Facebook: 97 conversions, 2.9x ROAS
- Messenger: 8 conversions, 1.2x ROAS
- Audience Network: 3 conversions, 0.8x ROAS

### 3. Top Performing Demographics (Table)
- 25-34 Female: 4.8% CVR, 5.2x ROAS
- 35-44 Female: 3.2% CVR, 4.1x ROAS
- 25-34 Male: 2.1% CVR, 3.2x ROAS

### 4. Daily Performance & Ad Frequency (Combo Chart)
- Line: Conversions
- Bars: Frequency
- Shows correlation between frequency and performance

### 5. Device Breakdown (Pie Chart)
- Mobile: 78% (4.5x ROAS)
- Desktop: 19% (2.1x ROAS)
- Tablet: 3% (1.8x ROAS)

### 6. Geographic Performance (Table)
- United States: 68%, 4.2x ROAS
- Canada: 18%, 3.8x ROAS
- United Kingdom: 9%, 3.2x ROAS

---

# 4. Google Analytics (GA4) Dashboard

**Route:** `/dashboard/google-analytics`

## Header
```tsx
title: "Google Analytics (GA4) - Website Performance"
subtitle: "Understand your website traffic, user behavior, conversion funnels, and organic performance. Identify opportunities to improve user experience and conversion rates."
```

## Filters
```tsx
- Customer selector
- Date range
- Traffic Source (ALL, Organic, Direct, Referral, Social)
- Device (ALL, Desktop, Mobile, Tablet)
```

## KPIs (6 cards)
```
- Total Sessions: 45,200 (+15%)
- Conversion Rate: 4.2% (+0.3%) [HIGHLIGHTED]
- Conversions: 1,898 (+18%)
- Bounce Rate: 32% (-4%) [Green - lower is better]
- Avg. Session Duration: 2:45 (+12s)
- Pages per Session: 3.2 (+0.4)
```

## AI Insights
```tsx
Descriptive: "Organic search drives 58% of traffic with excellent 4.2% conversion rate. Direct traffic shows highest engagement (4.1 pages/session). Mobile traffic is 72% of total, converting at 3.8%."

Diagnostic: "Your checkout page has 42% drop-off rate, likely due to 8.5s load time (3x slower than homepage). Users who view product comparison page convert 2.8x higher."
- Details: Checkout abandonment: 42%, Load time: 8.5s (critical)

Prescriptive: "Optimize checkout page load time (target <3s) to reduce abandonment. Promote product comparison feature on category pages. Improve mobile checkout UX (currently 48% abandonment)."
- Actions: [View Technical Recommendations] [Analyze Checkout Flow]
- Expected Impact: +18% conversion rate, +$4,200/month
- Confidence: 79%
```

## Visualizations (6 charts)

### 1. Traffic Sources Table
Columns: Source, Sessions, Conversions, CVR, Bounce Rate

### 2. Daily Sessions Trend (Line Chart - 30 days)
Show session volume over time

### 3. Conversion Funnel (Funnel Chart)
- Landing Page: 45,200 (100%)
- Product Page: 18,800 (58% drop)
- Add to Cart: 4,512 (76% drop)
- Checkout: 3,260 (28% drop)
- Purchase: 1,898 (42% drop)

### 4. Top Landing Pages Table
Columns: Page, Sessions, CVR, Bounce Rate

### 5. Device Performance (Bar Chart)
- Mobile: 32,544 sessions, 3.8% CVR
- Desktop: 11,296 sessions, 5.1% CVR
- Tablet: 1,360 sessions, 2.9% CVR

### 6. User Behavior Flow (Sankey Chart)
Visual flow from homepage → category → product → cart → checkout → exit

---

# 5. E-Commerce Dashboard

**Route:** `/dashboard`

## Header
```tsx
title: "E-Commerce Performance Dashboard"
subtitle: "Revenue, orders, and product performance across all marketing channels. Track your e-commerce KPIs and identify top-selling products."
```

## Filters
```tsx
- Customer selector
- Date range
- Channel (ALL, Google Ads, Meta Ads, Organic, Direct)
- Product Category (ALL, Electronics, Clothing, Home)
```

## KPIs (6 cards)
```
- Total Revenue: $49,400 (+18%)
- Total Orders: 1,898 (+15%) [HIGHLIGHTED]
- Avg. Order Value: $26.03 (+3%)
- Cart Abandonment: 42% (-5%) [Green - lower is better]
- Customer LTV: $142 (+8%)
- Repeat Purchase Rate: 28% (+4%)
```

## AI Insights
```tsx
Descriptive: "Google Ads drove 52% of e-commerce revenue ($25,688) with $26.05 AOV. Electronics category is top seller (48% of revenue). Mobile checkout improving: 38% abandonment vs 42% last month."

Diagnostic: "Repeat purchase rate dropped from 32% to 28% because email automation stopped working for 12 days. Cart abandonment spikes on mobile at checkout payment step (48%)."

Prescriptive: "Fix email automation to recover repeat purchases. Implement mobile-optimized payment options (Apple Pay, Google Pay) to reduce abandonment. Cross-sell electronics with accessories (+$3,200 potential revenue)."
- Actions: [Setup Cross-Sell Rules]
- Expected Impact: +$4,800/month
```

## Visualizations (5 charts)

### 1. Revenue by Channel (Bar Chart)
Show revenue contribution from each channel

### 2. Daily Revenue Trend (Line Chart - 30 days)
Track revenue over time

### 3. Top Products Table
Columns: Product, Units Sold, Revenue, AOV

### 4. Purchase Funnel (Funnel Chart)
Product View → Add to Cart → Checkout → Purchase

### 5. Customer Segments (Pie Chart)
New vs Returning customers, revenue contribution

---

# Technical Implementation Details

## Required Libraries

```json
{
  "dependencies": {
    "react": "^18.x",
    "react-router-dom": "^6.x",
    "@mui/material": "^5.x",
    "@mui/icons-material": "^5.x",
    "framer-motion": "^10.x",
    "recharts": "^2.x",
    "axios": "^1.x",
    "react-intersection-observer": "^9.x"
  }
}
```

## Global Filter Bar Enhancement

**File:** `src/components/common/GlobalFilterBar.tsx`

Add these filter types:
```tsx
interface FilterConfig {
  type: 'customer' | 'dateRange' | 'platform' | 'campaignType' | 'campaign' | 'source' | 'device' | 'objective';
  label: string;
  options?: string[];
  multiSelect?: boolean;
  default?: any;
}
```

Platform filter options:
```tsx
const platformOptions = ['ALL', 'Google Ads', 'Meta Ads', 'Organic'];
```

## API Service Layer

### Google Ads Service
**File:** `src/services/googleAdsService.ts`

```tsx
export const fetchGoogleAdsCampaigns = async (customerId: number, dateRange: string) => {
  const response = await axios.get(`${API_URL}/google-ads/campaigns`, {
    params: { customer_id: customerId, date_range: dateRange }
  });
  return response.data;
};

export const fetchGoogleAdsMetrics = async (customerId: number, dateRange: string) => {
  const response = await axios.get(`${API_URL}/google-ads/metrics/summary`, {
    params: { customer_id: customerId, date_range: dateRange }
  });
  return response.data;
};
```

### Meta Ads Service
**File:** `src/services/metaAdsService.ts`

```tsx
export const fetchMetaCampaigns = async (customerId: number, dateRange: string) => {
  const response = await axios.get(`${API_URL}/meta/campaigns`, {
    params: { customer_id: customerId, date_range: dateRange }
  });
  return response.data;
};

export const fetchMetaInsightsSummary = async (customerId: number, dateRange: string) => {
  const response = await axios.get(`${API_URL}/meta/insights/summary`, {
    params: { customer_id: customerId, date_range: dateRange }
  });
  return response.data;
};

export const fetchMetaDemographics = async (customerId: number, dateRange: string) => {
  const response = await axios.get(`${API_URL}/meta/insights/age-gender`, {
    params: { customer_id: customerId, date_range: dateRange }
  });
  return response.data;
};
```

### GA4 Service
**File:** `src/services/ga4Service.ts`

```tsx
export const fetchGA4Sessions = async (customerId: number, dateRange: string) => {
  const response = await axios.get(`${API_URL}/ga4/sessions`, {
    params: { customer_id: customerId, date_range: dateRange }
  });
  return response.data;
};

export const fetchGA4ConversionFunnel = async (customerId: number) => {
  const response = await axios.get(`${API_URL}/ga4/funnel`, {
    params: { customer_id: customerId }
  });
  return response.data;
};
```

### Unified Analytics Service
**File:** `src/services/unifiedAnalyticsService.ts`

```tsx
export const fetchUnifiedMetrics = async (customerId: number, dateRange: string) => {
  const [googleAds, metaAds, ga4] = await Promise.all([
    fetchGoogleAdsMetrics(customerId, dateRange),
    fetchMetaInsightsSummary(customerId, dateRange),
    fetchGA4Sessions(customerId, dateRange)
  ]);

  return {
    totalSpend: googleAds.spend + metaAds.spend,
    blendedROAS: calculateBlendedROAS(googleAds, metaAds),
    totalConversions: googleAds.conversions + metaAds.conversions + ga4.conversions,
    platforms: {
      googleAds: googleAds,
      metaAds: metaAds,
      organic: ga4
    }
  };
};

export const fetchPlatformComparison = async (customerId: number, dateRange: string) => {
  // Returns comparison data for table
};
```

---

## Routing Updates

**File:** `src/App.tsx`

```tsx
import UnifiedCrossPlatformDashboard from './components/dashboard/UnifiedCrossPlatformDashboard';
import GoogleAdsDashboard from './components/dashboard/GoogleAdsDashboard';
import MetaAdsDashboard from './components/dashboard/MetaAdsDashboard';
import GoogleAnalyticsDashboard from './components/dashboard/GoogleAnalyticsDashboard';

<Routes>
  {/* Landing Page */}
  <Route path="/" element={<PremiumLandingPage />} />

  {/* Dashboards */}
  <Route path="/*" element={
    <Layout>
      <Routes>
        <Route path="/dashboard/unified" element={<UnifiedCrossPlatformDashboard />} />
        <Route path="/dashboard/google-ads" element={<GoogleAdsDashboard />} />
        <Route path="/dashboard/meta-ads" element={<MetaAdsDashboard />} />
        <Route path="/dashboard/google-analytics" element={<GoogleAnalyticsDashboard />} />
        <Route path="/dashboard" element={<EcommerceDashboard />} />

        {/* Existing routes... */}
      </Routes>
    </Layout>
  } />
</Routes>
```

---

## Shared Components

### InsightCard Enhancement
**File:** `src/components/common/InsightCard.tsx`

```tsx
interface InsightCardProps {
  type: 'descriptive' | 'diagnostic' | 'prescriptive';
  title?: string;
  insight: string;
  priority?: 'info' | 'low' | 'medium' | 'high';
  details?: string[];
  actions?: Array<{
    label: string;
    onClick?: () => void;
    primary?: boolean;
  }>;
  expectedImpact?: string;
  confidence?: string;
}

const InsightCard: React.FC<InsightCardProps> = ({
  type,
  insight,
  priority = 'info',
  details,
  actions,
  expectedImpact,
  confidence
}) => {
  const getIcon = () => {
    switch (type) {
      case 'descriptive': return <Assessment />;
      case 'diagnostic': return <Psychology />;
      case 'prescriptive': return <Lightbulb />;
    }
  };

  const getColor = () => {
    switch (priority) {
      case 'high': return 'error';
      case 'medium': return 'warning';
      case 'low': return 'success';
      default: return 'info';
    }
  };

  return (
    <Paper sx={{ p: 3, borderLeft: 6, borderColor: `${getColor()}.main` }}>
      <Box display="flex" alignItems="center" gap={2} mb={2}>
        <Avatar sx={{ bgcolor: `${getColor()}.main` }}>
          {getIcon()}
        </Avatar>
        <Typography variant="h6">
          {title || (type === 'descriptive' ? 'What Happened' : type === 'diagnostic' ? 'Why It Happened' : 'What To Do')}
        </Typography>
      </Box>

      <Typography variant="body1" sx={{ mb: 2 }}>
        {insight}
      </Typography>

      {details && (
        <Box sx={{ pl: 2, mb: 2 }}>
          {details.map((detail, i) => (
            <Typography key={i} variant="body2" color="text.secondary">
              • {detail}
            </Typography>
          ))}
        </Box>
      )}

      {(expectedImpact || confidence) && (
        <Box display="flex" gap={2} mb={2}>
          {expectedImpact && (
            <Chip label={`Impact: ${expectedImpact}`} color="success" size="small" />
          )}
          {confidence && (
            <Chip label={`Confidence: ${confidence}`} color="info" size="small" />
          )}
        </Box>
      )}

      {actions && (
        <Box display="flex" gap={2}>
          {actions.map((action, i) => (
            <Button
              key={i}
              variant={action.primary ? 'contained' : 'outlined'}
              onClick={action.onClick}
            >
              {action.label}
            </Button>
          ))}
        </Box>
      )}
    </Paper>
  );
};
```

---

## Implementation Checklist

### Phase 1: Landing Page (Week 1)
- [ ] Install framer-motion and react-intersection-observer
- [ ] Create scroll animation variants
- [ ] Build Hero section with parallax
- [ ] Build Platform Integration section with stagger
- [ ] Build Metrics Preview with scale animations
- [ ] Build AI Insights with directional slides
- [ ] Build Comparison Table with row animations
- [ ] Build Features Grid with stagger
- [ ] Build CTA section with pulse
- [ ] Add floating chatbot with float animation
- [ ] Test all scroll triggers
- [ ] Optimize performance (60fps)

### Phase 2: Unified Dashboard (Week 2)
- [ ] Create UnifiedCrossPlatformDashboard component
- [ ] Implement unified analytics service
- [ ] Build platform comparison table
- [ ] Build spend vs revenue chart
- [ ] Build daily trend chart
- [ ] Build budget allocation chart
- [ ] Build conversion funnel chart
- [ ] Add AI insights (3 types)
- [ ] Connect to real APIs
- [ ] Test with sample data

### Phase 3: Platform-Specific Dashboards (Week 3)
- [ ] Build Google Ads Dashboard
- [ ] Build Meta Ads Dashboard
- [ ] Build Google Analytics Dashboard
- [ ] Create platform-specific services
- [ ] Ensure no data duplication
- [ ] Add platform-specific charts
- [ ] Add platform-specific insights

### Phase 4: E-Commerce & Polish (Week 4)
- [ ] Enhance E-Commerce Dashboard
- [ ] Add cross-selling recommendations
- [ ] Improve mobile responsiveness
- [ ] Performance optimization
- [ ] User testing
- [ ] Bug fixes

### Phase 5: Specialized Dashboards (Week 5)
- [ ] Budget Optimizer
- [ ] Forecasting Dashboard
- [ ] Alerts Dashboard
- [ ] Final polish

---

## When Meta Ads Data is Ready

**Run this checklist:**

1. ✅ Meta Ads API integrated (`warehouse_meta_ads_etl.py` running)
2. ✅ Data in `marketing_warehouse.db` (table: `dim_meta_campaign`, `fact_campaign_performance_daily`)
3. ✅ Meta API endpoints working (`/api/v1/meta/campaigns`, `/api/v1/meta/insights/summary`)
4. ✅ Build Meta Ads Dashboard component
5. ✅ Connect to Meta API service
6. ✅ Add Meta data to Unified Dashboard
7. ✅ Test all Meta-specific charts
8. ✅ Verify AI insights include Meta data
9. ✅ Update Landing Page to show Meta integration
10. ✅ Full end-to-end testing

---

## Success Metrics

### Landing Page:
- Time on page > 2 minutes
- Scroll depth > 80%
- CTA click rate > 10%
- Chatbot interaction > 30%

### Dashboards:
- User can identify best platform in < 30 seconds
- AI recommendations clicked > 40%
- Average session duration > 5 minutes
- Return user rate > 60%

---

## Notes for Future Reference

### Color Coding Standards:
- **Green** = Good/Positive (ROAS up, CPC down)
- **Red** = Bad/Negative (CTR down, Spend up without ROAS)
- **Blue** = Information/Neutral
- **Orange** = Warning (frequency high, ad fatigue)

### Chart Selection Guidelines:
- **Comparison** → Table or Bar Chart
- **Trend over time** → Line Chart or Area Chart
- **Part-of-whole** → Pie Chart
- **Funnel/Process** → Funnel Chart
- **Correlation** → Scatter Plot
- **Flow** → Sankey Diagram

### AI Insight Formula:
1. **Descriptive** = State what happened (facts, numbers)
2. **Diagnostic** = Explain why (root cause, correlations)
3. **Prescriptive** = Recommend action (specific, measurable, with confidence)

---

**End of Master Plan**

**Reference this document when Meta Ads data is ready to implement!**
