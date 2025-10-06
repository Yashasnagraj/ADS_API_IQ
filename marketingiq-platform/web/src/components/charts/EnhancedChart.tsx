/**
 * Enhanced Chart Component
 * Wrapper for Recharts with professional styling, axis labels, and formatting
 */
import React from 'react';
import {
  XAxis as RechartsXAxis,
  YAxis as RechartsYAxis,
  CartesianGrid as RechartsGrid,
  Tooltip as RechartsTooltip,
  Legend as RechartsLegend,
  ResponsiveContainer,
} from 'recharts';
import { useTheme, alpha } from '@mui/material';
import { chartConfig, formatters, axisLabelConfig } from './chartTheme';

export interface AxisConfig {
  label: string;
  format?: 'currency' | 'percentage' | 'number' | 'compact' | 'decimal';
  dataKey?: string;
  hide?: boolean;
  domain?: [number | 'auto' | 'dataMin' | 'dataMax', number | 'auto' | 'dataMin' | 'dataMax'];
}

/**
 * Enhanced X-Axis with proper labels and formatting
 */
export const EnhancedXAxis: React.FC<AxisConfig> = ({
  label,
  dataKey = 'name',
  hide = false,
  format,
}) => {
  const theme = useTheme();

  if (hide) return null;

  const formatter = format ? formatters[format] : undefined;

  return (
    <RechartsXAxis
      dataKey={dataKey}
      stroke={theme.palette.text.secondary}
      tick={{ fontSize: chartConfig.axis.fontSize, fill: theme.palette.text.secondary }}
      tickFormatter={formatter}
      label={{
        value: label,
        ...axisLabelConfig.xAxis,
      }}
    />
  );
};

/**
 * Enhanced Y-Axis with proper labels and formatting
 */
export const EnhancedYAxis: React.FC<AxisConfig> = ({
  label,
  hide = false,
  format,
  domain,
}) => {
  const theme = useTheme();

  if (hide) return null;

  const formatter = format ? formatters[format] : undefined;

  return (
    <RechartsYAxis
      stroke={theme.palette.text.secondary}
      tick={{ fontSize: chartConfig.axis.fontSize, fill: theme.palette.text.secondary }}
      tickFormatter={formatter}
      domain={domain}
      label={{
        value: label,
        ...axisLabelConfig.yAxis,
      }}
    />
  );
};

/**
 * Enhanced CartesianGrid with professional styling
 */
export const EnhancedGrid: React.FC = () => {
  const theme = useTheme();

  return (
    <RechartsGrid
      strokeDasharray={chartConfig.grid.strokeDasharray}
      stroke={alpha(theme.palette.divider, chartConfig.grid.opacity)}
    />
  );
};

/**
 * Enhanced Tooltip with custom styling
 */
export const EnhancedTooltip: React.FC<{ formatter?: (value: any) => string }> = ({ formatter }) => {
  const theme = useTheme();

  return (
    <RechartsTooltip
      contentStyle={{
        backgroundColor: theme.palette.background.paper,
        border: `1px solid ${theme.palette.divider}`,
        borderRadius: 8,
        boxShadow: theme.shadows[4],
      }}
      formatter={formatter}
      labelStyle={{
        fontWeight: 600,
        marginBottom: 4,
      }}
    />
  );
};

/**
 * Enhanced Legend with professional styling
 */
export const EnhancedLegend: React.FC = () => {
  return (
    <RechartsLegend
      iconSize={chartConfig.legend.iconSize}
      wrapperStyle={{
        fontSize: chartConfig.legend.fontSize,
        fontFamily: chartConfig.legend.fontFamily,
      }}
    />
  );
};

/**
 * Complete Enhanced Chart Wrapper
 * Combines all enhanced components with responsive container
 */
export const EnhancedChart: React.FC<{
  children: React.ReactElement<{ children?: React.ReactNode }>;
  height?: number;
  xAxis: AxisConfig;
  yAxis: AxisConfig;
  showGrid?: boolean;
  showTooltip?: boolean;
  showLegend?: boolean;
}> = ({
  children,
  height = 300,
  xAxis,
  yAxis,
  showGrid = true,
  showTooltip = true,
  showLegend = false,
}) => {
  // Safely extract children from the chart component
  const enhancedChildren = children.props?.children
    ? React.Children.toArray(children.props.children)
    : [];

  return (
    <ResponsiveContainer width="100%" height={height}>
      {React.cloneElement(children, {}, [
        showGrid && <EnhancedGrid key="grid" />,
        <EnhancedXAxis key="xaxis" {...xAxis} />,
        <EnhancedYAxis key="yaxis" {...yAxis} />,
        showTooltip && <EnhancedTooltip key="tooltip" formatter={yAxis.format ? formatters[yAxis.format] : undefined} />,
        showLegend && <EnhancedLegend key="legend" />,
        ...enhancedChildren,
      ])}
    </ResponsiveContainer>
  );
};

export default EnhancedChart;
