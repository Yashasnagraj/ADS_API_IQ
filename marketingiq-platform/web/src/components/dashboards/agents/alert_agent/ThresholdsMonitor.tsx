/**
 * Thresholds Monitor Dashboard - Alert Agent
 *
 * Configure and monitor performance thresholds
 *
 * Features:
 * - Configurable metric thresholds
 * - Real-time threshold monitoring
 * - Threshold breach history
 * - Custom alert rules
 * - Notification preferences
 *
 * Structure:
 * - Header (Title + Description)
 * - Threshold Configuration Panel
 * - Active Thresholds Table
 * - Threshold Status Monitoring
 * - Breach History
 */

import React, { useState, useMemo } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  Grid,
  Alert,
  AlertTitle,
  Chip,
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
  TextField,
  Switch,
  FormControlLabel,
  Dialog,
  DialogTitle,
  DialogContent,
  DialogActions,
  LinearProgress,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
} from '@mui/material';
import {
  Settings,
  TrendingUp,
  TrendingDown,
  Edit,
  Delete,
  Add,
  Save,
  Warning,
  CheckCircle,
  Notifications,
  Speed,
  AttachMoney,
  Mouse,
  Visibility,
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
  ReferenceLine,
} from 'recharts';

interface ThresholdConfig {
  id: string;
  metric_name: string;
  metric_display: string;
  icon: string;
  threshold_type: 'min' | 'max';
  threshold_value: number;
  warning_threshold: number;
  critical_threshold: number;
  current_value: number;
  enabled: boolean;
  notify_email: boolean;
  notify_dashboard: boolean;
  comparison_period: 'daily' | 'weekly' | 'monthly';
}

interface BreachHistory {
  timestamp: string;
  metric_name: string;
  severity: 'critical' | 'warning';
  value: number;
  threshold: number;
  duration_minutes: number;
}

