/**
 * Unified Dashboard with Real Filtered Data
 * Uses customer_id filter to show only selected customer's data
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  CircularProgress,
  Alert,
  useTheme,
  Chip,
  IconButton,
  Divider,
} from '@mui/material';
import {
  MonetizationOn,
  Campaign,
  TrendingUp,
  Speed,
  Refresh,
} from '@mui/icons-material';
import { useFilters } from '../../context/FilterContext';
import { useCampaigns, useMetricsSummary, useFilteredAPI } from '../../hooks/useFilteredAPI';
import AnimatedKPICard from '../common/AnimatedKPICard';
import {
  AreaChart,
  Area,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

const UnifiedDashboardFiltered: React.FC = () => {
  const theme = useTheme();
  const { filters } = useFilters();

  // Fetch data using filtered hooks
  const { data: metricsData, loading: metricsLoading, error: metricsError, refetch: refetchMetrics } = useMetricsSummary();
  const { data: campaignsData, loading: campaignsLoading, refetch: refetchCampaigns } = useCampaigns({ limit: 100 });
  const { data: timeseriesData, loading: timeseriesLoading } = useFilteredAPI({
    endpoint: '/metrics/timeseries',
    params: { days: 30, interval: 'daily' }
  });

  // Calculate derived metrics
  const totalRevenue = metricsData?.total_conversions * 100 || 0; // Placeholder: conversions * avg value
  const activeCampaigns = campaignsData?.campaigns?.filter((c: any) => c.status === 'ENABLED').length || 0;
  const totalCampaigns = campaignsData?.total || 0;
  const conversionRate = metricsData?.avg_conversion_rate * 100 || 0;
  const avgCPC = metricsData?.avg_cpc || 0;
  const totalImpressions = metricsData?.total_impressions || 0;
  const totalClicks = metricsData?.total_clicks || 0;
  const totalCost = metricsData?.total_cost || 0;
  const ctr = metricsData?.avg_ctr * 100 || 0;

  // Loading state
  if (!filters.customerId) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading customer data...</Typography>
      </Box>
    );
  }

  if (metricsLoading || campaignsLoading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading dashboard data...</Typography>
      </Box>
    );
  }

  if (metricsError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Error loading data: {metricsError.message}
        </Alert>
      </Box>
    );
  }

  // Prepare channel breakdown data
  const channelData = campaignsData?.campaigns?.reduce((acc: any, campaign: any) => {
    const channel = campaign.channel_type || 'UNKNOWN';
    if (!acc[channel]) {
      acc[channel] = { name: channel, value: 0, count: 0 };
    }
    acc[channel].count += 1;
    acc[channel].value += campaign.metrics?.cost || 0;
    return acc;
  }, {});

  const channelBreakdown = Object.values(channelData || {}) as Array<{ name: string; value: number; count: number }>;

  // Colors for pie chart
  const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'];

  // Refresh all data
  const handleRefresh = () => {
    refetchMetrics();
    refetchCampaigns();
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography variant="h4" fontWeight={700}>
          Dashboard Overview
        </Typography>
        <Box>
          <Chip
            label={`${filters.dateRange.replace(/_/g, ' ')}`}
            size="small"
            sx={{ mr: 1 }}
          />
          <IconButton onClick={handleRefresh} size="small">
            <Refresh />
          </IconButton>
        </Box>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <AnimatedKPICard
            title="Total Cost"
            value={totalCost}
            format="currency"
            icon={<MonetizationOn />}
            trend="up"
            trendValue={0}
            color="success"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <AnimatedKPICard
            title="Active Campaigns"
            value={activeCampaigns}
            format="number"
            icon={<Campaign />}
            trend="up"
            trendValue={0}
            color="primary"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <AnimatedKPICard
            title="CTR"
            value={ctr}
            format="percentage"
            icon={<TrendingUp />}
            trend="up"
            trendValue={0}
            color="info"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <AnimatedKPICard
            title="Avg. CPC"
            value={avgCPC}
            format="currency"
            icon={<Speed />}
            trend="down"
            trendValue={0}
            color="warning"
          />
        </Grid>
      </Grid>

      {/* Metrics Summary */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Performance Metrics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Impressions
                  </Typography>
                  <Typography variant="h6">
                    {totalImpressions.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Clicks
                  </Typography>
                  <Typography variant="h6">
                    {totalClicks.toLocaleString()}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Campaigns
                  </Typography>
                  <Typography variant="h6">
                    {totalCampaigns}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Keywords
                  </Typography>
                  <Typography variant="h6">
                    {metricsData?.keywords_count || 0}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom>
                Channel Breakdown
              </Typography>
              {channelBreakdown.length > 0 ? (
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={channelBreakdown}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={(entry) => `${entry.name} (${entry.count})`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="count"
                    >
                      {channelBreakdown.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" align="center">
                  No channel data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Performance Over Time */}
      {timeseriesData && timeseriesData.data_points && timeseriesData.data_points.length > 0 && (
        <Card sx={{ mb: 3 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom>
              Performance Over Time
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <AreaChart data={timeseriesData.data_points}>
                <defs>
                  <linearGradient id="colorClicks" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#6366f1" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#6366f1" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorCost" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#f59e0b" stopOpacity={0.8}/>
                    <stop offset="95%" stopColor="#f59e0b" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <RechartsTooltip />
                <Legend />
                <Area
                  type="monotone"
                  dataKey="clicks"
                  stroke="#6366f1"
                  fillOpacity={1}
                  fill="url(#colorClicks)"
                />
                <Area
                  type="monotone"
                  dataKey="cost"
                  stroke="#f59e0b"
                  fillOpacity={1}
                  fill="url(#colorCost)"
                />
              </AreaChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      )}

      {/* Campaign List */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom>
            Recent Campaigns
          </Typography>
          <Divider sx={{ mb: 2 }} />
          {campaignsData?.campaigns?.slice(0, 5).map((campaign: any) => (
            <Box
              key={campaign.campaign_id}
              sx={{
                p: 2,
                mb: 1,
                borderRadius: 1,
                backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)'
              }}
            >
              <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <Box>
                  <Typography variant="body1" fontWeight={600}>
                    {campaign.campaign_name}
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, mt: 0.5 }}>
                    <Chip label={campaign.status} size="small" color={campaign.status === 'ENABLED' ? 'success' : 'default'} />
                    <Chip label={campaign.channel_type} size="small" variant="outlined" />
                  </Box>
                </Box>
                <Box sx={{ textAlign: 'right' }}>
                  <Typography variant="body2" color="text.secondary">
                    Clicks: {campaign.metrics?.clicks || 0}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Cost: ₹{(campaign.metrics?.cost || 0).toFixed(2)}
                  </Typography>
                </Box>
              </Box>
            </Box>
          ))}
        </CardContent>
      </Card>
    </Box>
  );
};

export default UnifiedDashboardFiltered;