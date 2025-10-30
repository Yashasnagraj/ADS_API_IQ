/**
 * Global Filter Bar Component
 * Provides customer, date range, and campaign type filtering across all dashboards
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Paper,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  SelectChangeEvent,
  Typography,
  Chip,
  Stack,
  Divider,
  IconButton,
  Collapse
} from '@mui/material';
import {
  FilterList as FilterIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon
} from '@mui/icons-material';
import axios from 'axios';
import API_CONFIG from '../../config/api';

// Filter state interface
export interface FilterState {
  customerId: number | null;
  dateRange: string;
  campaignType: string;
}

// Customer interface
interface Customer {
  customer_id: number;
  customer_name: string;
  campaigns_count: number;
}

interface GlobalFilterBarProps {
  onFilterChange: (filters: FilterState) => void;
  initialFilters?: Partial<FilterState>;
  compact?: boolean;
}


const GlobalFilterBar: React.FC<GlobalFilterBarProps> = ({
  onFilterChange,
  initialFilters,
  compact = false
}) => {
  const [expanded, setExpanded] = useState(!compact);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);

  const [filters, setFilters] = useState<FilterState>({
    customerId: initialFilters?.customerId || null,
    dateRange: initialFilters?.dateRange || 'LAST_30_DAYS',
    campaignType: initialFilters?.campaignType || 'ALL'
  });

  // Fetch customers on mount
  useEffect(() => {
    fetchCustomers();
  }, []);

  // Set default customer if none selected
  useEffect(() => {
    if (customers.length > 0 && filters.customerId === null) {
      const defaultCustomer = customers[0];
      const newFilters = { ...filters, customerId: defaultCustomer.customer_id };
      setFilters(newFilters);
      onFilterChange(newFilters);
    }
  }, [customers]);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_CONFIG.BASE_URL}/customers`);
      if (response.data && response.data.customers) {
        setCustomers(response.data.customers);
      }
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCustomerChange = (event: SelectChangeEvent<number>) => {
    const newFilters = { ...filters, customerId: Number(event.target.value) };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleDateRangeChange = (event: SelectChangeEvent<string>) => {
    const newFilters = { ...filters, dateRange: event.target.value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const handleCampaignTypeChange = (event: SelectChangeEvent<string>) => {
    const newFilters = { ...filters, campaignType: event.target.value };
    setFilters(newFilters);
    onFilterChange(newFilters);
  };

  const getSelectedCustomerName = () => {
    const customer = customers.find(c => c.customer_id === filters.customerId);
    return customer ? customer.customer_name : 'Select Customer';
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.customerId) count++;
    if (filters.dateRange !== 'ALL_TIME') count++;
    if (filters.campaignType !== 'ALL') count++;
    return count;
  };

  return (
    <Paper
      elevation={2}
      sx={{
        position: 'sticky',
        top: 0,
        zIndex: 1000,
        backgroundColor: 'background.paper',
        borderRadius: 2,
        overflow: 'hidden',
        mb: 3
      }}
    >
      {/* Header */}
      <Box
        sx={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          p: 2,
          background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
          color: 'white'
        }}
      >
        <Stack direction="row" spacing={2} alignItems="center">
          <FilterIcon />
          <Typography variant="h6" fontWeight={600}>
            Filters
          </Typography>
          {getActiveFiltersCount() > 0 && (
            <Chip
              label={`${getActiveFiltersCount()} active`}
              size="small"
              sx={{
                backgroundColor: 'rgba(255,255,255,0.2)',
                color: 'white',
                fontWeight: 600
              }}
            />
          )}
        </Stack>

        {compact && (
          <IconButton
            onClick={() => setExpanded(!expanded)}
            sx={{ color: 'white' }}
            size="small"
          >
            {expanded ? <ExpandLessIcon /> : <ExpandMoreIcon />}
          </IconButton>
        )}
      </Box>

      <Collapse in={expanded} timeout="auto">
        <Box sx={{ p: 3 }}>
          <Stack
            direction={{ xs: 'column', sm: 'row' }}
            spacing={3}
            divider={<Divider orientation="vertical" flexItem />}
          >
            {/* Customer Selector */}
            <FormControl fullWidth size="small">
              <InputLabel id="customer-select-label">Customer</InputLabel>
              <Select
                labelId="customer-select-label"
                id="customer-select"
                value={filters.customerId && customers.some(c => c.customer_id === filters.customerId) ? filters.customerId : ''}
                label="Customer"
                onChange={handleCustomerChange}
                disabled={loading}
              >
                {customers.map((customer) => (
                  <MenuItem
                    key={customer.customer_id}
                    value={customer.customer_id}
                  >
                    <Stack direction="row" spacing={1} alignItems="center" width="100%">
                      <Typography variant="body2" flex={1}>
                        {customer.customer_name}
                      </Typography>
                      <Chip
                        label={`${customer.campaigns_count} campaigns`}
                        size="small"
                        variant="outlined"
                      />
                    </Stack>
                  </MenuItem>
                ))}
              </Select>
            </FormControl>

            {/* Date Range Selector */}
            <FormControl fullWidth size="small">
              <InputLabel id="date-range-label">Date Range</InputLabel>
              <Select
                labelId="date-range-label"
                id="date-range-select"
                value={filters.dateRange}
                label="Date Range"
                onChange={handleDateRangeChange}
              >
                <MenuItem value="LAST_7_DAYS">Last 7 Days</MenuItem>
                <MenuItem value="LAST_30_DAYS">Last 30 Days</MenuItem>
                <MenuItem value="LAST_90_DAYS">Last 90 Days</MenuItem>
                <MenuItem value="THIS_MONTH">This Month</MenuItem>
                <MenuItem value="LAST_MONTH">Last Month</MenuItem>
                <MenuItem value="THIS_YEAR">This Year</MenuItem>
                <MenuItem value="ALL_TIME">All Time</MenuItem>
              </Select>
            </FormControl>

            {/* Campaign Type Filter */}
            <FormControl fullWidth size="small">
              <InputLabel id="campaign-type-label">Campaign Type</InputLabel>
              <Select
                labelId="campaign-type-label"
                id="campaign-type-select"
                value={filters.campaignType}
                label="Campaign Type"
                onChange={handleCampaignTypeChange}
              >
                <MenuItem value="ALL">All Campaigns</MenuItem>
                <MenuItem value="SEARCH">Search</MenuItem>
                <MenuItem value="DISPLAY">Display</MenuItem>
                <MenuItem value="SHOPPING">Shopping</MenuItem>
                <MenuItem value="VIDEO">Video</MenuItem>
                <MenuItem value="PERFORMANCE_MAX">Performance Max</MenuItem>
              </Select>
            </FormControl>
          </Stack>

          {/* Active Filters Summary */}
          {filters.customerId && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Viewing data for{' '}
                <strong>{getSelectedCustomerName()}</strong>
                {filters.dateRange !== 'ALL_TIME' && (
                  <>, {filters.dateRange.replace(/_/g, ' ').toLowerCase()}</>
                )}
                {filters.campaignType !== 'ALL' && (
                  <>, {filters.campaignType.toLowerCase()} campaigns only</>
                )}
              </Typography>
            </Box>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};

export default GlobalFilterBar;