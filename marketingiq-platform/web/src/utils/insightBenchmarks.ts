/**
 * Benchmark Helper for Insight Generator
 *
 * Provides a simple interface to fetch and cache benchmarks for AI insights.
 * Falls back to hardcoded defaults if API is unavailable.
 */

import { benchmarkService, Benchmark } from '../services/benchmarkService';

interface BenchmarkSet {
  ctr: number;
  cpc: number;
  roas: number;
  conversion_rate: number;
  bounce_rate?: number;
  avg_session_duration?: number;
  pages_per_session?: number;
  blended_roas?: number;
  aov?: number;
  repeat_purchase_rate?: number;
}

class InsightBenchmarkManager {
  private cache: Map<string, BenchmarkSet> = new Map();
  private fetchPromises: Map<string, Promise<BenchmarkSet>> = new Map();

  // Fallback values (same as current hardcoded)
  private readonly FALLBACK_BENCHMARKS = {
    google_ads: {
      ctr: 3.17,
      cpc: 2.69,
      roas: 2.0,
      conversion_rate: 3.75,
    },
    ga4: {
      ctr: 0,
      cpc: 0,
      conversion_rate: 2.35,
      bounce_rate: 45,
      avg_session_duration: 120,
      pages_per_session: 2.5,
      roas: 0,
    },
    unified: {
      ctr: 0,
      cpc: 0,
      roas: 0,
      conversion_rate: 0,
      blended_roas: 2.5,
    },
    ecommerce: {
      ctr: 0,
      cpc: 0,
      roas: 4.0,
      conversion_rate: 2.5,
      aov: 3500,
      repeat_purchase_rate: 30,
    },
  };

  /**
   * Get benchmarks for a specific platform and industry
   * Returns cached values if available, otherwise fetches from API
   */
  async getBenchmarks(
    platform: 'google_ads' | 'ga4' | 'unified' | 'ecommerce',
    industry: string = 'general'
  ): Promise<BenchmarkSet> {
    const cacheKey = `${platform}_${industry}`;

    // Return cached if available
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    // Return pending promise if already fetching
    if (this.fetchPromises.has(cacheKey)) {
      return this.fetchPromises.get(cacheKey)!;
    }

    // Fetch from API
    const fetchPromise = this.fetchBenchmarksFromAPI(platform, industry);
    this.fetchPromises.set(cacheKey, fetchPromise);

    try {
      const benchmarks = await fetchPromise;
      this.cache.set(cacheKey, benchmarks);
      this.fetchPromises.delete(cacheKey);
      return benchmarks;
    } catch (error) {
      console.warn(`Failed to fetch benchmarks for ${platform}:`, error);
      this.fetchPromises.delete(cacheKey);
      // Return fallback
      return this.FALLBACK_BENCHMARKS[platform];
    }
  }

  /**
   * Get benchmarks synchronously (returns fallback immediately, fetches in background)
   */
  getBenchmarksSync(
    platform: 'google_ads' | 'ga4' | 'unified' | 'ecommerce',
    industry: string = 'general'
  ): BenchmarkSet {
    const cacheKey = `${platform}_${industry}`;

    // Return cached if available
    if (this.cache.has(cacheKey)) {
      return this.cache.get(cacheKey)!;
    }

    // Start fetching in background
    this.getBenchmarks(platform, industry).catch(() => {
      // Silently fail, fallback already returned
    });

    // Return fallback immediately
    return this.FALLBACK_BENCHMARKS[platform];
  }

  /**
   * Fetch benchmarks from API and convert to BenchmarkSet
   */
  private async fetchBenchmarksFromAPI(
    platform: string,
    industry: string
  ): Promise<BenchmarkSet> {
    const metrics: string[] = [];

    // Determine which metrics to fetch based on platform
    switch (platform) {
      case 'google_ads':
        metrics.push('ctr', 'cpc', 'roas', 'conversion_rate');
        break;
      case 'ga4':
        metrics.push(
          'conversion_rate',
          'bounce_rate',
          'avg_session_duration',
          'pages_per_session'
        );
        break;
      case 'unified':
        metrics.push('blended_roas');
        break;
      case 'ecommerce':
        metrics.push('roas', 'conversion_rate', 'aov', 'repeat_purchase_rate');
        break;
    }

    const benchmarkMap = await benchmarkService.getBenchmarksForMetrics(
      metrics,
      industry,
      platform,
      'ALL'
    );

    // Convert to BenchmarkSet
    const benchmarkSet: BenchmarkSet = {
      ctr: benchmarkMap.ctr?.benchmark_value || this.FALLBACK_BENCHMARKS[platform].ctr || 0,
      cpc: benchmarkMap.cpc?.benchmark_value || this.FALLBACK_BENCHMARKS[platform].cpc || 0,
      roas: benchmarkMap.roas?.benchmark_value || this.FALLBACK_BENCHMARKS[platform].roas || 0,
      conversion_rate:
        benchmarkMap.conversion_rate?.benchmark_value ||
        this.FALLBACK_BENCHMARKS[platform].conversion_rate ||
        0,
    };

    // Add platform-specific fields
    if (platform === 'ga4') {
      benchmarkSet.bounce_rate = benchmarkMap.bounce_rate?.benchmark_value || 45;
      benchmarkSet.avg_session_duration =
        benchmarkMap.avg_session_duration?.benchmark_value || 120;
      benchmarkSet.pages_per_session = benchmarkMap.pages_per_session?.benchmark_value || 2.5;
    }

    if (platform === 'unified') {
      benchmarkSet.blended_roas = benchmarkMap.blended_roas?.benchmark_value || 2.5;
    }

    if (platform === 'ecommerce') {
      benchmarkSet.aov = benchmarkMap.aov?.benchmark_value || 3500;
      benchmarkSet.repeat_purchase_rate = benchmarkMap.repeat_purchase_rate?.benchmark_value || 30;
    }

    return benchmarkSet;
  }

  /**
   * Clear cache (useful for testing or manual refresh)
   */
  clearCache() {
    this.cache.clear();
    this.fetchPromises.clear();
  }

  /**
   * Pre-fetch benchmarks for common platforms
   */
  async prefetchCommonBenchmarks(industry: string = 'general') {
    const platforms: Array<'google_ads' | 'ga4' | 'unified' | 'ecommerce'> = [
      'google_ads',
      'ga4',
      'unified',
      'ecommerce',
    ];

    await Promise.all(
      platforms.map((platform) => this.getBenchmarks(platform, industry))
    );
  }
}

// Singleton instance
export const insightBenchmarks = new InsightBenchmarkManager();

// Export types
export type { BenchmarkSet };
