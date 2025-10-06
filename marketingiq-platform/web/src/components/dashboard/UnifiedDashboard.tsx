import React, { useState, useEffect } from 'react';
import {
  Box,
  Grid,
  Card,
  CardContent,
  Typography,
  Paper,
  Button,
  IconButton,
  Chip,
  Avatar,
  Badge,
  Tooltip,
  LinearProgress,
  CircularProgress,
  Fade,
  Grow,
  Zoom,
  Slide,
  useTheme,
  alpha,
  Divider,
} from '@mui/material';
import {
  Dashboard,
  TrendingUp,
  TrendingDown,
  MonetizationOn,
  Campaign,
  Category,
  Tag,
  Search,
  Assessment,
  Timeline,
  Insights,
  Lightbulb,
  Warning,
  CheckCircle,
  Error,
  Speed,
  AutoAwesome,
  ElectricBolt,
  Psychology,
  AutoFixHigh,
  Refresh,
  Download,
  Share,
  Notifications,
  Settings,
  WbSunny,
  DarkMode,
} from '@mui/icons-material';
import { keyframes } from '@mui/system';
import AnimatedKPICard from '../common/AnimatedKPICard';
import {
  AreaChart,
  Area,
  BarChart,
  Bar,
  LineChart,
  Line,
  PieChart,
  Pie,
  Cell,
  RadialBarChart,
  RadialBar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';
import { useNavigate } from 'react-router-dom';

// Animations
const float = keyframes`
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
`;

const glow = keyframes`
  0%, 100% { box-shadow: 0 0 20px rgba(99, 102, 241, 0.4); }
  50% { box-shadow: 0 0 40px rgba(99, 102, 241, 0.8); }
`;

const pulse = keyframes`
  0% { transform: scale(1); }
  50% { transform: scale(1.05); }
  100% { transform: scale(1); }
`;

const shimmer = keyframes`
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
`;

const UnifiedDashboard: React.FC = () => {
  const theme = useTheme();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [selectedPeriod, setSelectedPeriod] = useState('7d');
  const [notifications, setNotifications] = useState(3);

  useEffect(() => {
    setTimeout(() => setLoading(false), 1500);
  }, []);

  // Overall KPIs
  const mainKPIs = [
    {
      title: 'Total Revenue',
      value: 2456789,
      format: 'currency' as const,
      icon: <MonetizationOn />,
      trend: 'up' as const,
      trendValue: 12.5,
      sparklineData: [200, 220, 215, 240, 235, 260, 255, 280, 290, 310],
      color: 'success' as const,
      target: 3000000,
      showProgress: true,
      glowEffect: true,
    },
    {
      title: 'Active Campaigns',
      value: 45,
      format: 'number' as const,
      icon: <Campaign />,
      trend: 'up' as const,
      trendValue: 5.2,
      sparklineData: [40, 41, 42, 43, 42, 44, 43, 45, 44, 45],
      color: 'primary' as const,
    },
    {
      title: 'Conversion Rate',
      value: 4.23,
      format: 'percentage' as const,
      icon: <TrendingUp />,
      trend: 'up' as const,
      trendValue: 8.3,
      sparklineData: [3.8, 3.9, 4.0, 4.05, 4.1, 4.15, 4.18, 4.2, 4.22, 4.23],
      color: 'info' as const,
      pulseOnHigh: true,
    },
    {
      title: 'Avg. CPC',
      value: 2.18,
      format: 'currency' as const,
      icon: <Speed />,
      trend: 'down' as const,
      trendValue: -6.7,
      sparklineData: [2.4, 2.35, 2.3, 2.28, 2.25, 2.22, 2.2, 2.19, 2.18, 2.18],
      color: 'warning' as const,
    },
  ];

  // Quick insights
  const quickInsights = [
    {
      type: 'success',
      title: 'Top Performer',
      description: 'Campaign "Summer Sale" exceeds targets by 35%',
      icon: <CheckCircle />,
      action: 'View Campaign',
      route: '/data/campaigns',
    },
    {
      type: 'warning',
      title: 'Budget Alert',
      description: '3 campaigns approaching daily budget limit',
      icon: <Warning />,
      action: 'Adjust Budgets',
      route: '/optimization/budget',
    },
    {
      type: 'info',
      title: 'AI Recommendation',
      description: 'Enable smart bidding for 5 eligible campaigns',
      icon: <Psychology />,
      action: 'Review',
      route: '/optimization/simulator',
    },
  ];

  // Performance data
  const performanceData = [
    { name: 'Mon', revenue: 320000, conversions: 1200, ctr: 3.2 },
    { name: 'Tue', revenue: 350000, conversions: 1350, ctr: 3.5 },
    { name: 'Wed', revenue: 330000, conversions: 1250, ctr: 3.3 },
    { name: 'Thu', revenue: 380000, conversions: 1450, ctr: 3.8 },
    { name: 'Fri', revenue: 420000, conversions: 1600, ctr: 4.2 },
    { name: 'Sat', revenue: 380000, conversions: 1400, ctr: 3.7 },
    { name: 'Sun', revenue: 360000, conversions: 1300, ctr: 3.5 },
  ];

  const channelPerformance = [
    { channel: 'Search', value: 45, fill: '#6366f1' },
    { channel: 'Display', value: 25, fill: '#8b5cf6' },
    { channel: 'Video', value: 15, fill: '#3b82f6' },
    { channel: 'Shopping', value: 10, fill: '#10b981' },
    { channel: 'Other', value: 5, fill: '#f59e0b' },
  ];

  const handleNavigate = (path: string) => {
    navigate(path);
  };

  return (
    <Box sx={{ p: 3, minHeight: '100vh' }}>
      {/* Header */}
      <Fade in timeout={500}>
        <Paper
          elevation={0}
          sx={{
            p: 3,
            mb: 4,
            background: `linear-gradient(135deg, ${alpha(theme.palette.primary.main, 0.05)} 0%, ${alpha(
              theme.palette.secondary.main,
              0.05
            )} 100%)`,
            borderRadius: 3,
            position: 'relative',
            overflow: 'hidden',
            '&::before': {
              content: '""',
              position: 'absolute',
              top: 0,
              left: '-100%',
              width: '200%',
              height: '4px',
              background: `linear-gradient(90deg, transparent, ${theme.palette.primary.main}, transparent)`,
              animation: `${shimmer} 3s linear infinite`,
            },
          }}
        >
          <Grid container alignItems="center" justifyContent="space-between">
            <Grid item>
              <Box display="flex" alignItems="center" gap={2}>
                <Avatar
                  sx={{
                    width: 56,
                    height: 56,
                    bgcolor: theme.palette.primary.main,
                    animation: `${float} 3s ease-in-out infinite`,
                  }}
                >
                  <Dashboard fontSize="large" />
                </Avatar>
                <Box>
                  <Typography
                    variant="h4"
                    fontWeight="bold"
                    sx={{
                      background: `linear-gradient(135deg, ${theme.palette.primary.main}, ${theme.palette.secondary.main})`,
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                    }}
                  >
                    MarketingIQ Command Center
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Real-time analytics and AI-powered insights across all campaigns
                  </Typography>
                </Box>
              </Box>
            </Grid>
            <Grid item>
              <Box display="flex" alignItems="center" gap={2}>
                <Chip
                  label={selectedPeriod === '7d' ? 'Last 7 Days' : 'Last 30 Days'}
                  onClick={() => setSelectedPeriod(selectedPeriod === '7d' ? '30d' : '7d')}
                  color="primary"
                  sx={{ fontWeight: 600 }}
                />
                <Badge badgeContent={notifications} color="error">
                  <IconButton>
                    <Notifications />
                  </IconButton>
                </Badge>
                <IconButton>
                  <Refresh />
                </IconButton>
                <IconButton>
                  <Settings />
                </IconButton>
              </Box>
            </Grid>
          </Grid>
        </Paper>
      </Fade>

      {/* Main KPIs */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {mainKPIs.map((kpi, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Zoom in timeout={600 + index * 100}>
              <Box>
                <AnimatedKPICard
                  {...kpi}
                  animationDelay={index * 0.1}
                  loading={loading}
                  onClick={() => handleNavigate('/data/campaigns')}
                />
              </Box>
            </Zoom>
          </Grid>
        ))}
      </Grid>

      {/* Quick Actions & Insights */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={8}>
          <Slide in direction="up" timeout={800}>
            <Card
              sx={{
                height: '100%',
                background: theme.palette.background.paper,
                '&:hover': { boxShadow: theme.shadows[8] },
                transition: 'all 0.3s ease',
              }}
            >
              <CardContent>
                <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
                  <Typography variant="h6" fontWeight="600">
                    Performance Overview
                  </Typography>
                  <Box display="flex" gap={1}>
                    <Chip
                      size="small"
                      label="Revenue"
                      sx={{ bgcolor: alpha('#6366f1', 0.1), color: '#6366f1' }}
                    />
                    <Chip
                      size="small"
                      label="Conversions"
                      sx={{ bgcolor: alpha('#10b981', 0.1), color: '#10b981' }}
                    />
                    <Chip
                      size="small"
                      label="CTR"
                      sx={{ bgcolor: alpha('#f59e0b', 0.1), color: '#f59e0b' }}
                    />
                  </Box>
                </Box>
                <ResponsiveContainer width="100%" height={300}>
                  <AreaChart data={performanceData}>
                    <defs>
                      <linearGradient id="colorRevenue" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#6366f1" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#6366f1" stopOpacity={0} />
                      </linearGradient>
                      <linearGradient id="colorConversions" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.3} />
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0} />
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" stroke={alpha(theme.palette.divider, 0.2)} />
                    <XAxis dataKey="name" stroke={theme.palette.text.secondary} />
                    <YAxis stroke={theme.palette.text.secondary} />
                    <RechartsTooltip
                      contentStyle={{
                        backgroundColor: alpha(theme.palette.background.paper, 0.95),
                        border: `1px solid ${theme.palette.divider}`,
                        borderRadius: 8,
                      }}
                    />
                    <Area
                      type="monotone"
                      dataKey="revenue"
                      stroke="#6366f1"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorRevenue)"
                    />
                    <Area
                      type="monotone"
                      dataKey="conversions"
                      stroke="#10b981"
                      strokeWidth={2}
                      fillOpacity={1}
                      fill="url(#colorConversions)"
                    />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>
          </Slide>
        </Grid>

        <Grid item xs={12} md={4}>
          <Slide in direction="up" timeout={900}>
            <Card
              sx={{
                height: '100%',
                '&:hover': { boxShadow: theme.shadows[8] },
                transition: 'all 0.3s ease',
              }}
            >
              <CardContent>
                <Typography variant="h6" fontWeight="600" mb={3}>
                  Channel Performance
                </Typography>
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={channelPerformance}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={100}
                      paddingAngle={5}
                      dataKey="value"
                    >
                      {channelPerformance.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.fill} />
                      ))}
                    </Pie>
                    <RechartsTooltip />
                  </PieChart>
                </ResponsiveContainer>
                <Box mt={2}>
                  {channelPerformance.map((channel, index) => (
                    <Box key={index} display="flex" justifyContent="space-between" alignItems="center" mb={1}>
                      <Box display="flex" alignItems="center" gap={1}>
                        <Box
                          sx={{
                            width: 12,
                            height: 12,
                            borderRadius: '50%',
                            bgcolor: channel.fill,
                          }}
                        />
                        <Typography variant="body2">{channel.channel}</Typography>
                      </Box>
                      <Typography variant="body2" fontWeight="600">
                        {channel.value}%
                      </Typography>
                    </Box>
                  ))}
                </Box>
              </CardContent>
            </Card>
          </Slide>
        </Grid>
      </Grid>

      {/* Quick Insights */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        {quickInsights.map((insight, index) => (
          <Grid item xs={12} md={4} key={index}>
            <Grow in timeout={700 + index * 100}>
              <Card
                sx={{
                  cursor: 'pointer',
                  borderLeft: `4px solid ${
                    insight.type === 'success'
                      ? theme.palette.success.main
                      : insight.type === 'warning'
                      ? theme.palette.warning.main
                      : theme.palette.info.main
                  }`,
                  '&:hover': {
                    transform: 'translateY(-4px)',
                    boxShadow: theme.shadows[8],
                  },
                  transition: 'all 0.3s ease',
                  ...(insight.type === 'warning' && {
                    animation: `${pulse} 2s infinite`,
                  }),
                }}
                onClick={() => handleNavigate(insight.route)}
              >
                <CardContent>
                  <Box display="flex" alignItems="center" mb={2}>
                    <Avatar
                      sx={{
                        bgcolor:
                          insight.type === 'success'
                            ? alpha(theme.palette.success.main, 0.1)
                            : insight.type === 'warning'
                            ? alpha(theme.palette.warning.main, 0.1)
                            : alpha(theme.palette.info.main, 0.1),
                        color:
                          insight.type === 'success'
                            ? theme.palette.success.main
                            : insight.type === 'warning'
                            ? theme.palette.warning.main
                            : theme.palette.info.main,
                        mr: 2,
                      }}
                    >
                      {insight.icon}
                    </Avatar>
                    <Box flex={1}>
                      <Typography variant="subtitle2" fontWeight="600">
                        {insight.title}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {insight.description}
                      </Typography>
                    </Box>
                  </Box>
                  <Button
                    variant="outlined"
                    size="small"
                    color={insight.type === 'success' ? 'success' : insight.type === 'warning' ? 'warning' : 'info'}
                    startIcon={<AutoAwesome />}
                    fullWidth
                  >
                    {insight.action}
                  </Button>
                </CardContent>
              </Card>
            </Grow>
          </Grid>
        ))}
      </Grid>

      {/* Analytics Navigation Cards */}
      <Typography variant="h5" fontWeight="600" sx={{ mb: 3 }}>
        Analytics & Insights
      </Typography>
      <Grid container spacing={3}>
        {[
          {
            title: 'Descriptive Analytics',
            description: 'What happened? View historical performance and trends',
            icon: <Assessment />,
            color: theme.palette.primary.main,
            route: '/data/campaigns',
            stats: '15 Active Reports',
          },
          {
            title: 'Diagnostic Analytics',
            description: 'Why did it happen? Understand root causes',
            icon: <Insights />,
            color: theme.palette.secondary.main,
            route: '/insights/summary',
            stats: '8 New Insights',
          },
          {
            title: 'Predictive Analytics',
            description: 'What will happen? Forecast future performance',
            icon: <Timeline />,
            color: theme.palette.info.main,
            route: '/forecasting/scenarios',
            stats: '92% Accuracy',
          },
          {
            title: 'Prescriptive Analytics',
            description: 'What should you do? Get AI recommendations',
            icon: <Lightbulb />,
            color: theme.palette.success.main,
            route: '/optimization/simulator',
            stats: '23 Recommendations',
          },
        ].map((item, index) => (
          <Grid item xs={12} sm={6} md={3} key={index}>
            <Zoom in timeout={800 + index * 100}>
              <Card
                sx={{
                  cursor: 'pointer',
                  height: '100%',
                  background: `linear-gradient(135deg, ${alpha(item.color, 0.05)} 0%, ${alpha(
                    item.color,
                    0.1
                  )} 100%)`,
                  borderTop: `3px solid ${item.color}`,
                  '&:hover': {
                    transform: 'translateY(-8px)',
                    boxShadow: theme.shadows[12],
                    '& .icon-container': {
                      animation: `${pulse} 1s infinite`,
                    },
                  },
                  transition: 'all 0.3s ease',
                }}
                onClick={() => handleNavigate(item.route)}
              >
                <CardContent>
                  <Box
                    className="icon-container"
                    sx={{
                      width: 60,
                      height: 60,
                      borderRadius: 2,
                      bgcolor: alpha(item.color, 0.1),
                      color: item.color,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      mb: 2,
                    }}
                  >
                    {item.icon}
                  </Box>
                  <Typography variant="h6" fontWeight="600" gutterBottom>
                    {item.title}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                    {item.description}
                  </Typography>
                  <Chip label={item.stats} size="small" sx={{ bgcolor: alpha(item.color, 0.1), color: item.color }} />
                </CardContent>
              </Card>
            </Zoom>
          </Grid>
        ))}
      </Grid>
    </Box>
  );
};

export default UnifiedDashboard;