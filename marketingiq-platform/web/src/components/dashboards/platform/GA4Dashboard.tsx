// Google Analytics 4 Dashboard
import React, { useState, useEffect, useMemo } from 'react';
import { Grid, Stack, Paper, Typography, Box, CircularProgress, Alert } from '@mui/material';
import DashboardTemplate from '../../common/DashboardTemplate';
import { KPICard } from '../../common/KPICard';
import InsightCard from '../../common/InsightCard';
import { SmartInsightCard } from '../../common/SmartInsightCard';
import { DataQualityIndicator } from '../../common/DataQualityIndicator';
import { SmartInsightSummary } from '../../common/SmartInsightSummary';
import { FilterState, KPIData, InsightData, GA4Metrics, GA4SourceMedium } from '../../../types';
import { useFilters } from '../../../context/FilterContext';
import { ga4Service } from '../../../services/ga4Service';
import { comparisonService, MetricComparison } from '../../../services/comparisonService';
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
} from 'recharts';

export const GA4Dashboard: React.FC = () => {
  const { filters } = useFilters();
  const [metrics, setMetrics] = useState<GA4Metrics | null>(null);
  const [sourceMedium, setSourceMedium] = useState<GA4SourceMedium[]>([]);
  const [comparisons, setComparisons] = useState<Record<string, MetricComparison>>({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const fetchData = async () => {
      if (!filters.customerId) return;

      setLoading(true);
      setError(null);
      try {
        const [metricsData, sourceData, comparisonsData] = await Promise.all([
          ga4Service.getSessions(Number(filters.customerId), filters.dateRange),
          ga4Service.getSourceMedium(Number(filters.customerId), filters.dateRange).catch(() => []),
          comparisonService.getBatchMetricComparisons(
            filters.customerId!,
            ['sessions', 'conversion_rate', 'conversions', 'bounce_rate', 'avg_session_duration', 'pages_per_session'],
            filters.dateRange
          ).catch(err => {
            console.warn('Failed to fetch GA4 comparisons:', err);
            return {};
          })
        ]);

        setMetrics(metricsData);
        setSourceMedium(sourceData);
        setComparisons(comparisonsData);
      } catch (err: any) {
        console.error('Error fetching GA4 data:', err);
        setError(err.message || 'Failed to load GA4 data');
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [filters.customerId, filters.dateRange]);

  // Generate AI-powered insights from GA4 metrics (MUST be before any conditional returns)
  const smartInsights = useMemo(() => {
    if (!metrics) return [];
    try {
      return SmartInsightGenerator.analyzeGA4Performance(metrics);
    } catch (error) {
      console.error('Error generating GA4 insights:', error);
      return [];
    }
  }, [metrics]);

  // Format session duration from seconds to MM:SS
  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, '0')}`;
  };

  const kpis: KPIData[] = metrics
    ? [
        {
          title: 'Total Sessions',
          value: metrics.sessions.toLocaleString(),
          change: comparisons.sessions?.change_percentage || 0,
          trend: comparisons.sessions?.change_direction === 'decrease' ? 'down' : (comparisons.sessions?.change_direction === 'increase' ? 'up' : undefined),
        },
        {
          title: 'Conversion Rate',
          value: `${metrics.conversion_rate.toFixed(1)}%`,
          change: comparisons.conversion_rate?.change_percentage || 0,
          trend: comparisons.conversion_rate?.change_direction === 'decrease' ? 'down' : (comparisons.conversion_rate?.change_direction === 'increase' ? 'up' : undefined),
          isHighlighted: true,
          color: comparisons.conversion_rate?.is_positive_change ? 'success' : 'error',
        },
        {
          title: 'Conversions',
          value: metrics.conversions.toLocaleString(),
          change: comparisons.conversions?.change_percentage || 0,
          trend: comparisons.conversions?.change_direction === 'decrease' ? 'down' : (comparisons.conversions?.change_direction === 'increase' ? 'up' : undefined),
        },
        {
          title: 'Bounce Rate',
          value: `${metrics.bounce_rate.toFixed(0)}%`,
          change: comparisons.bounce_rate?.change_percentage || 0,
          trend: comparisons.bounce_rate?.change_direction === 'decrease' ? 'down' : (comparisons.bounce_rate?.change_direction === 'increase' ? 'up' : undefined),
        },
        {
          title: 'Avg. Session Duration',
          value: formatDuration(metrics.avg_session_duration),
          change: comparisons.avg_session_duration?.change_percentage || 0,
          trend: comparisons.avg_session_duration?.change_direction === 'decrease' ? 'down' : (comparisons.avg_session_duration?.change_direction === 'increase' ? 'up' : undefined),
        },
        {
          title: 'Pages per Session',
          value: metrics.pages_per_session.toFixed(1),
          change: comparisons.pages_per_session?.change_percentage || 0,
          trend: comparisons.pages_per_session?.change_direction === 'decrease' ? 'down' : (comparisons.pages_per_session?.change_direction === 'increase' ? 'up' : undefined),
        },
      ]
    : [];

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

  // Use real data if available, no fallback
  const trafficSources = sourceMedium.length > 0
    ? sourceMedium.map(s => ({
        source: `${s.source} / ${s.medium}`,
        sessions: s.sessions,
        conversions: s.conversions,
        cvr: s.cvr,
      }))
    : [];

  // Device performance would need to come from API
  // For now, empty array - TODO: Add device breakdown endpoint
  const devicePerformance: any[] = [];

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
      title="Google Analytics (GA4) - Website Performance"
      subtitle="Understand your website traffic, user behavior, conversion funnels, and organic performance. Identify opportunities to improve user experience and conversion rates."
    >
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      {/* Data Quality Indicator */}
      <Box sx={{ mb: 3 }}>
        <DataQualityIndicator
          lastSync={new Date(Date.now() - 1000 * 60 * 7)} // 7 minutes ago
          dataPoints={metrics?.sessions || 0}
          qualityScore={metrics ? 90 : 0}
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

      {/* AI-Powered Smart Insights for GA4 */}
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

      <Grid container spacing={3} sx={{ mt: 4 }}>
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Traffic Sources
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={trafficSources}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ source, sessions }) =>
                    `${source}: ${sessions.toLocaleString()}`
                  }
                  outerRadius={100}
                  fill="#8884d8"
                  dataKey="sessions"
                >
                  {trafficSources.map((entry, index) => (
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

        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Device Performance
            </Typography>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={devicePerformance}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="device" />
                <YAxis />
                <Tooltip />
                <Legend />
                <Bar dataKey="sessions" fill="#1E88E5" name="Sessions" />
              </BarChart>
            </ResponsiveContainer>
          </Paper>
        </Grid>

        <Grid item xs={12}>
          <Paper sx={{ p: 3 }}>
            <Typography variant="h6" gutterBottom>
              Traffic Sources Performance
            </Typography>
            <Box sx={{ overflowX: 'auto' }}>
              <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                <thead>
                  <tr style={{ borderBottom: '2px solid #E0E0E0' }}>
                    <th style={{ textAlign: 'left', padding: '12px' }}>Source</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Sessions</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>Conversions</th>
                    <th style={{ textAlign: 'right', padding: '12px' }}>CVR</th>
                  </tr>
                </thead>
                <tbody>
                  {trafficSources.map((source, index) => (
                    <tr key={index} style={{ borderBottom: '1px solid #F0F0F0' }}>
                      <td style={{ padding: '12px' }}>{source.source}</td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        {source.sessions.toLocaleString()}
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        {source.conversions}
                      </td>
                      <td style={{ textAlign: 'right', padding: '12px' }}>
                        {source.cvr}%
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
