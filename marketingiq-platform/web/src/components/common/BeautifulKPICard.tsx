import React, { useEffect, useState } from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  useTheme,
  alpha,
} from '@mui/material';
import {
  TrendingUp,
  TrendingDown,
} from '@mui/icons-material';
import { keyframes } from '@mui/system';
import CountUp from 'react-countup';

// Beautiful animations
const shimmer = keyframes`
  0% {
    background-position: -200% 0;
  }
  100% {
    background-position: 200% 0;
  }
`;

const pulse = keyframes`
  0% {
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0.7);
  }
  70% {
    box-shadow: 0 0 0 10px rgba(99, 102, 241, 0);
  }
  100% {
    box-shadow: 0 0 0 0 rgba(99, 102, 241, 0);
  }
`;

const float = keyframes`
  0%, 100% {
    transform: translateY(0);
  }
  50% {
    transform: translateY(-5px);
  }
`;

const glow = keyframes`
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.8;
  }
`;

const slideInNumber = keyframes`
  from {
    transform: translateY(20px);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
`;

const gradientShift = keyframes`
  0% {
    background-position: 0% 50%;
  }
  50% {
    background-position: 100% 50%;
  }
  100% {
    background-position: 0% 50%;
  }
`;

const iconRotate = keyframes`
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
`;

interface BeautifulKPICardProps {
  title: string;
  value: number;
  previousValue?: number;
  format?: 'currency' | 'percentage' | 'number';
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: number;
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info';
  index?: number;
}

