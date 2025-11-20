import React from 'react';
import { Chip, ChipProps } from '@mui/material';
import AutoAwesomeIcon from '@mui/icons-material/AutoAwesome';
import { colors } from '../../../theme/designTokens';

interface AIBadgeProps extends Omit<ChipProps, 'label' | 'icon'> {
  label?: string;
  variant?: 'default' | 'compact';
}

export const AIBadge: React.FC<AIBadgeProps> = ({
  label = 'Powered by AI',
  variant = 'default',
  sx,
  ...props
}) => {
  return (
    <Chip
      icon={<AutoAwesomeIcon sx={{ fontSize: variant === 'compact' ? '14px !important' : '16px !important' }} />}
      label={label}
      size={variant === 'compact' ? 'small' : 'medium'}
      sx={{
        background: colors.ai.gradient,
        color: colors.ai.text,
        fontWeight: 600,
        fontSize: variant === 'compact' ? '0.75rem' : '0.875rem',
        height: variant === 'compact' ? 24 : 32,
        '& .MuiChip-icon': {
          color: colors.ai.text,
        },
        boxShadow: '0px 2px 8px rgba(102, 126, 234, 0.2)',
        transition: 'all 0.3s ease',
        '&:hover': {
          background: colors.ai.gradientHover,
          boxShadow: '0px 4px 12px rgba(102, 126, 234, 0.3)',
          transform: 'translateY(-1px)',
        },
        ...sx,
      }}
      {...props}
    />
  );
};

export default AIBadge;
