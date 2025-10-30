/**
 * GA4 KPI Card Component
 * Displays Google Analytics 4 specific metrics like bounce rate, engagement, session duration
 */
import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  useTheme,
  alpha,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  Schedule,
  TouchApp,
  ExitToApp,
  Speed,
} from '@mui/icons-material';

interface GA4KPICardProps {
  title: string;
  value: number;
  format?: 'percentage' | 'duration' | 'number' | 'score';
  trend?: 'up' | 'down' | 'flat';
  trendValue?: number;
  subtitle?: string;
  color?: 'success' | 'warning' | 'error' | 'info' | 'primary';
  showProgress?: boolean;
  maxValue?: number;
  icon?: React.ReactNode;
}

export const GA4KPICard: React.FC<GA4KPICardProps> = ({
  title,
  value,
  format = 'number',
  trend,
  trendValue,
  subtitle,
  color = 'primary',
  showProgress = false,
  maxValue = 100,
  icon,
}) => {
  const theme = useTheme();

  const formatValue = (val: number, fmt: string) => {
    switch (fmt) {
      case 'percentage':
        return `${val.toFixed(1)}%`;
      case 'duration':
        // Convert seconds to minutes:seconds format
        const minutes = Math.floor(val / 60);
        const seconds = Math.floor(val % 60);
        return `${minutes}m ${seconds}s`;
      case 'score':
        return `${val.toFixed(1)}/100`;
      case 'number':
      default:
        return val.toLocaleString();
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp fontSize="small" />;
      case 'down':
        return <TrendingDown fontSize="small" />;
      case 'flat':
        return <TrendingFlat fontSize="small" />;
      default:
        return null;
    }
  };

  const getTrendColor = () => {
    // For metrics like bounce rate, "down" is good, "up" is bad
    const isReverseMetric = title.toLowerCase().includes('bounce');

    if (isReverseMetric) {
      if (trend === 'down') return theme.palette.success.main;
      if (trend === 'up') return theme.palette.error.main;
    } else {
      if (trend === 'up') return theme.palette.success.main;
      if (trend === 'down') return theme.palette.error.main;
    }
    return theme.palette.text.secondary;
  };

  const getColorValue = () => {
    switch (color) {
      case 'success':
        return theme.palette.success.main;
      case 'warning':
        return theme.palette.warning.main;
      case 'error':
        return theme.palette.error.main;
      case 'info':
        return theme.palette.info.main;
      case 'primary':
      default:
        return theme.palette.primary.main;
    }
  };

  const getDefaultIcon = () => {
    if (icon) return icon;

    if (title.toLowerCase().includes('bounce')) return <ExitToApp />;
    if (title.toLowerCase().includes('engagement')) return <TouchApp />;
    if (title.toLowerCase().includes('session') || title.toLowerCase().includes('duration')) return <Schedule />;
    if (title.toLowerCase().includes('quality') || title.toLowerCase().includes('score')) return <Speed />;
    return <TrendingUp />;
  };

  const progressValue = showProgress ? (value / maxValue) * 100 : 0;

  return (
    <Card
      sx={{
        height: '100%',
        position: 'relative',
        overflow: 'visible',
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 8px 24px ${alpha(getColorValue(), 0.2)}`,
        },
      }}
    >
      <CardContent>
        {/* Icon Badge */}
        <Box
          sx={{
            position: 'absolute',
            top: -16,
            right: 16,
            width: 48,
            height: 48,
            borderRadius: '12px',
            background: `linear-gradient(135deg, ${getColorValue()} 0%, ${alpha(getColorValue(), 0.7)} 100%)`,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            color: 'white',
            boxShadow: `0 4px 12px ${alpha(getColorValue(), 0.4)}`,
          }}
        >
          {getDefaultIcon()}
        </Box>

        {/* Title */}
        <Typography
          variant="body2"
          color="text.secondary"
          sx={{ mb: 1, fontWeight: 500 }}
        >
          {title}
        </Typography>

        {/* Value */}
        <Typography
          variant="h4"
          sx={{
            fontWeight: 700,
            color: getColorValue(),
            mb: 1,
          }}
        >
          {formatValue(value, format)}
        </Typography>

        {/* Trend & Subtitle */}
        <Box sx={{ display: 'flex', alignItems: 'center', gap: 1, mb: showProgress ? 1 : 0 }}>
          {trend && trendValue !== undefined && (
            <Chip
              icon={getTrendIcon() || undefined}
              label={`${trendValue > 0 ? '+' : ''}${trendValue.toFixed(1)}%`}
              size="small"
              sx={{
                height: 24,
                backgroundColor: alpha(getTrendColor(), 0.1),
                color: getTrendColor(),
                fontWeight: 600,
                '& .MuiChip-icon': {
                  color: getTrendColor(),
                },
              }}
            />
          )}
          {subtitle && (
            <Typography variant="caption" color="text.secondary">
              {subtitle}
            </Typography>
          )}
        </Box>

        {/* Progress Bar */}
        {showProgress && (
          <Box sx={{ mt: 2 }}>
            <LinearProgress
              variant="determinate"
              value={progressValue}
              sx={{
                height: 6,
                borderRadius: 3,
                backgroundColor: alpha(getColorValue(), 0.1),
                '& .MuiLinearProgress-bar': {
                  borderRadius: 3,
                  background: `linear-gradient(90deg, ${getColorValue()} 0%, ${alpha(getColorValue(), 0.7)} 100%)`,
                },
              }}
            />
            <Typography
              variant="caption"
              color="text.secondary"
              sx={{ mt: 0.5, display: 'block' }}
            >
              {progressValue.toFixed(0)}% of target
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default GA4KPICard;
