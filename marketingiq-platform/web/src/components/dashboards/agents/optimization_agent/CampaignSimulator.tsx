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
  Button,
  LinearProgress,
  Alert,
  Chip,
  IconButton,
  Tooltip,
  Fade,
  useTheme,
  alpha,
} from '@mui/material';
import {
  TrendingUp,
  Info,
  PlayArrow,
  Psychology,
  Speed,
  AutoAwesome,
  TipsAndUpdates,
  ScienceRounded,
  ModelTraining,
  Science,
} from '@mui/icons-material';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import DashboardTemplate from '../../../common/DashboardTemplate';
import CompactKPICard from '../../../common/CompactKPICard';
import InteractiveKPICard from '../../../kpi/InteractiveKPICard';
import KPIDetailDrawer, { KPIDetailItem } from '../../../kpi/KPIDetailDrawer';
import EnhancedChart from '../../../charts/EnhancedChart';
import AIIntelligenceSection, { AIInsight } from '../../../common/AIIntelligenceSection';
import { optimizationService } from '../../../../services/api';

const CampaignSimulator: React.FC = () => {
  const theme = useTheme();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  // Drawer state for KPI details
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
      const result = await optimizationService.runSimulation({
        campaigns: [],
        budget: 10000,
        duration: 30
      });
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
      { label: 'Simulations Run', value: 24 },
      { label: 'Success Rate', value: 87.5 },
      { label: 'Avg ROI Gain', value: 32 },
      { label: 'Best Scenario', value: 156 },
      { label: 'Risk Score', value: 4.2 },
      { label: 'Confidence', value: 94 },
    ],
    chartData: [
      { scenario: 'Conservative', roi: 15, risk: 2, confidence: 95 },
      { scenario: 'Moderate', roi: 32, risk: 4, confidence: 87 },
      { scenario: 'Aggressive', roi: 56, risk: 7, confidence: 72 },
      { scenario: 'AI Optimized', roi: 48, risk: 5, confidence: 91 },
    ],
    scenarios: [
      { name: 'Current Setup', impressions: 50000, clicks: 2000, conversions: 120, cost: 5000, roi: 12 },
      { name: 'Budget +25%', impressions: 62500, clicks: 2650, conversions: 165, cost: 6250, roi: 18 },
      { name: 'Keyword Optimized', impressions: 48000, clicks: 2400, conversions: 156, cost: 4800, roi: 24 },
      { name: 'AI Recommended', impressions: 55000, clicks: 2750, conversions: 178, cost: 5200, roi: 32 },
    ]
  };

  // KPI Click Handlers
  const handleSimulationsClick = () => {
    const scenarios = displayData.scenarios || mockData.scenarios;
    const items: KPIDetailItem[] = scenarios.map((scenario: any, index: number) => ({
      id: `scenario-${index}`,
      name: scenario.name,
      value: `${scenario.conversions} conversions`,
      status: scenario.name === 'AI Recommended' ? 'success' : scenario.roi > 20 ? 'info' : 'warning',
      trend: index > 0 ? Math.round(((scenario.conversions - scenarios[0].conversions) / scenarios[0].conversions) * 100) : 0,
      subtitle: `ROI: ${scenario.roi}%`,
      metadata: scenario,
    }));
    setDrawerData(items);
    setDrawerTitle('Simulation Scenarios');
    setDrawerSubtitle(`${scenarios.length} scenarios analyzed`);
    setDrawerOpen(true);
  };

  const handleSuccessRateClick = () => {
    const scenarios = displayData.scenarios || mockData.scenarios;
    const items: KPIDetailItem[] = scenarios
      .map((scenario: any, index: number) => {
        const ctr = ((scenario.clicks / scenario.impressions) * 100).toFixed(2);
        const convRate = ((scenario.conversions / scenario.clicks) * 100).toFixed(2);
        return {
          id: `success-${index}`,
          name: scenario.name,
          value: `${convRate}%`,
          status: parseFloat(convRate) > 6 ? 'success' : parseFloat(convRate) > 4 ? 'warning' : 'error',
          trend: index > 0 ? parseFloat(convRate) - parseFloat(((scenarios[0].conversions / scenarios[0].clicks) * 100).toFixed(2)) : 0,
          subtitle: `CTR: ${ctr}%`,
        };
      })
      .sort((a: KPIDetailItem, b: KPIDetailItem) => parseFloat(String(b.value)) - parseFloat(String(a.value)));
    setDrawerData(items);
    setDrawerTitle('Conversion Rate Analysis');
    setDrawerSubtitle('Scenarios ranked by success rate');
    setDrawerOpen(true);
  };

  const handleROIClick = () => {
    const scenarios = displayData.scenarios || mockData.scenarios;
    const items: KPIDetailItem[] = scenarios
      .map((scenario: any, index: number) => ({
        id: `roi-${index}`,
        name: scenario.name,
        value: `${scenario.roi}%`,
        status: scenario.roi > 25 ? 'success' : scenario.roi > 15 ? 'warning' : 'error',
        trend: index > 0 ? scenario.roi - scenarios[0].roi : 0,
        subtitle: `Cost: ₹${scenario.cost.toLocaleString()}`,
      }))
      .sort((a: KPIDetailItem, b: KPIDetailItem) => parseFloat(String(b.value)) - parseFloat(String(a.value)));
    setDrawerData(items);
    setDrawerTitle('ROI Performance');
    setDrawerSubtitle('Return on investment by scenario');
    setDrawerOpen(true);
  };

  const handleBestScenarioClick = () => {
    const scenarios = displayData.scenarios || mockData.scenarios;
    const bestScenario = scenarios.reduce((best: any, current: any): any =>
      current.roi > best.roi ? current : best, scenarios[0]);
    const items: KPIDetailItem[] = [
      { id: 'imp', name: 'Impressions', value: bestScenario.impressions.toLocaleString(), status: 'info', subtitle: 'Total reach' },
      { id: 'clicks', name: 'Clicks', value: bestScenario.clicks.toLocaleString(), status: 'info', subtitle: 'User engagement' },
      { id: 'conv', name: 'Conversions', value: bestScenario.conversions.toString(), status: 'success', subtitle: 'Goals achieved' },
      { id: 'cost', name: 'Cost', value: `₹${bestScenario.cost.toLocaleString()}`, status: 'warning', subtitle: 'Total spend' },
      { id: 'roi', name: 'ROI', value: `${bestScenario.roi}%`, status: 'success', subtitle: 'Return on investment' },
    ];
    setDrawerData(items);
    setDrawerTitle(`Best Scenario: ${bestScenario.name}`);
    setDrawerSubtitle('Optimal performance metrics');
    setDrawerOpen(true);
  };

  const handleRiskScoreClick = () => {
    const chartData = displayData.chartData || mockData.chartData;
    const items: KPIDetailItem[] = chartData
      .map((item: any) => ({
        id: item.scenario,
        name: item.scenario,
        value: `${item.risk}/10`,
        status: item.risk < 4 ? 'success' : item.risk < 7 ? 'warning' : 'error',
        subtitle: `ROI: ${item.roi}%`,
      }))
      .sort((a: any, b: any) => parseFloat(a.value) - parseFloat(b.value));
    setDrawerData(items);
    setDrawerTitle('Risk Assessment');
    setDrawerSubtitle('Risk scores by scenario');
    setDrawerOpen(true);
  };

  const handleConfidenceClick = () => {
    const chartData = displayData.chartData || mockData.chartData;
    const items: KPIDetailItem[] = chartData
      .map((item: any) => ({
        id: item.scenario,
        name: item.scenario,
        value: `${item.confidence}%`,
        status: item.confidence > 90 ? 'success' : item.confidence > 80 ? 'info' : 'warning',
        subtitle: `Risk: ${item.risk}/10`,
      }))
      .sort((a: any, b: any) => parseFloat(b.value) - parseFloat(a.value));
    setDrawerData(items);
    setDrawerTitle('Confidence Levels');
    setDrawerSubtitle('AI prediction confidence by scenario');
    setDrawerOpen(true);
  };

  const aiInsights: AIInsight[] = [
    {
      type: 'prediction',
      title: 'AI-Optimized Scenario Best',
      description: 'AI-recommended configuration shows 32% ROI improvement with 91% confidence',
      impact: '+32% ROI potential',
      confidence: 91,
      action: 'Run Simulation',
      icon: <Psychology />,
    },
    {
      type: 'warning',
      title: 'High-Risk Scenarios Detected',
      description: 'Aggressive scenarios show high ROI but come with increased risk and lower confidence',
      impact: 'Risk management needed',
      confidence: 85,
      action: 'Review Risks',
      icon: <Science />,
    },
    {
      type: 'recommendation',
      title: 'Gradual Implementation',
      description: 'Start with moderate changes and progressively implement optimizations',
      impact: 'Safer optimization path',
      confidence: 92,
      action: 'Start Conservative',
      icon: <AutoAwesome />,
    },
  ];

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
      title="Campaign Simulator"
      subtitle="AI-powered campaign scenario simulation and what-if analysis"
      selectedTimeRange={selectedTimeRange}
      onTimeRangeChange={() => setSelectedTimeRange(selectedTimeRange === '7d' ? '30d' : '7d')}
    >
      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Simulations Run"
            value={displayData.metrics[0]?.value || 24}
            format="number"
            icon={<ScienceRounded />}
            trend="up"
            trendValue={12}
            color="primary"
            index={0}
            onClick={handleSimulationsClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Success Rate"
            value={displayData.metrics[1]?.value || 87.5}
            format="percentage"
            icon={<ModelTraining />}
            trend="up"
            trendValue={5}
            color="success"
            index={1}
            onClick={handleSuccessRateClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Avg ROI Gain"
            value={displayData.metrics[2]?.value || 32}
            format="percentage"
            icon={<TrendingUp />}
            trend="up"
            trendValue={8}
            color="success"
            index={2}
            onClick={handleROIClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Best Scenario"
            value={displayData.metrics[3]?.value || 156}
            format="percentage"
            icon={<Psychology />}
            trend="up"
            trendValue={23}
            color="error"
            index={3}
            onClick={handleBestScenarioClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Risk Score"
            value={displayData.metrics[4]?.value || 4.2}
            format="number"
            icon={<Science />}
            trend="down"
            trendValue={12}
            color="warning"
            index={4}
            onClick={handleRiskScoreClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Confidence"
            value={displayData.metrics[5]?.value || 94}
            format="percentage"
            icon={<AutoAwesome />}
            trend="up"
            trendValue={6}
            color="info"
            index={5}
            onClick={handleConfidenceClick}
            drillDownAvailable={true}
          />
        </Grid>
      </Grid>


      {/* AI Intelligence Section */}
      <Box sx={{ mb: 3 }}>
        <AIIntelligenceSection insights={aiInsights} />
      </Box>

      <Grid container spacing={3}>
        {/* Risk vs ROI Chart */}
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
                    Scenario Risk vs ROI Analysis
                  </Typography>
                  <Tooltip title="Shows risk-return profile for different scenarios">
                    <IconButton size="small" color="primary">
                      <TipsAndUpdates fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <EnhancedChart
                  height={300}
                  xAxis={{ label: 'Scenario', dataKey: 'scenario' }}
                  yAxis={{ label: 'Score', format: 'number' }}
                >
                  <AreaChart data={displayData.chartData}>
                    <Area
                      type="monotone"
                      dataKey="roi"
                      stroke={theme.palette.success.main}
                      fill={alpha(theme.palette.success.main, 0.3)}
                      name="ROI %"
                    />
                    <Area
                      type="monotone"
                      dataKey="risk"
                      stroke={theme.palette.error.main}
                      fill={alpha(theme.palette.error.main, 0.3)}
                      name="Risk Score"
                    />
                  </AreaChart>
                </EnhancedChart>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Confidence Scores */}
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
                <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
                  <Typography variant="h6">
                    Scenario Confidence
                  </Typography>
                  <Chip
                    icon={<Psychology />}
                    label="AI Analysis"
                    color="primary"
                    size="small"
                  />
                </Box>
                <EnhancedChart
                  height={250}
                  xAxis={{ label: 'Scenario', dataKey: 'scenario' }}
                  yAxis={{ label: 'Confidence %', format: 'percentage' }}
                >
                  <BarChart data={displayData.chartData}>
                    <Bar
                      dataKey="confidence"
                      fill={theme.palette.primary.main}
                      radius={[4, 4, 0, 0]}
                      name="Confidence %"
                    />
                  </BarChart>
                </EnhancedChart>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Scenario Comparison Table */}
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
                    Scenario Performance Comparison
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1 }}>
                    <Chip
                      icon={<PlayArrow />}
                      label="Ready to Simulate"
                      color="success"
                      size="small"
                      variant="outlined"
                    />
                    <Button
                      variant="contained"
                      color="primary"
                      startIcon={<ScienceRounded />}
                      size="small"
                    >
                      Run New Simulation
                    </Button>
                  </Box>
                </Box>
                <TableContainer component={Paper} elevation={0}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Scenario</TableCell>
                        <TableCell align="right">Impressions</TableCell>
                        <TableCell align="right">Clicks</TableCell>
                        <TableCell align="right">Conversions</TableCell>
                        <TableCell align="right">Cost</TableCell>
                        <TableCell align="right">ROI</TableCell>
                        <TableCell align="center">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {displayData.scenarios?.map((scenario: any, index: number) => (
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
                            bgcolor: scenario.name === 'AI Recommended' ? alpha(theme.palette.success.main, 0.1) : 'transparent',
                          }}
                        >
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body2" fontWeight={600}>
                                {scenario.name}
                              </Typography>
                              {scenario.name === 'AI Recommended' && (
                                <Chip
                                  label="Recommended"
                                  color="success"
                                  size="small"
                                  variant="outlined"
                                />
                              )}
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={500}>
                              {scenario.impressions?.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={500}>
                              {scenario.clicks?.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={500}>
                              {scenario.conversions}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={500}>
                              {scenario.cost?.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography
                              variant="body2"
                              fontWeight={600}
                              color={scenario.roi > 20 ? 'success.main' : scenario.roi > 15 ? 'warning.main' : 'error.main'}
                            >
                              {scenario.roi}%
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Button
                              size="small"
                              variant={scenario.name === 'AI Recommended' ? 'contained' : 'outlined'}
                              color="primary"
                              sx={{
                                minWidth: 'auto',
                                px: 2,
                                transition: 'all 0.2s',
                                '&:hover': { transform: 'scale(1.05)' },
                              }}
                            >
                              {scenario.name === 'Current Setup' ? 'Current' : 'Simulate'}
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
              severity="success"
              icon={<ScienceRounded />}
              sx={{
                background: `linear-gradient(45deg, ${alpha(theme.palette.success.main, 0.1)} 0%, ${alpha(theme.palette.success.light, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette.success.main, 0.2)}`,
              }}
            >
              <Typography variant="subtitle2">
                <strong>Simulation Complete:</strong> AI analysis shows the recommended scenario could improve ROI by 32% with high confidence (91%).
                Consider implementing changes gradually to minimize risk while maximizing returns.
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
        type="list"
        color="primary"
      />
    </DashboardTemplate>
  );
};

export default CampaignSimulator;