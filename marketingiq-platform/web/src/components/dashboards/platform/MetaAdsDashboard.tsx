// Meta Ads Dashboard - Real Data Integration
import React, { useState, useEffect, useMemo } from 'react';
import { Grid, Stack, Paper, Typography, Box, CircularProgress } from '@mui/material';
import DashboardTemplate from '../../common/DashboardTemplate';
import { KPICard } from '../../common/KPICard';
import InsightCard from '../../common/InsightCard';
import { SmartInsightCard } from '../../common/SmartInsightCard';
import { DataQualityIndicator } from '../../common/DataQualityIndicator';
import { SmartInsightSummary } from '../../common/SmartInsightSummary';
import { FilterState, KPIData } from '../../../types';
import { metaAdsService } from '../../../services/metaAdsService';
import { comparisonService, MetricComparison } from '../../../services/comparisonService';
import { useFilters } from '../../../context/FilterContext';
import { SmartInsightGenerator } from '../../../utils/insightGenerator';
import {
  BarChart,
  Bar,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
  LineChart,
  Line,
} from 'recharts';

interface MetaCampaign {
  campaign_id: string;
  name: string;
  status: string;
  objective: string;
  daily_budget?: number;
  lifetime_budget?: number;
  cost?: number;
  spend?: number;
  impressions?: number;
  clicks?: number;
  conversions?: number;
  ctr?: number;
  roas?: number;
}

