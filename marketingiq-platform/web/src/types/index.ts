// Core Types for Marketing IQ Platform

export interface Customer {
  customer_id: number;
  customer_name: string;
  descriptive_name?: string;
  google_ads_customer_id?: string;
  meta_business_id?: string;
  ga4_account_id?: string;
  industry_vertical?: string;
  currency: string;
  is_active: boolean;
}

export interface DateRange {
  start_date: string;
  end_date: string;
}

export interface FilterState {
  customer_id?: number;
  date_range: string; // 'last_7d', 'last_30d', 'last_90d', 'custom'
  custom_start?: string;
  custom_end?: string;
  platform?: 'ALL' | 'google_ads' | 'meta_ads' | 'ga4';
  campaign_type?: string;
  campaign_ids?: string[];
}

// KPI Card Data
export interface KPIData {
  title: string;
  value: string | number;
  change: number; // Percentage change
  changeLabel?: string;
  icon?: React.ReactNode;
  color?: 'primary' | 'success' | 'error' | 'warning' | 'info';
  trend?: 'up' | 'down' | 'neutral';
  isHighlighted?: boolean;
  prefix?: string;
  suffix?: string;
}

// Insight Card Data
export interface InsightData {
  type: 'descriptive' | 'diagnostic' | 'prescriptive';
  title?: string;
  insight: string;
  priority?: 'info' | 'low' | 'medium' | 'high';
  details?: string[];
  actions?: InsightAction[];
  expectedImpact?: string;
  confidence?: string;
}

export interface InsightAction {
  label: string;
  onClick?: () => void;
  primary?: boolean;
}

// Campaign Data
export interface Campaign {
  campaign_id: string;
  campaign_name: string;
  status: string;
  channel_type?: string;
  spend: number;
  impressions: number;
  clicks: number;
  conversions: number;
  ctr: number;
  cpc: number;
  roas?: number;
  quality_score?: number;
}

// Performance Metrics
export interface PerformanceMetrics {
  impressions: number;
  clicks: number;
  spend: number;
  conversions: number;
  conversion_value: number;
  ctr: number;
  cpc: number;
  cpm: number;
  cpa: number;
  roas: number;
}

// Daily Performance
export interface DailyPerformance {
  date: string;
  impressions: number;
  clicks: number;
  spend: number;
  conversions: number;
  revenue: number;
  roas: number;
}

// Platform Comparison
export interface PlatformComparison {
  platform: string;
  spend: number;
  revenue: number;
  roas: number;
  conversions: number;
  cpc: number;
  cvr: number;
}

// GA4 Data
export interface GA4Metrics {
  sessions: number;
  conversion_rate: number;
  conversions: number;
  bounce_rate: number;
  avg_session_duration: number;
  pages_per_session: number;
}

export interface GA4SourceMedium {
  source: string;
  medium: string;
  sessions: number;
  conversions: number;
  cvr: number;
  bounce_rate: number;
}

// Chart Data
export interface ChartDataPoint {
  date?: string;
  name?: string;
  value: number;
  [key: string]: any;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
  error?: string;
}

// Meta Ads Types
export interface MetaCampaign {
  campaign_id: string;
  name: string;
  status: string;
  objective: string;
  spend: number;
  impressions: number;
  clicks: number;
  conversions: number;
  ctr: number;
  cpc: number;
  roas: number;
  frequency?: number;
}

export interface MetaDemographics {
  age_range: string;
  gender: string;
  impressions: number;
  clicks: number;
  conversions: number;
  spend: number;
  cvr: number;
  roas: number;
}

// Unified Dashboard Data
export interface UnifiedMetrics {
  total_spend: number;
  blended_roas: number;
  total_conversions: number;
  best_platform: {
    name: string;
    roas: number;
  };
  best_platform_by_conversions: {
    name: string;
    conversions: number;
  };
  platforms: {
    google_ads?: PerformanceMetrics;
    meta_ads?: PerformanceMetrics;
    ga4?: GA4Metrics;
  };
}
