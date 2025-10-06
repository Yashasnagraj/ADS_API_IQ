/**
 * Alerts Dashboard with Real Filtered Data
 * Uses customer_id filter to show only selected customer's alerts
 */
import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  CircularProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Fade,
  useTheme,
  alpha,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Button,
} from '@mui/material';
import {
  TrendingUp,
  Info,
  NotificationsActive,
  Timeline,
  Speed,
  AutoAwesome,
  TipsAndUpdates,
  Warning,
  Error,
  CheckCircle,
  PriorityHigh,
  Refresh,
} from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import DashboardTemplate from '../../components/common/DashboardTemplate';
import CompactKPICard from '../../components/common/CompactKPICard';
import InteractiveKPICard from '../../components/kpi/InteractiveKPICard';
import KPIDetailDrawer, { KPIDetailItem } from '../../components/kpi/KPIDetailDrawer';
import { EnhancedChart } from '../../components/charts/EnhancedChart';
import AIIntelligenceSection, { AIInsight } from '../../components/common/AIIntelligenceSection';
import { useFilters } from '../../context/FilterContext';
import { useCampaigns, useKeywords, useMetricsSummary, useFilteredAPI } from '../../hooks/useFilteredAPI';

// Alert thresholds
const THRESHOLDS = {
  CTR_LOW: 1.5, // CTR < 1.5%
  CPC_HIGH: 3.0, // CPC > $3.00
  CONVERSION_RATE_LOW: 1.0, // Conv Rate < 1%
  QUALITY_SCORE_LOW: 5, // Quality Score < 5
  BUDGET_WARNING: 0.8, // 80% of budget spent
  COST_SPIKE: 1.5, // 50% cost increase
};

interface AlertItem {
  id: string;
  title: string;
  severity: 'critical' | 'high' | 'medium' | 'low';
  status: 'active' | 'investigating' | 'resolved';
  timestamp: string;
  campaign: string;
  description: string;
  metric?: string;
  value?: number;
  threshold?: number;
}

