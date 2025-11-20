/**
 * Design Tokens for MarketingIQ Platform
 * AI-First Brand Identity with Purple/Indigo Gradient
 */

export const colors = {
  // Primary: AI Intelligence Purple/Indigo
  primary: {
    main: '#667eea',
    light: '#8b92f6',
    dark: '#5568d3',
    50: '#f3f4fb',
    100: '#e7e9f7',
    200: '#d4d8f0',
    300: '#b5bde8',
    400: '#8b92f6',
    500: '#667eea',
    600: '#5568d3',
    700: '#4654b8',
    800: '#3a4494',
    900: '#2f3777',
  },

  // Secondary: Purple accent
  secondary: {
    main: '#764ba2',
    light: '#9568c4',
    dark: '#5a3880',
    50: '#f8f4fb',
    100: '#f0e8f7',
    200: '#e0d1ef',
    300: '#d1b9e7',
    400: '#9568c4',
    500: '#764ba2',
    600: '#5a3880',
    700: '#4a2f69',
    800: '#3a2553',
    900: '#2e1d42',
  },

  // Semantic colors
  success: {
    main: '#10b981',
    light: '#34d399',
    dark: '#059669',
    50: '#ecfdf5',
    100: '#d1fae5',
    500: '#10b981',
    900: '#064e3b',
  },

  warning: {
    main: '#f59e0b',
    light: '#fbbf24',
    dark: '#d97706',
    50: '#fffbeb',
    100: '#fef3c7',
    500: '#f59e0b',
    900: '#78350f',
  },

  error: {
    main: '#ef4444',
    light: '#f87171',
    dark: '#dc2626',
    50: '#fef2f2',
    100: '#fee2e2',
    500: '#ef4444',
    900: '#7f1d1d',
  },

  info: {
    main: '#3b82f6',
    light: '#60a5fa',
    dark: '#2563eb',
    50: '#eff6ff',
    100: '#dbeafe',
    500: '#3b82f6',
    900: '#1e3a8a',
  },

  // AI Feature Colors
  ai: {
    gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    gradientHover: 'linear-gradient(135deg, #7a8eee 0%, #8657b0 100%)',
    glow: 'rgba(102, 126, 234, 0.15)',
    glowStrong: 'rgba(102, 126, 234, 0.25)',
    badge: '#667eea',
    text: '#ffffff',
  },

  // Chart colors
  chart: {
    primary: '#6366f1',
    secondary: '#8b5cf6',
    success: '#10b981',
    warning: '#f59e0b',
    error: '#ef4444',
    info: '#3b82f6',
    teal: '#14b8a6',
    pink: '#ec4899',
    orange: '#f97316',
    cyan: '#06b6d4',
  },

  // Neutral grays
  gray: {
    50: '#f9fafb',
    100: '#f3f4f6',
    200: '#e5e7eb',
    300: '#d1d5db',
    400: '#9ca3af',
    500: '#6b7280',
    600: '#4b5563',
    700: '#374151',
    800: '#1f2937',
    900: '#111827',
  },

  // Background colors
  background: {
    default: '#f8f9fa',
    paper: '#ffffff',
    dark: '#0f172a',
    elevation1: '#ffffff',
    elevation2: '#f9fafb',
  },

  // Text colors
  text: {
    primary: '#2C3E50',
    secondary: '#546E7A',
    disabled: '#9ca3af',
    white: '#ffffff',
    dark: '#111827',
  },
};

