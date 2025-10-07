/**
 * E-commerce KPI Card Component
 * Displays header KPI metrics with trend indicators
 */
import React from 'react';
import { Box, Card, CardContent, Typography, useTheme, alpha, Tooltip } from '@mui/material';
import { TrendingUp, TrendingDown, Remove } from '@mui/icons-material';
import { keyframes } from '@mui/system';
import { formatCurrency, formatNumber, formatPercentage } from '../../utils/chartHelpers';

const slideUp = keyframes`
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
  0%, 100% { transform: scale(1); }
  50% { transform: scale(1.05); }
`;

interface EcommerceKPICardProps {
  title: string;
  value: number;
  trend: number;
  format: 'currency' | 'number' | 'percentage';
  icon: React.ReactNode;
  color: string;
  tooltip?: string;
  delay?: number;
}

export const EcommerceKPICard: React.FC<EcommerceKPICardProps> = ({
  title,
  value,
  trend,
  format,
  icon,
  color,
  tooltip,
  delay = 0
}) => {
  const theme = useTheme();

  const formatValue = (val: number) => {
    switch (format) {
      case 'currency':
        return formatCurrency(val);
      case 'percentage':
        return formatPercentage(val);
      default:
        return formatNumber(val);
    }
  };

  const isPositive = trend > 0;
  const isNeutral = trend === 0;
  const trendColor = isNeutral ? theme.palette.grey[500] : isPositive ? '#10b981' : '#ef4444';

  const TrendIcon = isNeutral ? Remove : isPositive ? TrendingUp : TrendingDown;

  return (
    <Card
      sx={{
        position: 'relative',
        overflow: 'hidden',
        background: `linear-gradient(135deg, ${alpha(color, 0.05)} 0%, ${alpha(color, 0.02)} 100%)`,
        border: `1px solid ${alpha(color, 0.2)}`,
        borderRadius: 2,
        transition: 'all 0.3s ease',
        animation: `${slideUp} 0.6s ease-out ${delay}ms backwards`,
        '&:hover': {
          transform: 'translateY(-4px)',
          boxShadow: `0 8px 24px ${alpha(color, 0.25)}`,
          borderColor: alpha(color, 0.4),
        }
      }}
    >
      {/* Background decoration */}
      <Box
        sx={{
          position: 'absolute',
          top: -20,
          right: -20,
          width: 100,
          height: 100,
          borderRadius: '50%',
          background: `radial-gradient(circle, ${alpha(color, 0.15)} 0%, transparent 70%)`,
          pointerEvents: 'none'
        }}
      />

      <CardContent sx={{ position: 'relative', p: 2.5 }}>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          {/* Icon */}
          <Box
            sx={{
              width: 48,
              height: 48,
              borderRadius: 1.5,
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              background: alpha(color, 0.1),
              color: color,
              fontSize: '1.5rem'
            }}
          >
            {icon}
          </Box>

          {/* Trend indicator */}
          <Tooltip title={tooltip || `${isPositive ? 'Increased' : 'Decreased'} by ${Math.abs(trend).toFixed(1)}% vs previous period`}>
            <Box
              sx={{
                display: 'flex',
                alignItems: 'center',
                gap: 0.5,
                px: 1,
                py: 0.5,
                borderRadius: 1,
                background: alpha(trendColor, 0.1),
                color: trendColor,
                fontSize: '0.875rem',
                fontWeight: 600,
                animation: isNeutral ? 'none' : `${pulse} 2s ease-in-out infinite`
              }}
            >
              <TrendIcon sx={{ fontSize: '1rem' }} />
              <Typography variant="caption" sx={{ fontWeight: 700 }}>
                {Math.abs(trend).toFixed(1)}%
              </Typography>
            </Box>
          </Tooltip>
        </Box>

        {/* Title */}
        <Typography
          variant="body2"
          sx={{
            color: theme.palette.text.secondary,
            fontWeight: 500,
            textTransform: 'uppercase',
            letterSpacing: 0.5,
            fontSize: '0.75rem',
            mb: 0.5
          }}
        >
          {title}
        </Typography>

        {/* Value */}
        <Typography
          variant="h4"
          sx={{
            color: theme.palette.text.primary,
            fontWeight: 700,
            fontSize: '1.75rem',
            lineHeight: 1.2
          }}
        >
          {formatValue(value)}
        </Typography>

        {/* Subtle bottom border */}
        <Box
          sx={{
            position: 'absolute',
            bottom: 0,
            left: 0,
            right: 0,
            height: 3,
            background: `linear-gradient(90deg, ${color} 0%, transparent 100%)`,
            opacity: 0.3
          }}
        />
      </CardContent>
    </Card>
  );
};

export default EcommerceKPICard;
