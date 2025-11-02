/**
 * Landing Page Data Constants
 * Centralized data for maintainability and easy content updates
 */

export const navItems = [
  { label: 'Home', href: '#hero' },
  { label: 'Features', href: '#features' },
  { label: 'Platforms', href: '#platforms' },
  { label: 'How It Works', href: '#how-it-works' },
  { label: 'Pricing', href: '#pricing' },
  { label: 'FAQ', href: '#faq' },
  { label: 'Contact', href: '#contact' },
];

export const platformCards = [
  {
    title: 'Google Ads',
    desc: 'Search, Display, Shopping campaigns unified',
    color: '#4285F4',
    icon: '🎯',
  },
  {
    title: 'Meta Ads',
    desc: 'Facebook & Instagram ad performance',
    color: '#1877F2',
    icon: '📱',
  },
  {
    title: 'Google Analytics',
    desc: 'Website traffic & behavior insights',
    color: '#E37400',
    icon: '📊',
  },
  {
    title: 'E-commerce',
    desc: 'Revenue, AOV, and product analytics',
    color: '#00C853',
    icon: '🛒',
  },
];

export const featureCards = [
  {
    icon: 'TrendingUp',
    title: 'AI-Powered Insights',
    description:
      'Get actionable recommendations based on your campaign data. Our AI analyzes patterns and suggests optimizations automatically.',
  },
  {
    icon: 'Speed',
    title: 'Real-Time Analytics',
    description:
      'Monitor your campaigns in real-time with live dashboards. See performance metrics update as they happen across all platforms.',
  },
  {
    icon: 'Psychology',
    title: 'Smart Predictions',
    description:
      'Forecast future performance with ML models. Predict ROAS, budget needs, and conversion trends before they happen.',
  },
  {
    icon: 'Timeline',
    title: 'Historical Analysis',
    description:
      'Track trends over time with comprehensive historical data. Understand seasonality and long-term campaign evolution.',
  },
  {
    icon: 'Warning',
    title: 'Automated Alerts',
    description:
      'Get notified instantly when campaigns underperform. Set custom thresholds and receive alerts via email or Slack.',
  },
  {
    icon: 'AttachMoney',
    title: 'Budget Optimization',
    description:
      'Automatically allocate budget to top-performing campaigns. Our algorithms maximize ROI by shifting spend dynamically.',
  },
];

export const quickBenefits = [
  {
    title: '10x Faster Reporting',
    description: 'Automated dashboards replace hours of manual work',
  },
  {
    title: '30% Better ROAS',
    description: 'AI-driven optimizations improve campaign efficiency',
  },
  {
    title: 'Unified View',
    description: 'All platforms in one place, no more tool switching',
  },
  {
    title: '24/7 Monitoring',
    description: 'Never miss critical performance changes',
  },
];

export const howItWorksSteps = [
  {
    number: '1',
    title: 'Connect Your Accounts',
    description:
      'Securely link Google Ads, Meta Ads, and Analytics in under 2 minutes with OAuth 2.0 authentication.',
  },
  {
    number: '2',
    title: 'AI Analyzes Your Data',
    description:
      'Our machine learning models process your historical data, identifying patterns and optimization opportunities.',
  },
  {
    number: '3',
    title: 'Get Actionable Insights',
    description:
      'Receive personalized recommendations with predicted impact. One-click apply optimizations or review before executing.',
  },
  {
    number: '4',
    title: 'Scale & Optimize',
    description:
      'Watch your ROAS improve as AI continuously learns from your campaigns and adjusts strategies in real-time.',
  },
];

