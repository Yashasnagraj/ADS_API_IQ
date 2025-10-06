/**
 * Chart Helper Utilities
 * Formatting, color selection, and data transformation utilities
 */

import { CHART_COLORS, PERFORMANCE_THRESHOLDS, NUMBER_FORMATS } from '../constants/visualizations';

/**
 * Format number as currency (INR)
 */
export const formatCurrency = (value: number, precise: boolean = false): string => {
  const options: Intl.NumberFormatOptions = precise
    ? { style: 'currency', currency: 'INR', minimumFractionDigits: 2, maximumFractionDigits: 2 }
    : { style: 'currency', currency: 'INR', minimumFractionDigits: 0, maximumFractionDigits: 0 };
  const formatter = new Intl.NumberFormat('en-IN', options);
  return formatter.format(value);
};

/**
 * Format number as percentage
 */
export const formatPercentage = (value: number, precise: boolean = false): string => {
  const options: Intl.NumberFormatOptions = precise
    ? { style: 'percent', minimumFractionDigits: 2, maximumFractionDigits: 2 }
    : { style: 'percent', minimumFractionDigits: 1, maximumFractionDigits: 1 };
  const formatter = new Intl.NumberFormat('en-US', options);
  return formatter.format(value / 100);
};

/**
 * Format large numbers with K, M, B suffixes
 */
export const formatCompactNumber = (value: number): string => {
  if (value >= 1000000000) {
    return `${(value / 1000000000).toFixed(1)}B`;
  }
  if (value >= 1000000) {
    return `${(value / 1000000).toFixed(1)}M`;
  }
  if (value >= 1000) {
    return `${(value / 1000).toFixed(1)}K`;
  }
  return value.toFixed(0);
};

/**
 * Format number with commas
 */
export const formatNumber = (value: number, decimals: number = 0): string => {
  return new Intl.NumberFormat('en-US', {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  }).format(value);
};

/**
 * Get color based on performance threshold
 */
export const getPerformanceColor = (
  value: number,
  metric: keyof typeof PERFORMANCE_THRESHOLDS
): string => {
  const thresholds = PERFORMANCE_THRESHOLDS[metric];

  if (value >= thresholds.excellent) return CHART_COLORS.success;
  if (value >= thresholds.good) return CHART_COLORS.info;
  if (value >= thresholds.average) return CHART_COLORS.warning;
  return CHART_COLORS.error;
};

/**
 * Get color for trend direction
 */
export const getTrendColor = (value: number, inverse: boolean = false): string => {
  if (value > 0) return inverse ? CHART_COLORS.error : CHART_COLORS.success;
  if (value < 0) return inverse ? CHART_COLORS.success : CHART_COLORS.error;
  return CHART_COLORS.neutral;
};

/**
 * Get gradient colors array
 */
export const getGradient = (type: keyof typeof CHART_COLORS.gradients): string[] => {
  return CHART_COLORS.gradients[type];
};

/**
 * Get category color by index
 */
export const getCategoryColor = (index: number): string => {
  return CHART_COLORS.categories[index % CHART_COLORS.categories.length];
};

/**
 * Calculate percentage change
 */
export const calculatePercentageChange = (current: number, previous: number): number => {
  if (previous === 0) return current > 0 ? 100 : 0;
  return ((current - previous) / previous) * 100;
};

/**
 * Calculate moving average
 */
export const calculateMovingAverage = (data: number[], window: number): number[] => {
  const result: number[] = [];
  for (let i = 0; i < data.length; i++) {
    const start = Math.max(0, i - window + 1);
    const subset = data.slice(start, i + 1);
    const average = subset.reduce((sum, val) => sum + val, 0) / subset.length;
    result.push(average);
  }
  return result;
};

/**
 * Generate gradient ID for SVG def
 */
export const generateGradientId = (prefix: string): string => {
  return `gradient-${prefix}-${Math.random().toString(36).substr(2, 9)}`;
};

/**
 * Create linear gradient definition
 */
export const createLinearGradientDef = (
  id: string,
  colors: string[],
  opacity: number = 1
): string => {
  return `
    <defs>
      <linearGradient id="${id}" x1="0" y1="0" x2="0" y2="1">
        ${colors
          .map(
            (color, index) =>
              `<stop offset="${(index / (colors.length - 1)) * 100}%" stopColor="${color}" stopOpacity="${opacity}" />`
          )
          .join('\n        ')}
      </linearGradient>
    </defs>
  `;
};

/**
 * Calculate confidence interval
 */
export const calculateConfidenceInterval = (
  data: number[],
  confidence: number = 0.95
): { lower: number; upper: number; mean: number } => {
  const mean = data.reduce((sum, val) => sum + val, 0) / data.length;
  const variance =
    data.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / data.length;
  const stdDev = Math.sqrt(variance);

  const zScore = confidence === 0.95 ? 1.96 : confidence === 0.99 ? 2.58 : 1.64;
  const margin = zScore * (stdDev / Math.sqrt(data.length));

  return {
    mean,
    lower: mean - margin,
    upper: mean + margin,
  };
};

/**
 * Generate forecast data points
 */
