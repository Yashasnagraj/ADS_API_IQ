// Google Ads Service
import { apiClient } from './api';
import { Campaign, PerformanceMetrics, DailyPerformance } from '../types';
import { API_ENDPOINTS } from '../config/api';

// Convert frontend date range format to backend format
const convertDateRange = (dateRange: string): string => {
  const rangeMap: Record<string, string> = {
    'last_7d': 'LAST_7_DAYS',
    'last_30d': 'LAST_30_DAYS',
    'last_90d': 'LAST_90_DAYS',
  };
  return rangeMap[dateRange] || 'LAST_30_DAYS';
};

export const googleAdsService = {
  /**
   * Get Google Ads campaigns
   */
  async getCampaigns(customerId: number, dateRange: string): Promise<Campaign[]> {
    try {
      const response: any = await apiClient.get(API_ENDPOINTS.GOOGLE_ADS_CAMPAIGNS, {
        params: { customer_id: customerId, date_range: convertDateRange(dateRange) },
      });
      return response.campaigns || [];
    } catch (error) {
      console.error('Error fetching Google Ads campaigns:', error);
      return [];
    }
  },

  /**
   * Get Google Ads metrics summary from warehouse
   */
  async getMetricsSummary(customerId: number, dateRange: string): Promise<PerformanceMetrics> {
    try {
      const data = await apiClient.get<PerformanceMetrics>(API_ENDPOINTS.GOOGLE_ADS_METRICS, {
        params: { customer_id: customerId, date_range: convertDateRange(dateRange) },
      });

      return data;
    } catch (error) {
      console.error('Error fetching Google Ads metrics:', error);
      // Return empty metrics on error
      return {
        impressions: 0,
        clicks: 0,
        spend: 0,
        conversions: 0,
        conversion_value: 0,
        ctr: 0,
        cpc: 0,
        cpm: 0,
        cpa: 0,
        roas: 0,
      };
    }
  },

  /**
   * Get Google Ads daily performance
   */
  async getDailyPerformance(customerId: number, dateRange: string): Promise<DailyPerformance[]> {
    try {
      return await apiClient.get<DailyPerformance[]>(API_ENDPOINTS.GOOGLE_ADS_DAILY_PERFORMANCE, {
        params: { customer_id: customerId, date_range: dateRange },
      });
    } catch (error) {
      console.error('Error fetching Google Ads daily performance:', error);
      throw error;
    }
  },

  /**
   * Get Google Ads keywords
   */
  async getKeywords(customerId: number, dateRange: string): Promise<any[]> {
    try {
      return await apiClient.get<any[]>(API_ENDPOINTS.GOOGLE_ADS_KEYWORDS, {
        params: { customer_id: customerId, date_range: dateRange },
      });
    } catch (error) {
      console.error('Error fetching Google Ads keywords:', error);
      throw error;
    }
  },
};
