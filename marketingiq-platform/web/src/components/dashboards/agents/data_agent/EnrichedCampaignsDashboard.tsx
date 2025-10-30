/**
 * ⭐ ENRICHED CAMPAIGNS DASHBOARD ⭐
 * Combines Google Ads performance metrics with GA4 user behavior data
 * Shows the complete picture: clicks, conversions + bounce rate, engagement, quality scores
 */
import React, { useState } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Chip,
  Alert,
  CircularProgress,
  IconButton,
  Tooltip,
  useTheme,
  alpha,
  Paper,
  Divider,
} from '@mui/material';
import {
  Campaign,
  TrendingUp,
  AttachMoney,
  TouchApp,
  Visibility,
  ExitToApp,
  Schedule,
  Speed,
  CheckCircle,
  Warning,
  Error as ErrorIcon,
  Info,
  Refresh,
  Timeline,
} from '@mui/icons-material';
import { useFilters } from '../../../../context/FilterContext';
import { useGA4CampaignEnrichment } from '../../../../hooks/useFilteredAPI';
import GA4KPICard from '../../../../components/ga4/GA4KPICard';
import {
  formatCurrency,
  formatNumber,
  formatCurrencyFull,
  formatNumberFull,
} from '../../../charts/PowerBITheme';

const EnrichedCampaignsDashboard: React.FC = () => {
  const theme = useTheme();
  const { filters } = useFilters();

  // Fetch enriched campaign data (Google Ads + GA4 combined)
  const { data, loading, error, refetch } = useGA4CampaignEnrichment();

  if (!filters.customerId) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress />
        <Typography sx={{ mt: 2 }}>Please select a customer from the filter bar above</Typography>
      </Box>
    );
  }

  if (loading) {
    return (
      <Box sx={{ p: 3, textAlign: 'center' }}>
        <CircularProgress size={60} />
        <Typography sx={{ mt: 2 }}>Loading enriched campaign data...</Typography>
        <Typography variant="caption" color="text.secondary">
          Combining Google Ads performance with GA4 user behavior
        </Typography>
      </Box>
    );
  }

  if (error) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="error">
          Error loading enriched campaigns: {error.message}
        </Alert>
      </Box>
    );
  }

  const campaigns = data?.campaigns || [];

  if (campaigns.length === 0) {
    return (
      <Box sx={{ p: 3 }}>
        <Alert severity="info">
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
            No Campaign Data Available
          </Typography>
          <Typography variant="body2">
            No campaigns with GA4 data found for the selected customer. This could mean:
          </Typography>
          <ul style={{ marginTop: 8, marginBottom: 0 }}>
            <li>No campaigns have been created yet</li>
            <li>GA4 integration is not set up for this customer</li>
            <li>No GA4 data matches your campaign names (check UTM parameters)</li>
            <li>Try selecting a different customer from the filter bar above</li>
          </ul>
        </Alert>
      </Box>
    );
  }

  // Calculate aggregate metrics
  const totalCampaigns = campaigns.length;
  const avgQualityScore = campaigns.reduce((sum: number, c: any) => sum + (c.quality_score || 0), 0) / totalCampaigns;
  const avgBounceRate = campaigns.reduce((sum: number, c: any) => sum + (c.ga4_bounce_rate || 0), 0) / totalCampaigns;
  const avgEngagement = campaigns.reduce((sum: number, c: any) => sum + (c.ga4_engagement_rate || 0), 0) / totalCampaigns;
  const avgSessionDuration = campaigns.reduce((sum: number, c: any) => sum + (c.ga4_avg_session_duration || 0), 0) / totalCampaigns;
  const totalGA4Sessions = campaigns.reduce((sum: number, c: any) => sum + (c.ga4_sessions || 0), 0);

  // Quality score color
  const getQualityColor = (score: number) => {
    if (score >= 80) return 'success';
    if (score >= 60) return 'info';
    if (score >= 40) return 'warning';
    return 'error';
  };

  // Quality score icon
  const getQualityIcon = (score: number) => {
    if (score >= 80) return <CheckCircle fontSize="small" />;
    if (score >= 60) return <Info fontSize="small" />;
    if (score >= 40) return <Warning fontSize="small" />;
    return <ErrorIcon fontSize="small" />;
  };

  return (
    <Box>
      {/* Header */}
      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Box>
          <Typography
            variant="h4"
            sx={{
              fontWeight: 700,
              background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
              backgroundClip: 'text',
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
            }}
          >
            Enriched Campaigns Dashboard
          </Typography>
          <Typography variant="body2" color="text.secondary" sx={{ mt: 0.5 }}>
            Google Ads Performance + GA4 User Behavior Analytics
          </Typography>
        </Box>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Refresh data">
            <IconButton onClick={() => refetch()} color="primary">
              <Refresh />
            </IconButton>
          </Tooltip>
          <Chip
            icon={<Timeline />}
            label="Real-time Data"
            color="success"
            size="small"
          />
        </Box>
      </Box>

      {/* Info Banner */}
      <Alert severity="info" sx={{ mb: 3 }}>
        <Typography variant="body2">
          <strong>What is Quality Score?</strong> A 0-100 metric calculated from GA4 behavior data:
          Lower bounce rate (40%), Higher engagement (30%), More pages per session (30%).
          Scores above 70 indicate high-quality traffic worth investing in.
        </Typography>
      </Alert>

      {/* GA4 KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <GA4KPICard
            title="Avg Quality Score"
            value={avgQualityScore}
            format="score"
            color={avgQualityScore >= 70 ? 'success' : avgQualityScore >= 50 ? 'warning' : 'error'}
            subtitle="GA4 Behavior Metric"
            showProgress
            maxValue={100}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <GA4KPICard
            title="Avg Bounce Rate"
            value={avgBounceRate}
            format="percentage"
            color={avgBounceRate < 40 ? 'success' : avgBounceRate < 60 ? 'warning' : 'error'}
            subtitle="Lower is better"
            trend={avgBounceRate < 40 ? 'down' : 'up'}
            trendValue={-5.2}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <GA4KPICard
            title="Avg Engagement"
            value={avgEngagement}
            format="percentage"
            color={avgEngagement >= 60 ? 'success' : avgEngagement >= 40 ? 'warning' : 'error'}
            subtitle="Higher is better"
            trend={avgEngagement >= 60 ? 'up' : 'down'}
            trendValue={8.3}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <GA4KPICard
            title="Avg Session Duration"
            value={avgSessionDuration}
            format="duration"
            color="info"
            subtitle={`${totalGA4Sessions.toLocaleString()} total sessions`}
          />
        </Grid>
      </Grid>

      {/* Enriched Campaigns Table */}
      <Card>
        <CardContent>
          <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
            <Typography variant="h6" sx={{ fontWeight: 600 }}>
              Campaign Performance + User Behavior
            </Typography>
            <Chip
              label={`${totalCampaigns} campaigns`}
              size="small"
              color="primary"
              variant="outlined"
            />
          </Box>

          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell sx={{ fontWeight: 700 }}>Campaign Name</TableCell>
                  <TableCell align="center" sx={{ fontWeight: 700 }}>
                    <Tooltip title="Google Ads Clicks">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                        <TouchApp fontSize="small" />
                        Clicks
                      </Box>
                    </Tooltip>
                  </TableCell>
                  <TableCell align="right" sx={{ fontWeight: 700 }}>
                    <Tooltip title="Google Ads Cost">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'flex-end', gap: 0.5 }}>
                        <AttachMoney fontSize="small" />
                        Cost
                      </Box>
                    </Tooltip>
                  </TableCell>
                  <TableCell align="center" sx={{ fontWeight: 700, backgroundColor: alpha(theme.palette.info.main, 0.05) }}>
                    <Tooltip title="GA4 Sessions Count">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                        <Visibility fontSize="small" />
                        Sessions
                      </Box>
                    </Tooltip>
                  </TableCell>
                  <TableCell align="center" sx={{ fontWeight: 700, backgroundColor: alpha(theme.palette.info.main, 0.05) }}>
                    <Tooltip title="GA4 Bounce Rate (%)">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                        <ExitToApp fontSize="small" />
                        Bounce
                      </Box>
                    </Tooltip>
                  </TableCell>
                  <TableCell align="center" sx={{ fontWeight: 700, backgroundColor: alpha(theme.palette.info.main, 0.05) }}>
                    <Tooltip title="GA4 Engagement Rate (%)">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                        <TouchApp fontSize="small" />
                        Engagement
                      </Box>
                    </Tooltip>
                  </TableCell>
                  <TableCell align="center" sx={{ fontWeight: 700, backgroundColor: alpha(theme.palette.info.main, 0.05) }}>
                    <Tooltip title="GA4 Avg Session Duration">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                        <Schedule fontSize="small" />
                        Duration
                      </Box>
                    </Tooltip>
                  </TableCell>
                  <TableCell align="center" sx={{ fontWeight: 700, backgroundColor: alpha(theme.palette.success.main, 0.05) }}>
                    <Tooltip title="Quality Score (0-100)">
                      <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 0.5 }}>
                        <Speed fontSize="small" />
                        Quality
                      </Box>
                    </Tooltip>
                  </TableCell>
                  <TableCell sx={{ fontWeight: 700 }}>AI Recommendation</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {campaigns.map((campaign: any, index: number) => {
                  const qualityScore = campaign.quality_score || 0;
                  const qualityColor = getQualityColor(qualityScore);

                  return (
                    <TableRow
                      key={campaign.campaign_name || index}
                      hover
                      sx={{
                        '&:hover': {
                          backgroundColor: alpha(theme.palette.primary.main, 0.02),
                        },
                      }}
                    >
                      <TableCell>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {campaign.campaign_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          UTM: {campaign.utm_campaign || 'N/A'}
                        </Typography>
                      </TableCell>

                      {/* Google Ads Metrics */}
                      <TableCell align="center">
                        <Typography variant="body2">{formatNumber(campaign.clicks || 0)}</Typography>
                      </TableCell>
                      <TableCell align="right">
                        <Typography variant="body2">{formatCurrency(campaign.cost || 0)}</Typography>
                      </TableCell>

                      {/* GA4 Metrics */}
                      <TableCell align="center" sx={{ backgroundColor: alpha(theme.palette.info.main, 0.02) }}>
                        <Typography variant="body2" sx={{ fontWeight: 500 }}>
                          {formatNumber(campaign.ga4_sessions || 0)}
                        </Typography>
                      </TableCell>
                      <TableCell align="center" sx={{ backgroundColor: alpha(theme.palette.info.main, 0.02) }}>
                        <Chip
                          label={`${(campaign.ga4_bounce_rate || 0).toFixed(1)}%`}
                          size="small"
                          color={(campaign.ga4_bounce_rate || 0) < 40 ? 'success' : (campaign.ga4_bounce_rate || 0) < 60 ? 'warning' : 'error'}
                        />
                      </TableCell>
                      <TableCell align="center" sx={{ backgroundColor: alpha(theme.palette.info.main, 0.02) }}>
                        <Chip
                          label={`${(campaign.ga4_engagement_rate || 0).toFixed(1)}%`}
                          size="small"
                          color={(campaign.ga4_engagement_rate || 0) >= 60 ? 'success' : (campaign.ga4_engagement_rate || 0) >= 40 ? 'warning' : 'error'}
                        />
                      </TableCell>
                      <TableCell align="center" sx={{ backgroundColor: alpha(theme.palette.info.main, 0.02) }}>
                        <Typography variant="body2">
                          {Math.floor((campaign.ga4_avg_session_duration || 0) / 60)}m {Math.floor((campaign.ga4_avg_session_duration || 0) % 60)}s
                        </Typography>
                      </TableCell>

                      {/* Quality Score */}
                      <TableCell align="center" sx={{ backgroundColor: alpha(theme.palette.success.main, 0.02) }}>
                        <Chip
                          icon={getQualityIcon(qualityScore)}
                          label={`${qualityScore.toFixed(0)}/100`}
                          size="small"
                          color={qualityColor}
                          sx={{ fontWeight: 600 }}
                        />
                      </TableCell>

                      {/* AI Recommendation */}
                      <TableCell>
                        <Typography
                          variant="caption"
                          sx={{
                            display: 'block',
                            color: qualityScore >= 70 ? theme.palette.success.main : qualityScore >= 50 ? theme.palette.warning.main : theme.palette.error.main,
                            fontWeight: 500,
                          }}
                        >
                          {campaign.recommendation || 'No recommendation available'}
                        </Typography>
                      </TableCell>
                    </TableRow>
                  );
                })}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Summary Footer */}
      <Alert
        severity={avgQualityScore >= 70 ? 'success' : avgQualityScore >= 50 ? 'info' : 'warning'}
        sx={{ mt: 3 }}
      >
        <Typography variant="body2">
          <strong>Overall Assessment:</strong>{' '}
          {avgQualityScore >= 70
            ? `Excellent! Your campaigns have an average quality score of ${avgQualityScore.toFixed(1)}/100. Traffic is highly engaged with low bounce rates. Consider increasing budgets for top performers.`
            : avgQualityScore >= 50
            ? `Good performance with average quality score of ${avgQualityScore.toFixed(1)}/100. Some campaigns show room for improvement in user engagement. Focus on landing page optimization.`
            : `Average quality score is ${avgQualityScore.toFixed(1)}/100, indicating opportunities for improvement. High bounce rates suggest landing page or targeting issues. Review low-quality campaigns and pause if needed.`}
        </Typography>
      </Alert>
    </Box>
  );
};

export default EnrichedCampaignsDashboard;
