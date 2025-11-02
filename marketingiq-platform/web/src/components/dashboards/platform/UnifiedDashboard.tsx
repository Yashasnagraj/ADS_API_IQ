// Unified Cross-Platform Dashboard
import React, { useState, useEffect, useMemo } from 'react';
import { Grid, Stack, Paper, Typography, Box } from '@mui/material';
import DashboardTemplate from '../../common/DashboardTemplate';
import { KPICard } from '../../common/KPICard';
import InsightCard from '../../common/InsightCard';
import { SmartInsightCard } from '../../common/SmartInsightCard';
import { SmartInsightSummary } from '../../common/SmartInsightSummary';
import { DataQualityIndicator } from '../../common/DataQualityIndicator';
import { KPIData, InsightData, UnifiedMetrics } from '../../../types';
import { useFilters, getDateRangeValues } from '../../../context/FilterContext';
import { unifiedService } from '../../../services/unifiedService';
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

export const UnifiedDashboard: React.FC = () => {
  const { filters } = useFilters();
  const [metrics, setMetrics] = useState<UnifiedMetrics | null>(null);
  const [platformComparison, setPlatformComparison] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    if (filters.customerId) {
      fetchData();
    }
  }, [filters]);

  // Generate AI-powered cross-platform insights
  const smartInsights = useMemo(() => {
    if (!metrics || !platformComparison || platformComparison.length === 0) return [];
    try {
      return SmartInsightGenerator.analyzeUnifiedPerformance(metrics, platformComparison);
    } catch (error) {
      console.error('Error generating unified insights:', error);
      return [];
    }
  }, [metrics, platformComparison]);

  const fetchData = async () => {
    try {
      setLoading(true);
      const { startDate, endDate } = getDateRangeValues(filters);

      // Convert customerId string to number for API
      const customerId = filters.customerId ? Number(filters.customerId) : null;
      if (!customerId) return;

      const [metricsData, comparisonData] = await Promise.all([
        unifiedService.getUnifiedMetrics(customerId, filters.dateRange),
        unifiedService.getPlatformComparison(customerId, filters.dateRange),
      ]);

      setMetrics(metricsData);
      setPlatformComparison(comparisonData);
    } catch (error) {
      console.error('Error fetching unified metrics:', error);
    } finally {
      setLoading(false);
    }
  };

  const kpis: KPIData[] = metrics
    ? [
        {
          title: 'Total Marketing Spend',
          value: metrics.total_spend,
          prefix: '₹',
          change: 0,
          changeLabel: 'vs last period',
        },
        {
          title: 'Blended ROAS',
          value: metrics.blended_roas.toFixed(2),
          suffix: 'x',
          change: 0,
          isHighlighted: true,
          color: 'success',
        },
        {
          title: 'Total Conversions',
          value: metrics.total_conversions,
          change: 0,
          changeLabel: 'vs last period',
        },
        {
          title: 'Best Platform (ROAS)',
          value: `${metrics.best_platform.name} - ${metrics.best_platform.roas.toFixed(1)}x`,
          change: 0,
        },
        {
          title: 'Best Platform (Conv)',
          value: `${metrics.best_platform_by_conversions.name} - ${metrics.best_platform_by_conversions.conversions}`,
          change: 0,
        },
        {
          title: 'Active Platforms',
          value: platformComparison.length,
          change: 0,
          color: 'info',
        },
      ]
    : [];

  // Use real comparison data from API
  const comparisonData = Array.isArray(platformComparison)
    ? platformComparison.map((platform) => ({
        platform: platform.platform,
        Spend: platform.spend,
        Revenue: platform.revenue,
        ROAS: platform.roas,
        Conversions: platform.conversions,
      }))
    : [];

  const COLORS = ['#1E88E5', '#26A69A', '#FFA726'];

  if (loading) {
    return (
      <DashboardTemplate
        title="Unified Cross-Platform Analytics"
        subtitle="Compare Google Ads, Meta Ads, and Google Analytics performance side-by-side. AI-powered insights to optimize your marketing budget allocation."
      >
        <Typography>Loading...</Typography>
      </DashboardTemplate>
    );
  }

  return (
    <DashboardTemplate
      title="Unified Cross-Platform Analytics"
      subtitle="Compare Google Ads, Meta Ads, and Google Analytics performance side-by-side. AI-powered insights to optimize your marketing budget allocation."
    >
      {/* Data Quality Indicator */}
      <Box sx={{ mb: 3 }}>
        <DataQualityIndicator
          lastSync={new Date(Date.now() - 1000 * 60 * 10)} // 10 minutes ago
          dataPoints={platformComparison.reduce((sum, p) => sum + (p.conversions || 0), 0)}
          qualityScore={platformComparison.length > 0 ? 95 : 0}
          isLoading={loading}
          compact={true}
        />
      </Box>

      {/* KPIs */}
      <Grid container spacing={3} sx={{ mt: 2 }}>
        {kpis.map((kpi, index) => (
          <Grid item xs={12} md={4} key={index}>
            <KPICard data={kpi} index={index} />
          </Grid>
        ))}
      </Grid>

      {/* AI-Powered Smart Insights - Cross-Platform Intelligence */}
      <Box sx={{ mt: 4 }}>
        <Typography variant="h5" fontWeight={700} gutterBottom sx={{ mb: 3 }}>
          🧠 AI Cross-Platform Intelligence
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

      {/* Platform Comparison Charts */}
      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Spend vs Revenue by Platform
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={comparisonData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="platform" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="Spend" fill="#1E88E5" />
                <Bar dataKey="Revenue" fill="#26A69A" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Conversions by Platform
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={comparisonData}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ platform, Conversions }) =>
                    `${platform}: ${Conversions}`
                  }
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="Conversions"
                >
                  {comparisonData.map((entry, index) => (
                    <Cell
                      key={`cell-${index}`}
                      fill={COLORS[index % COLORS.length]}
                    />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Platform Performance Comparison
            </Typography>
            <Box sx={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #E0E0E0' }}>
                    <th style={{ textAlign: 'left', padding: '12px' }}>Metric</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Google Ads</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Meta Ads</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Organic</th>
                    <th style={{ textAlign: 'center', padding: '12px' }}>Winner</th>
                  </tr>
                </thead>
                <tbody>
                  {/* Spend Row */}
                  <tr style={{ borderBottom: '1px solid #F0F0F0' }}>
                    <td style={{ padding: '12px' }}>Spend</td>
                    {['Google Ads', 'Meta Ads', 'Organic'].map((platformName) => {
                      const platform = platformComparison.find((p) => p.platform === platformName);
                      return (
                        <td key={platformName} style={{ textAlign: 'right', padding: '12px' }}>
                          {platform ? `₹${platform.spend.toLocaleString()}` : '-'}
                        </td>
                      );
                    })}
                    <td style={{ textAlign: 'center', padding: '12px' }}>N/A</td>
                  </tr>
                  {/* ROAS Row */}
                  <tr style={{ borderBottom: '1px solid #F0F0F0' }}>
                    <td style={{ padding: '12px' }}>ROAS</td>
                    {['Google Ads', 'Meta Ads', 'Organic'].map((platformName) => {
                      const platform = platformComparison.find((p) => p.platform === platformName);
                      const isWinner =
                        platform &&
                        platform.roas ===
                          Math.max(...platformComparison.map((p) => p.roas || 0));
                      return (
                        <td
                          key={platformName}
                          style={{
                            textAlign: 'right',
                            padding: '12px',
                            color: isWinner ? '#66BB6A' : 'inherit',
                            fontWeight: isWinner ? 600 : 'normal',
                          }}
                        >
                          {platform ? (platform.roas > 0 ? `${platform.roas.toFixed(2)}x` : 'N/A') : '-'}
                        </td>
                      );
                    })}
                    <td style={{ textAlign: 'center', padding: '12px' }}>
                      {platformComparison.length > 0
                        ? platformComparison.reduce((best, p) =>
                            p.roas > best.roas ? p : best
                          ).platform
                        : 'N/A'}
                    </td>
                  </tr>
                  {/* Conversions Row */}
                  <tr style={{ borderBottom: '1px solid #F0F0F0' }}>
                    <td style={{ padding: '12px' }}>Conversions</td>
                    {['Google Ads', 'Meta Ads', 'Organic'].map((platformName) => {
                      const platform = platformComparison.find((p) => p.platform === platformName);
                      const isWinner =
                        platform &&
                        platform.conversions ===
                          Math.max(...platformComparison.map((p) => p.conversions || 0));
                      return (
                        <td
                          key={platformName}
                          style={{
                            textAlign: 'right',
                            padding: '12px',
                            color: isWinner ? '#66BB6A' : 'inherit',
                            fontWeight: isWinner ? 600 : 'normal',
                          }}
                        >
                          {platform ? platform.conversions : '-'}
                        </td>
                      );
                    })}
                    <td style={{ textAlign: 'center', padding: '12px' }}>
                      {platformComparison.length > 0
                        ? platformComparison.reduce((best, p) =>
                            p.conversions > best.conversions ? p : best
                          ).platform
                        : 'N/A'}
                    </td>
                  </tr>
                </tbody>
              </table>
            </Box>
          </Paper>
        </Grid>
      </Grid>
    </DashboardTemplate>
  );
};
