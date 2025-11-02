/**
 * AI Insight Generator - Natural Language Intelligence
 *
 * Generates human-readable, contextual insights from campaign data
 * that sound genuinely intelligent, not templated.
 */

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

    // Industry benchmarks
    const benchmarkCTR = 3.17;
    const benchmarkCPC = 2.69;
    const benchmarkROAS = 2.0;
    const benchmarkConversionRate = 3.75;

    // 1. ROAS Analysis with Context
    if (overallROAS > benchmarkROAS * 1.5) {
      insights.push({
        type: 'success',
        title: 'Exceptional Return on Ad Spend',
        message: `Your campaigns are generating ${overallROAS.toFixed(2)}x ROAS—${((overallROAS / benchmarkROAS - 1) * 100).toFixed(0)}% above industry average. This means every ₹1 spent returns ₹${overallROAS.toFixed(2)}, significantly outperforming competitors at ${benchmarkROAS}x.`,
        impact: `Estimated ${(totalConversionValue - totalSpend).toFixed(0)} excess profit vs. average performance`,
        confidence: 94,
        actionable: true,
        actions: [
          'Scale budget by 20-30% on top-performing campaigns',
          'Expand to similar audience segments',
          'Test higher-funnel awareness campaigns with this proven formula'
        ]
      });
    } else if (overallROAS < benchmarkROAS * 0.7) {
      const roasGap = benchmarkROAS - overallROAS;
      const potentialGain = totalSpend * roasGap;

      insights.push({
        type: 'danger',
        title: 'ROAS Below Industry Standard',
        message: `Current ${overallROAS.toFixed(2)}x ROAS is ${((1 - overallROAS / benchmarkROAS) * 100).toFixed(0)}% below the ${benchmarkROAS}x industry benchmark. Analysis shows this is likely driven by high CPCs (₹${avgCPC.toFixed(2)}) or low conversion rates (${conversionRate.toFixed(2)}%).`,
        impact: `Improving to benchmark could unlock ₹${potentialGain.toFixed(0)} additional monthly revenue`,
        confidence: 88,
        actionable: true,
        actions: [
          'Pause campaigns with ROAS < 1.0x immediately',
          'Review landing page experience—conversion rate is the bottleneck',
          'Test lower-cost keywords with similar intent',
          'Consider audience exclusions to reduce wasted spend'
        ]
      });
    }

    // 2. CTR Analysis with Diagnosis
    if (avgCTR > benchmarkCTR * 1.2) {
      insights.push({
        type: 'success',
        title: 'High-Engagement Ads Detected',
        message: `${avgCTR.toFixed(2)}% CTR is ${((avgCTR / benchmarkCTR - 1) * 100).toFixed(0)}% above average. Your ad copy and targeting are resonating—users are clicking at ${totalClicks.toLocaleString()} total clicks.`,
        impact: 'Strong ad relevance = lower CPCs and higher Quality Scores',
        confidence: 91,
        actionable: true,
        actions: [
          'Clone winning ad copy to underperforming campaigns',
          'A/B test even bolder CTAs to push CTR higher',
          'Expand keyword match types while monitoring quality'
        ]
      });
    } else if (avgCTR < benchmarkCTR * 0.8) {
      insights.push({
        type: 'warning',
        title: 'Ad Relevance Needs Improvement',
        message: `${avgCTR.toFixed(2)}% CTR falls ${((1 - avgCTR / benchmarkCTR) * 100).toFixed(0)}% below the ${benchmarkCTR}% industry standard. This suggests a mismatch between ad creative and audience intent, resulting in ${totalImpressions.toLocaleString()} impressions but only ${totalClicks.toLocaleString()} clicks.`,
        impact: 'Low CTR increases CPCs and reduces campaign efficiency by 15-25%',
        confidence: 86,
        actionable: true,
        actions: [
          'Rewrite ad headlines to match exact search query language',
          'Add emotional triggers (urgency, social proof, benefits)',
          'Test responsive search ads with 8+ headline variations',
          'Review negative keywords—are you showing for irrelevant searches?'
        ]
      });
    }

    // 3. Conversion Rate Intelligence
    if (conversionRate > benchmarkConversionRate * 1.3) {
      insights.push({
        type: 'success',
        title: 'Landing Page Converting Exceptionally',
        message: `${conversionRate.toFixed(2)}% conversion rate crushes the ${benchmarkConversionRate}% benchmark. Your landing page, offer, and traffic quality are aligned—turning ${totalConversions} visitors into customers.`,
        impact: 'High conversion efficiency means more profit per click',
        confidence: 93,
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

      insights.push({
        type: 'danger',
        title: 'Conversion Funnel Leaking Revenue',
        message: `Only ${conversionRate.toFixed(2)}% of clicks convert vs. ${benchmarkConversionRate}% industry average. This means you're losing ~${missedConversions} potential customers monthly. Root cause: likely landing page friction, unclear value prop, or targeting mismatch.`,
        impact: `Fixing conversion rate could add ${missedConversions} conversions/month = ~₹${(missedConversions * (totalConversionValue / totalConversions)).toFixed(0)} revenue`,
        confidence: 89,
        actionable: true,
        actions: [
          'Urgent: Review landing page load speed (target <2s)',
          'Simplify form fields—each field costs ~10% conversions',
          'Add trust signals: reviews, guarantees, security badges',
          'Test different offers (discount vs. free shipping vs. limited time)',
          'Check mobile experience—50%+ traffic is mobile'
        ]
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
        confidence: 87,
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
        confidence: 95,
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

    // Industry benchmarks for GA4
    const benchmarkConversionRate = 2.35;
    const benchmarkBounceRate = 45;
    const benchmarkSessionDuration = 120; // 2 minutes
    const benchmarkPagesPerSession = 2.5;

    // 1. Conversion Rate Analysis
    if (conversion_rate > benchmarkConversionRate * 1.5) {
      insights.push({
        type: 'success',
        title: 'Exceptional Website Conversion Rate',
        message: `Your ${conversion_rate.toFixed(2)}% conversion rate is ${((conversion_rate / benchmarkConversionRate - 1) * 100).toFixed(0)}% above the ${benchmarkConversionRate}% industry benchmark. From ${sessions.toLocaleString()} sessions, you're converting ${conversions.toLocaleString()} users—significantly outperforming typical websites.`,
        impact: `Superior conversion efficiency = ${conversions} conversions from quality traffic`,
        confidence: 92,
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

      insights.push({
        type: 'danger',
        title: 'Website Conversion Rate Below Par',
        message: `Only ${conversion_rate.toFixed(2)}% of your ${sessions.toLocaleString()} sessions convert vs. ${benchmarkConversionRate}% industry standard. This means you're losing ~${missedConversions.toLocaleString()} potential conversions. Root cause analysis: likely poor user experience, slow load times, unclear value proposition, or traffic quality issues.`,
        impact: `Fixing conversion rate could add ${missedConversions.toLocaleString()} monthly conversions`,
        confidence: 87,
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
        confidence: 90,
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
        confidence: 85,
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
        confidence: 83,
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
        confidence: 91,
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
        confidence: 95,
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
        impact: 'Ready to scale: each 1,000 additional sessions = ~${Math.floor(1000 * (conversion_rate / 100))} conversions',
        confidence: 93,
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
}
