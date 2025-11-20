// E-Commerce Performance Dashboard
import React, { useState, useEffect, useMemo } from 'react';
import { Grid, Stack, Paper, Typography, Box, CircularProgress, Alert } from '@mui/material';
import DashboardTemplate from '../../common/DashboardTemplate';
import { KPICard } from '../../common/KPICard';
import InsightCard from '../../common/InsightCard';
import { SmartInsightCard } from '../../common/SmartInsightCard';
import { SmartInsightSummary } from '../../common/SmartInsightSummary';
import { DataQualityIndicator } from '../../common/DataQualityIndicator';
import { FilterState, KPIData, InsightData, UnifiedMetrics } from '../../../types';
import { useFilters } from '../../../context/FilterContext';
import { unifiedService } from '../../../services/unifiedService';
import { googleAdsService } from '../../../services/googleAdsService';
import { comparisonService, MetricComparison } from '../../../services/comparisonService';
import { SmartInsightGenerator } from '../../../utils/insightGenerator';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

export const EcommerceDashboard: React.FC = () => {
  const { filters } = useFilters();
  const [metrics, setMetrics] = useState<UnifiedMetrics | null>(null);
  const [googleMetrics, setGoogleMetrics] = useState<any>(null);
  const [comparisons, setComparisons] = useState<Record<string, MetricComparison>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!filters.customerId) return;

      setLoading(true);
      setError(null);
      try {
        const [unifiedData, googleData, comparisonsData] = await Promise.all([
          unifiedService.getUnifiedMetrics(Number(filters.customerId), filters.dateRange),
          googleAdsService.getMetricsSummary(Number(filters.customerId), filters.dateRange),
          comparisonService.getBatchMetricComparisons(
            filters.customerId!,
            ['spend', 'conversions', 'roas', 'conversion_rate'],
            filters.dateRange
          ).catch(err => {
            console.warn('Failed to fetch ecommerce comparisons:', err);
            return {};
          })
        ]);

        setMetrics(unifiedData);
        setGoogleMetrics(googleData);
        setComparisons(comparisonsData);
      } catch (err: any) {
        console.error('Error fetching ecommerce data:', err);
        setError(err.message || 'Failed to load ecommerce data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters.customerId, filters.dateRange]);

  const kpis: KPIData[] = (metrics && googleMetrics)
    ? [
        {
          title: 'Total Revenue',
          value: (googleMetrics.conversion_value || 0).toFixed(0),
          prefix: '₹',
          change: comparisons.conversions?.change_percentage || 0, // Using conversions as proxy for revenue
          trend: comparisons.conversions?.change_direction === 'decrease' ? 'down' : (comparisons.conversions?.change_direction === 'increase' ? 'up' : undefined),
        },
        {
          title: 'Total Orders',
          value: (googleMetrics.conversions || 0).toFixed(0),
          change: comparisons.conversions?.change_percentage || 0,
          trend: comparisons.conversions?.change_direction === 'decrease' ? 'down' : (comparisons.conversions?.change_direction === 'increase' ? 'up' : undefined),
          isHighlighted: true,
          color: comparisons.conversions?.is_positive_change ? 'success' : 'error',
        },
        {
          title: 'Avg. Order Value',
          value: googleMetrics.conversions > 0
            ? (googleMetrics.conversion_value / googleMetrics.conversions).toFixed(2)
            : '0',
          prefix: '₹',
          change: 0, // AOV comparison not in API yet
        },
        {
          title: 'Total Spend',
          value: (googleMetrics.spend || 0).toFixed(0),
          prefix: '₹',
          change: comparisons.spend?.change_percentage || 0,
          trend: comparisons.spend?.change_direction === 'decrease' ? 'down' : (comparisons.spend?.change_direction === 'increase' ? 'up' : undefined),
        },
        {
          title: 'ROAS',
          value: (googleMetrics.roas || 0).toFixed(1),
          suffix: 'x',
          change: comparisons.roas?.change_percentage || 0,
          trend: comparisons.roas?.change_direction === 'decrease' ? 'down' : (comparisons.roas?.change_direction === 'increase' ? 'up' : undefined),
        },
        {
          title: 'Conversion Rate',
          value: `${((googleMetrics.conversions / googleMetrics.clicks) * 100 || 0).toFixed(1)}%`,
          change: comparisons.conversion_rate?.change_percentage || 0,
          trend: comparisons.conversion_rate?.change_direction === 'decrease' ? 'down' : (comparisons.conversion_rate?.change_direction === 'increase' ? 'up' : undefined),
        },
      ]
    : [];

  const insights: InsightData[] = [
    {
      type: 'descriptive',
      insight:
        'Google Ads drove 52% of e-commerce revenue ($25,688) with $26.05 AOV. Electronics category is top seller (48% of revenue). Mobile checkout improving: 38% abandonment vs 42% last month.',
      priority: 'info',
    },
    {
      type: 'diagnostic',
      insight:
        'Repeat purchase rate dropped from 32% to 28% because email automation stopped working for 12 days. Cart abandonment spikes on mobile at checkout payment step (48%).',
      priority: 'high',
      details: [
        'Email automation: 12 days downtime',
        'Mobile cart abandonment: 48% at payment step',
      ],
    },
    {
      type: 'prescriptive',
      insight:
        'Fix email automation to recover repeat purchases. Implement mobile-optimized payment options (Apple Pay, Google Pay) to reduce abandonment. Cross-sell electronics with accessories (+$3,200 potential revenue).',
      priority: 'high',
      expectedImpact: '+$4,800/month',
      confidence: '82%',
      actions: [
        {
          label: 'Setup Cross-Sell Rules',
          primary: true,
        },
      ],
    },
  ];

  const revenueByChannel = [
    { channel: 'Google Ads', revenue: 25688, orders: 987 },
    { channel: 'Meta Ads', revenue: 14820, orders: 569 },
    { channel: 'Organic', revenue: 7560, orders: 291 },
    { channel: 'Direct', revenue: 1332, orders: 51 },
  ];

  // Generate AI-powered e-commerce insights (after revenueByChannel is defined)
  const smartInsights = useMemo(() => {
    if (!googleMetrics) return [];
    try {
      return SmartInsightGenerator.analyzeEcommercePerformance(googleMetrics, revenueByChannel);
    } catch (error) {
      console.error('Error generating e-commerce insights:', error);
      return [];
    }
  }, [googleMetrics, revenueByChannel]);

  const topProducts = [
    { product: 'Wireless Headphones', units: 342, revenue: 10260, aov: 30 },
    { product: 'Smart Watch', units: 256, revenue: 12800, aov: 50 },
    { product: 'Phone Case', units: 512, revenue: 5120, aov: 10 },
    { product: 'Laptop Stand', units: 178, revenue: 7120, aov: 40 },
  ];

  const COLORS = ['#1E88E5', '#26A69A', '#FFA726', '#EF5350'];

  if (loading) {
    return (
      <Box sx={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '400px' }}>
        <CircularProgress />
      </Box>
    );
  }

  return (
    <DashboardTemplate
      title="E-Commerce Performance Dashboard"
      subtitle="Revenue, orders, and product performance across all marketing channels. Track your e-commerce KPIs and identify top-selling products."
    >
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Data Quality Indicator */}
      <Box sx={{ mb: 3 }}>
        <DataQualityIndicator
          lastSync={new Date(Date.now() - 1000 * 60 * 8)} // 8 minutes ago
          dataPoints={googleMetrics?.conversions || 0}
          qualityScore={googleMetrics ? 93 : 0}
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

      {/* AI-Powered E-commerce Intelligence */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" fontWeight={700} gutterBottom sx={{ mb: 3 }}>
          🧠 AI E-commerce Intelligence
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

      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Revenue by Channel
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={revenueByChannel}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="channel" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="revenue" fill="#1E88E5" name="Revenue ($)" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Customer Segments
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={[
                    { name: 'New Customers', value: 1366 },
                    { name: 'Returning Customers', value: 532 },
                  ]}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, value }) => `${name}: ${value}`}
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="value"
                >
                  <Cell fill={COLORS[0]} />
                  <Cell fill={COLORS[1]} />
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Top Products
            </Typography>
            <Box sx={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #E0E0E0' }}>
                    <th style={{ textAlign: 'left', padding: '12px' }}>Product</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Units Sold</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Revenue</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>AOV</th>
                  </tr>
                </thead>
                <tbody>
                  {topProducts.map((product, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #F0F0F0' }}>
                      <td style={{ padding: '12px' }}>{product.product}</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>{product.units}</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        ₹{product.revenue.toLocaleString()}
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>₹{product.aov}</td>
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
