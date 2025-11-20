// Benchmark Service for fetching industry benchmarks
import { apiClient } from './api';
import { API_CONFIG } from '../config/api';

export interface Benchmark {
  benchmark_id: number;
  industry_vertical: string;
  industry_sub_vertical?: string;
  platform: string;
  metric_name: string;
  metric_category?: string;
  benchmark_value: number;
  benchmark_unit: string;
  excellent_threshold?: number;
  good_threshold?: number;
  average_threshold?: number;
  poor_threshold?: number;
  data_source?: string;
  sample_size?: number;
  confidence_score?: number;
  country_code: string;
  currency: string;
  valid_from: string;
  valid_until?: string;
  notes?: string;
}

export interface BenchmarkListResponse {
  industry_vertical: string;
  platform: string;
  country_code: string;
  benchmarks_count: number;
  benchmarks: Benchmark[];
}

export type PerformanceLevel = 'excellent' | 'good' | 'average' | 'poor' | 'unknown';

export const benchmarkService = {
  /**
   * Get all benchmarks for an industry and platform
   */
  async getBenchmarks(
    industryVertical: string = 'general',
    platform: string = 'google_ads',
    options?: {
      metrics?: string[];
      countryCode?: string;
    }
  ): Promise<BenchmarkListResponse> {
    try {
      const params: any = {
        industry_vertical: industryVertical,
        platform,
        country_code: options?.countryCode || 'ALL',
      };

      if (options?.metrics && options.metrics.length > 0) {
        params.metrics = options.metrics.join(',');
      }

      const response = await apiClient.get<BenchmarkListResponse>(
        `${API_CONFIG.BASE_URL}/benchmarks`,
        { params }
      );

      return response;
    } catch (error) {
      console.error('Error fetching benchmarks:', error);
      throw error;
    }
  },

  /**
   * Get benchmark for a specific metric
   */
  async getBenchmarkByMetric(
    metricName: string,
    industryVertical: string = 'general',
    platform: string = 'google_ads',
    countryCode: string = 'ALL'
  ): Promise<Benchmark> {
    try {
      const response = await apiClient.get<Benchmark>(
        `${API_CONFIG.BASE_URL}/benchmarks/${metricName}`,
        {
          params: {
            industry_vertical: industryVertical,
            platform,
            country_code: countryCode,
          },
        }
      );

      return response;
    } catch (error) {
      console.error(`Error fetching benchmark for ${metricName}:`, error);
      throw error;
    }
  },

  /**
   * Get benchmarks for multiple metrics
   * Returns a map of metric name to benchmark
   */
  async getBenchmarksForMetrics(
    metrics: string[],
    industryVertical: string = 'general',
    platform: string = 'google_ads',
    countryCode: string = 'ALL'
  ): Promise<Record<string, Benchmark>> {
    try {
      const response = await this.getBenchmarks(industryVertical, platform, {
        metrics,
        countryCode,
      });

      const benchmarkMap: Record<string, Benchmark> = {};
      response.benchmarks.forEach((benchmark) => {
        benchmarkMap[benchmark.metric_name] = benchmark;
      });

      return benchmarkMap;
    } catch (error) {
      console.error('Error fetching benchmarks for metrics:', error);
      throw error;
    }
  },

  /**
   * Compare a value against benchmark and determine performance level
   */
  getPerformanceLevel(value: number, benchmark: Benchmark): PerformanceLevel {
    if (!benchmark) return 'unknown';

    const { excellent_threshold, good_threshold, average_threshold, poor_threshold } = benchmark;

    // For metrics where lower is better (e.g., bounce_rate, cpc)
    const isInverseMetric = ['bounce_rate', 'cpc', 'cpm', 'cpa'].includes(
      benchmark.metric_name.toLowerCase()
    );

    if (isInverseMetric) {
      // Lower is better
      if (excellent_threshold !== undefined && value <= excellent_threshold) return 'excellent';
      if (good_threshold !== undefined && value <= good_threshold) return 'good';
      if (average_threshold !== undefined && value <= average_threshold) return 'average';
      if (poor_threshold !== undefined && value > poor_threshold) return 'poor';
    } else {
      // Higher is better
      if (excellent_threshold !== undefined && value >= excellent_threshold) return 'excellent';
      if (good_threshold !== undefined && value >= good_threshold) return 'good';
      if (average_threshold !== undefined && value >= average_threshold) return 'average';
      if (poor_threshold !== undefined && value < poor_threshold) return 'poor';
    }

    return 'unknown';
  },

  /**
   * Get performance level color for UI
   */
  getPerformanceLevelColor(level: PerformanceLevel): string {
    const colorMap: Record<PerformanceLevel, string> = {
      excellent: '#10b981', // green
      good: '#3b82f6', // blue
      average: '#f59e0b', // orange
      poor: '#ef4444', // red
      unknown: '#6b7280', // gray
    };

    return colorMap[level];
  },

  /**
   * Calculate performance score (0-100)
   */
  calculatePerformanceScore(value: number, benchmark: Benchmark): number {
    if (!benchmark || !benchmark.benchmark_value) return 50;

    const ratio = value / benchmark.benchmark_value;

    // For inverse metrics (lower is better), invert the ratio
    const isInverseMetric = ['bounce_rate', 'cpc', 'cpm', 'cpa'].includes(
      benchmark.metric_name.toLowerCase()
    );

    const score = isInverseMetric ? (2 - ratio) * 50 : ratio * 50;

    return Math.max(0, Math.min(100, score));
  },

  /**
   * Format benchmark value for display
   */
  formatBenchmarkValue(value: number, benchmark: Benchmark): string {
    const { benchmark_unit } = benchmark;

    switch (benchmark_unit) {
      case '%':
        return `${value.toFixed(2)}%`;
      case 'currency':
        return `${benchmark.currency} ${value.toFixed(2)}`;
      case 'ratio':
        return `${value.toFixed(2)}x`;
      case 'seconds':
        return `${Math.floor(value / 60)}:${(value % 60).toString().padStart(2, '0')}`;
      default:
        return value.toFixed(2);
    }
  },

  /**
   * Get performance insights based on benchmark comparison
   */
  getPerformanceInsight(value: number, benchmark: Benchmark): string {
    const level = this.getPerformanceLevel(value, benchmark);
    const diff = Math.abs(value - benchmark.benchmark_value);
    const diffPercent = (diff / benchmark.benchmark_value) * 100;

    const insights: Record<PerformanceLevel, string> = {
      excellent: `Excellent! You're ${diffPercent.toFixed(1)}% above the industry benchmark.`,
      good: `Good performance! You're ${diffPercent.toFixed(1)}% above average.`,
      average: `Meeting industry standards. ${diffPercent.toFixed(1)}% from benchmark.`,
      poor: `Below benchmark by ${diffPercent.toFixed(1)}%. Consider optimization strategies.`,
      unknown: 'Performance data needs more context for comparison.',
    };

    return insights[level];
  },

  /**
   * Cache management: Cache benchmarks to reduce API calls
   */
  _benchmarkCache: new Map<string, { data: BenchmarkListResponse; timestamp: number }>(),
  _cacheTimeout: 30 * 60 * 1000, // 30 minutes

  /**
   * Get cached benchmarks or fetch from API
   */
  async getBenchmarksWithCache(
    industryVertical: string,
    platform: string,
    countryCode: string = 'ALL'
  ): Promise<BenchmarkListResponse> {
    const cacheKey = `${industryVertical}_${platform}_${countryCode}`;
    const cached = this._benchmarkCache.get(cacheKey);

    if (cached && Date.now() - cached.timestamp < this._cacheTimeout) {
      return cached.data;
    }

    const data = await this.getBenchmarks(industryVertical, platform, { countryCode });
    this._benchmarkCache.set(cacheKey, { data, timestamp: Date.now() });

    return data;
  },

  /**
   * Clear benchmark cache
   */
  clearCache(): void {
    this._benchmarkCache.clear();
  },
};

export default benchmarkService;
