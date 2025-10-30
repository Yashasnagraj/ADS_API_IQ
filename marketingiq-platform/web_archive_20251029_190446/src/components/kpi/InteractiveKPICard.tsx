/**
 * Interactive KPI Card - Clickable KPI cards with drill-down capability
 * Shows a badge indicator when clickable and opens detail drawer on click
 */
import React from 'react';
import {
  Card,
  CardContent,
  Box,
  Typography,
  Avatar,
  Chip,
  LinearProgress,
  useTheme,
  alpha,
  Badge,
  Tooltip,
  Zoom,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  Remove,
  TouchApp,
} from '@mui/icons-material';
import { keyframes } from '@mui/system';

// Animations
const pulse = keyframes`
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
`;

const shimmer = keyframes`
  0% { background-position: -200% 0; }
  100% { background-position: 200% 0; }
`;

interface InteractiveKPICardProps {
  title: string;
  value: number | string;
  format?: 'number' | 'currency' | 'percentage';
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: number;
  color?: 'primary' | 'secondary' | 'success' | 'error' | 'warning' | 'info';
  loading?: boolean;
  onClick?: () => void;
  drillDownAvailable?: boolean;
  showProgress?: boolean;
  target?: number;
  subtitle?: string;
  index?: number;
}

const InteractiveKPICard: React.FC<InteractiveKPICardProps> = ({
  title,
  value,
  format = 'number',
  icon,
  trend,
  trendValue,
  color = 'primary',
  loading = false,
  onClick,
  drillDownAvailable = false,
  showProgress = false,
  target,
  subtitle,
  index = 0,
}) => {
  const theme = useTheme();

  const formatValue = (val: number | string) => {
    if (typeof val === 'string') return val;

    switch (format) {
      case 'currency':
        return `₹${val.toFixed(2)}`;
      case 'percentage':
        return `${val.toFixed(2)}%`;
      default:
        return val.toLocaleString();
    }
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp sx={{ fontSize: 16 }} />;
      case 'down':
        return <TrendingDown sx={{ fontSize: 16 }} />;
      default:
        return <Remove sx={{ fontSize: 16 }} />;
    }
  };

  const getTrendColor = () => {
    switch (trend) {
      case 'up':
        return theme.palette.success.main;
      case 'down':
        return theme.palette.error.main;
      default:
        return theme.palette.text.secondary;
    }
  };

  const colorMap = {
    primary: theme.palette.primary.main,
    secondary: theme.palette.secondary.main,
    success: theme.palette.success.main,
    error: theme.palette.error.main,
    warning: theme.palette.warning.main,
    info: theme.palette.info.main,
  };

  const selectedColor = colorMap[color];
  const isClickable = !!onClick || drillDownAvailable;

  return (
    <Zoom in timeout={600 + index * 100}>
      <Badge
        badgeContent={isClickable ? <TouchApp sx={{ fontSize: 14 }} /> : null}
        color="primary"
        invisible={!isClickable}
        sx={{
          width: '100%',
          '& .MuiBadge-badge': {
            top: 12,
            right: 12,
          },
        }}
      >
        <Card
          onClick={onClick}
          sx={{
            width: '100%',
            height: '100%',
            cursor: isClickable ? 'pointer' : 'default',
            position: 'relative',
            overflow: 'hidden',
            transition: 'all 0.3s ease',
            border: `1px solid ${alpha(selectedColor, 0.2)}`,
            '&:hover': isClickable ? {
              transform: 'translateY(-4px)',
              boxShadow: `0 8px 24px ${alpha(selectedColor, 0.25)}`,
              borderColor: selectedColor,
              '& .kpi-icon': {
                animation: `${pulse} 1s infinite`,
              },
            } : {},
            '&::before': loading ? {
              content: '""',
              position: 'absolute',
              top: 0,
              left: '-100%',
              width: '200%',
              height: '4px',
              background: `linear-gradient(90deg, transparent, ${selectedColor}, transparent)`,
              animation: `${shimmer} 1.5s linear infinite`,
            } : {},
          }}
        >
          <CardContent sx={{ p: 2.5 }}>
            <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
              <Box>
                <Typography variant="body2" color="text.secondary" fontWeight={500} gutterBottom>
                  {title}
                </Typography>
                {loading ? (
                  <LinearProgress sx={{ width: 100, mt: 1 }} />
                ) : (
                  <Typography
                    variant="h4"
                    fontWeight="bold"
                    sx={{
                      background: `linear-gradient(135deg, ${selectedColor}, ${alpha(selectedColor, 0.6)})`,
                      WebkitBackgroundClip: 'text',
                      WebkitTextFillColor: 'transparent',
                    }}
                  >
                    {formatValue(value)}
                  </Typography>
                )}
                {subtitle && (
                  <Typography variant="caption" color="text.secondary">
                    {subtitle}
                  </Typography>
                )}
              </Box>
              <Avatar
                className="kpi-icon"
                sx={{
                  width: 48,
                  height: 48,
                  bgcolor: alpha(selectedColor, 0.1),
                  color: selectedColor,
                }}
              >
                {icon}
              </Avatar>
            </Box>

            {(trend || showProgress) && (
              <Box sx={{ mt: 2 }}>
                {trend && trendValue !== undefined && (
                  <Chip
                    icon={getTrendIcon()}
                    label={`${trendValue > 0 ? '+' : ''}${trendValue}%`}
                    size="small"
                    sx={{
                      bgcolor: alpha(getTrendColor(), 0.1),
                      color: getTrendColor(),
                      fontWeight: 600,
                      '& .MuiChip-icon': {
                        color: getTrendColor(),
                      },
                    }}
                  />
                )}

                {showProgress && target && (
                  <Box sx={{ mt: 1 }}>
                    <Box sx={{ display: 'flex', justifyContent: 'space-between', mb: 0.5 }}>
                      <Typography variant="caption" color="text.secondary">
                        Progress
                      </Typography>
                      <Typography variant="caption" color="text.secondary">
                        {Math.round((Number(value) / target) * 100)}%
                      </Typography>
                    </Box>
                    <LinearProgress
                      variant="determinate"
                      value={Math.min((Number(value) / target) * 100, 100)}
                      sx={{
                        height: 6,
                        borderRadius: 3,
                        bgcolor: alpha(selectedColor, 0.1),
                        '& .MuiLinearProgress-bar': {
                          bgcolor: selectedColor,
                          borderRadius: 3,
                        },
                      }}
                    />
                  </Box>
                )}
              </Box>
            )}

            {isClickable && (
              <Tooltip title="Click to view details" placement="top">
                <Chip
                  label="View Details"
                  size="small"
                  variant="outlined"
                  sx={{
                    mt: 1,
                    opacity: 0.7,
                    borderColor: selectedColor,
                    color: selectedColor,
                    fontSize: '0.7rem',
                  }}
                />
              </Tooltip>
            )}
          </CardContent>
        </Card>
      </Badge>
    </Zoom>
  );
};

export default InteractiveKPICard;
