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

// Helper hooks for common API endpoints

export const useCampaigns = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/campaigns',
    params: additionalParams,
    autoFetch: true
  });
};

export const useKeywords = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/keywords',
    params: additionalParams,
    autoFetch: true
  });
};

export const useSearchTerms = (additionalParams?: Record<string, any>) => {
  return useFilteredAPI<any>({
    endpoint: '/search-terms',
    params: additionalParams,
    autoFetch: true
  });
};

export const useMetricsSummary = () => {
  return useFilteredAPI<any>({
    endpoint: '/metrics/summary',
    autoFetch: true
  });
};

export const useAdGroups = (campaignId?: number) => {
  return useFilteredAPI<any>({
    endpoint: campaignId ? `/campaigns/${campaignId}/adgroups` : '/adgroups',
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

export default useFilteredAPI;