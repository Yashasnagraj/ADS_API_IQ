/**
 * Alerts Dashboard - Alert Agent
 *
 * Active alerts monitoring and management
 *
 * Features:
 * - Real-time alert feed
 * - Alerts by severity (Critical, Warning, Info)
 * - Alert filtering and sorting
 * - Alert acknowledgment
 * - Historical alert trends
 *
 * Structure:
 * - Header (Title + Description)
 * - Alert Summary Cards
 * - Active Alerts List
 * - Alert Trends Chart
 * - Alert History
 */

import React, { useState, useEffect, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  AlertTitle,
  Chip,
  CircularProgress,
  Divider,
  Button,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
  Paper,
  IconButton,
  Tooltip,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  Badge,
} from '@mui/material';
import {
  Notifications,
  Error as ErrorIcon,
  Warning as WarningIcon,
  Info as InfoIcon,
  CheckCircle,
  Check,
  Close,
  FilterList,
  TrendingUp,
  TrendingDown,
  AttachMoney,
  Speed,
  Mouse,
  Assessment,
  Psychology,
  Timeline,
  Lightbulb,
} from '@mui/icons-material';
import { useFilters } from '../../../../context/FilterContext';
import {
  BarChart,
  Bar,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip as RechartsTooltip,
  Legend,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
} from 'recharts';

interface AlertItem {
  alert_id: string;
  timestamp: string;
  campaign_name: string;
  metric_name: string;
  severity: 'critical' | 'warning' | 'info';
  message: string;
  current_value: number;
  threshold_value: number;
  deviation: number;
  status: 'active' | 'acknowledged' | 'resolved';
  action_required: boolean;
}

