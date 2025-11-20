import React, { useState, useEffect } from 'react';
import {
  Box,
  Typography,
  Card,
  CardContent,
  Grid,
  Alert,
  AlertTitle,
  Chip,
  Button,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
  Paper,
  Stack,
  Divider,
  LinearProgress,
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import ErrorIcon from '@mui/icons-material/Error';
import InfoIcon from '@mui/icons-material/Info';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import TrendingFlatIcon from '@mui/icons-material/TrendingFlat';
import RefreshIcon from '@mui/icons-material/Refresh';
import NotificationsActiveIcon from '@mui/icons-material/NotificationsActive';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Area, AreaChart } from 'recharts';
import { AIBadge, AILoadingState, GradientCard, ConfidenceScore } from '../../ai/shared';
import { EmptyState } from '../../common/EmptyState';
import { useFilters } from '../../../context/FilterContext';
import { colors } from '../../../theme/designTokens';
import { useSnackbar } from 'notistack';
import axios from 'axios';

const API_BASE = 'http://localhost:8000/api/ai';

interface AlertData {
  id: string;
  severity: 'critical' | 'warning' | 'info';
  type: string;
  title: string;
  description: string;
  impact: string;
  recommendation: string;
  metric_value?: number;
  threshold?: number;
  trend?: string;
  affected_entity?: string;
  created_at: string;
}

