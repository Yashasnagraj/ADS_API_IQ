// Utility functions to generate insights for different dashboard types

export interface InsightData {
  type: 'descriptive' | 'diagnostic' | 'predictive' | 'prescriptive';
  title: string;
  message: string;
  impact?: 'high' | 'medium' | 'low';
  confidence?: number;
  action?: {
    label: string;
    onClick: () => void;
  };
  metrics?: {
    label: string;
    value: string | number;
    trend?: 'up' | 'down' | 'stable';
  }[];
}

export const generateAdGroupInsights = (data?: any): InsightData[] => {
  return [
    {
      type: 'descriptive',
      title: 'Ad Group Performance Overview',
      message: 'You have 156 ad groups with 102 currently active. Average CTR across all ad groups is 4.8%, which is 60% above industry average.',
      metrics: [
        { label: 'Active Rate', value: '65.4%', trend: 'up' },
        { label: 'Top Performer', value: 'Brand Keywords', trend: 'stable' },
      ],
    },
    {
      type: 'diagnostic',
      title: 'Performance Drivers Analysis',
      message: 'Your "Brand Keywords" ad group performs 40% better due to high relevance scores and optimized bid strategy. Weekend performance drops 25% across all groups.',
      impact: 'medium',
      confidence: 0.87,
    },
    {
      type: 'predictive',
      title: '30-Day Performance Forecast',
      message: 'Based on seasonal trends, we predict a 20% increase in impressions for product-focused ad groups. Competition will increase by 15% in your category.',
      confidence: 0.79,
      metrics: [
        { label: 'Predicted CTR', value: '5.2%', trend: 'up' },
        { label: 'Est. Spend', value: '₹68,500', trend: 'up' },
      ],
    },
    {
      type: 'prescriptive',
      title: 'Optimization Recommendations',
      message: 'Pause 3 underperforming ad groups with CTR below 2%. Increase budget by 30% for "Brand Keywords" group. Split test new ad copy for groups with declining CTR.',
      impact: 'high',
      confidence: 0.92,
      action: {
        label: 'Optimize Ad Groups',
        onClick: () => console.log('Optimizing ad groups...'),
      },
    },
  ];
};

export const generateSearchTermInsights = (data?: any): InsightData[] => {
  return [
    {
      type: 'descriptive',
      title: 'Search Terms Analysis',
      message: '1,234 unique search terms triggered your ads this month. 234 have been added as keywords, while 56 were added as negatives.',
      metrics: [
        { label: 'New Terms', value: '89', trend: 'up' },
        { label: 'Conversion Rate', value: '3.8%', trend: 'stable' },
      ],
    },
    {
      type: 'diagnostic',
      title: 'Search Intent Patterns',
      message: 'Terms containing "buy" or "price" convert 3x better. Long-tail queries (4+ words) show 45% higher intent but 60% lower volume.',
      impact: 'high',
      confidence: 0.91,
    },
    {
      type: 'predictive',
      title: 'Emerging Search Trends',
      message: 'AI predicts 35% growth in voice search queries. Mobile searches during commute hours will increase by 25% next quarter.',
      confidence: 0.76,
      metrics: [
        { label: 'New Terms/Week', value: '45-60', trend: 'up' },
      ],
    },
    {
      type: 'prescriptive',
      title: 'Search Term Actions',
      message: 'Add 23 high-converting search terms as exact match keywords. Block 18 irrelevant terms costing ₹3,200/month. Create dedicated ad groups for commercial intent queries.',
      impact: 'high',
      confidence: 0.88,
      action: {
        label: 'Apply Recommendations',
        onClick: () => console.log('Applying search term recommendations...'),
      },
    },
  ];
};

export const generateMLInsights = (data?: any): InsightData[] => {
  return [
    {
      type: 'descriptive',
      title: 'ML Model Performance',
      message: 'Current model achieves 87% accuracy in predicting campaign performance. Quality Score and Bid Amount are the strongest predictive features.',
      metrics: [
        { label: 'Model Accuracy', value: '87%', trend: 'up' },
        { label: 'Features Used', value: '24', trend: 'stable' },
      ],
    },
    {
      type: 'diagnostic',
      title: 'Feature Impact Analysis',
      message: 'Quality Score contributes 28% to prediction accuracy. Landing page experience shows stronger correlation with conversions than expected (r=0.78).',
      impact: 'medium',
      confidence: 0.93,
    },
    {
      type: 'predictive',
      title: 'ML-Powered Predictions',
      message: 'Model predicts 18.5% increase in CTR if quality scores improve by 1 point. Conversion rate will reach 4.2% with recommended optimizations.',
      confidence: 0.85,
      metrics: [
        { label: 'Predicted CTR', value: '3.8%', trend: 'up' },
        { label: 'Predicted CPC', value: '₹1.32', trend: 'down' },
      ],
    },
    {
      type: 'prescriptive',
      title: 'AI Recommendations',
      message: 'Focus on improving Quality Score for maximum impact. Adjust bids based on ML predictions to reduce CPC by 15%. Implement suggested landing page changes.',
      impact: 'high',
      confidence: 0.89,
      action: {
        label: 'Apply AI Suggestions',
        onClick: () => console.log('Applying ML recommendations...'),
      },
    },
  ];
};

// Helper function to get contextual tips
export const getContextualTips = (dashboardType: string): string[] => {
  const tips: { [key: string]: string[] } = {
    campaigns: [
      'Active campaigns should maintain CTR above 3% for optimal performance',
      'Review campaign budgets weekly to prevent overspending',
      'A/B test ad copies to improve click-through rates',
      'Use dayparting to show ads during peak conversion hours',
    ],
    keywords: [
      'Keywords with Quality Score 7+ get 50% lower CPC on average',
      'Use negative keywords to prevent irrelevant clicks',
      'Long-tail keywords often have higher conversion rates',
      'Review search terms weekly to find new keyword opportunities',
    ],
    adgroups: [
      'Keep ad groups focused with 15-20 closely related keywords',
      'Match ad copy to keyword themes for better Quality Score',
      'Use SKAG (Single Keyword Ad Groups) for high-value terms',
      'Test different match types to balance reach and relevance',
    ],
    searchterms: [
      'Add converting search terms as exact match keywords',
      'Block irrelevant terms to reduce wasted spend',
      'Look for patterns in high-converting queries',
      'Monitor for trademark violations in search terms',
    ],
    ml: [
      'ML predictions improve with more historical data',
      'Feature importance helps identify optimization priorities',
      'Regular model retraining ensures accuracy',
      'Combine ML insights with domain expertise for best results',
    ],
  };

  return tips[dashboardType] || [];
};