export const pricingPlans = [
  {
    name: 'Starter',
    price: '₹4,999',
    period: '/month',
    description: 'Perfect for small businesses and startups',
    features: [
      'Up to 5 campaigns monitored',
      'Basic AI insights & alerts',
      'Google Ads + Meta Ads',
      'Email support',
      '7-day data retention',
    ],
    buttonText: 'Start Free Trial',
    popular: false,
  },
  {
    name: 'Professional',
    price: '₹14,999',
    period: '/month',
    description: 'For growing teams managing multiple clients',
    features: [
      'Unlimited campaigns',
      'Advanced AI predictions',
      'All platforms (Google, Meta, GA4)',
      'Priority support + Slack',
      '90-day data retention',
      'Custom reports & alerts',
      'API access',
    ],
    buttonText: 'Start Free Trial',
    popular: true,
  },
  {
    name: 'Enterprise',
    price: 'Custom',
    period: '',
    description: 'Custom solutions for large organizations',
    features: [
      'Everything in Professional',
      'Dedicated account manager',
      'White-label dashboards',
      'Custom integrations',
      'Unlimited data retention',
      'SLA guarantee',
      'On-premise deployment option',
    ],
    buttonText: 'Contact Sales',
    popular: false,
  },
];

export const faqItems = [
  {
    question: 'How does MarketingIQ connect to my ad accounts?',
    answer:
      'We use OAuth 2.0, the industry-standard secure authentication method. You never share passwords with us—just authorize read-only access to your campaign data. You can revoke access anytime from your Google/Meta account settings.',
  },
  {
    question: 'What makes your AI insights different from Google/Meta native tools?',
    answer:
      'Native platforms analyze only their own data. MarketingIQ combines data across Google Ads, Meta Ads, and GA4 to provide cross-platform insights. Our AI identifies opportunities like "Your Meta awareness campaigns are driving Google search conversions"—insights impossible to see in siloed dashboards.',
  },
  {
    question: 'Can I try it before committing?',
    answer:
      'Absolutely! We offer a 14-day free trial (no credit card required). Connect your accounts, explore the dashboards, and see AI insights in action. If you don\'t see value, cancel anytime with one click.',
  },
  {
    question: 'How accurate are the AI predictions?',
    answer:
      'Our forecasting models achieve 85-92% accuracy on average (validated against actual campaign outcomes). Accuracy improves over time as the AI learns your specific campaigns. We show confidence scores with every prediction so you know which to trust most.',
  },
  {
    question: 'Is my data secure?',
    answer:
      'Yes. We\'re SOC 2 Type II certified and encrypt all data in transit (TLS 1.3) and at rest (AES-256). Your data is stored in isolated environments and never shared with third parties. We\'re also GDPR compliant for our European customers.',
  },
  {
    question: 'Do I need technical skills to use MarketingIQ?',
    answer:
      'No coding required! If you can manage Google Ads or Meta Ads Manager, you can use MarketingIQ. Our interface is designed for marketers, not engineers. Setup takes <5 minutes, and our AI explains insights in plain English, not jargon.',
  },
];

export const testimonials = [
  {
    name: 'Priya Sharma',
    role: 'Marketing Director',
    company: 'TechCorp India',
    avatar: 'PS',
    rating: 5,
    text: 'MarketingIQ helped us reduce our Google Ads CPA by 34% in just 2 months. The AI insights are incredibly accurate.',
  },
  {
    name: 'Rajesh Kumar',
    role: 'E-commerce Manager',
    company: 'ShopNow',
    avatar: 'RK',
    rating: 5,
    text: 'Finally, a tool that shows me which platform is actually driving revenue. Unified reporting saved us 15 hours per week.',
  },
  {
    name: 'Anita Desai',
    role: 'CEO',
    company: 'GrowthAgency',
    avatar: 'AD',
    rating: 5,
    text: 'We manage 50+ client accounts. MarketingIQ\'s automated alerts catch issues before clients even notice. Game changer.',
  },
];

export const contactInfo = {
  email: 'hello@marketingiq.ai',
  phone: '+91 98765 43210',
  address: 'Bengaluru, Karnataka, India',
  social: {
    linkedin: 'https://linkedin.com/company/marketingiq',
    twitter: 'https://twitter.com/marketingiq',
    github: 'https://github.com/marketingiq',
  },
};
