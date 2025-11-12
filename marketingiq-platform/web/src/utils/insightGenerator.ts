/**
 * AI Insight Generator - Natural Language Intelligence
 *
 * Generates human-readable, contextual insights from campaign data
 * that sound genuinely intelligent, not templated.
 */

import { insightBenchmarks } from './insightBenchmarks';
import { ConfidenceCalculator } from './confidenceCalculator';

interface CampaignMetrics {
  campaign_name?: string;
  name?: string;
  metrics?: {
    impressions?: number;
    clicks?: number;
    cost?: number;
    conversions?: number;
    ctr?: number;
    cpc?: number;
    conversion_value?: number;
  };
  spend?: number;
  impressions?: number;
  clicks?: number;
  conversions?: number;
  ctr?: number;
  roas?: number;
}

interface InsightResult {
  type: 'success' | 'warning' | 'danger' | 'info';
  title: string;
  message: string;
  impact: string;
  confidence: number;
  actionable: boolean;
  actions?: string[];
  impactScore?: number; // 0-100 for visualization
  whyItMatters?: string; // Contextual explanation
  category?: 'Performance' | 'Spend' | 'Conversion' | 'General';
}

/**
 * Analyze campaign performance and generate natural language insights
 */
export class SmartInsightGenerator {

  /**
   * Generate performance insights from campaign data
   */
  static analyzeCampaignPerformance(campaigns: CampaignMetrics[]): InsightResult[] {
    const insights: InsightResult[] = [];

    if (!campaigns || campaigns.length === 0) {
      return [{
        type: 'info',
        title: 'No Campaign Data',
        message: 'Connect your advertising accounts to start receiving AI-powered insights.',
        impact: 'Setup required',
        confidence: 100,
        actionable: false,
      }];
    }

    // Calculate aggregate metrics
    const totalSpend = campaigns.reduce((sum, c) => sum + (c.metrics?.cost || c.spend || 0), 0);
    const totalClicks = campaigns.reduce((sum, c) => sum + (c.metrics?.clicks || c.clicks || 0), 0);
    const totalImpressions = campaigns.reduce((sum, c) => sum + (c.metrics?.impressions || c.impressions || 0), 0);
    const totalConversions = campaigns.reduce((sum, c) => sum + (c.metrics?.conversions || c.conversions || 0), 0);
    const totalConversionValue = campaigns.reduce((sum, c) => sum + (c.metrics?.conversion_value || 0), 0);

    const avgCTR = totalImpressions > 0 ? (totalClicks / totalImpressions) * 100 : 0;
    const avgCPC = totalClicks > 0 ? totalSpend / totalClicks : 0;
    const overallROAS = totalSpend > 0 ? totalConversionValue / totalSpend : 0;
    const conversionRate = totalClicks > 0 ? (totalConversions / totalClicks) * 100 : 0;

    // Industry benchmarks - dynamically fetched from database
    const benchmarks = insightBenchmarks.getBenchmarksSync('google_ads', 'general');
    const benchmarkCTR = benchmarks.ctr;
    const benchmarkCPC = benchmarks.cpc;
    const benchmarkROAS = benchmarks.roas;
    const benchmarkConversionRate = benchmarks.conversion_rate;

    // Calculate base confidence for all insights
    const baseConfidence = ConfidenceCalculator.forCampaignInsight(
      totalImpressions,
      totalClicks,
      totalConversions,
      'database' // TODO: Track if benchmarks came from DB or fallback
    );

    // 1. ROAS Analysis with Context
    if (overallROAS > benchmarkROAS * 1.5) {
      const confidence = ConfidenceCalculator.adjustForDeviation(
        baseConfidence,
        overallROAS,
        benchmarkROAS
      );

      insights.push({
        type: 'success',
        title: 'Exceptional Return on Ad Spend',
        message: `Your campaigns are generating ${overallROAS.toFixed(2)}x ROAS—${((overallROAS / benchmarkROAS - 1) * 100).toFixed(0)}% above industry average. This means every ₹1 spent returns ₹${overallROAS.toFixed(2)}, significantly outperforming competitors at ${benchmarkROAS}x.`,
        impact: `+₹${(totalConversionValue - totalSpend).toFixed(0)} profit above average`,
        confidence,
        actionable: true,
        actions: [
          'Scale budget by 20-30% on top-performing campaigns',
          'Expand to similar audience segments',
          'Test higher-funnel awareness campaigns with this proven formula'
        ],
        impactScore: 85,
        whyItMatters: 'High ROAS indicates your targeting, messaging, and product-market fit are all aligned. This is the foundation for sustainable growth—you can confidently increase spend knowing it will generate profitable returns.',
        category: 'Performance'
      });
    } else if (overallROAS < benchmarkROAS * 0.7) {
      const roasGap = benchmarkROAS - overallROAS;
      const potentialGain = totalSpend * roasGap;
      const confidence = ConfidenceCalculator.adjustForDeviation(
        baseConfidence,
        overallROAS,
        benchmarkROAS
      );

      insights.push({
        type: 'danger',
        title: 'ROAS Below Industry Standard',
        message: `Current ${overallROAS.toFixed(2)}x ROAS is ${((1 - overallROAS / benchmarkROAS) * 100).toFixed(0)}% below the ${benchmarkROAS}x industry benchmark. Analysis shows this is likely driven by high CPCs (₹${avgCPC.toFixed(2)}) or low conversion rates (${conversionRate.toFixed(2)}%).`,
        impact: `+₹${potentialGain.toFixed(0)}/month potential revenue`,
        confidence,
        actionable: true,
        actions: [
          'Pause campaigns with ROAS < 1.0x immediately',
          'Review landing page experience—conversion rate is the bottleneck',
          'Test lower-cost keywords with similar intent',
          'Consider audience exclusions to reduce wasted spend'
        ],
        impactScore: 78,
        whyItMatters: 'Low ROAS means you\'re spending more to acquire customers than they\'re worth. This is unsustainable—every day of inaction compounds losses. Immediate optimization is critical to profitability.',
        category: 'Performance'
      });
    }

    // 2. CTR Analysis with Diagnosis
    if (avgCTR > benchmarkCTR * 1.2) {
      const confidence = ConfidenceCalculator.adjustForDeviation(
        baseConfidence,
        avgCTR,
        benchmarkCTR
      );

      insights.push({
        type: 'success',
        title: 'High-Engagement Ads Detected',
        message: `${avgCTR.toFixed(2)}% CTR is ${((avgCTR / benchmarkCTR - 1) * 100).toFixed(0)}% above average. Your ad copy and targeting are resonating—users are clicking at ${totalClicks.toLocaleString()} total clicks.`,
        impact: 'Strong ad relevance = lower CPCs and higher Quality Scores',
        confidence,
        actionable: true,
        actions: [
          'Clone winning ad copy to underperforming campaigns',
          'A/B test even bolder CTAs to push CTR higher',
          'Expand keyword match types while monitoring quality'
        ]
      });
    } else if (avgCTR < benchmarkCTR * 0.8) {
      const confidence = ConfidenceCalculator.adjustForDeviation(
        baseConfidence,
        avgCTR,
        benchmarkCTR
      );

      insights.push({
        type: 'warning',
        title: 'Ad Relevance Needs Improvement',
        message: `${avgCTR.toFixed(2)}% CTR falls ${((1 - avgCTR / benchmarkCTR) * 100).toFixed(0)}% below the ${benchmarkCTR}% industry standard. This suggests a mismatch between ad creative and audience intent, resulting in ${totalImpressions.toLocaleString()} impressions but only ${totalClicks.toLocaleString()} clicks.`,
        impact: '-15-25% campaign efficiency',
        confidence,
        actionable: true,
        actions: [
          'Rewrite ad headlines to match exact search query language',
          'Add emotional triggers (urgency, social proof, benefits)',
          'Test responsive search ads with 8+ headline variations',
          'Review negative keywords—are you showing for irrelevant searches?'
        ],
        impactScore: 65,
        whyItMatters: 'Low CTR signals to Google that your ads aren\'t relevant, which increases your costs per click and reduces ad visibility. Improving CTR creates a virtuous cycle of lower costs and better placement.',
        category: 'Performance'
      });
    }

    // 3. Conversion Rate Intelligence
    if (conversionRate > benchmarkConversionRate * 1.3) {
      const confidence = ConfidenceCalculator.adjustForDeviation(
        baseConfidence,
        conversionRate,
        benchmarkConversionRate
      );

      insights.push({
        type: 'success',
        title: 'Landing Page Converting Exceptionally',
        message: `${conversionRate.toFixed(2)}% conversion rate crushes the ${benchmarkConversionRate}% benchmark. Your landing page, offer, and traffic quality are aligned—turning ${totalConversions} visitors into customers.`,
        impact: 'High conversion efficiency means more profit per click',
        confidence,
        actionable: true,
        actions: [
          'Increase bids to capture more traffic at this conversion rate',
          'Replicate landing page structure for other campaigns',
          'Test upsell offers to increase average order value'
        ]
      });
    } else if (conversionRate < benchmarkConversionRate * 0.6) {
      const conversionGap = benchmarkConversionRate - conversionRate;
      const missedConversions = Math.floor(totalClicks * (conversionGap / 100));
      const confidence = ConfidenceCalculator.adjustForDeviation(
        baseConfidence,
        conversionRate,
        benchmarkConversionRate
      );

      insights.push({
        type: 'danger',
        title: 'Conversion Funnel Leaking Revenue',
        message: `Only ${conversionRate.toFixed(2)}% of clicks convert vs. ${benchmarkConversionRate}% industry average. This means you're losing ~${missedConversions} potential customers monthly. Root cause: likely landing page friction, unclear value prop, or targeting mismatch.`,
        impact: `+${missedConversions} conversions/month = ~₹${(missedConversions * (totalConversionValue / Math.max(totalConversions, 1))).toFixed(0)} potential revenue`,
        confidence,
        actionable: true,
        actions: [
          'Urgent: Review landing page load speed (target <2s)',
          'Simplify form fields—each field costs ~10% conversions',
          'Add trust signals: reviews, guarantees, security badges',
          'Test different offers (discount vs. free shipping vs. limited time)',
          'Check mobile experience—50%+ traffic is mobile'
        ],
        impactScore: 82,
        whyItMatters: 'Every visitor you lose is wasted ad spend. Since you\'re already paying to get clicks, fixing your conversion rate is the highest-leverage optimization—it doesn\'t cost more traffic, just better conversion.',
        category: 'Conversion'
      });
    }

    // 4. Budget Efficiency Analysis
    const topCampaigns = campaigns
      .filter(c => (c.metrics?.cost || c.spend || 0) > 0)
      .sort((a, b) => {
        const roasA = (a.metrics?.conversion_value || 0) / (a.metrics?.cost || a.spend || 1);
        const roasB = (b.metrics?.conversion_value || 0) / (b.metrics?.cost || b.spend || 1);
        return roasB - roasA;
      })
      .slice(0, 3);

    const bottomCampaigns = campaigns
      .filter(c => (c.metrics?.cost || c.spend || 0) > 0)
      .sort((a, b) => {
        const roasA = (a.metrics?.conversion_value || 0) / (a.metrics?.cost || a.spend || 1);
        const roasB = (b.metrics?.conversion_value || 0) / (b.metrics?.cost || b.spend || 1);
        return roasA - roasB;
      })
      .slice(0, 3);

    if (topCampaigns.length > 0 && bottomCampaigns.length > 0) {
      const topSpend = topCampaigns.reduce((sum, c) => sum + (c.metrics?.cost || c.spend || 0), 0);
      const bottomSpend = bottomCampaigns.reduce((sum, c) => sum + (c.metrics?.cost || c.spend || 0), 0);
      const reallocationOpportunity = bottomSpend * 0.5;

      insights.push({
        type: 'warning',
        title: 'Budget Allocation Inefficiency Detected',
        message: `Your top 3 campaigns account for ${((topSpend / totalSpend) * 100).toFixed(0)}% of spend but drive disproportionate results. Meanwhile, bottom 3 campaigns are burning ₹${bottomSpend.toFixed(0)} with minimal return.`,
        impact: `Reallocating ₹${reallocationOpportunity.toFixed(0)} from low to high performers could boost overall ROAS by 20-35%`,
        confidence: baseConfidence,
        actionable: true,
        actions: [
          `Reduce budget on "${bottomCampaigns[0]?.campaign_name || bottomCampaigns[0]?.name}" by 50%`,
          `Increase budget on "${topCampaigns[0]?.campaign_name || topCampaigns[0]?.name}" by 30%`,
          'Set ROAS targets: pause any campaign below 1.5x for 7 days',
          'Test campaign restructuring—combine low-spend campaigns'
        ]
      });
    }

    // 5. Spend Velocity Insight
    const dailySpend = totalSpend / 30; // Assume 30-day period
    if (dailySpend > 1000 && overallROAS < 1.5) {
      insights.push({
        type: 'danger',
        title: 'High Burn Rate with Suboptimal Returns',
        message: `Burning ₹${dailySpend.toFixed(0)}/day (₹${totalSpend.toFixed(0)}/month) at ${overallROAS.toFixed(2)}x ROAS means you're barely breaking even. At this spend level, you should be at 2.5-3x ROAS minimum.`,
        impact: 'Current trajectory = negative ROI. Immediate action required.',
        confidence: Math.min(baseConfidence + 10, 100), // High confidence for dangerous situations
        actionable: true,
        actions: [
          'Emergency: Reduce daily budget by 40% until ROAS improves',
          'Pause all campaigns with ROAS < 1.0x',
          'Focus spend on proven converters only',
          'Consider switching to CPA bidding to control costs'
        ]
      });
    }

    return insights.sort((a, b) => {
      const severityOrder = { danger: 0, warning: 1, success: 2, info: 3 };
      return severityOrder[a.type] - severityOrder[b.type];
    });
  }

