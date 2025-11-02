// Meta Ads Service
import { apiClient } from './api';
import { MetaCampaign, PerformanceMetrics, MetaDemographics, DailyPerformance } from '../types';
import { API_ENDPOINTS } from '../config/api';

export const metaAdsService = {
  /**
   * Get Meta Ads campaigns
   */
  async getCampaigns(customerId: number, dateRange: string): Promise<MetaCampaign[]> {
    try {
      const response = await apiClient.get<{ campaigns: MetaCampaign[]; total_count: number }>(
        API_ENDPOINTS.META_CAMPAIGNS,
        {
          params: { customer_id: customerId, date_range: dateRange },
        }
      );
      // API returns { campaigns: [...], total_count: N }
      return response.campaigns || [];
    } catch (error) {
      console.warn('Meta Ads campaigns endpoint not available:', error);
      return [];
    }
  },

  /**
   * Get Meta Ads insights summary
   */
  async getInsightsSummary(customerId: number, dateRange: string): Promise<any> {
    try {
      const response = await apiClient.get<any>(API_ENDPOINTS.META_INSIGHTS_SUMMARY, {
        params: { customer_id: customerId, date_range: dateRange },
      });
      return response;
    } catch (error) {
      console.warn('Meta Ads insights endpoint not available:', error);
      // Return empty metrics if API fails
      return {
        total_impressions: 0,
        total_clicks: 0,
        total_spend: 0,
        total_reach: 0,
        avg_frequency: 0,
        total_conversions: 0,
        total_purchase_value: 0,
        avg_ctr: 0,
        avg_cpc: 0,
        avg_cpm: 0,
        overall_roas: 0,
      };
    }
  },

  /**
   * Get Meta Ads demographics
   */
  async getDemographics(customerId: number, dateRange: string): Promise<MetaDemographics[]> {
    try {
      return await apiClient.get<MetaDemographics[]>(API_ENDPOINTS.META_DEMOGRAPHICS, {
        params: { customer_id: customerId, date_range: dateRange },
      });
    } catch (error) {
      console.warn('Meta Ads demographics endpoint not available:', error);
      return [];
    }
  },

  /**
   * Get Meta Ads daily performance
   */
  async getDailyPerformance(customerId: number, dateRange: string): Promise<DailyPerformance[]> {
    try {
      return await apiClient.get<DailyPerformance[]>(API_ENDPOINTS.META_DAILY_PERFORMANCE, {
        params: { customer_id: customerId, date_range: dateRange },
      });
    } catch (error) {
      console.warn('Meta Ads daily performance endpoint not available:', error);
      return [];
    }
  },
};