const AlertsDashboard: React.FC = () => {
  const { filters } = useFilters();
  const [severityFilter, setSeverityFilter] = useState<string>('all');
  const [statusFilter, setStatusFilter] = useState<string>('active');

  // Mock alerts data (in production, fetch from /ai/anomalies or dedicated alerts endpoint)
  const allAlerts = useMemo((): AlertItem[] => {
    const now = new Date();
    return [
      {
        alert_id: '1',
        timestamp: new Date(now.getTime() - 3600000).toISOString(),
        campaign_name: 'Eagle Diaries - Emcee Sons',
        metric_name: 'CPC',
        severity: 'critical',
        message: 'CPC spiked to $3.50, 180% above normal. Possible competitive attack or tracking error.',
        current_value: 3.50,
        threshold_value: 1.25,
        deviation: 180,
        status: 'active',
        action_required: true,
      },
      {
        alert_id: '2',
        timestamp: new Date(now.getTime() - 7200000).toISOString(),
        campaign_name: 'Carousel ads',
        metric_name: 'CTR',
        severity: 'warning',
        message: 'CTR dropped to 1.2%, down 40% from average. Ad fatigue or competitor activity detected.',
        current_value: 1.2,
        threshold_value: 2.0,
        deviation: -40,
        status: 'active',
        action_required: true,
      },
      {
        alert_id: '3',
        timestamp: new Date(now.getTime() - 10800000).toISOString(),
        campaign_name: '2021 Diaries',
        metric_name: 'Conversions',
        severity: 'critical',
        message: 'Zero conversions in last 24 hours. Possible tracking pixel issue or landing page error.',
        current_value: 0,
        threshold_value: 10,
        deviation: -100,
        status: 'active',
        action_required: true,
      },
      {
        alert_id: '4',
        timestamp: new Date(now.getTime() - 14400000).toISOString(),
        campaign_name: 'Fill Your Yoga Classes',
        metric_name: 'ROAS',
        severity: 'warning',
        message: 'ROAS dropped to 1.2x, below target of 2.0x. Review campaign performance.',
        current_value: 1.2,
        threshold_value: 2.0,
        deviation: -40,
        status: 'acknowledged',
        action_required: false,
      },
      {
        alert_id: '5',
        timestamp: new Date(now.getTime() - 18000000).toISOString(),
        campaign_name: 'Whatsappapicommunn',
        metric_name: 'Spend',
        severity: 'info',
        message: 'Daily spend exceeding budget by 15%. Consider adjusting bid strategy.',
        current_value: 575,
        threshold_value: 500,
        deviation: 15,
        status: 'active',
        action_required: false,
      },
      {
        alert_id: '6',
        timestamp: new Date(now.getTime() - 21600000).toISOString(),
        campaign_name: 'Bengaluru Orphanage',
        metric_name: 'Quality Score',
        severity: 'warning',
        message: 'Average quality score dropped to 4.2. Optimize ad relevance and landing page experience.',
        current_value: 4.2,
        threshold_value: 6.0,
        deviation: -30,
        status: 'resolved',
        action_required: false,
      },
    ];
  }, []);

  const filteredAlerts = useMemo(() => {
    return allAlerts.filter(alert => {
      const severityMatch = severityFilter === 'all' || alert.severity === severityFilter;
      const statusMatch = statusFilter === 'all' || alert.status === statusFilter;
      return severityMatch && statusMatch;
    });
  }, [allAlerts, severityFilter, statusFilter]);

  const alertSummary = useMemo(() => {
    const critical = allAlerts.filter(a => a.severity === 'critical' && a.status === 'active').length;
    const warning = allAlerts.filter(a => a.severity === 'warning' && a.status === 'active').length;
    const info = allAlerts.filter(a => a.severity === 'info' && a.status === 'active').length;
    const actionRequired = allAlerts.filter(a => a.action_required && a.status === 'active').length;

    return { critical, warning, info, total: critical + warning + info, actionRequired };
  }, [allAlerts]);

  const alertsBySeverity = useMemo(() => {
    return [
      { name: 'Critical', value: alertSummary.critical, color: '#f44336' },
      { name: 'Warning', value: alertSummary.warning, color: '#ff9800' },
      { name: 'Info', value: alertSummary.info, color: '#2196f3' },
    ];
  }, [alertSummary]);

  const alertTrends = useMemo(() => {
    // Mock trend data for last 7 days
    const data = [];
    for (let i = 6; i >= 0; i--) {
      const date = new Date();
      date.setDate(date.getDate() - i);
      data.push({
        date: date.toISOString().split('T')[0],
        critical: Math.floor(Math.random() * 3) + 1,
        warning: Math.floor(Math.random() * 5) + 2,
        info: Math.floor(Math.random() * 4) + 1,
      });
    }
    return data;
  }, []);

  const getSeverityIcon = (severity: string) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      case 'info':
        return <InfoIcon color="info" />;
      default:
        return <CheckCircle color="success" />;
    }
  };

  const getSeverityColor = (severity: string) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      case 'info':
        return 'info';
      default:
        return 'success';
    }
  };

  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / 3600000);
    const minutes = Math.floor((diff % 3600000) / 60000);

    if (hours > 24) return `${Math.floor(hours / 24)}d ago`;
    if (hours > 0) return `${hours}h ago`;
    return `${minutes}m ago`;
  };

  // AI Analysis - 4 Types (Alert Intelligence focus)
  const aiAnalysis = useMemo(() => {
    const criticalAlerts = allAlerts.filter(a => a.severity === 'critical' && a.status === 'active');
    const warningAlerts = allAlerts.filter(a => a.severity === 'warning' && a.status === 'active');
    const recentAlerts = allAlerts.filter(a => {
      const hoursAgo = (new Date().getTime() - new Date(a.timestamp).getTime()) / 3600000;
      return hoursAgo <= 24;
    });

    // 1. DESCRIPTIVE: Current alert landscape
    const metricBreakdown = allAlerts.reduce((acc, alert) => {
      acc[alert.metric_name] = (acc[alert.metric_name] || 0) + 1;
      return acc;
    }, {} as Record<string, number>);

    const mostAffectedMetric = Object.entries(metricBreakdown).reduce((max, [metric, count]) =>
      count > max[1] ? [metric, count] : max, ['', 0]);

    const avgDeviationCritical = criticalAlerts.length > 0
      ? criticalAlerts.reduce((sum, a) => sum + Math.abs(a.deviation), 0) / criticalAlerts.length
      : 0;

    const descriptive = `Alert Status Overview:\n• ${alertSummary.total} active alerts requiring attention\n• ${alertSummary.critical} critical (immediate action needed)\n• ${alertSummary.warning} warnings (monitor closely)\n• ${alertSummary.info} informational alerts\n\nAlert Distribution:\n• ${recentAlerts.length} alerts triggered in last 24 hours\n• Most affected metric: ${mostAffectedMetric[0]} (${mostAffectedMetric[1]} alerts)\n• ${alertSummary.actionRequired} alerts require immediate action\n\nSeverity Breakdown:\n• Critical avg deviation: ${avgDeviationCritical.toFixed(1)}% from threshold\n• ${allAlerts.filter(a => a.status === 'acknowledged').length} alerts acknowledged\n• ${allAlerts.filter(a => a.status === 'resolved').length} alerts resolved`;

    // 2. DIAGNOSTIC: Root causes
    let diagnostic = `Alert Root Cause Analysis:\n\n`;

    const cpcAlerts = allAlerts.filter(a => a.metric_name === 'CPC' && a.status === 'active');
    const ctrAlerts = allAlerts.filter(a => a.metric_name === 'CTR' && a.status === 'active');
    const conversionAlerts = allAlerts.filter(a => a.metric_name === 'Conversions' && a.status === 'active');

    if (cpcAlerts.length > 0) {
      diagnostic += `CPC Spike Patterns (${cpcAlerts.length} alerts):\n• Potential causes: Competitive pressure, bid wars, or tracking errors\n• Avg deviation: ${(cpcAlerts.reduce((sum, a) => sum + Math.abs(a.deviation), 0) / cpcAlerts.length).toFixed(0)}% above normal\n\n`;
    }

    if (ctrAlerts.length > 0) {
      diagnostic += `CTR Decline Analysis (${ctrAlerts.length} alerts):\n• Likely drivers: Ad fatigue, competitor activity, or seasonal drop\n• Requires creative refresh or audience retargeting\n\n`;
    }

    if (conversionAlerts.length > 0) {
      diagnostic += `Conversion Issues (${conversionAlerts.length} alerts):\n• Critical: Possible tracking pixel failure or landing page errors\n• Requires immediate technical investigation\n\n`;
    }

    if (criticalAlerts.length > 3) {
      diagnostic += `⚠️ High critical alert volume indicates systematic issues - not isolated incidents`;
    } else if (criticalAlerts.length === 0 && warningAlerts.length > 5) {
      diagnostic += `Multiple warnings suggest trending problems - monitor for escalation`;
    }

    // 3. PREDICTIVE: Alert trends & escalation risks
    const hoursSinceOldest = criticalAlerts.length > 0
      ? (new Date().getTime() - new Date(criticalAlerts[criticalAlerts.length - 1].timestamp).getTime()) / 3600000
      : 0;

    const escalationRisk = criticalAlerts.length > 3 ? 'High' : warningAlerts.length > 5 ? 'Medium' : 'Low';

    const predictive = `Alert Trend Forecast:\n\nEscalation Risk Assessment:\n• Risk level: ${escalationRisk}\n• ${criticalAlerts.length} critical alerts unresolved (avg age: ${hoursSinceOldest.toFixed(1)}h)\n• Alert velocity: ${recentAlerts.length} new alerts in 24h\n\nPredicted Impact:\n• If unaddressed: ${criticalAlerts.length > 0 ? `Potential revenue loss $${(criticalAlerts.length * 500).toFixed(0)}/day` : 'Minimal financial impact'}\n• Response time SLA: ${alertSummary.actionRequired > 5 ? 'At risk' : 'On track'}\n\nTrend Analysis:\n• Alert frequency ${recentAlerts.length > 5 ? 'increasing' : recentAlerts.length > 2 ? 'stable' : 'decreasing'}\n• Pattern recognition: ${mostAffectedMetric[1] > 3 ? `Recurring ${mostAffectedMetric[0]} issues` : 'Isolated incidents'}`;

    // 4. PRESCRIPTIVE: Alert response recommendations
    const recommendations: string[] = [];

    if (conversionAlerts.length > 0) {
      recommendations.push(`1. URGENT: Investigate ${conversionAlerts.length} conversion tracking alerts - check pixel & landing pages`);
    } else if (criticalAlerts.length > 0) {
      recommendations.push(`1. Address ${criticalAlerts.length} critical alerts within 2 hours - prioritize by revenue impact`);
    }

    if (cpcAlerts.length > 2) {
      recommendations.push(`2. Review bid strategy for ${cpcAlerts.length} campaigns with CPC spikes - consider bid caps`);
    }

    if (ctrAlerts.length > 0) {
      recommendations.push(`${recommendations.length + 1}. Refresh ad creatives for ${ctrAlerts.length} low-CTR campaigns - test new messaging`);
    }

    if (alertSummary.total > 10) {
      recommendations.push(`${recommendations.length + 1}. Alert volume high (${alertSummary.total}) - review threshold settings to reduce noise`);
    } else {
      recommendations.push(`${recommendations.length + 1}. Current alert volume optimal - thresholds well-calibrated`);
    }

    const prescriptive = `Alert Response Plan:\n${recommendations.slice(0, 4).join('\n')}\n\nAction Priority Matrix:\n• Critical alerts: Resolve within 2 hours\n• Warnings: Investigate within 24 hours\n• Info: Review during weekly optimization\n\nSuccess metrics: ${alertSummary.total} alerts → target <5 active within 48h`;

    return {
      descriptive: {
        text: descriptive,
        icon: Assessment,
        color: '#1E88E5',
      },
      diagnostic: {
        text: diagnostic,
        icon: Psychology,
        color: '#7B1FA2',
      },
      predictive: {
        text: predictive,
        icon: Timeline,
        color: '#F57C00',
      },
      prescriptive: {
        text: prescriptive,
        icon: Lightbulb,
        color: '#388E3C',
      },
    };
  }, [allAlerts, alertSummary]);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Badge badgeContent={alertSummary.total} color="error">
            <Notifications fontSize="large" color="primary" />
          </Badge>
          Alerts Dashboard
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Real-time monitoring of campaign performance alerts and anomalies
        </Typography>
      </Box>

      {/* AI Intelligence */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h5" fontWeight={600} gutterBottom sx={{ mb: 3 }}>
          🧠 AI Intelligence
        </Typography>

        <Grid container spacing={2.5}>
          {/* 1. Descriptive */}
          <Grid item xs={12} md={6}>
            <Card
              elevation={0}
              sx={{
                height: '100%',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                transition: 'all 0.3s',
                '&:hover': {
                  boxShadow: `0 4px 20px ${aiAnalysis.descriptive.color}20`,
                  borderColor: aiAnalysis.descriptive.color,
                }
              }}
            >
              <CardContent sx={{ p: 2.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box
                    sx={{
                      width: 36,
                      height: 36,
                      borderRadius: 1.5,
                      bgcolor: `${aiAnalysis.descriptive.color}10`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Assessment sx={{ color: aiAnalysis.descriptive.color, fontSize: 20 }} />
                  </Box>
                  <Box flex={1}>
                    <Typography variant="subtitle2" sx={{ color: aiAnalysis.descriptive.color, fontWeight: 600 }}>
                      Descriptive
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Alert landscape
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.secondary' }}>
                  {aiAnalysis.descriptive.text}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* 2. Diagnostic */}
          <Grid item xs={12} md={6}>
            <Card
              elevation={0}
              sx={{
                height: '100%',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                transition: 'all 0.3s',
                '&:hover': {
                  boxShadow: `0 4px 20px ${aiAnalysis.diagnostic.color}20`,
                  borderColor: aiAnalysis.diagnostic.color,
                }
              }}
            >
              <CardContent sx={{ p: 2.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box
                    sx={{
                      width: 36,
                      height: 36,
                      borderRadius: 1.5,
                      bgcolor: `${aiAnalysis.diagnostic.color}10`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Psychology sx={{ color: aiAnalysis.diagnostic.color, fontSize: 20 }} />
                  </Box>
                  <Box flex={1}>
                    <Typography variant="subtitle2" sx={{ color: aiAnalysis.diagnostic.color, fontWeight: 600 }}>
                      Diagnostic
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Root causes
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.secondary' }}>
                  {aiAnalysis.diagnostic.text}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* 3. Predictive */}
          <Grid item xs={12} md={6}>
            <Card
              elevation={0}
              sx={{
                height: '100%',
                border: '1px solid',
                borderColor: 'divider',
                borderRadius: 2,
                transition: 'all 0.3s',
                '&:hover': {
                  boxShadow: `0 4px 20px ${aiAnalysis.predictive.color}20`,
                  borderColor: aiAnalysis.predictive.color,
                }
              }}
            >
              <CardContent sx={{ p: 2.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box
                    sx={{
                      width: 36,
                      height: 36,
                      borderRadius: 1.5,
                      bgcolor: `${aiAnalysis.predictive.color}10`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Timeline sx={{ color: aiAnalysis.predictive.color, fontSize: 20 }} />
                  </Box>
                  <Box flex={1}>
                    <Typography variant="subtitle2" sx={{ color: aiAnalysis.predictive.color, fontWeight: 600 }}>
                      Predictive
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Trend forecast
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.secondary' }}>
                  {aiAnalysis.predictive.text}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          {/* 4. Prescriptive */}
          <Grid item xs={12} md={6}>
            <Card
              elevation={0}
              sx={{
                height: '100%',
                border: '1px solid',
                borderColor: aiAnalysis.prescriptive.color,
                borderRadius: 2,
                background: `linear-gradient(135deg, ${aiAnalysis.prescriptive.color}08 0%, ${aiAnalysis.prescriptive.color}03 100%)`,
                transition: 'all 0.3s',
                '&:hover': {
                  boxShadow: `0 4px 20px ${aiAnalysis.prescriptive.color}25`,
                }
              }}
            >
              <CardContent sx={{ p: 2.5 }}>
                <Box sx={{ display: 'flex', alignItems: 'center', gap: 1.5, mb: 2 }}>
                  <Box
                    sx={{
                      width: 36,
                      height: 36,
                      borderRadius: 1.5,
                      bgcolor: `${aiAnalysis.prescriptive.color}15`,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                    }}
                  >
                    <Lightbulb sx={{ color: aiAnalysis.prescriptive.color, fontSize: 20 }} />
                  </Box>
                  <Box flex={1}>
                    <Typography variant="subtitle2" sx={{ color: aiAnalysis.prescriptive.color, fontWeight: 600 }}>
                      Prescriptive
                    </Typography>
                    <Typography variant="caption" color="text.secondary">
                      Response plan
                    </Typography>
                  </Box>
                </Box>
                <Typography variant="body2" sx={{ whiteSpace: 'pre-line', lineHeight: 1.7, color: 'text.primary', fontWeight: 500 }}>
                  {aiAnalysis.prescriptive.text}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Box>

      {/* Summary Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f44336 0%, #e91e63 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Critical Alerts</Typography>
                  <Typography variant="h2" fontWeight={700}>{alertSummary.critical}</Typography>
                </Box>
                <ErrorIcon sx={{ fontSize: 60, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #ff9800 0%, #fb8c00 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Warning Alerts</Typography>
                  <Typography variant="h2" fontWeight={700}>{alertSummary.warning}</Typography>
                </Box>
                <WarningIcon sx={{ fontSize: 60, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Info Alerts</Typography>
                  <Typography variant="h2" fontWeight={700}>{alertSummary.info}</Typography>
                </Box>
                <InfoIcon sx={{ fontSize: 60, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Action Required</Typography>
                  <Typography variant="h2" fontWeight={700}>{alertSummary.actionRequired}</Typography>
                </Box>
                <Notifications sx={{ fontSize: 60, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Filters */}
      <Grid container spacing={2} sx={{ mb: 3 }}>
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Severity</InputLabel>
            <Select value={severityFilter} onChange={(e) => setSeverityFilter(e.target.value)} label="Severity">
              <MenuItem value="all">All Severities</MenuItem>
              <MenuItem value="critical">Critical</MenuItem>
              <MenuItem value="warning">Warning</MenuItem>
              <MenuItem value="info">Info</MenuItem>
            </Select>
          </FormControl>
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <FormControl fullWidth size="small">
            <InputLabel>Status</InputLabel>
            <Select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} label="Status">
              <MenuItem value="all">All Statuses</MenuItem>
              <MenuItem value="active">Active</MenuItem>
              <MenuItem value="acknowledged">Acknowledged</MenuItem>
              <MenuItem value="resolved">Resolved</MenuItem>
            </Select>
          </FormControl>
        </Grid>
      </Grid>

      {/* Severity Distribution Chart */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Alerts by Severity
              </Typography>
              <Divider sx={{ my: 2 }} />
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={alertsBySeverity}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={(entry) => `${entry.name}: ${entry.value}`}
                    outerRadius={100}
                    fill="#8884d8"
                    dataKey="value"
                  >
                    {alertsBySeverity.map((entry, index) => (
                      <Cell key={`cell-${index}`} fill={entry.color} />
                    ))}
                  </Pie>
                  <RechartsTooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} md={6}>
          <Card>
            <CardContent>
              <Typography variant="h6" fontWeight={600} gutterBottom>
                Alert Trends (Last 7 Days)
              </Typography>
              <Divider sx={{ my: 2 }} />
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={alertTrends}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="date" tickFormatter={(value) => {
                    const date = new Date(value);
                    return `${date.getMonth() + 1}/${date.getDate()}`;
                  }} />
                  <YAxis />
                  <RechartsTooltip />
                  <Legend />
                  <Bar dataKey="critical" fill="#f44336" stackId="a" name="Critical" />
                  <Bar dataKey="warning" fill="#ff9800" stackId="a" name="Warning" />
                  <Bar dataKey="info" fill="#2196f3" stackId="a" name="Info" />
                </BarChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Active Alerts List */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Active Alerts ({filteredAlerts.length})
          </Typography>
          <Divider sx={{ my: 2 }} />

          {filteredAlerts.length === 0 ? (
            <Box sx={{ textAlign: 'center', py: 4 }}>
              <CheckCircle sx={{ fontSize: 60, color: '#43e97b', mb: 2 }} />
              <Typography variant="h6" color="text.secondary">
                No alerts matching your filters
              </Typography>
            </Box>
          ) : (
            <List>
              {filteredAlerts.map((alert) => (
                <ListItem
                  key={alert.alert_id}
                  sx={{
                    flexDirection: 'column',
                    alignItems: 'flex-start',
                    borderLeft: `4px solid ${alert.severity === 'critical' ? '#f44336' : alert.severity === 'warning' ? '#ff9800' : '#2196f3'}`,
                    borderBottom: '1px solid #eee',
                    py: 2,
                  }}
                >
                  <Box sx={{ display: 'flex', width: '100%', justifyContent: 'space-between', alignItems: 'flex-start', mb: 1 }}>
                    <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                      {getSeverityIcon(alert.severity)}
                      <Box>
                        <Typography variant="subtitle1" fontWeight={600}>
                          {alert.campaign_name} - {alert.metric_name}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {formatTimestamp(alert.timestamp)}
                        </Typography>
                      </Box>
                    </Box>
                    <Box sx={{ display: 'flex', gap: 1 }}>
                      <Chip
                        label={alert.severity.toUpperCase()}
                        size="small"
                        color={getSeverityColor(alert.severity) as any}
                      />
                      <Chip
                        label={alert.status.toUpperCase()}
                        size="small"
                        variant={alert.status === 'active' ? 'filled' : 'outlined'}
                      />
                    </Box>
                  </Box>

                  <Typography variant="body2" paragraph sx={{ mb: 2 }}>
                    {alert.message}
                  </Typography>

                  <Grid container spacing={2} sx={{ mb: 2 }}>
                    <Grid item xs={12} sm={4}>
                      <Paper sx={{ p: 1.5, background: '#fff3e0' }}>
                        <Typography variant="caption" color="text.secondary">Current Value</Typography>
                        <Typography variant="h6" fontWeight={600}>{alert.current_value}</Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Paper sx={{ p: 1.5, background: '#e3f2fd' }}>
                        <Typography variant="caption" color="text.secondary">Threshold</Typography>
                        <Typography variant="h6" fontWeight={600}>{alert.threshold_value}</Typography>
                      </Paper>
                    </Grid>
                    <Grid item xs={12} sm={4}>
                      <Paper sx={{ p: 1.5, background: '#fce4ec' }}>
                        <Typography variant="caption" color="text.secondary">Deviation</Typography>
                        <Typography variant="h6" fontWeight={600} color="error">
                          {alert.deviation > 0 ? '+' : ''}{alert.deviation}%
                        </Typography>
                      </Paper>
                    </Grid>
                  </Grid>

                  <Box sx={{ display: 'flex', gap: 1 }}>
                    {alert.status === 'active' && (
                      <>
                        <Button size="small" variant="contained" color="primary" startIcon={<Check />}>
                          Acknowledge
                        </Button>
                        <Button size="small" variant="outlined" color="success" startIcon={<CheckCircle />}>
                          Resolve
                        </Button>
                      </>
                    )}
                    <Button size="small" variant="text" color="inherit">
                      View Campaign
                    </Button>
                  </Box>
                </ListItem>
              ))}
            </List>
          )}
        </CardContent>
      </Card>

      {/* Quick Actions */}
      <Card sx={{ background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)' }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Quick Actions
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} sm={6} md={3}>
              <Button fullWidth variant="outlined" startIcon={<CheckCircle />}>
                Acknowledge All
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button fullWidth variant="outlined" startIcon={<FilterList />}>
                Export Alerts
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button fullWidth variant="outlined" startIcon={<Notifications />}>
                Alert Settings
              </Button>
            </Grid>
            <Grid item xs={12} sm={6} md={3}>
              <Button fullWidth variant="outlined" startIcon={<Close />}>
                Clear Resolved
              </Button>
            </Grid>
          </Grid>
        </CardContent>
      </Card>
    </Box>
  );
};

export default AlertsDashboard;
