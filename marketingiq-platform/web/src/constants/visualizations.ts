/**
 * Visualization Constants and Configurations
 * Enterprise-grade chart settings used by billion-dollar companies
 */

// Chart color palette (matches theme + enterprise standards)
export const CHART_COLORS = {
  // Primary metrics
  primary: '#00bcd4',
  primaryLight: '#62efff',
  primaryDark: '#008ba3',

  // Success/Growth
  success: '#66bb6a',
  successLight: '#80e27e',
  successDark: '#087f23',

  // Warning/Attention
  warning: '#ffa726',
  warningLight: '#ffb74d',
  warningDark: '#f57c00',

  // Error/Decline
  error: '#ff5252',
  errorLight: '#ff867c',
  errorDark: '#c50e29',

  // Secondary metrics
  info: '#29b6f6',
  infoLight: '#73e8ff',
  infoDark: '#0086c3',

  // Tertiary
  purple: '#ab47bc',
  purpleLight: '#df78ef',
  purpleDark: '#790e8b',

  // Neutral/Gray scale
  neutral: '#78909c',
  neutralLight: '#a7c0cd',
  neutralDark: '#4b636e',

  // Category palette (for multi-series)
  categories: [
    '#00bcd4', // Cyan
    '#66bb6a', // Green
    '#ffa726', // Orange
    '#29b6f6', // Blue
    '#ab47bc', // Purple
    '#ff5252', // Red
    '#26a69a', // Teal
  ],

  // Performance quadrants
  highPerformer: '#66bb6a',
  potentialGrowth: '#29b6f6',
  needsAttention: '#ffa726',
  underPerformer: '#ff5252',

  // Gradients
  gradients: {
    success: ['#087f23', '#66bb6a', '#80e27e'],
    warning: ['#f57c00', '#ffa726', '#ffb74d'],
    error: ['#c50e29', '#ff5252', '#ff867c'],
    primary: ['#008ba3', '#00bcd4', '#62efff'],
    info: ['#0086c3', '#29b6f6', '#73e8ff'],
    purple: ['#790e8b', '#ab47bc', '#df78ef'],
  },
};

// Chart animation configurations
export const CHART_ANIMATIONS = {
  duration: 400,
  easing: 'ease-in-out',
  delay: 50, // stagger delay between elements

  // Specific animations
  fadeIn: {
    animationBegin: 0,
    animationDuration: 600,
    animationEasing: 'ease-out',
  },

  slideUp: {
    animationBegin: 100,
    animationDuration: 500,
    animationEasing: 'ease-out',
  },

  grow: {
    animationBegin: 0,
    animationDuration: 800,
    animationEasing: 'ease-out',
  },
};

// Responsive breakpoints for charts
export const CHART_BREAKPOINTS = {
  mobile: 320,
  tablet: 768,
  desktop: 1024,
  wide: 1440,

  // Height configurations
  heights: {
    compact: 200,
    standard: 300,
    expanded: 400,
    fullHeight: 500,
  },
};

// Tooltip configurations
export const TOOLTIP_STYLES = {
  dark: {
    backgroundColor: 'rgba(26, 26, 26, 0.95)',
    border: '1px solid rgba(255, 255, 255, 0.1)',
    borderRadius: '8px',
    padding: '12px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.5)',
  },

  light: {
    backgroundColor: 'rgba(255, 255, 255, 0.95)',
    border: '1px solid rgba(0, 0, 0, 0.1)',
    borderRadius: '8px',
    padding: '12px',
    boxShadow: '0 4px 20px rgba(0, 0, 0, 0.15)',
  },
};

// Grid and axis styling
export const AXIS_STYLES = {
  strokeDasharray: '3 3',
  strokeOpacity: 0.2,
  stroke: '#78909c',
};

export const GRID_STYLES = {
  strokeDasharray: '3 3',
  strokeOpacity: 0.1,
  stroke: '#78909c',
};

// Chart type configurations
export const CHART_CONFIGS = {
  line: {
    strokeWidth: 2,
    dot: {
      r: 4,
      strokeWidth: 2,
    },
    activeDot: {
      r: 6,
      strokeWidth: 2,
    },
  },

  area: {
    strokeWidth: 2,
    fillOpacity: 0.3,
    type: 'monotone' as const,
  },

  bar: {
    radius: [4, 4, 0, 0] as [number, number, number, number],
    maxBarSize: 60,
  },

  pie: {
    innerRadius: '60%',
    outerRadius: '100%',
    paddingAngle: 2,
    cornerRadius: 4,
  },

  scatter: {
    fillOpacity: 0.6,
    strokeWidth: 1.5,
  },
};

// Performance metric thresholds
export const PERFORMANCE_THRESHOLDS = {
  ctr: {
    excellent: 5.0,
    good: 3.0,
    average: 1.5,
    poor: 0,
  },

  conversionRate: {
    excellent: 10.0,
    good: 5.0,
    average: 2.0,
    poor: 0,
  },

  qualityScore: {
    excellent: 8,
    good: 6,
    average: 4,
    poor: 0,
  },

  roas: {
    excellent: 4.0,
    good: 2.0,
    average: 1.0,
    poor: 0,
  },
};

// Number formatting presets
export const NUMBER_FORMATS = {
  currency: {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  },

  currencyPrecise: {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  },

  percentage: {
    style: 'percent',
    minimumFractionDigits: 1,
    maximumFractionDigits: 1,
  },

  percentagePrecise: {
    style: 'percent',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  },

  number: {
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  },

  decimal: {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  },
};

// Chart margin presets
export const CHART_MARGINS = {
  standard: { top: 20, right: 30, left: 20, bottom: 20 },
  compact: { top: 10, right: 20, left: 10, bottom: 10 },
  withLabels: { top: 20, right: 30, left: 60, bottom: 40 },
  withLegend: { top: 20, right: 30, left: 20, bottom: 60 },
};

// Legend configurations
export const LEGEND_CONFIG = {
  iconType: 'circle' as const,
  layout: 'horizontal' as const,
  verticalAlign: 'bottom' as const,
  align: 'center' as const,
  wrapperStyle: {
    paddingTop: '20px',
  },
};

export default {
  CHART_COLORS,
  CHART_ANIMATIONS,
  CHART_BREAKPOINTS,
  TOOLTIP_STYLES,
  AXIS_STYLES,
  GRID_STYLES,
  CHART_CONFIGS,
  PERFORMANCE_THRESHOLDS,
  NUMBER_FORMATS,
  CHART_MARGINS,
  LEGEND_CONFIG,
};
