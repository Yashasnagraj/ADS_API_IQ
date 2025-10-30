/**
 * Performance Scatter/Bubble Chart - Enterprise Grade
 * Used for opportunity matrices, performance quadrants
 * Common in Google Ads (Quality Score vs CTR), Meta Ads Manager
 */
import React from 'react';
import {
  ScatterChart,
  Scatter,
  XAxis,
  YAxis,
  ZAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  Cell,
  ReferenceLine,
  Label,
} from 'recharts';
import { Box, Paper, Typography, useTheme, alpha } from '@mui/material';
import { CHART_COLORS, CHART_MARGINS, GRID_STYLES } from '../../constants/visualizations';
import { formatCurrency, formatCompactNumber, formatPercentage } from '../../utils/chartHelpers';

export interface ScatterDataPoint {
  name: string; // Item label (keyword, campaign, etc.)
  x: number; // X-axis value
  y: number; // Y-axis value
  z?: number; // Bubble size (optional)
  color?: string; // Custom color (optional)
  [key: string]: any; // Additional data for tooltip
}

interface PerformanceScatterChartProps {
  data: ScatterDataPoint[];
  height?: number;
  title?: string;
  subtitle?: string;
  xAxisLabel: string;
  yAxisLabel: string;
  xFormat?: 'currency' | 'number' | 'percentage';
  yFormat?: 'currency' | 'number' | 'percentage';
  zLabel?: string; // Label for bubble size
  showGrid?: boolean;
  quadrants?: {
    xThreshold: number;
    yThreshold: number;
    labels?: {
      topLeft?: string;
      topRight?: string;
      bottomLeft?: string;
      bottomRight?: string;
    };
  };
}

export const PerformanceScatterChart: React.FC<PerformanceScatterChartProps> = ({
  data,
  height = 400,
  title,
  subtitle,
  xAxisLabel,
  yAxisLabel,
  xFormat = 'number',
  yFormat = 'number',
  zLabel,
  showGrid = true,
  quadrants,
}) => {
  const theme = useTheme();

  const formatValue = (value: number, format: string) => {
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
  const CustomTooltip = ({ active, payload }: any) => {
    if (!active || !payload || !payload.length) return null;

    const data = payload[0].payload;

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
          {data.name}
        </Typography>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            {xAxisLabel}:
          </Typography>
          <Typography variant="body2" fontWeight="600" sx={{ ml: 2, color: theme.palette.text.primary }}>
            {formatValue(data.x, xFormat)}
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            {yAxisLabel}:
          </Typography>
          <Typography variant="body2" fontWeight="600" sx={{ ml: 2, color: theme.palette.text.primary }}>
            {formatValue(data.y, yFormat)}
          </Typography>
        </Box>
        {data.z !== undefined && zLabel && (
          <Box sx={{ display: 'flex', justifyContent: 'space-between' }}>
            <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
              {zLabel}:
            </Typography>
            <Typography variant="body2" fontWeight="600" sx={{ ml: 2, color: theme.palette.text.primary }}>
              {formatCompactNumber(data.z)}
            </Typography>
          </Box>
        )}
      </Paper>
    );
  };

  // Calculate bubble sizes
  const maxZ = data.reduce((max, d) => Math.max(max, d.z || 0), 0);
  const minZ = data.reduce((min, d) => Math.min(min, d.z || 0), Infinity);
  const zRange = maxZ - minZ;

  const getBubbleSize = (z?: number) => {
    if (z === undefined) return 60;
    if (zRange === 0) return 60;
    return 40 + ((z - minZ) / zRange) * 120; // Size range: 40-160
  };

  // Get quadrant color
  const getQuadrantColor = (x: number, y: number): string => {
    if (!quadrants) return CHART_COLORS.primary;

    const { xThreshold, yThreshold } = quadrants;

    if (x >= xThreshold && y >= yThreshold) return CHART_COLORS.highPerformer; // Top Right
    if (x < xThreshold && y >= yThreshold) return CHART_COLORS.potentialGrowth; // Top Left
    if (x >= xThreshold && y < yThreshold) return CHART_COLORS.needsAttention; // Bottom Right
    return CHART_COLORS.underPerformer; // Bottom Left
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
        <ScatterChart margin={{ ...CHART_MARGINS.withLabels, right: 40 }}>
          {/* Grid */}
          {showGrid && (
            <CartesianGrid
              strokeDasharray={GRID_STYLES.strokeDasharray}
              stroke={GRID_STYLES.stroke}
              strokeOpacity={GRID_STYLES.strokeOpacity}
            />
          )}

          {/* Quadrant reference lines */}
          {quadrants && (
            <>
              <ReferenceLine
                x={quadrants.xThreshold}
                stroke={theme.palette.divider}
                strokeDasharray="5 5"
                strokeWidth={2}
              >
                <Label
                  value="Target"
                  position="top"
                  style={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                />
              </ReferenceLine>
              <ReferenceLine
                y={quadrants.yThreshold}
                stroke={theme.palette.divider}
                strokeDasharray="5 5"
                strokeWidth={2}
              >
                <Label
                  value="Target"
                  position="right"
                  style={{ fill: theme.palette.text.secondary, fontSize: 12 }}
                />
              </ReferenceLine>
            </>
          )}

          {/* X Axis */}
          <XAxis
            type="number"
            dataKey="x"
            stroke={theme.palette.text.secondary}
            tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
            tickFormatter={(value) => formatValue(value, xFormat)}
            label={{ value: xAxisLabel, position: 'insideBottom', offset: -10, style: { fill: theme.palette.text.secondary, fontSize: 14, fontWeight: 600 } }}
          />

          {/* Y Axis */}
          <YAxis
            type="number"
            dataKey="y"
            stroke={theme.palette.text.secondary}
            tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
            tickFormatter={(value) => formatValue(value, yFormat)}
            label={{ value: yAxisLabel, angle: -90, position: 'insideLeft', style: { fill: theme.palette.text.secondary, fontSize: 14, fontWeight: 600 } }}
          />

          {/* Z Axis for bubble size */}
          {zLabel && <ZAxis type="number" dataKey="z" range={[40, 160]} />}

          {/* Tooltip */}
          <Tooltip content={<CustomTooltip />} cursor={{ strokeDasharray: '3 3' }} />

          {/* Scatter plot */}
          <Scatter
            data={data}
            animationDuration={800}
            animationEasing="ease-out"
          >
            {data.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={entry.color || getQuadrantColor(entry.x, entry.y)}
                fillOpacity={0.7}
                stroke={entry.color || getQuadrantColor(entry.x, entry.y)}
                strokeWidth={2}
              />
            ))}
          </Scatter>
        </ScatterChart>
      </ResponsiveContainer>

      {/* Quadrant labels */}
      {quadrants?.labels && (
        <Box sx={{ mt: 2, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: CHART_COLORS.potentialGrowth }} />
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
              {quadrants.labels.topLeft || 'Potential Growth'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: CHART_COLORS.highPerformer }} />
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
              {quadrants.labels.topRight || 'High Performers'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: CHART_COLORS.underPerformer }} />
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
              {quadrants.labels.bottomLeft || 'Under Performers'}
            </Typography>
          </Box>
          <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Box sx={{ width: 12, height: 12, borderRadius: '50%', bgcolor: CHART_COLORS.needsAttention }} />
            <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
              {quadrants.labels.bottomRight || 'Needs Attention'}
            </Typography>
          </Box>
        </Box>
      )}
    </Box>
  );
};

export default PerformanceScatterChart;
