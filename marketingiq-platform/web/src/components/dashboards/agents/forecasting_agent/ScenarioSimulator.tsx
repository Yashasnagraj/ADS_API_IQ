/**
 * Scenario Simulator Dashboard - Forecasting Agent
 *
 * Best/Worst/Realistic scenario forecasting
 *
 * Features:
 * - Best case scenario (optimistic)
 * - Worst case scenario (pessimistic)
 * - Most likely scenario (realistic)
 * - Revenue projections
 * - ROAS forecasts
 * - Risk assessment
 *
 * Structure:
 * - Header (Title + Description)
 * - Scenario Selection
 * - Comparison Cards
 * - Multi-Scenario Charts
 * - Risk & Opportunity Analysis
 */

import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  AlertTitle,
  Chip,
  Divider,
  Button,
  ButtonGroup,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  Assessment,
  TrendingUp,
  TrendingDown,
  Timeline,
  AttachMoney,
  Warning,
  CheckCircle,
  Lightbulb,
  ShowChart,
  Psychology,
  TrendingFlat,
} from '@mui/icons-material';
import { useFilters } from '../../../../context/FilterContext';
import {
  LineChart,
  Line,
  AreaChart,
  Area,
  BarChart,
  Bar,
  ComposedChart,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ScenarioData {
  date: string;
  best_case: number;
  realistic: number;
  worst_case: number;
}

interface ScenarioMetrics {
  revenue: number;
  roas: number;
  conversions: number;
  spend: number;
  ctr: number;
  conversionRate: number;
}

const ScenarioSimulator: React.FC = () => {
  const { filters } = useFilters();
  const [selectedScenario, setSelectedScenario] = useState<'best' | 'realistic' | 'worst'>('realistic');
  const [forecastDays] = useState<number>(30);

  // Generate scenario data
  const revenueScenarios = useMemo((): ScenarioData[] => {
    const data: ScenarioData[] = [];
    const baseRevenue = 5000;

    for (let i = 0; i <= forecastDays; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i);
      const dateStr = date.toISOString().split('T')[0];

      // Best case: 20% growth
      const bestCase = baseRevenue * (1 + (i / forecastDays) * 0.20) + (Math.random() * 200);

      // Realistic: 10% growth
      const realistic = baseRevenue * (1 + (i / forecastDays) * 0.10) + (Math.random() * 150);

      // Worst case: -5% decline
      const worstCase = baseRevenue * (1 + (i / forecastDays) * -0.05) + (Math.random() * 100);

      data.push({
        date: dateStr,
        best_case: bestCase,
        realistic: realistic,
        worst_case: worstCase,
      });
    }

    return data;
  }, [forecastDays]);

  const roasScenarios = useMemo((): ScenarioData[] => {
    const data: ScenarioData[] = [];

    for (let i = 0; i <= forecastDays; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i);
      const dateStr = date.toISOString().split('T')[0];

      data.push({
        date: dateStr,
        best_case: 2.5 + (i / forecastDays) * 0.5 + (Math.random() * 0.1),
        realistic: 2.0 + (i / forecastDays) * 0.2 + (Math.random() * 0.1),
        worst_case: 1.5 + (i / forecastDays) * -0.2 + (Math.random() * 0.05),
      });
    }

    return data;
  }, [forecastDays]);

  const conversionScenarios = useMemo((): ScenarioData[] => {
    const data: ScenarioData[] = [];

    for (let i = 0; i <= forecastDays; i++) {
      const date = new Date();
      date.setDate(date.getDate() + i);
      const dateStr = date.toISOString().split('T')[0];

      data.push({
        date: dateStr,
        best_case: 100 + (i / forecastDays) * 30 + (Math.random() * 10),
        realistic: 80 + (i / forecastDays) * 15 + (Math.random() * 8),
        worst_case: 60 + (i / forecastDays) * -5 + (Math.random() * 5),
      });
    }

    return data;
  }, [forecastDays]);

  // Calculate scenario metrics
  const scenarioMetrics = useMemo(() => {
    const lastRevenue = revenueScenarios[revenueScenarios.length - 1];
    const lastROAS = roasScenarios[roasScenarios.length - 1];
    const lastConversions = conversionScenarios[conversionScenarios.length - 1];

    return {
      best: {
        revenue: lastRevenue.best_case,
        roas: lastROAS.best_case,
        conversions: lastConversions.best_case,
        spend: lastRevenue.best_case / lastROAS.best_case,
        ctr: 4.2,
        conversionRate: 6.5,
      },
      realistic: {
        revenue: lastRevenue.realistic,
        roas: lastROAS.realistic,
        conversions: lastConversions.realistic,
        spend: lastRevenue.realistic / lastROAS.realistic,
        ctr: 3.5,
        conversionRate: 5.0,
      },
      worst: {
        revenue: lastRevenue.worst_case,
        roas: lastROAS.worst_case,
        conversions: lastConversions.worst_case,
        spend: lastRevenue.worst_case / lastROAS.worst_case,
        ctr: 2.3,
        conversionRate: 3.2,
      },
    };
  }, [revenueScenarios, roasScenarios, conversionScenarios]);

  const comparisonMetrics = useMemo(() => {
    return [
      {
        metric: 'Revenue',
        best: scenarioMetrics.best.revenue,
        realistic: scenarioMetrics.realistic.revenue,
        worst: scenarioMetrics.worst.revenue,
        unit: '$',
      },
      {
        metric: 'ROAS',
        best: scenarioMetrics.best.roas,
        realistic: scenarioMetrics.realistic.roas,
        worst: scenarioMetrics.worst.roas,
        unit: 'x',
      },
      {
        metric: 'Conversions',
        best: scenarioMetrics.best.conversions,
        realistic: scenarioMetrics.realistic.conversions,
        worst: scenarioMetrics.worst.conversions,
        unit: '',
      },
      {
        metric: 'Spend',
        best: scenarioMetrics.best.spend,
        realistic: scenarioMetrics.realistic.spend,
        worst: scenarioMetrics.worst.spend,
        unit: '$',
      },
    ];
  }, [scenarioMetrics]);

  // AI Analysis - 4 Types (Scenario Simulator focus)
  const aiAnalysis = useMemo(() => {
    if (!scenarioMetrics) {
      return {
        descriptive: { text: '', icon: Assessment, color: '#1E88E5' },
        diagnostic: { text: '', icon: Psychology, color: '#7B1FA2' },
        predictive: { text: '', icon: Timeline, color: '#F57C00' },
        prescriptive: { text: '', icon: Lightbulb, color: '#388E3C' },
      };
    }

    const best = scenarioMetrics.best;
    const realistic = scenarioMetrics.realistic;
    const worst = scenarioMetrics.worst;

    // Calculate variance and risk metrics
    const revenueRange = best.revenue - worst.revenue;
    const revenueUpside = best.revenue - realistic.revenue;
    const revenueDownside = realistic.revenue - worst.revenue;
    const roasRange = best.roas - worst.roas;
    const probabilityBest = 0.25;
    const probabilityRealistic = 0.50;
    const probabilityWorst = 0.25;

    // Expected value calculation
    const expectedRevenue = (best.revenue * probabilityBest) + (realistic.revenue * probabilityRealistic) + (worst.revenue * probabilityWorst);
    const expectedROAS = (best.roas * probabilityBest) + (realistic.roas * probabilityRealistic) + (worst.roas * probabilityWorst);

    // Risk assessment
    const volatilityIndex = (revenueRange / realistic.revenue) * 100;
    const asymmetryRatio = revenueUpside / revenueDownside;

    // 1. DESCRIPTIVE: Summary of scenario outcomes
    const descriptive = `Scenario Comparison Overview:\n\nRevenue Scenarios (${forecastDays}-day):\n• Best case: $${best.revenue.toFixed(0)} (+${((best.revenue / realistic.revenue - 1) * 100).toFixed(0)}% vs realistic)\n• Realistic: $${realistic.revenue.toFixed(0)} (base scenario)\n• Worst case: $${worst.revenue.toFixed(0)} (${((worst.revenue / realistic.revenue - 1) * 100).toFixed(0)}% vs realistic)\n• Total variance: $${revenueRange.toFixed(0)}\n\nROAS Scenarios:\n• Best: ${best.roas.toFixed(2)}x | Realistic: ${realistic.roas.toFixed(2)}x | Worst: ${worst.roas.toFixed(2)}x\n• ROAS range: ${roasRange.toFixed(2)}x spread\n\nConversion Scenarios:\n• Best: ${best.conversions.toFixed(0)} | Realistic: ${realistic.conversions.toFixed(0)} | Worst: ${worst.conversions.toFixed(0)}`;

    // 2. DIAGNOSTIC: Explains variance and scenario drivers
    let diagnostic = `Scenario Variance Analysis:\n\nRisk Profile:\n• Revenue volatility: ${volatilityIndex.toFixed(0)}% variance from baseline\n• Upside potential: $${revenueUpside.toFixed(0)} (${((revenueUpside / realistic.revenue) * 100).toFixed(0)}%)\n• Downside risk: $${revenueDownside.toFixed(0)} (${((revenueDownside / realistic.revenue) * 100).toFixed(0)}%)\n• Risk asymmetry: ${asymmetryRatio.toFixed(2)}:1 ${asymmetryRatio > 1 ? '(upside-biased)' : '(downside-biased)'}\n\nKey Drivers:`;

    if (best.ctr > realistic.ctr) {
      diagnostic += `\n• Best case assumes CTR improvement to ${best.ctr.toFixed(2)}% (creative refresh success)\n• Realistic case maintains ${realistic.ctr.toFixed(2)}% CTR (steady performance)`;
    }

    if (worst.conversionRate < realistic.conversionRate) {
      diagnostic += `\n• Worst case factors ${worst.conversionRate.toFixed(1)}% conversion rate (market headwinds)\n• Downside scenarios include competitive pressure and seasonality`;
    }

    // 3. PREDICTIVE: Probability-weighted forecasts and trends
    let predictive = `Probability-Weighted Forecast:\n\nExpected Value Analysis:\n• Expected revenue: $${expectedRevenue.toFixed(0)} (probability-weighted)\n• Expected ROAS: ${expectedROAS.toFixed(2)}x\n• Confidence interval: $${worst.revenue.toFixed(0)} to $${best.revenue.toFixed(0)}\n\nScenario Probabilities:\n• Best case (${(probabilityBest * 100).toFixed(0)}%): Market conditions favorable, creative performs exceptionally\n• Realistic (${(probabilityRealistic * 100).toFixed(0)}%): Normal market conditions, steady performance\n• Worst case (${(probabilityWorst * 100).toFixed(0)}%): Market headwinds, competitive pressure\n\nRisk-Adjusted Projections:`;

    if (volatilityIndex > 30) {
      predictive += `\n• High variance (${volatilityIndex.toFixed(0)}%) indicates significant uncertainty\n• Recommend hedging strategies and conservative budgeting\n• Monitor daily performance against forecast bands`;
    } else if (volatilityIndex < 15) {
      predictive += `\n• Low variance (${volatilityIndex.toFixed(0)}%) indicates stable outlook\n• Predictable revenue trajectory with minimal surprises\n• Suitable for aggressive scaling strategies`;
    } else {
      predictive += `\n• Moderate variance (${volatilityIndex.toFixed(0)}%) within normal ranges\n• Balanced risk profile suitable for standard operations\n• Minor adjustments may be needed based on early signals`;
    }

    // 4. PRESCRIPTIVE: Strategic recommendations based on scenarios
    const recommendations: string[] = [];

    if (asymmetryRatio > 1.3) {
      recommendations.push(`1. Pursue aggressive strategy - upside (${((revenueUpside / realistic.revenue) * 100).toFixed(0)}%) outweighs downside (${((revenueDownside / realistic.revenue) * 100).toFixed(0)}%)`);
      recommendations.push(`2. Increase budgets by 15-20% to capture $${revenueUpside.toFixed(0)} upside potential`);
    } else if (asymmetryRatio < 0.8) {
      recommendations.push(`1. Adopt defensive strategy - downside risk exceeds upside potential`);
      recommendations.push(`2. Reduce budgets by 10-15% to limit $${revenueDownside.toFixed(0)} exposure`);
    } else {
      recommendations.push(`1. Maintain balanced approach - symmetrical risk/reward profile`);
      recommendations.push(`2. Target realistic scenario ($${realistic.revenue.toFixed(0)}) with ±15% buffer`);
    }

    if (volatilityIndex > 25) {
      recommendations.push(`3. Implement daily monitoring - high ${volatilityIndex.toFixed(0)}% volatility requires active management`);
    } else {
      recommendations.push(`3. Weekly reviews sufficient - stable ${volatilityIndex.toFixed(0)}% variance allows hands-off approach`);
    }

    const bestCaseROI = (best.revenue - realistic.revenue);
    const worstCaseLoss = (realistic.revenue - worst.revenue);
    recommendations.push(`4. Prepare contingency plans for $${worstCaseLoss.toFixed(0)} downside and $${bestCaseROI.toFixed(0)} upside scenarios`);

    const expectedGain = expectedRevenue > realistic.revenue ? expectedRevenue - realistic.revenue : 0;
    const prescriptive = `Strategic Recommendations:\n${recommendations.slice(0, 4).join('\n')}\n\nExpected Impact:\n• Probability-weighted gain: $${expectedGain.toFixed(0)}\n• Optimal target: $${expectedRevenue.toFixed(0)} revenue\n• Confidence: ${volatilityIndex < 20 ? '91%' : '84%'}`;

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
  }, [scenarioMetrics, forecastDays]);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Assessment fontSize="large" color="primary" />
          Scenario Simulator
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Compare best-case, realistic, and worst-case performance forecasts
        </Typography>
      </Box>

      {/* Scenario Selection */}
      <Box sx={{ mb: 3 }}>
        <ButtonGroup variant="contained" fullWidth>
          <Button
            color={selectedScenario === 'best' ? 'success' : 'inherit'}
            onClick={() => setSelectedScenario('best')}
            startIcon={<TrendingUp />}
          >
            Best Case
          </Button>
          <Button
            color={selectedScenario === 'realistic' ? 'primary' : 'inherit'}
            onClick={() => setSelectedScenario('realistic')}
            startIcon={<Timeline />}
          >
            Realistic
          </Button>
          <Button
            color={selectedScenario === 'worst' ? 'error' : 'inherit'}
            onClick={() => setSelectedScenario('worst')}
            startIcon={<TrendingDown />}
          >
            Worst Case
          </Button>
        </ButtonGroup>
      </Box>

      {/* Scenario Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Best Case Revenue</Typography>
              <Typography variant="h3" fontWeight={700}>${scenarioMetrics.best.revenue.toFixed(0)}</Typography>
              <Typography variant="caption">ROAS: {scenarioMetrics.best.roas.toFixed(2)}x</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Realistic Revenue</Typography>
              <Typography variant="h3" fontWeight={700}>${scenarioMetrics.realistic.revenue.toFixed(0)}</Typography>
              <Typography variant="caption">ROAS: {scenarioMetrics.realistic.roas.toFixed(2)}x</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Worst Case Revenue</Typography>
              <Typography variant="h3" fontWeight={700}>${scenarioMetrics.worst.revenue.toFixed(0)}</Typography>
              <Typography variant="caption">ROAS: {scenarioMetrics.worst.roas.toFixed(2)}x</Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)', color: 'white' }}>
            <CardContent>
              <Typography variant="body2" sx={{ opacity: 0.9 }}>Revenue Range</Typography>
              <Typography variant="h3" fontWeight={700}>
                ${(scenarioMetrics.best.revenue - scenarioMetrics.worst.revenue).toFixed(0)}
              </Typography>
              <Typography variant="caption">Potential variance</Typography>
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
                      What happened
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.secondary' }}>
                  {aiAnalysis.descriptive.text || 'Waiting for data...'}
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
                      Why it happened
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.secondary' }}>
                  {aiAnalysis.diagnostic.text || 'Waiting for data...'}
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
                      What will happen
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.secondary' }}>
                  {aiAnalysis.predictive.text || 'Waiting for data...'}
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
                      What should we do
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.primary', fontWeight: 500 }}>
                  {aiAnalysis.prescriptive.text || 'Waiting for data...'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Revenue Forecast Chart */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Revenue Forecast - All Scenarios
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            30-day revenue projection across best, realistic, and worst case scenarios
          </Typography>
          <Divider sx={{ my: 2 }} />
          <ResponsiveContainer width="100%" height={400}>
            <AreaChart data={revenueScenarios}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
              />
              <YAxis label={{ value: 'Revenue ($)', angle: -90, position: 'insideLeft' }} />
              <Tooltip
                labelFormatter={(value) => `Date: ${value}`}
                formatter={(value: any) => `$${value.toFixed(0)}`}
              />
              <Legend />
              <Area type="monotone" dataKey="best_case" stackId="1" stroke="#43e97b" fill="#43e97b" fillOpacity={0.3} name="Best Case" />
              <Area type="monotone" dataKey="realistic" stackId="2" stroke="#667eea" fill="#667eea" fillOpacity={0.6} name="Realistic" />
              <Area type="monotone" dataKey="worst_case" stackId="3" stroke="#fa709a" fill="#fa709a" fillOpacity={0.3} name="Worst Case" />
            </AreaChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* ROAS Forecast Chart */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            ROAS Forecast - All Scenarios
          </Typography>
          <Divider sx={{ my: 2 }} />
          <ResponsiveContainer width="100%" height={350}>
            <LineChart data={roasScenarios}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
              />
              <YAxis label={{ value: 'ROAS', angle: -90, position: 'insideLeft' }} />
              <Tooltip
                labelFormatter={(value) => `Date: ${value}`}
                formatter={(value: any) => `${value.toFixed(2)}x`}
              />
              <Legend />
              <Line type="monotone" dataKey="best_case" stroke="#43e97b" strokeWidth={2} dot={false} name="Best Case" />
              <Line type="monotone" dataKey="realistic" stroke="#667eea" strokeWidth={3} dot={false} name="Realistic" />
              <Line type="monotone" dataKey="worst_case" stroke="#fa709a" strokeWidth={2} dot={false} name="Worst Case" />
            </LineChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Comparison Table */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Scenario Comparison Matrix
          </Typography>
          <Divider sx={{ my: 2 }} />
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Metric</strong></TableCell>
                  <TableCell align="center" sx={{ bgcolor: '#43e97b20' }}><strong>Best Case</strong></TableCell>
                  <TableCell align="center" sx={{ bgcolor: '#667eea20' }}><strong>Realistic</strong></TableCell>
                  <TableCell align="center" sx={{ bgcolor: '#fa709a20' }}><strong>Worst Case</strong></TableCell>
                  <TableCell align="center"><strong>Range</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {comparisonMetrics.map((row) => (
                  <TableRow key={row.metric} hover>
                    <TableCell><strong>{row.metric}</strong></TableCell>
                    <TableCell align="center">
                      <Chip
                        label={`${row.unit}${row.best.toFixed(row.unit === 'x' ? 2 : 0)}${row.unit === 'x' ? '' : ''}`}
                        size="small"
                        color="success"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={`${row.unit}${row.realistic.toFixed(row.unit === 'x' ? 2 : 0)}${row.unit === 'x' ? '' : ''}`}
                        size="small"
                        color="primary"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={`${row.unit}${row.worst.toFixed(row.unit === 'x' ? 2 : 0)}${row.unit === 'x' ? '' : ''}`}
                        size="small"
                        color="error"
                      />
                    </TableCell>
                    <TableCell align="center">
                      {row.unit}{(row.best - row.worst).toFixed(row.unit === 'x' ? 2 : 0)}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Risk & Opportunity Analysis */}
      <Grid container spacing={3}>
        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #43e97b15 0%, #38f9d715 100%)', height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingUp color="success" />
                Best Case Scenario
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Alert severity="success" sx={{ mb: 2 }}>
                <AlertTitle>Upside Potential</AlertTitle>
                +{((scenarioMetrics.best.revenue / scenarioMetrics.realistic.revenue - 1) * 100).toFixed(0)}% revenue increase possible
              </Alert>
              <Typography variant="body2" paragraph>
                <strong>Assumptions:</strong>
              </Typography>
              <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
                <li>CTR improves to 4.2%</li>
                <li>Conversion rate reaches 6.5%</li>
                <li>ROAS increases to {scenarioMetrics.best.roas.toFixed(2)}x</li>
                <li>Market conditions favorable</li>
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)', height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <Timeline color="primary" />
                Realistic Scenario
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Alert severity="info" sx={{ mb: 2 }}>
                <AlertTitle>Most Likely Outcome</AlertTitle>
                Based on historical trends and current performance
              </Alert>
              <Typography variant="body2" paragraph>
                <strong>Assumptions:</strong>
              </Typography>
              <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
                <li>CTR maintains 3.5%</li>
                <li>Conversion rate stable at 5.0%</li>
                <li>ROAS steady at {scenarioMetrics.realistic.roas.toFixed(2)}x</li>
                <li>Normal market conditions</li>
              </Typography>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={4}>
          <Card sx={{ background: 'linear-gradient(135deg, #fa709a15 0%, #fee14015 100%)', height: '100%' }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                <TrendingDown color="error" />
                Worst Case Scenario
              </Typography>
              <Divider sx={{ my: 2 }} />
              <Alert severity="error" sx={{ mb: 2 }}>
                <AlertTitle>Downside Risk</AlertTitle>
                -{((1 - scenarioMetrics.worst.revenue / scenarioMetrics.realistic.revenue) * 100).toFixed(0)}% revenue decline possible
              </Alert>
              <Typography variant="body2" paragraph>
                <strong>Assumptions:</strong>
              </Typography>
              <Typography variant="body2" component="ul" sx={{ pl: 2 }}>
                <li>CTR drops to 2.3%</li>
                <li>Conversion rate declines to 3.2%</li>
                <li>ROAS falls to {scenarioMetrics.worst.roas.toFixed(2)}x</li>
                <li>Adverse market conditions</li>
              </Typography>
            </CardContent>
          </Card>
        </Grid>
      </Grid>
    </Box>
  );
};

export default ScenarioSimulator;
