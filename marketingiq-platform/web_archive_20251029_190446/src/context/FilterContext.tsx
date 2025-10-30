/**
 * Filter Context
 * Global state management for customer and filter selections
 */
import React, { createContext, useContext, useState, useCallback, ReactNode } from 'react';

export interface FilterState {
  customerId: number | null;
  dateRange: string;
  campaignType: string;
}

interface FilterContextType {
  filters: FilterState;
  setFilters: (filters: FilterState) => void;
  updateFilter: (key: keyof FilterState, value: any) => void;
  resetFilters: () => void;
}

const defaultFilters: FilterState = {
  customerId: null,
  dateRange: 'LAST_30_DAYS',
  campaignType: 'ALL'
};

const FilterContext = createContext<FilterContextType | undefined>(undefined);

export const FilterProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [filters, setFiltersState] = useState<FilterState>(defaultFilters);

  const setFilters = useCallback((newFilters: FilterState) => {
    setFiltersState(newFilters);
    // Persist to localStorage for page refreshes
    localStorage.setItem('marketingiq_filters', JSON.stringify(newFilters));
  }, []);

  const updateFilter = useCallback((key: keyof FilterState, value: any) => {
    setFiltersState(prev => {
      const newFilters = { ...prev, [key]: value };
      localStorage.setItem('marketingiq_filters', JSON.stringify(newFilters));
      return newFilters;
    });
  }, []);

  const resetFilters = useCallback(() => {
    setFiltersState(defaultFilters);
    localStorage.removeItem('marketingiq_filters');
  }, []);

  // Load filters from localStorage on mount
  React.useEffect(() => {
    const savedFilters = localStorage.getItem('marketingiq_filters');
    if (savedFilters) {
      try {
        const parsed = JSON.parse(savedFilters);
        setFiltersState(parsed);
      } catch (error) {
        console.error('Failed to parse saved filters:', error);
      }
    }
  }, []);

  return (
    <FilterContext.Provider value={{ filters, setFilters, updateFilter, resetFilters }}>
      {children}
    </FilterContext.Provider>
  );
};

// Custom hook to use filter context
export const useFilters = (): FilterContextType => {
  const context = useContext(FilterContext);
  if (!context) {
    throw new Error('useFilters must be used within a FilterProvider');
  }
  return context;
};

export default FilterContext;