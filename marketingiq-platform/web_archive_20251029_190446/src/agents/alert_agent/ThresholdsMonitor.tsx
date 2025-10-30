import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  LinearProgress,
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
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  TrendingUp,
  Info,
  Settings,
  Timeline,
  Speed,
  AutoAwesome,
  TipsAndUpdates,
  Warning,
  CheckCircle,
  TuneRounded,
  MonitorHeart,
} from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar, Cell } from 'recharts';
import DashboardTemplate from '../../components/common/DashboardTemplate';
import CompactKPICard from '../../components/common/CompactKPICard';
import AIIntelligenceSection, { AIInsight } from '../../components/common/AIIntelligenceSection';
import { alertService } from '../../services/api';
import InteractiveKPICard from '../../components/kpi/InteractiveKPICard';
import KPIDetailDrawer, { KPIDetailItem } from '../../components/kpi/KPIDetailDrawer';
import { EnhancedChart } from '../../components/charts/EnhancedChart';

const ThresholdsMonitor: React.FC = () => {
  const theme = useTheme();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  // Drawer state for interactive KPIs
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerData, setDrawerData] = useState<KPIDetailItem[]>([]);
  const [drawerTitle, setDrawerTitle] = useState('');
  const [drawerSubtitle, setDrawerSubtitle] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await alertService.getThresholds();
      setData(result);
    } catch (error) {
      console.error('Error fetching data:', error);
      setData(mockData);
    } finally {
      setLoading(false);
    }
  };

  const mockData = {
    metrics: [
      { label: 'Active Thresholds', value: 24 },
      { label: 'Violations Today', value: 7 },
      { label: 'Accuracy Rate', value: 92.5 },
      { label: 'Response Time', value: 1.8 },
      { label: 'Coverage', value: 95 },
      { label: 'Optimization Score', value: 8.3 },
    ],
    thresholds: [
      { id: 'THR001', metric: 'CTR', operator: '<', value: 2.0, current: 1.8, status: 'violated', campaign: 'Summer Sale', lastTriggered: '5 mins ago', enabled: true },
      { id: 'THR002', metric: 'CPC', operator: '>', value: 2.50, current: 2.35, status: 'safe', campaign: 'Brand Awareness', lastTriggered: 'Never', enabled: true },
      { id: 'THR003', metric: 'Budget', operator: '>', value: 1000, current: 1150, status: 'violated', campaign: 'Holiday Campaign', lastTriggered: '2 mins ago', enabled: true },
      { id: 'THR004', metric: 'Quality Score', operator: '<', value: 5, current: 6.2, status: 'safe', campaign: 'Product Launch', lastTriggered: '1 day ago', enabled: false },
      { id: 'THR005', metric: 'Conversion Rate', operator: '<', value: 1.5, current: 0.8, status: 'violated', campaign: 'Retargeting', lastTriggered: '12 mins ago', enabled: true },
    ],
    violationTrends: [
      { date: 'Mon', violations: 5, thresholds: 24 },
      { date: 'Tue', violations: 8, thresholds: 24 },
      { date: 'Wed', violations: 3, thresholds: 25 },
      { date: 'Thu', violations: 12, thresholds: 25 },
      { date: 'Fri', violations: 7, thresholds: 24 },
    ],
    metricDistribution: [
      { metric: 'CTR', count: 6, violations: 2 },
      { metric: 'CPC', count: 5, violations: 1 },
      { metric: 'Budget', count: 8, violations: 3 },
      { metric: 'Quality Score', count: 3, violations: 0 },
      { metric: 'Conversion Rate', count: 2, violations: 1 },
    ]
  };

  const aiInsights: AIInsight[] = [
    {
      type: 'warning',
      title: 'Multiple Threshold Violations',
      description: '7 threshold violations detected today across 5 campaigns - review critical metrics',
      impact: 'Performance degradation',
      confidence: 94,
      action: 'Review Violations',
      icon: <Warning />,
    },
    {
      type: 'recommendation',
      title: 'Threshold Optimization',
      description: 'Adjust CTR threshold from 2.0% to 1.5% to reduce false positives by 30%',
      impact: 'Better accuracy',
      confidence: 88,
      action: 'Optimize Thresholds',
      icon: <TuneRounded />,
    },
    {
      type: 'opportunity',
      title: 'Coverage Enhancement',
      description: 'Add conversion rate thresholds for 8 campaigns currently not monitored',
      impact: 'Improved monitoring',
      confidence: 91,
      action: 'Expand Coverage',
      icon: <MonitorHeart />,
    },
  ];

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'violated':
        return 'error';
      case 'warning':
        return 'warning';
      case 'safe':
        return 'success';
      default:
        return 'default';
    }
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'violated':
        return <Warning sx={{ color: theme.palette.error.main }} />;
      case 'warning':
        return <Warning sx={{ color: theme.palette.warning.main }} />;
      case 'safe':
        return <CheckCircle sx={{ color: theme.palette.success.main }} />;
      default:
        return <Info />;
    }
  };

  // KPI Click Handlers
  const handleActiveThresholdsClick = () => {
    const displayData = data || mockData;
    const items: KPIDetailItem[] = displayData.thresholds?.map((t: any) => ({
      id: t.id,
      name: t.metric,
      value: `${t.operator} ${t.value}`,
      status: t.enabled ? 'success' : 'warning',
      subtitle: `${t.campaign} • Current: ${t.current}`,
      trend: t.status === 'safe' ? 1 : -1,
    })) || [];
    setDrawerData(items);
    setDrawerTitle('Active Thresholds');
    setDrawerSubtitle(`${displayData.metrics[0]?.value || 24} thresholds currently configured`);
    setDrawerOpen(true);
  };

  const handleViolationsTodayClick = () => {
    const displayData = data || mockData;
    const violatedThresholds = displayData.thresholds?.filter((t: any) => t.status === 'violated') || [];
    const items: KPIDetailItem[] = violatedThresholds.map((t: any) => ({
      id: t.id,
      name: t.metric,
      value: `Current: ${t.current}`,
      status: 'error',
      subtitle: `${t.campaign} • Threshold: ${t.operator} ${t.value}`,
      trend: -1,
    }));
    setDrawerData(items);
    setDrawerTitle('Threshold Violations');
    setDrawerSubtitle(`${displayData.metrics[1]?.value || 7} violations detected today`);
    setDrawerOpen(true);
  };

  const handleAccuracyRateClick = () => {
    const displayData = data || mockData;
    const items: KPIDetailItem[] = displayData.violationTrends?.map((vt: any, idx: number) => ({
      id: `trend-${idx}`,
      name: vt.date,
      value: `${vt.violations} violations`,
      status: vt.violations < 5 ? 'success' : vt.violations < 10 ? 'warning' : 'error',
      subtitle: `${vt.thresholds} active thresholds`,
      trend: idx > 0 ? (vt.violations < displayData.violationTrends[idx - 1].violations ? 1 : -1) : 0,
    })) || [];
    setDrawerData(items);
    setDrawerTitle('Accuracy Rate');
    setDrawerSubtitle(`${displayData.metrics[2]?.value || 92.5}% accuracy across all threshold checks`);
    setDrawerOpen(true);
  };

  const handleResponseTimeClick = () => {
    const displayData = data || mockData;
    const items: KPIDetailItem[] = displayData.thresholds?.map((t: any) => ({
      id: t.id,
      name: t.metric,
      value: t.lastTriggered,
      status: t.lastTriggered.includes('mins') ? 'error' : t.lastTriggered === 'Never' ? 'success' : 'warning',
      subtitle: `${t.campaign} • ${t.status.toUpperCase()}`,
    })) || [];
    setDrawerData(items);
    setDrawerTitle('Response Time');
    setDrawerSubtitle(`${displayData.metrics[3]?.value || 1.8}s average detection time`);
    setDrawerOpen(true);
  };

  const handleCoverageClick = () => {
    const displayData = data || mockData;
    const items: KPIDetailItem[] = displayData.metricDistribution?.map((md: any) => ({
      id: md.metric,
      name: md.metric,
      value: `${md.count} thresholds`,
      status: md.violations === 0 ? 'success' : md.violations < 2 ? 'warning' : 'error',
      subtitle: `${md.violations} violations`,
      trend: md.violations === 0 ? 1 : -1,
    })) || [];
    setDrawerData(items);
    setDrawerTitle('Coverage');
    setDrawerSubtitle(`${displayData.metrics[4]?.value || 95}% of campaigns have thresholds`);
    setDrawerOpen(true);
  };

  const handleOptimizationScoreClick = () => {
    const displayData = data || mockData;
    const items: KPIDetailItem[] = displayData.thresholds?.map((t: any) => ({
      id: t.id,
      name: t.metric,
      value: t.enabled ? 'Optimized' : 'Disabled',
      status: t.enabled && t.status === 'safe' ? 'success' : t.enabled && t.status === 'violated' ? 'error' : 'warning',
      subtitle: `${t.campaign} • ${t.operator} ${t.value}`,
      trend: t.status === 'safe' ? 1 : -1,
    })) || [];
    setDrawerData(items);
    setDrawerTitle('Optimization Score');
    setDrawerSubtitle(`${displayData.metrics[5]?.value || 8.3}/10 overall optimization score`);
    setDrawerOpen(true);
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  const displayData = data || mockData;

  return (
    <DashboardTemplate
      title="Thresholds Monitor"
      subtitle="Real-time threshold monitoring and intelligent alert configuration management"
      selectedTimeRange={selectedTimeRange}
      onTimeRangeChange={() => setSelectedTimeRange(selectedTimeRange === '7d' ? '30d' : '7d')}
    >
      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Active Thresholds"
            value={displayData.metrics[0]?.value || 24}
            format="number"
            icon={<TuneRounded />}
            trend="up"
            trendValue={4}
            color="primary"
            index={0}
            onClick={handleActiveThresholdsClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Violations Today"
            value={displayData.metrics[1]?.value || 7}
            format="number"
            icon={<Warning />}
            trend="down"
            trendValue={22}
            color="error"
            index={1}
            onClick={handleViolationsTodayClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Accuracy Rate"
            value={displayData.metrics[2]?.value || 92.5}
            format="percentage"
            icon={<CheckCircle />}
            trend="up"
            trendValue={3}
            color="success"
            index={2}
            onClick={handleAccuracyRateClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Response Time"
            value={displayData.metrics[3]?.value || 1.8}
            format="number"
            icon={<Speed />}
            trend="down"
            trendValue={15}
            color="info"
            index={3}
            onClick={handleResponseTimeClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Coverage"
            value={displayData.metrics[4]?.value || 95}
            format="percentage"
            icon={<MonitorHeart />}
            trend="up"
            trendValue={8}
            color="success"
            index={4}
            onClick={handleCoverageClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Optimization Score"
            value={displayData.metrics[5]?.value || 8.3}
            format="number"
            icon={<AutoAwesome />}
            trend="up"
            trendValue={12}
            color="secondary"
            index={5}
            onClick={handleOptimizationScoreClick}
            drillDownAvailable={true}
          />
        </Grid>
      </Grid>

      {/* AI Intelligence Section */}
      <Box sx={{ mb: 3 }}>
        <AIIntelligenceSection insights={aiInsights} />
      </Box>

      <Grid container spacing={3}>
        {/* Violation Trends */}
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
                    Threshold Violations Trend
                  </Typography>
                  <Chip
                    icon={<Timeline />}
                    label="Daily Tracking"
                    color="primary"
                    size="small"
                  />
                </Box>
                <EnhancedChart
                  xAxis={{ label: "Day", dataKey: "date" }}
                  yAxis={{ label: "Count", format: "number" }}
                  height={300}
                >
                  <AreaChart data={displayData.violationTrends}>
                    <Area
                      type="monotone"
                      dataKey="violations"
                      stroke={theme.palette.error.main}
                      fill={alpha(theme.palette.error.main, 0.3)}
                      name="Violations"
                    />
                    <Line
                      type="monotone"
                      dataKey="thresholds"
                      stroke={theme.palette.primary.main}
                      strokeWidth={2}
                      dot={{ fill: theme.palette.primary.main, r: 4 }}
                      name="Active Thresholds"
                    />
                  </AreaChart>
                </EnhancedChart>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Metric Distribution */}
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
                  Thresholds by Metric
                </Typography>
                <EnhancedChart
                  xAxis={{ label: "Metric", dataKey: "metric" }}
                  yAxis={{ label: "Count", format: "number" }}
                  height={250}
                >
                  <BarChart data={displayData.metricDistribution}>
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {displayData.metricDistribution.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.color || theme.palette.primary.main} />
                      ))}
                    </Bar>
                  </BarChart>
                </EnhancedChart>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Thresholds Configuration Table */}
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
                    Threshold Configuration
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip
                      icon={<Settings />}
                      label={`${displayData.thresholds?.filter((t: any) => t.enabled).length || 4}/${displayData.thresholds?.length || 5} Active`}
                      color="primary"
                      size="small"
                      variant="outlined"
                    />
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<TuneRounded />}
                      size="small"
                    >
                      Add Threshold
                    </Button>
                  </Box>
                </Box>
                <TableContainer component={Paper} elevation={0}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Metric</TableCell>
                        <TableCell>Campaign</TableCell>
                        <TableCell align="center">Condition</TableCell>
                        <TableCell align="right">Current Value</TableCell>
                        <TableCell align="center">Status</TableCell>
                        <TableCell>Last Triggered</TableCell>
                        <TableCell align="center">Enabled</TableCell>
                        <TableCell align="center">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {displayData.thresholds?.map((threshold: any, index: number) => (
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
                            bgcolor: threshold.status === 'violated' ? alpha(theme.palette.error.main, 0.1) : 'transparent',
                          }}
                        >
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {getStatusIcon(threshold.status)}
                              <Typography variant="body2" fontWeight={600}>
                                {threshold.metric}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight={500}>
                              {threshold.campaign}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Typography variant="body2" fontFamily="monospace">
                              {threshold.operator} {threshold.value}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography
                              variant="body2"
                              fontWeight={600}
                              color={threshold.status === 'violated' ? 'error.main' : 'text.primary'}
                            >
                              {threshold.current}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={threshold.status.toUpperCase()}
                              color={getStatusColor(threshold.status) as any}
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption" color="text.secondary">
                              {threshold.lastTriggered}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <FormControlLabel
                              control={
                                <Switch
                                  checked={threshold.enabled}
                                  size="small"
                                  color={threshold.status === 'violated' ? 'error' : 'primary'}
                                />
                              }
                              label=""
                              sx={{ m: 0 }}
                            />
                          </TableCell>
                          <TableCell align="center">
                            <Button
                              size="small"
                              variant="outlined"
                              color="primary"
                              sx={{
                                minWidth: 'auto',
                                px: 2,
                                transition: 'all 0.2s',
                                '&:hover': { transform: 'scale(1.05)' },
                              }}
                            >
                              Edit
                            </Button>
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        <Grid item xs={12}>
          <Fade in timeout={900}>
            <Alert
              severity="warning"
              icon={<TuneRounded />}
              sx={{
                background: `linear-gradient(45deg, ${alpha(theme.palette.warning.main, 0.1)} 0%, ${alpha(theme.palette.warning.light, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette.warning.main, 0.2)}`,
              }}
            >
              <Typography variant="subtitle2">
                <strong>Optimization Tip:</strong> 7 threshold violations detected today.
                Consider adjusting CTR threshold from 2.0% to 1.5% to reduce false positives while maintaining monitoring coverage.
              </Typography>
            </Alert>
          </Fade>
        </Grid>
      </Grid>

      {/* KPI Detail Drawer */}
      <KPIDetailDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={drawerTitle}
        subtitle={drawerSubtitle}
        data={drawerData}
      />
    </DashboardTemplate>
  );
};

export default ThresholdsMonitor;