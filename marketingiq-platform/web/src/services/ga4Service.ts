// Google Analytics 4 Service
import { apiClient } from './api';
import { GA4Metrics, GA4SourceMedium } from '../types';
import { API_ENDPOINTS } from '../config/api';

export const ga4Service = {
  /**
   * Get GA4 sessions summary
   */
  async getSessions(customerId: number, dateRange: string): Promise<GA4Metrics> {
    try {
      const data = await apiClient.get<GA4Metrics>(API_ENDPOINTS.GA4_SESSIONS, {
        params: { customer_id: customerId, date_range: dateRange },
      });

      return data;
    } catch (error) {
      console.error('Error fetching GA4 sessions:', error);
      // Return empty metrics on error
      return {
        sessions: 0,
        conversion_rate: 0,
        conversions: 0,
        bounce_rate: 0,
        avg_session_duration: 0,
        pages_per_session: 0,
      };
    }
  },

  /**
   * Get GA4 conversion funnel
   */
  async getConversionFunnel(customerId: number): Promise<any[]> {
    try {
      return await apiClient.get<any[]>(API_ENDPOINTS.GA4_CONVERSION_FUNNEL, {
        params: { customer_id: customerId },
      });
    } catch (error) {
      console.error('Error fetching GA4 conversion funnel:', error);
      throw error;
    }
  },

  /**
   * Get GA4 source/medium data
   */
  async getSourceMedium(customerId: number, dateRange: string): Promise<GA4SourceMedium[]> {
    try {
      return await apiClient.get<GA4SourceMedium[]>(API_ENDPOINTS.GA4_SOURCE_MEDIUM, {
        params: { customer_id: customerId, date_range: dateRange },
      });
    } catch (error) {
      console.error('Error fetching GA4 source/medium:', error);
      throw error;
    }
  },

  /**
   * Get GA4 daily traffic
   */
  async getDailyTraffic(customerId: number, dateRange: string): Promise<any[]> {
    try {
      return await apiClient.get<any[]>(API_ENDPOINTS.GA4_DAILY_TRAFFIC, {
        params: { customer_id: customerId, date_range: dateRange },
      });
    } catch (error) {
      console.error('Error fetching GA4 daily traffic:', error);
      throw error;
    }
  },
};
