/**
 * Forecast & Anomaly Strip Component
 * Bottom strip showing 7-day forecast and anomaly alerts
 */
import React from 'react';
import { Box, Grid, Paper, Typography, Chip, useTheme, alpha } from '@mui/material';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
import { Warning, Error, Info, TrendingUp, TrendingDown, Remove } from '@mui/icons-material';
import { formatCurrency } from '../../utils/chartHelpers';

interface ForecastDataPoint {
  date: string;
  predicted_revenue: number;
  confidence_lower: number;
  confidence_upper: number;
}

interface AnomalyAlert {
  severity: string;
  title: string;
  description: string;
  metric: string;
  value: number;
  recommendation: string;
}

interface ForecastAnomalyStripProps {
  forecast: {
    forecast: ForecastDataPoint[];
    trend: string;
  } | null;
  anomalies: {
    anomalies: AnomalyAlert[];
    total_anomalies: number;
  } | null;
}

export const ForecastAnomalyStrip: React.FC<ForecastAnomalyStripProps> = ({ forecast, anomalies }) => {
  const theme = useTheme();

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return '#ef4444';
      case 'HIGH':
        return '#f59e0b';
      case 'MEDIUM':
        return '#3b82f6';
      default:
        return '#6b7280';
    }
  };

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'CRITICAL':
        return <Error sx={{ fontSize: '1rem' }} />;
      case 'HIGH':
        return <Warning sx={{ fontSize: '1rem' }} />;
      default:
        return <Info sx={{ fontSize: '1rem' }} />;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'INCREASING':
        return <TrendingUp />;
      case 'DECREASING':
        return <TrendingDown />;
      default:
        return <Remove />;
    }
  };

  const getTrendColor = (trend: string) => {
    switch (trend) {
      case 'INCREASING':
        return '#10b981';
      case 'DECREASING':
        return '#ef4444';
      default:
        return '#6b7280';
    }
  };

  return (
    <Grid container spacing={3}>
      {/* Forecast Chart */}
      <Grid item xs={12} lg={7}>
        <Paper sx={{ p: 3, borderRadius: 2, boxShadow: theme.shadows[2] }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              7-Day Revenue Forecast
            </Typography>
            {forecast && (
              <Chip
                icon={getTrendIcon(forecast.trend)}
                label={forecast.trend}
                size="small"
                sx={{
                  background: alpha(getTrendColor(forecast.trend), 0.1),
                  color: getTrendColor(forecast.trend),
                  fontWeight: 600
                }}
              />
            )}
          </Box>

          {forecast && forecast.forecast && forecast.forecast.length > 0 ? (
            <ResponsiveContainer width="100%" height={150}>
              <AreaChart data={forecast.forecast} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor={theme.palette.primary.main} stopOpacity={0.3} />
                    <stop offset="95%" stopColor={theme.palette.primary.main} stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="date"
                  tick={{ fill: theme.palette.text.secondary, fontSize: 11 }}
                  tickFormatter={(value) => new Date(value).toLocaleDateString('en-US', { month: 'short', day: 'numeric' })}
                />
                <YAxis
                  tick={{ fill: theme.palette.text.secondary, fontSize: 11 }}
                  tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
                />
                <Tooltip
                  contentStyle={{
                    background: alpha(theme.palette.background.paper, 0.95),
                    border: `1px solid ${theme.palette.divider}`,
                    borderRadius: 4
                  }}
                  formatter={(value: number) => formatCurrency(value)}
                  labelFormatter={(label) => new Date(label).toLocaleDateString()}
                />
                <Area
                  type="monotone"
                  dataKey="predicted_revenue"
                  stroke={theme.palette.primary.main}
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorRevenue)"
                />
              </AreaChart>
            </ResponsiveContainer>
          ) : (
            <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
              No forecast data available
            </Typography>
          )}
        </Paper>
      </Grid>

      {/* Anomaly Alerts */}
      <Grid item xs={12} lg={5}>
        <Paper sx={{ p: 3, borderRadius: 2, boxShadow: theme.shadows[2], height: '100%' }}>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Anomaly Alerts
            </Typography>
            {anomalies && (
              <Chip
                label={`${anomalies.total_anomalies} alerts`}
                size="small"
                color={anomalies.total_anomalies > 0 ? 'error' : 'default'}
              />
            )}
          </Box>

          <Box sx={{ maxHeight: 200, overflowY: 'auto' }}>
            {anomalies && anomalies.anomalies && anomalies.anomalies.length > 0 ? (
              anomalies.anomalies.map((anomaly, index) => {
                const severityColor = getSeverityColor(anomaly.severity);

                return (
                  <Box
                    key={index}
                    sx={{
                      mb: 1.5,
                      p: 1.5,
                      borderRadius: 1,
                      border: `1px solid ${alpha(severityColor, 0.3)}`,
                      background: alpha(severityColor, 0.05)
                    }}
                  >
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: 0.5 }}>
                      <Box sx={{ color: severityColor }}>
                        {getSeverityIcon(anomaly.severity)}
                      </Box>
                      <Typography variant="body2" sx={{ fontWeight: 600 }}>
                        {anomaly.title}
                      </Typography>
                      <Chip
                        label={anomaly.severity}
                        size="small"
                        sx={{
                          height: 18,
                          fontSize: '0.65rem',
                          background: alpha(severityColor, 0.2),
                          color: severityColor,
                          fontWeight: 600
                        }}
                      />
                    </Box>
                    <Typography variant="caption" sx={{ display: 'block', mb: 0.5, color: theme.palette.text.secondary }}>
                      {anomaly.description}
                    </Typography>
                    <Typography variant="caption" sx={{ display: 'block', fontWeight: 600, color: severityColor }}>
                      💡 {anomaly.recommendation}
                    </Typography>
                  </Box>
                );
              })
            ) : (
              <Box
                sx={{
                  textAlign: 'center',
                  py: 3,
                  color: theme.palette.text.secondary
                }}
              >
                <Typography variant="body2">✅ No anomalies detected</Typography>
                <Typography variant="caption">All metrics are within normal ranges</Typography>
              </Box>
            )}
          </Box>
        </Paper>
      </Grid>
    </Grid>
  );
};

export default ForecastAnomalyStrip;
