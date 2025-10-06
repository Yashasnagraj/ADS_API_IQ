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

export default api;