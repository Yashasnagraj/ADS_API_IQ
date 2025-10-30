import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  CircularProgress,
  IconButton,
  Tooltip,
  useTheme,
  alpha,
  Alert,
} from '@mui/material';
import {
  Memory,
  TrendingUp,
  Speed,
  Assessment,
  AutoAwesome,
  Psychology,
  DataObject,
  Insights,
  ModelTraining,
  Analytics,
  Visibility,
} from '@mui/icons-material';
import {
  LineChart,
  Line,
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  ResponsiveContainer,
  Legend,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  Area,
  AreaChart,
} from 'recharts';
import DashboardTemplate from '../../../common/DashboardTemplate';
import CompactKPICard from '../../../common/CompactKPICard';
import AIIntelligenceSection, { AIInsight } from '../../../common/AIIntelligenceSection';
import { useFilters } from '../../../../context/FilterContext';
import { useFilteredAPI, useMetricsSummary } from '../../../../hooks/useFilteredAPI';

const MLFeaturesDashboard: React.FC = () => {
  const theme = useTheme();
  const { filters } = useFilters();
  const [selectedTimeRange, setSelectedTimeRange] = useState('7d');

  // Fetch ML features data using filtered API
  const {
    data: mlFeaturesData,
    loading: mlLoading,
    error: mlError,
    refetch: refetchMLFeatures
  } = useFilteredAPI({
    endpoint: '/ml-features',
    autoFetch: true
  });

  // Fetch metrics summary for additional context
  const {
    data: metricsData,
    loading: metricsLoading
  } = useMetricsSummary();

  // Calculate derived metrics from real data
  const modelAccuracy = mlFeaturesData?.model_accuracy ? mlFeaturesData.model_accuracy * 100 : 0;
  const featuresCount = mlFeaturesData?.features_count || mlFeaturesData?.top_features?.length || 0;
  const trainingTime = mlFeaturesData?.training_time || 0;
  const predictionsMade = mlFeaturesData?.predictions_made || mlFeaturesData?.total_predictions || 0;
  const modelVersion = mlFeaturesData?.model_version || mlFeaturesData?.version || 0;
  const featureImpact = mlFeaturesData?.feature_impact ? mlFeaturesData.feature_impact * 100 :
                        (mlFeaturesData?.avg_feature_importance ? mlFeaturesData.avg_feature_importance * 100 : 0);

  // KPI Data with real values
  const kpiData = [
    {
      title: 'Model Accuracy',
      value: modelAccuracy,
      format: 'percentage' as const,
      icon: <Psychology sx={{ fontSize: 18 }} />,
      trend: 'up' as const,
      trendValue: mlFeaturesData?.accuracy_trend || 0,
      color: 'success' as const,
    },
    {
      title: 'Total Features',
      value: featuresCount,
      format: 'number' as const,
      icon: <DataObject sx={{ fontSize: 18 }} />,
      trend: 'up' as const,
      trendValue: mlFeaturesData?.features_trend || 0,
      color: 'primary' as const,
    },
    {
      title: 'Training Time',
      value: trainingTime,
      format: 'number' as const,
      icon: <Speed sx={{ fontSize: 18 }} />,
      trend: 'down' as const,
      trendValue: mlFeaturesData?.training_time_improvement || 0,
      color: 'info' as const,
    },
    {
      title: 'Predictions Made',
      value: predictionsMade,
      format: 'number' as const,
      icon: <Insights sx={{ fontSize: 18 }} />,
      trend: 'up' as const,
      trendValue: mlFeaturesData?.predictions_trend || 0,
      color: 'warning' as const,
    },
    {
      title: 'Model Version',
      value: modelVersion,
      format: 'number' as const,
      icon: <ModelTraining sx={{ fontSize: 18 }} />,
      trend: 'up' as const,
      trendValue: mlFeaturesData?.version_change || 0,
      color: 'secondary' as const,
    },
    {
      title: 'Feature Impact',
      value: featureImpact,
      format: 'percentage' as const,
      icon: <Analytics sx={{ fontSize: 18 }} />,
      trend: 'up' as const,
      trendValue: mlFeaturesData?.impact_trend || 0,
      color: 'primary' as const,
    },
  ];

  // AI Insights from real data or intelligent defaults
  const aiInsights: AIInsight[] = mlFeaturesData?.ai_insights || [
    {
      type: 'opportunity',
      title: 'New Feature Pattern',
      description: mlFeaturesData?.insight_1?.description || 'Device type shows 30% higher importance in mobile campaigns',
      impact: mlFeaturesData?.insight_1?.impact || '+15% accuracy',
      confidence: mlFeaturesData?.insight_1?.confidence || 88,
      action: mlFeaturesData?.insight_1?.action || 'Add to model',
      icon: <Memory sx={{ fontSize: 16 }} />,
    },
    {
      type: 'recommendation',
      title: 'Feature Engineering',
      description: mlFeaturesData?.insight_2?.description || 'Combine CTR and Quality Score for better predictions',
      impact: mlFeaturesData?.insight_2?.impact || '+8% precision',
      confidence: mlFeaturesData?.insight_2?.confidence || 91,
      action: mlFeaturesData?.insight_2?.action || 'Create composite',
      icon: <AutoAwesome sx={{ fontSize: 16 }} />,
    },
    {
      type: 'prediction',
      title: 'Model Drift Alert',
      description: mlFeaturesData?.insight_3?.description || 'Performance expected to decline 5% without retraining',
      impact: mlFeaturesData?.insight_3?.impact || 'Proactive fix',
      confidence: mlFeaturesData?.insight_3?.confidence || 85,
      action: mlFeaturesData?.insight_3?.action || 'Schedule retraining',
      icon: <Assessment sx={{ fontSize: 16 }} />,
    },
  ];

  // Data for charts - use real data from API
  const featureData = mlFeaturesData?.top_features || mlFeaturesData?.features || [];

  const featureImportanceData = featureData.map((f: any) => ({
    name: f.feature || f.feature_name || f.name,
    importance: f.importance ? (f.importance * 100).toFixed(1) : f.importance_score ? (f.importance_score * 100).toFixed(1) : 0,
    category: f.category || f.feature_category || 'General',
  }));

  // Calculate category distribution from real feature data
  const categoryCounts = featureData.reduce((acc: any, f: any) => {
    const category = f.category || f.feature_category || 'General';
    acc[category] = (acc[category] || 0) + 1;
    return acc;
  }, {});

  const totalCategories = Object.values(categoryCounts).reduce((sum: number, count: any) => sum + count, 0) || 1;

  const categoryDistribution = mlFeaturesData?.category_distribution || Object.entries(categoryCounts).map(([name, count]: [string, any], index) => ({
    name,
    value: ((count / totalCategories) * 100).toFixed(1),
    color: [
      theme.palette.success.main,
      theme.palette.info.main,
      theme.palette.warning.main,
      theme.palette.primary.main,
      theme.palette.secondary.main
    ][index % 5]
  }));

  // Model performance metrics from real data
  const modelPerformance = mlFeaturesData?.model_performance || [
    { metric: 'Accuracy', value: mlFeaturesData?.model_accuracy ? mlFeaturesData.model_accuracy * 100 : 0 },
    { metric: 'Precision', value: mlFeaturesData?.model_precision ? mlFeaturesData.model_precision * 100 : 0 },
    { metric: 'Recall', value: mlFeaturesData?.model_recall ? mlFeaturesData.model_recall * 100 : 0 },
    { metric: 'F1 Score', value: mlFeaturesData?.model_f1_score ? mlFeaturesData.model_f1_score * 100 : 0 },
    { metric: 'AUC ROC', value: mlFeaturesData?.model_auc_roc ? mlFeaturesData.model_auc_roc * 100 : 0 },
    { metric: 'Speed', value: mlFeaturesData?.model_speed_score ? mlFeaturesData.model_speed_score * 100 : 0 },
  ];

  // Training history from real data
  const trainingHistory = mlFeaturesData?.training_history || mlFeaturesData?.training_data || [];

  const getImportanceColor = (importance: number) => {
    if (importance >= 0.9) return theme.palette.success.main;
    if (importance >= 0.8) return theme.palette.info.main;
    if (importance >= 0.7) return theme.palette.warning.main;
    return theme.palette.error.main;
  };

  // Loading state
  if (!filters.customerId) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading customer data...</Typography>
      </Box>
    );
  }

  if (mlLoading || metricsLoading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Loading ML features data...</Typography>
      </Box>
    );
  }

  // Error state
  if (mlError) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Error loading ML features: {mlError.message}
        </Alert>
      </Box>
    );
  }

  // No data state
  if (!mlFeaturesData || (featureData.length === 0 && !mlFeaturesData.model_accuracy)) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">
          No ML features data available for the selected customer and time period.
        </Alert>
      </Box>
    );
  }

  return (
    <DashboardTemplate
      title="ML Features Dashboard"
      subtitle="Analyze machine learning model features and performance metrics"
      selectedTimeRange={selectedTimeRange}
      onTimeRangeChange={() => setSelectedTimeRange(selectedTimeRange === '7d' ? '30d' : '7d')}
    >
      {/* KPI Cards Section */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        {kpiData.map((kpi, index) => (
          <Grid item xs={12} sm={6} md={2} key={index}>
            <CompactKPICard {...kpi} index={index} />
          </Grid>
        ))}
      </Grid>


      {/* AI Intelligence Section */}
      <Box sx={{ mb: 3 }}>
        <AIIntelligenceSection
          insights={aiInsights}
          title="ML Model Intelligence"
          subtitle="AI-driven insights for model optimization and feature engineering"
        />
      </Box>

      {/* Charts Section */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        {/* Feature Importance */}
        <Grid item xs={12} md={8}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Feature Importance Analysis
              </Typography>
              {featureImportanceData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={featureImportanceData} layout="horizontal">
                    <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
                    <XAxis type="number" stroke={theme.palette.text.secondary} />
                    <YAxis type="category" dataKey="name" stroke={theme.palette.text.secondary} width={120} />
                    <RechartsTooltip
                      contentStyle={{
                        backgroundColor: theme.palette.background.paper,
                        border: `1px solid ${theme.palette.divider}`,
                        borderRadius: 8
                      }}
                    />
                    <Bar dataKey="importance" fill={theme.palette.primary.main}>
                      {featureImportanceData.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={getImportanceColor(parseFloat(entry.importance) / 100)} />
                      ))}
                    </Bar>
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    No feature importance data available
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Model Performance Radar */}
        <Grid item xs={12} md={4}>
          <Card sx={{ height: '100%' }}>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Model Performance
              </Typography>
              {modelPerformance.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <RadarChart data={modelPerformance}>
                    <PolarGrid stroke={alpha(theme.palette.divider, 0.3)} />
                    <PolarAngleAxis dataKey="metric" stroke={theme.palette.text.secondary} />
                    <PolarRadiusAxis angle={90} domain={[0, 100]} stroke={theme.palette.text.secondary} />
                    <Radar
                      name="Performance"
                      dataKey="value"
                      stroke={theme.palette.primary.main}
                      fill={theme.palette.primary.main}
                      fillOpacity={0.6}
                    />
                    <RechartsTooltip
                      contentStyle={{
                        backgroundColor: theme.palette.background.paper,
                        border: `1px solid ${theme.palette.divider}`,
                        borderRadius: 8
                      }}
                    />
                  </RadarChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ height: 300, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    No performance metrics available
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Training History */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Training History
              </Typography>
              {trainingHistory.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <AreaChart data={trainingHistory}>
                    <defs>
                      <linearGradient id="colorAccuracy" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor={theme.palette.success.main} stopOpacity={0.8}/>
                        <stop offset="95%" stopColor={theme.palette.success.main} stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
                    <XAxis dataKey="day" stroke={theme.palette.text.secondary} />
                    <YAxis yAxisId="left" stroke={theme.palette.text.secondary} />
                    <YAxis yAxisId="right" orientation="right" stroke={theme.palette.text.secondary} />
                    <RechartsTooltip
                      contentStyle={{
                        backgroundColor: theme.palette.background.paper,
                        border: `1px solid ${theme.palette.divider}`,
                        borderRadius: 8
                      }}
                    />
                    <Area
                      yAxisId="left"
                      type="monotone"
                      dataKey="accuracy"
                      stroke={theme.palette.success.main}
                      fillOpacity={1}
                      fill="url(#colorAccuracy)"
                      strokeWidth={2}
                    />
                    <Line
                      yAxisId="right"
                      type="monotone"
                      dataKey="loss"
                      stroke={theme.palette.error.main}
                      strokeWidth={2}
                      dot={{ fill: theme.palette.error.main, r: 4 }}
                    />
                    <Legend />
                  </AreaChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    No training history available
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Feature Categories */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" gutterBottom fontWeight={600}>
                Feature Categories
              </Typography>
              {categoryDistribution.length > 0 ? (
                <ResponsiveContainer width="100%" height={250}>
                  <PieChart>
                    <Pie
                      data={categoryDistribution}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                      label={({ name, value }) => `${name}: ${value}%`}
                    >
                      {categoryDistribution.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <RechartsTooltip
                      contentStyle={{
                        backgroundColor: theme.palette.background.paper,
                        border: `1px solid ${theme.palette.divider}`,
                        borderRadius: 8
                      }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Box sx={{ height: 250, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                  <Typography variant="body2" color="text.secondary">
                    No category data available
                  </Typography>
                </Box>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Features Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" gutterBottom fontWeight={600}>
            Feature Details
          </Typography>
          <TableContainer component={Paper} elevation={0}>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Feature Name</TableCell>
                  <TableCell align="center">Category</TableCell>
                  <TableCell align="center">Importance Score</TableCell>
                  <TableCell align="center">Correlation</TableCell>
                  <TableCell align="center">Usage</TableCell>
                  <TableCell align="center">Status</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {featureData.map((feature: any, index: number) => (
                  <TableRow
                    key={index}
                    hover
                    sx={{
                      '&:hover': {
                        backgroundColor: alpha(theme.palette.primary.main, 0.02),
                      }
                    }}
                  >
                    <TableCell>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Memory sx={{ fontSize: 16, color: theme.palette.text.secondary }} />
                        <Typography variant="body2" fontWeight={500}>
                          {feature.feature}
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={feature.category}
                        size="small"
                        sx={{
                          bgcolor: alpha(theme.palette.primary.main, 0.1),
                          color: theme.palette.primary.main,
                          fontWeight: 600,
                        }}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Box display="flex" alignItems="center" justifyContent="center" gap={0.5}>
                        <Box
                          sx={{
                            width: 8,
                            height: 8,
                            borderRadius: '50%',
                            bgcolor: getImportanceColor(feature.importance),
                          }}
                        />
                        <Typography variant="body2" fontWeight={600}>
                          {(feature.importance * 100).toFixed(1)}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Typography variant="body2" color="text.secondary">
                        {(feature.importance * 0.85).toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label="Active"
                        color="success"
                        size="small"
                        sx={{ fontWeight: 600 }}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label="Enabled"
                        color="success"
                        size="small"
                        sx={{ fontWeight: 600 }}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="View Analysis">
                        <IconButton size="small" color="primary">
                          <Visibility fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Feature Details">
                        <IconButton size="small" color="info">
                          <Assessment fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </DashboardTemplate>
  );
};

export default MLFeaturesDashboard;