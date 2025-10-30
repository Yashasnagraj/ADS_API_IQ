/**
 * Performance Bar Chart - Enterprise Grade
 * Grouped/Stacked bar charts with tooltips and axis labels
 * Used in Google Ads, Meta Ads Manager, Salesforce
 */
import React from 'react';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { Box, Paper, Typography, useTheme, alpha } from '@mui/material';
import { CHART_COLORS, CHART_MARGINS, CHART_CONFIGS, GRID_STYLES } from '../../constants/visualizations';
import { formatCurrency, formatCompactNumber, formatPercentage } from '../../utils/chartHelpers';

export interface BarChartDataPoint {
  name: string;
  [key: string]: string | number;
}

export interface BarChartSeries {
  dataKey: string;
  name: string;
  color: string;
  format?: 'currency' | 'number' | 'percentage';
}

interface PerformanceBarChartProps {
  data: BarChartDataPoint[];
  series: BarChartSeries[];
  height?: number;
  title?: string;
  subtitle?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  layout?: 'vertical' | 'horizontal';
  stacked?: boolean;
  showLegend?: boolean;
  showGrid?: boolean;
}

export const PerformanceBarChart: React.FC<PerformanceBarChartProps> = ({
  data,
  series,
  height = 350,
  title,
  subtitle,
  xAxisLabel,
  yAxisLabel,
  layout = 'horizontal',
  stacked = false,
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

  // Custom tooltip
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
                    borderRadius: '4px',
                    bgcolor: entry.fill || entry.color,
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

  const chartProps = {
    data,
    margin: CHART_MARGINS.withLabels,
    layout,
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
        <BarChart {...chartProps}>
          {/* Grid */}
          {showGrid && (
            <CartesianGrid
              strokeDasharray={GRID_STYLES.strokeDasharray}
              stroke={GRID_STYLES.stroke}
              strokeOpacity={GRID_STYLES.strokeOpacity}
            />
          )}

          {/* Axes */}
          {layout === 'horizontal' ? (
            <>
              <XAxis
                dataKey="name"
                stroke={theme.palette.text.secondary}
                tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                label={xAxisLabel ? { value: xAxisLabel, position: 'insideBottom', offset: -10, style: { fill: theme.palette.text.secondary, fontSize: 14, fontWeight: 600 } } : undefined}
              />
              <YAxis
                stroke={theme.palette.text.secondary}
                tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                tickFormatter={(value) => formatCompactNumber(value)}
                label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: 'insideLeft', style: { fill: theme.palette.text.secondary, fontSize: 14, fontWeight: 600 } } : undefined}
              />
            </>
          ) : (
            <>
              <XAxis
                type="number"
                stroke={theme.palette.text.secondary}
                tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                tickFormatter={(value) => formatCompactNumber(value)}
                label={xAxisLabel ? { value: xAxisLabel, position: 'insideBottom', offset: -10, style: { fill: theme.palette.text.secondary, fontSize: 14, fontWeight: 600 } } : undefined}
              />
              <YAxis
                dataKey="name"
                type="category"
                stroke={theme.palette.text.secondary}
                tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                width={120}
                label={yAxisLabel ? { value: yAxisLabel, angle: -90, position: 'insideLeft', style: { fill: theme.palette.text.secondary, fontSize: 14, fontWeight: 600 } } : undefined}
              />
            </>
          )}

          {/* Tooltip */}
          <Tooltip content={<CustomTooltip />} cursor={{ fill: alpha(theme.palette.primary.main, 0.1) }} />

          {/* Legend */}
          {showLegend && (
            <Legend
              wrapperStyle={{ paddingTop: '20px' }}
              iconType="square"
              formatter={(value) => <span style={{ color: theme.palette.text.primary, fontSize: '14px' }}>{value}</span>}
            />
          )}

          {/* Bar series */}
          {series.map((s, index) => (
            <Bar
              key={index}
              dataKey={s.dataKey}
              name={s.name}
              fill={s.color}
              stackId={stacked ? 'stack' : undefined}
              radius={!stacked ? CHART_CONFIGS.bar.radius : undefined}
              maxBarSize={CHART_CONFIGS.bar.maxBarSize}
              animationDuration={600}
              animationEasing="ease-out"
            >
              {/* Add gradient effect */}
              {data.map((entry, entryIndex) => (
                <Cell key={`cell-${entryIndex}`} fill={s.color} />
              ))}
            </Bar>
          ))}
        </BarChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default PerformanceBarChart;
