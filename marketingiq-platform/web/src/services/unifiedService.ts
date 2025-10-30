// Unified Analytics Service (Cross-Platform)
import { apiClient } from './api';
import { UnifiedMetrics, PlatformComparison, DailyPerformance } from '../types';
import { API_ENDPOINTS } from '../config/api';
import { googleAdsService } from './googleAdsService';
import { metaAdsService } from './metaAdsService';
import { ga4Service } from './ga4Service';

export const unifiedService = {
  /**
   * Get unified metrics across all platforms
   */
  async getUnifiedMetrics(customerId: number, dateRange: string): Promise<UnifiedMetrics> {
    try {
      // Fetch data from all platforms in parallel
      const [googleAds, metaAds, ga4] = await Promise.allSettled([
        googleAdsService.getMetricsSummary(customerId, dateRange),
        metaAdsService.getInsightsSummary(customerId, dateRange),
        ga4Service.getSessions(customerId, dateRange),
      ]);

      const googleAdsData = googleAds.status === 'fulfilled' ? googleAds.value : null;
      const metaAdsData = metaAds.status === 'fulfilled' ? metaAds.value : null;
      const ga4Data = ga4.status === 'fulfilled' ? ga4.value : null;

      // Calculate unified metrics
      const totalSpend = (googleAdsData?.spend || 0) + (metaAdsData?.spend || 0);
      const totalRevenue = (googleAdsData?.conversion_value || 0) + (metaAdsData?.conversion_value || 0);
      const blendedROAS = totalSpend > 0 ? totalRevenue / totalSpend : 0;
      const totalConversions = (googleAdsData?.conversions || 0) + (metaAdsData?.conversions || 0) + (ga4Data?.conversions || 0);

      // Determine best platform
      const platformROAS = {
        google_ads: googleAdsData?.roas || 0,
        meta_ads: metaAdsData?.roas || 0,
      };
      const bestPlatform = Object.entries(platformROAS).reduce((best, [name, roas]) =>
        roas > best.roas ? { name, roas } : best
      , { name: 'google_ads', roas: 0 });

      return {
        total_spend: totalSpend,
        blended_roas: blendedROAS,
        total_conversions: totalConversions,
        best_platform: {
          name: bestPlatform.name === 'google_ads' ? 'Google Ads' : 'Meta Ads',
          roas: bestPlatform.roas,
        },
        platforms: {
          google_ads: googleAdsData || undefined,
          meta_ads: metaAdsData || undefined,
          ga4: ga4Data || undefined,
        },
      };
    } catch (error) {
      console.error('Error fetching unified metrics:', error);
      throw error;
    }
  },

  /**
   * Get platform comparison data
   */
  async getPlatformComparison(customerId: number, dateRange: string): Promise<PlatformComparison[]> {
    try {
      const metrics = await this.getUnifiedMetrics(customerId, dateRange);
      const comparison: PlatformComparison[] = [];

      if (metrics.platforms.google_ads) {
        comparison.push({
          platform: 'Google Ads',
          spend: metrics.platforms.google_ads.spend,
          revenue: metrics.platforms.google_ads.conversion_value,
          roas: metrics.platforms.google_ads.roas,
          conversions: metrics.platforms.google_ads.conversions,
          cpc: metrics.platforms.google_ads.cpc,
          cvr: (metrics.platforms.google_ads.conversions / metrics.platforms.google_ads.clicks) * 100,
        });
      }

      if (metrics.platforms.meta_ads) {
        comparison.push({
          platform: 'Meta Ads',
          spend: metrics.platforms.meta_ads.spend,
          revenue: metrics.platforms.meta_ads.conversion_value,
          roas: metrics.platforms.meta_ads.roas,
          conversions: metrics.platforms.meta_ads.conversions,
          cpc: metrics.platforms.meta_ads.cpc,
          cvr: (metrics.platforms.meta_ads.conversions / metrics.platforms.meta_ads.clicks) * 100,
        });
      }

      if (metrics.platforms.ga4) {
        comparison.push({
          platform: 'Organic',
          spend: 0,
          revenue: 0,
          roas: 0,
          conversions: metrics.platforms.ga4.conversions,
          cpc: 0,
          cvr: metrics.platforms.ga4.conversion_rate,
        });
      }

      return comparison;
    } catch (error) {
      console.error('Error fetching platform comparison:', error);
      throw error;
    }
  },

  /**
   * Get unified daily performance
   */
  async getDailyPerformance(customerId: number, dateRange: string): Promise<DailyPerformance[]> {
    try {
      return await apiClient.get<DailyPerformance[]>(API_ENDPOINTS.UNIFIED_DAILY_PERFORMANCE, {
        params: { customer_id: customerId, date_range: dateRange },
      });
    } catch (error) {
      console.error('Error fetching unified daily performance:', error);
      throw error;
    }
  },
};
