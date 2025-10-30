import { useState, useEffect, useCallback } from 'react';
import { useFilters } from '../context/FilterContext';
import apiClient from '../services/apiClient';

export interface UseAgentDataOptions {
  endpoint: string;
  enabled?: boolean;
  dependencies?: any[];
}

export interface UseAgentDataResult<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => Promise<void>;
}

/**
 * Custom hook for fetching customer-filtered agent data
 * Automatically handles:
 * - Customer ID filtering
 * - Date range filtering
 * - Loading states
 * - Error handling
 * - Auto-refresh on filter changes
 *
 * @param endpoint - API endpoint path (e.g., '/warehouse/data/campaigns')
 * @param enabled - Whether to fetch data (default: true)
 * @param dependencies - Additional dependencies for refetching
 *
 * @example
 * const { data, loading, error, refetch } = useAgentData<Campaign[]>({
 *   endpoint: '/warehouse/data/campaigns'
 * });
 */
export function useAgentData<T = any>({
  endpoint,
  enabled = true,
  dependencies = [],
}: UseAgentDataOptions): UseAgentDataResult<T> {
  const { filters } = useFilters();
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!enabled) {
      setLoading(false);
      return;
    }

    // Ensure we have a customer_id
    if (!filters.customerId) {
      setError('No customer selected');
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const response = await apiClient.get<T>(endpoint, {
        params: {
          customer_id: filters.customerId,
          date_range: filters.dateRange || 'last_30d',
          platform: filters.platform,
          campaign_type: filters.campaignType,
        },
      });

      setData(response);
    } catch (err: any) {
      console.error(`Error fetching data from ${endpoint}:`, err);
      setError(err.message || 'Failed to fetch data');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [endpoint, enabled, filters.customerId, filters.dateRange, filters.platform, filters.campaignType, ...dependencies]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
}

/**
 * Hook for fetching multi-source data (Meta + Google Ads + GA4)
 * Automatically handles Emcee Sons (customer_id=1) with unified data
 * and other customers with Google Ads only
 *
 * @example
 * const { data, loading } = useUnifiedAgentData<UnifiedMetrics>({
 *   endpoints: {
 *     meta: '/warehouse/meta/insights/summary',
 *     google: '/warehouse/google/campaigns/summary',
 *     ga4: '/warehouse/ga4/summary'
 *   }
 * });
 */
export function useUnifiedAgentData<T = any>({
  endpoints,
  enabled = true,
}: {
  endpoints: {
    meta?: string;
    google?: string;
    ga4?: string;
  };
  enabled?: boolean;
}): UseAgentDataResult<T> {
  const { filters } = useFilters();
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchUnifiedData = useCallback(async () => {
    if (!enabled || !filters.customerId) {
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const params = {
        customer_id: filters.customerId,
        date_range: filters.dateRange || 'last_30d',
      };

      // For Emcee Sons (customer_id=1), fetch from all sources
      if (Number(filters.customerId) === 1) {
        const requests = [];

        if (endpoints.meta) requests.push(apiClient.get(endpoints.meta, { params }));
        if (endpoints.google) requests.push(apiClient.get(endpoints.google, { params }));
        if (endpoints.ga4) requests.push(apiClient.get(endpoints.ga4, { params }));

        const responses = await Promise.all(requests);

        // Merge data from all sources
        const mergedData = responses.reduce((acc, response) => ({
          ...acc,
          ...response,
        }), {});

        setData(mergedData as T);
      } else {
        // For other customers, only fetch Google Ads data
        if (endpoints.google) {
          const response = await apiClient.get<T>(endpoints.google, { params });
          setData(response);
        } else {
          setError('Google Ads endpoint not configured');
        }
      }
    } catch (err: any) {
      console.error('Error fetching unified data:', err);
      setError(err.message || 'Failed to fetch unified data');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [endpoints, enabled, filters.customerId, filters.dateRange]);

  useEffect(() => {
    fetchUnifiedData();
  }, [fetchUnifiedData]);

  return {
    data,
    loading,
    error,
    refetch: fetchUnifiedData,
  };
}

export default useAgentData;
