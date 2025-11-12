/**
 * Dynamic Confidence Score Calculator
 *
 * Calculates confidence scores for AI insights based on data quality factors:
 * - Sample size (traffic volume, conversion count)
 * - Data recency (how fresh the data is)
 * - Statistical significance
 * - Benchmark quality (database vs fallback)
 */

interface DataQualityFactors {
  sampleSize?: number; // Number of data points (impressions, sessions, clicks, etc.)
  conversions?: number; // Number of conversions
  daysOfData?: number; // Number of days in dataset
  benchmarkSource?: 'database' | 'fallback'; // Whether benchmark came from DB or hardcoded
  metricVariance?: number; // Coefficient of variation (optional)
}

export class ConfidenceCalculator {
  /**
   * Calculate confidence score (0-100) based on data quality
   */
  static calculateConfidence(factors: DataQualityFactors): number {
    let confidence = 50; // Base confidence

    // Factor 1: Sample Size (0-25 points)
    confidence += this.calculateSampleSizeScore(factors.sampleSize || 0);

    // Factor 2: Conversion Volume (0-15 points)
    confidence += this.calculateConversionScore(factors.conversions || 0);

    // Factor 3: Data Recency (0-10 points)
    confidence += this.calculateRecencyScore(factors.daysOfData || 30);

    // Factor 4: Benchmark Quality (0-10 points)
    confidence += this.calculateBenchmarkScore(factors.benchmarkSource || 'fallback');

    // Cap at 100
    return Math.min(Math.round(confidence), 100);
  }

  /**
   * Sample size scoring (0-25 points)
   * More data = higher confidence in statistical significance
   */
  private static calculateSampleSizeScore(sampleSize: number): number {
    if (sampleSize >= 100000) return 25; // Excellent sample
    if (sampleSize >= 50000) return 22;
    if (sampleSize >= 10000) return 18;
    if (sampleSize >= 5000) return 14;
    if (sampleSize >= 1000) return 10;
    if (sampleSize >= 500) return 6;
    if (sampleSize >= 100) return 3;
    return 0; // Insufficient sample
  }

  /**
   * Conversion volume scoring (0-15 points)
   * More conversions = higher confidence in conversion-related insights
   */
  private static calculateConversionScore(conversions: number): number {
    if (conversions >= 500) return 15; // Statistically significant
    if (conversions >= 200) return 12;
    if (conversions >= 100) return 10;
    if (conversions >= 50) return 8;
    if (conversions >= 20) return 5;
    if (conversions >= 10) return 3;
    return 0; // Not enough conversions
  }

  /**
   * Data recency scoring (0-10 points)
   * Recent data = higher confidence (trends haven't shifted)
   */
  private static calculateRecencyScore(daysOfData: number): number {
    if (daysOfData <= 7) return 10; // Last week (most relevant)
    if (daysOfData <= 14) return 9;
    if (daysOfData <= 30) return 8; // Last month (standard)
    if (daysOfData <= 60) return 6;
    if (daysOfData <= 90) return 4;
    return 2; // Data may be stale
  }

  /**
   * Benchmark quality scoring (0-10 points)
   * Database benchmarks = higher confidence than hardcoded fallbacks
   */
  private static calculateBenchmarkScore(source: 'database' | 'fallback'): number {
    return source === 'database' ? 10 : 5;
  }

  /**
   * Calculate confidence for campaign performance insights
   */
  static forCampaignInsight(
    impressions: number,
    clicks: number,
    conversions: number,
    benchmarkSource: 'database' | 'fallback' = 'fallback'
  ): number {
    return this.calculateConfidence({
      sampleSize: impressions,
      conversions,
      daysOfData: 30, // Assume last 30 days
      benchmarkSource,
    });
  }

  /**
   * Calculate confidence for GA4 insights
   */
  static forGA4Insight(
    sessions: number,
    conversions: number,
    benchmarkSource: 'database' | 'fallback' = 'fallback'
  ): number {
    return this.calculateConfidence({
      sampleSize: sessions,
      conversions,
      daysOfData: 30,
      benchmarkSource,
    });
  }

  /**
   * Calculate confidence for unified cross-platform insights
   */
  static forUnifiedInsight(
    totalSpend: number,
    totalConversions: number,
    platformCount: number,
    benchmarkSource: 'database' | 'fallback' = 'fallback'
  ): number {
    // More platforms = more data complexity, slightly lower confidence
    const platformPenalty = Math.max(0, 5 - platformCount);

    let confidence = this.calculateConfidence({
      sampleSize: totalSpend > 0 ? totalSpend / 10 : 0, // Spend as proxy for scale
      conversions: totalConversions,
      daysOfData: 30,
      benchmarkSource,
    });

    return Math.max(50, confidence - platformPenalty);
  }

  /**
   * Calculate confidence for e-commerce insights
   */
  static forEcommerceInsight(
    orders: number,
    clicks: number,
    benchmarkSource: 'database' | 'fallback' = 'fallback'
  ): number {
    return this.calculateConfidence({
      sampleSize: clicks,
      conversions: orders,
      daysOfData: 30,
      benchmarkSource,
    });
  }

  /**
   * Adjust confidence based on deviation from benchmark
   * Large deviations (very good or very bad) increase confidence
   */
  static adjustForDeviation(
    baseConfidence: number,
    actualValue: number,
    benchmarkValue: number
  ): number {
    if (benchmarkValue === 0) return baseConfidence;

    const deviationPercent = Math.abs((actualValue - benchmarkValue) / benchmarkValue);

    // Large deviations (>50%) add confidence (clear signal)
    if (deviationPercent > 0.5) return Math.min(baseConfidence + 5, 100);
    if (deviationPercent > 0.3) return Math.min(baseConfidence + 3, 100);

    // Small deviations (<10%) reduce confidence (noisy signal)
    if (deviationPercent < 0.1) return Math.max(baseConfidence - 5, 50);

    return baseConfidence;
  }

  /**
   * Get confidence level label
   */
  static getConfidenceLabel(confidence: number): string {
    if (confidence >= 90) return 'Very High';
    if (confidence >= 80) return 'High';
    if (confidence >= 70) return 'Moderate';
    if (confidence >= 60) return 'Fair';
    return 'Low';
  }

  /**
   * Get confidence color for UI
   */
  static getConfidenceColor(confidence: number): string {
    if (confidence >= 85) return 'success';
    if (confidence >= 70) return 'primary';
    if (confidence >= 55) return 'warning';
    return 'error';
  }
}