export const typography = {
  fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',

  // Font weights
  weights: {
    light: 300,
    normal: 400,
    medium: 500,
    semibold: 600,
    bold: 700,
    extrabold: 800,
  },

  // Page hierarchy
  pageTitle: {
    size: '2rem', // 32px
    weight: 600,
    lineHeight: 1.2,
    letterSpacing: '-0.02em',
  },

  sectionTitle: {
    size: '1.5rem', // 24px
    weight: 600,
    lineHeight: 1.3,
    letterSpacing: '-0.01em',
  },

  cardTitle: {
    size: '1.125rem', // 18px
    weight: 500,
    lineHeight: 1.4,
    letterSpacing: '0',
  },

  // Body text
  body: {
    size: '1rem', // 16px
    weight: 400,
    lineHeight: 1.5,
    letterSpacing: '0',
  },

  bodySmall: {
    size: '0.875rem', // 14px
    weight: 400,
    lineHeight: 1.5,
    letterSpacing: '0',
  },

  caption: {
    size: '0.75rem', // 12px
    weight: 400,
    lineHeight: 1.4,
    letterSpacing: '0.01em',
  },

  overline: {
    size: '0.625rem', // 10px
    weight: 600,
    lineHeight: 1.5,
    letterSpacing: '0.08em',
    textTransform: 'uppercase',
  },
};

export const spacing = {
  xs: 4, // 4px
  sm: 8, // 8px
  md: 16, // 16px (base unit)
  lg: 24, // 24px
  xl: 32, // 32px
  xxl: 48, // 48px
  xxxl: 64, // 64px
  huge: 96, // 96px
};

export const borderRadius = {
  none: 0,
  sm: 4,
  md: 8,
  lg: 12,
  xl: 16,
  xxl: 24,
  full: 9999,
};

export const shadows = {
  none: 'none',
  sm: '0px 2px 4px rgba(0,0,0,0.05)',
  md: '0px 4px 12px rgba(0,0,0,0.08)',
  lg: '0px 8px 24px rgba(0,0,0,0.12)',
  xl: '0px 12px 32px rgba(0,0,0,0.16)',
  xxl: '0px 24px 48px rgba(0,0,0,0.20)',

  // AI-specific shadows
  aiGlow: '0px 8px 32px rgba(102, 126, 234, 0.25)',
  aiGlowStrong: '0px 12px 48px rgba(102, 126, 234, 0.35)',
};

export const transitions = {
  fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
  normal: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
  slow: '500ms cubic-bezier(0.4, 0, 0.2, 1)',

  // Easing functions
  easeIn: 'cubic-bezier(0.4, 0, 1, 1)',
  easeOut: 'cubic-bezier(0, 0, 0.2, 1)',
  easeInOut: 'cubic-bezier(0.4, 0, 0.2, 1)',
  sharp: 'cubic-bezier(0.4, 0, 0.6, 1)',
};

export const breakpoints = {
  xs: 0,
  sm: 600,
  md: 900,
  lg: 1200,
  xl: 1536,
};

export const zIndex = {
  mobileStepper: 1000,
  speedDial: 1050,
  appBar: 1100,
  drawer: 1200,
  modal: 1300,
  snackbar: 1400,
  tooltip: 1500,
};

// Component-specific tokens
export const components = {
  button: {
    borderRadius: borderRadius.md,
    paddingX: spacing.lg,
    paddingY: 10,
    minHeight: 40,
  },

  card: {
    borderRadius: borderRadius.xl,
    padding: spacing.lg,
    elevation: shadows.md,
    elevationHover: shadows.lg,
  },

  chip: {
    borderRadius: borderRadius.md,
    paddingX: spacing.md,
    paddingY: 6,
    height: 32,
  },

  input: {
    borderRadius: borderRadius.md,
    height: 44,
    paddingX: spacing.md,
  },

  kpiCard: {
    minHeight: 120,
    padding: spacing.lg,
    borderRadius: borderRadius.lg,
  },
};

// Export helper function to get color with opacity
export const withOpacity = (color: string, opacity: number): string => {
  // Convert hex to rgba
  const hex = color.replace('#', '');
  const r = parseInt(hex.substring(0, 2), 16);
  const g = parseInt(hex.substring(2, 4), 16);
  const b = parseInt(hex.substring(4, 6), 16);
  return `rgba(${r}, ${g}, ${b}, ${opacity})`;
};

export default {
  colors,
  typography,
  spacing,
  borderRadius,
  shadows,
  transitions,
  breakpoints,
  zIndex,
  components,
  withOpacity,
};
