/**
 * Campaign Simulator Dashboard - Optimization Agent
 *
 * What-if scenario testing for campaign optimization
 *
 * Features:
 * - Budget adjustment simulations
 * - Bid change impact analysis
 * - ROAS predictions
 * - Multi-variable scenario testing
 * - Side-by-side comparison
 *
 * Structure:
 * - Header (Title + Description)
 * - Scenario Configuration Panel
 * - Current vs Simulated Metrics
 * - Impact Visualization
 * - Recommendations
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  AlertTitle,
  Chip,
  CircularProgress,
  Divider,
  Button,
  Paper,
  Slider,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Switch,
  FormControlLabel,
} from '@mui/material';
import {
  Science,
  TrendingUp,
  TrendingDown,
  AttachMoney,
  CompareArrows,
  PlayArrow,
  Refresh,
  Lightbulb,
  Timeline,
  Assessment,
  Psychology,
  TrendingFlat,
} from '@mui/icons-material';
import { useFilters } from '../../../../context/FilterContext';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  RadarChart,
  PolarGrid,
  PolarAngleAxis,
  PolarRadiusAxis,
  Radar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface SimulationParams {
  budgetChange: number; // percentage
  bidChange: number; // percentage
  ctrImprovement: number; // percentage
  conversionRateChange: number; // percentage
}

interface SimulationResult {
  metric: string;
  current: number;
  simulated: number;
  change: number;
  changePct: number;
}

const CampaignSimulator: React.FC = () => {
  const { filters } = useFilters();
  const [loading, setLoading] = useState(false);
  const [campaignData, setCampaignData] = useState<any>(null);
  const [simulating, setSimulating] = useState(false);

  // Simulation parameters
  const [budgetChange, setBudgetChange] = useState<number>(0);
  const [bidChange, setBidChange] = useState<number>(0);
  const [ctrImprovement, setCtrImprovement] = useState<number>(0);
  const [conversionRateChange, setConversionRateChange] = useState<number>(0);
  const [autoOptimize, setAutoOptimize] = useState<boolean>(false);

  // Base metrics (mock data - in production, fetch from API)
  const baseMetrics = useMemo(() => ({
    budget: 5000,
    avgCPC: 1.25,
    impressions: 45000,
    clicks: 1350,
    ctr: 3.0,
    conversions: 67,
    conversionRate: 4.96,
    cost: 1687.50,
    revenue: 3375,
    roas: 2.0,
  }), []);

  // Calculate simulated results
  const simulationResults = useMemo((): SimulationResult[] => {
    const budgetMultiplier = 1 + (budgetChange / 100);
    const bidMultiplier = 1 + (bidChange / 100);
    const ctrMultiplier = 1 + (ctrImprovement / 100);
    const convRateMultiplier = 1 + (conversionRateChange / 100);

    // Simulation logic
    const simBudget = baseMetrics.budget * budgetMultiplier;
    const simCPC = baseMetrics.avgCPC * bidMultiplier;

    // Higher budget + higher CPC = more impressions but decreasing returns
    const impressionIncrease = budgetMultiplier * 0.8; // 80% efficiency
    const simImpressions = baseMetrics.impressions * impressionIncrease;

    const simCTR = baseMetrics.ctr * ctrMultiplier;
    const simClicks = (simImpressions * simCTR) / 100;

    const simConversionRate = baseMetrics.conversionRate * convRateMultiplier;
    const simConversions = (simClicks * simConversionRate) / 100;

    const simCost = simClicks * simCPC;
    const simRevenue = simConversions * (baseMetrics.revenue / baseMetrics.conversions); // avg order value
    const simROAS = simCost > 0 ? simRevenue / simCost : 0;

    const results: SimulationResult[] = [
      {
        metric: 'Budget',
        current: baseMetrics.budget,
        simulated: simBudget,
        change: simBudget - baseMetrics.budget,
        changePct: budgetChange,
      },
      {
        metric: 'Avg CPC',
        current: baseMetrics.avgCPC,
        simulated: simCPC,
        change: simCPC - baseMetrics.avgCPC,
        changePct: bidChange,
      },
      {
        metric: 'Impressions',
        current: baseMetrics.impressions,
        simulated: simImpressions,
        change: simImpressions - baseMetrics.impressions,
        changePct: ((simImpressions - baseMetrics.impressions) / baseMetrics.impressions) * 100,
      },
      {
        metric: 'CTR',
        current: baseMetrics.ctr,
        simulated: simCTR,
        change: simCTR - baseMetrics.ctr,
        changePct: ctrImprovement,
      },
      {
        metric: 'Clicks',
        current: baseMetrics.clicks,
        simulated: simClicks,
        change: simClicks - baseMetrics.clicks,
        changePct: ((simClicks - baseMetrics.clicks) / baseMetrics.clicks) * 100,
      },
      {
        metric: 'Conversion Rate',
        current: baseMetrics.conversionRate,
        simulated: simConversionRate,
        change: simConversionRate - baseMetrics.conversionRate,
        changePct: conversionRateChange,
      },
      {
        metric: 'Conversions',
        current: baseMetrics.conversions,
        simulated: simConversions,
        change: simConversions - baseMetrics.conversions,
        changePct: ((simConversions - baseMetrics.conversions) / baseMetrics.conversions) * 100,
      },
      {
        metric: 'Cost',
        current: baseMetrics.cost,
        simulated: simCost,
        change: simCost - baseMetrics.cost,
        changePct: ((simCost - baseMetrics.cost) / baseMetrics.cost) * 100,
      },
      {
        metric: 'Revenue',
        current: baseMetrics.revenue,
        simulated: simRevenue,
        change: simRevenue - baseMetrics.revenue,
        changePct: ((simRevenue - baseMetrics.revenue) / baseMetrics.revenue) * 100,
      },
      {
        metric: 'ROAS',
        current: baseMetrics.roas,
        simulated: simROAS,
        change: simROAS - baseMetrics.roas,
        changePct: ((simROAS - baseMetrics.roas) / baseMetrics.roas) * 100,
      },
    ];

    return results;
  }, [budgetChange, bidChange, ctrImprovement, conversionRateChange, baseMetrics]);

  const comparisonData = useMemo(() => {
    return simulationResults.map(result => ({
      metric: result.metric,
      Current: result.current,
      Simulated: result.simulated,
    }));
  }, [simulationResults]);

  const radarData = useMemo(() => {
    // Normalize metrics for radar chart (0-100 scale)
    const normalize = (value: number, max: number) => Math.min((value / max) * 100, 100);

    return [
      {
        metric: 'Budget',
        Current: normalize(baseMetrics.budget, 10000),
        Simulated: normalize(simulationResults.find(r => r.metric === 'Budget')?.simulated || 0, 10000),
      },
      {
        metric: 'CTR',
        Current: normalize(baseMetrics.ctr, 10),
        Simulated: normalize(simulationResults.find(r => r.metric === 'CTR')?.simulated || 0, 10),
      },
      {
        metric: 'Conv. Rate',
        Current: normalize(baseMetrics.conversionRate, 10),
        Simulated: normalize(simulationResults.find(r => r.metric === 'Conversion Rate')?.simulated || 0, 10),
      },
      {
        metric: 'ROAS',
        Current: normalize(baseMetrics.roas, 5),
        Simulated: normalize(simulationResults.find(r => r.metric === 'ROAS')?.simulated || 0, 5),
      },
      {
        metric: 'Conversions',
        Current: normalize(baseMetrics.conversions, 200),
        Simulated: normalize(simulationResults.find(r => r.metric === 'Conversions')?.simulated || 0, 200),
      },
    ];
  }, [baseMetrics, simulationResults]);

  const handleAutoOptimize = () => {
    // Auto-optimize: recommend best settings based on ROAS
    setBudgetChange(20); // Increase budget
    setBidChange(-5); // Decrease CPC
    setCtrImprovement(15); // Improve CTR
    setConversionRateChange(10); // Improve conversion rate
  };

  const handleReset = () => {
    setBudgetChange(0);
    setBidChange(0);
    setCtrImprovement(0);
    setConversionRateChange(0);
  };

  const roasResult = simulationResults.find(r => r.metric === 'ROAS');
  const revenueResult = simulationResults.find(r => r.metric === 'Revenue');

  // AI Analysis - 4 Types (Simulation & Scenario Testing focus)
  const aiAnalysis = useMemo(() => {
    const conversionsResult = simulationResults.find(r => r.metric === 'Conversions');
    const costResult = simulationResults.find(r => r.metric === 'Cost');
    const ctrResult = simulationResults.find(r => r.metric === 'CTR');
    const clicksResult = simulationResults.find(r => r.metric === 'Clicks');

    const isOptimizing = budgetChange !== 0 || bidChange !== 0 || ctrImprovement !== 0 || conversionRateChange !== 0;

    if (!isOptimizing) {
      return {
        descriptive: { text: 'Adjust simulation parameters to see predicted outcomes.\n\nUse sliders above to test different scenarios:\n• Budget adjustments (-50% to +100%)\n• Bid/CPC changes (-50% to +50%)\n• CTR improvements (-30% to +50%)\n• Conversion rate changes (-30% to +50%)\n\nOr click "Auto-Optimize" for AI-recommended settings.', icon: Assessment, color: '#1E88E5' },
        diagnostic: { text: '', icon: Psychology, color: '#7B1FA2' },
        predictive: { text: '', icon: Timeline, color: '#F57C00' },
        prescriptive: { text: '', icon: Lightbulb, color: '#388E3C' },
      };
    }

    // 1. DESCRIPTIVE: What scenario is being tested
    const changedParams = [];
    if (budgetChange !== 0) changedParams.push(`Budget ${budgetChange > 0 ? 'increase' : 'reduction'} of ${Math.abs(budgetChange)}%`);
    if (bidChange !== 0) changedParams.push(`CPC ${bidChange > 0 ? 'increase' : 'reduction'} of ${Math.abs(bidChange)}%`);
    if (ctrImprovement !== 0) changedParams.push(`CTR ${ctrImprovement > 0 ? 'improvement' : 'decline'} of ${Math.abs(ctrImprovement)}%`);
    if (conversionRateChange !== 0) changedParams.push(`Conversion rate ${conversionRateChange > 0 ? 'improvement' : 'decline'} of ${Math.abs(conversionRateChange)}%`);

    const descriptive = `Scenario Simulation Results:\n\nParameters Changed:\n• ${changedParams.join('\n• ')}\n\nProjected Outcomes:\n• ROAS: ${baseMetrics.roas.toFixed(2)}x → ${roasResult?.simulated.toFixed(2)}x (${roasResult && roasResult.changePct > 0 ? '+' : ''}${roasResult?.changePct.toFixed(1)}%)\n• Revenue: ₹${baseMetrics.revenue} → ₹${revenueResult?.simulated.toFixed(0)} (${revenueResult && revenueResult.changePct > 0 ? '+' : ''}${revenueResult?.changePct.toFixed(1)}%)\n• Conversions: ${baseMetrics.conversions} → ${conversionsResult?.simulated.toFixed(0)} (${conversionsResult && conversionsResult.changePct > 0 ? '+' : ''}${conversionsResult?.changePct.toFixed(1)}%)\n• Cost: ₹${baseMetrics.cost} → ₹${costResult?.simulated.toFixed(0)} (${costResult && costResult.changePct > 0 ? '+' : ''}${costResult?.changePct.toFixed(1)}%)`;

    // 2. DIAGNOSTIC: Why these outcomes occur
    let diagnostic = `Simulation Logic & Drivers:\n\n`;

    if (budgetChange > 0) {
      diagnostic += `Budget Increase Impact:\n• Higher budget → +${((clicksResult?.changePct || 0) * 0.8).toFixed(1)}% clicks (80% efficiency due to diminishing returns)\n• More traffic → ${(conversionsResult?.changePct || 0) > 0 ? 'increased' : 'decreased'} conversion volume\n\n`;
    } else if (budgetChange < 0) {
      diagnostic += `Budget Reduction Impact:\n• Lower budget → ${clicksResult?.changePct.toFixed(1)}% fewer clicks\n• Reduced traffic → proportional conversion decline\n\n`;
    }

    if (ctrImprovement !== 0) {
      diagnostic += `CTR ${ctrImprovement > 0 ? 'Improvement' : 'Decline'} Effect:\n• Better ad relevance → ${ctrImprovement > 0 ? 'more' : 'fewer'} clicks per impression\n• Quality Score impact → ${ctrImprovement > 0 ? 'potential CPC reduction' : 'possible CPC increase'}\n\n`;
    }

    if (conversionRateChange !== 0) {
      diagnostic += `Conversion Rate ${conversionRateChange > 0 ? 'Optimization' : 'Decline'}:\n• Landing page improvements → ${conversionRateChange > 0 ? 'higher' : 'lower'} conversion efficiency\n• Revenue per click ${conversionRateChange > 0 ? 'increases' : 'decreases'} proportionally\n\n`;
    }

    const roasChange = roasResult?.change || 0;
    if (roasChange > 0.5) {
      diagnostic += `⚠️ Strong ROAS improvement driven by ${ctrImprovement > 0 ? 'CTR' : conversionRateChange > 0 ? 'conversion rate' : 'efficiency'} gains`;
    } else if (roasChange < -0.3) {
      diagnostic += `⚠️ ROAS decline indicates cost growth outpacing revenue gains`;
    }

    // 3. PREDICTIVE: Forecast confidence & risks
    const confidenceScore = Math.abs(budgetChange) > 50 || Math.abs(bidChange) > 30 ? 65 : 85;
    const revenueUplift = revenueResult?.change || 0;
    const costIncrease = costResult?.change || 0;
    const netProfit = revenueUplift - costIncrease;

    let riskLevel = 'Low';
    let riskFactors = [];
    if (Math.abs(budgetChange) > 50) {
      riskLevel = 'High';
      riskFactors.push('Large budget swings may face market saturation');
    }
    if (roasChange < 0) {
      riskLevel = 'Medium';
      riskFactors.push('Negative ROAS trend requires close monitoring');
    }
    if (ctrImprovement > 30 || conversionRateChange > 30) {
      riskLevel = 'Medium';
      riskFactors.push('Aggressive optimization assumptions may not materialize');
    }

    let predictive = `Performance Forecast:\n\nProjected Financial Impact:\n• Net revenue change: ${revenueUplift > 0 ? '+' : ''}₹${revenueUplift.toFixed(0)}\n• Cost change: ${costIncrease > 0 ? '+' : ''}₹${costIncrease.toFixed(0)}\n• Net profit impact: ${netProfit > 0 ? '+' : ''}₹${netProfit.toFixed(0)}\n\nForecast Confidence: ${confidenceScore}%\nRisk Level: ${riskLevel}`;

    if (riskFactors.length > 0) {
      predictive += `\n\nRisk Factors:\n• ${riskFactors.join('\n• ')}`;
    }

    // 4. PRESCRIPTIVE: Recommendations
    const recommendations: string[] = [];

    if (roasChange > 0) {
      recommendations.push(`1. Implement this scenario - projected ${roasResult?.changePct.toFixed(1)}% ROAS improvement`);
    } else if (roasChange < -0.2) {
      recommendations.push(`1. ⚠️ Avoid this scenario - ROAS would decline ${Math.abs(roasResult?.changePct || 0).toFixed(1)}%`);
    }

    if (ctrImprovement > 0 && conversionRateChange > 0) {
      recommendations.push(`2. Prioritize creative & landing page optimization for maximum impact`);
    } else if (ctrImprovement > 0) {
      recommendations.push(`2. Focus on ad creative testing to achieve CTR improvement`);
    } else if (conversionRateChange > 0) {
      recommendations.push(`2. Invest in landing page optimization for conversion gains`);
    }

    if (budgetChange > 0 && roasChange > 0) {
      recommendations.push(`3. Scale budget gradually - test +${Math.min(20, budgetChange)}% first, then expand`);
    } else if (budgetChange < 0 && roasChange < 0) {
      recommendations.push(`3. Consider budget reduction to ${Math.abs(budgetChange)}% to cut waste`);
    }

    if (netProfit > 0) {
      recommendations.push(`4. Expected ROI: +₹${netProfit.toFixed(0)} profit - strong business case`);
    } else {
      recommendations.push(`4. Negative ROI projected - revise parameters before implementation`);
    }

    const prescriptive = `Actionable Recommendations:\n${recommendations.slice(0, 4).join('\n')}\n\nImplementation Plan:\n• Start with smallest viable change to validate assumptions\n• Monitor actual results vs predictions for 7-14 days\n• Adjust based on real performance data\n• Confidence level: ${confidenceScore}%`;

    return {
      descriptive: {
        text: descriptive,
        icon: Assessment,
        color: '#1E88E5',
      },
      diagnostic: {
        text: diagnostic,
        icon: Psychology,
        color: '#7B1FA2',
      },
      predictive: {
        text: predictive,
        icon: Timeline,
        color: '#F57C00',
      },
      prescriptive: {
        text: prescriptive,
        icon: Lightbulb,
        color: '#388E3C',
      },
    };
  }, [simulationResults, budgetChange, bidChange, ctrImprovement, conversionRateChange, baseMetrics, roasResult, revenueResult]);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Science fontSize="large" color="primary" />
          Campaign Simulator
        </Typography>
        <Typography variant="body1" color="text.secondary">
          What-if scenario testing - Predict campaign performance with different parameters
        </Typography>
      </Box>

      {/* Quick Actions */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <Button
          variant="contained"
          color="primary"
          startIcon={<Lightbulb />}
          onClick={handleAutoOptimize}
        >
          Auto-Optimize
        </Button>
        <Button
          variant="outlined"
          startIcon={<Refresh />}
          onClick={handleReset}
        >
          Reset
        </Button>
      </Box>

      {/* Impact Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{
            background: roasResult && roasResult.change > 0
              ? 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)'
              : 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)',
            color: 'white'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Simulated ROAS</Typography>
                  <Typography variant="h3" fontWeight={700}>
                    {roasResult?.simulated.toFixed(2)}x
                  </Typography>
                  <Typography variant="caption">
                    {roasResult && roasResult.change > 0 ? '+' : ''}{roasResult?.changePct.toFixed(1)}%
                  </Typography>
                </Box>
                {roasResult && roasResult.change > 0 ? (
                  <TrendingUp sx={{ fontSize: 50, opacity: 0.7 }} />
                ) : (
                  <TrendingDown sx={{ fontSize: 50, opacity: 0.7 }} />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{
            background: revenueResult && revenueResult.change > 0
              ? 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
              : 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
            color: 'white'
          }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Revenue Change</Typography>
                  <Typography variant="h3" fontWeight={700}>
                    {revenueResult && revenueResult.change > 0 ? '+' : ''}₹{revenueResult?.change.toFixed(0)}
                  </Typography>
                  <Typography variant="caption">
                    {revenueResult && revenueResult.change > 0 ? '+' : ''}{revenueResult?.changePct.toFixed(1)}%
                  </Typography>
                </Box>
                <AttachMoney sx={{ fontSize: 50, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Conversions Change</Typography>
                  <Typography variant="h3" fontWeight={700} color="text.primary">
                    {simulationResults.find(r => r.metric === 'Conversions')?.change.toFixed(0)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {simulationResults.find(r => r.metric === 'Conversions')?.changePct.toFixed(1)}%
                  </Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 50, color: 'text.secondary', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Cost Change</Typography>
                  <Typography variant="h3" fontWeight={700} color="text.primary">
                    ₹{simulationResults.find(r => r.metric === 'Cost')?.change.toFixed(0)}
                  </Typography>
                  <Typography variant="caption" color="text.secondary">
                    {simulationResults.find(r => r.metric === 'Cost')?.changePct.toFixed(1)}%
                  </Typography>
                </Box>
                <AttachMoney sx={{ fontSize: 50, color: 'text.secondary', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* AI Intelligence */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
          🧠 AI Intelligence
        </Typography>

        <Grid container spacing={2.5}>
          {/* 1. Descriptive */}
          <Grid item xs={12} md={6}>
            <Card
              elevation={0}
              sx={{
                height: '100%',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                transition: 'all 0.3s',
                '&:hover': {
                  boxShadow: `0 4px 20px ${aiAnalysis.descriptive.color}20`,
                  borderColor: aiAnalysis.descriptive.color,
                }
              }}
            >
              <CardContent sx={{ p: 2.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box
                    sx={{
                      width: 36,
                      height: 36,
                      borderRadius: 1.5,
                      bgcolor: `${aiAnalysis.descriptive.color}10`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Assessment sx={{ color: aiAnalysis.descriptive.color, fontSize: 20 }} />
                  </Box>
                  <Box flex={1}>
                    <Typography variant="subtitle2" sx={{ color: aiAnalysis.descriptive.color, fontWeight: 600 }}>
                      Descriptive
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Scenario overview
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.secondary' }}>
                  {aiAnalysis.descriptive.text || 'Adjust parameters to see predictions...'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* 2. Diagnostic */}
          <Grid item xs={12} md={6}>
            <Card
              elevation={0}
              sx={{
                height: '100%',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                transition: 'all 0.3s',
                '&:hover': {
                  boxShadow: `0 4px 20px ${aiAnalysis.diagnostic.color}20`,
                  borderColor: aiAnalysis.diagnostic.color,
                }
              }}
            >
              <CardContent sx={{ p: 2.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box
                    sx={{
                      width: 36,
                      height: 36,
                      borderRadius: 1.5,
                      bgcolor: `${aiAnalysis.diagnostic.color}10`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Psychology sx={{ color: aiAnalysis.diagnostic.color, fontSize: 20 }} />
                  </Box>
                  <Box flex={1}>
                    <Typography variant="subtitle2" sx={{ color: aiAnalysis.diagnostic.color, fontWeight: 600 }}>
                      Diagnostic
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Why these results
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.secondary' }}>
                  {aiAnalysis.diagnostic.text || 'Adjust parameters to see analysis...'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* 3. Predictive */}
          <Grid item xs={12} md={6}>
            <Card
              elevation={0}
              sx={{
                height: '100%',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                transition: 'all 0.3s',
                '&:hover': {
                  boxShadow: `0 4px 20px ${aiAnalysis.predictive.color}20`,
                  borderColor: aiAnalysis.predictive.color,
                }
              }}
            >
              <CardContent sx={{ p: 2.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box
                    sx={{
                      width: 36,
                      height: 36,
                      borderRadius: 1.5,
                      bgcolor: `${aiAnalysis.predictive.color}10`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Timeline sx={{ color: aiAnalysis.predictive.color, fontSize: 20 }} />
                  </Box>
                  <Box flex={1}>
                    <Typography variant="subtitle2" sx={{ color: aiAnalysis.predictive.color, fontWeight: 600 }}>
                      Predictive
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Forecast & risks
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.secondary' }}>
                  {aiAnalysis.predictive.text || 'Adjust parameters to see forecast...'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* 4. Prescriptive */}
          <Grid item xs={12} md={6}>
            <Card
              elevation={0}
              sx={{
                height: '100%',
                border: '1px solid',
                borderColor: aiAnalysis.prescriptive.color,
                borderRadius: 2,
                background: `linear-gradient(135deg, ${aiAnalysis.prescriptive.color}08 0%, ${aiAnalysis.prescriptive.color}03 100%)`,
                transition: 'all 0.3s',
                '&:hover': {
                  boxShadow: `0 4px 20px ${aiAnalysis.prescriptive.color}25`,
                }
              }}
            >
              <CardContent sx={{ p: 2.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box
                    sx={{
                      width: 36,
                      height: 36,
                      borderRadius: 1.5,
                      bgcolor: `${aiAnalysis.prescriptive.color}15`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Lightbulb sx={{ color: aiAnalysis.prescriptive.color, fontSize: 20 }} />
                  </Box>
                  <Box flex={1}>
                    <Typography variant="subtitle2" sx={{ color: aiAnalysis.prescriptive.color, fontWeight: 600 }}>
                      Prescriptive
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Action plan
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.primary', fontWeight: 500 }}>
                  {aiAnalysis.prescriptive.text || 'Adjust parameters to see recommendations...'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Simulation Controls */}
      <Card sx={{ mb: 4, background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)' }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Simulation Parameters
          </Typography>
          <Divider sx={{ my: 2 }} />

          <Grid container spacing={4}>
            <Grid item xs={12} md={6}>
              <Typography variant="body2" gutterBottom>
                Budget Change: {budgetChange > 0 ? '+' : ''}{budgetChange}%
              </Typography>
              <Slider
                value={budgetChange}
                onChange={(e, value) => setBudgetChange(value as number)}
                min={-50}
                max={100}
                step={5}
                marks
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${value > 0 ? '+' : ''}${value}%`}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="body2" gutterBottom>
                Bid/CPC Change: {bidChange > 0 ? '+' : ''}{bidChange}%
              </Typography>
              <Slider
                value={bidChange}
                onChange={(e, value) => setBidChange(value as number)}
                min={-50}
                max={50}
                step={5}
                marks
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${value > 0 ? '+' : ''}${value}%`}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="body2" gutterBottom>
                CTR Improvement: {ctrImprovement > 0 ? '+' : ''}{ctrImprovement}%
              </Typography>
              <Slider
                value={ctrImprovement}
                onChange={(e, value) => setCtrImprovement(value as number)}
                min={-30}
                max={50}
                step={5}
                marks
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${value > 0 ? '+' : ''}${value}%`}
              />
            </Grid>

            <Grid item xs={12} md={6}>
              <Typography variant="body2" gutterBottom>
                Conversion Rate Change: {conversionRateChange > 0 ? '+' : ''}{conversionRateChange}%
              </Typography>
              <Slider
                value={conversionRateChange}
                onChange={(e, value) => setConversionRateChange(value as number)}
                min={-30}
                max={50}
                step={5}
                marks
                valueLabelDisplay="auto"
                valueLabelFormat={(value) => `${value > 0 ? '+' : ''}${value}%`}
              />
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Radar Comparison */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Performance Comparison (Current vs Simulated)
          </Typography>
          <Divider sx={{ my: 2 }} />
          <ResponsiveContainer width="100%" height={400}>
            <RadarChart data={radarData}>
              <PolarGrid />
              <PolarAngleAxis dataKey="metric" />
              <PolarRadiusAxis angle={90} domain={[0, 100]} />
              <Radar name="Current" dataKey="Current" stroke="#667eea" fill="#667eea" fillOpacity={0.3} />
              <Radar name="Simulated" dataKey="Simulated" stroke="#43e97b" fill="#43e97b" fillOpacity={0.3} />
              <Legend />
              <Tooltip />
            </RadarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Detailed Comparison Bar Chart */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Detailed Metrics Comparison
          </Typography>
          <Divider sx={{ my: 2 }} />
          <ResponsiveContainer width="100%" height={400}>
            <BarChart data={comparisonData.filter(d => ['Budget', 'Clicks', 'Conversions', 'Cost', 'Revenue'].includes(d.metric))}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="metric" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Bar dataKey="Current" fill="#667eea" />
              <Bar dataKey="Simulated" fill="#43e97b" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Simulation Insights */}
      <Card sx={{ background: 'linear-gradient(135deg, #f093fb15 0%, #f5576c15 100%)' }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
            <Lightbulb color="warning" />
            Simulation Insights
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
            {roasResult && roasResult.change > 0 && (
              <Alert severity="success">
                <AlertTitle>ROAS Improvement</AlertTitle>
                Your simulated changes would improve ROAS by {roasResult.changePct.toFixed(1)}%,
                from {roasResult.current.toFixed(2)}x to {roasResult.simulated.toFixed(2)}x.
              </Alert>
            )}
            {roasResult && roasResult.change < 0 && (
              <Alert severity="warning">
                <AlertTitle>ROAS Decline</AlertTitle>
                Warning: These changes would decrease ROAS by {Math.abs(roasResult.changePct).toFixed(1)}%.
                Consider adjusting parameters.
              </Alert>
            )}
            {revenueResult && revenueResult.change > 0 && (
              <Alert severity="info">
                <AlertTitle>Revenue Projection</AlertTitle>
                Expected revenue increase: ₹{revenueResult.change.toFixed(0)} ({revenueResult.changePct.toFixed(1)}%)
              </Alert>
            )}
            <Alert severity="info">
              <AlertTitle>Recommendation</AlertTitle>
              {budgetChange > 0 && ctrImprovement > 0
                ? 'Increasing budget with CTR improvements is a strong strategy for scaling.'
                : bidChange < 0 && conversionRateChange > 0
                ? 'Lowering CPC while improving conversion rate will maximize profitability.'
                : 'Try the Auto-Optimize feature for AI-recommended settings.'}
            </Alert>
          </Box>
        </CardContent>
      </Card>
    </Box>
  );
};

export default CampaignSimulator;
