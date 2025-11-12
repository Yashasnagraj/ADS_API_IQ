// Comparison Service for Week-over-Week and Period-over-Period metrics
import { apiClient } from './api';
import { API_CONFIG } from '../config/api';

export interface MetricComparison {
  metric_name: string;
  current_value: number;
  previous_value: number;
  change_percentage: number;
  change_direction: 'increase' | 'decrease' | 'no_change';
  is_positive_change: boolean;
  current_period_start: string;
  current_period_end: string;
  previous_period_start: string;
  previous_period_end: string;
}

export interface BatchComparisonRequest {
  customer_id: string;
  metrics: string[];  // Array of metric names
  date_range?: string;
  start_date?: string;
  end_date?: string;
  platform?: string;
  campaign_id?: string;
}

export const comparisonService = {
  /**
   * Get comparison for a single metric
   */
  async getMetricComparison(
    customerId: string,
    metric: string,
    dateRange: string = 'LAST_30_DAYS',
    options?: {
      startDate?: string;
      endDate?: string;
      platform?: string;
      campaignId?: string;
    }
  ): Promise<MetricComparison> {
    try {
      const params: any = {
        customer_id: customerId,
        metric,
        date_range: dateRange,
      };

      if (options?.startDate) params.start_date = options.startDate;
      if (options?.endDate) params.end_date = options.endDate;
      if (options?.platform) params.platform = options.platform;
      if (options?.campaignId) params.campaign_id = options.campaignId;

      const response = await apiClient.get<MetricComparison>(
        `${API_CONFIG.BASE_URL}/comparisons/metrics`,
        { params }
      );

      return response;
    } catch (error) {
      console.error(`Error fetching comparison for metric ${metric}:`, error);
      throw error;
    }
  },

  /**
   * Get comparisons for multiple metrics in a single request
   * Returns a map of metric name to comparison data
   */
  async getBatchMetricComparisons(
    customerId: string,
    metrics: string[],
    dateRange: string = 'LAST_30_DAYS',
    options?: {
      startDate?: string;
      endDate?: string;
      platform?: string;
      campaignId?: string;
    }
  ): Promise<Record<string, MetricComparison>> {
    try {
      const params: any = {
        customer_id: customerId,
        metrics: metrics.join(','),
        date_range: dateRange,
      };

      if (options?.startDate) params.start_date = options.startDate;
      if (options?.endDate) params.end_date = options.endDate;
      if (options?.platform) params.platform = options.platform;
      if (options?.campaignId) params.campaign_id = options.campaignId;

      const response = await apiClient.get<MetricComparison[]>(
        `${API_CONFIG.BASE_URL}/comparisons/metrics/batch`,
        { params }
      );

      // Convert array to map
      const comparisonMap: Record<string, MetricComparison> = {};
      response.forEach((comparison: MetricComparison) => {
        comparisonMap[comparison.metric_name] = comparison;
      });

      return comparisonMap;
    } catch (error) {
      console.error('Error fetching batch metric comparisons:', error);
      throw error;
    }
  },

  /**
   * Get GA4-specific metric comparisons
   */
  async getGA4MetricComparison(
    customerId: string,
    metric: string,
    dateRange: string = 'LAST_30_DAYS',
    options?: {
      startDate?: string;
      endDate?: string;
    }
  ): Promise<MetricComparison> {
    try {
      const params: any = {
        customer_id: customerId,
        metric,
        date_range: dateRange,
      };

      if (options?.startDate) params.start_date = options.startDate;
      if (options?.endDate) params.end_date = options.endDate;

      const response = await apiClient.get<MetricComparison>(
        `${API_CONFIG.BASE_URL}/comparisons/ga4/metrics`,
        { params }
      );

      return response;
    } catch (error) {
      console.error(`Error fetching GA4 comparison for metric ${metric}:`, error);
      throw error;
    }
  },

  /**
   * Helper: Calculate change percentage locally
   */
  calculateChange(currentValue: number, previousValue: number): number {
    if (previousValue === 0) {
      return currentValue > 0 ? 100 : 0;
    }
    return ((currentValue - previousValue) / previousValue) * 100;
  },

  /**
   * Helper: Determine if change is positive based on metric type
   */
  isChangePositive(metric: string, changeDirection: 'increase' | 'decrease' | 'no_change'): boolean {
    // Metrics where decrease is good
    const inverseMetrics = ['bounce_rate', 'cpc', 'cpm', 'cpa', 'cost'];

    if (changeDirection === 'no_change') return true;

    if (inverseMetrics.includes(metric.toLowerCase())) {
      return changeDirection === 'decrease';
    }

    return changeDirection === 'increase';
  },

  /**
   * Helper: Format change percentage for display
   */
  formatChangePercentage(changePercentage: number): string {
    const sign = changePercentage > 0 ? '+' : '';
    return `${sign}${changePercentage.toFixed(1)}%`;
  },

  /**
   * Helper: Get change color for UI
   */
  getChangeColor(isPositive: boolean): string {
    return isPositive ? 'success' : 'error';
  },

  /**
   * Helper: Get change icon name
   */
  getChangeIcon(changeDirection: 'increase' | 'decrease' | 'no_change'): string {
    if (changeDirection === 'increase') return 'TrendingUp';
    if (changeDirection === 'decrease') return 'TrendingDown';
    return 'Minus';
  },
};

export default comparisonService;
