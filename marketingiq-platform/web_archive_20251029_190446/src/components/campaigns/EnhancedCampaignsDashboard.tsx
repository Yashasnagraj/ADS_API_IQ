/**
 * Enhanced Campaigns Dashboard with Real Filtered Data
 * Uses customer_id filter to show only selected customer's campaigns
 */
import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Chip,
  Button,
  IconButton,
  Alert,
  CircularProgress,
  useTheme,
  alpha,
  Avatar,
  Stack,
} from '@mui/material';
import {
  Campaign,
  MonetizationOn,
  Mouse,
  Visibility,
  ShoppingCart,
  Psychology,
  AttachMoney,
  Percent,
  ArrowUpward,
  ArrowDownward,
  Refresh,
  Download,
  Schedule,
} from '@mui/icons-material';
import { useFilters } from '../../context/FilterContext';
import { useCampaigns, useMetricsSummary, useFilteredAPI } from '../../hooks/useFilteredAPI';
import {
  ComposedChart,
  Area,
  Bar,
  Line,
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

const EnhancedCampaignsDashboard: React.FC = () => {
  const theme = useTheme();
  const { filters } = useFilters();

  // Fetch data using filtered hooks
  const { data: campaignsData, loading: campaignsLoading, error: campaignsError, refetch: refetchCampaigns } = useCampaigns({ limit: 100 });
  const { data: metricsData, loading: metricsLoading, refetch: refetchMetrics } = useMetricsSummary();
  const { data: timeseriesData, loading: timeseriesLoading } = useFilteredAPI({
    endpoint: '/metrics/timeseries',
    params: { days: 7, interval: 'daily' }
  });

  // Calculate metrics from real data
  const totalCost = metricsData?.total_cost || 0;
  const totalConversions = metricsData?.total_conversions || 0;
  const avgCTR = (metricsData?.avg_ctr || 0) * 100;
  const avgCPC = metricsData?.avg_cpc || 0;
  const totalImpressions = metricsData?.total_impressions || 0;
  const avgConversionRate = (metricsData?.avg_conversion_rate || 0) * 100;

  const activeCampaigns = campaignsData?.campaigns?.filter((c: any) => c.status === 'ENABLED').length || 0;
  const totalCampaigns = campaignsData?.total || 0;

  // Loading state
  if (!filters.customerId) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading customer data...</Typography>
      </Box>
    );
  }

  if (campaignsLoading || metricsLoading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading campaigns data...</Typography>
      </Box>
    );
  }

  if (campaignsError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Error loading campaigns: {campaignsError.message}
        </Alert>
      </Box>
    );
  }

  // Channel breakdown from real campaigns
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

  // Colors for charts
  const COLORS = ['#6366f1', '#8b5cf6', '#ec4899', '#f59e0b', '#10b981', '#3b82f6'];

  // KPI Cards data
  const kpiData = [
    {
      title: 'Total Cost',
      value: totalCost,
      format: 'currency' as const,
      icon: <MonetizationOn fontSize="small" />,
      color: 'success' as const,
    },
    {
      title: 'Conversions',
      value: totalConversions,
      format: 'number' as const,
      icon: <ShoppingCart fontSize="small" />,
      color: 'primary' as const,
    },
    {
      title: 'CTR',
      value: avgCTR,
      format: 'percentage' as const,
      icon: <Mouse fontSize="small" />,
      color: 'info' as const,
    },
    {
      title: 'Avg. CPC',
      value: avgCPC,
      format: 'currency' as const,
      icon: <AttachMoney fontSize="small" />,
      color: 'warning' as const,
    },
    {
      title: 'Impressions',
      value: totalImpressions,
      format: 'number' as const,
      icon: <Visibility fontSize="small" />,
      color: 'secondary' as const,
    },
    {
      title: 'Conv. Rate',
      value: avgConversionRate,
      format: 'percentage' as const,
      icon: <Percent fontSize="small" />,
      color: 'success' as const,
    },
  ];

  const formatCompactNumber = (num: number) => {
    if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
    if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
    return num.toFixed(2);
  };

  const handleRefresh = () => {
    refetchCampaigns();
    refetchMetrics();
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header Section */}
      <Box sx={{ mb: 3 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center">
          <Box>
            <Typography variant="h4" fontWeight="bold" gutterBottom>
              Campaign Performance
            </Typography>
            <Typography variant="body2" color="text.secondary">
              Real-time analytics from your Google Ads campaigns
            </Typography>
          </Box>
          <Stack direction="row" spacing={1}>
            <Chip
              icon={<Schedule fontSize="small" />}
              label={filters.dateRange.replace(/_/g, ' ')}
              color="primary"
              variant="outlined"
              size="small"
            />
            <IconButton size="small" color="primary" onClick={handleRefresh}>
              <Refresh fontSize="small" />
            </IconButton>
          </Stack>
        </Box>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {kpiData.map((kpi, index) => (
          <Grid item xs={6} sm={4} md={2} key={index}>
            <Card
              sx={{
                height: '100%',
                position: 'relative',
                overflow: 'hidden',
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.shadows[4],
                },
                '&::before': {
                  content: '""',
                  position: 'absolute',
                  top: 0,
                  left: 0,
                  right: 0,
                  height: '3px',
                  background: `linear-gradient(90deg, ${theme.palette[kpi.color].main}, ${alpha(
                    theme.palette[kpi.color].main,
                    0.3
                  )})`,
                },
              }}
            >
              <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
                <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
                  <Typography variant="caption" color="text.secondary" fontWeight={500}>
                    {kpi.title}
                  </Typography>
                  <Box
                    sx={{
                      width: 28,
                      height: 28,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      borderRadius: 1,
                      bgcolor: alpha(theme.palette[kpi.color].main, 0.1),
                      color: theme.palette[kpi.color].main,
                    }}
                  >
                    {kpi.icon}
                  </Box>
                </Box>
                <Typography variant="h6" fontWeight="bold" sx={{ mb: 0.5 }}>
                  {kpi.format === 'currency'
                    ? `₹${formatCompactNumber(kpi.value)}`
                    : kpi.format === 'percentage'
                    ? `${kpi.value.toFixed(2)}%`
                    : formatCompactNumber(kpi.value)}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        ))}
      </Grid>

      {/* Main Content Grid */}
      <Grid container spacing={3}>
        {/* Performance Chart */}
        {timeseriesData && timeseriesData.data_points && timeseriesData.data_points.length > 0 && (
          <Grid item xs={12} lg={8}>
            <Card sx={{ height: '100%' }}>
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
                  <Typography variant="h6" fontWeight="600">
                    Performance Over Time
                  </Typography>
                </Box>
                <ResponsiveContainer width="100%" height={300}>
                  <ComposedChart data={timeseriesData.data_points}>
                    <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
                    <XAxis dataKey="date" tick={{ fontSize: 12 }} />
                    <YAxis yAxisId="left" tick={{ fontSize: 12 }} />
                    <YAxis yAxisId="right" orientation="right" tick={{ fontSize: 12 }} />
                    <RechartsTooltip
                      contentStyle={{
                        backgroundColor: alpha(theme.palette.background.paper, 0.95),
                        border: `1px solid ${theme.palette.divider}`,
                        borderRadius: 8,
                        fontSize: '0.875rem',
                      }}
                    />
                    <Legend wrapperStyle={{ fontSize: '0.875rem' }} />
                    <Area
                      yAxisId="left"
                      type="monotone"
                      dataKey="cost"
                      fill={alpha('#6366f1', 0.2)}
                      stroke="#6366f1"
                      strokeWidth={2}
                    />
                    <Bar yAxisId="left" dataKey="clicks" fill="#10b981" opacity={0.8} />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="conversions"
                      stroke="#ef4444"
                      strokeWidth={3}
                      dot={{ fill: '#ef4444', r: 3 }}
                    />
                  </ComposedChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Grid>
        )}

        {/* Channel Distribution */}
        <Grid item xs={12} lg={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight="600" mb={2}>
                Channel Performance
              </Typography>
              {channelBreakdown.length > 0 ? (
                <>
                  <ResponsiveContainer width="100%" height={250}>
                    <PieChart>
                      <Pie
                        data={channelBreakdown}
                        cx="50%"
                        cy="50%"
                        innerRadius={40}
                        outerRadius={80}
                        paddingAngle={5}
                        dataKey="count"
                      >
                        {channelBreakdown.map((entry, index) => (
                          <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                        ))}
                      </Pie>
                      <RechartsTooltip />
                    </PieChart>
                  </ResponsiveContainer>
                  <Box mt={2}>
                    {channelBreakdown.map((channel, idx) => (
                      <Box key={idx} display="flex" justifyContent="space-between" alignItems="center" mb={0.5}>
                        <Box display="flex" alignItems="center" gap={1}>
                          <Box sx={{ width: 10, height: 10, bgcolor: COLORS[idx % COLORS.length], borderRadius: '50%' }} />
                          <Typography variant="caption">{channel.name}</Typography>
                        </Box>
                        <Typography variant="caption" fontWeight={600}>
                          {channel.count} campaigns
                        </Typography>
                      </Box>
                    ))}
                  </Box>
                </>
              ) : (
                <Typography variant="body2" color="text.secondary" align="center">
                  No channel data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Campaign Statistics */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="600" mb={2}>
                Campaign Statistics
              </Typography>
              <Grid container spacing={2}>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Total Campaigns
                  </Typography>
                  <Typography variant="h5" fontWeight={600}>
                    {totalCampaigns}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Active Campaigns
                  </Typography>
                  <Typography variant="h5" fontWeight={600} color="success.main">
                    {activeCampaigns}
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Avg CTR
                  </Typography>
                  <Typography variant="h5" fontWeight={600}>
                    {avgCTR.toFixed(2)}%
                  </Typography>
                </Grid>
                <Grid item xs={6}>
                  <Typography variant="body2" color="text.secondary">
                    Avg CPC
                  </Typography>
                  <Typography variant="h5" fontWeight={600}>
                    ₹{avgCPC.toFixed(2)}
                  </Typography>
                </Grid>
              </Grid>
            </CardContent>
          </Card>
        </Grid>

        {/* Top Campaigns */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight="600" mb={2}>
                Top Campaigns
              </Typography>
              <Box sx={{ overflowX: 'auto' }}>
                {campaignsData?.campaigns?.slice(0, 5).map((campaign: any) => (
                  <Box
                    key={campaign.campaign_id}
                    sx={{
                      p: 2,
                      mb: 1,
                      borderRadius: 1,
                      backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.02)',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        backgroundColor: theme.palette.mode === 'dark' ? 'rgba(255,255,255,0.08)' : 'rgba(0,0,0,0.04)',
                      }
                    }}
                  >
                    <Box display="flex" justifyContent="space-between" alignItems="center">
                      <Box flex={1}>
                        <Typography variant="body2" fontWeight={600} noWrap>
                          {campaign.campaign_name}
                        </Typography>
                        <Stack direction="row" spacing={1} mt={0.5}>
                          <Chip
                            label={campaign.status}
                            size="small"
                            color={campaign.status === 'ENABLED' ? 'success' : 'default'}
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                          <Chip
                            label={campaign.channel_type}
                            size="small"
                            variant="outlined"
                            sx={{ height: 20, fontSize: '0.7rem' }}
                          />
                        </Stack>
                      </Box>
                      <Box textAlign="right">
                        <Typography variant="caption" color="text.secondary" display="block">
                          Cost: ₹{(campaign.metrics?.cost || 0).toFixed(2)}
                        </Typography>
                        <Typography variant="caption" color="text.secondary" display="block">
                          Clicks: {campaign.metrics?.clicks || 0}
                        </Typography>
                      </Box>
                    </Box>
                  </Box>
                ))}
                {(!campaignsData?.campaigns || campaignsData.campaigns.length === 0) && (
                  <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 2 }}>
                    No campaigns found
                  </Typography>
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default EnhancedCampaignsDashboard;