/**
 * Performance Area Chart - Enterprise Grade
 * Multi-series area chart with gradient fills, tooltips, and axis labels
 * Used for trend visualization in Google Ads, Salesforce, Adobe Analytics
 */
import React from 'react';
import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { Box, Paper, Typography, useTheme, alpha } from '@mui/material';
import { CHART_COLORS, CHART_MARGINS, AXIS_STYLES, GRID_STYLES } from '../../constants/visualizations';
import { formatCurrency, formatCompactNumber, formatPercentage } from '../../utils/chartHelpers';

export interface AreaChartDataPoint {
  name: string; // X-axis label (date, category, etc.)
  [key: string]: string | number; // Dynamic keys for multiple metrics
}

export interface AreaChartSeries {
  dataKey: string;
  name: string;
  color: string;
  format?: 'currency' | 'number' | 'percentage';
}

interface PerformanceAreaChartProps {
  data: AreaChartDataPoint[];
  series: AreaChartSeries[];
  height?: number;
  title?: string;
  subtitle?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  showLegend?: boolean;
  showGrid?: boolean;
}

export const PerformanceAreaChart: React.FC<PerformanceAreaChartProps> = ({
  data,
  series,
  height = 350,
  title,
  subtitle,
  xAxisLabel,
  yAxisLabel,
  showLegend = true,
  showGrid = true,
}) => {
  const theme = useTheme();

  const formatValue = (value: number, format?: string) => {
    switch (format) {
      case 'currency':
        return formatCurrency(value);
      case 'percentage':
        return formatPercentage(value);
      case 'number':
      default:
        return formatCompactNumber(value);
    }
  };

  // Custom tooltip component
  const CustomTooltip = ({ active, payload, label }: any) => {
    if (!active || !payload || !payload.length) return null;

    return (
      <Paper
        elevation={8}
        sx={{
          p: 2,
          backgroundColor: alpha(theme.palette.background.paper, 0.98),
          border: `1px solid ${theme.palette.divider}`,
          borderRadius: 2,
          minWidth: 200,
        }}
      >
        <Typography variant="subtitle2" fontWeight="600" sx={{ mb: 1, color: theme.palette.text.primary }}>
          {label}
        </Typography>
        {payload.map((entry: any, index: number) => {
          const seriesConfig = series.find(s => s.dataKey === entry.dataKey);
          return (
            <Box key={index} sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', mb: 0.5 }}>
              <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Box
                  sx={{
                    width: 12,
                    height: 12,
                    borderRadius: '50%',
                    bgcolor: entry.color,
                  }}
                />
                <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
                  {entry.name}:
                </Typography>
              </Box>
              <Typography variant="body2" fontWeight="600" sx={{ ml: 2, color: theme.palette.text.primary }}>
                {formatValue(entry.value, seriesConfig?.format)}
              </Typography>
            </Box>
          );
        })}
      </Paper>
    );
  };

  return (
    <Box sx={{ width: '100%' }}>
      {/* Header */}
      {(title || subtitle) && (
        <Box sx={{ mb: 2 }}>
          {title && (
            <Typography variant="h6" fontWeight="600" sx={{ color: theme.palette.text.primary }}>
              {title}
            </Typography>
          )}
          {subtitle && (
            <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
              {subtitle}
            </Typography>
          )}
        </Box>
      )}

      {/* Chart */}
      <ResponsiveContainer width="100%" height={height}>
        <AreaChart data={data} margin={CHART_MARGINS.withLabels}>
          {/* Gradient definitions */}
          <defs>
            {series.map((s, index) => (
              <linearGradient key={`gradient-${index}`} id={`gradient-${s.dataKey}`} x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor={s.color} stopOpacity={0.4} />
                <stop offset="95%" stopColor={s.color} stopOpacity={0.05} />
              </linearGradient>
            ))}
          </defs>

          {/* Grid */}
          {showGrid && (
            <CartesianGrid
              strokeDasharray={GRID_STYLES.strokeDasharray}
              stroke={GRID_STYLES.stroke}
              strokeOpacity={GRID_STYLES.strokeOpacity}
            />
          )}

          {/* X Axis */}
          <XAxis
            dataKey="name"
            stroke={theme.palette.text.secondary}
            tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
            label={xAxisLabel ? { value: xAxisLabel, position: 'insideBottom', offset: -10, style: { fill: theme.palette.text.secondary, fontSize: 14, fontWeight: 600 } } : undefined}
          />

          {/* Y Axis */}
          <YAxis
            stroke={theme.palette.text.secondary}
            tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
            tickFormatter={(value) => formatCompactNumber(value)}
            label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: 'insideLeft', style: { fill: theme.palette.text.secondary, fontSize: 14, fontWeight: 600 } } : undefined}
          />

          {/* Tooltip */}
          <Tooltip content={<CustomTooltip />} cursor={{ stroke: theme.palette.divider, strokeWidth: 1 }} />

          {/* Legend */}
          {showLegend && (
            <Legend
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="circle"
              formatter={(value) => <span style={{ color: theme.palette.text.primary, fontSize: '14px' }}>{value}</span>}
            />
          )}

          {/* Area series */}
          {series.map((s, index) => (
            <Area
              key={index}
              type="monotone"
              dataKey={s.dataKey}
              name={s.name}
              stroke={s.color}
              strokeWidth={2}
              fillOpacity={1}
              fill={`url(#gradient-${s.dataKey})`}
              animationDuration={600}
              animationEasing="ease-out"
            />
          ))}
        </AreaChart>
      </ResponsiveContainer>

      {/* Axis Labels */}
      {(xAxisLabel || yAxisLabel) && (
        <Box sx={{ mt: 1, display: 'flex', justifyContent: 'space-between', px: 6 }}>
          {xAxisLabel && (
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary, fontWeight: 500 }}>
              {xAxisLabel}
            </Typography>
          )}
        </Box>
      )}
    </Box>
  );
};

export default PerformanceAreaChart;
