/**
 * Chart Theme Configuration
 * Professional color palette and styling for all visualizations
 */

export const chartColors = {
  // Primary palette
  primary: '#6366f1',        // Indigo
  secondary: '#8b5cf6',      // Purple
  success: '#10b981',        // Green
  warning: '#f59e0b',        // Amber
  error: '#ef4444',          // Red
  info: '#3b82f6',           // Blue

  // Extended palette
  teal: '#14b8a6',
  cyan: '#06b6d4',
  pink: '#ec4899',
  orange: '#f97316',
  lime: '#84cc16',

  // Gradients
  gradients: {
    primary: ['#6366f1', '#8b5cf6'],
    success: ['#10b981', '#14b8a6'],
    warning: ['#f59e0b', '#f97316'],
    error: ['#ef4444', '#ec4899'],
    info: ['#3b82f6', '#06b6d4'],
  },

  // Chart-specific colors
  line: {
    revenue: '#10b981',
    cost: '#ef4444',
    ctr: '#3b82f6',
    conversions: '#8b5cf6',
    impressions: '#06b6d4',
    clicks: '#10b981',
  },

  // Status colors
  status: {
    high: '#ef4444',
    medium: '#f59e0b',
    low: '#3b82f6',
    good: '#10b981',
  },
};

export const chartConfig = {
  // Axis configuration
  axis: {
    stroke: '#9ca3af',          // Gray-400
    fontSize: 12,
    fontFamily: '"Inter", "Roboto", "Helvetica", sans-serif',
    tickSize: 5,
  },

  // Grid configuration
  grid: {
    stroke: '#e5e7eb',          // Gray-200
    strokeDasharray: '3 3',
    opacity: 0.3,
  },

  // Tooltip configuration
  tooltip: {
    backgroundColor: '#ffffff',
    border: '1px solid #e5e7eb',
    borderRadius: 8,
    boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
  },

  // Legend configuration
  legend: {
    fontSize: 12,
    fontFamily: '"Inter", "Roboto", "Helvetica", sans-serif',
    iconSize: 12,
  },

  // Animation
  animation: {
    duration: 800,
    easing: 'ease-in-out',
  },
};

/**
 * Format axis labels with appropriate units
 */
export const formatters = {
  currency: (value: number) => `₹${value.toLocaleString()}`,
  percentage: (value: number) => `${value}%`,
  number: (value: number) => value.toLocaleString(),
  compact: (value: number) => {
    if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
    if (value >= 1000) return `{(value / 1000).toFixed(1)}K`;
    return value.toString();
  },
  decimal: (value: number, decimals: number = 2) => value.toFixed(decimals),
};

/**
 * Get gradient definition for charts
 */
export const getGradientDef = (id: string, color1: string, color2: string) => ({
  id,
  x1: '0',
  y1: '0',
  x2: '0',
  y2: '1',
  stops: [
    { offset: '5%', stopColor: color1, stopOpacity: 0.8 },
    { offset: '95%', stopColor: color2, stopOpacity: 0 },
  ],
});

/**
 * Common label configuration
 */
export const axisLabelConfig = {
  xAxis: {
    position: 'insideBottom' as const,
    offset: -5,
    style: {
      fontSize: 12,
      fontWeight: 500,
      fill: '#6b7280',  // Gray-500
    },
  },
  yAxis: {
    angle: -90,
    position: 'insideLeft' as const,
    style: {
      fontSize: 12,
      fontWeight: 500,
      fill: '#6b7280',  // Gray-500
    },
  },
};

/**
 * Responsive configurations
 */
export const responsiveConfig = {
  mobile: {
    fontSize: 10,
    hideLabels: true,
    compactLegend: true,
  },
  tablet: {
    fontSize: 11,
    hideLabels: false,
    compactLegend: false,
  },
  desktop: {
    fontSize: 12,
    hideLabels: false,
    compactLegend: false,
  },
};

export default {
  colors: chartColors,
  config: chartConfig,
  formatters,
  getGradientDef,
  axisLabelConfig,
  responsiveConfig,
};
