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
  getCampaigns: () => api.get('/campaigns'),
  getCampaignById: (id: string) => api.get(`/campaigns/${id}`),
  getCampaignMetrics: () => api.get('/metrics/campaigns'),
};

export const insightService = {
  getCampaignInsights: () => api.get('/insights/campaigns'),
  getKeywordInsights: () => api.get('/insights/keywords'),
  getAnomalies: () => api.get('/insights/anomalies'),
  getSummary: () => api.get('/insights/summary'),
};

export const forecastService = {
  getCTRForecast: () => api.get('/forecasts/ctr'),
  getSpendForecast: () => api.get('/forecasts/spend'),
  getScenarios: () => api.get('/forecasts/scenarios'),
};

export const alertService = {
  getAlerts: () => api.get('/alerts'),
  getThresholds: () => api.get('/alerts/thresholds'),
  createAlert: (data: any) => api.post('/alerts', data),
  updateThreshold: (id: string, data: any) => api.put(`/alerts/thresholds/${id}`, data),
};

export const optimizationService = {
  getBudgetRecommendations: () => api.get('/optimization/budget'),
  getKeywordRecommendations: () => api.get('/optimization/keywords'),
  runSimulation: (data: any) => api.post('/optimization/simulator', data),
};
