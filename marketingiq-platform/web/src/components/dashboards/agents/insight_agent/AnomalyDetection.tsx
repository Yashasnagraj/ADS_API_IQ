import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  Alert,
  IconButton,
  Tooltip,
  Button,
  ToggleButton,
  ToggleButtonGroup,
  Fade,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Warning,
  Error,
  Info,
  TrendingUp,
  TrendingDown,
  Refresh,
  FilterList,
  BugReport,
  Speed,
  Timeline,
  Analytics,
  TipsAndUpdates,
  Settings,
} from '@mui/icons-material';
import { ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, Cell, LineChart, Line, Area, ComposedChart } from 'recharts';
import DashboardTemplate from '../../../common/DashboardTemplate';
import CompactKPICard from '../../../common/CompactKPICard';
import AIIntelligenceSection, { AIInsight } from '../../../common/AIIntelligenceSection';
import { insightService } from '../../../../services/api';
import InteractiveKPICard from '../../../kpi/InteractiveKPICard';
import KPIDetailDrawer, { KPIDetailItem } from '../../../kpi/KPIDetailDrawer';
import { EnhancedChart } from '../../../charts/EnhancedChart';

const AnomalyDetection: React.FC = () => {
  const theme = useTheme();
  const [anomalies, setAnomalies] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [filterType, setFilterType] = useState('all');
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerData, setDrawerData] = useState<KPIDetailItem[]>([]);
  const [drawerTitle, setDrawerTitle] = useState('');
  const [drawerSubtitle, setDrawerSubtitle] = useState('');

  useEffect(() => {
    fetchAnomalies();
  }, []);

  const fetchAnomalies = async () => {
    try {
      setLoading(true);
      const data = await insightService.getAnomalies();
      setAnomalies(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching anomalies:', error);
      setAnomalies(mockAnomalies);
    } finally {
      setLoading(false);
    }
  };

  const mockAnomalies = [
    {
      anomaly_id: 'AN001',
      entity_type: 'campaign',
      entity_name: 'Summer Sale 2024',
      metric: 'ctr',
      expected_value: 4.5,
      actual_value: 2.1,
      deviation_percentage: -53,
      severity: 'high',
      detected_at: new Date(Date.now() - 2 * 60 * 60 * 1000).toISOString(),
    },
    {
      anomaly_id: 'AN002',
      entity_type: 'keyword',
      entity_name: 'discount offers',
      metric: 'cpc',
      expected_value: 1.20,
      actual_value: 2.85,
      deviation_percentage: 138,
      severity: 'high',
      detected_at: new Date(Date.now() - 5 * 60 * 60 * 1000).toISOString(),
    },
    {
      anomaly_id: 'AN003',
      entity_type: 'ad_group',
      entity_name: 'Brand Keywords',
      metric: 'conversions',
      expected_value: 150,
      actual_value: 198,
      deviation_percentage: 32,
      severity: 'low',
      detected_at: new Date(Date.now() - 12 * 60 * 60 * 1000).toISOString(),
    },
    {
      anomaly_id: 'AN004',
      entity_type: 'campaign',
      entity_name: 'Retargeting Q4',
      metric: 'impressions',
      expected_value: 50000,
      actual_value: 15000,
      deviation_percentage: -70,
      severity: 'high',
      detected_at: new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString(),
    },
    {
      anomaly_id: 'AN005',
      entity_type: 'keyword',
      entity_name: 'buy online',
      metric: 'quality_score',
      expected_value: 8,
      actual_value: 5,
      deviation_percentage: -37.5,
      severity: 'medium',
      detected_at: new Date(Date.now() - 36 * 60 * 60 * 1000).toISOString(),
    },
  ];

  const scatterData = anomalies.map(a => ({
    x: a.expected_value,
    y: a.actual_value,
    severity: a.severity,
    name: a.entity_name,
    deviation: a.deviation_percentage,
  }));

  const timelineData = [
    { time: '00:00', anomalies: 2, baseline: 3 },
    { time: '04:00', anomalies: 3, baseline: 3 },
    { time: '08:00', anomalies: 8, baseline: 3 },
    { time: '12:00', anomalies: 5, baseline: 3 },
    { time: '16:00', anomalies: 12, baseline: 3 },
    { time: '20:00', anomalies: 7, baseline: 3 },
    { time: '24:00', anomalies: 4, baseline: 3 },
  ];

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'info';
      default:
        return 'default';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'high':
        return <Error sx={{ fontSize: 16 }} />;
      case 'medium':
        return <Warning sx={{ fontSize: 16 }} />;
      case 'low':
        return <Info sx={{ fontSize: 16 }} />;
      default:
        return <Info sx={{ fontSize: 16 }} />;
    }
  };

  const getScatterColor = (severity: string) => {
    switch (severity) {
      case 'high':
        return '#f44336';
      case 'medium':
        return '#ff9800';
      case 'low':
        return '#2196f3';
      default:
        return '#9e9e9e';
    }
  };

  const filteredAnomalies = filterType === 'all'
    ? anomalies
    : anomalies.filter(a => a.severity === filterType);

  // Handle KPI click - open drawer with details
  const handleKPIClick = (severity?: string) => {
    const filteredData = severity
      ? anomalies.filter(a => a.severity === severity)
      : anomalies;

    const drawerItems: KPIDetailItem[] = filteredData.map(a => ({
      id: a.anomaly_id,
      name: a.entity_name,
      value: `${a.deviation_percentage}%`,
      status: a.severity === 'high' ? 'error' : a.severity === 'medium' ? 'warning' : 'info',
      subtitle: `${a.metric.toUpperCase()} - Expected: ${a.expected_value}, Actual: ${a.actual_value}`,
      trend: a.deviation_percentage,
    }));

    setDrawerData(drawerItems);
    setDrawerTitle(severity ? `${severity.charAt(0).toUpperCase() + severity.slice(1)} Severity Anomalies` : 'All Anomalies');
    setDrawerSubtitle(`Detected performance anomalies sorted by severity`);
    setDrawerOpen(true);
  };

  const handleFilterChange = (event: React.MouseEvent<HTMLElement>, newFilter: string) => {
    if (newFilter !== null) {
      setFilterType(newFilter);
    }
  };

  const formatTimeAgo = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / (1000 * 60 * 60));

    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    const days = Math.floor(hours / 24);
    return `${days} day${days > 1 ? 's' : ''} ago`;
  };

  const aiInsights: AIInsight[] = [
    {
      type: 'warning',
      title: 'Critical Performance Drop',
      description: 'CTR dropped 53% for Summer Sale campaign in the last 2 hours - investigate ad fatigue',
      impact: 'High impact on ROI',
      confidence: 95,
      action: 'Investigate Now',
      icon: <Error />,
    },
    {
      type: 'prediction',
      title: 'Anomaly Pattern Detection',
      description: 'Unusual spending spikes detected during 4-8PM timeframe, 138% above expected',
      impact: 'Budget overrun risk',
      confidence: 87,
      action: 'Adjust Bids',
      icon: <Analytics />,
    },
    {
      type: 'recommendation',
      title: 'Prevention Strategy',
      description: 'Set up automated alerts for deviations above 25% to catch anomalies faster',
      impact: 'Prevent future issues',
      confidence: 92,
      action: 'Configure Alerts',
      icon: <BugReport />,
    },
  ];

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <DashboardTemplate
      title="Anomaly Detection"
      subtitle="AI-powered detection and analysis of unusual patterns in campaign performance"
      selectedTimeRange={selectedTimeRange}
      onTimeRangeChange={() => setSelectedTimeRange(selectedTimeRange === '7d' ? '30d' : '7d')}
    >
      {/* Interactive KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Total Anomalies"
            value={anomalies.length}
            format="number"
            icon={<BugReport />}
            trend="up"
            trendValue={23}
            color="warning"
            onClick={() => handleKPIClick()}
            drillDownAvailable={true}
            index={0}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="High Severity"
            value={anomalies.filter(a => a.severity === 'high').length}
            format="number"
            icon={<Error />}
            trend="down"
            trendValue={15}
            color="error"
            onClick={() => handleKPIClick('high')}
            drillDownAvailable={true}
            index={1}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Medium Severity"
            value={anomalies.filter(a => a.severity === 'medium').length}
            format="number"
            icon={<Warning />}
            trend="up"
            trendValue={8}
            color="warning"
            onClick={() => handleKPIClick('medium')}
            drillDownAvailable={true}
            index={2}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Low Severity"
            value={anomalies.filter(a => a.severity === 'low').length}
            format="number"
            icon={<Info />}
            trend="up"
            trendValue={5}
            color="info"
            onClick={() => handleKPIClick('low')}
            drillDownAvailable={true}
            index={3}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Detection Rate"
            value={87}
            format="percentage"
            icon={<Analytics />}
            trend="up"
            trendValue={12}
            color="success"
            index={4}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Avg Response"
            value={4.2}
            format="number"
            icon={<Timeline />}
            trend="down"
            trendValue={18}
            color="primary"
            subtitle="hours"
            index={5}
          />
        </Grid>
      </Grid>

      {/* AI Intelligence Section - Premium insights display */}
      {(() => {
        const monitoredMetrics = 24;
        const activeAnomalies = anomalies.length;
        const falsePositiveCount = 12;
        const highSeverityCount = anomalies.filter(a => a.severity === 'high').length;

        return (
          <Box sx={{ mb: 3 }}>
            <AIIntelligenceSection
              insights={[
                {
                  type: 'opportunity',
                  title: 'Real-Time Anomaly Detection',
                  description: `Monitoring ${monitoredMetrics} metrics across campaigns - ${activeAnomalies} anomalies detected requiring attention (${highSeverityCount} high severity)`,
                  impact: highSeverityCount > 3 ? 'Critical issues detected' : 'System healthy',
                  confidence: 94,
                  action: 'Review Anomalies',
                  icon: <Warning />,
                },
                {
                  type: 'prediction',
                  title: 'Pattern Recognition Insights',
                  description: activeAnomalies > 0
                    ? `AI detected unusual ${anomalies[0]?.metric || 'metric'} changes in ${anomalies[0]?.entity_name || 'campaigns'} - likely due to market shifts or configuration changes`
                    : 'No significant patterns detected - all metrics within expected ranges',
                  impact: activeAnomalies > 0 ? 'Opportunity to investigate' : 'Stable performance',
                  confidence: 87,
                  action: 'View Patterns',
                  icon: <Timeline />,
                },
                {
                  type: 'recommendation',
                  title: 'Alert Threshold Tuning',
                  description: `${falsePositiveCount}% false positive rate detected - recommend adjusting sensitivity thresholds for better accuracy`,
                  impact: 'Reduced alert fatigue',
                  confidence: 91,
                  action: 'Tune Thresholds',
                  icon: <Settings />,
                },
              ]}
            />
          </Box>
        );
      })()}

      {/* KPI Detail Drawer */}
      <KPIDetailDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={drawerTitle}
        subtitle={drawerSubtitle}
        data={drawerData}
        type="table"
        color="warning"
      />

      {/* AI Intelligence Section */}
      <Box sx={{ mb: 3 }}>
        <AIIntelligenceSection insights={aiInsights} />
      </Box>

      <Grid container spacing={3}>

        <Grid item xs={12} md={6}>
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
                    Expected vs Actual Values
                  </Typography>
                  <Tooltip title="Scatter plot showing deviation from expected performance">
                    <IconButton size="small" color="primary">
                      <TipsAndUpdates fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <EnhancedChart
                  height={300}
                  xAxis={{ label: 'Expected Value', dataKey: 'x' }}
                  yAxis={{ label: 'Actual Value' }}
                  showGrid={true}
                  showTooltip={true}
                >
                  <ScatterChart>
                    <RechartsTooltip
                      content={({ active, payload }) => {
                        if (active && payload && payload.length) {
                          const data = payload[0].payload;
                          return (
                            <Box sx={{
                              bgcolor: theme.palette.background.paper,
                              p: 2,
                              border: 1,
                              borderColor: theme.palette.divider,
                              borderRadius: 2,
                              boxShadow: theme.shadows[4],
                            }}>
                              <Typography variant="body2" fontWeight={600}>{data.name}</Typography>
                              <Typography variant="caption" display="block">Expected: {data.x}</Typography>
                              <Typography variant="caption" display="block">Actual: {data.y}</Typography>
                              <Typography
                                variant="caption"
                                display="block"
                                color={data.deviation > 0 ? 'success.main' : 'error.main'}
                                fontWeight={600}
                              >
                                Deviation: {data.deviation}%
                              </Typography>
                            </Box>
                          );
                        }
                        return null;
                      }}
                    />
                    <Scatter name="Anomalies" data={scatterData}>
                      {scatterData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={getScatterColor(entry.severity)} />
                      ))}
                    </Scatter>
                  </ScatterChart>
                </EnhancedChart>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        <Grid item xs={12} md={6}>
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
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Anomaly Detection Timeline
                  </Typography>
                  <Chip
                    icon={<Speed />}
                    label="Live Monitoring"
                    color="error"
                    size="small"
                  />
                </Box>
                <EnhancedChart
                  height={300}
                  xAxis={{ label: 'Time', dataKey: 'time' }}
                  yAxis={{ label: 'Anomaly Count', format: 'number' }}
                  showGrid={true}
                  showTooltip={true}
                  showLegend={true}
                >
                  <ComposedChart data={timelineData}>
                    <Area
                      type="monotone"
                      dataKey="anomalies"
                      fill={alpha(theme.palette.warning.main, 0.3)}
                      stroke={theme.palette.warning.main}
                      strokeWidth={2}
                      fillOpacity={0.4}
                      name="Detected Anomalies"
                    />
                    <Line
                      type="monotone"
                      dataKey="baseline"
                      stroke={theme.palette.success.main}
                      strokeDasharray="5 5"
                      strokeWidth={2}
                      name="Normal Baseline"
                    />
                  </ComposedChart>
                </EnhancedChart>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

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
                    Detected Anomalies
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
                    <Chip
                      icon={<Speed />}
                      label="Real-time"
                      color="primary"
                      size="small"
                      variant="outlined"
                    />
                    <ToggleButtonGroup
                      value={filterType}
                      exclusive
                      onChange={handleFilterChange}
                      size="small"
                    >
                      <ToggleButton value="all">All</ToggleButton>
                      <ToggleButton value="high">High</ToggleButton>
                      <ToggleButton value="medium">Medium</ToggleButton>
                      <ToggleButton value="low">Low</ToggleButton>
                    </ToggleButtonGroup>
                  </Box>
                </Box>

                <TableContainer component={Paper} elevation={0}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Entity</TableCell>
                        <TableCell>Type</TableCell>
                        <TableCell>Metric</TableCell>
                        <TableCell align="right">Expected</TableCell>
                        <TableCell align="right">Actual</TableCell>
                        <TableCell align="right">Deviation</TableCell>
                        <TableCell align="center">Severity</TableCell>
                        <TableCell>Detected</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {filteredAnomalies.map((anomaly) => (
                        <TableRow
                          key={anomaly.anomaly_id}
                          hover
                          sx={{
                            cursor: 'pointer',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              bgcolor: alpha(theme.palette.primary.main, 0.05),
                              transform: 'scale(1.01)',
                            },
                          }}
                        >
                          <TableCell>
                            <Typography variant="body2" fontWeight={500}>
                              {anomaly.entity_name}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Chip
                              label={anomaly.entity_type}
                              size="small"
                              variant="outlined"
                              color="primary"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight={600}>
                              {anomaly.metric.toUpperCase()}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2">
                              {anomaly.expected_value.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={500}>
                              {anomaly.actual_value.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                              {anomaly.deviation_percentage > 0 ? (
                                <TrendingUp sx={{ fontSize: 16, color: theme.palette.success.main }} />
                              ) : (
                                <TrendingDown sx={{ fontSize: 16, color: theme.palette.error.main }} />
                              )}
                              <Typography
                                variant="body2"
                                fontWeight={600}
                                color={anomaly.deviation_percentage > 0 ? 'success.main' : 'error.main'}
                              >
                                {Math.abs(anomaly.deviation_percentage)}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              icon={getSeverityIcon(anomaly.severity)}
                              label={anomaly.severity.toUpperCase()}
                              color={getSeverityColor(anomaly.severity) as any}
                              size="small"
                              variant="filled"
                            />
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption" color="text.secondary">
                              {formatTimeAgo(anomaly.detected_at)}
                            </Typography>
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
              icon={<Warning />}
              sx={{
                background: `linear-gradient(45deg, ${alpha(theme.palette.warning.main, 0.1)} 0%, ${alpha(theme.palette.warning.light, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette.warning.main, 0.2)}`,
              }}
            >
              <Typography variant="subtitle2">
                <strong>Action Required:</strong> {anomalies.filter(a => a.severity === 'high').length} high severity anomalies detected.
                Our AI recommends immediate investigation of unusual patterns in campaign performance metrics.
              </Typography>
            </Alert>
          </Fade>
        </Grid>
      </Grid>
    </DashboardTemplate>
  );
};

export default AnomalyDetection;