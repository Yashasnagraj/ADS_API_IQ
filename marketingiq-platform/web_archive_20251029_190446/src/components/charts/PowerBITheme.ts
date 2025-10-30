/**
 * Power BI-Style Chart Theme Configuration
 * Professional, presentation-ready chart styling
 */

export const POWER_BI_CHART_CONFIG = {
  // Standard margins for all charts
  margin: {
    top: 20,
    right: 30,
    left: 60,
    bottom: 50,
  },

  // Axis styling
  axisStyle: {
    fontSize: 12,
    fontWeight: 500,
    stroke: '#666',
  },

  // Axis label styling
  axisLabelStyle: {
    fontWeight: 600,
    fontSize: 12,
    fill: '#333',
  },

  // Grid styling
  gridStyle: {
    strokeDasharray: '3 3',
    stroke: '#e0e0e0',
    strokeOpacity: 0.7,
  },

  // Tooltip styling
  tooltipStyle: {
    backgroundColor: 'rgba(255, 255, 255, 0.97)',
    border: '2px solid #1976d2',
    borderRadius: '8px',
    padding: '12px',
    boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
    fontSize: '13px',
  },

  // Legend styling
  legendStyle: {
    verticalAlign: 'top' as const,
    height: 40,
    wrapperStyle: { paddingBottom: '10px', fontSize: '12px' },
    iconSize: 12,
  },

  // Color palette (Power BI inspired)
  colors: {
    primary: '#1976d2',
    success: '#4caf50',
    warning: '#ff9800',
    error: '#f44336',
    info: '#00bcd4',
    purple: '#9c27b0',
    teal: '#009688',
    amber: '#ffc107',
    indigo: '#3f51b5',
    pink: '#e91e63',
  },

  // Chart-specific defaults
  lineChart: {
    strokeWidth: 3,
    dotSize: 5,
    activeDotSize: 8,
  },

  barChart: {
    radius: [4, 4, 0, 0] as [number, number, number, number],
    barSize: 30,
  },

  areaChart: {
    strokeWidth: 2,
    fillOpacity: 0.3,
  },
};

/**
 * Format currency value
 */
export const formatCurrency = (value: number): string => {
  if (value === 0) return '₹0';
  if (value >= 10000000) return `₹${(value / 10000000).toFixed(2)}Cr`;
  if (value >= 100000) return `₹${(value / 100000).toFixed(2)}L`;
  if (value >= 1000) return `₹${(value / 1000).toFixed(1)}K`;
  return `₹${value.toFixed(2)}`;
};

/**
 * Format currency (full, no abbreviation)
 */
export const formatCurrencyFull = (value: number): string => {
  return `₹${value.toLocaleString('en-IN', {
    minimumFractionDigits: 0,
    maximumFractionDigits: 2
  })}`;
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number, decimals: number = 2): string => {
  if (typeof value !== 'number' || isNaN(value)) return '0.00%';
  return `${(value * 100).toFixed(decimals)}%`;
};

/**
 * Format large numbers
 */
export const formatNumber = (value: number): string => {
  if (value === 0) return '0';
  if (value >= 10000000) return `${(value / 10000000).toFixed(1)}Cr`;
  if (value >= 100000) return `${(value / 100000).toFixed(1)}L`;
  if (value >= 1000) return `${(value / 1000).toFixed(1)}K`;
  return value.toLocaleString('en-IN');
};

/**
 * Format number (full, with commas)
 */
export const formatNumberFull = (value: number): string => {
  return value.toLocaleString('en-IN');
};

/**
 * Get color by index (for charts with multiple series)
 */
export const getColorByIndex = (index: number): string => {
  const colors = Object.values(POWER_BI_CHART_CONFIG.colors);
  return colors[index % colors.length];
};

/**
 * Custom tooltip content renderer
 */
export interface TooltipFormatterConfig {
  currencyFields?: string[];
  percentageFields?: string[];
  numberFields?: string[];
  labelFormatter?: (label: string) => string;
}

