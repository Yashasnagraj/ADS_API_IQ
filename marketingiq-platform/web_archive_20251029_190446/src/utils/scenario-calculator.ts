/**
 * Scenario Calculator - Simulates outcomes for keyword optimization decisions
 * Provides best-case, worst-case, and no-action scenarios
 */

export interface KeywordMetrics {
  keyword_text: string;
  ad_clicks: number;
  ad_cost: number;
  ad_ctr: number;
  ad_conversions: number;
  ga4_bounce_rate: number;
  ga4_engagement_rate: number;
  ga4_avg_session_duration: number;
  quality_score: number;
}

export interface ScenarioOutcome {
  name: string;
  description: string;
  probability: number;
  metrics: {
    ctr: number;
    ctrChange: number;
    cpc: number;
    cpcChange: number;
    bounceRate: number;
    bounceRateChange: number;
    conversions: number;
    conversionsChange: number;
    monthlyROI: number;
    qualityScore: number;
  };
  risks: string[];
  opportunities: string[];
  timeline: string;
  actionSteps: string[];
}

export interface SimulationResult {
  keyword: string;
  currentMetrics: {
    ctr: number;
    cpc: number;
    bounceRate: number;
    conversions: number;
    qualityScore: number;
  };
  recommendation: {
    action: string;
    rationale: string;
  };
  scenarios: {
    success: ScenarioOutcome;
    failure: ScenarioOutcome;
    noAction: ScenarioOutcome;
  };
}

/**
 * Calculate monthly revenue impact
 */
const calculateMonthlyROI = (
  conversions: number,
  avgOrderValue: number = 2500,
  cost: number
): number => {
  const revenue = conversions * avgOrderValue;
  return revenue - cost;
};

/**
 * Generate simulation for a keyword based on current performance
 */
