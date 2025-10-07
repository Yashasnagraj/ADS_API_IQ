/**
 * Customer Segment Chart Component
 * Shows New vs Returning customers with donut chart
 */
import React from 'react';
import { Box, Typography, Grid, useTheme, alpha, Chip } from '@mui/material';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts';
import { formatCurrency } from '../../utils/chartHelpers';

interface CustomerSegment {
  segment: string;
  count: number;
  percentage: number;
  revenue: number;
  revenue_percentage: number;
  avg_order_value: number;
  conversion_rate: number;
}

interface CustomerSegmentChartProps {
  data: {
    segments: CustomerSegment[];
    insight: string;
  } | null;
}

export const CustomerSegmentChart: React.FC<CustomerSegmentChartProps> = ({ data }) => {
  const theme = useTheme();

  if (!data || !data.segments || data.segments.length === 0) {
    return <Typography>No segment data available</Typography>;
  }

  const { segments, insight } = data;

  const COLORS: Record<string, string> = {
    'RETURNING': '#8b5cf6',
    'NEW': '#3b82f6'
  };

  const chartData = segments.map(seg => ({
    name: seg.segment === 'RETURNING' ? 'Returning' : 'New',
    value: seg.percentage,
    count: seg.count,
    revenue: seg.revenue,
    revenue_pct: seg.revenue_percentage
  }));

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
            {payload[0].name} Customers
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            {payload[0].payload.count} users ({payload[0].value.toFixed(1)}%)
          </Typography>
          <Typography variant="caption" sx={{ display: 'block' }}>
            Revenue: {formatCurrency(payload[0].payload.revenue)} ({payload[0].payload.revenue_pct.toFixed(1)}%)
          </Typography>
        </Box>
      );
    }
    return null;
  };

  return (
    <Box>
      <ResponsiveContainer width="100%" height={200}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={80}
            paddingAngle={5}
            dataKey="value"
          >
            {chartData.map((entry, index) => (
              <Cell
                key={`cell-${index}`}
                fill={COLORS[entry.name === 'Returning' ? 'RETURNING' : 'NEW']}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
        </PieChart>
      </ResponsiveContainer>

      {/* Segment Stats */}
      <Grid container spacing={2} sx={{ mt: 1 }}>
        {segments.map((segment, index) => (
          <Grid item xs={6} key={index}>
            <Box
              sx={{
                p: 1.5,
                borderRadius: 1,
                background: alpha(COLORS[segment.segment], 0.1),
                border: `1px solid ${alpha(COLORS[segment.segment], 0.3)}`
              }}
            >
              <Typography
                variant="caption"
                sx={{
                  textTransform: 'uppercase',
                  fontWeight: 600,
                  color: COLORS[segment.segment],
                  display: 'block',
                  mb: 0.5
                }}
              >
                {segment.segment === 'RETURNING' ? 'Returning' : 'New'}
              </Typography>
              <Typography variant="body2" sx={{ fontWeight: 600, mb: 0.5 }}>
                {segment.count} orders
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: theme.palette.text.secondary }}>
                AOV: {formatCurrency(segment.avg_order_value)}
              </Typography>
              <Typography variant="caption" sx={{ display: 'block', color: theme.palette.text.secondary }}>
                CVR: {segment.conversion_rate.toFixed(1)}%
              </Typography>
            </Box>
          </Grid>
        ))}
      </Grid>

      {/* Insight */}
      {insight && (
        <Box sx={{ mt: 2, p: 2, borderRadius: 1, background: alpha(theme.palette.info.main, 0.1) }}>
          <Chip label="AI Insight" size="small" sx={{ mb: 1 }} />
          <Typography variant="caption" sx={{ color: theme.palette.text.secondary }}>
            {insight}
          </Typography>
        </Box>
      )}
    </Box>
  );
};

export default CustomerSegmentChart;