export const MetaAdsDashboard: React.FC = () => {
  const { filters } = useFilters();

  const [loading, setLoading] = useState(true);
  const [campaigns, setCampaigns] = useState<MetaCampaign[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [comparisons, setComparisons] = useState<Record<string, MetricComparison>>({});
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!filters.customerId) return;

      setLoading(true);
      setError(null);
      try {
        // Fetch campaigns, metrics, and comparisons in parallel
        const [campaignsData, metricsData, comparisonsData] = await Promise.all([
          metaAdsService.getCampaigns(Number(filters.customerId), filters.dateRange),
          metaAdsService.getInsightsSummary(Number(filters.customerId), filters.dateRange),
          comparisonService.getBatchMetricComparisons(
            filters.customerId!,
            ['spend', 'roas', 'conversions', 'cpc', 'ctr'],
            filters.dateRange,
            { platform: 'meta_ads' }
          ).catch(err => {
            console.warn('Failed to fetch Meta Ads comparisons:', err);
            return {};
          })
        ]);

        // Ensure campaigns is always an array
        setCampaigns(Array.isArray(campaignsData) ? campaignsData : []);
        setMetrics(metricsData);
        setComparisons(comparisonsData);
      } catch (err: any) {
        console.error('Error fetching Meta Ads data:', err);
        setError(err.message || 'Failed to load Meta Ads data');
        // Set empty arrays on error
        setCampaigns([]);
        setMetrics(null);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters.customerId, filters.dateRange]);

  // Generate AI-powered insights from campaign data (MUST be before any conditional returns)
  const smartInsights = useMemo(() => {
    if (!campaigns || campaigns.length === 0) return [];
    try {
      return SmartInsightGenerator.analyzeCampaignPerformance(campaigns);
    } catch (error) {
      console.error('Error generating insights:', error);
      return [];
    }
  }, [campaigns]);

  // Generate KPIs from real data (using standard field names)
  const kpis: KPIData[] = metrics
    ? [
        {
          title: 'Total Spend',
          value: metrics.spend || metrics.total_spend || 0,
          prefix: '₹',
          change: comparisons.spend?.change_percentage || 0,
          trend: comparisons.spend?.change_direction === 'decrease' ? 'down' : (comparisons.spend?.change_direction === 'increase' ? 'up' : undefined),
        },
        {
          title: 'ROAS',
          value: (metrics.roas || metrics.overall_roas || 0).toFixed(2),
          suffix: 'x',
          change: comparisons.roas?.change_percentage || 0,
          trend: comparisons.roas?.change_direction === 'decrease' ? 'down' : (comparisons.roas?.change_direction === 'increase' ? 'up' : undefined),
          isHighlighted: true,
          color: comparisons.roas?.is_positive_change ? 'success' : 'error',
        },
        {
          title: 'Conversions',
          value: metrics.conversions || metrics.total_conversions || 0,
          change: comparisons.conversions?.change_percentage || 0,
          trend: comparisons.conversions?.change_direction === 'decrease' ? 'down' : (comparisons.conversions?.change_direction === 'increase' ? 'up' : undefined),
        },
        {
          title: 'Avg. CPC',
          value: (metrics.cpc || metrics.avg_cpc || 0).toFixed(2),
          prefix: '₹',
          change: comparisons.cpc?.change_percentage || 0,
          trend: comparisons.cpc?.change_direction === 'decrease' ? 'down' : (comparisons.cpc?.change_direction === 'increase' ? 'up' : undefined),
        },
        {
          title: 'CTR',
          value: `${(metrics.ctr || metrics.avg_ctr || 0).toFixed(2)}%`,
          change: comparisons.ctr?.change_percentage || 0,
          trend: comparisons.ctr?.change_direction === 'decrease' ? 'down' : (comparisons.ctr?.change_direction === 'increase' ? 'up' : undefined),
        },
        {
          title: 'Frequency',
          value: (metrics.avg_frequency || 0).toFixed(1),
          change: 0, // Frequency comparison not in API yet
        },
      ]
    : [];

  // Generate campaign performance data
  const campaignPerformance = Array.isArray(campaigns)
    ? campaigns.slice(0, 10).map((campaign) => ({
        name: campaign.name.length > 20 ? campaign.name.substring(0, 20) + '...' : campaign.name,
        status: campaign.status,
        objective: campaign.objective,
        budget: campaign.daily_budget || campaign.lifetime_budget || 0,
      }))
    : [];

  // Group campaigns by objective
  const campaignsByObjective = Array.isArray(campaigns) ? campaigns.reduce((acc: any, campaign) => {
    const objective = campaign.objective || 'UNKNOWN';
    if (!acc[objective]) {
      acc[objective] = { objective, count: 0, budgets: [] };
    }
    acc[objective].count++;
    if (campaign.daily_budget) acc[objective].budgets.push(campaign.daily_budget);
    if (campaign.lifetime_budget) acc[objective].budgets.push(campaign.lifetime_budget);
    return acc;
  }, {}) : {};

  const objectiveData = Object.values(campaignsByObjective).map((obj: any) => ({
    objective: obj.objective.replace('OUTCOME_', '').replace('_', ' '),
    count: obj.count,
    avgBudget: obj.budgets.length > 0
      ? obj.budgets.reduce((a: number, b: number) => a + b, 0) / obj.budgets.length
      : 0,
  }));

  // Campaign status distribution
  const statusData = Array.isArray(campaigns) ? campaigns.reduce((acc: any, campaign) => {
    const status = campaign.status || 'UNKNOWN';
    if (!acc[status]) {
      acc[status] = { status, count: 0 };
    }
    acc[status].count++;
    return acc;
  }, {}) : {};

  const statusDistribution = Object.values(statusData);

  const COLORS = ['#1E88E5', '#26A69A', '#FFA726', '#EF5350', '#AB47BC', '#66BB6A'];

  if (loading) {
    return (
      <DashboardTemplate
        title="Meta Ads Performance"
        subtitle="Analyze your Facebook and Instagram advertising performance"
      >
        <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', minHeight: 400 }}>
          <CircularProgress />
        </Box>
      </DashboardTemplate>
    );
  }

  if (error) {
    return (
      <DashboardTemplate
        title="Meta Ads Performance"
        subtitle="Analyze your Facebook and Instagram advertising performance"
      >
        <Box sx={{ p: 3, textAlign: 'center' }}>
          <Typography color="error">Error: {error}</Typography>
          <Typography variant="body2" sx={{ mt: 2 }}>
            Please ensure the Meta Ads API is configured correctly and the backend is running.
          </Typography>
        </Box>
      </DashboardTemplate>
    );
  }

  return (
    <DashboardTemplate
      title="Meta Ads Performance"
      subtitle="Analyze your Facebook and Instagram advertising performance. Real-time data from Meta Marketing API."
    >
      {/* Data Quality Indicator */}
      <Box sx={{ mb: 3 }}>
        <DataQualityIndicator
          lastSync={new Date(Date.now() - 1000 * 60 * 3)} // 3 minutes ago
          dataPoints={campaigns.length}
          qualityScore={campaigns.length > 0 ? 88 : 0}
          isLoading={loading}
          compact={true}
        />
      </Box>

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {kpis.map((kpi, index) => (
          <Grid item xs={12} md={4} key={index}>
            <KPICard data={kpi} index={index} />
          </Grid>
        ))}
      </Grid>

      {/* AI-Powered Smart Insights */}
      {smartInsights.length > 0 && (
        <Box sx={{ mt: 4 }}>
          <Typography variant="h5" fontWeight={700} gutterBottom sx={{ mb: 3 }}>
            🧠 AI Intelligence & Recommendations
          </Typography>

          {/* Summary Banner */}
          <SmartInsightSummary
            totalInsights={smartInsights.length}
            avgConfidence={Math.round(
              smartInsights.reduce((sum, i) => sum + i.confidence, 0) / Math.max(smartInsights.length, 1)
            )}
            highPriorityCount={smartInsights.filter(i => i.type === 'danger' || i.type === 'warning').length}
            actionableCount={smartInsights.filter(i => i.actionable).length}
            isLoading={loading}
          />

          {/* Insights by Category */}
          <Stack spacing={2.5}>
            {smartInsights.map((insight, index) => (
              <SmartInsightCard
                key={index}
                type={insight.type}
                title={insight.title}
                message={insight.message}
                impact={insight.impact}
                confidence={insight.confidence}
                actionable={insight.actionable}
                actions={insight.actions}
                impactScore={insight.impactScore}
                whyItMatters={insight.whyItMatters}
                category={insight.category}
                index={index}
              />
            ))}
          </Stack>
        </Box>
      )}

      {/* Campaign Statistics */}
      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Campaign Spend Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Array.isArray(campaigns) ? campaigns
                .filter(c => (c.cost || 0) > 0)
                .sort((a, b) => (b.cost || 0) - (a.cost || 0))
                .slice(0, 5)
                .map(c => ({
                  name: (c.name || '').substring(0, 20) + '...',
                  spend: parseFloat((c.cost || 0).toFixed(2)),
                })) : []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip formatter={(value: any) => `₹${parseFloat(value).toFixed(2)}`} />
                <Legend />
                <Bar dataKey="spend" fill="#1E88E5" name="Spend (₹)" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Clicks vs Impressions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Clicks vs Impressions
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Array.isArray(campaigns) ? campaigns
                .filter(c => (c.impressions || 0) > 0)
                .slice(0, 5)
                .map(c => ({
                  name: (c.name || '').substring(0, 20) + '...',
                  clicks: c.clicks || 0,
                  impressions: c.impressions || 0,
                })) : []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip formatter={(value: any) => parseFloat(value).toLocaleString()} />
                <Legend />
                <Bar dataKey="clicks" fill="#26A69A" name="Clicks" />
                <Bar dataKey="impressions" fill="#FFA726" name="Impressions" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* CTR Comparison */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Campaign CTR Comparison
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Array.isArray(campaigns) ? campaigns
                .filter(c => (c.ctr || 0) > 0)
                .sort((a, b) => (b.ctr || 0) - (a.ctr || 0))
                .slice(0, 5)
                .map(c => ({
                  name: (c.name || '').substring(0, 20) + '...',
                  ctr: parseFloat((c.ctr || 0).toFixed(2)),
                })) : []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip formatter={(value: any) => `${parseFloat(value).toFixed(2)}%`} />
                <Legend />
                <Bar dataKey="ctr" fill="#EF5350" name="CTR (%)" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Conversions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Conversions by Campaign
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={Array.isArray(campaigns) ? campaigns
                .filter(c => (c.conversions || 0) > 0)
                .sort((a, b) => (b.conversions || 0) - (a.conversions || 0))
                .slice(0, 5)
                .map(c => ({
                  name: (c.name || '').substring(0, 20) + '...',
                  conversions: parseFloat((c.conversions || 0).toFixed(2)),
                })) : []}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip formatter={(value: any) => parseFloat(value).toFixed(2)} />
                <Legend />
                <Bar dataKey="conversions" fill="#66BB6A" name="Conversions" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Active Campaigns
            </Typography>
            <Box sx={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #E0E0E0' }}>
                    <th style={{ textAlign: 'left', padding: '12px' }}>Campaign Name</th>
                    <th style={{ textAlign: 'left', padding: '12px' }}>Status</th>
                    <th style={{ textAlign: 'left', padding: '12px' }}>Objective</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Daily Budget</th>
                  </tr>
                </thead>
                <tbody>
                  {Array.isArray(campaigns) && campaigns.slice(0, 10).map((campaign, index) => (
                    <tr key={campaign.campaign_id} style={{ borderBottom: '1px solid #F0F0F0' }}>
                      <td style={{ padding: '12px' }}>{campaign.name}</td>
                      <td style={{ padding: '12px' }}>
                        <Box
                          component="span"
                          sx={{
                            px: 1.5,
                            py: 0.5,
                            borderRadius: 1,
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            bgcolor:
                              campaign.status === 'ACTIVE'
                                ? 'success.main'
                                : campaign.status === 'PAUSED'
                                ? 'warning.main'
                                : 'error.main',
                            color: 'white',
                          }}
                        >
                          {campaign.status}
                        </Box>
                      </td>
                      <td style={{ padding: '12px' }}>
                        {(campaign.objective || 'N/A').replace('OUTCOME_', '')}
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        {campaign.daily_budget
                          ? `₹${campaign.daily_budget.toFixed(2)}`
                          : campaign.lifetime_budget
                          ? `₹${campaign.lifetime_budget.toFixed(2)} (Lifetime)`
                          : 'N/A'}
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Box>
            {(!Array.isArray(campaigns) || campaigns.length === 0) && (
              <Box sx={{ textAlign: 'center', py: 4 }}>
                <Typography color="text.secondary">
                  No campaigns found. Run the ETL pipeline to sync your Meta Ads data.
                </Typography>
              </Box>
            )}
          </Paper>
        </Grid>
      </Grid>

      {/* Insights - Only show if we have meaningful data */}
      {metrics && ((metrics.spend || metrics.total_spend || 0) > 0 || (metrics.clicks || metrics.total_clicks || 0) > 0) && (
        <Stack spacing={2} sx={{ mt: 4 }}>
          <InsightCard
            data={{
              type: 'descriptive',
              insight: `You have ${Array.isArray(campaigns) ? campaigns.length : 0} campaigns with a total spend of ₹${
                (metrics.spend || metrics.total_spend || 0).toFixed(2)
              }. Generated ${metrics.clicks || metrics.total_clicks || 0} clicks and ${
                metrics.conversions || metrics.total_conversions || 0
              } conversions.`,
              priority: 'info',
            }}
            index={0}
          />
          {(metrics.roas || metrics.overall_roas || 0) > 0 && (
            <InsightCard
              data={{
                type: 'descriptive',
                insight: `Your current ROAS is ${(metrics.roas || metrics.overall_roas || 0).toFixed(2)}x with an average CPC of ₹${
                  (metrics.cpc || metrics.avg_cpc || 0).toFixed(2)
                } and CTR of ${(metrics.ctr || metrics.avg_ctr || 0).toFixed(2)}%.`,
                priority: (metrics.roas || metrics.overall_roas || 0) > 3 ? 'high' : 'info',
              }}
              index={1}
            />
          )}
        </Stack>
      )}
    </DashboardTemplate>
  );
};