const ThresholdsMonitor: React.FC = () => {
  const { filters } = useFilters();
  const [editDialogOpen, setEditDialogOpen] = useState(false);
  const [selectedThreshold, setSelectedThreshold] = useState<ThresholdConfig | null>(null);

  // Helper function to render icons
  const renderIcon = (iconName: string) => {
    const icons: Record<string, React.ReactNode> = {
      mouse: <Mouse />,
      money: <AttachMoney />,
      trending_up: <TrendingUp />,
      speed: <Speed />,
      visibility: <Visibility />,
      check_circle: <CheckCircle />,
    };
    return icons[iconName] || <Settings />;
  };

  // Threshold configurations
  const [thresholds, setThresholds] = useState<ThresholdConfig[]>([
    {
      id: '1',
      metric_name: 'ctr',
      metric_display: 'CTR (%)',
      icon: 'mouse',
      threshold_type: 'min',
      threshold_value: 2.0,
      warning_threshold: 1.5,
      critical_threshold: 1.0,
      current_value: 3.2,
      enabled: true,
      notify_email: true,
      notify_dashboard: true,
      comparison_period: 'daily',
    },
    {
      id: '2',
      metric_name: 'cpc',
      metric_display: 'CPC ($)',
      icon: 'money',
      threshold_type: 'max',
      threshold_value: 2.00,
      warning_threshold: 2.50,
      critical_threshold: 3.00,
      current_value: 1.45,
      enabled: true,
      notify_email: true,
      notify_dashboard: true,
      comparison_period: 'daily',
    },
    {
      id: '3',
      metric_name: 'roas',
      metric_display: 'ROAS',
      icon: 'trending_up',
      threshold_type: 'min',
      threshold_value: 2.0,
      warning_threshold: 1.5,
      critical_threshold: 1.0,
      current_value: 2.3,
      enabled: true,
      notify_email: true,
      notify_dashboard: true,
      comparison_period: 'daily',
    },
    {
      id: '4',
      metric_name: 'conversion_rate',
      metric_display: 'Conversion Rate (%)',
      icon: 'speed',
      threshold_type: 'min',
      threshold_value: 4.0,
      warning_threshold: 3.0,
      critical_threshold: 2.0,
      current_value: 4.8,
      enabled: true,
      notify_email: false,
      notify_dashboard: true,
      comparison_period: 'weekly',
    },
    {
      id: '5',
      metric_name: 'impressions',
      metric_display: 'Impressions',
      icon: 'visibility',
      threshold_type: 'min',
      threshold_value: 1000,
      warning_threshold: 500,
      critical_threshold: 100,
      current_value: 1250,
      enabled: false,
      notify_email: false,
      notify_dashboard: true,
      comparison_period: 'daily',
    },
    {
      id: '6',
      metric_name: 'quality_score',
      metric_display: 'Quality Score',
      icon: 'check_circle',
      threshold_type: 'min',
      threshold_value: 6.0,
      warning_threshold: 5.0,
      critical_threshold: 4.0,
      current_value: 6.8,
      enabled: true,
      notify_email: true,
      notify_dashboard: true,
      comparison_period: 'weekly',
    },
  ]);

  // Breach history
  const breachHistory = useMemo((): BreachHistory[] => {
    const history: BreachHistory[] = [];
    const now = new Date();

    for (let i = 0; i < 10; i++) {
      const timestamp = new Date(now.getTime() - i * 3600000 * 24);
      history.push({
        timestamp: timestamp.toISOString(),
        metric_name: ['CTR', 'CPC', 'ROAS', 'Conversion Rate'][Math.floor(Math.random() * 4)],
        severity: Math.random() > 0.5 ? 'critical' : 'warning',
        value: Math.random() * 5,
        threshold: Math.random() * 3 + 1,
        duration_minutes: Math.floor(Math.random() * 240) + 30,
      });
    }
    return history;
  }, []);

  const thresholdStatus = useMemo(() => {
    const total = thresholds.length;
    const enabled = thresholds.filter(t => t.enabled).length;

    const breaching = thresholds.filter(t => {
      if (!t.enabled) return false;
      if (t.threshold_type === 'min') {
        return t.current_value < t.critical_threshold;
      } else {
        return t.current_value > t.critical_threshold;
      }
    }).length;

    const warning = thresholds.filter(t => {
      if (!t.enabled) return false;
      if (t.threshold_type === 'min') {
        return t.current_value < t.warning_threshold && t.current_value >= t.critical_threshold;
      } else {
        return t.current_value > t.warning_threshold && t.current_value <= t.critical_threshold;
      }
    }).length;

    const healthy = enabled - breaching - warning;

    return { total, enabled, breaching, warning, healthy };
  }, [thresholds]);

  const getStatusColor = (threshold: ThresholdConfig) => {
    if (!threshold.enabled) return 'default';

    if (threshold.threshold_type === 'min') {
      if (threshold.current_value < threshold.critical_threshold) return 'error';
      if (threshold.current_value < threshold.warning_threshold) return 'warning';
      return 'success';
    } else {
      if (threshold.current_value > threshold.critical_threshold) return 'error';
      if (threshold.current_value > threshold.warning_threshold) return 'warning';
      return 'success';
    }
  };

  const getStatusPercentage = (threshold: ThresholdConfig) => {
    if (threshold.threshold_type === 'min') {
      return (threshold.current_value / threshold.threshold_value) * 100;
    } else {
      return 100 - ((threshold.current_value / threshold.critical_threshold) * 50);
    }
  };

  const handleEdit = (threshold: ThresholdConfig) => {
    setSelectedThreshold(threshold);
    setEditDialogOpen(true);
  };

  const handleToggleEnabled = (id: string) => {
    setThresholds(thresholds.map(t =>
      t.id === id ? { ...t, enabled: !t.enabled } : t
    ));
  };

  // AI Analysis - 4 Types (Threshold Optimization focus)
  const aiAnalysis = useMemo(() => {
    if (!thresholds || thresholds.length === 0) {
      return {
        descriptive: { text: '', icon: Assessment, color: '#1E88E5' },
        diagnostic: { text: '', icon: Psychology, color: '#7B1FA2' },
        predictive: { text: '', icon: Timeline, color: '#F57C00' },
        prescriptive: { text: '', icon: Lightbulb, color: '#388E3C' },
      };
    }

    const total = thresholdStatus.total;
    const enabled = thresholdStatus.enabled;
    const breaching = thresholdStatus.breaching;
    const warning = thresholdStatus.warning;
    const healthy = thresholdStatus.healthy;

    // Calculate effectiveness metrics
    const breachRate = enabled > 0 ? (breaching / enabled) * 100 : 0;
    const warningRate = enabled > 0 ? (warning / enabled) * 100 : 0;
    const healthyRate = enabled > 0 ? (healthy / enabled) * 100 : 0;

    // Analyze threshold tightness
    const tooTightThresholds = thresholds.filter(t => {
      const margin = Math.abs(t.current_value - t.threshold_value) / t.threshold_value;
      return margin < 0.1 && t.enabled; // Within 10% of threshold
    }).length;

    const tooLooseThresholds = thresholds.filter(t => {
      const margin = Math.abs(t.current_value - t.threshold_value) / t.threshold_value;
      return margin > 0.5 && t.enabled; // More than 50% away
    }).length;

    // 1. DESCRIPTIVE: Threshold configuration status
    const descriptive = `Threshold Monitoring Overview:\n• ${total} thresholds configured (${enabled} active, ${total - enabled} disabled)\n• ${healthy} metrics within healthy range (${healthyRate.toFixed(0)}%)\n• ${warning} metrics approaching limits (${warningRate.toFixed(0)}%)\n• ${breaching} metrics breaching thresholds (${breachRate.toFixed(0)}%)\n\nThreshold Distribution:\n• ${thresholds.filter(t => t.threshold_type === 'min').length} minimum thresholds (floor protection)\n• ${thresholds.filter(t => t.threshold_type === 'max').length} maximum thresholds (ceiling protection)\n\nNotification Settings:\n• ${thresholds.filter(t => t.notify_email).length} email alerts enabled\n• ${thresholds.filter(t => t.notify_dashboard).length} dashboard alerts active`;

    // 2. DIAGNOSTIC: Why thresholds are performing this way
    let diagnostic = `Threshold Effectiveness Analysis:\n\n`;

    if (breachRate > 20) {
      diagnostic += `High Breach Rate (${breachRate.toFixed(0)}%):\n• ${breaching} thresholds consistently breached\n• Indicates thresholds set too aggressively or systematic performance issues\n\n`;
    } else if (breachRate > 0) {
      diagnostic += `Normal Breach Rate (${breachRate.toFixed(0)}%):\n• ${breaching} active breaches within acceptable range\n• Thresholds effectively catching outliers\n\n`;
    }

    if (tooTightThresholds > 0) {
      diagnostic += `Tight Threshold Warning:\n• ${tooTightThresholds} metrics running close to limits (<10% margin)\n• Risk of frequent alert fatigue\n\n`;
    }

    if (tooLooseThresholds > 0) {
      diagnostic += `Loose Threshold Gap:\n• ${tooLooseThresholds} thresholds too relaxed (>50% margin)\n• May miss important performance degradation\n\n`;
    }

    if (breachRate === 0 && warningRate === 0) {
      diagnostic += `⚠️ Zero breaches/warnings may indicate thresholds are too loose - review settings`;
    } else if (breachRate > 30) {
      diagnostic += `⚠️ Excessive breaches indicate either unrealistic thresholds or serious performance issues`;
    }

    // 3. PREDICTIVE: Threshold breach forecasts
    const avgBreachDuration = breachHistory.reduce((sum, b) => sum + b.duration_minutes, 0) / Math.max(breachHistory.length, 1);
    const recentBreaches = breachHistory.filter(b => {
      const hoursAgo = (new Date().getTime() - new Date(b.timestamp).getTime()) / 3600000;
      return hoursAgo <= 24;
    }).length;

    const breachTrend = recentBreaches > breachHistory.length * 0.4 ? 'increasing' : recentBreaches > breachHistory.length * 0.2 ? 'stable' : 'decreasing';
    const futureRisk = breachRate > 20 ? 'High' : breachRate > 10 ? 'Medium' : 'Low';

    const predictive = `Threshold Breach Forecast:\n\nBreach Patterns:\n• Recent breach velocity: ${recentBreaches} in last 24h\n• Trend direction: ${breachTrend}\n• Average breach duration: ${avgBreachDuration.toFixed(0)} minutes\n\nRisk Assessment:\n• Future breach risk: ${futureRisk}\n• ${warning} metrics in warning zone (may escalate to breaches)\n• Alert fatigue risk: ${tooTightThresholds > 3 ? 'High' : tooTightThresholds > 0 ? 'Medium' : 'Low'}\n\nProjected Impact:\n• If current trend continues: ${breachTrend === 'increasing' ? `+${(recentBreaches * 1.5).toFixed(0)} breaches next 24h` : 'Breach rate stabilizing'}`;

    // 4. PRESCRIPTIVE: Threshold optimization recommendations
    const recommendations: string[] = [];

    if (tooTightThresholds > 0) {
      recommendations.push(`1. Relax ${tooTightThresholds} overly tight thresholds by 15-20% to reduce alert noise`);
    }

    if (tooLooseThresholds > 0) {
      recommendations.push(`${recommendations.length + 1}. Tighten ${tooLooseThresholds} loose thresholds to catch issues earlier (target 20-30% margin)`);
    }

    if (breaching > 0) {
      recommendations.push(`${recommendations.length + 1}. Investigate ${breaching} breaching metrics - address root causes before adjusting thresholds`);
    }

    if (total - enabled > 3) {
      recommendations.push(`${recommendations.length + 1}. Review ${total - enabled} disabled thresholds - re-enable if still relevant or delete`);
    }

    if (thresholds.filter(t => !t.notify_email && !t.notify_dashboard).length > 0) {
      recommendations.push(`${recommendations.length + 1}. Enable notifications for ${thresholds.filter(t => !t.notify_email && !t.notify_dashboard).length} silent thresholds`);
    }

    const prescriptive = `Threshold Optimization Plan:\n${recommendations.slice(0, 4).join('\n')}\n\nBest Practice Guidelines:\n• Set warning at 70-80% of critical threshold\n• Review monthly and adjust based on performance evolution\n• Balance sensitivity (catch issues) vs noise (alert fatigue)\n• Target: 5-10% breach rate for optimal effectiveness`;

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
  }, [thresholds, thresholdStatus, breachHistory]);

  return (
    <Box sx={{ p: 3 }}>
      {/* Header */}
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" fontWeight={700} gutterBottom sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
          <Settings fontSize="large" color="primary" />
          Thresholds Monitor
        </Typography>
        <Typography variant="body1" color="text.secondary">
          Configure and monitor performance thresholds for automated alerting
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
                      Threshold status
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
                      Effectiveness
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
                      Breach forecast
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
                      Optimization plan
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
          <Card sx={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Total Thresholds</Typography>
                  <Typography variant="h2" fontWeight={700}>{thresholdStatus.total}</Typography>
                  <Typography variant="caption">{thresholdStatus.enabled} enabled</Typography>
                </Box>
                <Settings sx={{ fontSize: 60, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Healthy</Typography>
                  <Typography variant="h2" fontWeight={700}>{thresholdStatus.healthy}</Typography>
                  <Typography variant="caption">Within range</Typography>
                </Box>
                <CheckCircle sx={{ fontSize: 60, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #ff9800 0%, #fb8c00 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Warning</Typography>
                  <Typography variant="h2" fontWeight={700}>{thresholdStatus.warning}</Typography>
                  <Typography variant="caption">Approaching limit</Typography>
                </Box>
                <Warning sx={{ fontSize: 60, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>

        <Grid item xs={12} sm={6} md={3}>
          <Card sx={{ background: 'linear-gradient(135deg, #f44336 0%, #e91e63 100%)', color: 'white' }}>
            <CardContent>
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                <Box>
                  <Typography variant="body2" sx={{ opacity: 0.9 }}>Breaching</Typography>
                  <Typography variant="h2" fontWeight={700}>{thresholdStatus.breaching}</Typography>
                  <Typography variant="caption">Over threshold</Typography>
                </Box>
                <TrendingDown sx={{ fontSize: 60, opacity: 0.7 }} />
              </Box>
            </CardContent>
          </Card>
        </Grid>
      </Grid>

      {/* Actions */}
      <Box sx={{ mb: 3, display: 'flex', gap: 2 }}>
        <Button variant="contained" color="primary" startIcon={<Add />}>
          Add Threshold
        </Button>
        <Button variant="outlined" startIcon={<Save />}>
          Save All Changes
        </Button>
      </Box>

      {/* Active Thresholds */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Configured Thresholds
          </Typography>
          <Divider sx={{ my: 2 }} />
          <TableContainer>
            <Table>
              <TableHead>
                <TableRow>
                  <TableCell><strong>Metric</strong></TableCell>
                  <TableCell align="center"><strong>Type</strong></TableCell>
                  <TableCell align="center"><strong>Current Value</strong></TableCell>
                  <TableCell align="center"><strong>Target</strong></TableCell>
                  <TableCell align="center"><strong>Warning</strong></TableCell>
                  <TableCell align="center"><strong>Critical</strong></TableCell>
                  <TableCell align="center"><strong>Status</strong></TableCell>
                  <TableCell align="center"><strong>Enabled</strong></TableCell>
                  <TableCell align="center"><strong>Notifications</strong></TableCell>
                  <TableCell align="center"><strong>Actions</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {thresholds.map((threshold) => (
                  <TableRow key={threshold.id} hover>
                    <TableCell>
                      <Box sx={{ display: 'flex', alignItems: 'center', gap: 1 }}>
                        {renderIcon(threshold.icon)}
                        <Typography variant="body2" fontWeight={600}>{threshold.metric_display}</Typography>
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Chip
                        label={threshold.threshold_type === 'min' ? 'MIN' : 'MAX'}
                        size="small"
                        color={threshold.threshold_type === 'min' ? 'primary' : 'secondary'}
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Typography variant="body2" fontWeight={600}>
                        {threshold.current_value.toFixed(2)}
                      </Typography>
                    </TableCell>
                    <TableCell align="center">{threshold.threshold_value.toFixed(2)}</TableCell>
                    <TableCell align="center">{threshold.warning_threshold.toFixed(2)}</TableCell>
                    <TableCell align="center">{threshold.critical_threshold.toFixed(2)}</TableCell>
                    <TableCell align="center">
                      <Box sx={{ width: '100%' }}>
                        <LinearProgress
                          variant="determinate"
                          value={Math.min(getStatusPercentage(threshold), 100)}
                          sx={{ height: 8, borderRadius: 4, mb: 0.5 }}
                          color={getStatusColor(threshold) as any}
                        />
                        <Chip
                          label={
                            !threshold.enabled ? 'DISABLED' :
                            getStatusColor(threshold) === 'error' ? 'BREACH' :
                            getStatusColor(threshold) === 'warning' ? 'WARNING' :
                            'HEALTHY'
                          }
                          size="small"
                          color={getStatusColor(threshold) as any}
                        />
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Switch
                        checked={threshold.enabled}
                        onChange={() => handleToggleEnabled(threshold.id)}
                        color="primary"
                      />
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                        {threshold.notify_email && (
                          <Tooltip title="Email notifications enabled">
                            <Chip label="Email" size="small" variant="outlined" />
                          </Tooltip>
                        )}
                        {threshold.notify_dashboard && (
                          <Tooltip title="Dashboard notifications enabled">
                            <Chip label="Dashboard" size="small" variant="outlined" />
                          </Tooltip>
                        )}
                      </Box>
                    </TableCell>
                    <TableCell align="center">
                      <Box sx={{ display: 'flex', gap: 0.5, justifyContent: 'center' }}>
                        <Tooltip title="Edit threshold">
                          <IconButton size="small" onClick={() => handleEdit(threshold)}>
                            <Edit fontSize="small" />
                          </IconButton>
                        </Tooltip>
                        <Tooltip title="Delete threshold">
                          <IconButton size="small" color="error">
                            <Delete fontSize="small" />
                          </IconButton>
                        </Tooltip>
                      </Box>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Breach History */}
      <Card sx={{ mb: 4 }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Recent Threshold Breaches
          </Typography>
          <Divider sx={{ my: 2 }} />
          <TableContainer>
            <Table size="small">
              <TableHead>
                <TableRow>
                  <TableCell><strong>Timestamp</strong></TableCell>
                  <TableCell><strong>Metric</strong></TableCell>
                  <TableCell align="center"><strong>Severity</strong></TableCell>
                  <TableCell align="right"><strong>Value</strong></TableCell>
                  <TableCell align="right"><strong>Threshold</strong></TableCell>
                  <TableCell align="right"><strong>Duration</strong></TableCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {breachHistory.slice(0, 10).map((breach, idx) => (
                  <TableRow key={idx} hover>
                    <TableCell>
                      {new Date(breach.timestamp).toLocaleString()}
                    </TableCell>
                    <TableCell>{breach.metric_name}</TableCell>
                    <TableCell align="center">
                      <Chip
                        label={breach.severity.toUpperCase()}
                        size="small"
                        color={breach.severity === 'critical' ? 'error' : 'warning'}
                      />
                    </TableCell>
                    <TableCell align="right">{breach.value.toFixed(2)}</TableCell>
                    <TableCell align="right">{breach.threshold.toFixed(2)}</TableCell>
                    <TableCell align="right">{breach.duration_minutes}m</TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </CardContent>
      </Card>

      {/* Best Practices */}
      <Card sx={{ background: 'linear-gradient(135deg, #667eea15 0%, #764ba215 100%)' }}>
        <CardContent>
          <Typography variant="h6" fontWeight={600} gutterBottom>
            Threshold Best Practices
          </Typography>
          <Divider sx={{ my: 2 }} />
          <Grid container spacing={2}>
            <Grid item xs={12} md={6}>
              <Alert severity="info">
                <AlertTitle>Set Realistic Thresholds</AlertTitle>
                Base thresholds on historical performance data, not aspirational goals. Use 20-30% variance from average as a starting point.
              </Alert>
            </Grid>
            <Grid item xs={12} md={6}>
              <Alert severity="success">
                <AlertTitle>Use Warning & Critical Levels</AlertTitle>
                Warning thresholds give you time to investigate before critical breaches occur. Set warnings at 70-80% of critical values.
              </Alert>
            </Grid>
            <Grid item xs={12} md={6}>
              <Alert severity="warning">
                <AlertTitle>Avoid Alert Fatigue</AlertTitle>
                Too many alerts reduce effectiveness. Focus on metrics that directly impact business goals and require action.
              </Alert>
            </Grid>
            <Grid item xs={12} md={6}>
              <Alert severity="info">
                <AlertTitle>Regular Review</AlertTitle>
                Review and adjust thresholds monthly as campaign performance evolves. What's normal today may not be normal next month.
              </Alert>
            </Grid>
          </Grid>
        </CardContent>
      </Card>

      {/* Edit Dialog */}
      <Dialog open={editDialogOpen} onClose={() => setEditDialogOpen(false)} maxWidth="sm" fullWidth>
        <DialogTitle>Edit Threshold: {selectedThreshold?.metric_display}</DialogTitle>
        <DialogContent>
          {selectedThreshold && (
            <Box sx={{ pt: 2, display: 'flex', flexDirection: 'column', gap: 2 }}>
              <TextField
                label="Target Threshold"
                type="number"
                value={selectedThreshold.threshold_value}
                fullWidth
                size="small"
              />
              <TextField
                label="Warning Threshold"
                type="number"
                value={selectedThreshold.warning_threshold}
                fullWidth
                size="small"
              />
              <TextField
                label="Critical Threshold"
                type="number"
                value={selectedThreshold.critical_threshold}
                fullWidth
                size="small"
              />
              <FormControlLabel
                control={<Switch checked={selectedThreshold.notify_email} />}
                label="Email Notifications"
              />
              <FormControlLabel
                control={<Switch checked={selectedThreshold.notify_dashboard} />}
                label="Dashboard Notifications"
              />
            </Box>
          )}
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setEditDialogOpen(false)}>Cancel</Button>
          <Button variant="contained" color="primary" onClick={() => setEditDialogOpen(false)}>
            Save Changes
          </Button>
        </DialogActions>
      </Dialog>
    </Box>
  );
};

export default ThresholdsMonitor;
