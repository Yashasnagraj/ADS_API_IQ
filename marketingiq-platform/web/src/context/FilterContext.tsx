import React, { createContext, useContext, useState, useEffect, ReactNode } from 'react';

/**
 * Filter state interface for global dashboard filtering
 */
export interface FilterState {
  customerId: string | null; // Selected customer ID
  dateRange: string; // Date range: LAST_7_DAYS, LAST_30_DAYS, LAST_90_DAYS, LAST_6_MONTHS, LAST_YEAR, THIS_MONTH, LAST_MONTH, THIS_YEAR, ALL_TIME, CUSTOM
  startDate: string | null; // Custom start date (YYYY-MM-DD)
  endDate: string | null; // Custom end date (YYYY-MM-DD)
  campaignType: string; // Campaign type filter: ALL, SEARCH, DISPLAY, SHOPPING, VIDEO
  platform: string; // Platform filter: ALL, GOOGLE_ADS, META_ADS, GA4
}

/**
 * Filter context interface
 */
interface FilterContextType {
  filters: FilterState;
  setFilters: (filters: Partial<FilterState>) => void;
  resetFilters: () => void;
  isLoading: boolean;
}

/**
 * Default filter state
 */
const defaultFilters: FilterState = {
  customerId: null,
  dateRange: 'LAST_30_DAYS',
  startDate: null,
  endDate: null,
  campaignType: 'ALL',
  platform: 'ALL',
};

// Create context
const FilterContext = createContext<FilterContextType | undefined>(undefined);

/**
 * Filter Provider Props
 */
interface FilterProviderProps {
  children: ReactNode;
}

/**
 * Filter Provider Component
 * Provides global filter state to all dashboards
 */
export const FilterProvider: React.FC<FilterProviderProps> = ({ children }) => {
  const [filters, setFiltersState] = useState<FilterState>(defaultFilters);
  const [isLoading, setIsLoading] = useState(false);

  // Load filters from localStorage on mount
  useEffect(() => {
    try {
      const savedFilters = localStorage.getItem('dashboardFilters');
      if (savedFilters) {
        const parsed = JSON.parse(savedFilters);
        setFiltersState({ ...defaultFilters, ...parsed });
      }
    } catch (error) {
      console.error('Error loading saved filters:', error);
    }
  }, []);

  // Save filters to localStorage whenever they change
  useEffect(() => {
    try {
      localStorage.setItem('dashboardFilters', JSON.stringify(filters));
    } catch (error) {
      console.error('Error saving filters:', error);
    }
  }, [filters]);

  /**
   * Update filters (partial update)
   */
  const setFilters = (newFilters: Partial<FilterState>) => {
    setIsLoading(true);
    setFiltersState((prev) => ({
      ...prev,
      ...newFilters,
    }));
    // Simulate loading delay for smooth transitions
    setTimeout(() => setIsLoading(false), 300);
  };

  /**
   * Reset filters to default values
   */
  const resetFilters = () => {
    setFiltersState(defaultFilters);
    localStorage.removeItem('dashboardFilters');
  };

  const value: FilterContextType = {
    filters,
    setFilters,
    resetFilters,
    isLoading,
  };

  return <FilterContext.Provider value={value}>{children}</FilterContext.Provider>;
};

/**
 * Hook to use filter context
 * Must be used within FilterProvider
 */
export const useFilters = (): FilterContextType => {
  const context = useContext(FilterContext);
  if (context === undefined) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};

/**
 * Helper: Get date range as start/end dates
 */
export const getDateRangeValues = (filters: FilterState): { startDate: string; endDate: string } => {
  const today = new Date();
  let startDate: Date;
  let endDate: Date = today;

  // If custom date range, use provided dates
  if (filters.dateRange === 'CUSTOM' && filters.startDate && filters.endDate) {
    return {
      startDate: filters.startDate,
      endDate: filters.endDate,
    };
  }

  // Calculate date range based on preset
  switch (filters.dateRange) {
    case 'LAST_7_DAYS':
      startDate = new Date(today);
      startDate.setDate(today.getDate() - 7);
      break;
    case 'LAST_30_DAYS':
      startDate = new Date(today);
      startDate.setDate(today.getDate() - 30);
      break;
    case 'LAST_90_DAYS':
      startDate = new Date(today);
      startDate.setDate(today.getDate() - 90);
      break;
    case 'LAST_6_MONTHS':
      startDate = new Date(today);
      startDate.setMonth(today.getMonth() - 6);
      break;
    case 'LAST_YEAR':
      startDate = new Date(today);
      startDate.setFullYear(today.getFullYear() - 1);
      break;
    case 'ALL_TIME':
      // Set to a very early date (e.g., 10 years ago)
      // In production, this should query the earliest data point from DB
      startDate = new Date(today);
      startDate.setFullYear(today.getFullYear() - 10);
      break;
    case 'THIS_MONTH':
      startDate = new Date(today.getFullYear(), today.getMonth(), 1);
      break;
    case 'LAST_MONTH':
      startDate = new Date(today.getFullYear(), today.getMonth() - 1, 1);
      endDate = new Date(today.getFullYear(), today.getMonth(), 0);
      break;
    case 'THIS_YEAR':
      startDate = new Date(today.getFullYear(), 0, 1); // January 1st of current year
      break;
    default:
      startDate = new Date(today);
      startDate.setDate(today.getDate() - 30);
  }

  return {
    startDate: startDate.toISOString().split('T')[0],
    endDate: endDate.toISOString().split('T')[0],
  };
};

/**
 * Helper: Build query parameters from filters
 */
export const buildFilterQueryParams = (filters: FilterState): Record<string, string> => {
  const params: Record<string, string> = {};

  if (filters.customerId) {
    params.customer_id = filters.customerId;
  }

  const { startDate, endDate } = getDateRangeValues(filters);
  params.start_date = startDate;
  params.end_date = endDate;

  if (filters.campaignType && filters.campaignType !== 'ALL') {
    params.campaign_type = filters.campaignType;
  }

  if (filters.platform && filters.platform !== 'ALL') {
    params.platform = filters.platform;
  }

  return params;
};
