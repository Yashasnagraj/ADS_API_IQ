// Google Ads Performance Dashboard
import React, { useState, useEffect, useMemo } from 'react';
import { Grid, Stack, Paper, Typography, Box, CircularProgress, Alert } from '@mui/material';
import DashboardTemplate from '../../common/DashboardTemplate';
import { KPICard } from '../../common/KPICard';
import InsightCard from '../../common/InsightCard';
import { SmartInsightCard } from '../../common/SmartInsightCard';
import { DataQualityIndicator } from '../../common/DataQualityIndicator';
import { FilterState, KPIData, InsightData } from '../../../types';
import { googleAdsService } from '../../../services/googleAdsService';
import { useFilters } from '../../../context/FilterContext';
import { SmartInsightGenerator } from '../../../utils/insightGenerator';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export const GoogleAdsDashboard: React.FC = () => {
  const { filters } = useFilters();
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [metrics, setMetrics] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    console.log('GoogleAdsDashboard filters changed:', filters);
    if (filters.customerId) {
      fetchData();
    }
  }, [filters.customerId, filters.dateRange]);

  const fetchData = async () => {
    try {
      setLoading(true);
      setError(null);
      const campaignsData = await googleAdsService.getCampaigns(Number(filters.customerId), filters.dateRange);

      console.log('Google Ads campaigns data:', campaignsData);

      setCampaigns(campaignsData);

      // Calculate aggregated metrics from campaigns data
      if (campaignsData && campaignsData.length > 0) {
        const aggregated = campaignsData.reduce((acc: any, campaign: any) => {
          const m = campaign.metrics || {};
          return {
            impressions: (acc.impressions || 0) + (m.impressions || 0),
            clicks: (acc.clicks || 0) + (m.clicks || 0),
            spend: (acc.spend || 0) + (m.cost || 0),
            conversions: (acc.conversions || 0) + (m.conversions || 0),
            conversion_value: (acc.conversion_value || 0) + (m.conversions_value || m.conversion_value || 0),
          };
        }, {});

        // Calculate derived metrics
        aggregated.ctr = aggregated.impressions > 0 ? (aggregated.clicks / aggregated.impressions) * 100 : 0;
        aggregated.cpc = aggregated.clicks > 0 ? aggregated.spend / aggregated.clicks : 0;
        aggregated.roas = aggregated.spend > 0 ? aggregated.conversion_value / aggregated.spend : 0;
        aggregated.cpa = aggregated.conversions > 0 ? aggregated.spend / aggregated.conversions : 0;

        console.log('Calculated metrics:', aggregated);
        setMetrics(aggregated);
      } else {
        // Fallback to API summary if no campaigns
        const metricsData = await googleAdsService.getMetricsSummary(Number(filters.customerId), filters.dateRange);
        setMetrics(metricsData);
      }
    } catch (err: any) {
      console.error('Error fetching Google Ads data:', err);
      setError(err.message || 'Failed to load Google Ads data');
    } finally {
      setLoading(false);
    }
  };

  const kpis: KPIData[] = metrics
    ? [
        {
          title: 'Total Spend',
          value: (metrics.spend || 0).toFixed(0),
          prefix: '₹',
          change: 8,
        },
        {
          title: 'ROAS',
          value: (metrics.roas || 0).toFixed(1),
          suffix: 'x',
          change: 12,
          isHighlighted: true,
          color: 'success',
        },
        {
          title: 'Conversions',
          value: (metrics.conversions || 0).toFixed(0),
          change: 24,
        },
        {
          title: 'Avg. CPC',
          value: (metrics.cpc || 0).toFixed(2),
          prefix: '₹',
          change: -5,
          trend: 'down',
        },
        {
          title: 'CTR',
          value: `${(metrics.ctr || 0).toFixed(1)}%`,
          change: 0.4,
        },
        {
          title: 'Impressions',
          value: (metrics.impressions || 0).toLocaleString(),
          change: 0.3,
          color: 'info',
        },
      ]
    : [];

  // Generate AI-powered insights from campaign data
  const smartInsights = useMemo(() => {
    return SmartInsightGenerator.analyzeCampaignPerformance(campaigns);
  }, [campaigns]);

  // Convert smart insights to InsightData format
  const insights: InsightData[] = smartInsights.map((insight) => {
    const priorityMap: Record<string, 'high' | 'medium' | 'low' | 'info'> = {
      danger: 'high',
      warning: 'medium',
      success: 'low',
      info: 'info',
    };

    return {
      type: 'prescriptive',
      insight: insight.message,
      priority: priorityMap[insight.type] || 'info',
      expectedImpact: insight.impact,
      confidence: `${insight.confidence}%`,
      details: insight.actions,
      actions: insight.actionable ? [
        {
          label: 'View Recommendations',
          primary: true,
          onClick: () => console.log('View recommendations for:', insight.title),
        },
      ] : undefined,
    };
  });

  // Use campaigns data for chart - only campaigns with spend > 0
  const campaignPerformance = campaigns.length > 0
    ? campaigns
        .filter(c => (c.metrics?.cost || 0) > 0) // Only campaigns with actual spend
        .sort((a, b) => (b.metrics?.cost || 0) - (a.metrics?.cost || 0)) // Sort by spend descending
        .slice(0, 4)
        .map(c => {
          const spend = c.metrics?.cost || 0;
          const conversions = c.metrics?.conversions || 0;
          // Estimate revenue if not available (assume ₹500 per conversion as average)
          const revenue = c.metrics?.conversions_value || c.metrics?.conversion_value || (conversions * 500);
          const roas = spend > 0 ? revenue / spend : 0;

          return {
            name: c.campaign_name || c.name,
            spend: spend,
            revenue: revenue,
            ROAS: roas,
          };
        })
    : [
        { name: 'Brand Keywords', spend: 1200, revenue: 14880, ROAS: 12.4 },
        { name: 'Shopping Campaign', spend: 2100, revenue: 8610, ROAS: 4.1 },
        { name: 'Search Generic', spend: 1400, revenue: 8120, ROAS: 5.8 },
        { name: 'Competitor Terms', spend: 500, revenue: 1050, ROAS: 2.1 },
      ];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <DashboardTemplate
      title="Google Ads Performance"
      subtitle="Comprehensive view of your Google Ads campaigns, keywords, and search terms. Optimize your search and shopping campaigns with AI-powered insights."
    >
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Data Quality Indicator */}
      <Box sx={{ mb: 3 }}>
        <DataQualityIndicator
          lastSync={new Date(Date.now() - 1000 * 60 * 5)} // 5 minutes ago
          dataPoints={campaigns.length}
          qualityScore={campaigns.length > 0 ? 92 : 0}
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
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" fontWeight={700} gutterBottom sx={{ mb: 3 }}>
          🧠 AI Intelligence & Recommendations
        </Typography>
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
              index={index}
            />
          ))}
        </Stack>
      </Box>

      <Grid container spacing={3} sx={{ mt: 4 }}>
        {/* Campaign Spend Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Campaign Spend Distribution
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={campaignPerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="spend" fill="#1E88E5" name="Spend (₹)" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Campaign Clicks & Impressions Chart */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Clicks vs Impressions
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={campaigns.filter(c => (c.metrics?.impressions || 0) > 0).slice(0, 5).map(c => ({
                name: (c.campaign_name || c.name || '').substring(0, 15) + '...',
                clicks: c.metrics?.clicks || 0,
                impressions: c.metrics?.impressions || 0,
              }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="clicks" fill="#26A69A" name="Clicks" />
                <Bar dataKey="impressions" fill="#FFA726" name="Impressions" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Campaign CTR Comparison */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Campaign CTR Comparison
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={campaigns
                .filter(c => (c.metrics?.ctr || 0) > 0)
                .sort((a, b) => (b.metrics?.ctr || 0) - (a.metrics?.ctr || 0))
                .slice(0, 5)
                .map(c => ({
                  name: (c.campaign_name || c.name || '').substring(0, 15) + '...',
                  ctr: c.metrics?.ctr || 0,
                }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="ctr" fill="#EF5350" name="CTR (%)" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        {/* Campaign Conversions */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Conversions by Campaign
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={campaigns
                .filter(c => (c.metrics?.conversions || 0) > 0)
                .sort((a, b) => (b.metrics?.conversions || 0) - (a.metrics?.conversions || 0))
                .slice(0, 5)
                .map(c => ({
                  name: (c.campaign_name || c.name || '').substring(0, 15) + '...',
                  conversions: c.metrics?.conversions || 0,
                }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="conversions" fill="#66BB6A" name="Conversions" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Top Google Ads Campaigns
            </Typography>
            <Box sx={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #E0E0E0' }}>
                    <th style={{ textAlign: 'left', padding: '12px' }}>Campaign</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Spend</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>ROAS</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Conversions</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>CPC</th>
                    <th style={{ textAlign: 'center', padding: '12px' }}>Status</th>
                  </tr>
                </thead>
                <tbody>
                  {campaigns.slice(0, 10).map((campaign, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #F0F0F0' }}>
                      <td style={{ padding: '12px' }}>{campaign.campaign_name || campaign.name}</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        ₹{(campaign.metrics?.cost || 0).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        {campaign.metrics?.cost > 0 && campaign.metrics?.conversions > 0
                          ? ((campaign.metrics.conversions_value || 0) / campaign.metrics.cost).toFixed(2)
                          : '0.00'}x
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        {(campaign.metrics?.conversions || 0).toFixed(0)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        ₹{(campaign.metrics?.avg_cpc || 0).toFixed(2)}
                      </td>
                      <td style={{ textAlign: 'center', padding: '12px' }}>
                        <span style={{
                          color: campaign.status === 'ENABLED' ? '#66BB6A' :
                                 campaign.status === 'PAUSED' ? '#FFA726' : '#EF5350'
                        }}>
                          {campaign.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </DashboardTemplate>
  );
};
