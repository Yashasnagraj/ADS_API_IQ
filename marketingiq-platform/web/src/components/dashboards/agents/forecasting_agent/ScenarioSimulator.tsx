import React, { useState, useEffect } from 'react';
import { Box, Card, CardContent, Typography, Grid, LinearProgress, Alert, Chip, IconButton, Tooltip, Fade, useTheme, alpha, Button, Table, TableBody, TableCell, TableContainer, TableHead, TableRow, Paper } from '@mui/material';
import { TrendingUp, Info, PlayArrow, Timeline, Speed, AutoAwesome, TipsAndUpdates, TrendingUpRounded, Analytics, ScienceRounded } from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, ComposedChart, Bar } from 'recharts';
import DashboardTemplate from '../../../common/DashboardTemplate';
import CompactKPICard from '../../../common/CompactKPICard';
import InteractiveKPICard from '../../../kpi/InteractiveKPICard';
import KPIDetailDrawer, { KPIDetailItem } from '../../../kpi/KPIDetailDrawer';
import EnhancedChart from '../../../charts/EnhancedChart';
import AIIntelligenceSection, { AIInsight } from '../../../common/AIIntelligenceSection';
import { forecastService } from '../../../../services/api';

const ScenarioSimulator: React.FC = () => {
  const theme = useTheme();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  // Drawer state
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerData, setDrawerData] = useState<any[]>([]);
  const [drawerTitle, setDrawerTitle] = useState('');
  const [drawerSubtitle, setDrawerSubtitle] = useState('');

  useEffect(() => {
    fetchData();
  }, []);

  const fetchData = async () => {
    try {
      setLoading(true);
      const result = await forecastService.runScenario({
        scenarios: ['conservative', 'moderate', 'aggressive'],
        budget: 10000,
        timeframe: 30
      });

      // Transform API response to expected format or use mock data
      const apiData = result?.data || result;
      if (apiData && typeof apiData === 'object' && apiData.scenarios) {
        const transformedData = {
          ...mockData,
          scenarios: apiData.scenarios,
          recommended: apiData.recommended
        };
        setData(transformedData);
      } else {
        setData(mockData);
      }
    } catch (error) {
      console.error('Error fetching data:', error);
      setData(mockData);
    } finally {
      setLoading(false);
    }
  };

  const mockData = {
    metrics: [
      { label: 'Active Scenarios', value: 4 },
      { label: 'Best ROI', value: 156 },
      { label: 'Avg Confidence', value: 87 },
      { label: 'Risk Score', value: 5.2 },
      { label: 'Success Rate', value: 94 },
      { label: 'Simulations Run', value: 247 },
    ],
    scenarios: [
      { name: 'Conservative', roi: 24, ctr: 3.8, spend: 8500, risk: 2, confidence: 96, status: 'Safe' },
      { name: 'Moderate', roi: 45, ctr: 4.6, spend: 12000, risk: 4, confidence: 89, status: 'Balanced' },
      { name: 'Aggressive', roi: 156, ctr: 6.2, spend: 18500, risk: 8, confidence: 72, status: 'High Risk' },
      { name: 'AI Optimized', roi: 87, ctr: 5.4, spend: 14200, risk: 5, confidence: 91, status: 'Recommended' },
    ]
  };

  const aiInsights: AIInsight[] = [
    {
      type: 'recommendation',
      title: 'AI-Optimized Scenario',
      description: 'AI recommends moderate-aggressive approach with 87% ROI and 91% confidence',
      impact: '87% ROI potential',
      confidence: 91,
      action: 'Implement Scenario',
      icon: <ScienceRounded />,
    },
    {
      type: 'warning',
      title: 'Risk Assessment',
      description: 'Aggressive scenario shows highest ROI but comes with 8/10 risk score',
      impact: 'High volatility risk',
      confidence: 85,
      action: 'Review Risks',
      icon: <Analytics />,
    },
    {
      type: 'prediction',
      title: 'Success Probability',
      description: 'Based on 247 simulations, moderate scenario has 94% success rate',
      impact: 'Stable returns',
      confidence: 94,
      action: 'Consider Safe Option',
      icon: <TrendingUpRounded />,
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

  // Ensure metrics array exists
  if (!displayData.metrics || !Array.isArray(displayData.metrics)) {
    displayData.metrics = mockData.metrics;
  }

  // KPI Click Handlers
  const handleActiveScenariosClick = () => {
    const scenarios = displayData.scenarios || [];
    setDrawerTitle('Active Scenarios');
    setDrawerSubtitle(`${scenarios.length} scenarios currently running`);
    setDrawerData(
      scenarios.map((s: any) => ({
        label: s.name,
        value: s.status,
        subtitle: `Confidence: ${s.confidence}%`,
        trend: s.roi > 50 ? 'up' : 'down',
        trendValue: s.roi
      }))
    );
    setDrawerOpen(true);
  };

  const handleBestROIClick = () => {
    const scenarios = displayData.scenarios || [];
    const sortedByROI = [...scenarios].sort((a, b) => b.roi - a.roi);
    setDrawerTitle('ROI Rankings');
    setDrawerSubtitle('Scenarios sorted by ROI performance');
    setDrawerData(
      sortedByROI.map((s: any) => ({
        label: s.name,
        value: `${s.roi}%`,
        subtitle: `Spend: $${s.spend?.toLocaleString()}`,
        trend: 'up',
        trendValue: s.roi
      }))
    );
    setDrawerOpen(true);
  };

  const handleAvgConfidenceClick = () => {
    const scenarios = displayData.scenarios || [];
    setDrawerTitle('Confidence Levels');
    setDrawerSubtitle('Confidence scores per scenario');
    setDrawerData(
      scenarios.map((s: any) => ({
        label: s.name,
        value: `${s.confidence}%`,
        subtitle: `Risk: ${s.risk}/10`,
        trend: s.confidence >= 85 ? 'up' : 'down',
        trendValue: s.confidence
      }))
    );
    setDrawerOpen(true);
  };

  const handleRiskScoreClick = () => {
    const scenarios = displayData.scenarios || [];
    setDrawerTitle('Risk Assessment');
    setDrawerSubtitle('Risk scores across all scenarios');
    setDrawerData(
      scenarios.map((s: any) => ({
        label: s.name,
        value: `${s.risk}/10`,
        subtitle: s.status,
        trend: s.risk <= 5 ? 'down' : 'up',
        trendValue: s.risk * 10
      }))
    );
    setDrawerOpen(true);
  };

  const handleSuccessRateClick = () => {
    const scenarios = displayData.scenarios || [];
    setDrawerTitle('Success Rate Analysis');
    setDrawerSubtitle('Expected success rates by scenario');
    setDrawerData(
      scenarios.map((s: any) => ({
        label: s.name,
        value: `${s.confidence}%`,
        subtitle: `ROI: ${s.roi}%`,
        trend: 'up',
        trendValue: s.confidence
      }))
    );
    setDrawerOpen(true);
  };

  const handleSimulationsClick = () => {
    const scenarios = displayData.scenarios || [];
    setDrawerTitle('Simulation Details');
    setDrawerSubtitle('247 simulations completed');
    setDrawerData(
      scenarios.map((s: any, idx: number) => ({
        label: s.name,
        value: `${Math.floor(247 / scenarios.length)} runs`,
        subtitle: `Last run: ${idx + 1}h ago`,
        trend: 'up',
        trendValue: 100
      }))
    );
    setDrawerOpen(true);
  };

  return (
    <DashboardTemplate
      title="Scenario Simulator"
      subtitle="AI-powered what-if analysis and scenario planning for campaign optimization"
      selectedTimeRange={selectedTimeRange}
      onTimeRangeChange={() => setSelectedTimeRange(selectedTimeRange === '7d' ? '30d' : '7d')}
    >
      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Active Scenarios"
            value={displayData.metrics[0]?.value || 4}
            format="number"
            icon={<PlayArrow />}
            trend="up"
            trendValue={25}
            color="primary"
            index={0}
            onClick={handleActiveScenariosClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Best ROI"
            value={displayData.metrics[1]?.value || 156}
            format="percentage"
            icon={<TrendingUp />}
            trend="up"
            trendValue={34}
            color="success"
            index={1}
            onClick={handleBestROIClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Avg Confidence"
            value={displayData.metrics[2]?.value || 87}
            format="percentage"
            icon={<Analytics />}
            trend="up"
            trendValue={8}
            color="info"
            index={2}
            onClick={handleAvgConfidenceClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Risk Score"
            value={displayData.metrics[3]?.value || 5.2}
            format="number"
            icon={<Info />}
            trend="down"
            trendValue={12}
            color="warning"
            index={3}
            onClick={handleRiskScoreClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Success Rate"
            value={displayData.metrics[4]?.value || 94}
            format="percentage"
            icon={<AutoAwesome />}
            trend="up"
            trendValue={6}
            color="success"
            index={4}
            onClick={handleSuccessRateClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Simulations"
            value={displayData.metrics[5]?.value || 247}
            format="number"
            icon={<ScienceRounded />}
            trend="up"
            trendValue={45}
            color="secondary"
            index={5}
            onClick={handleSimulationsClick}
            drillDownAvailable={true}
          />
        </Grid>
      </Grid>


      {/* AI Intelligence Section */}
      <Box sx={{ mb: 3 }}>
        <AIIntelligenceSection insights={aiInsights} />
      </Box>

      <Grid container spacing={3}>
        {/* Scenario Comparison Table */}
        <Grid item xs={12}>
          <Fade in timeout={600}>
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
                      icon={<Speed />}
                      label="Real-time Analysis"
                      color="success"
                      size="small"
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
                        <TableCell align="right">ROI</TableCell>
                        <TableCell align="right">CTR</TableCell>
                        <TableCell align="right">Projected Spend</TableCell>
                        <TableCell align="center">Risk Level</TableCell>
                        <TableCell align="center">Confidence</TableCell>
                        <TableCell align="center">Status</TableCell>
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
                            bgcolor: scenario.status === 'Recommended' ? alpha(theme.palette.success.main, 0.1) : 'transparent',
                          }}
                        >
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              <Typography variant="body2" fontWeight={600}>
                                {scenario.name}
                              </Typography>
                              {scenario.status === 'Recommended' && (
                                <Chip
                                  label="AI Recommended"
                                  color="success"
                                  size="small"
                                  variant="outlined"
                                />
                              )}
                            </Box>
                          </TableCell>
                          <TableCell align="right">
                            <Typography
                              variant="body2"
                              fontWeight={600}
                              color={scenario.roi > 80 ? 'success.main' : scenario.roi > 40 ? 'warning.main' : 'text.primary'}
                            >
                              {scenario.roi}%
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={500}>
                              {scenario.ctr}%
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={500}>
                              {scenario.spend?.toLocaleString()}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                              <Box
                                sx={{
                                  width: 8,
                                  height: 8,
                                  borderRadius: '50%',
                                  bgcolor: scenario.risk <= 3 ? theme.palette.success.main :
                                          scenario.risk <= 6 ? theme.palette.warning.main :
                                          theme.palette.error.main
                                }}
                              />
                              <Typography variant="body2">
                                {scenario.risk}/10
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="center">
                            <Typography variant="body2" fontWeight={600}>
                              {scenario.confidence}%
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={scenario.status}
                              color={
                                scenario.status === 'Recommended' ? 'success' :
                                scenario.status === 'Safe' ? 'info' :
                                scenario.status === 'Balanced' ? 'warning' :
                                'error'
                              }
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell align="center">
                            <Button
                              size="small"
                              variant={scenario.status === 'Recommended' ? 'contained' : 'outlined'}
                              color="primary"
                              sx={{
                                minWidth: 'auto',
                                px: 2,
                                transition: 'all 0.2s',
                                '&:hover': { transform: 'scale(1.05)' },
                              }}
                            >
                              {scenario.status === 'Recommended' ? 'Implement' : 'Simulate'}
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
          <Fade in timeout={700}>
            <Alert
              severity="info"
              icon={<ScienceRounded />}
              sx={{
                background: `linear-gradient(45deg, ${alpha(theme.palette.info.main, 0.1)} 0%, ${alpha(theme.palette.info.light, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
              }}
            >
              <Typography variant="subtitle2">
                <strong>Simulation Insight:</strong> Based on 247 simulations, the AI-Optimized scenario offers the best balance of ROI (87%) and risk (5/10) with 91% confidence.
                Consider gradual implementation to minimize risk while maximizing returns.
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

export default ScenarioSimulator;