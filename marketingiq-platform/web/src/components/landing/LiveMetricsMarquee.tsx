/**
 * Live Metrics Marquee - Infinite Scrolling Ticker
 * Shows real-time metrics flowing across the screen
 * Like a stock ticker but for ads performance
 */
import React from 'react';
import { Box, Typography, useTheme, alpha } from '@mui/material';
import { keyframes } from '@mui/system';
import {
  MonetizationOn,
  Campaign,
  TrendingUp,
  Mouse,
  Speed,
  ShoppingCart,
  AutoAwesome,
} from '@mui/icons-material';
import { formatCurrency, formatPercentage, formatCompactNumber } from '../../utils/chartHelpers';

const scroll = keyframes`
  0% {
    transform: translateX(0);
  }
  100% {
    transform: translateX(-50%);
  }
`;

const pulse = keyframes`
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.8;
    transform: scale(1.05);
  }
`;

interface MetricItem {
  icon: React.ReactNode;
  label: string;
  value: string | number;
  format?: 'currency' | 'number' | 'percentage' | 'string';
  color: string;
}

interface LiveMetricsMarqueeProps {
  metrics: {
    totalSpend: number;
    activeCampaigns: number;
    conversionRate: number;
    clicks: number;
    avgCPC: number;
    ecommerceOrders: number;
    aiRevenue: number;
  };
}

export const LiveMetricsMarquee: React.FC<LiveMetricsMarqueeProps> = ({ metrics }) => {
  const theme = useTheme();

  const items: MetricItem[] = [
    {
      icon: <MonetizationOn />,
      label: 'Spend Today',
      value: metrics.totalSpend,
      format: 'currency',
      color: '#ffa726',
    },
    {
      icon: <Campaign />,
      label: 'Active Campaigns',
      value: metrics.activeCampaigns,
      format: 'number',
      color: '#00bcd4',
    },
    {
      icon: <TrendingUp />,
      label: 'CVR',
      value: metrics.conversionRate,
      format: 'percentage',
      color: '#66bb6a',
    },
    {
      icon: <Mouse />,
      label: 'Clicks',
      value: metrics.clicks,
      format: 'number',
      color: '#29b6f6',
    },
    {
      icon: <Speed />,
      label: 'Avg CPC',
      value: `₹${metrics.avgCPC.toFixed(2)}`,
      format: 'string',
      color: '#ab47bc',
    },
    {
      icon: <ShoppingCart />,
      label: 'E-commerce Orders',
      value: metrics.ecommerceOrders,
      format: 'number',
      color: '#4caf50',
    },
    {
      icon: <AutoAwesome />,
      label: 'AI Generated Revenue',
      value: metrics.aiRevenue,
      format: 'currency',
      color: '#ff5252',
    },
  ];

  const formatValue = (value: number | string, format?: string) => {
    if (typeof value === 'string') return value;
    switch (format) {
      case 'currency':
        return formatCurrency(value);
      case 'percentage':
        return formatPercentage(value);
      default:
        return formatCompactNumber(value);
    }
  };

  // Duplicate items for seamless loop
  const duplicatedItems = [...items, ...items];

  return (
    <Box
      sx={{
        width: '100%',
        overflow: 'hidden',
        background: `linear-gradient(90deg, ${alpha(theme.palette.background.paper, 0.5)}, ${alpha(theme.palette.background.paper, 0.8)}, ${alpha(theme.palette.background.paper, 0.5)})`,
        backdropFilter: 'blur(10px)',
        borderTop: `1px solid ${alpha('#00bcd4', 0.2)}`,
        borderBottom: `1px solid ${alpha('#00bcd4', 0.2)}`,
        position: 'relative',
        py: 1.5,
        '&::before, &::after': {
          content: '""',
          position: 'absolute',
          top: 0,
          bottom: 0,
          width: '100px',
          zIndex: 2,
          pointerEvents: 'none',
        },
        '&::before': {
          left: 0,
          background: `linear-gradient(90deg, ${theme.palette.background.default}, transparent)`,
        },
        '&::after': {
          right: 0,
          background: `linear-gradient(90deg, transparent, ${theme.palette.background.default})`,
        },
      }}
    >
      {/* Live indicator */}
      <Box
        sx={{
          position: 'absolute',
          top: 8,
          left: 16,
          display: 'flex',
          alignItems: 'center',
          gap: 0.5,
          zIndex: 3,
        }}
      >
        <Box
          sx={{
            width: 8,
            height: 8,
            borderRadius: '50%',
            bgcolor: '#ff5252',
            animation: `${pulse} 2s ease-in-out infinite`,
            boxShadow: '0 0 10px rgba(255, 82, 82, 0.8)',
          }}
        />
        <Typography
          variant="caption"
          sx={{
            color: theme.palette.text.secondary,
            fontWeight: 700,
            textTransform: 'uppercase',
            fontSize: '0.65rem',
            letterSpacing: 1,
          }}
        >
          LIVE
        </Typography>
      </Box>

      {/* Scrolling metrics */}
      <Box
        sx={{
          display: 'flex',
          animation: `${scroll} 40s linear infinite`,
          gap: 6,
          pl: 6,
        }}
      >
        {duplicatedItems.map((item, index) => (
          <Box
            key={index}
            sx={{
              display: 'flex',
              alignItems: 'center',
              gap: 1.5,
              flexShrink: 0,
              px: 2,
              py: 1,
              borderRadius: 2,
              background: alpha(item.color, 0.08),
              border: `1px solid ${alpha(item.color, 0.2)}`,
              transition: 'all 0.3s ease',
              '&:hover': {
                background: alpha(item.color, 0.15),
                transform: 'scale(1.05)',
              },
            }}
          >
            <Box
              sx={{
                width: 32,
                height: 32,
                borderRadius: '50%',
                background: alpha(item.color, 0.2),
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                color: item.color,
                fontSize: '1.2rem',
              }}
            >
              {item.icon}
            </Box>

            <Box>
              <Typography
                variant="caption"
                sx={{
                  color: theme.palette.text.secondary,
                  fontSize: '0.65rem',
                  textTransform: 'uppercase',
                  letterSpacing: 0.5,
                  display: 'block',
                  lineHeight: 1.2,
                }}
              >
                {item.label}
              </Typography>
              <Typography
                variant="h6"
                sx={{
                  color: item.color,
                  fontWeight: 700,
                  fontSize: '1.1rem',
                  lineHeight: 1.2,
                  textShadow: `0 0 10px ${alpha(item.color, 0.5)}`,
                }}
              >
                {formatValue(item.value, item.format)}
              </Typography>
            </Box>
          </Box>
        ))}
      </Box>
    </Box>
  );
};

export default LiveMetricsMarquee;
