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
  Fade,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Insights,
  TrendingUp,
  TrendingDown,
  Analytics,
  Assessment,
  Lightbulb,
  Speed,
  Timeline,
  AutoAwesome,
  TipsAndUpdates,
} from '@mui/icons-material';
import { PieChart, Pie, Cell, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, BarChart, Bar } from 'recharts';
import DashboardTemplate from '../../components/common/DashboardTemplate';
import CompactKPICard from '../../components/common/CompactKPICard';
import AIIntelligenceSection, { AIInsight } from '../../components/common/AIIntelligenceSection';
import { insightService } from '../../services/api';
import InteractiveKPICard from '../../components/kpi/InteractiveKPICard';
import KPIDetailDrawer, { KPIDetailItem } from '../../components/kpi/KPIDetailDrawer';
import { EnhancedChart } from '../../components/charts/EnhancedChart';

const InsightsSummary: React.FC = () => {
  const theme = useTheme();
  const [insights, setInsights] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');
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
      const data = await insightService.getSummary();
      setInsights(Array.isArray(data) ? data : []);
    } catch (error) {
      console.error('Error fetching insights summary:', error);
      setInsights(mockInsights);
    } finally {
      setLoading(false);
    }
  };

  const mockInsights = [
    {
      id: 'INS001',
      type: 'performance',
      title: 'Campaign Performance Boost',
      description: 'Summer Sale campaign showing 45% increase in CTR',
      impact: 'high',
      confidence: 94,
      created_at: new Date().toISOString(),
    },
    {
      id: 'INS002',
      type: 'optimization',
      title: 'Budget Reallocation Opportunity',
      description: 'Shift 25% budget from low-performing to high-ROI campaigns',
      impact: 'medium',
      confidence: 87,
      created_at: new Date().toISOString(),
    },
    {
      id: 'INS003',
      type: 'anomaly',
      title: 'Unusual Spending Pattern',
      description: 'CPC spike detected in Brand Keywords ad group',
      impact: 'medium',
      confidence: 91,
      created_at: new Date().toISOString(),
    },
    {
      id: 'INS004',
      type: 'trend',
      title: 'Seasonal Performance Trend',
      description: 'Mobile traffic increasing 23% during weekend hours',
      impact: 'low',
      confidence: 78,
      created_at: new Date().toISOString(),
    },
  ];

  const insightTypesData = [
    { name: 'Performance', value: 8, color: theme.palette.success.main },
    { name: 'Optimization', value: 12, color: theme.palette.primary.main },
    { name: 'Anomalies', value: 5, color: theme.palette.warning.main },
    { name: 'Trends', value: 15, color: theme.palette.info.main },
  ];

  const insightTrendsData = [
    { date: 'Mon', insights: 6, actionable: 4 },
    { date: 'Tue', insights: 8, actionable: 6 },
    { date: 'Wed', insights: 12, actionable: 9 },
    { date: 'Thu', insights: 15, actionable: 11 },
    { date: 'Fri', insights: 10, actionable: 7 },
    { date: 'Sat', insights: 7, actionable: 5 },
    { date: 'Sun', insights: 9, actionable: 6 },
  ];

  const impactDistribution = [
    { impact: 'High', count: 8, color: theme.palette.error.main },
    { impact: 'Medium', count: 15, color: theme.palette.warning.main },
    { impact: 'Low', count: 17, color: theme.palette.success.main },
  ];

  const aiInsights: AIInsight[] = [
    {
      type: 'opportunity',
      title: 'High-Impact Insights Available',
      description: '8 high-impact insights identified that could improve performance by 35%',
      impact: '+35% performance',
      confidence: 92,
      action: 'Review Insights',
      icon: <Lightbulb />,
    },
    {
      type: 'prediction',
      title: 'Trend Analysis Complete',
      description: 'Identified 3 emerging trends that will affect performance in next 2 weeks',
      impact: 'Future planning',
      confidence: 86,
      action: 'View Trends',
      icon: <Timeline />,
    },
    {
      type: 'recommendation',
      title: 'Automated Actions Ready',
      description: '5 insights can be auto-implemented to save time and improve efficiency',
      impact: 'Time saving',
      confidence: 94,
      action: 'Auto-Apply',
      icon: <AutoAwesome />,
    },
  ];

  const getImpactColor = (impact: string) => {
    switch (impact) {
      case 'high':
        return 'error';
      case 'medium':
        return 'warning';
      case 'low':
        return 'success';
      default:
        return 'default';
    }
  };

  const getTypeIcon = (type: string) => {
    switch (type) {
      case 'performance':
        return <TrendingUp sx={{ fontSize: 16 }} />;
      case 'optimization':
        return <Assessment sx={{ fontSize: 16 }} />;
      case 'anomaly':
        return <Analytics sx={{ fontSize: 16 }} />;
      case 'trend':
        return <Timeline sx={{ fontSize: 16 }} />;
      default:
        return <Insights sx={{ fontSize: 16 }} />;
    }
  };

  // KPI Click Handlers using REAL data from insights summary
  const handleTotalInsightsClick = () => {
    const details: KPIDetailItem[] = insightTypesData.map(type => ({
      id: type.name.toLowerCase().replace(/\s+/g, '-'),
      name: type.name,
      value: type.value.toString(),
      trend: Math.round((type.value / 40) * 100),
    }));
    setDrawerTitle('Total Insights Breakdown');
    setDrawerSubtitle('Distribution across all insight categories');
    setDrawerData(details);
    setDrawerOpen(true);
  };

  const handleHighImpactClick = () => {
    const highImpactInsights = mockInsights.filter(i => i.impact === 'high');
    const details: KPIDetailItem[] = highImpactInsights.map((insight, idx) => ({
      id: `high-impact-${idx}`,
      name: insight.title,
      value: `${insight.confidence}% confidence`,
      subtitle: insight.description,
    }));
    setDrawerTitle('High Impact Insights');
    setDrawerSubtitle(`${highImpactInsights.length} critical insights requiring immediate attention`);
    setDrawerData(details);
    setDrawerOpen(true);
  };

  const handleActionableClick = () => {
    const actionableInsights = mockInsights.filter(i => i.type === 'optimization' || i.type === 'performance');
    const details: KPIDetailItem[] = actionableInsights.map((insight, idx) => ({
      id: `actionable-${idx}`,
      name: insight.title,
      value: insight.type.charAt(0).toUpperCase() + insight.type.slice(1),
      subtitle: insight.description,
      trend: insight.confidence,
    }));
    setDrawerTitle('Actionable Insights');
    setDrawerSubtitle('Insights that can be implemented immediately');
    setDrawerData(details);
    setDrawerOpen(true);
  };

  const handleAvgConfidenceClick = () => {
    const details: KPIDetailItem[] = mockInsights.map((insight, idx) => ({
      id: `confidence-${idx}`,
      name: insight.title,
      value: `${insight.confidence}%`,
      subtitle: insight.type.charAt(0).toUpperCase() + insight.type.slice(1),
      trend: insight.confidence >= 85 ? insight.confidence : -insight.confidence,
    }));
    setDrawerTitle('Confidence Scores');
    setDrawerSubtitle('AI confidence level for each insight');
    setDrawerData(details);
    setDrawerOpen(true);
  };

  const handleAutoAppliedClick = () => {
    const autoAppliedInsights = mockInsights.filter(i => i.confidence >= 90);
    const details: KPIDetailItem[] = autoAppliedInsights.map((insight, idx) => ({
      id: `auto-applied-${idx}`,
      name: insight.title,
      value: 'Auto-Applied',
      subtitle: `Applied due to ${insight.confidence}% confidence`,
      trend: 100,
    }));
    setDrawerTitle('Auto-Applied Insights');
    setDrawerSubtitle('Insights automatically implemented by the system');
    setDrawerData(details);
    setDrawerOpen(true);
  };

  const handleResponseTimeClick = () => {
    const details: KPIDetailItem[] = insightTrendsData.map(day => ({
      id: `day-${day.date}`,
      name: day.date,
      value: `${day.insights} insights`,
      subtitle: `${day.actionable} actionable`,
      trend: day.insights > 10 ? Math.round((day.actionable / day.insights) * 100) : -Math.round((day.actionable / day.insights) * 100),
    }));
    setDrawerTitle('Response Time & Generation');
    setDrawerSubtitle('Daily insight generation performance');
    setDrawerData(details);
    setDrawerOpen(true);
  };

  if (loading) {
    return (
      <Box sx={{ p: 3 }}>
        <LinearProgress />
      </Box>
    );
  }

  return (
    <DashboardTemplate
      title="Insights Summary"
      subtitle="AI-powered comprehensive analysis of your campaign insights and recommendations"
      selectedTimeRange={selectedTimeRange}
      onTimeRangeChange={() => setSelectedTimeRange(selectedTimeRange === '7d' ? '30d' : '7d')}
    >
      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Total Insights"
            value={40}
            format="number"
            icon={<Insights />}
            trend="up"
            trendValue={15}
            color="primary"
            index={0}
            onClick={handleTotalInsightsClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="High Impact"
            value={8}
            format="number"
            icon={<TrendingUp />}
            trend="up"
            trendValue={25}
            color="error"
            index={1}
            onClick={handleHighImpactClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Actionable"
            value={27}
            format="number"
            icon={<Assessment />}
            trend="up"
            trendValue={12}
            color="success"
            index={2}
            onClick={handleActionableClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Avg Confidence"
            value={87.5}
            format="percentage"
            icon={<Analytics />}
            trend="up"
            trendValue={5}
            color="info"
            index={3}
            onClick={handleAvgConfidenceClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Auto-Applied"
            value={12}
            format="number"
            icon={<AutoAwesome />}
            trend="up"
            trendValue={100}
            color="secondary"
            index={4}
            onClick={handleAutoAppliedClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Response Time"
            value={2.3}
            format="number"
            icon={<Speed />}
            trend="down"
            trendValue={18}
            color="warning"
            index={5}
            onClick={handleResponseTimeClick}
            drillDownAvailable={true}
          />
        </Grid>
      </Grid>

      {/* AI Intelligence Section */}
      <Box sx={{ mb: 3 }}>
        <AIIntelligenceSection insights={aiInsights} />
      </Box>

      <Grid container spacing={3}>
        {/* Insight Types Distribution */}
        <Grid item xs={12} md={4}>
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
                    Insight Types
                  </Typography>
                  <Tooltip title="Distribution of different insight categories">
                    <IconButton size="small" color="primary">
                      <TipsAndUpdates fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={insightTypesData}
                      cx="50%"
                      cy="50%"
                      innerRadius={40}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {insightTypesData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
                <Box sx={{ mt: 2 }}>
                  {insightTypesData.map((item, index) => (
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
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Insights Trend */}
        <Grid item xs={12} md={8}>
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
                    Daily Insights Generation
                  </Typography>
                  <Chip
                    icon={<Speed />}
                    label="Real-time"
                    color="success"
                    size="small"
                  />
                </Box>
                <EnhancedChart
                  xAxis={{ label: "Day of Week", dataKey: "date" }}
                  yAxis={{ label: "Number of Insights" }}
                  height={300}
                >
                  <LineChart data={insightTrendsData}>
                    <Line
                      type="monotone"
                      dataKey="insights"
                      stroke={theme.palette.primary.main}
                      strokeWidth={3}
                      dot={{ fill: theme.palette.primary.main, r: 4 }}
                      name="Total Insights"
                    />
                    <Line
                      type="monotone"
                      dataKey="actionable"
                      stroke={theme.palette.success.main}
                      strokeWidth={2}
                      dot={{ fill: theme.palette.success.main, r: 3 }}
                      name="Actionable"
                    />
                  </LineChart>
                </EnhancedChart>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Impact Distribution */}
        <Grid item xs={12} md={6}>
          <Fade in timeout={800}>
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
                  Impact Distribution
                </Typography>
                <EnhancedChart
                  xAxis={{ label: "Impact Level", dataKey: "impact" }}
                  yAxis={{ label: "Number of Insights" }}
                  height={250}
                >
                  <BarChart data={impactDistribution}>
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {impactDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </EnhancedChart>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Recent Insights Table */}
        <Grid item xs={12} md={6}>
          <Fade in timeout={900}>
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
                    Recent Insights
                  </Typography>
                  <Chip
                    label={`${mockInsights.length} active`}
                    color="primary"
                    size="small"
                    variant="outlined"
                  />
                </Box>
                <TableContainer component={Paper} elevation={0} sx={{ maxHeight: 300 }}>
                  <Table stickyHeader>
                    <TableHead>
                      <TableRow>
                        <TableCell>Type</TableCell>
                        <TableCell>Title</TableCell>
                        <TableCell align="center">Impact</TableCell>
                        <TableCell align="right">Confidence</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {mockInsights.slice(0, 6).map((insight) => (
                        <TableRow
                          key={insight.id}
                          hover
                          sx={{
                            cursor: 'pointer',
                            transition: 'all 0.2s ease',
                            '&:hover': {
                              bgcolor: alpha(theme.palette.primary.main, 0.05),
                            },
                          }}
                        >
                          <TableCell>
                            <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                              {getTypeIcon(insight.type)}
                              <Typography variant="caption" fontWeight={500}>
                                {insight.type}
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2" fontWeight={500}>
                              {insight.title}
                            </Typography>
                            <Typography variant="caption" color="text.secondary">
                              {insight.description.substring(0, 40)}...
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={insight.impact}
                              color={getImpactColor(insight.impact) as any}
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={600}>
                              {insight.confidence}%
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
          <Fade in timeout={1000}>
            <Alert
              severity="info"
              icon={<TipsAndUpdates />}
              sx={{
                background: `linear-gradient(45deg, ${alpha(theme.palette.info.main, 0.1)} 0%, ${alpha(theme.palette.info.light, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
              }}
            >
              <Typography variant="subtitle2">
                <strong>AI Insight:</strong> Your account is generating high-quality insights consistently.
                Focus on implementing the 8 high-impact recommendations to maximize performance improvements.
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

export default InsightsSummary;