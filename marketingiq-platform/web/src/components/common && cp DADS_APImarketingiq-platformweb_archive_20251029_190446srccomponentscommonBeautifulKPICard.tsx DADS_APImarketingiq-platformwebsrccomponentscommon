import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  Chip,
  LinearProgress,
  useTheme,
  alpha,
  Skeleton,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
  TrendingFlat,
  ArrowUpward,
  ArrowDownward,
} from '@mui/icons-material';
import { keyframes } from '@mui/system';
import CountUp from 'react-countup';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler,
} from 'chart.js';

ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
  Filler
);

// Animations
const pulse = keyframes`
  0% {
    transform: scale(1);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }
  50% {
    transform: scale(1.02);
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
  }
  100% {
    transform: scale(1);
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  }
`;

const shimmer = keyframes`
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
`;

const slideIn = keyframes`
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
`;

const glow = keyframes`
  0%, 100% {
    box-shadow: 0 0 20px rgba(99, 102, 241, 0.3);
  }
  50% {
    box-shadow: 0 0 40px rgba(99, 102, 241, 0.5);
  }
`;

interface AnimatedKPICardProps {
  title: string;
  value: number | string;
  previousValue?: number;
  format?: 'currency' | 'percentage' | 'number' | 'custom';
  prefix?: string;
  suffix?: string;
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: number;
  sparklineData?: number[];
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
  animationDelay?: number;
  loading?: boolean;
  onClick?: () => void;
  description?: string;
  target?: number;
  showProgress?: boolean;
  pulseOnHigh?: boolean;
  glowEffect?: boolean;
}

