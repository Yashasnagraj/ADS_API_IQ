/**
 * Utility functions for formatting numbers, currency, and percentages
 * All currency values should be in INR (₹)
 */

/**
 * Format number as INR currency
 * @param value - Numeric value to format
 * @param options - Optional formatting options
 * @returns Formatted currency string with ₹ symbol
 */
export function formatINR(
  value: number | null | undefined,
  options?: {
    minimumFractionDigits?: number;
    maximumFractionDigits?: number;
    showSymbol?: boolean;
  }
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-';
  }

  const {
    minimumFractionDigits = 0,
    maximumFractionDigits = 2,
    showSymbol = true
  } = options || {};

  const formatted = new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits,
    maximumFractionDigits
  }).format(value);

  // If showSymbol is false, remove the currency symbol
  if (!showSymbol) {
    return formatted.replace('₹', '').trim();
  }

  return formatted;
}

/**
 * Format number with Indian numbering system (lakhs, crores)
 * @param value - Numeric value to format
 * @returns Formatted number string
 */
export function formatNumber(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-';
  }

  return new Intl.NumberFormat('en-IN').format(value);
}

/**
 * Format percentage value
 * @param value - Numeric value (e.g., 5.23 for 5.23%)
 * @param decimals - Number of decimal places (default: 2)
 * @returns Formatted percentage string
 */
export function formatPercentage(
  value: number | null | undefined,
  decimals: number = 2
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-';
  }

  return `${value.toFixed(decimals)}%`;
}

/**
 * Format compact number (1K, 1M, 1B)
 * @param value - Numeric value to format
 * @returns Compact formatted number
 */
export function formatCompact(value: number | null | undefined): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-';
  }

  if (value >= 10000000) {
    // 1 crore = 10 million
    return `₹${(value / 10000000).toFixed(1)}Cr`;
  } else if (value >= 100000) {
    // 1 lakh = 100 thousand
    return `₹${(value / 100000).toFixed(1)}L`;
  } else if (value >= 1000) {
    return `₹${(value / 1000).toFixed(1)}K`;
  } else {
    return `₹${value.toFixed(0)}`;
  }
}

/**
 * Format decimal value with specified precision
 * @param value - Numeric value
 * @param decimals - Number of decimal places
 * @returns Formatted decimal string
 */
export function formatDecimal(
  value: number | null | undefined,
  decimals: number = 2
): string {
  if (value === null || value === undefined || isNaN(value)) {
    return '-';
  }

  return value.toFixed(decimals);
}

/**
 * Format cost from micros (Google Ads stores cost in micros)
 * @param micros - Cost in micros (1 rupee = 1,000,000 micros)
 * @returns Cost in rupees
 */
export function microToRupees(micros: number | null | undefined): number {
  if (micros === null || micros === undefined || isNaN(micros)) {
    return 0;
  }

  return micros / 1_000_000;
}

/**
 * Calculate CTR (Click-Through Rate)
 * @param clicks - Number of clicks
 * @param impressions - Number of impressions
 * @returns CTR as percentage (e.g., 5.23 for 5.23%)
 */
export function calculateCTR(
  clicks: number,
  impressions: number
): number | null {
  if (!impressions || impressions === 0) {
    return null;
  }

  return (clicks / impressions) * 100;
}

/**
 * Calculate average CPC (Cost Per Click)
 * @param cost - Total cost in rupees
 * @param clicks - Number of clicks
 * @returns Average CPC in rupees
 */
export function calculateAvgCPC(cost: number, clicks: number): number | null {
  if (!clicks || clicks === 0) {
    return null;
  }

  return cost / clicks;
}

/**
 * Calculate CPA (Cost Per Acquisition/Conversion)
 * @param cost - Total cost in rupees
 * @param conversions - Number of conversions
 * @returns CPA in rupees
 */
export function calculateCPA(
  cost: number,
  conversions: number
): number | null {
  if (!conversions || conversions === 0) {
    return null;
  }

  return cost / conversions;
}

/**
 * Calculate ROAS (Return on Ad Spend)
 * @param revenue - Total revenue in rupees
 * @param cost - Total cost in rupees
 * @returns ROAS as ratio (e.g., 3.5 for 3.5:1)
 */
export function calculateROAS(revenue: number, cost: number): number | null {
  if (!cost || cost === 0) {
    return null;
  }

  return revenue / cost;
}

/**
 * Calculate conversion rate
 * @param conversions - Number of conversions
 * @param clicks - Number of clicks
 * @returns Conversion rate as percentage
 */
export function calculateConversionRate(
  conversions: number,
  clicks: number
): number | null {
  if (!clicks || clicks === 0) {
    return null;
  }

  return (conversions / clicks) * 100;
}

/**
 * Ensure value is numeric (convert from string if needed)
 * @param value - Value to convert
 * @returns Numeric value or null
 */
export function ensureNumeric(value: any): number | null {
  if (value === null || value === undefined) {
    return null;
  }

  const num = typeof value === 'string' ? parseFloat(value) : Number(value);

  return isNaN(num) ? null : num;
}

/**
 * Format metric based on type
 * @param value - Value to format
 * @param type - Metric type
 * @returns Formatted string
 */
export function formatMetric(
  value: number | null | undefined,
  type: 'currency' | 'percentage' | 'number' | 'decimal'
): string {
  switch (type) {
    case 'currency':
      return formatINR(value);
    case 'percentage':
      return formatPercentage(value);
    case 'number':
      return formatNumber(value);
    case 'decimal':
      return formatDecimal(value);
    default:
      return value?.toString() || '-';
  }
}
