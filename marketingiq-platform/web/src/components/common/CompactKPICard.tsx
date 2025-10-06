import React from 'react';
import {
  Card,
  CardContent,
  Typography,
  Box,
  useTheme,
  alpha,
  Zoom,
} from '@mui/material';
import {
  ArrowUpward,
  ArrowDownward,
} from '@mui/icons-material';
import { formatCompactNumber } from './DashboardTemplate';

interface CompactKPICardProps {
  title: string;
  value: number | string;
  format?: 'currency' | 'percentage' | 'number';
  icon: React.ReactNode;
  trend?: 'up' | 'down' | 'neutral';
  trendValue?: number;
  color?: 'primary' | 'success' | 'warning' | 'error' | 'info' | 'secondary';
  index?: number;
  animate?: boolean;
}

const CompactKPICard: React.FC<CompactKPICardProps> = ({
  title,
  value,
  format = 'number',
  icon,
  trend = 'up',
  trendValue = 0,
  color = 'primary',
  index = 0,
  animate = true,
}) => {
  const theme = useTheme();

  const getFormattedValue = () => {
    const numValue = typeof value === 'string' ? parseFloat(value) : value;
    if (format === 'currency') {
      return `₹${numValue.toFixed(2)}`;
    } else if (format === 'percentage') {
      return `${numValue.toFixed(2)}%`;
    } else {
      return formatCompactNumber(numValue);
    }
  };

  return (
    <Zoom in={animate} timeout={400 + index * 50}>
      <Card
        sx={{
          height: '100%',
          position: 'relative',
          overflow: 'hidden',
          cursor: 'pointer',
          transition: 'all 0.3s ease',
          '&:hover': {
            transform: 'translateY(-4px)',
            boxShadow: theme.shadows[4],
          },
          '&::before': {
            content: '""',
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            height: '3px',
            background: `linear-gradient(90deg, ${theme.palette[color].main}, ${alpha(
              theme.palette[color].main,
              0.3
            )})`,
          },
        }}
      >
        <CardContent sx={{ p: 2, '&:last-child': { pb: 2 } }}>
          <Box display="flex" alignItems="center" justifyContent="space-between" mb={1}>
            <Typography variant="caption" color="text.secondary" fontWeight={500}>
              {title}
            </Typography>
            <Box
              sx={{
                width: 28,
                height: 28,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                borderRadius: 1,
                bgcolor: alpha(theme.palette[color].main, 0.1),
                color: theme.palette[color].main,
              }}
            >
              {icon}
            </Box>
          </Box>
          <Typography variant="h6" fontWeight="bold" sx={{ mb: 0.5 }}>
            {getFormattedValue()}
          </Typography>
          {trend !== 'neutral' && (
            <Box display="flex" alignItems="center" gap={0.5}>
              {trend === 'up' ? (
                <ArrowUpward sx={{ fontSize: 14, color: theme.palette.success.main }} />
              ) : (
                <ArrowDownward sx={{ fontSize: 14, color: theme.palette.error.main }} />
              )}
              <Typography
                variant="caption"
                sx={{
                  color: trend === 'up' ? theme.palette.success.main : theme.palette.error.main,
                  fontWeight: 600,
                }}
              >
                {Math.abs(trendValue)}%
              </Typography>
            </Box>
          )}
        </CardContent>
      </Card>
    </Zoom>
  );
};

export default CompactKPICard;