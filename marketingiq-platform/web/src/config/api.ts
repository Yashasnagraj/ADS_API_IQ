/**
 * API Configuration
 * Centralized configuration for API endpoints
 * Supports environment variables for production deployment via Vite
 */

// Check if we're in production
const isProduction = import.meta.env.PROD;

// Helper to get env var with fallback
const getEnvVar = (value: string | undefined, fallback: string): string => {
  return value || fallback;
};

export const API_CONFIG = {
  // Backend REST API (SQLite)
  BASE_URL: getEnvVar(
    import.meta.env.VITE_API_BASE_URL,
    isProduction
      ? 'https://your-backend-api.com/api/v1' // Replace with your actual backend URL
      : 'http://localhost:8000/api/v1'
  ),

  // Main Data API (SQLite-based)
  DATA_API_URL: getEnvVar(
    import.meta.env.VITE_DATA_API_URL,
    isProduction ? 'https://your-backend-api.com' : 'http://localhost:8000'
  ),

  // Multi-Agent System API
  AGENT_API_URL: getEnvVar(
    import.meta.env.VITE_AGENT_API_URL,
    isProduction ? 'https://your-agent-api.com/api' : 'http://localhost:8000/api'
  ),

  // ADK Chatbot API
  CHATBOT_API_URL: getEnvVar(
    import.meta.env.VITE_CHATBOT_API_URL,
    isProduction ? 'https://your-chatbot-api.com/api' : 'http://localhost:8003/api'
  ),

  // Request timeout (ms)
  TIMEOUT: 30000,

  // Enable debug logging (disabled in production)
  DEBUG: !isProduction,
} as const;

export const API_ENDPOINTS = {
  // Customers
  CUSTOMERS: '/customers',

  // Google Ads - Data Agent endpoints (using warehouse)
  GOOGLE_ADS_CAMPAIGNS: '/warehouse/campaigns',
  GOOGLE_ADS_KEYWORDS: '/warehouse/keywords',
  GOOGLE_ADS_ADGROUPS: '/warehouse/ad-groups',
  GOOGLE_ADS_SEARCH_TERMS: '/warehouse/search-terms',
  GOOGLE_ADS_ML_FEATURES: '/warehouse/ml-features',
  GOOGLE_ADS_ENRICHED_CAMPAIGNS: '/warehouse/campaigns/enriched',

  // Google Ads - Performance endpoints
  GOOGLE_ADS_METRICS: '/warehouse/google-ads/summary',
  GOOGLE_ADS_DAILY_PERFORMANCE: '/warehouse/campaigns/performance/daily',
  METRICS_SUMMARY: '/warehouse/metrics/summary',

  // Meta Ads (using warehouse/database endpoints to avoid API rate limits)
  META_CAMPAIGNS: '/warehouse/meta/campaigns',
  META_INSIGHTS_SUMMARY: '/warehouse/meta/insights/summary',
  META_DEMOGRAPHICS: '/meta/insights/demographics',
  META_DAILY_PERFORMANCE: '/meta/performance/daily',

  // GA4
  GA4_SESSIONS: '/warehouse/ga4/sessions',
  GA4_CONVERSION_FUNNEL: '/ga4/funnel',
  GA4_SOURCE_MEDIUM: '/ga4/source-medium',
  GA4_DAILY_TRAFFIC: '/ga4/traffic/daily',

  // Unified
  UNIFIED_METRICS: '/unified/metrics',
  UNIFIED_PLATFORM_COMPARISON: '/unified/platform-comparison',
  UNIFIED_DAILY_PERFORMANCE: '/unified/performance/daily',

  // Insight Agent endpoints
  INSIGHTS_SUMMARY: '/insights/summary',
  INSIGHTS_CAMPAIGN: '/insights/campaigns',
  INSIGHTS_KEYWORD: '/insights/keywords',
  INSIGHTS_ANOMALIES: '/insights/anomalies',

  // Optimization Agent endpoints
  OPTIMIZATION_BUDGET: '/optimization/budget',
  OPTIMIZATION_KEYWORDS: '/optimization/keywords',
  OPTIMIZATION_SIMULATOR: '/optimization/simulator',

  // Forecasting Agent endpoints
  FORECASTS_CTR: '/forecasts/ctr',
  FORECASTS_SPEND: '/forecasts/spend',
  FORECASTS_SCENARIOS: '/forecasts/scenarios',

  // Alert Agent endpoints
  ALERTS: '/alerts',
  ALERTS_THRESHOLDS: '/alerts/thresholds',
};

export const DEFAULT_DATE_RANGES = {
  last_7d: 7,
  last_30d: 30,
  last_90d: 90,
};

export const DATE_RANGE_OPTIONS = [
  { label: 'Last 7 days', value: 'last_7d' },
  { label: 'Last 30 days', value: 'last_30d' },
  { label: 'Last 90 days', value: 'last_90d' },
  { label: 'Custom', value: 'custom' },
];

export const PLATFORM_OPTIONS = [
  { label: 'All Platforms', value: 'ALL' },
  { label: 'Google Ads', value: 'google_ads' },
  { label: 'Meta Ads', value: 'meta_ads' },
  { label: 'Google Analytics', value: 'ga4' },
];

export default API_CONFIG;