const BeautifulKPICard: React.FC<BeautifulKPICardProps> = ({
  title,
  value,
  previousValue,
  format = 'number',
  icon,
  trend = 'neutral',
  trendValue,
  color = 'primary',
  index = 0,
}) => {
  const theme = useTheme();
  const [isHovered, setIsHovered] = useState(false);
  const [isAnimating, setIsAnimating] = useState(false);

  useEffect(() => {
    setIsAnimating(true);
    const timer = setTimeout(() => setIsAnimating(false), 2000);
    return () => clearTimeout(timer);
  }, [value]);

  const getColorScheme = () => {
    const schemes = {
      primary: {
        gradient: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
        light: '#667eea',
        dark: '#764ba2',
      },
      success: {
        gradient: 'linear-gradient(135deg, #10b981 0%, #059669 100%)',
        light: '#10b981',
        dark: '#059669',
      },
      warning: {
        gradient: 'linear-gradient(135deg, #f59e0b 0%, #d97706 100%)',
        light: '#f59e0b',
        dark: '#d97706',
      },
      error: {
        gradient: 'linear-gradient(135deg, #ef4444 0%, #dc2626 100%)',
        light: '#ef4444',
        dark: '#dc2626',
      },
      info: {
        gradient: 'linear-gradient(135deg, #3b82f6 0%, #2563eb 100%)',
        light: '#3b82f6',
        dark: '#2563eb',
      },
    };
    return schemes[color];
  };

  const formatValue = (val: number) => {
    if (format === 'percentage') {
      return `${val.toFixed(2)}%`;
    }

    // Format large numbers without currency symbol
    if (val >= 1000000) {
      return `${(val / 1000000).toFixed(1)}M`;
    }
    if (val >= 1000) {
      return `${(val / 1000).toFixed(1)}K`;
    }
    return val.toFixed(0);
  };

  const colorScheme = getColorScheme();

  return (
    <Card
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      sx={{
        height: '100%',
        position: 'relative',
        overflow: 'visible',
        cursor: 'pointer',
        background: theme.palette.background.paper,
        border: `1px solid ${alpha(colorScheme.light, 0.2)}`,
        transition: 'all 0.4s cubic-bezier(0.4, 0, 0.2, 1)',
        animation: `${slideInNumber} 0.6s ease-out ${index * 0.1}s both`,
        '&:hover': {
          transform: 'translateY(-8px) scale(1.02)',
          boxShadow: `0 20px 40px ${alpha(colorScheme.dark, 0.2)}`,
          border: `1px solid ${alpha(colorScheme.light, 0.4)}`,
          '& .kpi-gradient-bg': {
            opacity: 1,
          },
          '& .kpi-icon-container': {
            transform: 'scale(1.1)',
            animation: `${iconRotate} 0.6s ease-in-out`,
          },
          '& .kpi-value': {
            transform: 'scale(1.05)',
          },
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: colorScheme.gradient,
          opacity: 0.03,
          transition: 'opacity 0.3s ease',
        },
        ...(isAnimating && {
          animation: `${pulse} 1s`,
        }),
      }}
    >
      {/* Animated gradient background */}
      <Box
        className="kpi-gradient-bg"
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '4px',
          background: colorScheme.gradient,
          backgroundSize: '200% 200%',
          animation: `${gradientShift} 3s ease infinite`,
          opacity: isHovered ? 1 : 0.7,
          transition: 'opacity 0.3s ease',
        }}
      />

      <CardContent sx={{ p: 2.5, position: 'relative' }}>
        {/* Header with icon */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Box>
            <Typography
              variant="caption"
              sx={{
                color: theme.palette.text.secondary,
                fontWeight: 600,
                textTransform: 'uppercase',
                fontSize: '0.7rem',
                letterSpacing: '0.05em',
                display: 'block',
                animation: `${glow} 2s ease-in-out infinite`,
              }}
            >
              {title}
            </Typography>
          </Box>
          <Box
            className="kpi-icon-container"
            sx={{
              width: 36,
              height: 36,
              borderRadius: '12px',
              background: colorScheme.gradient,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'white',
              boxShadow: `0 4px 12px ${alpha(colorScheme.light, 0.3)}`,
              transition: 'all 0.3s ease',
              animation: `${float} 3s ease-in-out infinite`,
              animationDelay: `${index * 0.2}s`,
            }}
          >
            {icon}
          </Box>
        </Box>

        {/* Animated value */}
        <Box mb={1.5}>
          <Typography
            className="kpi-value"
            variant="h5"
            component="div"
            fontWeight="bold"
            sx={{
              background: colorScheme.gradient,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundSize: '200% 200%',
              animation: `${gradientShift} 3s ease infinite`,
              transition: 'transform 0.3s ease',
              display: 'inline-block',
            }}
          >
            {format === 'percentage' ? (
              <>
                <CountUp
                  start={previousValue || 0}
                  end={value}
                  duration={2}
                  decimals={2}
                  delay={index * 0.1}
                />
                %
              </>
            ) : (
              <CountUp
                start={previousValue || 0}
                end={value}
                duration={2}
                decimals={0}
                delay={index * 0.1}
                formattingFn={(val) => formatValue(val)}
              />
            )}
          </Typography>
        </Box>

        {/* Trend indicator with animation */}
        {trend !== 'neutral' && trendValue && (
          <Box
            display="flex"
            alignItems="center"
            gap={0.5}
            sx={{
              animation: `${slideInNumber} 0.8s ease-out ${index * 0.1 + 0.3}s both`,
            }}
          >
            <Box
              sx={{
                width: 24,
                height: 24,
                borderRadius: '50%',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                background:
                  trend === 'up'
                    ? alpha(theme.palette.success.main, 0.1)
                    : alpha(theme.palette.error.main, 0.1),
                animation: isHovered ? `${iconRotate} 1s ease-in-out` : 'none',
              }}
            >
              {trend === 'up' ? (
                <TrendingUp
                  sx={{
                    fontSize: 16,
                    color: theme.palette.success.main,
                  }}
                />
              ) : (
                <TrendingDown
                  sx={{
                    fontSize: 16,
                    color: theme.palette.error.main,
                  }}
                />
              )}
            </Box>
            <Typography
              variant="caption"
              sx={{
                color: trend === 'up' ? theme.palette.success.main : theme.palette.error.main,
                fontWeight: 700,
                fontSize: '0.75rem',
              }}
            >
              {Math.abs(trendValue)}%
            </Typography>
            <Typography
              variant="caption"
              sx={{
                color: theme.palette.text.secondary,
                fontSize: '0.7rem',
              }}
            >
              vs last period
            </Typography>
          </Box>
        )}

        {/* Animated progress bar at bottom */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: '2px',
            background: alpha(colorScheme.light, 0.1),
            overflow: 'hidden',
          }}
        >
          <Box
            sx={{
              height: '100%',
              width: '100%',
              background: colorScheme.gradient,
              backgroundSize: '200% 100%',
              animation: `${shimmer} 2s linear infinite`,
              transform: isHovered ? 'scaleX(1)' : 'scaleX(0)',
              transformOrigin: 'left',
              transition: 'transform 0.6s ease',
            }}
          />
        </Box>
      </CardContent>
    </Card>
  );
};

export default BeautifulKPICard;