/**
 * Channel Performance Chart Component
 * Dual Y-axis chart showing Spend (Bar) and ROAS (Line)
 */
import React from 'react';
import { Box, Typography, useTheme, alpha, Chip } from '@mui/material';
import {
  ComposedChart,
  Bar,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer
} from 'recharts';
import { formatCurrency } from '../../utils/chartHelpers';

interface ChannelMetrics {
  channel: string;
  spend: number;
  revenue: number;
  roas: number;
  orders: number;
}

interface ChannelPerformanceChartProps {
  data: {
    channels: ChannelMetrics[];
    insight: string;
  } | null;
}

export const ChannelPerformanceChart: React.FC<ChannelPerformanceChartProps> = ({ data }) => {
  const theme = useTheme();

  if (!data || !data.channels || data.channels.length === 0) {
    return <Typography>No channel data available</Typography>;
  }

  const { channels, insight } = data;

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      return (
        <Box
          sx={{
            background: alpha(theme.palette.background.paper, 0.95),
            p: 1.5,
            borderRadius: 1,
            border: `1px solid ${theme.palette.divider}`,
            boxShadow: theme.shadows[3]
          }}
        >
          <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
            {payload[0].payload.channel}
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            Spend: {formatCurrency(payload[0].payload.spend)}
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            ROAS: {payload[0].payload.roas.toFixed(2)}x
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            Orders: {payload[0].payload.orders}
          </Typography>
        </Box>
      );
    }
    return null;
  };

  return (
    <Box>
      <ResponsiveContainer width="100%" height={300}>
        <ComposedChart data={channels} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
          <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.3)} />
          <XAxis
            dataKey="channel"
            tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
          />
          <YAxis
            yAxisId="left"
            tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
            tickFormatter={(value) => `₹${(value / 1000).toFixed(0)}k`}
          />
          <YAxis
            yAxisId="right"
            orientation="right"
            tick={{ fill: theme.palette.text.secondary, fontSize: 12 }}
            tickFormatter={(value) => `${value.toFixed(1)}x`}
          />
          <Tooltip content={<CustomTooltip />} />
          <Legend
            wrapperStyle={{ fontSize: '12px' }}
            iconType="rect"
          />
          <Bar
            yAxisId="left"
            dataKey="spend"
            fill={theme.palette.primary.main}
            name="Spend (₹)"
            radius={[4, 4, 0, 0]}
          />
          <Line
            yAxisId="right"
            type="monotone"
            dataKey="roas"
            stroke="#10b981"
            strokeWidth={3}
            name="ROAS"
            dot={{ fill: '#10b981', r: 4 }}
          />
        </ComposedChart>
      </ResponsiveContainer>

      {/* Insight */}
      {insight && (
        <Box sx={{ mt: 2, p: 2, borderRadius: 1, background: alpha(theme.palette.info.main, 0.1) }}>
          <Chip label="AI Insight" size="small" sx={{ mb: 1 }} />
          <Typography variant="body2" sx={{ color: theme.palette.text.secondary }}>
            {insight}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default ChannelPerformanceChart;
