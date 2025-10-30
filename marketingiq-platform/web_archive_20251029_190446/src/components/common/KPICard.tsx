import React from 'react';
import { Card, CardContent, Typography, Box, Chip, useTheme } from '@mui/material';
import { TrendingUp, TrendingDown, Remove } from '@mui/icons-material';

interface KPICardProps {
  title: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  icon?: React.ReactNode;
  color?: 'primary' | 'secondary' | 'error' | 'warning' | 'info' | 'success';
  subtitle?: string;
  onClick?: () => void;
}

const KPICard: React.FC<KPICardProps> = ({
  title,
  value,
  change,
  changeLabel,
  icon,
  color = 'primary',
  subtitle,
  onClick,
}) => {
  const theme = useTheme();

  const getTrendIcon = () => {
    if (!change) return <Remove />;
    return change > 0 ? <TrendingUp /> : <TrendingDown />;
  };

  const getTrendColor = () => {
    if (!change) return 'default';
    return change > 0 ? 'success' : 'error';
  };

  return (
    <Card
      sx={{
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s',
        border: `1px solid ${theme.palette.divider}`,
        '&:hover': onClick
          ? {
              transform: 'translateY(-4px)',
              boxShadow: `0 4px 20px ${theme.palette.primary.main}20`,
              borderColor: theme.palette.primary.main,
            }
          : {},
      }}
      onClick={onClick}
    >
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
          <Box sx={{ flex: 1 }}>
            <Typography variant="body2" color="text.secondary" gutterBottom>
              {title}
            </Typography>
            <Typography variant="h4" sx={{ fontWeight: 600, my: 1, color: `${color}.main` }}>
              {value}
            </Typography>
            {subtitle && (
              <Typography variant="caption" color="text.secondary">
                {subtitle}
              </Typography>
            )}
            {change !== undefined && (
              <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
                <Chip
                  size="small"
                  icon={getTrendIcon()}
                  label={`${change > 0 ? '+' : ''}${change.toFixed(1)}%${
                    changeLabel ? ` ${changeLabel}` : ''
                  }`}
                  color={getTrendColor()}
                  variant="outlined"
                  sx={{ fontSize: '0.75rem' }}
                />
              </Box>
            )}
          </Box>
          {icon && (
            <Box
              sx={{
                p: 1,
                borderRadius: 2,
                bgcolor: `${color}.main`,
                color: 'background.paper',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              {icon}
            </Box>
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default KPICard;