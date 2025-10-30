// Meta Ads Dashboard - Real Data Integration
import React, { useState, useEffect } from 'react';
import { Grid, Stack, Paper, Typography, Box, CircularProgress } from '@mui/material';
import DashboardTemplate from '../common/DashboardTemplate';
import { GlobalFilterBar } from '../common/GlobalFilterBar';
import { KPICard } from '../common/KPICard';
import InsightCard from '../common/InsightCard';
import { FilterState, KPIData } from '../../types';
import { metaAdsService } from '../../services/metaAdsService';
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
}

export const MetaAdsDashboard: React.FC = () => {
  const [filters, setFilters] = useState<FilterState>({
    customer_id: 1,
    date_range: 'last_30d',
  });

  const [loading, setLoading] = useState(true);
  const [campaigns, setCampaigns] = useState<MetaCampaign[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Fetch campaigns and metrics in parallel
        const [campaignsData, metricsData] = await Promise.all([
          metaAdsService.getCampaigns(filters.customer_id, filters.date_range),
          metaAdsService.getInsightsSummary(filters.customer_id, filters.date_range),
        ]);

        // Ensure campaigns is always an array
        setCampaigns(Array.isArray(campaignsData) ? campaignsData : []);
        setMetrics(metricsData);
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
  }, [filters]);

  // Generate KPIs from real data (using standard field names)
  const kpis: KPIData[] = metrics
    ? [
        {
          title: 'Total Spend',
          value: metrics.spend || metrics.total_spend || 0,
          prefix: '₹',
          change: 0,
        },
        {
          title: 'ROAS',
          value: (metrics.roas || metrics.overall_roas || 0).toFixed(2),
          suffix: 'x',
          change: 0,
          isHighlighted: true,
          color: 'success',
        },
        {
          title: 'Conversions',
          value: metrics.conversions || metrics.total_conversions || 0,
          change: 0,
        },
        {
          title: 'Avg. CPC',
          value: (metrics.cpc || metrics.avg_cpc || 0).toFixed(2),
          prefix: '₹',
          change: 0,
        },
        {
          title: 'CTR',
          value: `${(metrics.ctr || metrics.avg_ctr || 0).toFixed(2)}%`,
          change: 0,
        },
        {
          title: 'Frequency',
          value: (metrics.avg_frequency || 0).toFixed(1),
          change: 0,
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
      <GlobalFilterBar onFilterChange={setFilters} showPlatformFilter={false} />

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {kpis.map((kpi, index) => (
          <Grid item xs={12} md={4} key={index}>
            <KPICard data={kpi} index={index} />
          </Grid>
        ))}
      </Grid>

      {/* Campaign Statistics */}
      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Campaign Status Distribution
            </Typography>
            <Box sx={{ mb: 2 }}>
              <Typography variant="body2" color="text.secondary">
                Total Campaigns: {Array.isArray(campaigns) ? campaigns.length : 0}
              </Typography>
            </Box>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={statusDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={(entry: any) => `${entry.status}: ${entry.count}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="count"
                >
                  {statusDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Campaigns by Objective
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={objectiveData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="objective" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="count" fill="#1E88E5" name="Campaign Count" />
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
