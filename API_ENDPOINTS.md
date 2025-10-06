# MarketingIQ API Endpoints

## Base URL
`http://localhost:8000`

## Available Endpoints

### Campaigns
- `GET /campaigns` - List campaigns with performance metrics
- `GET /campaigns/{id}` - Get specific campaign details
- `GET /campaigns/{id}/performance` - Time-series performance data
- `GET /campaigns/{id}/ads` - Get ads for a campaign
- `GET /campaigns/top-performers` - Top campaigns by metric (roas/conversions/ctr)

### Ad Groups
- `GET /ad-groups` - List ad groups with filtering
- `GET /ad-groups/{id}` - Get specific ad group details
- `GET /ad-groups/{id}/ads` - Get ads for an ad group

### Ads
- `GET /ads` - List all ads with creative content and performance

### Keywords
- `GET /keywords` - List keywords with quality scores
- `GET /keywords/underperformers` - Keywords wasting budget without conversions

### Search Terms
- `GET /search-terms` - Actual search queries triggering ads
- `GET /search-terms/negative` - Suggested negative keywords to reduce waste

### Aggregated Metrics
- `GET /metrics/by-campaign` - Metrics grouped by campaign
- `GET /metrics/by-ad-group` - Metrics grouped by ad group
- `GET /metrics/by-keyword` - Metrics grouped by keyword
- `GET /metrics/by-day-of-week` - Performance by day of week

### Analytics
- `GET /metrics/summary` - Overall performance summary
- `GET /metrics/trends` - Trending metrics over time
- `GET /metrics/compare` - Compare two time periods

### System
- `GET /health` - Database connection health check
- `GET /` - API documentation

## Multi-Agent System Validation

### ✅ Sufficient for Multi-Agent System

**Available Capabilities:**
- **Performance Analysis Agent** - Can analyze campaigns, ads, keywords using metrics endpoints
- **Budget Optimization Agent** - Can identify underperformers and suggest budget reallocation
- **Keyword Research Agent** - Can find negative keywords and analyze search terms
- **Trend Analysis Agent** - Can track performance over time and compare periods
- **Campaign Management Agent** - Can monitor campaign/ad group/ad performance
- **Anomaly Detection Agent** - Can identify unusual patterns in day-of-week or trend data

**Data Points Available:**
- Impressions, Clicks, Cost, Conversions
- CTR, CPC, ROAS, Conversion Rate
- Quality Scores, Ad Positions
- Time-series data for trend analysis
- Search term performance for insights

**Limitations:**
- Read-only API (no create/update/delete)
- No real-time bidding adjustments
- No audience/demographic data
- No competitor analysis data

**Recommendation:** The API provides comprehensive read access to Google Ads data, making it suitable for building analytical and monitoring multi-agent systems. For full automation, you'd need to integrate Google Ads API for write operations.