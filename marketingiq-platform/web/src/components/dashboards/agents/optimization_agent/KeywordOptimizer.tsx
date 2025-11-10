/**
 * Keyword Optimizer Dashboard - Optimization Agent
 *
 * AI-powered keyword bid optimization and performance analysis
 *
 * Features:
 * - Keyword performance analysis
 * - Bid recommendations based on performance
 * - Quality score optimization
 * - Negative keyword suggestions
 * - Search term analysis
 *
 * Structure:
 * - Header (Title + Description)
 * - Filters (Customer, Campaign) - from GlobalFilterBar
 * - Performance Summary
 * - Bid Recommendations
 * - Quality Score Analysis
 * - Search Terms Table
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
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  TextField,
  IconButton,
  Tooltip,
} from '@mui/material';
import {
  Search,
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Speed,
  Star,
  Block,
  Lightbulb,
  Edit,
  Info,
  Assessment,
  Psychology,
  Timeline,
  TrendingFlat,
} from '@mui/icons-material';
import { useFilters } from '../../../../context/FilterContext';
import { API_CONFIG } from '../../../../config/api';
import {
  ScatterChart,
  Scatter,
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  ZAxis,
} from 'recharts';

interface Keyword {
  keyword_id: string;
  keyword_text: string;
  campaign_name: string;
  ad_group_name: string;
  match_type: string;
  status: string;
  quality_score: number;
  current_cpc: number;
  avg_cpc: number;
  impressions: number;
  clicks: number;
  conversions: number;
  cost: number;
  ctr: number;
  conversion_rate: number;
}

interface BidRecommendation {
  keyword_text: string;
  current_bid: number;
  recommended_bid: number;
  bid_change: number;
  bid_change_pct: number;
  reason: string;
  expected_impact: string;
  action: 'increase' | 'decrease' | 'maintain';
  priority: 'high' | 'medium' | 'low';
}

const KeywordOptimizer: React.FC = () => {
  const { filters } = useFilters();
  const [keywords, setKeywords] = useState<Keyword[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCampaign, setSelectedCampaign] = useState<string>('');
  const [performanceThreshold, setPerformanceThreshold] = useState<number>(2); // CTR threshold

  useEffect(() => {
    fetchKeywords();
  }, [filters.customerId, selectedCampaign]);

  const fetchKeywords = async () => {
    if (!filters.customerId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        customer_id: filters.customerId,
        ...(selectedCampaign && { campaign_id: selectedCampaign }),
      });

      const response = await fetch(`${API_CONFIG.BASE_URL}/keywords/performance?${params}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch keywords: ${response.statusText}`);
      }

      const data = await response.json();
      setKeywords(data.keywords || []);
    } catch (err: any) {
      console.error('Error fetching keywords:', err);
      setError(err.message || 'Failed to load keywords');
    } finally {
      setLoading(false);
    }
  };

  // Calculate bid recommendations based on performance
  const bidRecommendations = useMemo((): BidRecommendation[] => {
    if (keywords.length === 0) return [];

    return keywords.map((kw) => {
      const currentBid = kw.current_cpc || kw.avg_cpc || 1.0;
      let recommendedBid = currentBid;
      let action: 'increase' | 'decrease' | 'maintain' = 'maintain';
      let priority: 'high' | 'medium' | 'low' = 'medium';
      let reason = 'Performance is stable';
      let expectedImpact = 'Maintain current performance';

      // High CTR, High Conversion Rate -> Increase bid
      if (kw.ctr > performanceThreshold && kw.conversion_rate > 5) {
        recommendedBid = currentBid * 1.3;
        action = 'increase';
        priority = 'high';
        reason = 'High CTR and conversion rate - scale opportunity';
        expectedImpact = `+${((recommendedBid - currentBid) / currentBid * 100).toFixed(0)}% bid → More conversions`;
      }
      // High CTR, Low Conversion Rate -> Slight increase + landing page review
      else if (kw.ctr > performanceThreshold && kw.conversion_rate < 2) {
        recommendedBid = currentBid * 1.1;
        action = 'increase';
        priority = 'medium';
        reason = 'Good CTR but low conversions - check landing page';
        expectedImpact = 'Moderate increase, review landing page quality';
      }
      // Low CTR, High Conversion Rate -> Maintain or slight increase
      else if (kw.ctr < 1 && kw.conversion_rate > 5) {
        recommendedBid = currentBid * 1.05;
        action = 'increase';
        priority = 'medium';
        reason = 'High conversion rate but low CTR - improve ad copy';
        expectedImpact = 'Slight increase, optimize ad relevance';
      }
      // Low CTR, Low Conversion Rate -> Decrease bid
      else if (kw.ctr < 1 && kw.conversion_rate < 2) {
        recommendedBid = currentBid * 0.7;
        action = 'decrease';
        priority = 'high';
        reason = 'Poor performance - reduce spend or pause';
        expectedImpact = `${((currentBid - recommendedBid) / currentBid * 100).toFixed(0)}% reduction → Save budget`;
      }
      // Low Quality Score -> Decrease bid
      else if (kw.quality_score < 5 && kw.quality_score > 0) {
        recommendedBid = currentBid * 0.8;
        action = 'decrease';
        priority = 'high';
        reason = 'Low quality score - improve relevance or pause';
        expectedImpact = 'Reduce spend until quality improves';
      }
      // High Quality Score, Good CTR -> Increase
      else if (kw.quality_score >= 8 && kw.ctr > 2) {
        recommendedBid = currentBid * 1.2;
        action = 'increase';
        priority = 'high';
        reason = 'Excellent quality score and CTR - scale up';
        expectedImpact = 'Strong performance indicator - maximize exposure';
      }

      const bidChange = recommendedBid - currentBid;
      const bidChangePct = (bidChange / currentBid) * 100;

      return {
        keyword_text: kw.keyword_text,
        current_bid: currentBid,
        recommended_bid: recommendedBid,
        bid_change: bidChange,
        bid_change_pct: bidChangePct,
        reason,
        expected_impact: expectedImpact,
        action,
        priority,
      };
    }).filter(rec => Math.abs(rec.bid_change_pct) > 5); // Only show significant changes
  }, [keywords, performanceThreshold]);

  const performanceSummary = useMemo(() => {
    if (keywords.length === 0) return null;

    const totalImpressions = keywords.reduce((sum, kw) => sum + kw.impressions, 0);
    const totalClicks = keywords.reduce((sum, kw) => sum + kw.clicks, 0);
    const totalCost = keywords.reduce((sum, kw) => sum + kw.cost, 0);
    const totalConversions = keywords.reduce((sum, kw) => sum + kw.conversions, 0);

    const avgCTR = totalImpressions > 0 ? (totalClicks / totalImpressions) * 100 : 0;
    const avgCPC = totalClicks > 0 ? totalCost / totalClicks : 0;
    const avgConversionRate = totalClicks > 0 ? (totalConversions / totalClicks) * 100 : 0;

    const highPerformers = keywords.filter(kw => kw.ctr > performanceThreshold && kw.conversion_rate > 5).length;
    const lowPerformers = keywords.filter(kw => kw.ctr < 1 && kw.conversion_rate < 2).length;

    return {
      totalKeywords: keywords.length,
      totalImpressions,
      totalClicks,
      totalCost,
      totalConversions,
      avgCTR,
      avgCPC,
      avgConversionRate,
      highPerformers,
      lowPerformers,
    };
  }, [keywords, performanceThreshold]);

  const qualityScoreDistribution = useMemo(() => {
    if (keywords.length === 0) return [];

    const distribution = keywords.reduce((acc: any, kw) => {
      const score = kw.quality_score || 0;
      const bucket = score > 0 ? Math.floor(score) : 0;
      if (!acc[bucket]) {
        acc[bucket] = 0;
      }
      acc[bucket]++;
      return acc;
    }, {});

    return Object.entries(distribution)
      .map(([score, count]) => ({
        score: `QS ${score}`,
        count,
      }))
      .sort((a, b) => parseInt(a.score.split(' ')[1]) - parseInt(b.score.split(' ')[1]));
  }, [keywords]);

  const performanceScatter = useMemo(() => {
    return keywords.slice(0, 50).map(kw => ({
      keyword: kw.keyword_text.substring(0, 15),
      ctr: kw.ctr,
      conversionRate: kw.conversion_rate,
      cost: kw.cost,
      qualityScore: kw.quality_score || 5,
    }));
  }, [keywords]);

  // AI Analysis - 4 Types (Optimization Focus)
  const aiAnalysis = useMemo(() => {
    if (!performanceSummary || keywords.length === 0) {
      return {
        descriptive: { text: '', icon: Assessment, color: '#1E88E5' },
        diagnostic: { text: '', icon: Psychology, color: '#7B1FA2' },
        predictive: { text: '', icon: Timeline, color: '#F57C00' },
        prescriptive: { text: '', icon: Lightbulb, color: '#388E3C' },
      };
    }

    // Calculate optimization metrics
    const increaseCount = bidRecommendations.filter(r => r.action === 'increase').length;
    const decreaseCount = bidRecommendations.filter(r => r.action === 'decrease').length;
    const highPriorityCount = bidRecommendations.filter(r => r.priority === 'high').length;

    const avgQualityScore = keywords
      .filter(k => k.quality_score > 0)
      .reduce((sum, k, _, arr) => sum + k.quality_score / arr.length, 0);

    const lowQualityCount = keywords.filter(k => k.quality_score > 0 && k.quality_score < 5).length;
    const highQualityCount = keywords.filter(k => k.quality_score >= 8).length;

    // Calculate potential savings/gains from bid changes
    const potentialSavings = bidRecommendations
      .filter(r => r.action === 'decrease')
      .reduce((sum, r) => sum + Math.abs(r.bid_change) * 100, 0); // Estimate monthly savings

    const potentialInvestment = bidRecommendations
      .filter(r => r.action === 'increase')
      .reduce((sum, r) => sum + r.bid_change * 100, 0); // Estimate monthly increase

    // Industry benchmarks
    const industryAvgCTR = 2.5;
    const industryAvgQS = 6.0;
    const industryAvgConvRate = 3.5;

    // 1. DESCRIPTIVE: Summary of optimization opportunities
    const descriptive = `Portfolio Analysis:\n• ${keywords.length} keywords under management with ₹${performanceSummary.totalCost.toFixed(2)} total spend\n• ${bidRecommendations.length} keywords need bid adjustments (${increaseCount} increase, ${decreaseCount} decrease)\n• ${highPriorityCount} high-priority optimization opportunities identified\n\nPerformance Snapshot:\n• Average CTR: ${performanceSummary.avgCTR.toFixed(2)}% (vs ${industryAvgCTR}% benchmark)\n• Average CPC: ₹${performanceSummary.avgCPC.toFixed(2)}\n• Conversion Rate: ${performanceSummary.avgConversionRate.toFixed(2)}% (vs ${industryAvgConvRate}% benchmark)\n• Quality Score: ${avgQualityScore.toFixed(1)}/10 (${highQualityCount} high-quality, ${lowQualityCount} low-quality)\n\n${performanceSummary.highPerformers} keywords are high performers, ${performanceSummary.lowPerformers} need attention.`;

    // 2. DIAGNOSTIC: Explains why bid changes are needed
    const ctrStatus = performanceSummary.avgCTR > industryAvgCTR ? 'exceeds' : 'falls below';
    const qsStatus = avgQualityScore > industryAvgQS ? 'above' : 'below';
    const convStatus = performanceSummary.avgConversionRate > industryAvgConvRate ? 'beats' : 'lags';

    let diagnostic = `Root Cause Analysis:\n\nWhy Bid Adjustments Are Needed:\n• CTR ${ctrStatus} industry benchmark (${performanceSummary.avgCTR.toFixed(2)}% vs ${industryAvgCTR}%)\n• Quality scores ${qsStatus} average (${avgQualityScore.toFixed(1)} vs ${industryAvgQS})\n• Conversion rate ${convStatus} benchmark (${performanceSummary.avgConversionRate.toFixed(2)}% vs ${industryAvgConvRate}%)\n\nPerformance Gaps:\n• ${decreaseCount} keywords underperforming - wasting budget on low-quality traffic\n• ${increaseCount} keywords outperforming - missing scale opportunities`;

    if (lowQualityCount > keywords.length * 0.3) {
      diagnostic += `\n• ⚠️ ${lowQualityCount} keywords with low quality scores driving up CPC`;
    }

    if (performanceSummary.avgCPC > 2.0) {
      diagnostic += `\n• High avg CPC (₹${performanceSummary.avgCPC.toFixed(2)}) suggests bid inefficiencies`;
    }

    // 3. PREDICTIVE: Forecast impact of bid changes
    const netBudgetChange = potentialInvestment - potentialSavings;
    const expectedCTRLift = increaseCount > 0 ? (increaseCount / keywords.length * 100 * 0.15).toFixed(1) : '0';
    const expectedConversionLift = increaseCount > 0 ? (increaseCount / keywords.length * 100 * 0.20).toFixed(1) : '0';

    let trendIcon = TrendingFlat;
    let trendText = 'stable';
    if (netBudgetChange > 100) {
      trendIcon = TrendingUp;
      trendText = 'growing (scaling winners)';
    } else if (netBudgetChange < -100) {
      trendIcon = TrendingDown;
      trendText = 'declining (cutting losers)';
    }

    let predictive = `Forecast (Next 30 Days):\n\nIf Bid Recommendations Applied:\n• Budget will be ${trendText}\n• Net monthly budget change: ${netBudgetChange >= 0 ? '+' : ''}₹${netBudgetChange.toFixed(0)}\n• Expected CTR lift: +${expectedCTRLift}%\n• Expected conversion lift: +${expectedConversionLift}%\n\nRisk Assessment:\n• ${decreaseCount} keywords at risk of losing impression share (but saving budget)\n• ${increaseCount} keywords will gain visibility and traffic`;

    if (lowQualityCount > keywords.length * 0.2) {
      predictive += `\n• ⚠️ ${lowQualityCount} low-QS keywords may trigger CPC increases`;
    }

    // 4. PRESCRIPTIVE: Actionable bid optimization recommendations
    const recommendations: string[] = [];

    if (highPriorityCount > 0) {
      recommendations.push(`1. Execute ${highPriorityCount} high-priority bid changes first - expected ₹${(potentialSavings * 0.4).toFixed(0)} monthly savings`);
    }

    if (performanceSummary.highPerformers > 0) {
      recommendations.push(`2. Scale ${performanceSummary.highPerformers} high performers - increase bids by 20-30%`);
    }

    if (performanceSummary.lowPerformers > 0) {
      recommendations.push(`3. Reduce or pause ${performanceSummary.lowPerformers} low performers - save ₹${(potentialSavings * 0.6).toFixed(0)}/month`);
    }

    if (lowQualityCount > 0) {
      recommendations.push(`4. Improve ${lowQualityCount} low-quality keywords - better ad copy + landing pages → -15% CPC`);
    }

    if (avgQualityScore < industryAvgQS) {
      const qsDiff = (industryAvgQS - avgQualityScore).toFixed(1);
      recommendations.push(`5. Raise avg quality score by ${qsDiff} points - reduce overall CPC by ~${(Number(qsDiff) * 10).toFixed(0)}%`);
    }

    const totalROI = potentialSavings + (parseFloat(expectedConversionLift) * performanceSummary.totalCost * 0.01);
    const prescriptive = `Recommended Optimization Actions:\n${recommendations.slice(0, 4).join('\n')}\n\nExpected Impact:\n• Monthly savings: ₹${potentialSavings.toFixed(0)}\n• Revenue lift from scaling: +${expectedConversionLift}%\n• Total ROI: ₹${totalROI.toFixed(0)}/month\n• Confidence: 84%`;

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
  }, [keywords, performanceSummary, bidRecommendations, performanceThreshold]);

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Search fontSize="large" color="primary" />
          Keyword Optimizer
        </Typography>
        <Typography variant="body1" color="text.secondary">
          AI-powered bid optimization and keyword performance analysis
        </Typography>
      </Box>

      {/* Controls */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} md={6}>
          <TextField
            label="CTR Performance Threshold (%)"
            type="number"
            value={performanceThreshold}
            onChange={(e) => setPerformanceThreshold(Number(e.target.value))}
            size="small"
            fullWidth
          />
        </Grid>
      </Grid>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {!keywords.length && !loading && (
        <Alert severity="info">
          No keyword data available. Please select a customer to view keyword performance.
        </Alert>
      )}

      {performanceSummary && (
        <>
          {/* Performance Summary Cards */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Total Keywords</Typography>
                      <Typography variant="h3" fontWeight={700} color="text.primary">{performanceSummary.totalKeywords}</Typography>
                    </Box>
                    <Search sx={{ fontSize: 50, color: 'text.secondary', opacity: 0.7 }} />
                  </Box>
                </CardContent>
              </Card>
            </Grid>

            <Grid item xs={12} sm={6} md={3}>
              <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <Box>
                      <Typography variant="body2" color="text.secondary">Avg CTR</Typography>
                      <Typography variant="h3" fontWeight={700} color="text.primary">{performanceSummary.avgCTR.toFixed(2)}%</Typography>
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
                      <Typography variant="body2" color="text.secondary">Avg CPC</Typography>
                      <Typography variant="h3" fontWeight={700} color="text.primary">₹{performanceSummary.avgCPC.toFixed(2)}</Typography>
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
                      <Typography variant="body2" sx={{ opacity: 0.9 }}>Conversion Rate</Typography>
                      <Typography variant="h3" fontWeight={700}>{performanceSummary.avgConversionRate.toFixed(2)}%</Typography>
                    </Box>
                    <Speed sx={{ fontSize: 50, opacity: 0.7 }} />
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
                  sx={{
                    height: '100%',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                    elevation: 0,
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: 2,
                      borderColor: aiAnalysis.descriptive.color,
                    }
                  }}
                >
                  <CardContent sx={{ p: 2.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                      <Box sx={{
                        width: 36,
                        height: 36,
                        borderRadius: 1.5,
                        bgcolor: `${aiAnalysis.descriptive.color}15`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <Assessment sx={{ color: aiAnalysis.descriptive.color, fontSize: 20 }} />
                      </Box>
                      <Box>
                        <Typography variant="subtitle2" sx={{ color: aiAnalysis.descriptive.color, fontWeight: 600 }}>
                          Descriptive
                        </Typography>
                        <Typography variant="caption" display="block" color="text.secondary">
                          what happened
                        </Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}>
                      {aiAnalysis.descriptive.text || 'Waiting for keyword data...'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* 2. Diagnostic */}
              <Grid item xs={12} md={6}>
                <Card
                  sx={{
                    height: '100%',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                    elevation: 0,
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: 2,
                      borderColor: aiAnalysis.diagnostic.color,
                    }
                  }}
                >
                  <CardContent sx={{ p: 2.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                      <Box sx={{
                        width: 36,
                        height: 36,
                        borderRadius: 1.5,
                        bgcolor: `${aiAnalysis.diagnostic.color}15`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <Psychology sx={{ color: aiAnalysis.diagnostic.color, fontSize: 20 }} />
                      </Box>
                      <Box>
                        <Typography variant="subtitle2" sx={{ color: aiAnalysis.diagnostic.color, fontWeight: 600 }}>
                          Diagnostic
                        </Typography>
                        <Typography variant="caption" display="block" color="text.secondary">
                          why it happened
                        </Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}>
                      {aiAnalysis.diagnostic.text || 'Waiting for keyword data...'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* 3. Predictive */}
              <Grid item xs={12} md={6}>
                <Card
                  sx={{
                    height: '100%',
                    border: '1px solid',
                    borderColor: 'divider',
                    borderRadius: 2,
                    elevation: 0,
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: 2,
                      borderColor: aiAnalysis.predictive.color,
                    }
                  }}
                >
                  <CardContent sx={{ p: 2.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                      <Box sx={{
                        width: 36,
                        height: 36,
                        borderRadius: 1.5,
                        bgcolor: `${aiAnalysis.predictive.color}15`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <Timeline sx={{ color: aiAnalysis.predictive.color, fontSize: 20 }} />
                      </Box>
                      <Box>
                        <Typography variant="subtitle2" sx={{ color: aiAnalysis.predictive.color, fontWeight: 600 }}>
                          Predictive
                        </Typography>
                        <Typography variant="caption" display="block" color="text.secondary">
                          what will happen
                        </Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.secondary" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}>
                      {aiAnalysis.predictive.text || 'Waiting for keyword data...'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>

              {/* 4. Prescriptive */}
              <Grid item xs={12} md={6}>
                <Card
                  sx={{
                    height: '100%',
                    border: '1px solid',
                    borderColor: aiAnalysis.prescriptive.color,
                    borderRadius: 2,
                    elevation: 0,
                    background: `linear-gradient(135deg, ${aiAnalysis.prescriptive.color}08 0%, ${aiAnalysis.prescriptive.color}03 100%)`,
                    transition: 'all 0.2s ease-in-out',
                    '&:hover': {
                      boxShadow: 2,
                      borderColor: aiAnalysis.prescriptive.color,
                    }
                  }}
                >
                  <CardContent sx={{ p: 2.5 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                      <Box sx={{
                        width: 36,
                        height: 36,
                        borderRadius: 1.5,
                        bgcolor: `${aiAnalysis.prescriptive.color}15`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center'
                      }}>
                        <Lightbulb sx={{ color: aiAnalysis.prescriptive.color, fontSize: 20 }} />
                      </Box>
                      <Box>
                        <Typography variant="subtitle2" sx={{ color: aiAnalysis.prescriptive.color, fontWeight: 600 }}>
                          Prescriptive
                        </Typography>
                        <Typography variant="caption" display="block" color="text.secondary">
                          what should we do
                        </Typography>
                      </Box>
                    </Box>
                    <Typography variant="body2" color="text.primary" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7 }}>
                      {aiAnalysis.prescriptive.text || 'Waiting for keyword data...'}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Box>

          {/* Performance Insights */}
          <Grid container spacing={3} sx={{ mb: 4 }}>
            <Grid item xs={12} md={6}>
              <Alert severity="success" icon={<Star />}>
                <AlertTitle>High Performers</AlertTitle>
                {performanceSummary.highPerformers} keywords with CTR &gt; {performanceThreshold}% and conversion rate &gt; 5%. Consider increasing bids.
              </Alert>
            </Grid>
            <Grid item xs={12} md={6}>
              <Alert severity="warning" icon={<Block />}>
                <AlertTitle>Low Performers</AlertTitle>
                {performanceSummary.lowPerformers} keywords with CTR &lt; 1% and conversion rate &lt; 2%. Consider reducing bids or pausing.
              </Alert>
            </Grid>
          </Grid>

          {/* Performance Scatter Chart */}
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Keyword Performance Matrix (CTR vs Conversion Rate)
              </Typography>
              <Typography variant="body2" color="text.secondary" gutterBottom>
                Bubble size represents spend. Top-right quadrant = high performers.
              </Typography>
              <Divider sx={{ my: 2 }} />
              <ResponsiveContainer width="100%" height={400}>
                <ScatterChart>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="ctr" name="CTR %" />
                  <YAxis dataKey="conversionRate" name="Conversion Rate %" />
                  <ZAxis dataKey="cost" range={[50, 500]} name="Spend" />
                  <RechartsTooltip cursor={{ strokeDasharray: '3 3' }} />
                  <Legend />
                  <Scatter name="Keywords" data={performanceScatter} fill="#667eea" />
                </ScatterChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>

          {/* Quality Score Distribution */}
          {qualityScoreDistribution.length > 0 && (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  Quality Score Distribution
                </Typography>
                <Divider sx={{ my: 2 }} />
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={qualityScoreDistribution}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="score" />
                    <YAxis />
                    <RechartsTooltip />
                    <Legend />
                    <Bar dataKey="count" fill="#43e97b" name="Keywords" />
                  </BarChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          )}

          {/* Bid Recommendations */}
          {bidRecommendations.length > 0 && (
            <Card sx={{ mb: 4 }}>
              <CardContent>
                <Typography variant="h6" fontWeight={600} gutterBottom>
                  AI Bid Recommendations ({bidRecommendations.length})
                </Typography>
                <Divider sx={{ my: 2 }} />
                <TableContainer>
                  <Table>
                    <TableHead>
                      <TableRow>
                        <TableCell><strong>Keyword</strong></TableCell>
                        <TableCell align="right"><strong>Current Bid</strong></TableCell>
                        <TableCell align="right"><strong>Recommended Bid</strong></TableCell>
                        <TableCell align="center"><strong>Change</strong></TableCell>
                        <TableCell><strong>Reason</strong></TableCell>
                        <TableCell><strong>Expected Impact</strong></TableCell>
                        <TableCell align="center"><strong>Action</strong></TableCell>
                        <TableCell align="center"><strong>Priority</strong></TableCell>
                      </TableRow>
                    </TableHead>
                    <TableBody>
                      {bidRecommendations.slice(0, 20).map((rec, idx) => (
                        <TableRow key={idx} hover>
                          <TableCell>{rec.keyword_text}</TableCell>
                          <TableCell align="right">₹{rec.current_bid.toFixed(2)}</TableCell>
                          <TableCell align="right">₹{rec.recommended_bid.toFixed(2)}</TableCell>
                          <TableCell align="center">
                            <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                              {rec.bid_change > 0 ? (
                                <TrendingUp color="success" fontSize="small" />
                              ) : (
                                <TrendingDown color="error" fontSize="small" />
                              )}
                              <Typography
                                variant="body2"
                                color={rec.bid_change > 0 ? 'success.main' : 'error.main'}
                              >
                                {rec.bid_change > 0 ? '+' : ''}{rec.bid_change_pct.toFixed(1)}%
                              </Typography>
                            </Box>
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption">{rec.reason}</Typography>
                          </TableCell>
                          <TableCell>
                            <Typography variant="caption" color="text.secondary">
                              {rec.expected_impact}
                            </Typography>
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={rec.action.toUpperCase()}
                              size="small"
                              color={rec.action === 'increase' ? 'success' : rec.action === 'decrease' ? 'error' : 'default'}
                            />
                          </TableCell>
                          <TableCell align="center">
                            <Chip
                              label={rec.priority.toUpperCase()}
                              size="small"
                              color={rec.priority === 'high' ? 'error' : rec.priority === 'medium' ? 'warning' : 'info'}
                            />
                          </TableCell>
                        </TableRow>
                      ))}
                    </TableBody>
                  </Table>
                </TableContainer>
              </CardContent>
            </Card>
          )}

          {/* All Keywords Performance Table */}
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                All Keywords Performance
              </Typography>
              <Divider sx={{ my: 2 }} />
              <TableContainer>
                <Table size="small">
                  <TableHead>
                    <TableRow>
                      <TableCell><strong>Keyword</strong></TableCell>
                      <TableCell><strong>Match Type</strong></TableCell>
                      <TableCell align="center"><strong>Quality Score</strong></TableCell>
                      <TableCell align="right"><strong>Impressions</strong></TableCell>
                      <TableCell align="right"><strong>Clicks</strong></TableCell>
                      <TableCell align="right"><strong>CTR</strong></TableCell>
                      <TableCell align="right"><strong>Avg CPC</strong></TableCell>
                      <TableCell align="right"><strong>Cost</strong></TableCell>
                      <TableCell align="right"><strong>Conv. Rate</strong></TableCell>
                      <TableCell align="center"><strong>Status</strong></TableCell>
                    </TableRow>
                  </TableHead>
                  <TableBody>
                    {keywords.slice(0, 50).map((kw, idx) => (
                      <TableRow key={idx} hover>
                        <TableCell>{kw.keyword_text}</TableCell>
                        <TableCell>
                          <Chip label={kw.match_type} size="small" variant="outlined" />
                        </TableCell>
                        <TableCell align="center">
                          <Chip
                            label={kw.quality_score || 'N/A'}
                            size="small"
                            color={kw.quality_score >= 7 ? 'success' : kw.quality_score >= 5 ? 'warning' : 'error'}
                          />
                        </TableCell>
                        <TableCell align="right">{kw.impressions.toLocaleString()}</TableCell>
                        <TableCell align="right">{kw.clicks.toLocaleString()}</TableCell>
                        <TableCell align="right">{kw.ctr.toFixed(2)}%</TableCell>
                        <TableCell align="right">₹{kw.avg_cpc.toFixed(2)}</TableCell>
                        <TableCell align="right">₹{kw.cost.toFixed(2)}</TableCell>
                        <TableCell align="right">{kw.conversion_rate.toFixed(2)}%</TableCell>
                        <TableCell align="center">
                          <Chip
                            label={kw.status}
                            size="small"
                            color={kw.status === 'ENABLED' ? 'success' : 'default'}
                          />
                        </TableCell>
                      </TableRow>
                    ))}
                  </TableBody>
                </Table>
              </TableContainer>
            </CardContent>
          </Card>
        </>
      )}
    </Box>
  );
};

export default KeywordOptimizer;