export const generateKeywordSimulation = (keyword: KeywordMetrics): SimulationResult => {
  const currentCTR = keyword.ad_ctr;
  const currentCPC = keyword.ad_cost / (keyword.ad_clicks || 1);
  const currentBounceRate = keyword.ga4_bounce_rate;
  const currentConversions = keyword.ad_conversions;
  const currentQualityScore = keyword.quality_score;

  // Determine recommendation based on quality score and performance
  let recommendationAction = '';
  let recommendationRationale = '';

  if (currentQualityScore < 50) {
    recommendationAction = 'Pause keyword and optimize landing page';
    recommendationRationale = 'Low quality score and high bounce rate indicate poor user experience';
  } else if (currentQualityScore >= 70) {
    recommendationAction = 'Increase bid by 20% to capture more traffic';
    recommendationRationale = 'High quality score and engagement suggest good ROI potential';
  } else {
    recommendationAction = 'Optimize ad copy and test landing page variants';
    recommendationRationale = 'Moderate performance with room for improvement';
  }

  // SUCCESS SCENARIO (if recommendation works)
  const successScenario: ScenarioOutcome = {
    name: 'Success Path',
    description: 'If you implement the recommendation and it works as expected',
    probability: currentQualityScore >= 70 ? 85 : currentQualityScore >= 50 ? 70 : 60,
    metrics: {
      ctr: currentCTR * (currentQualityScore >= 70 ? 1.28 : 1.15),
      ctrChange: currentQualityScore >= 70 ? 28 : 15,
      cpc: currentCPC * (currentQualityScore >= 70 ? 1.05 : currentQualityScore >= 50 ? 1.0 : 0.85),
      cpcChange: currentQualityScore >= 70 ? 5 : currentQualityScore >= 50 ? 0 : -15,
      bounceRate: currentBounceRate * 0.72,
      bounceRateChange: -28,
      conversions: currentConversions * (currentQualityScore >= 70 ? 1.45 : 1.25),
      conversionsChange: currentQualityScore >= 70 ? 45 : 25,
      monthlyROI: calculateMonthlyROI(
        currentConversions * (currentQualityScore >= 70 ? 1.45 : 1.25) * 30,
        2500,
        currentCPC * keyword.ad_clicks * 30 * (currentQualityScore >= 70 ? 1.05 : 1.0)
      ),
      qualityScore: Math.min(currentQualityScore + 15, 100),
    },
    risks: [
      'Initial cost increase during optimization phase',
      'May need 2-3 weeks to see full results',
      'Requires continuous monitoring and tweaking',
    ],
    opportunities: [
      'Improved Quality Score reduces future CPC',
      'Better user engagement leads to repeat customers',
      'Competitive advantage in ad auctions',
    ],
    timeline: currentQualityScore >= 70 ? '2-3 weeks' : '3-4 weeks',
    actionSteps: currentQualityScore >= 70
      ? [
          'Increase daily budget by 20%',
          'Monitor CTR and conversion rate daily',
          'Adjust bids based on performance after 1 week',
        ]
      : [
          'A/B test 3 landing page variants',
          'Optimize ad copy for better relevance',
          'Review and adjust negative keywords',
        ],
  };

  // FAILURE SCENARIO (if recommendation doesn't work)
  const failureScenario: ScenarioOutcome = {
    name: 'Failure Path',
    description: 'If you implement the recommendation but it doesn\'t deliver expected results',
    probability: currentQualityScore >= 70 ? 15 : currentQualityScore >= 50 ? 30 : 40,
    metrics: {
      ctr: currentCTR * 0.98,
      ctrChange: -2,
      cpc: currentCPC * (currentQualityScore >= 70 ? 1.15 : 1.33),
      cpcChange: currentQualityScore >= 70 ? 15 : 33,
      bounceRate: currentBounceRate * 1.08,
      bounceRateChange: 8,
      conversions: currentConversions * 0.92,
      conversionsChange: -8,
      monthlyROI: calculateMonthlyROI(
        currentConversions * 0.92 * 30,
        2500,
        currentCPC * keyword.ad_clicks * 30 * (currentQualityScore >= 70 ? 1.15 : 1.33)
      ),
      qualityScore: Math.max(currentQualityScore - 5, 0),
    },
    risks: [
      `Potential loss of ₹${Math.round(currentCPC * keyword.ad_clicks * 0.2 * 30).toLocaleString()}/month`,
      'Quality Score may decline further',
      'Competitors may gain market share',
    ],
    opportunities: [
      'Early detection allows quick pivot to alternative strategy',
      'Learnings can be applied to similar keywords',
      'Fallback options available within 1 week',
    ],
    timeline: '1 week to detect issues',
    actionSteps: [
      'Set up automated alerts for performance drops',
      'Prepare rollback plan before implementation',
      'Monitor hourly during first 48 hours',
      'Pause campaign if CPC increases >20% with no conversion improvement',
    ],
  };

  // NO ACTION SCENARIO (baseline - what happens if you do nothing)
  const noActionScenario: ScenarioOutcome = {
    name: 'No Action Path',
    description: 'If you don\'t make any changes and continue with current settings',
    probability: 100,
    metrics: {
      ctr: currentCTR * 0.88,
      ctrChange: -12,
      cpc: currentCPC * 1.12,
      cpcChange: 12,
      bounceRate: currentBounceRate * 1.15,
      bounceRateChange: 15,
      conversions: currentConversions * 0.82,
      conversionsChange: -18,
      monthlyROI: calculateMonthlyROI(
        currentConversions * 0.82 * 30,
        2500,
        currentCPC * keyword.ad_clicks * 30 * 1.12
      ),
      qualityScore: Math.max(currentQualityScore - 12, 0),
    },
    risks: [
      `Opportunity cost: ₹${Math.round(currentConversions * 2500 * 0.18 * 30).toLocaleString()}/month in lost revenue`,
      'Quality Score degradation (estimated -12 points over 3 months)',
      'Competitors optimize while you stay static',
      'Higher CPC as competition increases',
    ],
    opportunities: [
      'Zero implementation risk',
      'No resource allocation needed',
      'Can observe competitor strategies first',
    ],
    timeline: 'Gradual decline over 3 months',
    actionSteps: [
      'Monitor weekly performance trends',
      'Watch for further deterioration',
      'Consider action if metrics decline >20%',
    ],
  };

  return {
    keyword: keyword.keyword_text,
    currentMetrics: {
      ctr: currentCTR,
      cpc: currentCPC,
      bounceRate: currentBounceRate,
      conversions: currentConversions,
      qualityScore: currentQualityScore,
    },
    recommendation: {
      action: recommendationAction,
      rationale: recommendationRationale,
    },
    scenarios: {
      success: successScenario,
      failure: failureScenario,
      noAction: noActionScenario,
    },
  };
};

/**
 * Calculate aggregate simulation for multiple keywords
 */
export const generateAggregateSimulation = (keywords: KeywordMetrics[]): {
  totalKeywords: number;
  avgQualityScore: number;
  aggregateScenarios: {
    success: { totalROI: number; totalConversions: number };
    failure: { totalROI: number; totalConversions: number };
    noAction: { totalROI: number; totalConversions: number };
  };
} => {
  const simulations = keywords.map(generateKeywordSimulation);

  const avgQualityScore = keywords.reduce((sum, k) => sum + k.quality_score, 0) / keywords.length;

  const aggregateScenarios = {
    success: {
      totalROI: simulations.reduce((sum, s) => sum + s.scenarios.success.metrics.monthlyROI, 0),
      totalConversions: simulations.reduce(
        (sum, s) => sum + s.scenarios.success.metrics.conversions,
        0
      ),
    },
    failure: {
      totalROI: simulations.reduce((sum, s) => sum + s.scenarios.failure.metrics.monthlyROI, 0),
      totalConversions: simulations.reduce(
        (sum, s) => sum + s.scenarios.failure.metrics.conversions,
        0
      ),
    },
    noAction: {
      totalROI: simulations.reduce((sum, s) => sum + s.scenarios.noAction.metrics.monthlyROI, 0),
      totalConversions: simulations.reduce(
        (sum, s) => sum + s.scenarios.noAction.metrics.conversions,
        0
      ),
    },
  };

  return {
    totalKeywords: keywords.length,
    avgQualityScore,
    aggregateScenarios,
  };
};
