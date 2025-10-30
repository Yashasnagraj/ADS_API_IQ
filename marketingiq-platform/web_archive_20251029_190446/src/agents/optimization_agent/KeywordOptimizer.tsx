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
  Search,
  Star,
  Visibility,
  Speed,
  AutoAwesome,
  TipsAndUpdates,
  TuneRounded,
  WorkspacePremium,
} from '@mui/icons-material';
import { LineChart, Line, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, ResponsiveContainer, ScatterChart, Scatter, Cell } from 'recharts';
import DashboardTemplate from '../../components/common/DashboardTemplate';
import CompactKPICard from '../../components/common/CompactKPICard';
import AIIntelligenceSection, { AIInsight } from '../../components/common/AIIntelligenceSection';
import InteractiveKPICard from '../../components/kpi/InteractiveKPICard';
import KPIDetailDrawer, { KPIDetailItem } from '../../components/kpi/KPIDetailDrawer';
import { EnhancedChart } from '../../components/charts/EnhancedChart';
import { optimizationService } from '../../services/api';

const KeywordOptimizer: React.FC = () => {
  const theme = useTheme();
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  // Drawer state for KPI drill-down
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
      const result = await optimizationService.getKeywordRecommendations();

      // Transform API response to expected format or use mock data
      const apiData = result?.data || result;
      if (apiData && Array.isArray(apiData)) {
        const transformedData = {
          ...mockData,
          recommendations: apiData
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
      { label: 'Total Keywords', value: 248 },
      { label: 'Optimizable', value: 89 },
      { label: 'High Potential', value: 24 },
      { label: 'Avg Quality Score', value: 7.2 },
      { label: 'Performance Gain', value: 34 },
      { label: 'Cost Reduction', value: 18 },
    ],
    chartData: [
      { date: 'Mon', current: 4.2, optimized: 5.8 },
      { date: 'Tue', current: 4.5, optimized: 6.2 },
      { date: 'Wed', current: 4.1, optimized: 5.9 },
      { date: 'Thu', current: 4.7, optimized: 6.4 },
      { date: 'Fri', current: 4.9, optimized: 6.7 },
      { date: 'Sat', current: 4.3, optimized: 6.0 },
      { date: 'Sun', current: 4.6, optimized: 6.3 },
    ],
    recommendations: [
      { keyword: 'digital marketing', action: 'Increase bid by 25%', currentBid: 1.20, suggestedBid: 1.50, impact: 'High', confidence: 92, qualityScore: 8 },
      { keyword: 'seo services', action: 'Add negative keywords', currentBid: 2.10, suggestedBid: 2.10, impact: 'Medium', confidence: 87, qualityScore: 6 },
      { keyword: 'ppc management', action: 'Improve ad relevance', currentBid: 3.20, suggestedBid: 2.80, impact: 'High', confidence: 94, qualityScore: 4 },
      { keyword: 'content marketing', action: 'Expand match types', currentBid: 1.80, suggestedBid: 1.80, impact: 'Medium', confidence: 78, qualityScore: 7 },
    ]
  };

  const qualityScoreDistribution = [
    { score: '1-3', count: 12, color: theme.palette.error.main },
    { score: '4-6', count: 45, color: theme.palette.warning.main },
    { score: '7-8', count: 156, color: theme.palette.success.main },
    { score: '9-10', count: 35, color: theme.palette.primary.main },
  ];

  const aiInsights: AIInsight[] = [
    {
      type: 'opportunity',
      title: 'High-Value Keywords Identified',
      description: '24 keywords with quality scores above 8 that could benefit from increased bids',
      impact: '+34% CTR potential',
      confidence: 92,
      action: 'Optimize Bids',
      icon: <TrendingUp />,
    },
    {
      type: 'warning',
      title: 'Low-Quality Keywords',
      description: '12 keywords with quality scores below 4 are draining budget without conversions',
      impact: '18% cost reduction',
      confidence: 87,
      action: 'Pause/Improve',
      icon: <Star />,
    },
    {
      type: 'recommendation',
      title: 'Keyword Expansion Opportunity',
      description: 'Found 67 related keywords with high search volume and low competition',
      impact: '+45% reach expansion',
      confidence: 85,
      action: 'Add Keywords',
      icon: <AutoAwesome />,
    },
  ];

  // KPI Click Handlers using REAL data from recommendations
  const handleTotalKeywordsClick = () => {
    const keywords = (displayData.recommendations || mockData.recommendations).map((rec: any, idx: number) => ({
      id: `keyword-${idx}`,
      name: rec.keyword,
      value: `Bid: ₹${rec.currentBid?.toFixed(2)}`,
      status: rec.qualityScore >= 7 ? 'success' : rec.qualityScore >= 4 ? 'warning' : 'error',
      subtitle: `Quality Score: ${rec.qualityScore}/10`,
      trend: rec.suggestedBid > rec.currentBid ?
        Math.round(((rec.suggestedBid - rec.currentBid) / rec.currentBid) * 100) :
        -Math.round(((rec.currentBid - rec.suggestedBid) / rec.currentBid) * 100),
    }));
    setDrawerData(keywords);
    setDrawerTitle('All Keywords');
    setDrawerSubtitle(`${displayData.metrics[0]?.value || 248} total keywords in your account`);
    setDrawerOpen(true);
  };

  const handleOptimizableClick = () => {
    const optimizable = (displayData.recommendations || mockData.recommendations)
      .filter((rec: any) => rec.currentBid !== rec.suggestedBid)
      .map((rec: any, idx: number) => ({
        id: `opt-${idx}`,
        name: rec.keyword,
        value: `${rec.action}`,
        status: rec.impact === 'High' ? 'warning' : 'info',
        subtitle: `Current: ₹${rec.currentBid?.toFixed(2)} → Suggested: ₹${rec.suggestedBid?.toFixed(2)}`,
        trend: rec.confidence,
      }));
    setDrawerData(optimizable);
    setDrawerTitle('Optimizable Keywords');
    setDrawerSubtitle(`${displayData.metrics[1]?.value || 89} keywords with optimization opportunities`);
    setDrawerOpen(true);
  };

  const handleHighPotentialClick = () => {
    const highPotential = (displayData.recommendations || mockData.recommendations)
      .filter((rec: any) => rec.impact === 'High')
      .map((rec: any, idx: number) => ({
        id: `high-${idx}`,
        name: rec.keyword,
        value: `Confidence: ${rec.confidence}%`,
        status: 'success',
        subtitle: `${rec.action}`,
        trend: rec.qualityScore >= 7 ? rec.qualityScore : -rec.qualityScore,
      }));
    setDrawerData(highPotential);
    setDrawerTitle('High Potential Keywords');
    setDrawerSubtitle(`${displayData.metrics[2]?.value || 24} keywords with high impact potential`);
    setDrawerOpen(true);
  };

  const handleQualityScoreClick = () => {
    const byQualityScore = (displayData.recommendations || mockData.recommendations)
      .sort((a: any, b: any) => b.qualityScore - a.qualityScore)
      .map((rec: any, idx: number) => ({
        id: `qs-${idx}`,
        name: rec.keyword,
        value: `${rec.qualityScore}/10`,
        status: rec.qualityScore >= 7 ? 'success' : rec.qualityScore >= 4 ? 'warning' : 'error',
        subtitle: `Bid: ₹${rec.currentBid?.toFixed(2)}`,
      }));
    setDrawerData(byQualityScore);
    setDrawerTitle('Quality Score Analysis');
    setDrawerSubtitle(`Average quality score: ${displayData.metrics[3]?.value || 7.2}/10`);
    setDrawerOpen(true);
  };

  const handlePerformanceGainClick = () => {
    const gainOpportunities = (displayData.recommendations || mockData.recommendations)
      .filter((rec: any) => rec.suggestedBid > rec.currentBid)
      .map((rec: any, idx: number) => ({
        id: `gain-${idx}`,
        name: rec.keyword,
        value: `+${Math.round(((rec.suggestedBid - rec.currentBid) / rec.currentBid) * 100)}%`,
        status: 'success',
        subtitle: `Increase bid from ₹${rec.currentBid?.toFixed(2)} to ₹${rec.suggestedBid?.toFixed(2)}`,
        trend: rec.confidence,
      }));
    setDrawerData(gainOpportunities);
    setDrawerTitle('Performance Gain Opportunities');
    setDrawerSubtitle(`Potential ${displayData.metrics[4]?.value || 34}% overall performance improvement`);
    setDrawerOpen(true);
  };

  const handleCostReductionClick = () => {
    const costSavings = (displayData.recommendations || mockData.recommendations)
      .filter((rec: any) => rec.suggestedBid < rec.currentBid || rec.qualityScore < 4)
      .map((rec: any, idx: number) => ({
        id: `cost-${idx}`,
        name: rec.keyword,
        value: rec.suggestedBid < rec.currentBid ?
          `-${Math.round(((rec.currentBid - rec.suggestedBid) / rec.currentBid) * 100)}%` :
          'Pause recommended',
        status: 'error',
        subtitle: rec.suggestedBid < rec.currentBid ?
          `Reduce bid from ₹${rec.currentBid?.toFixed(2)} to ₹${rec.suggestedBid?.toFixed(2)}` :
          `Low quality score: ${rec.qualityScore}/10`,
      }));
    setDrawerData(costSavings);
    setDrawerTitle('Cost Reduction Opportunities');
    setDrawerSubtitle(`Potential ${displayData.metrics[5]?.value || 18}% cost savings`);
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

  // Ensure metrics array exists
  if (!displayData.metrics || !Array.isArray(displayData.metrics)) {
    displayData.metrics = mockData.metrics;
  }

  return (
    <DashboardTemplate
      title="Keyword Optimizer"
      subtitle="AI-powered keyword analysis and optimization recommendations"
      selectedTimeRange={selectedTimeRange}
      onTimeRangeChange={() => setSelectedTimeRange(selectedTimeRange === '7d' ? '30d' : '7d')}
    >
      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Total Keywords"
            value={displayData.metrics[0]?.value || 248}
            format="number"
            icon={<Search />}
            trend="up"
            trendValue={12}
            color="primary"
            index={0}
            onClick={handleTotalKeywordsClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Optimizable"
            value={displayData.metrics[1]?.value || 89}
            format="number"
            icon={<TuneRounded />}
            trend="up"
            trendValue={15}
            color="warning"
            index={1}
            onClick={handleOptimizableClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="High Potential"
            value={displayData.metrics[2]?.value || 24}
            format="number"
            icon={<WorkspacePremium />}
            trend="up"
            trendValue={23}
            color="success"
            index={2}
            onClick={handleHighPotentialClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Avg Quality Score"
            value={displayData.metrics[3]?.value || 7.2}
            format="number"
            icon={<Star />}
            trend="up"
            trendValue={8}
            color="info"
            index={3}
            onClick={handleQualityScoreClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Performance Gain"
            value={displayData.metrics[4]?.value || 34}
            format="percentage"
            icon={<TrendingUp />}
            trend="up"
            trendValue={18}
            color="success"
            index={4}
            onClick={handlePerformanceGainClick}
            drillDownAvailable={true}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={2}>
          <InteractiveKPICard
            title="Cost Reduction"
            value={displayData.metrics[5]?.value || 18}
            format="percentage"
            icon={<TuneRounded />}
            trend="down"
            trendValue={12}
            color="error"
            index={5}
            onClick={handleCostReductionClick}
            drillDownAvailable={true}
          />
        </Grid>
      </Grid>

      {/* AI Intelligence Section */}
      <Box sx={{ mb: 3 }}>
        <AIIntelligenceSection insights={aiInsights} />
      </Box>

      <Grid container spacing={3}>
        {/* Performance Comparison Chart */}
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
                    Current vs Optimized Performance
                  </Typography>
                  <Tooltip title="Shows potential CTR improvement after optimization">
                    <IconButton size="small" color="primary">
                      <TipsAndUpdates fontSize="small" />
                    </IconButton>
                  </Tooltip>
                </Box>
                <EnhancedChart
                  height={300}
                  xAxis={{ label: 'Day of Week', dataKey: 'date' }}
                  yAxis={{ label: 'CTR (%)', format: 'decimal' }}
                  showLegend={true}
                >
                  <LineChart data={displayData.chartData}>
                    <Line
                      type="monotone"
                      dataKey="current"
                      stroke={theme.palette.warning.main}
                      strokeWidth={3}
                      dot={{ fill: theme.palette.warning.main, r: 4 }}
                      name="Current CTR"
                    />
                    <Line
                      type="monotone"
                      dataKey="optimized"
                      stroke={theme.palette.success.main}
                      strokeWidth={3}
                      dot={{ fill: theme.palette.success.main, r: 4 }}
                      name="Optimized CTR"
                    />
                  </LineChart>
                </EnhancedChart>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Quality Score Distribution */}
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
                    Quality Score Distribution
                  </Typography>
                  <Chip
                    icon={<Star />}
                    label="QS Analysis"
                    color="primary"
                    size="small"
                  />
                </Box>
                <EnhancedChart
                  height={250}
                  xAxis={{ label: 'Quality Score Range', dataKey: 'score' }}
                  yAxis={{ label: 'Number of Keywords', format: 'number' }}
                >
                  <BarChart data={qualityScoreDistribution}>
                    <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                      {qualityScoreDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Bar>
                  </BarChart>
                </EnhancedChart>
                <Box sx={{ mt: 2 }}>
                  {qualityScoreDistribution.map((item, index) => (
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
                        Score {item.score}
                      </Typography>
                      <Typography variant="caption" fontWeight={600}>
                        {item.count}
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Fade>
        </Grid>

        {/* Optimization Recommendations */}
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
                    Keyword Optimization Recommendations
                  </Typography>
                  <Chip
                    icon={<AutoAwesome />}
                    label={`${displayData.recommendations?.length || 4} Actions Available`}
                    color="success"
                    size="small"
                    variant="outlined"
                  />
                </Box>
                <TableContainer component={Paper} elevation={0}>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell>Keyword</TableCell>
                        <TableCell>Recommendation</TableCell>
                        <TableCell align="right">Current Bid</TableCell>
                        <TableCell align="right">Suggested Bid</TableCell>
                        <TableCell align="center">Quality Score</TableCell>
                        <TableCell align="center">Impact</TableCell>
                        <TableCell align="right">Confidence</TableCell>
                        <TableCell align="center">Actions</TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {(displayData.recommendations || mockData.recommendations).map((row: any, index: number) => (
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
                          }}
                        >
                          <TableCell>
                            <Typography variant="body2" fontWeight={600}>
                              {row.keyword}
                            </Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="body2">
                              {row.action}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={500}>
                              {row.currentBid?.toFixed(2)}
                            </Typography>
                          </TableCell>
                          <TableCell align="right">
                            <Typography
                              variant="body2"
                              fontWeight={600}
                              color={row.suggestedBid > row.currentBid ? 'error.main' : 'success.main'}
                            >
                              {row.suggestedBid?.toFixed(2)}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 1 }}>
                              <Star
                                sx={{
                                  fontSize: 16,
                                  color: row.qualityScore >= 7 ? theme.palette.success.main :
                                         row.qualityScore >= 4 ? theme.palette.warning.main :
                                         theme.palette.error.main
                                }}
                              />
                              <Typography variant="body2" fontWeight={600}>
                                {row.qualityScore}/10
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={row.impact}
                              color={row.impact === 'High' ? 'error' : row.impact === 'Medium' ? 'warning' : 'success'}
                              size="small"
                              variant="outlined"
                            />
                          </TableCell>
                          <TableCell align="right">
                            <Typography variant="body2" fontWeight={600}>
                              {row.confidence}%
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Button
                              size="small"
                              variant="contained"
                              color="primary"
                              sx={{
                                minWidth: 'auto',
                                px: 2,
                                transition: 'all 0.2s',
                                '&:hover': { transform: 'scale(1.05)' },
                              }}
                            >
                              Apply
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
              severity="info"
              icon={<TipsAndUpdates />}
              sx={{
                background: `linear-gradient(45deg, ${alpha(theme.palette.info.main, 0.1)} 0%, ${alpha(theme.palette.info.light, 0.05)} 100%)`,
                border: `1px solid ${alpha(theme.palette.info.main, 0.2)}`,
              }}
            >
              <Typography variant="subtitle2">
                <strong>AI Optimization Insight:</strong> Implementing these keyword optimizations could improve your overall CTR by 34% and reduce costs by 18%.
                Focus on the 24 high-potential keywords for maximum impact.
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
        showTopCount={10}
        color="primary"
      />
    </DashboardTemplate>
  );
};

export default KeywordOptimizer;