const AlertsDashboard: React.FC = () => {
  const theme = useTheme();
  const { filters } = useFilters();
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  // Drawer state for interactive KPIs
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerData, setDrawerData] = useState<KPIDetailItem[]>([]);
  const [drawerTitle, setDrawerTitle] = useState('');
  const [drawerSubtitle, setDrawerSubtitle] = useState('');

  // Fetch data using filtered hooks
  const { data: metricsData, loading: metricsLoading, error: metricsError, refetch: refetchMetrics } = useMetricsSummary();
  const { data: campaignsData, loading: campaignsLoading, refetch: refetchCampaigns } = useCampaigns({ limit: 100 });
  const { data: keywordsData, loading: keywordsLoading } = useKeywords({ limit: 100 });
  const { data: timeseriesData, loading: timeseriesLoading } = useFilteredAPI({
    endpoint: '/metrics/timeseries',
    params: { days: 7, interval: 'daily' }
  });

  // Generate alerts based on real data
  const alerts: AlertItem[] = useMemo(() => {
    if (!campaignsData?.campaigns) return [];

    const alertsList: AlertItem[] = [];
    let alertId = 1;

    campaignsData.campaigns.forEach((campaign: any) => {
      const metrics = campaign.metrics || {};
      const ctr = (metrics.ctr || 0) * 100;
      const cpc = metrics.cpc || 0;
      const convRate = (metrics.conversion_rate || 0) * 100;
      const cost = metrics.cost || 0;
      const campaignName = campaign.name || 'Unknown Campaign';

      // CTR Alert
      if (ctr > 0 && ctr < THRESHOLDS.CTR_LOW) {
        alertsList.push({
          id: `ALT${String(alertId++).padStart(3, '0')}`,
          title: 'CTR Below Threshold',
          severity: ctr < 1.0 ? 'critical' : 'high',
          status: 'active',
          timestamp: 'Recent',
          campaign: campaignName,
          description: `CTR is ${ctr.toFixed(2)}%, below ${THRESHOLDS.CTR_LOW}% threshold`,
          metric: 'CTR',
          value: ctr,
          threshold: THRESHOLDS.CTR_LOW
        });
      }

      // CPC Alert
      if (cpc > THRESHOLDS.CPC_HIGH) {
        alertsList.push({
          id: `ALT${String(alertId++).padStart(3, '0')}`,
          title: 'High CPC Detected',
          severity: cpc > THRESHOLDS.CPC_HIGH * 1.5 ? 'critical' : 'medium',
          status: 'active',
          timestamp: 'Recent',
          campaign: campaignName,
          description: `CPC is ₹${cpc.toFixed(2)}, above ₹${THRESHOLDS.CPC_HIGH.toFixed(2)} threshold`,
          metric: 'CPC',
          value: cpc,
          threshold: THRESHOLDS.CPC_HIGH
        });
      }

      // Conversion Rate Alert
      if (metrics.conversions > 0 && convRate < THRESHOLDS.CONVERSION_RATE_LOW) {
        alertsList.push({
          id: `ALT${String(alertId++).padStart(3, '0')}`,
          title: 'Low Conversion Rate',
          severity: convRate < 0.5 ? 'critical' : 'high',
          status: 'active',
          timestamp: 'Recent',
          campaign: campaignName,
          description: `Conversion rate is ${convRate.toFixed(2)}%, below ${THRESHOLDS.CONVERSION_RATE_LOW}% threshold`,
          metric: 'Conv Rate',
          value: convRate,
          threshold: THRESHOLDS.CONVERSION_RATE_LOW
        });
      }

      // Zero Conversions Alert (campaigns with clicks but no conversions)
      if (metrics.clicks > 50 && metrics.conversions === 0) {
        alertsList.push({
          id: `ALT${String(alertId++).padStart(3, '0')}`,
          title: 'Zero Conversions Alert',
          severity: 'critical',
          status: 'active',
          timestamp: 'Recent',
          campaign: campaignName,
          description: `${metrics.clicks} clicks but zero conversions - check tracking`,
          metric: 'Conversions',
          value: 0,
          threshold: 1
        });
      }

      // Budget Warning (if campaign budget available)
      if (campaign.budget_amount && cost > campaign.budget_amount * THRESHOLDS.BUDGET_WARNING) {
        alertsList.push({
          id: `ALT${String(alertId++).padStart(3, '0')}`,
          title: 'Budget Warning',
          severity: 'medium',
          status: 'active',
          timestamp: 'Recent',
          campaign: campaignName,
          description: `${((cost / campaign.budget_amount) * 100).toFixed(0)}% of budget spent`,
          metric: 'Budget',
          value: cost,
          threshold: campaign.budget_amount
        });
      }
    });

    // Sort by severity
    const severityOrder = { critical: 0, high: 1, medium: 2, low: 3 };
    return alertsList.sort((a, b) => severityOrder[a.severity] - severityOrder[b.severity]);
  }, [campaignsData]);

  // Calculate metrics
  const activeAlerts = alerts.filter(a => a.status === 'active').length;
  const criticalAlerts = alerts.filter(a => a.severity === 'critical' && a.status === 'active').length;
  const resolvedAlerts = alerts.filter(a => a.status === 'resolved').length;
  const totalAlerts = alerts.length;

  // Calculate resolution rate
  const resolutionRate = totalAlerts > 0 ? ((resolvedAlerts / totalAlerts) * 100) : 0;

  // Alert trends (based on timeseries data)
  const alertTrends = useMemo(() => {
    if (!timeseriesData?.timeseries) {
      return [
        { date: 'Mon', critical: 0, high: 0, medium: 0, low: 0 },
        { date: 'Tue', critical: 0, high: 0, medium: 0, low: 0 },
        { date: 'Wed', critical: 0, high: 0, medium: 0, low: 0 },
        { date: 'Thu', critical: 0, high: 0, medium: 0, low: 0 },
        { date: 'Fri', critical: 0, high: 0, medium: 0, low: 0 },
      ];
    }

    return timeseriesData.timeseries.slice(-5).map((item: any, index: number) => {
      const ctr = (item.ctr || 0) * 100;
      const cpc = item.cpc || 0;
      const convRate = (item.conversion_rate || 0) * 100;

      let critical = 0, high = 0, medium = 0, low = 0;

      if (ctr < 1.0) critical++;
      else if (ctr < THRESHOLDS.CTR_LOW) high++;

      if (cpc > THRESHOLDS.CPC_HIGH * 1.5) critical++;
      else if (cpc > THRESHOLDS.CPC_HIGH) medium++;

      if (convRate < 0.5) critical++;
      else if (convRate < THRESHOLDS.CONVERSION_RATE_LOW) high++;

      const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
      const date = new Date(item.date);

      return {
        date: days[date.getDay()],
        critical,
        high,
        medium,
        low
      };
    });
  }, [timeseriesData]);

  // Severity distribution
  const severityDistribution = useMemo(() => {
    const counts = {
      critical: alerts.filter(a => a.severity === 'critical').length,
      high: alerts.filter(a => a.severity === 'high').length,
      medium: alerts.filter(a => a.severity === 'medium').length,
      low: alerts.filter(a => a.severity === 'low').length,
    };

    return [
      { name: 'Critical', value: counts.critical, color: theme.palette.error.main },
      { name: 'High', value: counts.high, color: theme.palette.warning.main },
      { name: 'Medium', value: counts.medium, color: theme.palette.info.main },
      { name: 'Low', value: counts.low, color: theme.palette.success.main },
    ].filter(item => item.value > 0);
  }, [alerts, theme]);

  // AI Insights
  const aiInsights: AIInsight[] = useMemo(() => {
    const insights: AIInsight[] = [];

    if (criticalAlerts > 0) {
      insights.push({
        type: 'warning',
        title: 'Critical Alerts Detected',
        description: `${criticalAlerts} critical alert${criticalAlerts > 1 ? 's' : ''} require immediate attention`,
        impact: 'Performance impact',
        confidence: 96,
        action: 'Investigate Now',
        icon: <Error />,
      });
    }

    if (alerts.filter(a => a.metric === 'CTR').length > 2) {
      insights.push({
        type: 'recommendation',
        title: 'CTR Optimization Needed',
        description: 'Multiple campaigns have low CTR - review ad copy and targeting',
        impact: 'Efficiency improvement',
        confidence: 89,
        action: 'Optimize Campaigns',
        icon: <AutoAwesome />,
      });
    }

    if (alerts.filter(a => a.metric === 'Conversions').length > 0) {
      insights.push({
        type: 'prediction',
        title: 'Conversion Tracking Issue',
        description: 'Campaigns with clicks but no conversions detected - verify tracking setup',
        impact: 'Data accuracy',
        confidence: 92,
        action: 'Check Tracking',
        icon: <Timeline />,
      });
    }

    return insights;
  }, [alerts, criticalAlerts]);

  // KPI Click Handlers - using REAL data from alerts
  const handleActiveAlertsClick = () => {
    const activeAlertsList = alerts.filter(a => a.status === 'active');
    setDrawerData(activeAlertsList.map(alert => ({
      id: alert.id,
      name: alert.campaign,
      value: alert.title,
      subtitle: alert.description,
      status: alert.severity === 'critical' ? 'error' : alert.severity === 'high' ? 'warning' : 'info',
    })));
    setDrawerTitle('Active Alerts');
    setDrawerSubtitle(`${activeAlerts} alerts currently active and requiring attention`);
    setDrawerOpen(true);
  };

  const handleCriticalAlertsClick = () => {
    const criticalAlertsList = alerts.filter(a => a.severity === 'critical' && a.status === 'active');
    setDrawerData(criticalAlertsList.map(alert => ({
      id: alert.id,
      name: alert.campaign,
      value: alert.title,
      subtitle: alert.description,
      status: 'error',
      metadata: { metric: alert.metric, value: alert.value, threshold: alert.threshold },
    })));
    setDrawerTitle('Critical Alerts');
    setDrawerSubtitle(`${criticalAlerts} critical alerts demanding immediate action`);
    setDrawerOpen(true);
  };

  const handleTotalAlertsClick = () => {
    setDrawerData(alerts.map(alert => ({
      id: alert.id,
      name: alert.campaign,
      value: `${alert.severity.toUpperCase()} - ${alert.title}`,
      subtitle: alert.description,
      status: alert.severity === 'critical' ? 'error' :
              alert.severity === 'high' ? 'warning' :
              alert.severity === 'medium' ? 'info' : 'success',
    })));
    setDrawerTitle('All Alerts');
    setDrawerSubtitle(`Complete list of ${totalAlerts} detected alerts`);
    setDrawerOpen(true);
  };

  const handleResolutionRateClick = () => {
    const resolvedAlertsList = alerts.filter(a => a.status === 'resolved');
    setDrawerData(resolvedAlertsList.map(alert => ({
      id: alert.id,
      name: alert.campaign,
      value: alert.title,
      subtitle: `Resolved - ${alert.description}`,
      status: 'success',
    })));
    setDrawerTitle('Resolution Rate');
    setDrawerSubtitle(`${resolvedAlerts} resolved out of ${totalAlerts} total (${resolutionRate.toFixed(1)}%)`);
    setDrawerOpen(true);
  };

  const handleCampaignsAffectedClick = () => {
    const campaignAlertMap = new Map<string, AlertItem[]>();
    alerts.forEach(alert => {
      const existing = campaignAlertMap.get(alert.campaign) || [];
      campaignAlertMap.set(alert.campaign, [...existing, alert]);
    });

    setDrawerData(Array.from(campaignAlertMap.entries()).map(([campaign, campaignAlerts]) => ({
      id: campaign,
      name: campaign,
      value: `${campaignAlerts.length} alert${campaignAlerts.length > 1 ? 's' : ''}`,
      subtitle: campaignAlerts.map(a => a.title).join(', '),
      status: campaignAlerts.some(a => a.severity === 'critical') ? 'error' :
              campaignAlerts.some(a => a.severity === 'high') ? 'warning' : 'info',
    })));
    setDrawerTitle('Campaigns Affected');
    setDrawerSubtitle(`${new Set(alerts.map(a => a.campaign)).size} campaigns with active alerts`);
    setDrawerOpen(true);
  };

  const handleAvgSeverityClick = () => {
    const severityCounts = {
      critical: alerts.filter(a => a.severity === 'critical').length,
      high: alerts.filter(a => a.severity === 'high').length,
      medium: alerts.filter(a => a.severity === 'medium').length,
      low: alerts.filter(a => a.severity === 'low').length,
    };

    setDrawerData([
      {
        id: 'critical',
        name: 'Critical Severity',
        value: `${severityCounts.critical} alerts`,
        subtitle: 'Requires immediate attention',
        status: 'error',
      },
      {
        id: 'high',
        name: 'High Severity',
        value: `${severityCounts.high} alerts`,
        subtitle: 'Action needed soon',
        status: 'warning',
      },
      {
        id: 'medium',
        name: 'Medium Severity',
        value: `${severityCounts.medium} alerts`,
        subtitle: 'Monitor closely',
        status: 'info',
      },
      {
        id: 'low',
        name: 'Low Severity',
        value: `${severityCounts.low} alerts`,
        subtitle: 'For awareness',
        status: 'success',
      },
    ]);
    setDrawerTitle('Alert Severity Distribution');
    setDrawerSubtitle(`Breakdown of ${totalAlerts} alerts by severity level`);
    setDrawerOpen(true);
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <Error sx={{ color: theme.palette.error.main }} />;
      case 'high':
        return <Warning sx={{ color: theme.palette.warning.main }} />;
      case 'medium':
        return <Info sx={{ color: theme.palette.info.main }} />;
      case 'low':
        return <CheckCircle sx={{ color: theme.palette.success.main }} />;
      default:
        return <Info />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'high':
        return 'warning';
      case 'medium':
        return 'info';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  // Refresh all data
  const handleRefresh = () => {
    refetchMetrics();
    refetchCampaigns();
  };

  // Loading state
  if (!filters.customerId) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Please select a customer to view alerts</Typography>
      </Box>
    );
  }

  if (metricsLoading || campaignsLoading || keywordsLoading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading alerts data...</Typography>
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

  return (
    <DashboardTemplate
      title="Alerts Dashboard"
      subtitle="Real-time monitoring and intelligent alert management for campaign performance"
      selectedTimeRange={selectedTimeRange}
      onTimeRangeChange={() => setSelectedTimeRange(selectedTimeRange === '7d' ? '30d' : '7d')}
    >
      {/* Header Actions */}
      <Box sx={{ display: 'flex', justifyContent: 'flex-end', mb: 2 }}>
        <Tooltip title="Refresh alerts">
          <IconButton onClick={handleRefresh} size="small">
            <Refresh />
          </IconButton>
        </Tooltip>
      </Box>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Active Alerts"
            value={activeAlerts}
            format="number"
            icon={<NotificationsActive />}
            trend={activeAlerts > 0 ? "up" : "neutral"}
            trendValue={0}
            color="warning"
            index={0}
            onClick={handleActiveAlertsClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Critical Alerts"
            value={criticalAlerts}
            format="number"
            icon={<PriorityHigh />}
            trend={criticalAlerts > 0 ? "up" : "neutral"}
            trendValue={0}
            color="error"
            index={1}
            onClick={handleCriticalAlertsClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Total Alerts"
            value={totalAlerts}
            format="number"
            icon={<Timeline />}
            trend="neutral"
            trendValue={0}
            color="info"
            index={2}
            onClick={handleTotalAlertsClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Resolution Rate"
            value={Number(resolutionRate.toFixed(1))}
            format="percentage"
            icon={<CheckCircle />}
            trend="up"
            trendValue={0}
            color="success"
            index={3}
            onClick={handleResolutionRateClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Campaigns Affected"
            value={new Set(alerts.map(a => a.campaign)).size}
            format="number"
            icon={<Warning />}
            trend="neutral"
            trendValue={0}
            color="warning"
            index={4}
            onClick={handleCampaignsAffectedClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Avg Severity"
            value={activeAlerts > 0 ? Number((criticalAlerts / activeAlerts * 10).toFixed(1)) : 0}
            format="number"
            icon={<Speed />}
            trend="down"
            trendValue={0}
            color="info"
            index={5}
            onClick={handleAvgSeverityClick}
            drillDownAvailable={true}
          />
        </Grid>
      </Grid>

      {/* AI Intelligence Section */}
      {aiInsights.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <AIIntelligenceSection insights={aiInsights} />
        </Box>
      )}

      <Grid container spacing={3}>
        {/* Alert Trends */}
        <Grid item xs={12} md={8}>
          <Fade in timeout={600}>
            <Card
              sx={{
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.shadows[8],
                },
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Alert Trends by Severity
                  </Typography>
                  <Chip
                    icon={<Speed />}
                    label="Real-time"
                    color="success"
                    size="small"
                  />
                </Box>
                <EnhancedChart
                  height={300}
                  xAxis={{ label: 'Day of Week', dataKey: 'date' }}
                  yAxis={{ label: 'Alert Count', format: 'number' }}
                  showLegend={true}
                >
                  <AreaChart data={alertTrends}>
                    <Area
                      type="monotone"
                      dataKey="critical"
                      stackId="1"
                      stroke={theme.palette.error.main}
                      fill={alpha(theme.palette.error.main, 0.7)}
                      name="Critical"
                    />
                    <Area
                      type="monotone"
                      dataKey="high"
                      stackId="1"
                      stroke={theme.palette.warning.main}
                      fill={alpha(theme.palette.warning.main, 0.7)}
                      name="High"
                    />
                    <Area
                      type="monotone"
                      dataKey="medium"
                      stackId="1"
                      stroke={theme.palette.info.main}
                      fill={alpha(theme.palette.info.main, 0.7)}
                      name="Medium"
                    />
                    <Area
                      type="monotone"
                      dataKey="low"
                      stackId="1"
                      stroke={theme.palette.success.main}
                      fill={alpha(theme.palette.success.main, 0.7)}
                      name="Low"
                    />
                  </AreaChart>
                </EnhancedChart>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Severity Distribution */}
        <Grid item xs={12} md={4}>
          <Fade in timeout={700}>
            <Card
              sx={{
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: theme.shadows[8],
                },
              }}
            >
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2 }}>
                  Alert Severity Distribution
                </Typography>
                {severityDistribution.length > 0 ? (
                  <>
                    <ResponsiveContainer width="100%" height={250}>
                      <PieChart>
                        <Pie
                          data={severityDistribution}
                          cx="50%"
                          cy="50%"
                          innerRadius={40}
                          outerRadius={80}
                          paddingAngle={5}
                          dataKey="value"
                        >
                          {severityDistribution.map((entry: any, index: number) => (
                            <Cell key={`cell-${index}`} fill={entry.color} />
                          ))}
                        </Pie>
                        <RechartsTooltip />
                      </PieChart>
                    </ResponsiveContainer>
                    <Box sx={{ mt: 2 }}>
                      {severityDistribution.map((item: any, index: number) => (
                        <Box key={index} sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <Box
                            sx={{
                              width: 12,
                              height: 12,
                              bgcolor: item.color,
                              borderRadius: '50%',
                              mr: 1,
                            }}
                          />
                          <Typography variant="caption" sx={{ flex: 1 }}>
                            {item.name}
                          </Typography>
                          <Typography variant="caption" fontWeight={600}>
                            {item.value}
                          </Typography>
                        </Box>
                      ))}
                    </Box>
                  </>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 4 }}>
                    <CheckCircle sx={{ fontSize: 60, color: theme.palette.success.main, mb: 2 }} />
                    <Typography variant="body2" color="text.secondary">
                      No alerts at this time
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Recent Alerts */}
        <Grid item xs={12}>
          <Fade in timeout={800}>
            <Card
              sx={{
                transition: 'all 0.3s ease',
                '&:hover': {
                  boxShadow: theme.shadows[4],
                },
              }}
            >
              <CardContent>
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Recent Alerts
                  </Typography>
                  <Chip
                    icon={<NotificationsActive />}
                    label={`${activeAlerts} Active`}
                    color={activeAlerts > 0 ? "warning" : "success"}
                    size="small"
                    variant="outlined"
                  />
                </Box>
                {alerts.length > 0 ? (
                  <TableContainer component={Paper} elevation={0}>
                    <Table>
                      <TableHead>
                        <TableRow>
                          <TableCell>Alert</TableCell>
                          <TableCell>Campaign</TableCell>
                          <TableCell>Description</TableCell>
                          <TableCell align="center">Severity</TableCell>
                          <TableCell align="center">Status</TableCell>
                          <TableCell>Time</TableCell>
                          <TableCell align="center">Actions</TableCell>
                        </TableRow>
                      </TableHead>
                      <TableBody>
                        {alerts.slice(0, 10).map((alert: AlertItem, index: number) => (
                          <TableRow
                            key={index}
                            hover
                            sx={{
                              cursor: 'pointer',
                              transition: 'all 0.2s ease',
                              '&:hover': {
                                bgcolor: alpha(theme.palette.primary.main, 0.05),
                                transform: 'scale(1.01)',
                              },
                              bgcolor: alert.severity === 'critical' ? alpha(theme.palette.error.main, 0.1) : 'transparent',
                            }}
                          >
                            <TableCell>
                              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                                {getSeverityIcon(alert.severity)}
                                <Typography variant="body2" fontWeight={600}>
                                  {alert.title}
                                </Typography>
                              </Box>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" fontWeight={500}>
                                {alert.campaign.length > 30 ? alert.campaign.substring(0, 30) + '...' : alert.campaign}
                              </Typography>
                            </TableCell>
                            <TableCell>
                              <Typography variant="body2" color="text.secondary">
                                {alert.description}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Chip
                                label={alert.severity.toUpperCase()}
                                color={getSeverityColor(alert.severity) as any}
                                size="small"
                                variant="outlined"
                              />
                            </TableCell>
                            <TableCell align="center">
                              <Chip
                                label={alert.status}
                                color={alert.status === 'resolved' ? 'success' : alert.status === 'investigating' ? 'warning' : 'error'}
                                size="small"
                              />
                            </TableCell>
                            <TableCell>
                              <Typography variant="caption" color="text.secondary">
                                {alert.timestamp}
                              </Typography>
                            </TableCell>
                            <TableCell align="center">
                              <Button
                                size="small"
                                variant={alert.status === 'active' ? 'contained' : 'outlined'}
                                color={alert.severity === 'critical' ? 'error' : 'primary'}
                                sx={{
                                  minWidth: 'auto',
                                  px: 2,
                                  transition: 'all 0.2s',
                                  '&:hover': { transform: 'scale(1.05)' },
                                }}
                              >
                                {alert.status === 'resolved' ? 'View' : 'Investigate'}
                              </Button>
                            </TableCell>
                          </TableRow>
                        ))}
                      </TableBody>
                    </Table>
                  </TableContainer>
                ) : (
                  <Box sx={{ textAlign: 'center', py: 6 }}>
                    <CheckCircle sx={{ fontSize: 80, color: theme.palette.success.main, mb: 2 }} />
                    <Typography variant="h6" color="text.secondary">
                      All Clear!
                    </Typography>
                    <Typography variant="body2" color="text.secondary">
                      No alerts detected for this customer
                    </Typography>
                  </Box>
                )}
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {criticalAlerts > 0 && (
          <Grid item xs={12}>
            <Fade in timeout={900}>
              <Alert
                severity="error"
                icon={<PriorityHigh />}
                sx={{
                  background: `linear-gradient(45deg, ${alpha(theme.palette.error.main, 0.1)} 0%, ${alpha(theme.palette.error.light, 0.05)} 100%)`,
                  border: `1px solid ${alpha(theme.palette.error.main, 0.2)}`,
                }}
              >
                <Typography variant="subtitle2">
                  <strong>Critical Alert:</strong> {criticalAlerts} critical alert{criticalAlerts > 1 ? 's' : ''} require immediate attention.
                  Review campaigns with low CTR, high CPC, or zero conversions to prevent performance degradation.
                </Typography>
              </Alert>
            </Fade>
          </Grid>
        )}
      </Grid>

      {/* KPI Detail Drawer */}
      <KPIDetailDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={drawerTitle}
        subtitle={drawerSubtitle}
        data={drawerData}
        type="list"
        showTopCount={10}
        color="warning"
      />
    </DashboardTemplate>
  );
};

export default AlertsDashboard;