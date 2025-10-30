// Google Ads Performance Dashboard
import React, { useState, useEffect } from 'react';
import { Grid, Stack, Paper, Typography, Box } from '@mui/material';
import DashboardTemplate from '../common/DashboardTemplate';
import { GlobalFilterBar } from '../common/GlobalFilterBar';
import { KPICard } from '../common/KPICard';
import InsightCard from '../common/InsightCard';
import { FilterState, KPIData, InsightData } from '../../types';
import { googleAdsService } from '../../services/googleAdsService';
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
  const [filters, setFilters] = useState<FilterState>({
    customer_id: 1,
    date_range: 'last_30d',
  });
  const [campaigns, setCampaigns] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (filters.customer_id) {
      fetchData();
    }
  }, [filters]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const data = await googleAdsService.getCampaigns(
        filters.customer_id!,
        filters.date_range
      );
      setCampaigns(data);
    } catch (error) {
      console.error('Error fetching Google Ads data:', error);
    } finally {
      setLoading(false);
    }
  };

  const kpis: KPIData[] = [
    {
      title: 'Total Spend',
      value: 5200,
      prefix: '$',
      change: 8,
    },
    {
      title: 'ROAS',
      value: '5.2',
      suffix: 'x',
      change: 12,
      isHighlighted: true,
      color: 'success',
    },
    {
      title: 'Conversions',
      value: 420,
      change: 24,
    },
    {
      title: 'Avg. CPC',
      value: '1.20',
      prefix: '$',
      change: -5,
      trend: 'down',
    },
    {
      title: 'CTR',
      value: '3.8%',
      change: 0.4,
    },
    {
      title: 'Quality Score',
      value: '7.2/10',
      change: 0.3,
      color: 'info',
    },
  ];

  const insights: InsightData[] = [
    {
      type: 'descriptive',
      insight:
        'Search campaigns generated 78% of conversions at 5.8x ROAS. Shopping campaigns contributed 18% at 4.1x ROAS.',
      priority: 'info',
    },
    {
      type: 'diagnostic',
      insight:
        '"Brand Keywords" campaign has 12.4x ROAS due to high purchase intent. "Competitor Terms" struggling with 2.1x ROAS because of high CPCs ($4.20) and low quality scores (4.2).',
      priority: 'medium',
      details: [
        'Brand Keywords: 12.4x ROAS, Low CPC ($0.85)',
        'Competitor Terms: 2.1x ROAS, High CPC ($4.20)',
      ],
    },
    {
      type: 'prescriptive',
      insight:
        'Increase brand campaign budget by 25% (expected +$2,100 revenue). Pause 12 underperforming keywords with QS < 3. Add 8 negative keywords to reduce wasted spend by $450/month.',
      priority: 'high',
      expectedImpact: '+$1,850 monthly profit',
      confidence: '91%',
      actions: [
        {
          label: 'Apply All Recommendations',
          primary: true,
          onClick: () => console.log('Apply recommendations'),
        },
      ],
    },
  ];

  // Mock data for charts
  const campaignPerformance = [
    { name: 'Brand Keywords', spend: 1200, revenue: 14880, ROAS: 12.4 },
    { name: 'Shopping Campaign', spend: 2100, revenue: 8610, ROAS: 4.1 },
    { name: 'Search Generic', spend: 1400, revenue: 8120, ROAS: 5.8 },
    { name: 'Competitor Terms', spend: 500, revenue: 1050, ROAS: 2.1 },
  ];

  return (
    <DashboardTemplate
      title="Google Ads Performance"
      subtitle="Comprehensive view of your Google Ads campaigns, keywords, and search terms. Optimize your search and shopping campaigns with AI-powered insights."
    >
      <GlobalFilterBar onFilterChange={setFilters} showPlatformFilter={false} />

      <Grid container spacing={3} sx={{ mt: 2 }}>
        {kpis.map((kpi, index) => (
          <Grid item xs={12} md={4} key={index}>
            <KPICard data={kpi} index={index} />
          </Grid>
        ))}
      </Grid>

      <Stack spacing={2} sx={{ mt: 4 }}>
        {insights.map((insight, index) => (
          <InsightCard key={index} data={insight} index={index} />
        ))}
      </Stack>

      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Campaign Performance Comparison
            </Typography>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={campaignPerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" />
                <YAxis yAxisId="left" />
                <YAxis yAxisId="right" orientation="right" />
                <Tooltip />
                <Legend />
                <Bar yAxisId="left" dataKey="spend" fill="#1E88E5" name="Spend ($)" />
                <Bar yAxisId="left" dataKey="revenue" fill="#26A69A" name="Revenue ($)" />
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
                  {campaignPerformance.map((campaign, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #F0F0F0' }}>
                      <td style={{ padding: '12px' }}>{campaign.name}</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        ${campaign.spend.toLocaleString()}
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        {campaign.ROAS}x
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        {Math.floor(campaign.revenue / 50)}
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        ${(campaign.spend / (campaign.revenue / 50) / 10).toFixed(2)}
                      </td>
                      <td style={{ textAlign: 'center', padding: '12px' }}>
                        <span style={{ color: '#66BB6A' }}>ENABLED</span>
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
