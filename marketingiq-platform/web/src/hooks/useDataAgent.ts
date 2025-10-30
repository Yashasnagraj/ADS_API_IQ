import { useState, useEffect, useCallback } from 'react';
import { useFilters, buildFilterQueryParams } from '../context/FilterContext';
import apiClient from '../config/api';

/**
 * Generic hook state interface
 */
interface UseDataState<T> {
  data: T | null;
  loading: boolean;
  error: string | null;
  refetch: () => void;
}

/**
 * Campaign data interface
 */
export interface Campaign {
  campaign_id: string;
  campaign_name: string;
  status: string;
  budget: number;
  budget_used: number;
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
  ctr: number;
  cpc: number;
  conversion_rate: number;
  roas: number;
  campaign_type?: string;
}

/**
 * Ad Group data interface
 */
export interface AdGroup {
  adgroup_id: string;
  adgroup_name: string;
  campaign_id: string;
  campaign_name: string;
  status: string;
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
  ctr: number;
  cpc: number;
}

/**
 * Keyword data interface
 */
export interface Keyword {
  keyword_id: string;
  keyword_text: string;
  adgroup_id: string;
  adgroup_name: string;
  match_type: string;
  quality_score: number;
  status: string;
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
  ctr: number;
  cpc: number;
  avg_position: number;
}

/**
 * Search Term data interface
 */
export interface SearchTerm {
  search_term: string;
  keyword_text: string;
  match_type: string;
  impressions: number;
  clicks: number;
  cost: number;
  conversions: number;
  ctr: number;
  cpc: number;
  conversion_rate: number;
}

/**
 * ML Features data interface
 */
export interface MLFeature {
  entity_id: string;
  entity_name: string;
  entity_type: string;
  feature_name: string;
  feature_value: number;
  importance_score: number;
}

/**
 * Hook to fetch campaigns with filters
 */
export const useCampaigns = (options?: { includePaused?: boolean }): UseDataState<Campaign[]> => {
  const { filters } = useFilters();
  const [data, setData] = useState<Campaign[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!filters.customerId) {
      setData(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const params = buildFilterQueryParams(filters);
      if (options?.includePaused !== undefined) {
        params.include_paused = options.includePaused.toString();
      }

      const response = await apiClient.get('/campaigns', { params });
      setData(response.data || []);
    } catch (err: any) {
      console.error('Error fetching campaigns:', err);
      setError(err.message || 'Failed to fetch campaigns');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [filters, options?.includePaused]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

/**
 * Hook to fetch ad groups with filters
 */
export const useAdGroups = (campaignIds?: string[]): UseDataState<AdGroup[]> => {
  const { filters } = useFilters();
  const [data, setData] = useState<AdGroup[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!filters.customerId) {
      setData(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const params = buildFilterQueryParams(filters);
      if (campaignIds && campaignIds.length > 0) {
        params.campaign_ids = campaignIds.join(',');
      }

      const response = await apiClient.get('/adgroups', { params });
      setData(response.data || []);
    } catch (err: any) {
      console.error('Error fetching ad groups:', err);
      setError(err.message || 'Failed to fetch ad groups');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [filters, campaignIds]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

/**
 * Hook to fetch keywords with filters
 */
export const useKeywords = (options?: {
  adGroupIds?: string[];
  minImpressions?: number;
}): UseDataState<Keyword[]> => {
  const { filters } = useFilters();
  const [data, setData] = useState<Keyword[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!filters.customerId) {
      setData(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const params = buildFilterQueryParams(filters);
      if (options?.adGroupIds && options.adGroupIds.length > 0) {
        params.adgroup_ids = options.adGroupIds.join(',');
      }
      if (options?.minImpressions) {
        params.min_impressions = options.minImpressions.toString();
      }

      const response = await apiClient.get('/keywords', { params });
      setData(response.data || []);
    } catch (err: any) {
      console.error('Error fetching keywords:', err);
      setError(err.message || 'Failed to fetch keywords');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [filters, options?.adGroupIds, options?.minImpressions]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

/**
 * Hook to fetch search terms with filters
 */
export const useSearchTerms = (): UseDataState<SearchTerm[]> => {
  const { filters } = useFilters();
  const [data, setData] = useState<SearchTerm[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!filters.customerId) {
      setData(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const params = buildFilterQueryParams(filters);
      const response = await apiClient.get('/search-terms', { params });
      setData(response.data || []);
    } catch (err: any) {
      console.error('Error fetching search terms:', err);
      setError(err.message || 'Failed to fetch search terms');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [filters]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

/**
 * Hook to fetch ML features with filters
 */
export const useMLFeatures = (entityType?: 'campaign' | 'keyword' | 'adgroup'): UseDataState<MLFeature[]> => {
  const { filters } = useFilters();
  const [data, setData] = useState<MLFeature[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!filters.customerId) {
      setData(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const params = buildFilterQueryParams(filters);
      if (entityType) {
        params.entity_type = entityType;
      }

      const response = await apiClient.get('/ml-features', { params });
      setData(response.data || []);
    } catch (err: any) {
      console.error('Error fetching ML features:', err);
      setError(err.message || 'Failed to fetch ML features');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [filters, entityType]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};

/**
 * Hook to fetch campaign budget data
 */
export const useCampaignBudgets = (campaignIds?: string[]): UseDataState<any[]> => {
  const { filters } = useFilters();
  const [data, setData] = useState<any[] | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    if (!filters.customerId) {
      setData(null);
      setLoading(false);
      return;
    }

    try {
      setLoading(true);
      setError(null);

      const params = buildFilterQueryParams(filters);
      if (campaignIds && campaignIds.length > 0) {
        params.campaign_ids = campaignIds.join(',');
      }

      const response = await apiClient.get('/campaigns/budgets', { params });
      setData(response.data || []);
    } catch (err: any) {
      console.error('Error fetching campaign budgets:', err);
      setError(err.message || 'Failed to fetch campaign budgets');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [filters, campaignIds]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return { data, loading, error, refetch: fetchData };
};
