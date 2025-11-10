import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';
import { colors } from '../../../theme/designTokens';

interface ImpactMeterProps {
  value: number | string;
  label: string;
  type?: 'positive' | 'negative' | 'neutral';
  format?: 'currency' | 'percentage' | 'number';
  currency?: string;
  subtitle?: string;
  size?: 'small' | 'medium' | 'large';
}

export const ImpactMeter: React.FC<ImpactMeterProps> = ({
  value,
  label,
  type = 'positive',
  format = 'currency',
  currency = '₹',
  subtitle,
  size = 'medium',
}) => {
  // Get color based on type
  const getColor = () => {
    switch (type) {
      case 'positive':
        return colors.success.main;
      case 'negative':
        return colors.error.main;
      default:
        return colors.info.main;
    }
  };

  // Format value
  const formatValue = () => {
    const numValue = typeof value === 'number' ? value : parseFloat(value as string);

    if (format === 'currency') {
      return `${currency}${Math.abs(numValue).toLocaleString('en-IN')}`;
    } else if (format === 'percentage') {
      return `${numValue}%`;
    }
    return Math.abs(numValue).toLocaleString('en-IN');
  };

  // Get size styles
  const getSizeStyles = () => {
    switch (size) {
      case 'small':
        return {
          valueSize: '1.25rem',
          labelSize: '0.75rem',
          padding: 2,
        };
      case 'large':
        return {
          valueSize: '2.5rem',
          labelSize: '1rem',
          padding: 3,
        };
      default:
        return {
          valueSize: '1.75rem',
          labelSize: '0.875rem',
          padding: 2.5,
        };
    }
  };

  const mainColor = getColor();
  const bgColor = `${mainColor}15`;
  const styles = getSizeStyles();

  // Icon component
  const Icon = type === 'positive' ? TrendingUpIcon : type === 'negative' ? TrendingDownIcon : null;

  return (
    <Card
      sx={{
        border: `2px solid ${mainColor}`,
        borderRadius: 2,
        background: bgColor,
        boxShadow: `0px 4px 12px ${mainColor}30`,
        transition: 'all 0.3s ease',
        '&:hover': {
          transform: 'translateY(-2px)',
          boxShadow: `0px 6px 16px ${mainColor}40`,
        },
      }}
    >
      <CardContent sx={{ padding: styles.padding, '&:last-child': { pb: styles.padding } }}>
        <Box sx={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 1 }}>
          <Box sx={{ flex: 1 }}>
            <Typography
              sx={{
                fontSize: styles.labelSize,
                color: colors.text.secondary,
                fontWeight: 500,
                mb: 0.5,
              }}
            >
              {label}
            </Typography>
            <Typography
              variant="h4"
              sx={{
                fontSize: styles.valueSize,
                fontWeight: 700,
                color: mainColor,
                lineHeight: 1.2,
                mb: subtitle ? 0.5 : 0,
              }}
            >
              {type === 'negative' && '-'}
              {formatValue()}
            </Typography>
            {subtitle && (
              <Typography
                sx={{
                  fontSize: '0.75rem',
                  color: colors.text.secondary,
                  mt: 0.5,
                }}
              >
                {subtitle}
              </Typography>
            )}
          </Box>
          {Icon && (
            <Chip
              icon={<Icon sx={{ fontSize: '16px !important' }} />}
              label={type === 'positive' ? 'Impact' : 'Risk'}
              size="small"
              sx={{
                bgcolor: mainColor,
                color: 'white',
                fontWeight: 600,
                fontSize: '0.7rem',
                height: 24,
                '& .MuiChip-icon': {
                  color: 'white',
                },
              }}
            />
          )}
        </Box>
      </CardContent>
    </Card>
  );
};

export default ImpactMeter;
