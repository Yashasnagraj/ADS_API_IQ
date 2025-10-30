/**
 * Global Filter Bar Component
 * Provides customer, date range, and campaign type filtering across all dashboards
 * Integrated with FilterContext for global state management
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
  Collapse,
} from '@mui/material';
import {
  FilterList as FilterIcon,
  ExpandMore as ExpandMoreIcon,
  ExpandLess as ExpandLessIcon,
} from '@mui/icons-material';
import { useFilters } from '../../context/FilterContext';
import { customerService } from '../../services/customerService';
import { Customer } from '../../types';

interface GlobalFilterBarProps {
  compact?: boolean;
  showPlatformFilter?: boolean;
  showCampaignTypeFilter?: boolean;
}

export const GlobalFilterBar: React.FC<GlobalFilterBarProps> = ({
  compact = false,
  showPlatformFilter = false,
  showCampaignTypeFilter = true,
}) => {
  const { filters, setFilters } = useFilters();
  const [expanded, setExpanded] = useState(!compact);
  const [customers, setCustomers] = useState<Customer[]>([]);
  const [loading, setLoading] = useState(false);

  // Fetch customers on mount
  useEffect(() => {
    fetchCustomers();
  }, []);

  // Set default customer if none selected
  useEffect(() => {
    if (customers.length > 0 && !filters.customerId) {
      const defaultCustomer = customers[0];
      console.log('Setting default customer:', defaultCustomer.customer_name, defaultCustomer.customer_id);
      setFilters({ customerId: String(defaultCustomer.customer_id) });
    }
  }, [customers, filters.customerId, setFilters]);

  const fetchCustomers = async () => {
    setLoading(true);
    try {
      const data = await customerService.getCustomers();
      setCustomers(data);
    } catch (error) {
      console.error('Failed to fetch customers:', error);
    } finally {
      setLoading(false);
    }
  };

  const handleCustomerChange = (event: SelectChangeEvent<string>) => {
    setFilters({ customerId: event.target.value });
  };

  const handleDateRangeChange = (event: SelectChangeEvent<string>) => {
    setFilters({ dateRange: event.target.value });
  };

  const handleCampaignTypeChange = (event: SelectChangeEvent<string>) => {
    setFilters({ campaignType: event.target.value });
  };

  const handlePlatformChange = (event: SelectChangeEvent<string>) => {
    setFilters({ platform: event.target.value });
  };

  const getSelectedCustomerName = () => {
    const customer = customers.find((c) => String(c.customer_id) === filters.customerId);
    return customer ? customer.customer_name : 'Select Customer';
  };

  const getActiveFiltersCount = () => {
    let count = 0;
    if (filters.customerId) count++;
    if (filters.dateRange !== 'LAST_30_DAYS') count++;
    if (filters.campaignType !== 'ALL') count++;
    if (filters.platform !== 'ALL') count++;
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
        mb: 3,
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
          color: 'white',
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
                fontWeight: 600,
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
                value={filters.customerId || ''}
                label="Customer"
                onChange={handleCustomerChange}
                disabled={loading}
              >
                {customers.map((customer) => (
                  <MenuItem key={customer.customer_id} value={String(customer.customer_id)}>
                    <Stack direction="row" spacing={1} alignItems="center" width="100%">
                      <Typography variant="body2" flex={1}>
                        {customer.customer_name}
                      </Typography>
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
              </Select>
            </FormControl>

            {/* Campaign Type Filter */}
            {showCampaignTypeFilter && (
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
            )}

            {/* Platform Filter */}
            {showPlatformFilter && (
              <FormControl fullWidth size="small">
                <InputLabel id="platform-label">Platform</InputLabel>
                <Select
                  labelId="platform-label"
                  id="platform-select"
                  value={filters.platform}
                  label="Platform"
                  onChange={handlePlatformChange}
                >
                  <MenuItem value="ALL">All Platforms</MenuItem>
                  <MenuItem value="google_ads">Google Ads</MenuItem>
                  <MenuItem value="meta_ads">Meta Ads</MenuItem>
                  <MenuItem value="ga4">Google Analytics 4</MenuItem>
                </Select>
              </FormControl>
            )}
          </Stack>

          {/* Active Filters Summary */}
          {filters.customerId && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="caption" color="text.secondary">
                Viewing data for <strong>{getSelectedCustomerName()}</strong>
                {filters.dateRange !== 'LAST_30_DAYS' && (
                  <>, {filters.dateRange.replace(/_/g, ' ').toLowerCase()}</>
                )}
                {filters.campaignType !== 'ALL' && (
                  <>, {filters.campaignType.toLowerCase()} campaigns only</>
                )}
                {filters.platform !== 'ALL' && (
                  <>, {filters.platform.replace(/_/g, ' ')} only</>
                )}
              </Typography>
            </Box>
          )}
        </Box>
      </Collapse>
    </Paper>
  );
};
