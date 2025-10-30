// KPI Card Component - Clean, Minimal Design
import React from 'react';
import { Card, CardContent, Typography, Box, Chip } from '@mui/material';
import { motion } from 'framer-motion';
import { KPIData } from '../../types';

interface KPICardProps {
  data: KPIData;
  index?: number;
}

export const KPICard: React.FC<KPICardProps> = ({ data, index = 0 }) => {
  const {
    title,
    value,
    change,
    changeLabel,
    color = 'primary',
    trend,
    isHighlighted = false,
    prefix = '',
    suffix = '',
  } = data;

  const getTrendColor = () => {
    if (trend === 'up' && change > 0) return 'success.main';
    if (trend === 'down' && change < 0) return 'error.main';
    if (change > 0) return 'success.main';
    if (change < 0) return 'error.main';
    return 'text.secondary';
  };

  const changeSymbol = change > 0 ? '+' : '';

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1, duration: 0.4 }}
    >
      <Card
        sx={{
          height: '100%',
          borderLeft: isHighlighted ? `4px solid` : 'none',
          borderColor: `${color}.main`,
          position: 'relative',
          overflow: 'visible',
        }}
      >
        <CardContent>
          <Typography variant="body2" color="text.secondary" gutterBottom>
            {title}
          </Typography>

          <Typography variant="h4" component="div" sx={{ my: 1, fontWeight: 700 }}>
            {prefix}{typeof value === 'number' ? value.toLocaleString() : value}{suffix}
          </Typography>

          <Box display="flex" alignItems="center" gap={1}>
            <Chip
              label={`${changeSymbol}${Math.abs(change)}%`}
              size="small"
              sx={{
                bgcolor: change > 0 ? 'success.lighter' : change < 0 ? 'error.lighter' : 'grey.100',
                color: getTrendColor(),
                fontWeight: 600,
                fontSize: '0.75rem',
              }}
            />
            {changeLabel && (
              <Typography variant="caption" color="text.secondary">
                {changeLabel}
              </Typography>
            )}
          </Box>
        </CardContent>
      </Card>
    </motion.div>
  );
};