export const createTooltipFormatter = (config: TooltipFormatterConfig = {}) => {
  return (value: any, name: string) => {
    const { currencyFields = [], percentageFields = [], numberFields = [] } = config;

    // Check if this field should be formatted as currency
    if (currencyFields.includes(name) || name.toLowerCase().includes('cost') || name.toLowerCase().includes('spend') || name.toLowerCase().includes('cpc') || name.toLowerCase().includes('budget')) {
      return [formatCurrencyFull(value), name];
    }

    // Check if this field should be formatted as percentage
    if (percentageFields.includes(name) || name.toLowerCase().includes('ctr') || name.toLowerCase().includes('rate') || name.toLowerCase().includes('percent')) {
      const percentValue = typeof value === 'number' && value <= 1 ? value : value / 100;
      return [formatPercentage(percentValue), name];
    }

    // Check if this field should be formatted as number
    if (numberFields.includes(name) || name.toLowerCase().includes('clicks') || name.toLowerCase().includes('impressions') || name.toLowerCase().includes('conversions')) {
      return [formatNumberFull(value), name];
    }

    // Default: return as-is with comma formatting
    if (typeof value === 'number') {
      return [formatNumberFull(value), name];
    }

    return [value, name];
  };
};

/**
 * Standard X-Axis configuration
 */
export const getXAxisConfig = (label: string, dataKey: string = 'date') => ({
  dataKey,
  label: {
    value: label,
    position: 'insideBottom' as const,
    offset: -15,
    style: POWER_BI_CHART_CONFIG.axisLabelStyle,
  },
  tick: { fontSize: 12, fill: '#666' },
  stroke: '#666',
  height: 60,
});

/**
 * Standard Y-Axis configuration
 */
export const getYAxisConfig = (label: string, formatter?: (value: number) => string) => ({
  label: {
    value: label,
    angle: -90,
    position: 'insideLeft' as const,
    offset: 10,
    style: POWER_BI_CHART_CONFIG.axisLabelStyle,
  },
  tick: { fontSize: 12, fill: '#666' },
  stroke: '#666',
  width: 80,
  tickFormatter: formatter || formatNumber,
});

/**
 * Standard Tooltip configuration
 */
export const getTooltipConfig = (formatterConfig?: TooltipFormatterConfig) => ({
  formatter: createTooltipFormatter(formatterConfig),
  labelFormatter: formatterConfig?.labelFormatter || ((label: string) => `${label}`),
  contentStyle: POWER_BI_CHART_CONFIG.tooltipStyle,
  cursor: { fill: 'rgba(0, 0, 0, 0.05)' },
});

/**
 * Standard Legend configuration
 */
export const getLegendConfig = (position: 'top' | 'bottom' = 'top') => ({
  verticalAlign: position,
  height: 40,
  wrapperStyle: { paddingBottom: position === 'top' ? '15px' : '0', fontSize: '12px' },
  iconSize: 12,
});

/**
 * Standard CartesianGrid configuration
 */
export const getCartesianGridConfig = () => ({
  strokeDasharray: '3 3',
  stroke: '#e0e0e0',
  strokeOpacity: 0.7,
});

/**
 * Mock data generator for empty states
 */
export const generateMockChartData = (days: number = 7, type: 'line' | 'bar' | 'area' = 'line') => {
  const data = [];
  const today = new Date();

  for (let i = days - 1; i >= 0; i--) {
    const date = new Date(today);
    date.setDate(date.getDate() - i);
    const dateStr = date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });

    data.push({
      date: dateStr,
      impressions: Math.floor(Math.random() * 50000) + 10000,
      clicks: Math.floor(Math.random() * 2000) + 500,
      cost: Math.floor(Math.random() * 5000) + 1000,
      conversions: Math.floor(Math.random() * 100) + 10,
      ctr: (Math.random() * 0.05) + 0.01,
      cpc: (Math.random() * 2) + 0.5,
    });
  }

  return data;
};

export default POWER_BI_CHART_CONFIG;