const AnimatedKPICard: React.FC<AnimatedKPICardProps> = ({
  title,
  value,
  previousValue,
  format = 'number',
  prefix = '',
  suffix = '',
  icon,
  trend = 'neutral',
  trendValue,
  sparklineData = [],
  color = 'primary',
  animationDelay = 0,
  loading = false,
  onClick,
  description,
  target,
  showProgress = false,
  pulseOnHigh = false,
  glowEffect = false,
}) => {
  const theme = useTheme();
  const [isAnimating, setIsAnimating] = useState(false);
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    setIsAnimating(true);
    const timer = setTimeout(() => setIsAnimating(false), 2000);
    return () => clearTimeout(timer);
  }, [value]);

  const getColorByType = () => {
    const colors = {
      primary: theme.palette.primary.main,
      success: theme.palette.success.main,
      warning: theme.palette.warning.main,
      error: theme.palette.error.main,
      info: theme.palette.info.main,
    };
    return colors[color];
  };

  const getTrendIcon = () => {
    switch (trend) {
      case 'up':
        return <TrendingUp sx={{ color: theme.palette.success.main }} />;
      case 'down':
        return <TrendingDown sx={{ color: theme.palette.error.main }} />;
      default:
        return <TrendingFlat sx={{ color: theme.palette.text.secondary }} />;
    }
  };

  const formatValue = (val: number | string) => {
    if (typeof val === 'string') return val;

    switch (format) {
      case 'currency':
        return `${prefix}₹${val.toFixed(2)}${suffix}`;
      case 'percentage':
        return `${prefix}${val.toFixed(2)}%${suffix}`;
      case 'number':
        return `${prefix}${val.toLocaleString()}${suffix}`;
      default:
        return `${prefix}${val}${suffix}`;
    }
  };

  const calculateProgress = () => {
    if (!target || typeof value !== 'number') return 0;
    return Math.min((value / target) * 100, 100);
  };

  const sparklineChartData = {
    labels: sparklineData.map((_, i) => ''),
    datasets: [
      {
        data: sparklineData,
        fill: true,
        backgroundColor: alpha(getColorByType(), 0.1),
        borderColor: getColorByType(),
        borderWidth: 2,
        tension: 0.4,
        pointRadius: 0,
        pointHoverRadius: 0,
      },
    ],
  };

  const sparklineOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      tooltip: { enabled: false },
    },
    scales: {
      x: { display: false },
      y: { display: false },
    },
  };

  if (loading) {
    return (
      <Card sx={{ height: '100%' }}>
        <CardContent>
          <Skeleton variant="text" width="60%" />
          <Skeleton variant="text" width="40%" height={60} />
          <Skeleton variant="rectangular" height={40} />
        </CardContent>
      </Card>
    );
  }

  return (
    <Card
      onClick={onClick}
      sx={{
        height: '100%',
        cursor: onClick ? 'pointer' : 'default',
        position: 'relative',
        overflow: 'hidden',
        animation: `${slideIn} 0.6s ease-out ${animationDelay}s both`,
        ...(pulseOnHigh && trendValue && trendValue > 20 && {
          animation: `${pulse} 2s infinite`,
        }),
        ...(glowEffect && {
          animation: `${glow} 2s infinite`,
        }),
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: onClick ? 'translateY(-8px)' : 'none',
          boxShadow: onClick ? theme.shadows[8] : theme.shadows[2],
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: `linear-gradient(90deg, ${getColorByType()}, ${alpha(
            getColorByType(),
            0.5
          )})`,
          ...(isAnimating && {
            background: `linear-gradient(90deg, transparent, ${getColorByType()}, transparent)`,
            backgroundSize: '200% 100%',
            animation: `${shimmer} 1.5s linear infinite`,
          }),
        },
      }}
    >
      <CardContent>
        <Box display="flex" justifyContent="space-between" alignItems="flex-start" mb={2}>
          <Box flex={1}>
            <Typography
              variant="body2"
              color="text.secondary"
              gutterBottom
              sx={{ fontWeight: 500, textTransform: 'uppercase', fontSize: '0.75rem' }}
            >
              {title}
            </Typography>
            {description && (
              <Typography variant="caption" color="text.secondary" sx={{ display: 'block', mb: 1 }}>
                {description}
              </Typography>
            )}
          </Box>
          <Box
            sx={{
              width: 40,
              height: 40,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              borderRadius: 2,
              bgcolor: alpha(getColorByType(), 0.1),
              color: getColorByType(),
            }}
          >
            {icon}
          </Box>
        </Box>

        <Box mb={2}>
          <Typography variant="h4" component="div" fontWeight="bold" color={getColorByType()}>
            {typeof value === 'number' && !loading ? (
              <CountUp
                start={previousValue || 0}
                end={value}
                duration={1.5}
                separator=","
                decimals={format === 'percentage' || format === 'currency' ? 2 : 0}
                decimal="."
                prefix={prefix}
                suffix={suffix}
                delay={animationDelay}
              />
            ) : (
              formatValue(value)
            )}
          </Typography>
        </Box>

        {(trend !== 'neutral' || trendValue !== undefined) && (
          <Box display="flex" alignItems="center" gap={1} mb={2}>
            {getTrendIcon()}
            {trendValue !== undefined && (
              <Chip
                size="small"
                icon={
                  trendValue > 0 ? (
                    <ArrowUpward sx={{ fontSize: 14 }} />
                  ) : (
                    <ArrowDownward sx={{ fontSize: 14 }} />
                  )
                }
                label={`${trendValue > 0 ? '+' : ''}${trendValue.toFixed(1)}%`}
                sx={{
                  bgcolor: alpha(
                    trendValue > 0 ? theme.palette.success.main : theme.palette.error.main,
                    0.1
                  ),
                  color: trendValue > 0 ? theme.palette.success.main : theme.palette.error.main,
                  fontWeight: 600,
                }}
              />
            )}
          </Box>
        )}

        {showProgress && target && (
          <Box mb={2}>
            <Box display="flex" justifyContent="space-between" mb={0.5}>
              <Typography variant="caption" color="text.secondary">
                Progress
              </Typography>
              <Typography variant="caption" color="text.secondary">
                {calculateProgress().toFixed(0)}%
              </Typography>
            </Box>
            <LinearProgress
              variant="determinate"
              value={calculateProgress()}
              sx={{
                height: 6,
                borderRadius: 3,
                bgcolor: alpha(getColorByType(), 0.1),
                '& .MuiLinearProgress-bar': {
                  bgcolor: getColorByType(),
                  borderRadius: 3,
                },
              }}
            />
            {target && (
              <Typography variant="caption" color="text.secondary" sx={{ mt: 0.5 }}>
                Target: {formatValue(target)}
              </Typography>
            )}
          </Box>
        )}

        {sparklineData.length > 0 && (
          <Box height={50} mt={2}>
            <Line data={sparklineChartData} options={sparklineOptions} />
          </Box>
        )}
      </CardContent>
    </Card>
  );
};

export default AnimatedKPICard;