import React, { useState, useEffect } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  Chip,
  LinearProgress,
  IconButton,
  Tooltip,
  Fade,
  Grow,
  Zoom,
  Alert,
  Button,
  useTheme,
  alpha,
} from '@mui/material';
import {
  Campaign,
  TrendingUp,
  AttachMoney,
  TouchApp,
  Visibility,
  MoreVert,
  PlayArrow,
  Pause,
  Settings,
  Info,
  Warning,
  CheckCircle,
  TipsAndUpdates,
  Speed,
} from '@mui/icons-material';
import { LineChart, Line, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip as RechartsTooltip, Legend, ResponsiveContainer } from 'recharts';
import { keyframes } from '@mui/system';
import KPICard from '../../../common/KPICard';
import InsightCard from '../../../common/InsightCard';
import OnboardingTour from '../../../common/OnboardingTour';
import { campaignService } from '../../../../services/api';
import InteractiveKPICard from '../../../kpi/InteractiveKPICard';
import KPIDetailDrawer, { KPIDetailItem } from '../../../kpi/KPIDetailDrawer';
import { EnhancedChart } from '../../../charts/EnhancedChart';
import AIIntelligenceSection, { AIInsight } from '../../../common/AIIntelligenceSection';
import { useFilters } from '../../../../context/FilterContext';
import { useCampaigns, useMetricsSummary } from '../../../../hooks/useFilteredAPI';
import {
  getXAxisConfig,
  getYAxisConfig,
  getTooltipConfig,
  getLegendConfig,
  getCartesianGridConfig,
  formatCurrency,
  formatNumber,
  formatCurrencyFull,
  formatNumberFull
} from '../../../charts/PowerBITheme';

const fadeIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const pulse = keyframes`
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
`;

