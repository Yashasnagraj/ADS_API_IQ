/**
 * Performance Line Chart - Enterprise Grade
 * Multi-series line chart with tooltips, axis labels, and data points
 * Used for time-series visualization in all major analytics platforms
 */
import React from 'react';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Dot,
} from 'recharts';
import { Box, Paper, Typography, useTheme, alpha } from '@mui/material';
import { CHART_COLORS, CHART_MARGINS, CHART_CONFIGS, GRID_STYLES } from '../../constants/visualizations';
import { formatCurrency, formatCompactNumber, formatPercentage } from '../../utils/chartHelpers';

export interface LineChartDataPoint {
  name: string;
  [key: string]: string | number;
}

export interface LineChartSeries {
  dataKey: string;
  name: string;
  color: string;
  format?: 'currency' | 'number' | 'percentage';
  dashed?: boolean;
}

interface PerformanceLineChartProps {
  data: LineChartDataPoint[];
  series: LineChartSeries[];
  height?: number;
  title?: string;
  subtitle?: string;
  xAxisLabel?: string;
  yAxisLabel?: string;
  showLegend?: boolean;
  showGrid?: boolean;
  showDots?: boolean;
}

export const PerformanceLineChart: React.FC<PerformanceLineChartProps> = ({
  data,
  series,
  height = 350,
  title,
  subtitle,
  xAxisLabel,
  yAxisLabel,
  showLegend = true,
  showGrid = true,
  showDots = true,
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
                    width: 3,
                    height: 12,
                    bgcolor: entry.color,
                    borderRadius: 0.5,
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

  // Custom dot for data points
  const CustomDot = (props: any) => {
    const { cx, cy, stroke } = props;
    return (
      <Dot
        cx={cx}
        cy={cy}
        r={4}
        fill={stroke}
        stroke="#fff"
        strokeWidth={2}
      />
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
        <LineChart data={data} margin={CHART_MARGINS.withLabels}>
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
              iconType="line"
              formatter={(value) => <span style={{ color: theme.palette.text.primary, fontSize: '14px' }}>{value}</span>}
            />
          )}

          {/* Line series */}
          {series.map((s, index) => (
            <Line
              key={index}
              type="monotone"
              dataKey={s.dataKey}
              name={s.name}
              stroke={s.color}
              strokeWidth={CHART_CONFIGS.line.strokeWidth}
              strokeDasharray={s.dashed ? '5 5' : undefined}
              dot={showDots ? <CustomDot /> : false}
              activeDot={showDots ? { r: 6, strokeWidth: 2 } : false}
              animationDuration={600}
              animationEasing="ease-out"
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </Box>
  );
};

export default PerformanceLineChart;
