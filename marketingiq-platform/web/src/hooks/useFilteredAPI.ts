/**
 * Custom hook for making filtered API calls
 * Automatically includes customer_id and other filters in API requests
 */
import { useState, useEffect, useCallback } from 'react';
import axios, { AxiosRequestConfig } from 'axios';
import { useFilters } from '../context/FilterContext';
import API_CONFIG from '../config/api';

interface UseFilteredAPIOptions {
  endpoint: string;
  params?: Record<string, any>;
  autoFetch?: boolean;
  dependencies?: any[];
}

export const useFilteredAPI = <T = any>({
  endpoint,
  params = {},
  autoFetch = true,
  dependencies = []
}: UseFilteredAPIOptions) => {
  const { filters } = useFilters();
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(autoFetch);
  const [error, setError] = useState<Error | null>(null);

  const fetchData = useCallback(async (additionalParams: Record<string, any> = {}) => {
    setLoading(true);
    setError(null);

    try {
      // Build query params with filters
      const queryParams: Record<string, any> = {
        ...params,
        ...additionalParams
      };

      // Add customer_id if present
      if (filters.customerId) {
        queryParams.customer_id = filters.customerId;
      }

      // Add date range if not ALL_TIME
      if (filters.dateRange && filters.dateRange !== 'ALL_TIME') {
        queryParams.date_range = filters.dateRange;
      }

      // Add campaign type filter if not ALL
      if (filters.campaignType && filters.campaignType !== 'ALL') {
        queryParams.campaign_type = filters.campaignType;
      }

      const config: AxiosRequestConfig = {
        params: queryParams,
        timeout: API_CONFIG.TIMEOUT
      };

      const response = await axios.get(`${API_CONFIG.BASE_URL}${endpoint}`, config);
      setData(response.data);
      return response.data;
    } catch (err: any) {
      const error = err.response?.data?.message || err.message || 'An error occurred';
      setError(new Error(error));
      console.error(`API Error [${endpoint}]:`, error);
      return null;
    } finally {
      setLoading(false);
    }
  }, [endpoint, params, filters, ...dependencies]);

  useEffect(() => {
    if (autoFetch && filters.customerId !== null) {
      fetchData();
    }
  }, [autoFetch, filters.customerId, filters.dateRange, filters.campaignType, ...dependencies]);

  const refetch = useCallback((additionalParams?: Record<string, any>) => {
    return fetchData(additionalParams);
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch
  };
};

// Helper hooks for common API endpoints (using warehouse data)

export const useCampaigns = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/warehouse/campaigns', // Read from warehouse database
    params: additionalParams,
    autoFetch: true
  });
};

export const useKeywords = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/warehouse/keywords', // Read from warehouse database
    params: additionalParams,
    autoFetch: true
  });
};

export const useSearchTerms = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/search-terms', // TODO: Create /warehouse/search-terms endpoint
    params: additionalParams,
    autoFetch: true
  });
};

export const useMetricsSummary = () => {
  return useFilteredAPI<any>({
    endpoint: '/warehouse/metrics/summary', // Read from warehouse database
    autoFetch: true
  });
};

export const useAdGroups = (campaignId?: string, additionalParams?: Record<string, any>) => {
  const params = campaignId ? { campaign_id: campaignId, ...additionalParams } : additionalParams;
  return useFilteredAPI<any>({
    endpoint: '/warehouse/ad-groups', // Read from warehouse database
    params,
    autoFetch: true,
    dependencies: [campaignId]
  });
};

export const useInsightsSummary = () => {
  return useFilteredAPI<any>({
    endpoint: '/insights/summary',
    autoFetch: true
  });
};

export const useForecastScenarios = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/forecasts/scenarios',
    params: additionalParams,
    autoFetch: true
  });
};

export const useAlerts = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/alerts',
    params: additionalParams,
    autoFetch: true
  });
};

export const useThresholds = () => {
  return useFilteredAPI<any>({
    endpoint: '/alerts/thresholds',
    autoFetch: true
  });
};

export const useAnomalies = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/insights/anomalies',
    params: additionalParams,
    autoFetch: true
  });
};

export const useCTRForecast = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/forecasts/ctr',
    params: additionalParams,
    autoFetch: true
  });
};

export const useSpendForecast = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/forecasts/spend',
    params: additionalParams,
    autoFetch: true
  });
};

