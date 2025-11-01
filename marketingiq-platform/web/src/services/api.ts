// API Client Service
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';
import API_CONFIG from '../config/api';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_CONFIG.BASE_URL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Add auth token if needed
        const token = localStorage.getItem('auth_token');
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => {
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          // Handle unauthorized
          console.error('Unauthorized access');
        }
        return Promise.reject(error);
      }
    );
  }

  async get<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.get<T>(url, config);
    return response.data;
  }

  async post<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.post<T>(url, data, config);
    return response.data;
  }

  async put<T>(url: string, data?: any, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.put<T>(url, data, config);
    return response.data;
  }

  async delete<T>(url: string, config?: AxiosRequestConfig): Promise<T> {
    const response = await this.client.delete<T>(url, config);
    return response.data;
  }
}

export const apiClient = new ApiClient();

// Service exports for dashboards
const api = apiClient;

export const campaignService = {
  getCampaigns: (customerId: string, dateRange: string = 'LAST_30_DAYS', limit: number = 100) =>
    api.get('/warehouse/campaigns', {
      params: { customer_id: customerId, date_range: dateRange, limit }
    }),
  getCampaignById: (id: string, customerId: string) =>
    api.get(`/warehouse/campaigns/${id}`, {
      params: { customer_id: customerId }
    }),
  getCampaignMetrics: (customerId: string, dateRange: string = 'LAST_30_DAYS') =>
    api.get('/warehouse/metrics/summary', {
      params: { customer_id: customerId, date_range: dateRange }
    }),
};

export const insightService = {
  getCampaignInsights: (customerId: string, dateRange: string = 'last_30d') =>
    api.get('/warehouse/insights/campaign-insights', {
      params: { customer_id: customerId, date_range: dateRange }
    }),
  getKeywordInsights: (customerId: string, dateRange: string = 'last_30d') =>
    api.get('/warehouse/insights/keyword-insights', {
      params: { customer_id: customerId, date_range: dateRange }
    }),
  getAnomalies: (customerId: string, dateRange: string = 'last_30d') =>
    api.get('/warehouse/insights/anomalies', {
      params: { customer_id: customerId, date_range: dateRange }
    }),
  getSummary: (customerId: string, dateRange: string = 'last_30d') =>
    api.get('/warehouse/insights/campaign-insights', {
      params: { customer_id: customerId, date_range: dateRange }
    }),
};

export const forecastService = {
  getCTRForecast: (customerId: string, forecastDays: number = 7) =>
    api.get('/warehouse/forecasting/ctr-forecast', {
      params: { customer_id: customerId, forecast_days: forecastDays }
    }),
  getSpendForecast: (customerId: string, forecastDays: number = 7) =>
    api.get('/warehouse/forecasting/spend-forecast', {
      params: { customer_id: customerId, forecast_days: forecastDays }
    }),
  getScenarios: (customerId: string) =>
    api.get('/warehouse/forecasting/scenarios', {
      params: { customer_id: customerId }
    }),
  runScenario: (customerId: string, data: any) =>
    api.post('/warehouse/forecasting/scenarios', data, {
      params: { customer_id: customerId }
    }),
};

export const alertService = {
  getAlerts: (customerId: string) =>
    api.get('/warehouse/alerts/active', {
      params: { customer_id: customerId }
    }),
  getThresholds: (customerId: string) =>
    api.get('/warehouse/alerts/thresholds', {
      params: { customer_id: customerId }
    }),
  createAlert: (customerId: string, data: any) =>
    api.post('/warehouse/alerts/active', data, {
      params: { customer_id: customerId }
    }),
  updateThreshold: (customerId: string, id: string, data: any) =>
    api.put(`/warehouse/alerts/thresholds/${id}`, data, {
      params: { customer_id: customerId }
    }),
};

export const optimizationService = {
  getBudgetRecommendations: (customerId: string, dateRange: string = 'last_30d') =>
    api.get('/warehouse/optimization/budget-recommendations', {
      params: { customer_id: customerId, date_range: dateRange }
    }),
  getKeywordRecommendations: (customerId: string, dateRange: string = 'last_30d') =>
    api.get('/warehouse/optimization/keyword-recommendations', {
      params: { customer_id: customerId, date_range: dateRange }
    }),
  getCampaignSimulations: (customerId: string, scenarioType: string = 'budget_increase') =>
    api.get('/warehouse/optimization/campaign-simulator', {
      params: { customer_id: customerId, scenario_type: scenarioType }
    }),
};
