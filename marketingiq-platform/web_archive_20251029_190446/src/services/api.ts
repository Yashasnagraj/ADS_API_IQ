import axios from 'axios';

const API_BASE_URL = 'http://localhost:8001';

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error);
    return Promise.reject(error);
  }
);

export const campaignService = {
  getCampaigns: () => api.get('/campaigns'),
  getCampaignById: (id: string) => api.get(`/campaigns/${id}`),
  getCampaignMetrics: () => api.get('/metrics/campaigns'),
};

export const adGroupService = {
  getAdGroups: () => api.get('/adgroups'),
  getAdGroupById: (id: string) => api.get(`/adgroups/${id}`),
  getAdGroupMetrics: () => api.get('/metrics/adgroups'),
};

export const keywordService = {
  getKeywords: () => api.get('/keywords'),
  getKeywordById: (id: string) => api.get(`/keywords/${id}`),
  getKeywordPerformance: () => api.get('/metrics/keywords'),
};

export const searchTermService = {
  getSearchTerms: () => api.get('/search-terms'),
  getSearchTermMetrics: () => api.get('/metrics/search-terms'),
};

export const insightService = {
  getCampaignInsights: () => api.get('/insights/campaigns'),
  getKeywordInsights: () => api.get('/insights/keywords'),
  getAnomalies: () => api.get('/insights/anomalies'),
  getSummary: () => api.get('/insights/summary'),
};

export const optimizationService = {
  getBudgetRecommendations: () => api.get('/optimization/budget'),
  getKeywordRecommendations: () => api.get('/optimization/keywords'),
  runSimulation: (params: any) => api.post('/optimization/simulate', params),
};

export const forecastService = {
  getCTRForecast: (days?: number) => api.get(`/forecast/ctr?days=${days || 30}`),
  getSpendForecast: (days?: number) => api.get(`/forecast/spend?days=${days || 30}`),
  runScenario: (params: any) => api.post('/forecast/scenario', params),
};

export const alertService = {
  getAlerts: () => api.get('/alerts'),
  getThresholds: () => api.get('/alerts/thresholds'),
  updateThreshold: (id: string, data: any) => api.put(`/alerts/thresholds/${id}`, data),
};

export const mlService = {
  getFeatureImportance: () => api.get('/ml/features'),
  getPredictions: () => api.get('/ml/predictions'),
};

// ==============================================================================
// GA4 SERVICES (Google Analytics 4 Integration)
// ==============================================================================

export const ga4IntegrationService = {
  // Check GA4 integration status for a customer
  getStatus: (customerId: number) =>
    api.get(`/ga4/integration/status?customer_id=${customerId}`),

  // Get all GA4 properties for a customer
  getProperties: (customerId: number) =>
    api.get(`/ga4/properties?customer_id=${customerId}`),
};

export const ga4SessionService = {
  // Get session metrics filtered by date, source, campaign, device
  getSessions: (customerId: number, params?: any) =>
    api.get(`/ga4/sessions`, { params: { customer_id: customerId, ...params } }),

  // Get aggregated behavior metrics grouped by source
  getBehaviorBySource: (customerId: number, startDate?: string, endDate?: string) =>
    api.get(`/ga4/sessions/by-source`, {
      params: { customer_id: customerId, start_date: startDate, end_date: endDate }
    }),

  // Get aggregated behavior metrics grouped by campaign
  getBehaviorByCampaign: (customerId: number, startDate?: string, endDate?: string) =>
    api.get(`/ga4/sessions/by-campaign`, {
      params: { customer_id: customerId, start_date: startDate, end_date: endDate }
    }),
};

export const ga4EventService = {
  // Get event tracking data
  getEvents: (customerId: number, params?: any) =>
    api.get(`/ga4/events`, { params: { customer_id: customerId, ...params } }),

  // Get top events by count
  getTopEvents: (customerId: number, limit: number = 10) =>
    api.get(`/ga4/events/top`, {
      params: { customer_id: customerId, limit }
    }),
};

export const ga4AttributionService = {
  // Get conversion paths showing customer journey
  getConversionPaths: (customerId: number, params?: any) =>
    api.get(`/ga4/conversion-paths`, {
      params: { customer_id: customerId, ...params }
    }),

  // Get attribution models (first-touch, last-touch, linear, time-decay)
  getAttributionModels: (customerId: number, startDate?: string, endDate?: string) =>
    api.get(`/ga4/attribution`, {
      params: { customer_id: customerId, start_date: startDate, end_date: endDate }
    }),
};

export const ga4AudienceService = {
  // Get audience demographics and technology insights
  getInsights: (customerId: number, params?: any) =>
    api.get(`/ga4/audience-insights`, {
      params: { customer_id: customerId, ...params }
    }),

  // Get aggregated metrics by device category
  getDeviceBreakdown: (customerId: number, startDate?: string, endDate?: string) =>
    api.get(`/ga4/audience-insights/devices`, {
      params: { customer_id: customerId, start_date: startDate, end_date: endDate }
    }),

  // Get aggregated metrics by country
  getCountryBreakdown: (customerId: number, limit: number = 10, startDate?: string, endDate?: string) =>
    api.get(`/ga4/audience-insights/countries`, {
      params: { customer_id: customerId, limit, start_date: startDate, end_date: endDate }
    }),
};

// ⭐ MOST IMPORTANT: Campaign Enrichment (Google Ads + GA4 Combined)
export const ga4EnrichmentService = {
  // Combine Google Ads campaign data with GA4 user behavior metrics
  // Returns campaigns with bounce rate, engagement, session duration, quality score
  enrichCampaigns: (customerId: number, startDate?: string, endDate?: string) =>
    api.get(`/ga4/campaign-enrichment`, {
      params: { customer_id: customerId, start_date: startDate, end_date: endDate }
    }),

  // Get detailed user behavior for a specific campaign
  getUserBehaviorByCampaign: (customerId: number, campaignId: number) =>
    api.get(`/ga4/user-behavior`, {
      params: { customer_id: customerId, campaign_id: campaignId }
    }),
};

export default api;