export const generateForecast = (
  historical: number[],
  periods: number,
  confidence: number = 0.95
): Array<{ predicted: number; lower: number; upper: number }> => {
  // Simple linear regression for trend
  const n = historical.length;
  const xValues = Array.from({ length: n }, (_, i) => i);
  const xMean = xValues.reduce((a, b) => a + b, 0) / n;
  const yMean = historical.reduce((a, b) => a + b, 0) / n;

  let numerator = 0;
  let denominator = 0;
  for (let i = 0; i < n; i++) {
    numerator += (xValues[i] - xMean) * (historical[i] - yMean);
    denominator += Math.pow(xValues[i] - xMean, 2);
  }

  const slope = numerator / denominator;
  const intercept = yMean - slope * xMean;

  // Calculate residual standard error
  const residuals = historical.map((y, i) => y - (slope * i + intercept));
  const rse = Math.sqrt(
    residuals.reduce((sum, r) => sum + r * r, 0) / (n - 2)
  );

  // Generate forecast
  const forecast = [];
  const zScore = confidence === 0.95 ? 1.96 : 2.58;

  for (let i = 0; i < periods; i++) {
    const x = n + i;
    const predicted = slope * x + intercept;
    const margin = zScore * rse * Math.sqrt(1 + 1 / n + Math.pow(x - xMean, 2) / denominator);

    forecast.push({
      predicted,
      lower: predicted - margin,
      upper: predicted + margin,
    });
  }

  return forecast;
};

/**
 * Normalize data to 0-1 range
 */
export const normalizeData = (data: number[]): number[] => {
  const min = Math.min(...data);
  const max = Math.max(...data);
  const range = max - min;

  if (range === 0) return data.map(() => 0.5);

  return data.map((value) => (value - min) / range);
};

/**
 * Calculate percentile
 */
export const calculatePercentile = (data: number[], percentile: number): number => {
  const sorted = [...data].sort((a, b) => a - b);
  const index = (percentile / 100) * (sorted.length - 1);
  const lower = Math.floor(index);
  const upper = Math.ceil(index);
  const weight = index - lower;

  return sorted[lower] * (1 - weight) + sorted[upper] * weight;
};

/**
 * Group data by time period
 */
export const groupByTimePeriod = <T extends { date: string }>(
  data: T[],
  period: 'day' | 'week' | 'month'
): { [key: string]: T[] } => {
  return data.reduce((groups, item) => {
    const date = new Date(item.date);
    let key: string;

    switch (period) {
      case 'day':
        key = date.toISOString().split('T')[0];
        break;
      case 'week':
        const weekStart = new Date(date);
        weekStart.setDate(date.getDate() - date.getDay());
        key = weekStart.toISOString().split('T')[0];
        break;
      case 'month':
        key = `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, '0')}`;
        break;
      default:
        key = date.toISOString().split('T')[0];
    }

    if (!groups[key]) {
      groups[key] = [];
    }
    groups[key].push(item);

    return groups;
  }, {} as { [key: string]: T[] });
};

/**
 * Calculate ROAS (Return on Ad Spend)
 */
export const calculateROAS = (revenue: number, cost: number): number => {
  return cost > 0 ? revenue / cost : 0;
};

/**
 * Calculate CPA (Cost Per Acquisition)
 */
export const calculateCPA = (cost: number, conversions: number): number => {
  return conversions > 0 ? cost / conversions : 0;
};

/**
 * Calculate CTR (Click-Through Rate)
 */
export const calculateCTR = (clicks: number, impressions: number): number => {
  return impressions > 0 ? (clicks / impressions) * 100 : 0;
};

/**
 * Calculate conversion rate
 */
export const calculateConversionRate = (conversions: number, clicks: number): number => {
  return clicks > 0 ? (conversions / clicks) * 100 : 0;
};

/**
 * Get responsive chart height
 */
export const getResponsiveHeight = (width: number): number => {
  if (width < 768) return 250; // Mobile
  if (width < 1024) return 300; // Tablet
  if (width < 1440) return 350; // Desktop
  return 400; // Wide screen
};

/**
 * Format axis tick for large numbers
 */
export const formatAxisTick = (value: number): string => {
  if (value >= 1000000) return `${(value / 1000000).toFixed(1)}M`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
  return value.toFixed(0);
};

/**
 * Get color with opacity
 */
export const colorWithOpacity = (color: string, opacity: number): string => {
  // Convert hex to rgba
  const hex = color.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);

  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};

export default {
  formatCurrency,
  formatPercentage,
  formatCompactNumber,
  formatNumber,
  getPerformanceColor,
  getTrendColor,
  getGradient,
  getCategoryColor,
  calculatePercentageChange,
  calculateMovingAverage,
  generateGradientId,
  createLinearGradientDef,
  calculateConfidenceInterval,
  generateForecast,
  normalizeData,
  calculatePercentile,
  groupByTimePeriod,
  calculateROAS,
  calculateCPA,
  calculateCTR,
  calculateConversionRate,
  getResponsiveHeight,
  formatAxisTick,
  colorWithOpacity,
};