export const PredictiveAlertsPage: React.FC = () => {
  const [alerts, setAlerts] = useState<AlertData[]>([]);
  const [loading, setLoading] = useState(false);
  const [forecastData, setForecastData] = useState<any>(null);
  const [forecastMetric, setForecastMetric] = useState<'spend' | 'clicks' | 'conversions'>('spend');
  const [alertStats, setAlertStats] = useState({ total: 0, critical: 0, warnings: 0, info: 0 });
  const [days, setDays] = useState(7);
  const { filters } = useFilters();
  const { enqueueSnackbar } = useSnackbar();

  useEffect(() => {
    if (filters.customerId) {
      loadAlerts();
      loadForecast();
    }
  }, [filters.customerId, days]);

  useEffect(() => {
    if (filters.customerId) {
      loadForecast();
    }
  }, [forecastMetric]);

  const loadAlerts = async () => {
    setLoading(true);
    try {
      const response = await axios.get(`${API_BASE}/predictions/alerts`, {
        params: { customer_id: filters.customerId, days },
      });

      setAlerts(response.data.alerts || []);
      setAlertStats({
        total: response.data.total_alerts || 0,
        critical: response.data.critical || 0,
        warnings: response.data.warnings || 0,
        info: response.data.info || 0,
      });

      if (response.data.critical > 0) {
        enqueueSnackbar(`${response.data.critical} critical alert(s) detected!`, { variant: 'error' });
      }
    } catch (error) {
      console.error('Error loading alerts:', error);
      enqueueSnackbar('Failed to load predictive alerts', { variant: 'error' });
    } finally {
      setLoading(false);
    }
  };

  const loadForecast = async () => {
    try {
      const response = await axios.get(`${API_BASE}/predictions/forecast`, {
        params: {
          customer_id: filters.customerId,
          metric: forecastMetric,
          days_ahead: 7,
        },
      });

      if (response.data.success) {
        setForecastData(response.data);
      }
    } catch (error) {
      console.error('Error loading forecast:', error);
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon />;
      case 'warning':
        return <WarningIcon />;
      case 'info':
        return <InfoIcon />;
      default:
        return <InfoIcon />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return colors.error.main;
      case 'warning':
        return colors.warning.main;
      case 'info':
        return colors.info.main;
      default:
        return colors.text.secondary;
    }
  };

  const getTrendIcon = (trend?: string) => {
    if (!trend) return null;
    if (trend === 'increasing' || trend === 'critical') return <TrendingUpIcon sx={{ color: colors.error.main }} />;
    if (trend === 'decreasing') return <TrendingDownIcon sx={{ color: colors.warning.main }} />;
    if (trend === 'stable') return <TrendingFlatIcon sx={{ color: colors.success.main }} />;
    return null;
  };

  const getMetricLabel = () => {
    switch (forecastMetric) {
      case 'spend':
        return 'Spend (₹)';
      case 'clicks':
        return 'Clicks';
      case 'conversions':
        return 'Conversions';
    }
  };

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography variant="h4" sx={{ fontWeight: 600, mb: 1 }}>
            Predictive Alerts
          </Typography>
          <Typography variant="body1" color="text.secondary">
            AI-powered predictions and proactive monitoring of your campaigns
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 2, alignItems: 'center' }}>
          <AIBadge />
          <Button variant="outlined" startIcon={<RefreshIcon />} onClick={loadAlerts} disabled={loading}>
            Refresh
          </Button>
        </Box>
      </Box>

      {/* Alert Stats */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} md={3}>
          <GradientCard variant="error" intensity="subtle">
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <ErrorIcon sx={{ fontSize: 40, color: colors.error.main }} />
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 600, color: colors.error.main }}>
                    {alertStats.critical}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Critical Alerts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </GradientCard>
        </Grid>

        <Grid item xs={12} md={3}>
          <GradientCard variant="warning" intensity="subtle">
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <WarningIcon sx={{ fontSize: 40, color: colors.warning.main }} />
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 600, color: colors.warning.main }}>
                    {alertStats.warnings}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Warnings
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </GradientCard>
        </Grid>

        <Grid item xs={12} md={3}>
          <GradientCard variant="info" intensity="subtle">
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <InfoIcon sx={{ fontSize: 40, color: colors.info.main }} />
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 600, color: colors.info.main }}>
                    {alertStats.info}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Info
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </GradientCard>
        </Grid>

        <Grid item xs={12} md={3}>
          <Card>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 2 }}>
                <NotificationsActiveIcon sx={{ fontSize: 40, color: colors.primary.main }} />
                <Box>
                  <Typography variant="h3" sx={{ fontWeight: 600 }}>
                    {alertStats.total}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Alerts
                  </Typography>
                </Box>
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      <Grid container spacing={3}>
        {/* Alerts List */}
        <Grid item xs={12} md={8}>
          <Paper sx={{ p: 2, mb: 3 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">Active Alerts</Typography>
              <FormControl size="small" sx={{ minWidth: 150 }}>
                <InputLabel>Time Period</InputLabel>
                <Select value={days} onChange={(e) => setDays(e.target.value as number)} label="Time Period">
                  <MenuItem value={7}>Last 7 days</MenuItem>
                  <MenuItem value={14}>Last 14 days</MenuItem>
                  <MenuItem value={30}>Last 30 days</MenuItem>
                </Select>
              </FormControl>
            </Box>

            {loading ? (
              <AILoadingState message="Analyzing your campaigns..." size="medium" variant="pulse" />
            ) : alerts.length > 0 ? (
              <Stack spacing={2}>
                {alerts.map((alert) => (
                  <Alert
                    key={alert.id}
                    severity={alert.severity}
                    icon={getSeverityIcon(alert.severity)}
                    sx={{
                      border: `2px solid ${getSeverityColor(alert.severity)}`,
                      '& .MuiAlert-message': { width: '100%' },
                    }}
                  >
                    <AlertTitle sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {alert.title}
                      {getTrendIcon(alert.trend)}
                      {alert.affected_entity && (
                        <Chip label={alert.affected_entity} size="small" sx={{ ml: 'auto' }} />
                      )}
                    </AlertTitle>

                    <Typography variant="body2" sx={{ mb: 1 }}>
                      {alert.description}
                    </Typography>

                    {alert.metric_value !== undefined && alert.metric_value !== null && alert.threshold !== undefined && alert.threshold !== null && (
                      <Box sx={{ my: 2 }}>
                        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 1 }}>
                          <Typography variant="caption">Current: {alert.metric_value.toFixed(2)}</Typography>
                          <Typography variant="caption">Threshold: {alert.threshold.toFixed(2)}</Typography>
                        </Box>
                        <LinearProgress
                          variant="determinate"
                          value={Math.min((alert.metric_value / alert.threshold) * 100, 100)}
                          color={alert.severity === 'critical' ? 'error' : 'warning'}
                          sx={{ height: 8, borderRadius: 1 }}
                        />
                      </Box>
                    )}

                    <Box sx={{ mt: 2, p: 2, bgcolor: 'background.default', borderRadius: 1 }}>
                      <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 0.5 }}>
                        Impact:
                      </Typography>
                      <Typography variant="body2" sx={{ mb: 1 }}>
                        {alert.impact}
                      </Typography>

                      <Typography variant="caption" sx={{ fontWeight: 600, display: 'block', mb: 0.5 }}>
                        Recommendation:
                      </Typography>
                      <Typography variant="body2" color="primary">
                        {alert.recommendation}
                      </Typography>
                    </Box>

                    <Box sx={{ mt: 1, display: 'flex', gap: 1 }}>
                      <Chip label={alert.type} size="small" variant="outlined" />
                      <Typography variant="caption" color="text.secondary" sx={{ ml: 'auto', alignSelf: 'center' }}>
                        {new Date(alert.created_at).toLocaleString()}
                      </Typography>
                    </Box>
                  </Alert>
                ))}
              </Stack>
            ) : (
              <EmptyState
                icon="search"
                title="No Alerts"
                description="Your campaigns are running smoothly with no critical issues detected."
              />
            )}
          </Paper>
        </Grid>

        {/* Forecast */}
        <Grid item xs={12} md={4}>
          <GradientCard variant="ai" intensity="subtle">
            <CardContent>
              <Typography variant="h6" sx={{ mb: 2 }}>
                7-Day Forecast
              </Typography>

              <FormControl fullWidth size="small" sx={{ mb: 3 }}>
                <InputLabel>Metric</InputLabel>
                <Select
                  value={forecastMetric}
                  onChange={(e) => setForecastMetric(e.target.value as any)}
                  label="Metric"
                >
                  <MenuItem value="spend">Spend</MenuItem>
                  <MenuItem value="clicks">Clicks</MenuItem>
                  <MenuItem value="conversions">Conversions</MenuItem>
                </Select>
              </FormControl>

              {forecastData ? (
                <>
                  <Box sx={{ mb: 3 }}>
                    <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
                      Trend: {forecastData.trend}
                    </Typography>
                    <Chip
                      label={`${forecastData.trend_percentage > 0 ? '+' : ''}${forecastData.trend_percentage}%`}
                      color={forecastData.trend === 'increasing' ? 'success' : forecastData.trend === 'decreasing' ? 'error' : 'default'}
                      size="small"
                    />
                  </Box>

                  <ResponsiveContainer width="100%" height={250}>
                    <AreaChart data={forecastData.forecast}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="date" tick={{ fontSize: 10 }} />
                      <YAxis />
                      <Tooltip />
                      <Area
                        type="monotone"
                        dataKey="value"
                        stroke={colors.primary.main}
                        fill={colors.primary[100]}
                        name={getMetricLabel()}
                      />
                    </AreaChart>
                  </ResponsiveContainer>

                  <Divider sx={{ my: 2 }} />

                  <Typography variant="subtitle2" sx={{ mb: 2 }}>
                    Projected Values
                  </Typography>
                  <Stack spacing={1}>
                    {forecastData.forecast.slice(0, 3).map((point: any, index: number) => (
                      <Box
                        key={index}
                        sx={{
                          display: 'flex',
                          justifyContent: 'space-between',
                          p: 1,
                          bgcolor: 'background.default',
                          borderRadius: 1,
                        }}
                      >
                        <Typography variant="caption">{point.date}</Typography>
                        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                          <Typography variant="caption" sx={{ fontWeight: 600 }}>
                            {point.value != null ? point.value.toFixed(2) : 'N/A'}
                          </Typography>
                          {point.confidence != null && (
                            <ConfidenceScore score={point.confidence} label="" showPercentage={false} size="small" variant="compact" />
                          )}
                        </Box>
                      </Box>
                    ))}
                  </Stack>
                </>
              ) : (
                <AILoadingState message="Generating forecast..." size="small" variant="dots" />
              )}
            </CardContent>
          </GradientCard>
        </Grid>
      </Grid>
    </Box>
  );
};

export default PredictiveAlertsPage;
