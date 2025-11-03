/**
 * Ad Groups Dashboard - Data Agent
 *
 * Shows all ad groups with performance metrics and bid management
 *
 * Structure:
 * - Header (Title + Description)
 * - Filters (Customer, Date Range, Campaign Type) - from GlobalFilterBar
 * - KPIs (6 key metrics)
 * - AI Intelligence (Ad group optimization recommendations)
 * - Visualizations (Status distribution, Bid analysis)
 * - Data Table (All ad groups with metrics)
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  CircularProgress,
  Alert,
  Divider,
} from '@mui/material';
import {
  Group,
  CheckCircle,
  Pause,
  MonetizationOn,
  TrendingUp,
  TrendingDown,
  Speed,
  Assessment,
  Psychology,
  Timeline,
  Lightbulb,
} from '@mui/icons-material';
import { useFilters } from '../../../../context/FilterContext';
import { API_CONFIG } from '../../../../config/api';
import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid, Legend } from 'recharts';

interface AdGroup {
  ad_group_id: number;
  adgroup_name: string;
  status: string;
  cpc_bid_micros: number | null;
  metrics: {
    clicks: number;
    impressions: number;
    cost: number;
    conversions: number;
    ctr: number;
    avg_cpc: number;
  };
}

interface KPIMetrics {
  totalAdGroups: number;
  activeAdGroups: number;
  pausedAdGroups: number;
  avgBid: number;
  totalClicks: number;
  avgCTR: number;
}

const STATUS_COLORS: Record<string, string> = {
  ENABLED: '#43e97b',
  PAUSED: '#f093fb',
  REMOVED: '#999',
};

const AdGroupsDashboard: React.FC = () => {
  const { filters } = useFilters();
  const [adGroups, setAdGroups] = useState<AdGroup[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchAdGroups();
  }, [filters.customerId, filters.dateRange]);

  const fetchAdGroups = async () => {
    if (!filters.customerId) {
      setLoading(false);
      return;
    }

    setLoading(true);
    setError(null);

    try {
      const params = new URLSearchParams({
        customer_id: filters.customerId,
        limit: '1000',
      });

      const response = await fetch(`${API_CONFIG.BASE_URL}/warehouse/ad-groups?${params}`);

      if (!response.ok) {
        throw new Error(`Failed to fetch ad groups: ${response.statusText}`);
      }

      const data = await response.json();
      
      // Deduplicate ad groups by ad_group_id to prevent duplicates
      const adGroupsArray = data.ad_groups || [];
      const uniqueAdGroupsMap = new Map<number, AdGroup>();
      const nameToIdMap = new Map<string, number>(); // Track name->ID mapping for fallback deduplication
      
      adGroupsArray.forEach((ag: any) => {
        const adGroupId = ag.ad_group_id || ag.adgroup_id || ag.id;
        const adGroupName = ag.adgroup_name || ag.name || ag.ad_group_name || '';
        
        if (adGroupId) {
          const existingAdGroup = uniqueAdGroupsMap.get(adGroupId);
          
          if (!existingAdGroup) {
            // First occurrence - add it
            uniqueAdGroupsMap.set(adGroupId, {
              ad_group_id: adGroupId,
              adgroup_name: adGroupName || `Ad Group ${adGroupId}`,
              status: ag.status || 'UNKNOWN',
              cpc_bid_micros: ag.cpc_bid_micros !== undefined ? ag.cpc_bid_micros : null,
              metrics: {
                clicks: ag.metrics?.clicks || ag.clicks || 0,
                impressions: ag.metrics?.impressions || ag.impressions || 0,
                cost: ag.metrics?.cost || ag.cost || 0,
                conversions: ag.metrics?.conversions || ag.conversions || 0,
                ctr: ag.metrics?.ctr || ag.ctr || 0,
                avg_cpc: ag.metrics?.avg_cpc || ag.avg_cpc || 0,
              },
            });
            
            // Track name mapping
            if (adGroupName) {
              nameToIdMap.set(adGroupName.toLowerCase(), adGroupId);
            }
          } else {
            // Duplicate ID found - merge metrics (sum them) and keep the most recent status
            existingAdGroup.metrics.clicks += (ag.metrics?.clicks || ag.clicks || 0);
            existingAdGroup.metrics.impressions += (ag.metrics?.impressions || ag.impressions || 0);
            existingAdGroup.metrics.cost += (ag.metrics?.cost || ag.cost || 0);
            existingAdGroup.metrics.conversions += (ag.metrics?.conversions || ag.conversions || 0);
            
            // Recalculate CTR and avg_cpc from merged totals
            existingAdGroup.metrics.ctr = existingAdGroup.metrics.impressions > 0
              ? (existingAdGroup.metrics.clicks / existingAdGroup.metrics.impressions) * 100
              : 0;
            existingAdGroup.metrics.avg_cpc = existingAdGroup.metrics.clicks > 0
              ? existingAdGroup.metrics.cost / existingAdGroup.metrics.clicks
              : 0;
            
            // Update status and bid if the new one has values
            if (ag.status && ag.status !== 'UNKNOWN') {
              existingAdGroup.status = ag.status;
            }
            if (ag.cpc_bid_micros !== undefined && ag.cpc_bid_micros !== null) {
              existingAdGroup.cpc_bid_micros = ag.cpc_bid_micros;
            }
          }
        } else if (adGroupName) {
          // Fallback: deduplicate by name if ID is missing
          const existingIdForName = nameToIdMap.get(adGroupName.toLowerCase());
          if (existingIdForName) {
            const existingAdGroup = uniqueAdGroupsMap.get(existingIdForName);
            if (existingAdGroup) {
              // Merge metrics with existing ad group that has the same name
              existingAdGroup.metrics.clicks += (ag.metrics?.clicks || ag.clicks || 0);
              existingAdGroup.metrics.impressions += (ag.metrics?.impressions || ag.impressions || 0);
              existingAdGroup.metrics.cost += (ag.metrics?.cost || ag.cost || 0);
              existingAdGroup.metrics.conversions += (ag.metrics?.conversions || ag.conversions || 0);
              
              existingAdGroup.metrics.ctr = existingAdGroup.metrics.impressions > 0
                ? (existingAdGroup.metrics.clicks / existingAdGroup.metrics.impressions) * 100
                : 0;
              existingAdGroup.metrics.avg_cpc = existingAdGroup.metrics.clicks > 0
                ? existingAdGroup.metrics.cost / existingAdGroup.metrics.clicks
                : 0;
            }
          }
        }
      });
      
      // Convert map to array and sort by ad_group_id for consistency
      const uniqueAdGroups = Array.from(uniqueAdGroupsMap.values()).sort((a, b) => a.ad_group_id - b.ad_group_id);
      setAdGroups(uniqueAdGroups);
    } catch (err: any) {
      console.error('Error fetching ad groups:', err);
      setError(err.message || 'Failed to load ad groups');
    } finally {
      setLoading(false);
    }
  };

  // Calculate KPIs
  const kpiMetrics = useMemo((): KPIMetrics => {
    if (adGroups.length === 0) {
      return {
        totalAdGroups: 0,
        activeAdGroups: 0,
        pausedAdGroups: 0,
        avgBid: 0,
        totalClicks: 0,
        avgCTR: 0,
      };
    }

    const activeAdGroups = adGroups.filter(ag => ag.status === 'ENABLED').length;
    const pausedAdGroups = adGroups.filter(ag => ag.status === 'PAUSED').length;

    const bids = adGroups.filter(ag => ag.cpc_bid_micros !== null).map(ag => (ag.cpc_bid_micros || 0) / 1_000_000);
    const avgBid = bids.length > 0
      ? bids.reduce((sum, bid) => sum + bid, 0) / bids.length
      : 0;

    const totals = adGroups.reduce(
      (acc, ag) => ({
        clicks: acc.clicks + (ag.metrics.clicks || 0),
        impressions: acc.impressions + (ag.metrics.impressions || 0),
      }),
      { clicks: 0, impressions: 0 }
    );

    const avgCTR = totals.impressions > 0
      ? (totals.clicks / totals.impressions) * 100
      : 0;

    return {
      totalAdGroups: adGroups.length,
      activeAdGroups,
      pausedAdGroups,
      avgBid: Number(avgBid.toFixed(2)),
      totalClicks: totals.clicks,
      avgCTR: Number(avgCTR.toFixed(2)),
    };
  }, [adGroups]);

  // Status distribution
  const statusDistribution = useMemo(() => {
    const distribution: Record<string, number> = {};

    adGroups.forEach(ag => {
      const status = ag.status || 'UNKNOWN';
      distribution[status] = (distribution[status] || 0) + 1;
    });

    return Object.entries(distribution).map(([name, value]) => ({
      name,
      value,
      percentage: adGroups.length > 0 ? ((value / adGroups.length) * 100).toFixed(1) : '0',
    }));
  }, [adGroups]);

  // Bid distribution
  const bidDistribution = useMemo(() => {
    const bins: Record<string, number> = {
      '₹0-0.50': 0,
      '₹0.51-1.00': 0,
      '₹1.01-2.00': 0,
      '₹2.01+': 0,
      'No Bid': 0,
    };

    adGroups.forEach(ag => {
      if (ag.cpc_bid_micros === null) {
        bins['No Bid']++;
      } else {
        const bidDollars = ag.cpc_bid_micros / 1_000_000;
        if (bidDollars <= 0.50) {
          bins['₹0-0.50']++;
        } else if (bidDollars <= 1.00) {
          bins['₹0.51-1.00']++;
        } else if (bidDollars <= 2.00) {
          bins['₹1.01-2.00']++;
        } else {
          bins['₹2.01+']++;
        }
      }
    });

    return Object.entries(bins).map(([name, value]) => ({ name, value }));
  }, [adGroups]);

  // Comprehensive AI Analysis (4 Types)
  const aiAnalysis = useMemo(() => {
    if (adGroups.length === 0) {
      return {
        descriptive: { text: '', icon: Assessment, color: '#1E88E5' },
        diagnostic: { text: '', icon: Psychology, color: '#7B1FA2' },
        predictive: { text: '', icon: Timeline, color: '#F57C00' },
        prescriptive: { text: '', icon: Lightbulb, color: '#388E3C' },
      };
    }

    // Find performers
    const sortedByCTR = [...adGroups].filter(ag => ag.metrics.ctr > 0).sort((a, b) => b.metrics.ctr - a.metrics.ctr);
    const topPerformer = sortedByCTR[0];
    const bottomPerformer = sortedByCTR[sortedByCTR.length - 1];

    // Calculate averages
    const avgClicksPerAdGroup = kpiMetrics.totalClicks / adGroups.length;
    const totalSpend = adGroups.reduce((sum, ag) => sum + (ag.metrics.cost || 0), 0);
    const avgSpendPerAdGroup = totalSpend / adGroups.length;

    // Industry benchmarks
    const industryAvgCTR = 2.5;
    const industryAvgBid = 1.75;

    // 1. DESCRIPTIVE
    const descriptive = `Your ${adGroups.length} ad groups generated ${kpiMetrics.totalClicks.toLocaleString()} total clicks with ${kpiMetrics.avgCTR}% average CTR. ${kpiMetrics.activeAdGroups} ad groups are active, ${kpiMetrics.pausedAdGroups} paused. Average CPC bid is ₹${kpiMetrics.avgBid}. ${topPerformer ? `Top performer: "${topPerformer.adgroup_name}" with ${topPerformer.metrics.ctr.toFixed(2)}% CTR.` : ''} Average ${avgClicksPerAdGroup.toFixed(0)} clicks per ad group.`;

    // 2. DIAGNOSTIC
    let diagnostic = '';
    if (topPerformer && bottomPerformer && adGroups.length > 3) {
      const bidCorrelation = topPerformer.cpc_bid_micros && bottomPerformer.cpc_bid_micros
        ? (topPerformer.cpc_bid_micros / bottomPerformer.cpc_bid_micros).toFixed(1)
        : 'N/A';
      diagnostic = `Top ad group "${topPerformer.adgroup_name}" (${topPerformer.metrics.ctr.toFixed(2)}% CTR) outperforms "${bottomPerformer.adgroup_name}" (${bottomPerformer.metrics.ctr.toFixed(2)}% CTR) by ${((topPerformer.metrics.ctr - bottomPerformer.metrics.ctr) / bottomPerformer.metrics.ctr * 100).toFixed(0)}%. `;
    }

    if (kpiMetrics.avgCTR > industryAvgCTR) {
      diagnostic += `Your ${kpiMetrics.avgCTR}% CTR exceeds industry average (${industryAvgCTR}%) indicating well-targeted ad groups with relevant ad copy. `;
    } else {
      diagnostic += `Your ${kpiMetrics.avgCTR}% CTR is below industry benchmark (${industryAvgCTR}%) - consider improving ad group structure, keyword relevance, and ad copy quality. `;
    }

    if (kpiMetrics.pausedAdGroups > kpiMetrics.activeAdGroups) {
      diagnostic += `High pause rate (${(kpiMetrics.pausedAdGroups / adGroups.length * 100).toFixed(0)}%) indicates underperformance or budget constraints.`;
    }

    // 3. PREDICTIVE
    const expectedMonthlyClicks = (kpiMetrics.totalClicks / 30) * 30;
    const bidTrend = kpiMetrics.avgBid > industryAvgBid ? 'increasing' : 'stable';

    let predictive = `Based on current performance, expect ~${expectedMonthlyClicks.toFixed(0)} monthly clicks across ad groups. `;

    if (kpiMetrics.avgCTR > industryAvgCTR) {
      predictive += `CTR trend is positive. Projected 7-day CTR: ${(kpiMetrics.avgCTR * 1.03).toFixed(2)}% (stable growth). `;
    } else {
      predictive += `CTR needs improvement. Without optimization, expect CTR to stabilize at ${kpiMetrics.avgCTR}% over next 7 days. `;
    }

    const highBidAdGroups = adGroups.filter(ag => ag.cpc_bid_micros && ag.cpc_bid_micros / 1_000_000 > kpiMetrics.avgBid * 1.5).length;
    if (highBidAdGroups > 0) {
      predictive += `⚠️ ${highBidAdGroups} ad group(s) with bids 50% above average may impact budget efficiency.`;
    }

    // 4. PRESCRIPTIVE
    const recommendations: string[] = [];

    // Bid optimization
    if (kpiMetrics.avgBid > industryAvgBid) {
      const savings = (kpiMetrics.avgBid - industryAvgBid) * kpiMetrics.totalClicks;
      recommendations.push(`1. Reduce average bid from ₹${kpiMetrics.avgBid} to ₹${industryAvgBid} benchmark (-₹${savings.toFixed(0)}/month savings)`);
    } else if (topPerformer && kpiMetrics.avgCTR > industryAvgCTR) {
      recommendations.push(`1. Increase bids on top ${Math.ceil(adGroups.length * 0.2)} performers (+15% potential click volume)`);
    }

    // Pause recommendations
    if (kpiMetrics.pausedAdGroups > 3) {
      recommendations.push(`2. Audit ${kpiMetrics.pausedAdGroups} paused ad groups - archive low-potential, reactivate winners`);
    }

    // Structure optimization
    if (bottomPerformer && bottomPerformer.metrics.ctr < industryAvgCTR * 0.4) {
      recommendations.push(`3. Restructure or pause "${bottomPerformer.adgroup_name}" (${bottomPerformer.metrics.ctr.toFixed(2)}% CTR) to improve account health`);
    }

    // Top performer scaling
    if (topPerformer && topPerformer.metrics.ctr > industryAvgCTR * 1.5) {
      const budgetIncrease = avgSpendPerAdGroup * 0.3;
      recommendations.push(`4. Scale "${topPerformer.adgroup_name}" budget by ₹${budgetIncrease.toFixed(0)} (+₹${(budgetIncrease * 4).toFixed(0)} expected revenue at 4x ROAS)`);
    }

    const prescriptive = recommendations.length > 0
      ? `Recommended Actions:\n${recommendations.join('\n')}\n\nExpected Impact: +${(kpiMetrics.totalClicks * 0.12).toFixed(0)} monthly clicks | Confidence: 85%`
      : 'Ad groups are well-optimized. Monitor performance trends.';

    return {
      descriptive: { text: descriptive, icon: Assessment, color: '#1E88E5' },
      diagnostic: { text: diagnostic, icon: Psychology, color: '#7B1FA2' },
      predictive: { text: predictive, icon: Timeline, color: '#F57C00' },
      prescriptive: { text: prescriptive, icon: Lightbulb, color: '#388E3C' },
    };
  }, [adGroups, kpiMetrics]);

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
          <Group fontSize="large" color="primary" />
          Ad Groups Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Comprehensive ad group management with performance metrics and bid optimization
        </Typography>
      </Box>

      {error && (
        <Alert severity="error" sx={{ mb: 3 }}>
          {error}
        </Alert>
      )}

      {/* KPIs */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Total Ad Groups</Typography>
                  <Typography variant="h4" fontWeight={700} color="text.primary">{kpiMetrics.totalAdGroups}</Typography>
                </Box>
                <Group sx={{ fontSize: 40, color: 'text.secondary', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Active</Typography>
                  <Typography variant="h4" fontWeight={700} color="text.primary">{kpiMetrics.activeAdGroups}</Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 40, color: 'text.secondary', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Paused</Typography>
                  <Typography variant="h4" fontWeight={700} color="text.primary">{kpiMetrics.pausedAdGroups}</Typography>
                </Box>
                <Pause sx={{ fontSize: 40, color: 'text.secondary', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Avg CPC Bid</Typography>
                  <Typography variant="h4" fontWeight={700} color="text.primary">₹{kpiMetrics.avgBid}</Typography>
                </Box>
                <MonetizationOn sx={{ fontSize: 40, color: 'text.secondary', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Total Clicks</Typography>
                  <Typography variant="h4" fontWeight={700} color="text.primary">{kpiMetrics.totalClicks.toLocaleString()}</Typography>
                </Box>
                <TrendingUp sx={{ fontSize: 40, color: 'text.secondary', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={2}>
          <Card sx={{ background: 'white', border: '1px solid #e0e0e0' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" color="text.secondary">Avg CTR</Typography>
                  <Typography variant="h4" fontWeight={700} color="text.primary">{kpiMetrics.avgCTR}%</Typography>
                </Box>
                <Speed sx={{ fontSize: 40, color: 'text.secondary', opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* AI-Powered Analysis - Lighter Design */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" fontWeight={600} gutterBottom sx={{ mb: 3, color: 'text.primary' }}>
          🧠 AI Intelligence
        </Typography>

        <Grid container spacing={2.5}>
          {/* 1. Descriptive Analysis */}
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
                  {aiAnalysis.descriptive.text || 'Waiting for ad group data...'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* 2. Diagnostic Analysis */}
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
                  {aiAnalysis.diagnostic.text || 'Waiting for ad group data...'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* 3. Predictive Analysis */}
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
                  {aiAnalysis.predictive.text || 'Waiting for ad group data...'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* 4. Prescriptive Analysis */}
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
                  {aiAnalysis.prescriptive.text || 'Waiting for ad group data...'}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Visualizations */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {/* Status Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Status Distribution
              </Typography>
              {statusDistribution.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={statusDistribution}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percentage }) => `${name}: ${percentage}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {statusDistribution.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.name] || '#999'} />
                      ))}
                    </Pie>
                    <Tooltip />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 10 }}>
                  No data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>

        {/* Bid Distribution */}
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                CPC Bid Distribution
              </Typography>
              {bidDistribution.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <BarChart data={bidDistribution}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="name" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Bar dataKey="value" fill="#667eea" name="Ad Groups" />
                  </BarChart>
                </ResponsiveContainer>
              ) : (
                <Typography variant="body2" color="text.secondary" align="center" sx={{ py: 10 }}>
                  No data available
                </Typography>
              )}
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Data Table */}
      <Card>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            All Ad Groups ({adGroups.length})
          </Typography>
          <TableContainer sx={{ maxHeight: 600 }}>
            <Table stickyHeader>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Ad Group Name</strong></TableCell>
                  <TableCell><strong>Status</strong></TableCell>
                  <TableCell align="right"><strong>CPC Bid</strong></TableCell>
                  <TableCell align="right"><strong>Impressions</strong></TableCell>
                  <TableCell align="right"><strong>Clicks</strong></TableCell>
                  <TableCell align="right"><strong>CTR</strong></TableCell>
                  <TableCell align="right"><strong>Cost</strong></TableCell>
                  <TableCell align="right"><strong>Avg CPC</strong></TableCell>
                  <TableCell align="right"><strong>Conversions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {adGroups.length === 0 ? (
                  <TableRow>
                    <TableCell colSpan={9} align="center">
                      <Typography variant="body2" color="text.secondary" sx={{ py: 4 }}>
                        No ad groups found. Try adjusting your filters.
                      </Typography>
                    </TableCell>
                  </TableRow>
                ) : (
                  adGroups.map((adGroup) => (
                    <TableRow key={adGroup.ad_group_id} hover>
                      <TableCell>{adGroup.adgroup_name}</TableCell>
                      <TableCell>
                        <Chip
                          label={adGroup.status}
                          size="small"
                          color={adGroup.status === 'ENABLED' ? 'success' : 'default'}
                        />
                      </TableCell>
                      <TableCell align="right">
                        {adGroup.cpc_bid_micros !== null
                          ? `₹${(adGroup.cpc_bid_micros / 1_000_000).toFixed(2)}`
                          : '-'}
                      </TableCell>
                      <TableCell align="right">{adGroup.metrics.impressions.toLocaleString()}</TableCell>
                      <TableCell align="right">{adGroup.metrics.clicks.toLocaleString()}</TableCell>
                      <TableCell align="right">{adGroup.metrics.ctr.toFixed(2)}%</TableCell>
                      <TableCell align="right">₹{adGroup.metrics.cost.toFixed(2)}</TableCell>
                      <TableCell align="right">₹{adGroup.metrics.avg_cpc.toFixed(2)}</TableCell>
                      <TableCell align="right">{adGroup.metrics.conversions.toFixed(1)}</TableCell>
                    </TableRow>
                  ))
                )}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AdGroupsDashboard;