  /**
   * Generate time-based insights (trends, seasonality)
   */
  static analyzeTemporalPatterns(historicalData: any[]): InsightResult[] {
    // Placeholder for time-series analysis
    return [];
  }

  /**
   * Detect anomalies with root cause analysis
   */
  static detectAnomaliesWithContext(metrics: any, historical: any): InsightResult[] {
    // Placeholder for anomaly detection
    return [];
  }

  /**
   * Analyze GA4 website analytics performance
   */
  static analyzeGA4Performance(metrics: any): InsightResult[] {
    const insights: InsightResult[] = [];

    if (!metrics) {
      return [{
        type: 'info',
        title: 'No Analytics Data',
        message: 'Connect your Google Analytics 4 property to start receiving website performance insights.',
        impact: 'Setup required',
        confidence: 100,
        actionable: false,
      }];
    }

    const {
      sessions = 0,
      conversion_rate = 0,
      conversions = 0,
      bounce_rate = 0,
      avg_session_duration = 0,
      pages_per_session = 0,
    } = metrics;

    // Industry benchmarks for GA4 - dynamically fetched from database
    const benchmarks = insightBenchmarks.getBenchmarksSync('ga4', 'general');
    const benchmarkConversionRate = benchmarks.conversion_rate;
    const benchmarkBounceRate = benchmarks.bounce_rate || 45;
    const benchmarkSessionDuration = benchmarks.avg_session_duration || 120; // 2 minutes
    const benchmarkPagesPerSession = benchmarks.pages_per_session || 2.5;

    // Calculate base confidence for GA4 insights
    const baseConfidence = ConfidenceCalculator.forGA4Insight(
      sessions,
      conversions,
      'database'
    );

    // 1. Conversion Rate Analysis
    if (conversion_rate > benchmarkConversionRate * 1.5) {
      const confidence = ConfidenceCalculator.adjustForDeviation(
        baseConfidence,
        conversion_rate,
        benchmarkConversionRate
      );

      insights.push({
        type: 'success',
        title: 'Exceptional Website Conversion Rate',
        message: `Your ${conversion_rate.toFixed(2)}% conversion rate is ${((conversion_rate / benchmarkConversionRate - 1) * 100).toFixed(0)}% above the ${benchmarkConversionRate}% industry benchmark. From ${sessions.toLocaleString()} sessions, you're converting ${conversions.toLocaleString()} users—significantly outperforming typical websites.`,
        impact: `Superior conversion efficiency = ${conversions} conversions from quality traffic`,
        confidence,
        actionable: true,
        actions: [
          'Document your winning conversion formula (UX, copy, CTAs)',
          'Expand traffic to high-converting pages',
          'Test premium upsell offers to increase order value',
          'Replicate successful elements across other landing pages'
        ]
      });
    } else if (conversion_rate < benchmarkConversionRate * 0.6) {
      const conversionGap = benchmarkConversionRate - conversion_rate;
      const missedConversions = Math.floor(sessions * (conversionGap / 100));
      const confidence = ConfidenceCalculator.adjustForDeviation(
        baseConfidence,
        conversion_rate,
        benchmarkConversionRate
      );

      insights.push({
        type: 'danger',
        title: 'Website Conversion Rate Below Par',
        message: `Only ${conversion_rate.toFixed(2)}% of your ${sessions.toLocaleString()} sessions convert vs. ${benchmarkConversionRate}% industry standard. This means you're losing ~${missedConversions.toLocaleString()} potential conversions. Root cause analysis: likely poor user experience, slow load times, unclear value proposition, or traffic quality issues.`,
        impact: `Fixing conversion rate could add ${missedConversions.toLocaleString()} monthly conversions`,
        confidence,
        actionable: true,
        actions: [
          'Run speed test: target <2s load time (use PageSpeed Insights)',
          'Simplify navigation—users should find what they need in 2 clicks',
          'Clarify value proposition above the fold',
          'Add trust signals: testimonials, security badges, guarantees',
          'Test your checkout/contact flow on mobile (60%+ of traffic)',
          'Review traffic sources—are you attracting the right audience?'
        ]
      });
    }

    // 2. Bounce Rate Analysis
    if (bounce_rate < benchmarkBounceRate * 0.7) {
      insights.push({
        type: 'success',
        title: 'Low Bounce Rate Indicates Strong Engagement',
        message: `${bounce_rate.toFixed(1)}% bounce rate is ${((1 - bounce_rate / benchmarkBounceRate) * 100).toFixed(0)}% better than the ${benchmarkBounceRate}% benchmark. Visitors are staying and exploring your content, which strongly correlates with higher conversion rates.`,
        impact: 'High engagement = better SEO rankings and more conversions',
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Analyze which pages have lowest bounce—replicate their patterns',
          'Create internal linking strategy to guide users deeper',
          'Add related content recommendations'
        ]
      });
    } else if (bounce_rate > benchmarkBounceRate * 1.3) {
      insights.push({
        type: 'warning',
        title: 'High Bounce Rate Losing Visitors',
        message: `${bounce_rate.toFixed(1)}% bounce rate means ${Math.floor(sessions * (bounce_rate / 100)).toLocaleString()} visitors left immediately without engaging. This is ${((bounce_rate / benchmarkBounceRate - 1) * 100).toFixed(0)}% higher than the ${benchmarkBounceRate}% industry standard. High bounce rates hurt SEO and indicate content/experience mismatch.`,
        impact: 'Each 10% bounce reduction = 5-10% more conversions',
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Check page load speed (mobile + desktop)',
          'Ensure headline matches ad/search intent',
          'Add compelling CTAs above the fold',
          'Remove intrusive popups that trigger immediate exits',
          'Improve mobile responsiveness—test on actual devices'
        ]
      });
    }

    // 3. Session Duration & Engagement
    if (avg_session_duration < benchmarkSessionDuration * 0.6) {
      const minutes = Math.floor(avg_session_duration / 60);
      const seconds = Math.floor(avg_session_duration % 60);
      insights.push({
        type: 'warning',
        title: 'Low Session Duration Shows Weak Engagement',
        message: `Average session of ${minutes}m ${seconds}s is ${((1 - avg_session_duration / benchmarkSessionDuration) * 100).toFixed(0)}% below the ${Math.floor(benchmarkSessionDuration / 60)}m standard. Combined with ${pages_per_session.toFixed(1)} pages/session (vs ${benchmarkPagesPerSession} benchmark), this suggests visitors aren't finding what they need quickly enough.`,
        impact: 'Low engagement = lower trust = fewer conversions',
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Add engaging content: videos, interactive tools, calculators',
          'Improve internal search functionality',
          'Create content hubs that keep users exploring',
          'Add "related articles" or "you might also like" sections',
          'Review exit pages—where are users leaving?'
        ]
      });
    } else if (avg_session_duration > benchmarkSessionDuration * 1.5 && pages_per_session > benchmarkPagesPerSession * 1.2) {
      insights.push({
        type: 'success',
        title: 'Exceptional User Engagement',
        message: `Users spend ${Math.floor(avg_session_duration / 60)}m ${Math.floor(avg_session_duration % 60)}s and view ${pages_per_session.toFixed(1)} pages per session—both significantly above benchmarks. This high engagement indicates quality content and good UX.`,
        impact: 'Deep engagement = higher conversion intent and brand trust',
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Identify most-engaged user segments for targeting',
          'Create retargeting campaigns for engaged visitors',
          'Add exit-intent offers to convert engaged browsers'
        ]
      });
    }

    // 4. Traffic Volume Assessment
    if (sessions < 1000) {
      insights.push({
        type: 'info',
        title: 'Low Traffic Volume Limits Insights',
        message: `With only ${sessions.toLocaleString()} sessions, statistical significance is limited. Small traffic volumes make it hard to identify reliable patterns and A/B test effectively.`,
        impact: 'Need 5,000+ monthly sessions for reliable optimization',
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Invest in SEO: optimize for long-tail keywords',
          'Create content marketing strategy (blog, guides, tools)',
          'Build backlinks through guest posting and PR',
          'Run targeted paid campaigns to supplement organic growth',
          'Leverage social media and email to drive repeat visits'
        ]
      });
    } else if (sessions > 10000 && conversion_rate > benchmarkConversionRate) {
      insights.push({
        type: 'success',
        title: 'Scalable High-Performance Website',
        message: `${sessions.toLocaleString()} monthly sessions converting at ${conversion_rate.toFixed(2)}% = strong foundation for growth. You have the traffic volume and conversion efficiency to scale profitably.`,
        impact: `Ready to scale: each 1,000 additional sessions = ~${Math.floor(1000 * (conversion_rate / 100))} conversions`,
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Invest aggressively in paid acquisition (proven ROI)',
          'Scale top-performing content and traffic sources',
          'Implement advanced personalization and segmentation',
          'Test premium features or upsells'
        ]
      });
    }

    return insights.sort((a, b) => {
      const severityOrder = { danger: 0, warning: 1, success: 2, info: 3 };
      return severityOrder[a.type] - severityOrder[b.type];
    });
  }

  /**
   * Analyze unified cross-platform performance
   */
  static analyzeUnifiedPerformance(
    metrics: any,
    platformComparison: any[]
  ): InsightResult[] {
    const insights: InsightResult[] = [];

    if (!metrics || !platformComparison || platformComparison.length === 0) {
      return [{
        type: 'info',
        title: 'Connect Multiple Platforms',
        message: 'Connect your marketing platforms to unlock cross-channel insights and budget allocation recommendations.',
        impact: 'Setup required',
        confidence: 100,
        actionable: false,
        category: 'General'
      }];
    }

    const {
      total_spend = 0,
      blended_roas = 0,
      total_conversions = 0,
      best_platform = null,
    } = metrics;

    // Industry benchmarks for cross-platform - dynamically fetched from database
    const benchmarks = insightBenchmarks.getBenchmarksSync('unified', 'general');
    const benchmarkBlendedROAS = benchmarks.blended_roas || 2.5;
    const optimalPlatformDiversity = 0.4; // 40% budget concentration is healthy

    // Calculate base confidence for unified insights
    const baseConfidence = ConfidenceCalculator.forUnifiedInsight(
      total_spend,
      total_conversions,
      platformComparison.length,
      'database'
    );

    // Calculate platform diversity (budget concentration)
    const platformBudgets = platformComparison.map(p => p.spend || 0);
    const totalBudget = platformBudgets.reduce((sum, b) => sum + b, 0);
    const budgetShares = platformBudgets.map(b => b / totalBudget);
    const budgetConcentration = Math.max(...budgetShares);

    // 1. Blended ROAS Analysis
    if (blended_roas > benchmarkBlendedROAS * 1.3) {
      insights.push({
        type: 'success',
        title: 'Outstanding Cross-Platform ROAS',
        message: `Your ${blended_roas.toFixed(2)}x blended ROAS across ${platformComparison.length} platforms is ${((blended_roas / benchmarkBlendedROAS - 1) * 100).toFixed(0)}% above the ${benchmarkBlendedROAS}x industry benchmark. Total spend of ₹${total_spend.toLocaleString()} is generating ${total_conversions} conversions—your multi-channel strategy is working exceptionally well.`,
        impact: `+₹${((blended_roas - benchmarkBlendedROAS) * total_spend).toFixed(0)} profit above average`,
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Scale budget proportionally across all performing platforms',
          'Document your cross-platform attribution model',
          'Test expanding to additional channels (TikTok, LinkedIn)',
          'Implement cross-platform retargeting sequences'
        ],
        impactScore: 88,
        whyItMatters: 'High blended ROAS proves your marketing mix is optimized. Each platform complements the others in the customer journey, from awareness to conversion.',
        category: 'Performance'
      });
    } else if (blended_roas < benchmarkBlendedROAS * 0.7) {
      const roasGap = benchmarkBlendedROAS - blended_roas;
      const potentialGain = total_spend * roasGap;

      insights.push({
        type: 'danger',
        title: 'Cross-Platform Efficiency Below Benchmark',
        message: `Blended ${blended_roas.toFixed(2)}x ROAS is ${((1 - blended_roas / benchmarkBlendedROAS) * 100).toFixed(0)}% below the ${benchmarkBlendedROAS}x industry standard. Across ₹${total_spend.toLocaleString()} spend on ${platformComparison.length} platforms, you're underperforming—likely due to poor channel mix, weak attribution, or platform-specific inefficiencies.`,
        impact: `+₹${potentialGain.toFixed(0)} potential monthly revenue`,
        confidence: baseConfidence,
        actionable: true,
        actions: [
          `Audit ${best_platform?.name || 'top platform'} first—replicate winning tactics`,
          'Review attribution model (last-click vs. data-driven)',
          'Pause platforms with ROAS < 1.0x immediately',
          'Implement unified conversion tracking across platforms',
          'Test reallocating budget to highest-performing channel'
        ],
        impactScore: 75,
        whyItMatters: 'Low blended ROAS means your marketing dollars are inefficiently distributed. Every day of inaction means wasted budget that could be driving profitable growth.',
        category: 'Performance'
      });
    }

    // 2. Platform Diversity Analysis
    if (budgetConcentration > 0.75) {
      const dominantPlatform = platformComparison[budgetShares.indexOf(budgetConcentration)];
      insights.push({
        type: 'warning',
        title: 'Over-Reliance on Single Platform',
        message: `${(budgetConcentration * 100).toFixed(0)}% of your budget (₹${dominantPlatform.spend.toLocaleString()}) is concentrated on ${dominantPlatform.platform}. While consolidation can be efficient, it creates significant risk—algorithm changes, policy updates, or platform issues could devastate your acquisition.`,
        impact: '-30-50% revenue risk if platform disrupted',
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Diversify: allocate 20-30% budget to secondary platforms',
          'Build owned audiences (email, SMS) to reduce platform dependency',
          'Test emerging channels as insurance',
          'Implement multi-touch attribution to value all touchpoints'
        ],
        impactScore: 70,
        whyItMatters: 'Platform diversification is business insurance. The best marketers spread risk while maintaining efficiency—aim for 40-60% on your top channel, not 75%+.',
        category: 'Spend'
      });
    } else if (budgetConcentration < 0.35 && platformComparison.length > 3) {
      insights.push({
        type: 'warning',
        title: 'Budget Spread Too Thin',
        message: `Your budget is fragmented across ${platformComparison.length} platforms with only ${(budgetConcentration * 100).toFixed(0)}% on the top performer. Spreading too thin prevents platforms from reaching critical mass for algorithm optimization and makes it hard to achieve statistical significance in testing.`,
        impact: 'Sub-optimal learning and scaling',
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Consolidate: move budget from lowest ROAS platforms to top 2-3',
          'Set minimum viable budgets (₹10,000/month per platform)',
          'Pause experimental channels until you scale core platforms',
          'Focus on depth over breadth in testing'
        ],
        impactScore: 68,
        whyItMatters: 'Platform algorithms need sufficient budget to learn and optimize. Too many small budgets means none of your campaigns reach their full potential.',
        category: 'Spend'
      });
    }

    // 3. Platform-Specific Performance Gaps
    const platformsWithData = platformComparison.filter(p => p.spend > 0 && p.conversions > 0);
    if (platformsWithData.length >= 2) {
      const roasValues = platformsWithData.map(p => p.roas || 0);
      const maxROAS = Math.max(...roasValues);
      const minROAS = Math.min(...roasValues);
      const roasVariance = maxROAS - minROAS;

      if (roasVariance > 2.0) {
        const bestPlatform = platformsWithData.find(p => p.roas === maxROAS);
        const worstPlatform = platformsWithData.find(p => p.roas === minROAS);

        insights.push({
          type: 'warning',
          title: 'Significant Platform Performance Gap',
          message: `${bestPlatform?.platform} (${maxROAS.toFixed(2)}x ROAS) is outperforming ${worstPlatform?.platform} (${minROAS.toFixed(2)}x ROAS) by ${roasVariance.toFixed(2)}x. This ${((roasVariance / maxROAS) * 100).toFixed(0)}% gap suggests either different audience quality, creative effectiveness, or fundamentally misaligned platform-product fit.`,
          impact: `Reallocating ₹${(worstPlatform?.spend || 0).toFixed(0)} to ${bestPlatform?.platform} could add ${((worstPlatform?.spend || 0) * (maxROAS - minROAS)).toFixed(0)} revenue`,
          confidence: baseConfidence,
          actionable: true,
          actions: [
            `Analyze ${bestPlatform?.platform} winning tactics: creative, targeting, offers`,
            `Test ${bestPlatform?.platform} strategy on ${worstPlatform?.platform}`,
            'Review audience overlap between platforms',
            `Consider pausing ${worstPlatform?.platform} if ROAS < 1.0x`,
            'Implement platform-specific optimization sprints'
          ],
          impactScore: 72,
          whyItMatters: `Not all platforms work equally for every business. ${bestPlatform?.platform} is proving product-market-channel fit. Double down on what works or fix what doesn't.`,
          category: 'Performance'
        });
      }
    }

    // 4. Conversion Volume vs. Efficiency Trade-off
    if (best_platform && total_conversions > 50) {
      const bestROASPlatform = platformComparison.reduce((best, p) =>
        (p.roas || 0) > (best.roas || 0) ? p : best
      );
      const bestConversionsPlatform = platformComparison.reduce((best, p) =>
        (p.conversions || 0) > (best.conversions || 0) ? p : best
      );

      if (bestROASPlatform.platform !== bestConversionsPlatform.platform) {
        insights.push({
          type: 'info',
          title: 'Platform Strategy: Volume vs. Efficiency',
          message: `${bestROASPlatform.platform} delivers highest efficiency (${bestROASPlatform.roas.toFixed(2)}x ROAS) while ${bestConversionsPlatform.platform} drives highest volume (${bestConversionsPlatform.conversions} conversions). This is actually healthy—${bestConversionsPlatform.platform} builds top-of-funnel awareness while ${bestROASPlatform.platform} converts high-intent users.`,
          impact: 'Balanced funnel strategy',
          confidence: baseConfidence,
          actionable: true,
          actions: [
            `Use ${bestConversionsPlatform.platform} for awareness and remarketing pool building`,
            `Use ${bestROASPlatform.platform} for direct response and bottom-funnel`,
            'Implement cross-platform attribution to value assists',
            'Test sequential messaging: awareness → consideration → conversion'
          ],
          impactScore: 65,
          whyItMatters: 'Full-funnel marketing requires different platforms for different jobs. Volume platforms feed efficiency platforms through retargeting and brand building.',
          category: 'General'
        });
      }
    }

    return insights.sort((a, b) => {
      const severityOrder = { danger: 0, warning: 1, success: 2, info: 3 };
      return severityOrder[a.type] - severityOrder[b.type];
    });
  }

  /**
   * Analyze e-commerce performance metrics
   */
  static analyzeEcommercePerformance(
    metrics: any,
    revenueByChannel?: any[]
  ): InsightResult[] {
    const insights: InsightResult[] = [];

    if (!metrics) {
      return [{
        type: 'info',
        title: 'Connect E-commerce Data',
        message: 'Connect your e-commerce platform to unlock revenue, AOV, and product performance insights.',
        impact: 'Setup required',
        confidence: 100,
        actionable: false,
        category: 'General'
      }];
    }

    const {
      conversion_value = 0,
      conversions = 0,
      spend = 0,
      clicks = 0,
      roas = 0,
    } = metrics;

    const avgOrderValue = conversions > 0 ? conversion_value / conversions : 0;
    const conversionRate = clicks > 0 ? (conversions / clicks) * 100 : 0;

    // E-commerce benchmarks - dynamically fetched from database
    const benchmarks = insightBenchmarks.getBenchmarksSync('ecommerce', 'general');
    const benchmarkAOV = benchmarks.aov || 3500; // ₹3,500
    const benchmarkROAS = benchmarks.roas || 4.0; // E-commerce should have higher ROAS
    const benchmarkConversionRate = benchmarks.conversion_rate || 2.5; // E-commerce conversion rate
    const benchmarkRepeatRate = benchmarks.repeat_purchase_rate || 30; // 30% repeat purchase rate

    // Calculate base confidence for e-commerce insights
    const baseConfidence = ConfidenceCalculator.forEcommerceInsight(
      conversions,
      clicks,
      'database'
    );

    // 1. ROAS Analysis (E-commerce specific)
    if (roas > benchmarkROAS * 1.5) {
      insights.push({
        type: 'success',
        title: 'Exceptional E-commerce ROAS',
        message: `Your ${roas.toFixed(2)}x ROAS is ${((roas / benchmarkROAS - 1) * 100).toFixed(0)}% above the ${benchmarkROAS}x e-commerce benchmark. Total spend of ₹${spend.toLocaleString()} generated ₹${conversion_value.toLocaleString()} in revenue (${conversions} orders)—your product-market fit and ad targeting are excellent.`,
        impact: `+₹${((roas - benchmarkROAS) * spend).toFixed(0)} profit above average`,
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Scale winning product campaigns by 30-50%',
          'Expand to similar product categories',
          'Test dynamic product ads for cross-selling',
          'Increase bids on high-ROAS shopping campaigns'
        ],
        impactScore: 90,
        whyItMatters: 'High e-commerce ROAS means your products are resonating with your target audience. You can confidently scale ad spend knowing each rupee invested returns profitable revenue.',
        category: 'Performance'
      });
    } else if (roas < benchmarkROAS * 0.6) {
      const roasGap = benchmarkROAS - roas;
      const potentialGain = spend * roasGap;

      insights.push({
        type: 'danger',
        title: 'E-commerce ROAS Below Target',
        message: `Current ${roas.toFixed(2)}x ROAS is ${((1 - roas / benchmarkROAS) * 100).toFixed(0)}% below the ${benchmarkROAS}x e-commerce standard. With ₹${spend.toLocaleString()} ad spend generating only ₹${conversion_value.toLocaleString()} revenue, you're likely facing pricing issues, wrong product-market fit, or poor ad creative.`,
        impact: `+₹${potentialGain.toFixed(0)} potential monthly revenue`,
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Audit product pricing vs. competitors (may be too high)',
          'Review shopping feed quality (titles, images, descriptions)',
          'Pause low-performing SKUs and focus budget on winners',
          'Test free shipping thresholds to increase AOV',
          'Implement urgency tactics (limited stock, countdown timers)'
        ],
        impactScore: 80,
        whyItMatters: 'Low e-commerce ROAS means customers aren\'t buying at prices that justify your ad costs. Every sale may actually be losing money when factoring in COGS and fulfillment.',
        category: 'Performance'
      });
    }

    // 2. Average Order Value Analysis
    if (avgOrderValue > benchmarkAOV * 1.3) {
      insights.push({
        type: 'success',
        title: 'Premium Average Order Value',
        message: `₹${avgOrderValue.toFixed(2)} AOV is ${((avgOrderValue / benchmarkAOV - 1) * 100).toFixed(0)}% above the ₹${benchmarkAOV.toLocaleString()} benchmark. From ${conversions} orders, you're maximizing revenue per transaction—your product bundling, upsells, or premium positioning is working excellently.`,
        impact: `+₹${((avgOrderValue - benchmarkAOV) * conversions).toFixed(0)} extra revenue`,
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Document your upsell/cross-sell strategy for replication',
          'Test "Frequently Bought Together" product bundles',
          'Introduce tiered pricing (Good/Better/Best)',
          'Add premium product lines to capture high-value customers'
        ],
        impactScore: 75,
        whyItMatters: 'High AOV means you\'re extracting maximum value per customer. This allows you to bid higher in auctions and still maintain profitability.',
        category: 'Conversion'
      });
    } else if (avgOrderValue < benchmarkAOV * 0.7) {
      const aovGap = benchmarkAOV - avgOrderValue;
      const potentialRevenue = aovGap * conversions;

      insights.push({
        type: 'warning',
        title: 'Low Average Order Value',
        message: `₹${avgOrderValue.toFixed(2)} AOV is ${((1 - avgOrderValue / benchmarkAOV) * 100).toFixed(0)}% below the ₹${benchmarkAOV.toLocaleString()} benchmark. With ${conversions} orders, you're leaving ₹${potentialRevenue.toFixed(0)} on the table. Customers are buying, but in smaller quantities or lower-priced items.`,
        impact: `+₹${potentialRevenue.toFixed(0)} potential revenue`,
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Implement free shipping threshold (₹500+) to encourage larger orders',
          'Add "Complete the Look" product recommendations',
          'Create product bundles at 10-15% discount',
          'Test quantity discounts (Buy 2 Get 10% Off)',
          'Introduce urgency: "Add ₹X more for free shipping"'
        ],
        impactScore: 72,
        whyItMatters: 'Increasing AOV is the fastest way to scale e-commerce profitably. A 20% AOV increase means 20% more revenue from the same traffic and ad spend.',
        category: 'Conversion'
      });
    }

    // 3. Conversion Rate Analysis
    if (conversionRate > benchmarkConversionRate * 1.4) {
      insights.push({
        type: 'success',
        title: 'Excellent E-commerce Conversion Rate',
        message: `${conversionRate.toFixed(2)}% conversion rate (${conversions} orders from ${clicks.toLocaleString()} clicks) is ${((conversionRate / benchmarkConversionRate - 1) * 100).toFixed(0)}% above the ${benchmarkConversionRate}% benchmark. Your product pages, pricing, and checkout flow are optimized—traffic quality is high.`,
        impact: 'High conversion efficiency',
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Increase traffic volume to capitalize on high conversion rate',
          'Test expanding to broader keywords while maintaining quality',
          'Replicate winning product page structure across catalog',
          'Implement post-purchase upsells to increase LTV'
        ],
        impactScore: 68,
        whyItMatters: 'High conversion rates mean your store experience is compelling. You can afford to bid more aggressively for traffic since visitors convert at above-average rates.',
        category: 'Conversion'
      });
    } else if (conversionRate < benchmarkConversionRate * 0.6) {
      const convGap = benchmarkConversionRate - conversionRate;
      const missedOrders = Math.floor(clicks * (convGap / 100));

      insights.push({
        type: 'danger',
        title: 'E-commerce Conversion Funnel Broken',
        message: `Only ${conversionRate.toFixed(2)}% of your ${clicks.toLocaleString()} clicks convert vs. ${benchmarkConversionRate}% industry average. You're losing ~${missedOrders} potential orders monthly. Root causes: likely pricing concerns, shipping costs, checkout friction, or poor product presentation.`,
        impact: `+${missedOrders} orders/month = ₹${(missedOrders * avgOrderValue).toFixed(0)} revenue`,
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Critical: Review mobile checkout (60% of traffic is mobile)',
          'Display shipping costs upfront (hidden costs kill conversions)',
          'Add trust signals: reviews, ratings, security badges',
          'Simplify checkout to 1-page (every extra step loses 10% of users)',
          'A/B test product images (lifestyle vs. white background)',
          'Offer guest checkout (don\'t force account creation)'
        ],
        impactScore: 85,
        whyItMatters: 'Visitors are interested enough to click but not buying. Fixing conversion rate has 3x more impact than increasing traffic—you\'re already paying for the clicks.',
        category: 'Conversion'
      });
    }

    // 4. Revenue Channel Diversification
    if (revenueByChannel && revenueByChannel.length > 0) {
      const totalRevenue = revenueByChannel.reduce((sum, ch) => sum + (ch.revenue || 0), 0);
      const topChannelRevenue = Math.max(...revenueByChannel.map(ch => ch.revenue || 0));
      const topChannel = revenueByChannel.find(ch => ch.revenue === topChannelRevenue);
      const channelConcentration = topChannelRevenue / totalRevenue;

      if (channelConcentration > 0.7) {
        insights.push({
          type: 'warning',
          title: 'Over-Reliance on Single Revenue Channel',
          message: `${(channelConcentration * 100).toFixed(0)}% of revenue (₹${topChannelRevenue.toLocaleString()}) comes from ${topChannel?.channel}. While channel focus can be efficient, this creates major business risk—algorithm changes or policy updates could devastate sales.`,
          impact: '-40-60% revenue risk',
          confidence: baseConfidence,
          actionable: true,
          actions: [
            'Diversify: allocate 15-20% budget to secondary channels',
            'Build email list aggressively (owned audience)',
            'Test influencer marketing or affiliate partnerships',
            'Invest in SEO for long-term organic traffic',
            'Launch referral program to reduce paid acquisition dependency'
          ],
          impactScore: 70,
          whyItMatters: 'E-commerce businesses that rely on 1-2 channels are vulnerable. Platform policy changes can happen overnight—diversification is insurance against disaster.',
          category: 'Spend'
        });
      }
    }

    // 5. Product Performance Insight
    if (conversions >= 50 && avgOrderValue > 0) {
      const estimatedProducts = Math.ceil(conversions / 100); // Rough estimate
      insights.push({
        type: 'info',
        title: 'Product Portfolio Strategy',
        message: `With ${conversions} orders and ₹${avgOrderValue.toFixed(0)} AOV, you're likely selling multiple product types. Top performers typically drive 80% of revenue. Identify your hero products and double down—cut underperformers to free up budget for winners.`,
        impact: 'Portfolio optimization opportunity',
        confidence: baseConfidence,
        actionable: true,
        actions: [
          'Run 80/20 analysis: which 20% of SKUs drive 80% of revenue?',
          'Pause bottom 20% of products (low margin, low volume)',
          'Create dedicated campaigns for top 5 bestsellers',
          'Use dynamic remarketing to show users products they viewed',
          'Test product bundles combining hero items with complementary products'
        ],
        impactScore: 65,
        whyItMatters: 'Not all products are created equal. Focusing budget on proven winners while cutting losers dramatically improves overall profitability and simplifies operations.',
        category: 'General'
      });
    }

    return insights.sort((a, b) => {
      const severityOrder = { danger: 0, warning: 1, success: 2, info: 3 };
      return severityOrder[a.type] - severityOrder[b.type];
    });
  }
}
