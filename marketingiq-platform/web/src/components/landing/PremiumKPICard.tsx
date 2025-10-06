/**
 * Premium KPI Card - Ultra Insane Edition
 * Glass-morphism, neon glow, 3D tilt, sparklines, real-time animations
 * Makes your boss say "HOLY SH*T!"
 */
import React, { useState, useEffect, useRef } from 'react';
import { Box, Card, Typography, useTheme, alpha } from '@mui/material';
import { keyframes } from '@mui/system';
import CountUp from 'react-countup';
import { LineChart, Line, ResponsiveContainer } from 'recharts';
import { CHART_COLORS } from '../../constants/visualizations';
import { formatCurrency, formatPercentage, formatCompactNumber } from '../../utils/chartHelpers';

// Insane animations
const neonPulse = keyframes`
  0%, 100% {
    box-shadow: 0 0 20px rgba(0, 188, 212, 0.4), 0 0 40px rgba(0, 188, 212, 0.2);
  }
  50% {
    box-shadow: 0 0 30px rgba(0, 188, 212, 0.6), 0 0 60px rgba(0, 188, 212, 0.4);
  }
`;

const numberGlow = keyframes`
  0%, 100% { text-shadow: 0 0 10px rgba(255, 255, 255, 0.5); }
  50% { text-shadow: 0 0 20px rgba(255, 255, 255, 0.8); }
`;

const shimmer = keyframes`
  0% { background-position: -200% center; }
  100% { background-position: 200% center; }
`;

const float = keyframes`
  0%, 100% { transform: translateY(0px); }
  50% { transform: translateY(-5px); }
`;

interface PremiumKPICardProps {
  title: string;
  value: number;
  format?: 'currency' | 'number' | 'percentage';
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: number;
  sparklineData?: number[];
  color?: 'success' | 'warning' | 'error' | 'info' | 'primary';
  glowEffect?: boolean;
  loading?: boolean;
  onClick?: () => void;
}