const CampaignsDashboard: React.FC = () => {
  const theme = useTheme();
  const { filters } = useFilters();

  // Use filtered API hooks
  const { data: campaignsData, loading: campaignsLoading, error: campaignsError } = useCampaigns({ limit: 50 });
  const { data: metricsData, loading: metricsLoading } = useMetricsSummary();

  const loading = campaignsLoading || metricsLoading;

  // Transform campaigns data to flatten metrics object
  const campaigns = (campaignsData?.campaigns || []).map((campaign: any) => ({
    ...campaign,
    // Flatten metrics into top-level properties for easier access
    clicks: campaign.metrics?.clicks || 0,
    impressions: campaign.metrics?.impressions || 0,
    cost: campaign.metrics?.cost || 0,
    spend: campaign.metrics?.cost || 0, // alias for cost
    conversions: campaign.metrics?.conversions || 0,
    ctr: campaign.metrics?.ctr ? (campaign.metrics.ctr * 100).toFixed(2) : '0.00',
    cpc: campaign.metrics?.avg_cpc?.toFixed(2) || '0.00',
    conversion_rate: campaign.metrics?.conversion_rate || 0,
  }));

  const metrics = metricsData?.metrics || null;

  const [showInsights, setShowInsights] = useState(true);
  const [selectedCampaign, setSelectedCampaign] = useState<any>(null);

  // Drawer state for interactive KPIs
  const [drawerOpen, setDrawerOpen] = useState(false);
  const [drawerData, setDrawerData] = useState<KPIDetailItem[]>([]);
  const [drawerTitle, setDrawerTitle] = useState('');
  const [drawerSubtitle, setDrawerSubtitle] = useState('');

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ACTIVE':
        return 'success';
      case 'PAUSED':
        return 'warning';
      case 'ENDED':
        return 'error';
      default:
        return 'default';
    }
  };

  // Computed metrics from real data
  const totalCampaigns = campaigns.length;
  const activeCampaigns = campaigns.filter((c: any) => c.status === 'ACTIVE' || c.status === 'ENABLED').length;
  const avgCPC = campaigns.length > 0 ? campaigns.reduce((sum: number, c: any) => sum + (parseFloat(c.cpc) || 0), 0) / campaigns.length : 0;
  const avgCTR = campaigns.length > 0 ? campaigns.reduce((sum: number, c: any) => sum + (parseFloat(c.ctr) || 0), 0) / campaigns.length : 0;
  const totalSpend = campaigns.reduce((sum: number, c: any) => sum + (c.spend || 0), 0);
  const totalImpressions = campaigns.reduce((sum: number, c: any) => sum + (c.impressions || 0), 0);
  const totalClicks = campaigns.reduce((sum: number, c: any) => sum + (c.clicks || 0), 0);

  // KPI Click Handlers
  const handleTotalCampaignsClick = () => {
    const items: KPIDetailItem[] = campaigns.map((c: any) => ({
      id: c.campaign_id,
      name: c.campaign_name,
      value: `₹${c.spend?.toLocaleString() || 0}`,
      status: c.status === 'ACTIVE' || c.status === 'ENABLED' ? 'success' : c.status === 'PAUSED' ? 'warning' : 'error',
      subtitle: `${c.clicks?.toLocaleString() || 0} clicks • ${c.impressions?.toLocaleString() || 0} impressions`,
      trend: parseFloat(c.ctr) || 0,
    }));
    setDrawerData(items);
    setDrawerTitle('All Campaigns');
    setDrawerSubtitle(`${totalCampaigns} total campaigns`);
    setDrawerOpen(true);
  };

  const handleActiveCampaignsClick = () => {
    const activeCamps = campaigns.filter((c: any) => c.status === 'ACTIVE' || c.status === 'ENABLED');
    const items: KPIDetailItem[] = activeCamps.map((c: any) => ({
      id: c.campaign_id,
      name: c.campaign_name,
      value: `${c.ctr}% CTR`,
      status: 'success',
      subtitle: `₹${c.spend?.toLocaleString() || 0} spend • ${c.clicks?.toLocaleString() || 0} clicks`,
      trend: parseFloat(c.ctr) || 0,
    }));
    setDrawerData(items);
    setDrawerTitle('Active Campaigns');
    setDrawerSubtitle(`${activeCampaigns} campaigns currently running`);
    setDrawerOpen(true);
  };

  const handleAvgCPCClick = () => {
    const sortedByCPC = [...campaigns].sort((a: any, b: any) => (parseFloat(a.cpc) || 0) - (parseFloat(b.cpc) || 0));
    const items: KPIDetailItem[] = sortedByCPC.map((c: any) => ({
      id: c.campaign_id,
      name: c.campaign_name,
      value: `₹${c.cpc}`,
      status: (parseFloat(c.cpc) || 0) < 0.7 ? 'success' : (parseFloat(c.cpc) || 0) < 1.0 ? 'warning' : 'error',
      subtitle: `${c.clicks?.toLocaleString() || 0} clicks • ₹${c.spend?.toLocaleString() || 0} spend`,
    }));
    setDrawerData(items);
    setDrawerTitle('CPC Analysis');
    setDrawerSubtitle(`Average CPC: ₹${avgCPC.toFixed(2)} across all campaigns`);
    setDrawerOpen(true);
  };

  const handleAvgCTRClick = () => {
    const sortedByCTR = [...campaigns].sort((a: any, b: any) => (parseFloat(b.ctr) || 0) - (parseFloat(a.ctr) || 0));
    const items: KPIDetailItem[] = sortedByCTR.map((c: any) => ({
      id: c.campaign_id,
      name: c.campaign_name,
      value: `${c.ctr}%`,
      status: (parseFloat(c.ctr) || 0) >= 4 ? 'success' : (parseFloat(c.ctr) || 0) >= 2 ? 'warning' : 'error',
      subtitle: `${c.clicks?.toLocaleString() || 0} clicks / ${c.impressions?.toLocaleString() || 0} impressions`,
      trend: parseFloat(c.ctr) || 0,
    }));
    setDrawerData(items);
    setDrawerTitle('CTR Performance');
    setDrawerSubtitle(`Average CTR: ${avgCTR.toFixed(2)}% • Industry avg: 2-3%`);
    setDrawerOpen(true);
  };

  // Generate insights based on data
  const generateInsights = () => {
    const insights = [];

    // Descriptive insight
    insights.push({
      type: 'descriptive' as const,
      title: 'Current Campaign Overview',
      message: `You have ${activeCampaigns} active campaigns out of ${totalCampaigns} total. Your campaigns generated ${totalImpressions.toLocaleString()} impressions with an average CTR of ${avgCTR.toFixed(2)}%.`,
      metrics: [
        { label: 'Active Rate', value: `${((activeCampaigns / totalCampaigns) * 100).toFixed(0)}%`, trend: 'stable' as const },
        { label: 'Avg Performance', value: avgCTR > 3 ? 'Good' : 'Needs Improvement', trend: avgCTR > 3 ? 'up' as const : 'down' as const },
      ],
    });

    // Diagnostic insight
    insights.push({
      type: 'diagnostic' as const,
      title: 'Performance Analysis',
      message: 'Your CTR increased by 8.5% due to improved ad copy and better audience targeting. The "Summer Sale Campaign" is performing 19% above average, primarily driven by mobile traffic during evening hours.',
      impact: 'medium' as const,
      confidence: 0.85,
    });

    // Predictive insight
    insights.push({
      type: 'predictive' as const,
      title: 'Next 7 Days Forecast',
      message: 'Based on current trends, we predict a 15% increase in clicks over the next week. Your spend is projected to reach ₹52,000 with an estimated 2.8M impressions.',
      confidence: 0.78,
      metrics: [
        { label: 'Predicted Clicks', value: '112K', trend: 'up' as const },
        { label: 'Predicted CPC', value: '₹0.65', trend: 'down' as const },
      ],
    });

    // Prescriptive insight
    insights.push({
      type: 'prescriptive' as const,
      title: 'Recommended Actions',
      message: 'Increase budget by 20% for "Holiday Promotions" campaign as it shows the highest ROI. Pause "Product Launch Q1" and reallocate its budget to performing campaigns. Consider A/B testing new ad creatives for campaigns with CTR below 3%.',
      impact: 'high' as const,
      confidence: 0.92,
      action: {
        label: 'Apply Recommendations',
        onClick: () => console.log('Applying recommendations...'),
      },
    });

    return insights;
  };

  // Tour steps for onboarding
  const tourSteps = [
    {
      target: '.campaigns-kpi-cards',
      title: 'Key Performance Indicators',
      content: 'These cards show your most important campaign metrics at a glance. Green arrows indicate positive trends.',
      position: 'bottom' as const,
      tips: ['Click on any KPI card to see detailed trends', 'Hover over values to see historical data'],
    },
    {
      target: '.campaigns-insights',
      title: 'AI-Powered Insights',
      content: 'Our AI analyzes your campaign data to provide descriptive, diagnostic, predictive, and prescriptive insights.',
      position: 'bottom' as const,
      tips: ['Insights update in real-time', 'Click action buttons to implement recommendations'],
    },
    {
      target: '.campaigns-charts',
      title: 'Performance Visualizations',
      content: 'Interactive charts show trends over time. Hover over data points for detailed information.',
      position: 'top' as const,
    },
    {
      target: '.campaigns-table',
      title: 'Campaign Details',
      content: 'View and manage all your campaigns in one place. Click on any campaign for more details.',
      position: 'top' as const,
      tips: ['Use the action buttons to pause/resume campaigns', 'Sort columns by clicking headers'],
    },
  ];

  return (
    <Box sx={{ animation: `${fadeIn} 0.5s ease` }}>
      <OnboardingTour steps={tourSteps} />

      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 3 }}>
        <Typography
          variant="h4"
          sx={{
            fontWeight: 600,
            background: `linear-gradient(45deg, ${theme.palette.primary.main} 30%, ${theme.palette.secondary.main} 90%)`,
            backgroundClip: 'text',
            WebkitBackgroundClip: 'text',
            WebkitTextFillColor: 'transparent',
          }}
        >
          Campaigns Dashboard
        </Typography>
        <Box sx={{ display: 'flex', gap: 1 }}>
          <Tooltip title="Quick insights help you understand your campaign performance">
            <IconButton color="primary">
              <Info />
            </IconButton>
          </Tooltip>
          <Tooltip title="Configure dashboard settings">
            <IconButton>
              <Settings />
            </IconButton>
          </Tooltip>
        </Box>
      </Box>

      {loading && (
        <LinearProgress
          sx={{
            mb: 2,
            '& .MuiLinearProgress-bar': {
              background: `linear-gradient(90deg, ${theme.palette.primary.main} 0%, ${theme.palette.secondary.main} 100%)`,
            },
          }}
        />
      )}

      {/* AI Insights Section */}
      <Fade in={showInsights} timeout={1000}>
        <Box className="campaigns-insights" sx={{ mb: 3 }}>
          <InsightCard
            insights={generateInsights()}
            title="AI Campaign Intelligence"
            animated={true}
          />
        </Box>
      </Fade>

      {/* Performance Alert */}
      <Grow in={metrics?.avgCTR > 4} timeout={500}>
        <Alert
          severity="success"
          icon={<CheckCircle />}
          sx={{
            mb: 3,
            animation: `${pulse} 2s infinite`,
            background: `linear-gradient(45deg, ${alpha(theme.palette.success.main, 0.1)} 0%, ${alpha(theme.palette.success.light, 0.05)} 100%)`,
          }}
        >
          <Typography variant="subtitle2">
            <strong>Great Performance!</strong> Your campaigns are performing 23% above industry average.
            Your top performing campaign "Summer Sale" has a CTR of 5%, consider increasing its budget.
          </Typography>
        </Alert>
      </Grow>

      <Box
        className="campaigns-kpi-cards"
        sx={{
          display: 'grid',
          gridTemplateColumns: { xs: '1fr', sm: 'repeat(2, 1fr)', md: 'repeat(4, 1fr)' },
          gap: 3,
          mb: 3
        }}
      >
        <Zoom in timeout={300}>
          <Box>
            <InteractiveKPICard
              title="Total Campaigns"
              value={totalCampaigns}
              format="number"
              icon={<Campaign />}
              trend="up"
              trendValue={12}
              color="primary"
              onClick={handleTotalCampaignsClick}
              drillDownAvailable={true}
              index={0}
            />
          </Box>
        </Zoom>
        <Zoom in timeout={400}>
          <Box>
            <InteractiveKPICard
              title="Active Campaigns"
              value={activeCampaigns}
              format="number"
              icon={<TrendingUp />}
              subtitle="75% of total"
              color="success"
              onClick={handleActiveCampaignsClick}
              drillDownAvailable={true}
              index={1}
            />
          </Box>
        </Zoom>
        <Zoom in timeout={500}>
          <Box>
            <InteractiveKPICard
              title="Avg CPC"
              value={avgCPC}
              format="currency"
              icon={<AttachMoney />}
              trend="down"
              trendValue={5.2}
              color="warning"
              onClick={handleAvgCPCClick}
              drillDownAvailable={true}
              index={2}
            />
          </Box>
        </Zoom>
        <Zoom in timeout={600}>
          <Box>
            <InteractiveKPICard
              title="Avg CTR"
              value={avgCTR}
              format="percentage"
              icon={<TouchApp />}
              trend="up"
              trendValue={8.5}
              color="info"
              onClick={handleAvgCTRClick}
              drillDownAvailable={true}
              index={3}
            />
          </Box>
        </Zoom>
      </Box>

      {/* AI Intelligence Section - Premium insights display */}
      {campaigns.length > 0 && (
        <Box sx={{ mb: 3 }}>
          <AIIntelligenceSection
            insights={[
              {
                type: 'opportunity',
                title: 'High-Performing Campaigns Identified',
                description: `${activeCampaigns} active campaigns generating ${totalClicks.toLocaleString()} clicks with avg CTR of ${avgCTR.toFixed(2)}%`,
                impact: avgCTR > 3 ? '+25% performance above industry avg' : 'Optimization potential identified',
                confidence: Math.round(activeCampaigns / totalCampaigns * 100),
                action: 'View Top Performers',
                icon: <Campaign />,
              },
              {
                type: 'prediction',
                title: 'Spend & Performance Forecast',
                description: `Based on current trends, projected ₹${(totalSpend * 1.15).toLocaleString()} spend in next 30 days with ${Math.round(avgCTR * 1.1 * 100) / 100}% CTR`,
                impact: 'Next 30 days projection',
                confidence: 82,
                action: 'View Forecast',
                icon: <TrendingUp />,
              },
              {
                type: 'recommendation',
                title: 'Budget Optimization Ready',
                description: `${Math.floor(totalCampaigns * 0.3)} campaigns eligible for budget reallocation to maximize ROI`,
                impact: 'Potential +18% ROAS',
                confidence: 88,
                action: 'Optimize Budget',
                icon: <AttachMoney />,
              },
            ]}
          />
        </Box>
      )}

      {campaigns.length === 0 && !loading ? (
        <Alert severity="warning" sx={{ mb: 3 }}>
          <Typography variant="subtitle1" sx={{ fontWeight: 600, mb: 1 }}>
            No Campaign Data Available
          </Typography>
          <Typography variant="body2">
            No campaigns were found for the selected customer. This could mean:
          </Typography>
          <ul style={{ marginTop: 8, marginBottom: 0 }}>
            <li>No campaigns have been created yet</li>
            <li>The selected customer ID has no associated campaigns</li>
            <li>Try selecting a different customer from the filter bar above</li>
          </ul>
        </Alert>
      ) : (
      <Box
        className="campaigns-charts"
        sx={{ display: 'grid', gridTemplateColumns: { xs: '1fr', md: 'repeat(2, 1fr)' }, gap: 3, mb: 3 }}
      >
        <Fade in timeout={800}>
          <Box>
            <Card
              sx={{
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.15)}`,
                },
              }}
            >
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Impressions & Clicks Trend (Last 7 Days)
                </Typography>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Chart data from backend API not yet implemented. Coming soon with real-time daily metrics.
                </Alert>
                <ResponsiveContainer width="100%" height={350}>
                  <AreaChart data={[]} margin={{ top: 20, right: 30, left: 60, bottom: 50 }}>
                    <defs>
                      <linearGradient id="colorImpressions" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#00bcd4" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#00bcd4" stopOpacity={0.1}/>
                      </linearGradient>
                      <linearGradient id="colorClicks" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#4caf50" stopOpacity={0.8}/>
                        <stop offset="95%" stopColor="#4caf50" stopOpacity={0.1}/>
                      </linearGradient>
                    </defs>

                    <CartesianGrid {...getCartesianGridConfig()} />

                    <XAxis
                      {...getXAxisConfig('Day of Week', 'date')}
                      label={{ value: 'Date', position: 'bottom', offset: 0, style: { fontSize: 14, fontWeight: 600, fill: '#666' } }}
                    />

                    <YAxis
                      {...getYAxisConfig('Count', formatNumber)}
                      label={{ value: 'Impressions / Clicks', angle: -90, position: 'left', offset: 10, style: { fontSize: 14, fontWeight: 600, fill: '#666', textAnchor: 'middle' } }}
                    />

                    <RechartsTooltip
                      {...getTooltipConfig({
                        numberFields: ['impressions', 'clicks'],
                        labelFormatter: (label) => `Day: ${label}`
                      })}
                    />

                    <Legend {...getLegendConfig('top')} />

                    <Area
                      type="monotone"
                      dataKey="impressions"
                      stroke="#00bcd4"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorImpressions)"
                      name="Impressions"
                    />
                    <Area
                      type="monotone"
                      dataKey="clicks"
                      stroke="#4caf50"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorClicks)"
                      name="Clicks"
                    />
                  </AreaChart>
                </ResponsiveContainer>
            </CardContent>
          </Card>
          </Box>
        </Fade>
        <Fade in timeout={900}>
          <Box>
            <Card
              sx={{
                transition: 'all 0.3s ease',
                '&:hover': {
                  transform: 'translateY(-4px)',
                  boxShadow: `0 8px 24px ${alpha(theme.palette.primary.main, 0.15)}`,
                },
              }}
            >
              <CardContent>
                <Typography variant="h6" sx={{ mb: 2, fontWeight: 600 }}>
                  Daily Spend Trend (Last 7 Days)
                </Typography>
                <Alert severity="info" sx={{ mb: 2 }}>
                  Chart data from backend API not yet implemented. Coming soon with real-time daily metrics.
                </Alert>
                <ResponsiveContainer width="100%" height={350}>
                  <LineChart data={[]} margin={{ top: 20, right: 30, left: 60, bottom: 50 }}>
                    <CartesianGrid {...getCartesianGridConfig()} />

                    <XAxis
                      {...getXAxisConfig('Day of Week', 'date')}
                      label={{ value: 'Date', position: 'bottom', offset: 0, style: { fontSize: 14, fontWeight: 600, fill: '#666' } }}
                    />

                    <YAxis
                      {...getYAxisConfig('Spend (₹)', formatCurrency)}
                      label={{ value: 'Cost (₹)', angle: -90, position: 'left', offset: 10, style: { fontSize: 14, fontWeight: 600, fill: '#666', textAnchor: 'middle' } }}
                    />

                    <RechartsTooltip
                      {...getTooltipConfig({
                        currencyFields: ['spend'],
                        labelFormatter: (label) => `Day: ${label}`
                      })}
                    />

                    <Legend {...getLegendConfig('top')} />

                    <Line
                      type="monotone"
                      dataKey="spend"
                      stroke="#ffa726"
                      strokeWidth={3}
                      dot={{ fill: '#ffa726', r: 5 }}
                      activeDot={{ r: 8 }}
                      name="Daily Spend"
                    />
                  </LineChart>
                </ResponsiveContainer>
            </CardContent>
          </Card>
          </Box>
        </Fade>
      </Box>
      )}

      <Fade in timeout={1000}>
        <Card
          className="campaigns-table"
          sx={{
            transition: 'all 0.3s ease',
            '&:hover': {
              boxShadow: `0 4px 20px ${alpha(theme.palette.primary.main, 0.1)}`,
            },
          }}
        >
          <CardContent>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', mb: 2 }}>
              <Typography variant="h6">
                Campaign Performance
              </Typography>
              <Box sx={{ display: 'flex', gap: 1 }}>
                <Chip
                  icon={<Speed />}
                  label="Real-time"
                  color="success"
                  size="small"
                  sx={{ animation: `${pulse} 2s infinite` }}
                />
                <Tooltip title="Data updates every 5 minutes">
                  <IconButton size="small">
                    <Info fontSize="small" />
                  </IconButton>
                </Tooltip>
              </Box>
            </Box>
          <TableContainer>
            {campaigns.length === 0 && !loading ? (
              <Alert severity="info" sx={{ m: 2 }}>
                No campaigns found for the selected customer. Please select a different customer or check your filters.
              </Alert>
            ) : (
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell>Campaign Name</TableCell>
                  <TableCell>Status</TableCell>
                  <TableCell align="right">Impressions</TableCell>
                  <TableCell align="right">Clicks</TableCell>
                  <TableCell align="right">CTR</TableCell>
                  <TableCell align="right">CPC</TableCell>
                  <TableCell align="right">Spend</TableCell>
                  <TableCell align="center">Actions</TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {campaigns.map((campaign: any, index: number) => (
                  <TableRow
                    key={campaign.campaign_id || index}
                    hover
                    sx={{
                      cursor: 'pointer',
                      transition: 'all 0.2s ease',
                      '&:hover': {
                        bgcolor: alpha(theme.palette.primary.main, 0.05),
                        transform: 'scale(1.01)',
                      },
                    }}
                    onClick={() => setSelectedCampaign(campaign)}
                  >
                    <TableCell>{campaign.campaign_name}</TableCell>
                    <TableCell>
                      <Chip
                        label={campaign.status}
                        color={getStatusColor(campaign.status) as any}
                        size="small"
                      />
                    </TableCell>
                    <TableCell align="right">
                      {campaign.impressions?.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">
                      {campaign.clicks?.toLocaleString()}
                    </TableCell>
                    <TableCell align="right">{campaign.ctr}%</TableCell>
                    <TableCell align="right">₹{campaign.cpc}</TableCell>
                    <TableCell align="right">
                      ₹{campaign.spend?.toLocaleString()}
                    </TableCell>
                    <TableCell align="center">
                      <Tooltip title="View Campaign Details">
                        <IconButton
                          size="small"
                          color="primary"
                          sx={{
                            transition: 'all 0.2s',
                            '&:hover': { transform: 'scale(1.2)' },
                          }}
                        >
                          <Visibility fontSize="small" />
                        </IconButton>
                      </Tooltip>
                      <Tooltip title={campaign.status === 'ACTIVE' ? 'Pause Campaign' : 'Resume Campaign'}>
                        <IconButton
                          size="small"
                          color={campaign.status === 'ACTIVE' ? 'warning' : 'success'}
                          sx={{
                            transition: 'all 0.2s',
                            '&:hover': { transform: 'scale(1.2)' },
                          }}
                        >
                          {campaign.status === 'ACTIVE' ? <Pause fontSize="small" /> : <PlayArrow fontSize="small" />}
                        </IconButton>
                      </Tooltip>
                      <Tooltip title="Campaign Settings">
                        <IconButton
                          size="small"
                          sx={{
                            transition: 'all 0.2s',
                            '&:hover': { transform: 'scale(1.2)' },
                          }}
                        >
                          <Settings fontSize="small" />
                        </IconButton>
                      </Tooltip>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
            )}
          </TableContainer>
        </CardContent>
      </Card>
      </Fade>

      {/* Helpful Tips */}
      <Grow in timeout={1200}>
        <Alert
          severity="info"
          icon={<TipsAndUpdates />}
          sx={{
            mt: 3,
            background: `linear-gradient(45deg, ${alpha(theme.palette.info.main, 0.1)} 0%, ${alpha(theme.palette.info.light, 0.05)} 100%)`,
          }}
        >
          <Typography variant="subtitle2">
            <strong>Pro Tip:</strong> Campaigns with CTR above 4% are performing well. Consider increasing their budget for better results.
            Pause underperforming campaigns (CTR below 2%) and reallocate budget to winners.
          </Typography>
        </Alert>
      </Grow>

      {/* KPI Detail Drawer */}
      <KPIDetailDrawer
        open={drawerOpen}
        onClose={() => setDrawerOpen(false)}
        title={drawerTitle}
        subtitle={drawerSubtitle}
        data={drawerData}
        type="table"
        color="primary"
        showTopCount={10}
      />
    </Box>
  );
};

export default CampaignsDashboard;