export const useKeywordOptimization = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/optimization/keywords',
    params: additionalParams,
    autoFetch: true
  });
};

export const useBudgetOptimization = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/optimization/budget',
    params: additionalParams,
    autoFetch: true
  });
};

// E-commerce hooks
export const useEcommerceOverview = () => {
  return useFilteredAPI<any>({
    endpoint: '/ecommerce/overview',
    autoFetch: true
  });
};

export const useEcommerceKPIs = () => {
  return useFilteredAPI<any>({
    endpoint: '/ecommerce/kpis',
    autoFetch: true
  });
};

export const useEcommerceFunnel = () => {
  return useFilteredAPI<any>({
    endpoint: '/ecommerce/funnel',
    autoFetch: true
  });
};

export const useChannelPerformance = () => {
  return useFilteredAPI<any>({
    endpoint: '/ecommerce/channels',
    autoFetch: true
  });
};

export const useProductPerformance = () => {
  return useFilteredAPI<any>({
    endpoint: '/ecommerce/products',
    autoFetch: true
  });
};

export const useCustomerSegmentation = () => {
  return useFilteredAPI<any>({
    endpoint: '/ecommerce/segments',
    autoFetch: true
  });
};

export const useRevenueForecast = () => {
  return useFilteredAPI<any>({
    endpoint: '/ecommerce/forecast',
    autoFetch: true
  });
};

export const useEcommerceAnomalies = () => {
  return useFilteredAPI<any>({
    endpoint: '/ecommerce/anomalies',
    autoFetch: true
  });
};

// ==============================================================================
// GA4 HOOKS (Google Analytics 4 Integration)
// ==============================================================================

// GA4 Integration Status
export const useGA4Status = () => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/integration/status',
    autoFetch: true
  });
};

// GA4 Properties
export const useGA4Properties = () => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/properties',
    autoFetch: true
  });
};

// GA4 Sessions
export const useGA4Sessions = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/sessions',
    params: additionalParams,
    autoFetch: true
  });
};

// GA4 Behavior by Source
export const useGA4BehaviorBySource = () => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/sessions/by-source',
    autoFetch: true
  });
};

// GA4 Behavior by Campaign
export const useGA4BehaviorByCampaign = () => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/sessions/by-campaign',
    autoFetch: true
  });
};

// GA4 Events
export const useGA4Events = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/events',
    params: additionalParams,
    autoFetch: true
  });
};

// GA4 Top Events
export const useGA4TopEvents = (limit: number = 10) => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/events/top',
    params: { limit },
    autoFetch: true
  });
};

// GA4 Conversion Paths (Multi-Touch Attribution)
export const useGA4ConversionPaths = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/conversion-paths',
    params: additionalParams,
    autoFetch: true
  });
};

// GA4 Attribution Models
export const useGA4Attribution = () => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/attribution',
    autoFetch: true
  });
};

// GA4 Audience Insights
export const useGA4AudienceInsights = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/audience-insights',
    params: additionalParams,
    autoFetch: true
  });
};

// GA4 Device Performance
export const useGA4DevicePerformance = () => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/audience-insights/devices',
    autoFetch: true
  });
};

// GA4 Country Breakdown
export const useGA4CountryBreakdown = (limit: number = 10) => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/audience-insights/countries',
    params: { limit },
    autoFetch: true
  });
};

// ⭐ MOST IMPORTANT: Campaign Enrichment (Google Ads + GA4 Combined)
export const useGA4CampaignEnrichment = () => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/campaign-enrichment',
    autoFetch: true
  });
};

// Keyword Enrichment (Google Ads + GA4 Combined)
export const useGA4KeywordEnrichment = () => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/keyword-enrichment',
    autoFetch: true
  });
};

// Ad Group Enrichment (Google Ads + GA4 Combined)
export const useGA4AdGroupEnrichment = () => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/adgroup-enrichment',
    autoFetch: true
  });
};

// GA4 User Behavior by Campaign
export const useGA4UserBehaviorByCampaign = (campaignId?: number) => {
  return useFilteredAPI<any>({
    endpoint: '/ga4/user-behavior',
    params: campaignId ? { campaign_id: campaignId } : {},
    autoFetch: !!campaignId,
    dependencies: [campaignId]
  });
};

export default useFilteredAPI;