export const PremiumKPICard: React.FC<PremiumKPICardProps> = ({
  title,
  value,
  format = 'number',
  icon,
  trend,
  trendValue,
  sparklineData,
  color = 'primary',
  glowEffect = false,
  loading = false,
  onClick,
}) => {
  const theme = useTheme();
  const cardRef = useRef<HTMLDivElement>(null);
  const [tiltStyle, setTiltStyle] = useState({});
  const [displayValue, setDisplayValue] = useState(0);

  // Color mapping
  const colorMap = {
    success: CHART_COLORS.success,
    warning: CHART_COLORS.warning,
    error: CHART_COLORS.error,
    info: CHART_COLORS.info,
    primary: CHART_COLORS.primary,
  };

  const accentColor = colorMap[color];

  // Format value
  const formattedValue = (val: number) => {
    switch (format) {
      case 'currency':
        return formatCurrency(val);
      case 'percentage':
        return formatPercentage(val);
      default:
        return formatCompactNumber(val);
    }
  };

  // 3D Tilt effect on mouse move
  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;

    const card = cardRef.current;
    const rect = card.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;

    const centerX = rect.width / 2;
    const centerY = rect.height / 2;

    const rotateX = ((y - centerY) / centerY) * -10; // Max 10deg
    const rotateY = ((x - centerX) / centerX) * 10;

    setTiltStyle({
      transform: `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`,
      transition: 'transform 0.1s ease-out',
    });
  };

  const handleMouseLeave = () => {
    setTiltStyle({
      transform: 'perspective(1000px) rotateX(0deg) rotateY(0deg) scale3d(1, 1, 1)',
      transition: 'transform 0.3s ease-out',
    });
  };

  // Animate value on change
  useEffect(() => {
    setDisplayValue(value);
  }, [value]);

  // Prepare sparkline data
  const chartData = sparklineData?.map((val, idx) => ({ value: val, index: idx })) || [];

  return (
    <Card
      ref={cardRef}
      onMouseMove={handleMouseMove}
      onMouseLeave={handleMouseLeave}
      onClick={onClick}
      sx={{
        position: 'relative',
        overflow: 'hidden',
        cursor: onClick ? 'pointer' : 'default',
        background: `linear-gradient(135deg, ${alpha(theme.palette.background.paper, 0.8)}, ${alpha(theme.palette.background.paper, 0.95)})`,
        backdropFilter: 'blur(20px)',
        border: `1px solid ${alpha(accentColor, 0.3)}`,
        borderRadius: 3,
        ...tiltStyle,
        ...(glowEffect && {
          animation: `${neonPulse} 3s ease-in-out infinite`,
        }),
        '&:hover': {
          borderColor: alpha(accentColor, 0.6),
          '& .icon-container': {
            animation: `${float} 2s ease-in-out infinite`,
          },
          '& .shimmer-overlay': {
            opacity: 1,
          },
        },
        '&::before': {
          content: '""',
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)`,
          backgroundSize: '200% 100%',
          animation: `${shimmer} 3s linear infinite`,
        },
      }}
    >
      {/* Glass shine overlay */}
      <Box
        className="shimmer-overlay"
        sx={{
          position: 'absolute',
          top: 0,
          left: 0,
          right: 0,
          bottom: 0,
          background: `linear-gradient(135deg, ${alpha('#fff', 0.05)} 0%, transparent 50%, ${alpha('#fff', 0.05)} 100%)`,
          opacity: 0,
          transition: 'opacity 0.3s ease',
          pointerEvents: 'none',
        }}
      />

      <Box sx={{ p: 3, position: 'relative', zIndex: 1 }}>
        {/* Header with icon */}
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', mb: 2 }}>
          <Typography
            variant="subtitle2"
            sx={{
              color: theme.palette.text.secondary,
              textTransform: 'uppercase',
              letterSpacing: 1,
              fontWeight: 600,
              fontSize: '0.75rem',
            }}
          >
            {title}
          </Typography>

          <Box
            className="icon-container"
            sx={{
              width: 40,
              height: 40,
              borderRadius: 2,
              background: alpha(accentColor, 0.15),
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: accentColor,
              boxShadow: `0 0 20px ${alpha(accentColor, 0.3)}`,
            }}
          >
            {icon}
          </Box>
        </Box>

        {/* Main value */}
        <Box sx={{ mb: 2 }}>
          <Typography
            variant="h3"
            sx={{
              fontWeight: 700,
              color: theme.palette.text.primary,
              animation: glowEffect ? `${numberGlow} 2s ease-in-out infinite` : 'none',
              background: `linear-gradient(135deg, ${theme.palette.text.primary}, ${alpha(accentColor, 0.8)})`,
              WebkitBackgroundClip: 'text',
              WebkitTextFillColor: 'transparent',
              backgroundSize: '200% 200%',
            }}
          >
            {loading ? (
              '---'
            ) : (
              <CountUp
                start={0}
                end={value}
                duration={2.5}
                decimals={format === 'percentage' ? 1 : format === 'currency' ? 0 : 0}
                formattingFn={formattedValue}
              />
            )}
          </Typography>

          {/* Trend indicator */}
          {trend && trendValue !== undefined && (
            <Box sx={{ display: 'flex', alignItems: 'center', gap: 0.5, mt: 1 }}>
              <Box
                sx={{
                  px: 1,
                  py: 0.5,
                  borderRadius: 1,
                  background: alpha(
                    trend === 'up' ? CHART_COLORS.success : trend === 'down' ? CHART_COLORS.error : CHART_COLORS.neutral,
                    0.15
                  ),
                  display: 'flex',
                  alignItems: 'center',
                  gap: 0.5,
                }}
              >
                <Typography
                  variant="caption"
                  sx={{
                    color: trend === 'up' ? CHART_COLORS.success : trend === 'down' ? CHART_COLORS.error : CHART_COLORS.neutral,
                    fontWeight: 700,
                    fontSize: '0.7rem',
                  }}
                >
                  {trend === 'up' ? '↑' : trend === 'down' ? '↓' : '→'} {Math.abs(trendValue).toFixed(1)}%
                </Typography>
              </Box>
              <Typography variant="caption" sx={{ color: theme.palette.text.secondary, fontSize: '0.7rem' }}>
                vs last period
              </Typography>
            </Box>
          )}
        </Box>

        {/* Sparkline */}
        {sparklineData && sparklineData.length > 0 && (
          <Box sx={{ height: 40, mt: 2 }}>
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData}>
                <Line
                  type="monotone"
                  dataKey="value"
                  stroke={accentColor}
                  strokeWidth={2}
                  dot={false}
                  isAnimationActive={true}
                  animationDuration={1000}
                />
              </LineChart>
            </ResponsiveContainer>
          </Box>
        )}

        {/* Bottom glow accent */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: '2px',
            background: `linear-gradient(90deg, transparent, ${accentColor}, transparent)`,
            opacity: 0.5,
          }}
        />
      </Box>
    </Card>
  );
};

export default PremiumKPICard;
