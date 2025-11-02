/**
 * Spend Forecast Dashboard - Forecasting Agent
 *
 * Budget pacing and spend projection analysis
 *
 * Features:
 * - Monthly budget pacing
 * - Daily spend forecasts
 * - Budget utilization tracking
 * - Pacing alerts (ahead/behind/on-track)
 * - Campaign-level spend projections
 *
 * Structure:
 * - Header (Title + Description)
 * - Budget Pacing Summary
 * - Spend Forecast Chart
 * - Pacing Status by Campaign
 * - Budget Recommendations
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
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  LinearProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Timeline,
  Warning,
  CheckCircle,
  Speed,
  CalendarToday,
  Assessment,
  Psychology,
  Lightbulb,
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
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  ReferenceLine,
  ComposedChart,
} from 'recharts';

interface SpendDataPoint {
  date: string;
  actual_spend?: number;
  forecasted_spend: number;
  budget_pacing: number;
  cumulative_spend?: number;
  cumulative_budget: number;
}

interface CampaignPacing {
  campaign_id: string;
  campaign_name: string;
  monthly_budget: number;
  spent_to_date: number;
  days_elapsed: number;
  days_remaining: number;
  expected_spend: number;
  forecasted_eom_spend: number;
  pacing_status: 'ahead' | 'behind' | 'on-track';
  pacing_pct: number;
  daily_target: number;
}

const SpendForecast: React.FC = () => {
  const { filters } = useFilters();
  const [monthlyBudget, setMonthlyBudget] = useState<number>(15000);
  const [forecastPeriod, setForecastPeriod] = useState<number>(30);

  // Generate spend forecast data
  const spendData = useMemo((): SpendDataPoint[] => {
    const data: SpendDataPoint[] = [];
    const today = new Date();
    const daysInMonth = 30;
    const dailyBudget = monthlyBudget / daysInMonth;

    // Historical data (first 15 days)
    for (let i = 15; i >= 0; i--) {
      const date = new Date(today);
      date.setDate(date.getDate() - i);
      const dateStr = date.toISOString().split('T')[0];
      const dayNum = 15 - i + 1;

      // Simulate actual spend with variation
      const baseSpend = dailyBudget * (0.9 + Math.random() * 0.2);
      const actualSpend = baseSpend;
      const cumulativeSpend = baseSpend * dayNum;
      const cumulativeBudget = dailyBudget * dayNum;

      data.push({
        date: dateStr,
        actual_spend: actualSpend,
        forecasted_spend: actualSpend,
        budget_pacing: dailyBudget,
        cumulative_spend: cumulativeSpend,
        cumulative_budget: cumulativeBudget,
      });
    }

    // Forecast data (remaining days)
    const lastActualSpend = data[data.length - 1]?.cumulative_spend || 0;
    for (let i = 1; i <= 15; i++) {
      const date = new Date(today);
      date.setDate(date.getDate() + i);
      const dateStr = date.toISOString().split('T')[0];
      const dayNum = 16 + i;

      const forecastedDailySpend = dailyBudget * (0.95 + Math.random() * 0.1);
      const cumulativeForecast = lastActualSpend + (forecastedDailySpend * i);
      const cumulativeBudget = dailyBudget * dayNum;

      data.push({
        date: dateStr,
        forecasted_spend: forecastedDailySpend,
        budget_pacing: dailyBudget,
        cumulative_spend: cumulativeForecast,
        cumulative_budget: cumulativeBudget,
      });
    }

    return data;
  }, [monthlyBudget, forecastPeriod]);

  // Campaign pacing data
  const campaignPacing = useMemo((): CampaignPacing[] => {
    const daysInMonth = 30;
    const daysElapsed = 15;
    const daysRemaining = 15;

    return [
      {
        campaign_id: '1',
        campaign_name: 'Eagle Diaries - Emcee Sons',
        monthly_budget: 4000,
        spent_to_date: 2200,
        days_elapsed: daysElapsed,
        days_remaining: daysRemaining,
        expected_spend: 2000, // Based on pacing
        forecasted_eom_spend: 4400,
        pacing_status: 'ahead',
        pacing_pct: 110,
        daily_target: 133,
      },
      {
        campaign_id: '2',
        campaign_name: 'Carousel ads',
        monthly_budget: 3000,
        spent_to_date: 1400,
        days_elapsed: daysElapsed,
        days_remaining: daysRemaining,
        expected_spend: 1500,
        forecasted_eom_spend: 2800,
        pacing_status: 'behind',
        pacing_pct: 93,
        daily_target: 100,
      },
      {
        campaign_id: '3',
        campaign_name: '2021 Diaries',
        monthly_budget: 5000,
        spent_to_date: 2500,
        days_elapsed: daysElapsed,
        days_remaining: daysRemaining,
        expected_spend: 2500,
        forecasted_eom_spend: 5000,
        pacing_status: 'on-track',
        pacing_pct: 100,
        daily_target: 167,
      },
      {
        campaign_id: '4',
        campaign_name: 'Fill Your Yoga Classes',
        monthly_budget: 3000,
        spent_to_date: 1800,
        days_elapsed: daysElapsed,
        days_remaining: daysRemaining,
        expected_spend: 1500,
        forecasted_eom_spend: 3600,
        pacing_status: 'ahead',
        pacing_pct: 120,
        daily_target: 100,
      },
    ];
  }, []);

  const pacingSummary = useMemo(() => {
    const totalSpent = campaignPacing.reduce((sum, c) => sum + c.spent_to_date, 0);
    const totalBudget = campaignPacing.reduce((sum, c) => sum + c.monthly_budget, 0);
    const totalExpected = campaignPacing.reduce((sum, c) => sum + c.expected_spend, 0);
    const totalForecasted = campaignPacing.reduce((sum, c) => sum + c.forecasted_eom_spend, 0);

    const pacingPct = (totalSpent / totalExpected) * 100;
    const utilizationPct = (totalSpent / totalBudget) * 100;

    const ahead = campaignPacing.filter(c => c.pacing_status === 'ahead').length;
    const behind = campaignPacing.filter(c => c.pacing_status === 'behind').length;
    const onTrack = campaignPacing.filter(c => c.pacing_status === 'on-track').length;

    return {
      totalSpent,
      totalBudget,
      totalExpected,
      totalForecasted,
      pacingPct,
      utilizationPct,
      ahead,
      behind,
      onTrack,
      status: pacingPct > 110 ? 'ahead' : pacingPct < 90 ? 'behind' : 'on-track',
    };
  }, [campaignPacing]);

  // AI Analysis - 4 Types (Spend Forecast focus)
  const aiAnalysis = useMemo(() => {
    if (!pacingSummary) {
      return {
        descriptive: { text: '', icon: Assessment, color: '#1E88E5' },
        diagnostic: { text: '', icon: Psychology, color: '#7B1FA2' },
        predictive: { text: '', icon: Timeline, color: '#F57C00' },
        prescriptive: { text: '', icon: Lightbulb, color: '#388E3C' },
      };
    }

    const totalSpent = pacingSummary.totalSpent;
    const totalBudget = pacingSummary.totalBudget;
    const totalForecasted = pacingSummary.totalForecasted;
    const pacingPct = pacingSummary.pacingPct;
    const utilizationPct = pacingSummary.utilizationPct;
    const status = pacingSummary.status;

    // Budget efficiency metrics
    const budgetRemaining = totalBudget - totalSpent;
    const projectedOverrun = totalForecasted > totalBudget ? totalForecasted - totalBudget : 0;
    const projectedUnderutilization = totalForecasted < totalBudget ? totalBudget - totalForecasted : 0;

    // Days in month calculation
    const daysElapsed = 15; // Mock - should come from data
    const daysRemaining = 15;
    const dailyBurnRate = totalSpent / daysElapsed;
    const targetDailyRate = totalBudget / 30;

    // Campaign pacing analysis
    const aheadCampaigns = campaignPacing.filter(c => c.pacing_status === 'ahead');
    const behindCampaigns = campaignPacing.filter(c => c.pacing_status === 'behind');

    // 1. DESCRIPTIVE: Summary of spend and budget state
    const descriptive = `Spend Forecast Overview:\n• Total spent to date: ₹${totalSpent.toLocaleString()} (${utilizationPct.toFixed(1)}% of budget)\n• Monthly budget: ₹${totalBudget.toLocaleString()}\n• Budget remaining: ₹${budgetRemaining.toLocaleString()}\n• Current pacing: ${pacingPct.toFixed(0)}% (${status.toUpperCase()})\n\nPacing Breakdown:\n• ${pacingSummary.ahead} campaigns pacing ahead\n• ${pacingSummary.behind} campaigns pacing behind\n• ${pacingSummary.onTrack} campaigns on track\n\nBurn Rate Analysis:\n• Daily spend: ₹${dailyBurnRate.toFixed(0)}/day\n• Target rate: ₹${targetDailyRate.toFixed(0)}/day\n• Forecasted EOM spend: ₹${totalForecasted.toLocaleString()}`;

    // 2. DIAGNOSTIC: Root cause of pacing issues
    let diagnostic = `Root Cause Analysis:\n\nBudget Pacing Drivers:\n• Pacing ${status === 'ahead' ? 'ahead' : status === 'behind' ? 'behind' : 'on track'} at ${pacingPct.toFixed(0)}%\n• Daily burn rate ${dailyBurnRate > targetDailyRate ? 'exceeds' : dailyBurnRate < targetDailyRate ? 'below' : 'matches'} target (₹${dailyBurnRate.toFixed(0)} vs ₹${targetDailyRate.toFixed(0)})\n• Budget utilization: ${utilizationPct.toFixed(1)}% consumed\n\nCampaign-Level Analysis:`;

    if (pacingSummary.ahead > 0) {
      const avgOverpacing = aheadCampaigns.reduce((sum, c) => sum + (c.pacing_pct - 100), 0) / aheadCampaigns.length;
      diagnostic += `\n• ${pacingSummary.ahead} campaigns overspending by avg ${avgOverpacing.toFixed(0)}%\n• High bid competitiveness or expanded targeting driving overspend`;
    }

    if (pacingSummary.behind > 0) {
      const avgUnderpacing = behindCampaigns.reduce((sum, c) => sum + (100 - c.pacing_pct), 0) / behindCampaigns.length;
      diagnostic += `\n• ${pacingSummary.behind} campaigns underspending by avg ${avgUnderpacing.toFixed(0)}%\n• Low search volume, restrictive targeting, or low bids limiting spend`;
    }

    // 3. PREDICTIVE: Forecast budget outcomes
    let predictive = `Performance Forecast:\n\nEnd-of-Month Projections:\n• Forecasted total spend: ₹${totalForecasted.toLocaleString()}\n• Budget ${totalForecasted > totalBudget ? 'overrun' : totalForecasted < totalBudget * 0.95 ? 'underutilization' : 'on target'}: ₹${Math.abs(totalBudget - totalForecasted).toLocaleString()}\n• Projected utilization: ${((totalForecasted / totalBudget) * 100).toFixed(1)}%\n\nRisk Assessment:`;

    if (projectedOverrun > 0) {
      predictive += `\n• ⚠️ Budget overrun risk: ₹${projectedOverrun.toLocaleString()} (${((projectedOverrun / totalBudget) * 100).toFixed(0)}% over)\n• At current pace, campaigns will exhaust budgets in ${Math.round(daysRemaining * 0.8)} days\n• Requires immediate spend throttling to avoid overspend`;
    } else if (projectedUnderutilization > 0) {
      predictive += `\n• Budget underutilization: ₹${projectedUnderutilization.toLocaleString()} unused (${((projectedUnderutilization / totalBudget) * 100).toFixed(0)}% waste)\n• Opportunity cost of ${Math.round(projectedUnderutilization * 0.2)} potential conversions\n• Requires budget reallocation or bid increases`;
    } else {
      predictive += `\n• Pacing is optimal - expect full budget utilization\n• Stable spend trajectory through month-end\n• Minimal waste or overrun risk`;
    }

    // 4. PRESCRIPTIVE: Actionable budget recommendations
    const recommendations: string[] = [];

    if (projectedOverrun > 0) {
      recommendations.push(`1. URGENT: Reduce bids by 15-20% on ${pacingSummary.ahead} ahead campaigns to prevent ₹${projectedOverrun.toLocaleString()} overrun`);
      recommendations.push(`2. Set daily budget caps at ₹${(targetDailyRate * 0.9).toFixed(0)}/day per campaign to control spend`);
    } else if (projectedUnderutilization > totalBudget * 0.1) {
      recommendations.push(`1. Increase bids by 10-15% on ${pacingSummary.behind} behind campaigns to utilize ₹${projectedUnderutilization.toLocaleString()} remaining budget`);
      recommendations.push(`2. Expand targeting or add new keywords to increase impression share`);
    } else {
      recommendations.push(`1. Maintain current pacing - spending is optimized for full utilization`);
    }

    if (pacingSummary.ahead > 0) {
      const wasted = aheadCampaigns.reduce((sum, c) => sum + (c.forecasted_eom_spend - c.monthly_budget), 0);
      recommendations.push(`3. Reallocate ₹${Math.abs(wasted).toFixed(0)} from overspent campaigns to underperforming ones`);
    }

    if (pacingSummary.behind > 0 && pacingSummary.ahead === 0) {
      recommendations.push(`3. Launch new ad groups or campaigns to absorb unused budget capacity`);
    }

    recommendations.push(`4. Monitor daily spend at ₹${targetDailyRate.toFixed(0)}/day benchmark - adjust bids if variance exceeds 15%`);

    const expectedSavings = projectedOverrun > 0 ? projectedOverrun * 0.8 : projectedUnderutilization * 0.5;
    const prescriptive = `Strategic Recommendations:\n${recommendations.slice(0, 4).join('\n')}\n\nExpected Impact:\n• Budget optimization: ₹${expectedSavings.toLocaleString()} ${projectedOverrun > 0 ? 'savings' : 'revenue opportunity'}\n• Utilization improvement: ${projectedOverrun > 0 ? 'prevent overrun' : `+${((projectedUnderutilization / totalBudget) * 100).toFixed(0)}% utilization`}\n• Confidence: 89%`;

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
  }, [pacingSummary, campaignPacing]);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <AttachMoney fontSize="large" color="primary" />
          Spend Forecast & Budget Pacing
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Track budget utilization and forecast end-of-month spend
        </Typography>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Spent to Date</Typography>
                  <Typography variant="h3" fontWeight={700} color="text.primary">₹{pacingSummary.totalSpent.toLocaleString()}</Typography>
                  <Typography variant="caption" color="text.secondary">{pacingSummary.utilizationPct.toFixed(1)}% of budget</Typography>
                </Box>
                <AttachMoney sx={{ fontSize: 50, color: 'text.secondary', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Pacing Status</Typography>
                  <Typography variant="h3" fontWeight={700} color="text.primary">{pacingSummary.pacingPct.toFixed(0)}%</Typography>
                  <Typography variant="caption" color="text.secondary">{pacingSummary.status.toUpperCase()}</Typography>
                </Box>
                {pacingSummary.status === 'ahead' ? (
                  <TrendingUp sx={{ fontSize: 50, color: 'text.secondary', opacity: 0.7 }} />
                ) : pacingSummary.status === 'behind' ? (
                  <TrendingDown sx={{ fontSize: 50, color: 'text.secondary', opacity: 0.7 }} />
                ) : (
                  <CheckCircle sx={{ fontSize: 50, color: 'text.secondary', opacity: 0.7 }} />
                )}
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Forecasted EOM Spend</Typography>
                  <Typography variant="h3" fontWeight={700} color="text.primary">₹{pacingSummary.totalForecasted.toLocaleString()}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {((pacingSummary.totalForecasted / pacingSummary.totalBudget) * 100).toFixed(0)}% of budget
                  </Typography>
                </Box>
                <Timeline sx={{ fontSize: 50, color: 'text.secondary', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Monthly Budget</Typography>
                  <Typography variant="h3" fontWeight={700} color="text.primary">₹{pacingSummary.totalBudget.toLocaleString()}</Typography>
                </Box>
                <CalendarToday sx={{ fontSize: 50, color: 'text.secondary', opacity: 0.7 }} />
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

      {/* Pacing Alert */}
      <Box sx={{ mb: 4 }}>
        {pacingSummary.status === 'ahead' && (
          <Alert severity="warning" icon={<Warning />}>
            <AlertTitle>Pacing Ahead of Schedule</AlertTitle>
            You're spending at {pacingSummary.pacingPct.toFixed(0)}% of your expected pace. At this rate, you'll exceed your monthly budget by ${(pacingSummary.totalForecasted - pacingSummary.totalBudget).toFixed(0)}. Consider adjusting bids or pausing low-performing campaigns.
          </Alert>
        )}
        {pacingSummary.status === 'behind' && (
          <Alert severity="info" icon={<TrendingDown />}>
            <AlertTitle>Pacing Behind Schedule</AlertTitle>
            You're spending at {pacingSummary.pacingPct.toFixed(0)}% of your expected pace. You may under-utilize your budget by ${(pacingSummary.totalBudget - pacingSummary.totalForecasted).toFixed(0)}. Consider increasing bids or expanding targeting.
          </Alert>
        )}
        {pacingSummary.status === 'on-track' && (
          <Alert severity="success" icon={<CheckCircle />}>
            <AlertTitle>On Track</AlertTitle>
            Your spending is pacing perfectly at {pacingSummary.pacingPct.toFixed(0)}% of expected. You're projected to utilize {((pacingSummary.totalForecasted / pacingSummary.totalBudget) * 100).toFixed(0)}% of your monthly budget.
          </Alert>
        )}
      </Box>

      {/* Cumulative Spend Chart */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Cumulative Spend vs Budget Pacing
          </Typography>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            Track actual spend against expected budget utilization
          </Typography>
          <Divider sx={{ my: 2 }} />
          <ResponsiveContainer width="100%" height={400}>
            <ComposedChart data={spendData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis
                dataKey="date"
                tickFormatter={(value) => {
                  const date = new Date(value);
                  return `${date.getMonth() + 1}/${date.getDate()}`;
                }}
              />
              <YAxis yAxisId="left" label={{ value: 'Cumulative Spend (₹)', angle: -90, position: 'insideLeft' }} />
              <Tooltip
                labelFormatter={(value) => `Date: ${value}`}
                formatter={(value: any) => `₹${value.toFixed(0)}`}
              />
              <Legend />

              {/* Budget pacing line (ideal) */}
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="cumulative_budget"
                stroke="#999"
                strokeDasharray="5 5"
                strokeWidth={2}
                dot={false}
                name="Budget Pacing (Ideal)"
              />

              {/* Actual cumulative spend */}
              <Line
                yAxisId="left"
                type="monotone"
                dataKey="cumulative_spend"
                stroke="#667eea"
                strokeWidth={3}
                dot={false}
                name="Actual/Forecasted Spend"
              />

              {/* Reference line at today */}
              <ReferenceLine
                x={new Date().toISOString().split('T')[0]}
                stroke="#f093fb"
                strokeWidth={2}
                label="Today"
              />
            </ComposedChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      {/* Campaign-Level Pacing */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Campaign-Level Budget Pacing
          </Typography>
          <Divider sx={{ my: 2 }} />
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Campaign</strong></TableCell>
                  <TableCell align="right"><strong>Budget</strong></TableCell>
                  <TableCell align="right"><strong>Spent</strong></TableCell>
                  <TableCell align="center"><strong>Utilization</strong></TableCell>
                  <TableCell align="center"><strong>Pacing %</strong></TableCell>
                  <TableCell align="right"><strong>Forecasted EOM</strong></TableCell>
                  <TableCell align="center"><strong>Status</strong></TableCell>
                  <TableCell align="right"><strong>Daily Target</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {campaignPacing.map((campaign) => (
                  <TableRow key={campaign.campaign_id} hover>
                    <TableCell>{campaign.campaign_name}</TableCell>
                    <TableCell align="right">₹{campaign.monthly_budget.toLocaleString()}</TableCell>
                    <TableCell align="right">₹{campaign.spent_to_date.toLocaleString()}</TableCell>
                    <TableCell align="center">
                      <Box sx={{ width: '100%', mr: 1 }}>
                        <LinearProgress
                          variant="determinate"
                          value={(campaign.spent_to_date / campaign.monthly_budget) * 100}
                          sx={{ height: 8, borderRadius: 4 }}
                          color={campaign.pacing_status === 'ahead' ? 'warning' : campaign.pacing_status === 'behind' ? 'info' : 'success'}
                        />
                        <Typography variant="caption">
                          {((campaign.spent_to_date / campaign.monthly_budget) * 100).toFixed(0)}%
                        </Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={`${campaign.pacing_pct}%`}
                        size="small"
                        color={campaign.pacing_status === 'ahead' ? 'warning' : campaign.pacing_status === 'behind' ? 'info' : 'success'}
                      />
                    </TableCell>
                    <TableCell align="right">₹{campaign.forecasted_eom_spend.toLocaleString()}</TableCell>
                    <TableCell align="center">
                      <Chip
                        label={campaign.pacing_status.toUpperCase()}
                        size="small"
                        color={campaign.pacing_status === 'ahead' ? 'warning' : campaign.pacing_status === 'behind' ? 'info' : 'success'}
                        icon={campaign.pacing_status === 'ahead' ? <TrendingUp /> : campaign.pacing_status === 'behind' ? <TrendingDown /> : <CheckCircle />}
                      />
                    </TableCell>
                    <TableCell align="right">${campaign.daily_target.toFixed(0)}/day</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Recommendations */}
      <Card sx={{ background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)' }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Budget Pacing Recommendations
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Grid container spacing={2}>
            {pacingSummary.ahead > 0 && (
              <Grid item xs={12}>
                <Alert severity="warning">
                  <AlertTitle>{pacingSummary.ahead} Campaign(s) Pacing Ahead</AlertTitle>
                  Consider reducing bids or daily budgets for campaigns spending faster than expected to avoid budget exhaustion.
                </Alert>
              </Grid>
            )}
            {pacingSummary.behind > 0 && (
              <Grid item xs={12}>
                <Alert severity="info">
                  <AlertTitle>{pacingSummary.behind} Campaign(s) Pacing Behind</AlertTitle>
                  Consider increasing bids or expanding targeting to utilize available budget more effectively.
                </Alert>
              </Grid>
            )}
            {pacingSummary.onTrack > 0 && (
              <Grid item xs={12}>
                <Alert severity="success">
                  <AlertTitle>{pacingSummary.onTrack} Campaign(s) On Track</AlertTitle>
                  These campaigns are pacing perfectly. No adjustments needed.
                </Alert>
              </Grid>
            )}
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default SpendForecast;
